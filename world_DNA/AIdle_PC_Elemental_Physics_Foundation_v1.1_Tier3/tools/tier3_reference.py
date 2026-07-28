from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import copy
import json
from typing import Any

DYNAMIC_FARM_IDS = {"cozy_farm_plot_A", "prop_farm_plot_2x2"}
DYNAMIC_POND_IDS = {"cozy_pond_small_A", "water_pond_small"}
STATIC_CONTROL_IDS = {"cozy_rock_A", "nature_rock_soft", "cozy_path_stone_A", "path_stone_straight", "cozy_fence_A"}
ALLOWED_STATE_FIELDS = {"wetness", "growth", "health", "temperature", "integrity", "charge", "pressure", "states"}


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def validate_elapsed(saved_wall: float, current_wall: float, saved_monotonic_msec: int,
                     current_monotonic_msec: int, max_offline_seconds: float) -> dict[str, Any]:
    observed = float(current_wall) - float(saved_wall)
    monotonic_delta = None
    monotonic_reset = current_monotonic_msec < saved_monotonic_msec
    if not monotonic_reset:
        monotonic_delta = (current_monotonic_msec - saved_monotonic_msec) / 1000.0

    if observed < 0.0:
        used = 0.0
        decision = "CLOCK_BACKWARD_REJECTED"
    elif observed > max_offline_seconds:
        used = float(max_offline_seconds)
        decision = "MAX_OFFLINE_CLAMPED"
    else:
        used = observed
        decision = "ACCEPTED"

    return {
        "observed_elapsed_seconds": observed,
        "used_elapsed_seconds": used,
        "time_decision": decision,
        "saved_wall_clock_unix": saved_wall,
        "current_wall_clock_unix": current_wall,
        "saved_monotonic_msec": saved_monotonic_msec,
        "current_monotonic_msec": current_monotonic_msec,
        "monotonic_delta_seconds": monotonic_delta,
        "monotonic_reset_detected": monotonic_reset,
        "max_offline_seconds": max_offline_seconds,
    }


def _integral_min_clamped_linear(w0: float, slope: float, limit: float, elapsed: float) -> tuple[float, int]:
    """Exact integral of min(clamp(w0+slope*t,0,1), limit) over [0, elapsed]."""
    if elapsed <= 0.0:
        return 0.0, 0
    limit = clamp01(limit)
    points = [0.0, float(elapsed)]
    if abs(slope) > 1e-18:
        for boundary in (0.0, limit, 1.0):
            t = (boundary - w0) / slope
            if 0.0 < t < elapsed:
                points.append(t)
    points = sorted(set(points))
    area = 0.0
    segments = 0
    for a, b in zip(points, points[1:]):
        fa = min(clamp01(w0 + slope * a), limit)
        fb = min(clamp01(w0 + slope * b), limit)
        area += (fa + fb) * 0.5 * (b - a)
        segments += 1
    return area, segments


def advance_farm_state(state: dict[str, Any], elapsed_seconds: float, config: dict[str, Any],
                       pond_available: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    before = copy.deepcopy(state)
    result = copy.deepcopy(state)
    farm = config["farm_solver"]
    w0 = clamp01(result.get("wetness", 0.0))
    growth0 = clamp01(result.get("growth", 0.0))
    health0 = clamp01(result.get("health", 1.0))
    decay = float(farm["wetness_decay_per_second"])
    source = float(farm["pond_replenish_per_second"]) if pond_available else 0.0
    slope = source - decay
    limiting_constant = min(
        clamp01(result.get("light", farm["default_light"])),
        clamp01(result.get("fertility", farm["default_fertility"])),
        clamp01(result.get("temperature_fit", farm["default_temperature_fit"])),
    )
    water_integral, segment_count = _integral_min_clamped_linear(w0, slope, limiting_constant, elapsed_seconds)
    growth_delta = float(farm["growth_rate_per_second"]) * water_integral
    result["wetness"] = clamp01(w0 + slope * elapsed_seconds)
    result["growth"] = clamp01(growth0 + growth_delta)
    result["health"] = health0
    variant = "wet" if result["wetness"] >= float(farm["wet_variant_threshold"]) else "default"
    result["visual_variant"] = variant
    metrics = {
        "wetness_before": w0,
        "wetness_after": result["wetness"],
        "growth_before": growth0,
        "growth_after": result["growth"],
        "growth_delta": result["growth"] - growth0,
        "pond_available": pond_available,
        "closed_form_segments": segment_count,
        "state_changed": stable_hash(before) != stable_hash(result),
        "selected_visual_variant": variant,
    }
    return result, metrics


class ValidatedPersistenceStore:
    def __init__(self, records: list[dict[str, Any]]):
        self._records = {record["entity_id"]: copy.deepcopy(record) for record in records}
        self.event_trace: list[str] = []

    def snapshot(self) -> list[dict[str, Any]]:
        return [copy.deepcopy(self._records[key]) for key in sorted(self._records)]

    def update_existing_state(self, entity_id: str, new_state: dict[str, Any]) -> None:
        if entity_id not in self._records:
            raise KeyError("Tier 3 may not create entities")
        record = self._records[entity_id]
        if not record.get("canonical_committed", False):
            raise PermissionError("Tier 3 may only update canonical committed entities")
        forbidden = set(new_state) - (set(record.get("state", {})) | ALLOWED_STATE_FIELDS | {"visual_variant", "light", "fertility", "temperature_fit"})
        if forbidden:
            raise PermissionError(f"Tier 3 attempted forbidden state fields: {sorted(forbidden)}")
        record["state"] = copy.deepcopy(new_state)
        self.event_trace.append(f"persist:{entity_id}")


class Tier3OfflineService:
    def __init__(self, config: dict[str, Any]):
        self.config = copy.deepcopy(config)

    def reconcile_chunk(self, chunk_id: str, records: list[dict[str, Any]], current_wall: float,
                        current_monotonic_msec: int) -> dict[str, Any]:
        before_records = copy.deepcopy(records)
        store = ValidatedPersistenceStore(records)
        event_trace = ["interaction_disabled", "records_loaded"]
        chunk_records = [r for r in records if r.get("chunk_id") == chunk_id]
        if not chunk_records:
            raise ValueError("Chunk has no persisted records")
        saved_wall = min(float(r["saved_wall_clock_unix"]) for r in chunk_records)
        saved_monotonic = min(int(r["saved_monotonic_msec"]) for r in chunk_records)
        time_info = validate_elapsed(
            saved_wall, current_wall, saved_monotonic, current_monotonic_msec,
            float(self.config["max_offline_seconds"]),
        )
        elapsed = time_info["used_elapsed_seconds"]
        pond_ids = {
            r["entity_id"] for r in chunk_records
            if r.get("module_id") in DYNAMIC_POND_IDS and r.get("canonical_committed", False)
        }
        updated, skipped, metrics = [], [], {}
        original_ids = sorted(r["entity_id"] for r in records)
        original_transforms = {r["entity_id"]: copy.deepcopy(r["transform"]) for r in records}
        event_trace.append("deterministic_advance_started")
        for record in sorted(chunk_records, key=lambda x: x["entity_id"]):
            entity_id = record["entity_id"]
            module_id = record.get("module_id")
            if not record.get("canonical_committed", False):
                skipped.append(entity_id)
                metrics[entity_id] = {"reason": "NOT_CANONICAL_COMMITTED"}
                continue
            if module_id in DYNAMIC_FARM_IDS:
                source_ids = set(record.get("nearby_source_ids", []))
                new_state, entity_metrics = advance_farm_state(
                    record["state"], elapsed, self.config, bool(source_ids & pond_ids)
                )
                store.update_existing_state(entity_id, new_state)
                updated.append(entity_id)
                metrics[entity_id] = entity_metrics
            else:
                skipped.append(entity_id)
                metrics[entity_id] = {"reason": "OUTSIDE_DYNAMIC_PILOT_SCOPE", "byte_identical": True}
        event_trace.append("deterministic_advance_complete")
        event_trace.extend(store.event_trace)
        after_records = store.snapshot()
        after_ids = sorted(r["entity_id"] for r in after_records)
        if original_ids != after_ids:
            raise AssertionError("Tier 3 created or destroyed an entity")
        for record in after_records:
            if record["transform"] != original_transforms[record["entity_id"]]:
                raise AssertionError("Tier 3 changed placement")
        event_trace.append("persistence_complete")
        visual_variants = {
            r["entity_id"]: r.get("state", {}).get("visual_variant", "default")
            for r in after_records if r["entity_id"] in updated
        }
        event_trace.append("visual_variants_selected")
        event_trace.append("interaction_enabled")
        before_hash = stable_hash(before_records)
        after_hash = stable_hash(after_records)
        receipt_id = f"tier3_{chunk_id}_{int(current_wall)}_{after_hash[:12]}"
        receipt = {
            "receipt_id": receipt_id,
            "mutation_kind": "TIER3_OFFLINE_ADVANCE",
            "chunk_id": chunk_id,
            **time_info,
            "updated_entity_ids": updated,
            "skipped_entity_ids": skipped,
            "before_hash": before_hash,
            "after_hash": after_hash,
            "entity_metrics": metrics,
            "visual_variants": visual_variants,
            "event_trace": event_trace,
            "authority_proof": {
                "original_entity_ids": original_ids,
                "final_entity_ids": after_ids,
                "entity_count_unchanged": len(original_ids) == len(after_ids),
                "transforms_unchanged": True,
                "only_canonical_entities_updated": all(
                    next(r for r in records if r["entity_id"] == entity_id)["canonical_committed"]
                    for entity_id in updated
                ),
                "persistence_gateway": "ValidatedPersistenceStore.update_existing_state",
            },
            "accepted": False,
            "self_accept": False,
            "tier3_source_status": "IMPLEMENTED_HERE_SOURCE_PACKAGE_MISSING",
            "grok_status_crosscheck": "NOT_AVAILABLE_IN_SUPPLIED_PACKAGE",
        }
        return {"records": after_records, "receipt": receipt}


def tier_for_entity(distance_m: float, chunk_loaded: bool, distances=(12.0, 32.0, 96.0)) -> int:
    if not chunk_loaded:
        return 3
    if distance_m < distances[0]:
        return 0
    if distance_m < distances[1]:
        return 1
    if distance_m < distances[2]:
        return 2
    return 2

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import time

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tier3_reference", ROOT / "tools/tier3_reference.py")
tier3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tier3)
CONFIG = json.loads((ROOT / "catalogs/tier3_offline_config.json").read_text(encoding="utf-8"))
FIXTURE = json.loads((ROOT / "evidence/tier3/tier3_pilot_fixture.json").read_text(encoding="utf-8"))


def farm_state():
    return deepcopy(next(r for r in FIXTURE["records"] if r["entity_id"] == "farm_01")["state"])


def test_determinism_one_hour_equals_sixty_minutes():
    one, metrics = tier3.advance_farm_state(farm_state(), 3600.0, CONFIG, True)
    many = farm_state()
    max_segments = 0
    for _ in range(60):
        many, step_metrics = tier3.advance_farm_state(many, 60.0, CONFIG, True)
        max_segments = max(max_segments, step_metrics["closed_form_segments"])
    assert abs(one["wetness"] - many["wetness"]) <= CONFIG["floating_point_tolerance"]
    assert abs(one["growth"] - many["growth"]) <= CONFIG["floating_point_tolerance"]
    assert metrics["closed_form_segments"] <= 4
    assert max_segments <= 4


def test_bounded_30_days_is_clamped_and_constant_segments():
    service = tier3.Tier3OfflineService(CONFIG)
    start = time.perf_counter()
    result = service.reconcile_chunk(
        FIXTURE["chunk_id"], deepcopy(FIXTURE["records"]),
        FIXTURE["saved_wall_clock_unix"] + 30 * 86400,
        FIXTURE["saved_monotonic_msec"] + 30 * 86400 * 1000,
    )
    duration = time.perf_counter() - start
    receipt = result["receipt"]
    assert receipt["used_elapsed_seconds"] == CONFIG["max_offline_seconds"]
    assert receipt["time_decision"] == "MAX_OFFLINE_CLAMPED"
    assert receipt["entity_metrics"]["farm_01"]["closed_form_segments"] <= 4
    assert duration < 0.25


def test_clock_backwards_yields_zero_and_receipt():
    service = tier3.Tier3OfflineService(CONFIG)
    result = service.reconcile_chunk(
        FIXTURE["chunk_id"], deepcopy(FIXTURE["records"]),
        FIXTURE["saved_wall_clock_unix"] - 60,
        10,
    )
    receipt = result["receipt"]
    assert receipt["used_elapsed_seconds"] == 0.0
    assert receipt["time_decision"] == "CLOCK_BACKWARD_REJECTED"
    assert receipt["receipt_id"]


def test_authority_no_create_destroy_transform_or_preview_update():
    service = tier3.Tier3OfflineService(CONFIG)
    before = deepcopy(FIXTURE["records"])
    result = service.reconcile_chunk(
        FIXTURE["chunk_id"], before,
        FIXTURE["saved_wall_clock_unix"] + 3600,
        FIXTURE["saved_monotonic_msec"] + 3600 * 1000,
    )
    after = result["records"]
    assert [r["entity_id"] for r in after] == sorted(r["entity_id"] for r in before)
    before_map = {r["entity_id"]: r for r in before}
    for record in after:
        assert record["transform"] == before_map[record["entity_id"]]["transform"]
    preview_after = next(r for r in after if r["entity_id"] == "preview_farm")
    assert preview_after == before_map["preview_farm"]
    assert result["receipt"]["updated_entity_ids"] == ["farm_01"]
    assert result["receipt"]["authority_proof"]["entity_count_unchanged"] is True


def test_static_control_group_byte_identical():
    service = tier3.Tier3OfflineService(CONFIG)
    before = deepcopy(FIXTURE["records"])
    result = service.reconcile_chunk(
        FIXTURE["chunk_id"], before,
        FIXTURE["saved_wall_clock_unix"] + 7200,
        FIXTURE["saved_monotonic_msec"] + 7200 * 1000,
    )
    before_map = {r["entity_id"]: json.dumps(r, sort_keys=True, separators=(",", ":")) for r in before}
    for entity_id in ["rock_01", "path_01", "fence_01"]:
        record = next(r for r in result["records"] if r["entity_id"] == entity_id)
        assert json.dumps(record, sort_keys=True, separators=(",", ":")) == before_map[entity_id]


def test_residency_drives_tier_three_at_zero_distance():
    assert tier3.tier_for_entity(0.0, False) == 3
    assert tier3.tier_for_entity(0.0, True) == 0
    assert tier3.tier_for_entity(20.0, True) == 1
    assert tier3.tier_for_entity(50.0, True) == 2
    assert tier3.tier_for_entity(200.0, True) == 2


def test_visual_reconciliation_and_ordering():
    service = tier3.Tier3OfflineService(CONFIG)
    result = service.reconcile_chunk(
        FIXTURE["chunk_id"], deepcopy(FIXTURE["records"]),
        FIXTURE["saved_wall_clock_unix"] + 3600,
        FIXTURE["saved_monotonic_msec"] + 3600 * 1000,
    )
    receipt = result["receipt"]
    assert receipt["visual_variants"]["farm_01"] == "wet"
    trace = receipt["event_trace"]
    assert trace.index("persistence_complete") < trace.index("visual_variants_selected")
    assert trace.index("visual_variants_selected") < trace.index("interaction_enabled")


def test_receipt_marks_source_gap_and_no_self_accept():
    service = tier3.Tier3OfflineService(CONFIG)
    receipt = service.reconcile_chunk(
        FIXTURE["chunk_id"], deepcopy(FIXTURE["records"]),
        FIXTURE["saved_wall_clock_unix"] + 3600,
        FIXTURE["saved_monotonic_msec"] + 3600 * 1000,
    )["receipt"]
    assert receipt["accepted"] is False
    assert receipt["self_accept"] is False
    assert receipt["tier3_source_status"] == "IMPLEMENTED_HERE_SOURCE_PACKAGE_MISSING"

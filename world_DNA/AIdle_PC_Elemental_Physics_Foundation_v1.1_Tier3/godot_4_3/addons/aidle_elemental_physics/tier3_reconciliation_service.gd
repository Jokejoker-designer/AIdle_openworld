class_name AIdleTier3ReconciliationService
extends Node

signal offline_advance_completed(receipt: Dictionary)

@export var persistence_path: NodePath
var config: Dictionary = {}

const FARM_MODULES := {"cozy_farm_plot_A": true, "prop_farm_plot_2x2": true}
const POND_MODULES := {"cozy_pond_small_A": true, "water_pond_small": true}

func configure(value: Dictionary) -> void:
    config = value.duplicate(true)

func reconcile_chunk(chunk_id: String, records: Array, current_wall_clock_unix: float,
        current_monotonic_msec: int) -> Dictionary:
    var persistence := get_node_or_null(persistence_path) as AIdleValidatedStatePersistence
    if persistence == null:
        return {"passed": false, "error": "Validated persistence path unavailable."}
    persistence.load_existing_records(records)
    var chunk_records: Array = []
    for record in records:
        if String(record.get("chunk_id", "")) == chunk_id:
            chunk_records.append(record)
    if chunk_records.is_empty():
        return {"passed": false, "error": "Chunk has no records."}
    var saved_wall := float(chunk_records[0]["saved_wall_clock_unix"])
    var saved_monotonic := int(chunk_records[0]["saved_monotonic_msec"])
    for record in chunk_records:
        saved_wall = minf(saved_wall, float(record["saved_wall_clock_unix"]))
        saved_monotonic = mini(saved_monotonic, int(record["saved_monotonic_msec"]))
    var time_info := AIdleTier3TimeValidator.validate(
        saved_wall, current_wall_clock_unix, saved_monotonic,
        current_monotonic_msec, float(config["max_offline_seconds"])
    )
    var pond_ids: Dictionary = {}
    for record in chunk_records:
        if POND_MODULES.has(String(record.get("module_id", ""))) and bool(record.get("canonical_committed", false)):
            pond_ids[record["entity_id"]] = true
    var updated: Array[String] = []
    var skipped: Array[String] = []
    var metrics: Dictionary = {}
    chunk_records.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
        return String(a["entity_id"]) < String(b["entity_id"]))
    for record in chunk_records:
        var entity_id := String(record["entity_id"])
        if not bool(record.get("canonical_committed", false)):
            skipped.append(entity_id)
            metrics[entity_id] = {"reason": "NOT_CANONICAL_COMMITTED"}
            continue
        if FARM_MODULES.has(String(record.get("module_id", ""))):
            var pond_available := false
            for source_id in record.get("nearby_source_ids", []):
                if pond_ids.has(source_id):
                    pond_available = true
                    break
            var advanced := AIdleTier3FarmSolver.advance(
                record["state"], float(time_info["used_elapsed_seconds"]), config, pond_available)
            var persisted := persistence.update_existing_state(entity_id, advanced["state"])
            if not persisted["passed"]:
                return persisted
            updated.append(entity_id)
            metrics[entity_id] = advanced["metrics"]
        else:
            skipped.append(entity_id)
            metrics[entity_id] = {"reason": "OUTSIDE_DYNAMIC_PILOT_SCOPE", "byte_identical": true}
    var receipt := {
        "receipt_id": "tier3_%s_%d" % [chunk_id, int(current_wall_clock_unix)],
        "mutation_kind": "TIER3_OFFLINE_ADVANCE",
        "chunk_id": chunk_id,
        "observed_elapsed_seconds": time_info["observed_elapsed_seconds"],
        "used_elapsed_seconds": time_info["used_elapsed_seconds"],
        "time_decision": time_info["time_decision"],
        "updated_entity_ids": updated,
        "skipped_entity_ids": skipped,
        "entity_metrics": metrics,
        "accepted": false,
        "self_accept": false,
        "tier3_source_status": "IMPLEMENTED_HERE_SOURCE_PACKAGE_MISSING",
    }
    offline_advance_completed.emit(receipt)
    return {"passed": true, "records": persistence.snapshot(), "receipt": receipt}

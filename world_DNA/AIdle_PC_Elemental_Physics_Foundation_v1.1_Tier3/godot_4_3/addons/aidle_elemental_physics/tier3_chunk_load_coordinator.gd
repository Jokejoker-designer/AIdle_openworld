class_name AIdleTier3ChunkLoadCoordinator
extends Node

signal records_reconciled_before_spawn(chunk_id: StringName, records: Array, receipt: Dictionary)
signal reconciliation_failed(chunk_id: StringName, error: String)

@export var reconciliation_service_path: NodePath

func reconcile_before_spawn(chunk_id: StringName, records: Array,
        current_wall_clock_unix: float, current_monotonic_msec: int) -> void:
    # Chunk loader must await this signal before spawning interactable entities.
    var service := get_node_or_null(reconciliation_service_path) as AIdleTier3ReconciliationService
    if service == null:
        reconciliation_failed.emit(chunk_id, "Tier 3 reconciliation service unavailable.")
        return
    var result := service.reconcile_chunk(
        String(chunk_id), records, current_wall_clock_unix, current_monotonic_msec)
    if not bool(result.get("passed", false)):
        reconciliation_failed.emit(chunk_id, String(result.get("error", "Unknown error")))
        return
    records_reconciled_before_spawn.emit(chunk_id, result["records"], result["receipt"])

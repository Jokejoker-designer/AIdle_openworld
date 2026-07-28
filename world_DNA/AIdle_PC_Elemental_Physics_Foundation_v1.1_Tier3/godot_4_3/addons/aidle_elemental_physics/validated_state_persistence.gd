class_name AIdleValidatedStatePersistence
extends Node

signal state_batch_persisted(receipt: Dictionary)

const ALLOWED_STATE_FIELDS := {
    "wetness": true, "growth": true, "health": true, "temperature": true,
    "integrity": true, "charge": true, "pressure": true, "states": true,
    "visual_variant": true, "light": true, "fertility": true,
    "temperature_fit": true,
}
var _records: Dictionary = {}

func load_existing_records(records: Array) -> void:
    _records.clear()
    for record in records:
        _records[record["entity_id"]] = record.duplicate(true)

func update_existing_state(entity_id: String, state: Dictionary) -> Dictionary:
    if not _records.has(entity_id):
        return {"passed": false, "error": "Tier 3 may not create entities."}
    var record: Dictionary = _records[entity_id]
    if not bool(record.get("canonical_committed", false)):
        return {"passed": false, "error": "Entity is not canonical committed."}
    for key in state:
        if not ALLOWED_STATE_FIELDS.has(key):
            return {"passed": false, "error": "Forbidden Tier 3 state field: %s" % key}
    record["state"] = state.duplicate(true)
    _records[entity_id] = record
    return {"passed": true}

func snapshot() -> Array:
    var ids := _records.keys()
    ids.sort()
    var result: Array = []
    for entity_id in ids:
        result.append(_records[entity_id].duplicate(true))
    return result

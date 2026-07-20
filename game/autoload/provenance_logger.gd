## ProvenanceLogger – Master Blueprint §2.5 + Common Contracts §1.3.
## Every manifested object must keep immutable provenance after commit.
extends Node

## In-memory ring for debug overlay; file log is append-only.
const MAX_MEMORY_ENTRIES := 256

var _entries: Array[Dictionary] = []
var _file: FileAccess


func _ready() -> void:
	_ensure_log_file()
	EventBus.manifestation_completed.connect(_on_manifestation_completed)
	EventBus.manifestation_started.connect(_on_manifestation_started)
	EventBus.random_alchemist_gift.connect(_on_alchemist)


func _ensure_log_file() -> void:
	var path := AIdleConstants.PROVENANCE_LOG_PATH
	var user_root := DirAccess.open("user://")
	if user_root:
		user_root.make_dir_recursive("logs")
	if FileAccess.file_exists(path):
		_file = FileAccess.open(path, FileAccess.READ_WRITE)
		if _file:
			_file.seek_end()
	else:
		_file = FileAccess.open(path, FileAccess.WRITE_READ)
	if _file == null:
		push_warning("[ProvenanceLogger] Could not open log file.")


## Record a provenance blob. Never mutates an existing committed record.
func log_provenance(prompt_id: String, provenance: Dictionary, extra: Dictionary = {}) -> void:
	var record := {
		"prompt_id": prompt_id,
		"timestamp": Time.get_datetime_string_from_system(true),
		"provenance": provenance.duplicate(true),
		"extra": extra.duplicate(true),
	}
	_entries.append(record)
	if _entries.size() > MAX_MEMORY_ENTRIES:
		_entries.pop_front()
	_append_file(record)


func get_recent(limit: int = 20) -> Array:
	var n: int = mini(limit, _entries.size())
	return _entries.slice(_entries.size() - n, _entries.size())


func find_by_prompt_id(prompt_id: String) -> Dictionary:
	for i in range(_entries.size() - 1, -1, -1):
		if str(_entries[i].get("prompt_id", "")) == prompt_id:
			return _entries[i].duplicate(true)
	return {}


func _append_file(record: Dictionary) -> void:
	if _file == null:
		return
	_file.store_line(JSON.stringify(record))
	_file.flush()


func _on_manifestation_started(prompt_id: String, target_space: String, provenance: Dictionary) -> void:
	log_provenance(prompt_id, provenance, {"event": "started", "target_space": target_space})


func _on_manifestation_completed(prompt_id: String, provenance: Dictionary) -> void:
	log_provenance(prompt_id, provenance, {"event": "completed"})


func _on_alchemist(prompt_id: String, companion_id: String, provenance: Dictionary) -> void:
	var p := provenance.duplicate(true)
	p["source_type"] = "random_alchemist"
	p["companion_id"] = companion_id
	log_provenance(prompt_id, p, {"event": "alchemist_gift"})

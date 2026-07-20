## PersistModule — Offline Private Reality local journal (G4-001).
## Append-only mutation log + deterministic entity hashes.
## Authority: local simulation durability only; online/shared still World Commit.
class_name PersistModule
extends Node

const MODULE_ID := "persist"
const SCHEMA_VERSION := "1.0.0"
const _IPersist = preload("res://scripts/modules/interfaces/i_persist_module.gd")
const _JournalStore = preload("res://scripts/modules/persist/journal_store.gd")
const _Canon = preload("res://scripts/modules/persist/canonical_json.gd")
const _Hasher = preload("res://scripts/modules/persist/entity_hasher.gd")

var _store: RefCounted


func _ready() -> void:
	_store = _JournalStore.new()
	_try_register()
	var missing: PackedStringArray = _IPersist.validate(self)
	if not missing.is_empty():
		push_error("[PersistModule] Missing API methods: %s" % str(missing))
	print("[PersistModule] Ready – Private Reality journal (schema %s)." % SCHEMA_VERSION)


func _try_register() -> void:
	var existing: Node = ModuleRegistry.get_module(MODULE_ID)
	if existing == null or existing == self or existing.has_method("is_stub"):
		ModuleRegistry.register_module(MODULE_ID, self)


func is_stub() -> bool:
	return false


func get_status() -> String:
	if _store == null or not _store.has_journal():
		return "persist ready (no journal open)"
	return "persist journal rev=%d entities=%d" % [
		_store.get_world_revision(),
		_store.list_entity_ids().size(),
	]


func get_schema_version() -> String:
	return SCHEMA_VERSION


func create_journal(
	space_id: String,
	base_world_revision: int,
	base_snapshot_id: String = "",
	session_id: String = ""
) -> Dictionary:
	_ensure_store()
	return _store.create_journal(space_id, base_world_revision, base_snapshot_id, session_id)


func load_journal(path: String) -> Dictionary:
	_ensure_store()
	return _store.load_journal(path)


func save_journal(path: String) -> Dictionary:
	_ensure_store()
	return _store.save_journal(path)


func apply_mutation(request: Dictionary) -> Dictionary:
	_ensure_store()
	return _store.apply_mutation(request)


func apply_compensation(request: Dictionary) -> Dictionary:
	_ensure_store()
	return _store.apply_compensation(request)


func get_world_revision() -> int:
	_ensure_store()
	return _store.get_world_revision()


func get_entity(entity_id: String) -> Variant:
	_ensure_store()
	return _store.get_entity(entity_id)


func list_entity_ids() -> PackedStringArray:
	_ensure_store()
	return _store.list_entity_ids()


func entity_hash(entity_id: String) -> String:
	_ensure_store()
	return _store.entity_hash(entity_id)


func entity_set_hash() -> String:
	_ensure_store()
	return _store.entity_set_hash()


func canonical_stringify(value: Variant) -> String:
	return _Canon.stringify(value)


func sha256_hex(utf8_text: String) -> String:
	return _Hasher.sha256_hex(utf8_text)


func replay_to_entities(path: String = "") -> Dictionary:
	_ensure_store()
	if not path.is_empty():
		var loaded: Dictionary = _store.load_journal(path)
		if not bool(loaded.get("ok", false)):
			return loaded
	return _store.replay_to_entities()


func get_entries() -> Array:
	_ensure_store()
	return _store.get_entries()


func get_journal_snapshot() -> Dictionary:
	_ensure_store()
	return _store.get_journal_snapshot()


func entry_count() -> int:
	_ensure_store()
	return _store.entry_count()


func get_store() -> RefCounted:
	_ensure_store()
	return _store


func _ensure_store() -> void:
	if _store == null:
		_store = _JournalStore.new()

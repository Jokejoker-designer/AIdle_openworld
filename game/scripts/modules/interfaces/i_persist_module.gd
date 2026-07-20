## Interface contract for Offline Private Reality persistence (G4-001).
## Local signed journal only — NOT Shared District / server economy authority.
class_name IPersistModule
extends RefCounted

## Recommended surface (P0_schema api_surface_for_persist):
## func get_schema_version() -> String
## func create_journal(space_id, base_world_revision, base_snapshot_id, session_id) -> Dictionary
## func load_journal(path) -> Dictionary
## func save_journal(path) -> Dictionary
## func apply_mutation(request) -> Dictionary
## func apply_compensation(request) -> Dictionary
## func get_world_revision() -> int
## func get_entity(entity_id) -> Dictionary|null
## func list_entity_ids() -> PackedStringArray
## func entity_hash(entity_id) -> String
## func entity_set_hash() -> String
## func canonical_stringify(value) -> String
## func sha256_hex(utf8_text) -> String
## func replay_to_entities() -> Dictionary

const REQUIRED_METHODS := [
	"get_schema_version",
	"create_journal",
	"load_journal",
	"save_journal",
	"apply_mutation",
	"apply_compensation",
	"get_world_revision",
	"get_entity",
	"list_entity_ids",
	"entity_hash",
	"entity_set_hash",
	"canonical_stringify",
	"sha256_hex",
	"replay_to_entities",
]


static func validate(module: Object) -> PackedStringArray:
	var missing: PackedStringArray = []
	for m in REQUIRED_METHODS:
		if not module.has_method(m):
			missing.append(m)
	return missing

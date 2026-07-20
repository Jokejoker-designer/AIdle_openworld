## SHA-256 entity / entity-set hashes over aidle_canonical_json_v1 UTF-8.
## Uses HashingContext only (no MD5, no Dictionary hash()).
class_name AIdleEntityHasher
extends RefCounted

const _Canon = preload("res://scripts/modules/persist/canonical_json.gd")

## Canonical durable entity fields (MVP). Unknown keys dropped before hash.
const ENTITY_FIELD_KEYS := [
	"entity_id",
	"kind",
	"recipe_id",
	"transform",
	"bounds",
	"interaction_tags",
	"space_id",
	"chunk_id",
	"status",
	"origin_request_id",
	"origin_prompt_id",
]


static func sha256_hex(utf8_text: String) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(utf8_text.to_utf8_buffer())
	var digest: PackedByteArray = ctx.finish()
	return _to_hex_lower(digest)


static func _to_hex_lower(bytes: PackedByteArray) -> String:
	var out := ""
	for b in bytes:
		out += "%02x" % b
	return out


## Normalize entity to hash material: known fields only, sorted tags, no noise.
static func canonicalize_entity(entity: Dictionary) -> Dictionary:
	var out: Dictionary = {}
	if entity.has("entity_id"):
		out["entity_id"] = str(entity["entity_id"])
	if entity.has("kind"):
		out["kind"] = str(entity["kind"])
	if entity.has("recipe_id"):
		out["recipe_id"] = str(entity["recipe_id"])
	if entity.has("transform") and entity["transform"] is Dictionary:
		var tr: Dictionary = entity["transform"]
		out["transform"] = {
			"x": num_field(tr.get("x", 0)),
			"y": num_field(tr.get("y", 0)),
			"elevation": num_field(tr.get("elevation", 0)),
			"rotation_deg": num_field(tr.get("rotation_deg", 0)),
		}
	if entity.has("bounds") and entity["bounds"] is Dictionary:
		var b: Dictionary = entity["bounds"]
		out["bounds"] = {
			"width": num_field(b.get("width", 0)),
			"depth": num_field(b.get("depth", 0)),
			"height": num_field(b.get("height", 0)),
		}
	if entity.has("interaction_tags"):
		var tags: Array = []
		var raw = entity["interaction_tags"]
		if raw is Array or raw is PackedStringArray:
			for t in raw:
				tags.append(str(t))
		out["interaction_tags"] = _Canon.sorted_unique_strings(tags)
	if entity.has("space_id"):
		out["space_id"] = str(entity["space_id"])
	if entity.has("chunk_id") and str(entity["chunk_id"]) != "":
		out["chunk_id"] = str(entity["chunk_id"])
	if entity.has("status"):
		out["status"] = str(entity["status"])
	else:
		out["status"] = "active"
	if entity.has("origin_request_id"):
		out["origin_request_id"] = str(entity["origin_request_id"])
	if entity.has("origin_prompt_id"):
		out["origin_prompt_id"] = str(entity["origin_prompt_id"])
	return out


static func num_field(v: Variant) -> Variant:
	# Prefer int when whole number so canonical form has no decimal for grid coords.
	if typeof(v) == TYPE_INT:
		return v as int
	if typeof(v) == TYPE_FLOAT:
		var f: float = v as float
		if is_equal_approx(f, round(f)) and absf(f) < 1e15:
			return int(round(f))
		return f
	if typeof(v) == TYPE_STRING:
		if (v as String).is_valid_int():
			return (v as String).to_int()
		if (v as String).is_valid_float():
			return (v as String).to_float()
	return 0


## Back-compat alias used by journal_store.
static func _num(v: Variant) -> Variant:
	return num_field(v)


static func entity_hash(entity: Dictionary) -> String:
	var canon: Dictionary = canonicalize_entity(entity)
	var material: String = _Canon.stringify(canon)
	return sha256_hex(material)


## Hash active entity set: array of canonical entities sorted by entity_id.
## Tombstones (status=tombstoned) are excluded from the active set hash.
static func entity_set_hash(entities_by_id: Dictionary) -> String:
	var arr: Array = active_entity_array(entities_by_id)
	var material: String = _Canon.stringify(arr)
	return sha256_hex(material)


static func active_entity_array(entities_by_id: Dictionary) -> Array:
	var ids: Array = entities_by_id.keys()
	ids.sort()
	var arr: Array = []
	for eid in ids:
		var ent: Dictionary = entities_by_id[eid]
		if not (ent is Dictionary):
			continue
		var status: String = str(ent.get("status", "active"))
		if status == "tombstoned":
			continue
		arr.append(canonicalize_entity(ent))
	return arr

## Fail-closed allowlist gate for Block Assembly (consume accepted DNA adapter catalogs).
## Rejects unknown modules, sockets, normalizations, materials, out-of-budget placement.
class_name BlockCatalogGate
extends RefCounted

const _C = preload("res://scripts/modules/block_assembly/block_assembly_constants.gd")

var _loaded: bool = false
var _modules: Dictionary = {}  # id -> true
var _materials: Dictionary = {}  # MAT_* -> true
var _slots: Dictionary = {}  # semantic slot -> true
var _slot_to_mat: Dictionary = {}
var _mat_to_slot: Dictionary = {}
var _world_profiles: Dictionary = {}
var _norms: Dictionary = {}  # normalization_id -> true
var _sockets: Dictionary = {}  # socket_type -> true
var _load_error: String = ""


func ensure_loaded() -> bool:
	if _loaded:
		return _load_error.is_empty()
	_loaded = true
	var cat: Variant = _load_json(_C.RUNTIME_CATALOG_PATH)
	var sock: Variant = _load_json(_C.SOCKET_RULES_PATH)
	if cat == null or not (cat is Dictionary):
		_load_error = "runtime_catalog_missing"
		return false
	if sock == null or not (sock is Dictionary):
		_load_error = "socket_rules_missing"
		return false
	var c: Dictionary = cat
	for m in c.get("module_ids", []):
		_modules[str(m)] = true
	for s in c.get("semantic_material_slots", []):
		_slots[str(s)] = true
	for m in c.get("live_p1e_material_ids", []):
		_materials[str(m)] = true
	var stm: Dictionary = c.get("slot_to_material", {}) as Dictionary
	for k in stm.keys():
		_slot_to_mat[str(k)] = str(stm[k])
	var mts: Dictionary = c.get("material_to_slot", {}) as Dictionary
	for k in mts.keys():
		_mat_to_slot[str(k)] = str(mts[k])
	for w in c.get("world_profiles", []):
		_world_profiles[str(w)] = true
	var s: Dictionary = sock
	for st in s.get("socket_types", []):
		if st is Dictionary:
			_sockets[str((st as Dictionary).get("socket_type", ""))] = true
	for n in s.get("adapter_normalizations", []):
		if n is Dictionary:
			_norms[str((n as Dictionary).get("normalization_id", ""))] = true
	return true


func get_load_error() -> String:
	ensure_loaded()
	return _load_error


func is_module_allowed(module_id: String) -> bool:
	ensure_loaded()
	return _modules.has(module_id)


func get_allowlisted_module_ids() -> PackedStringArray:
	## Stable sorted order for player-facing picker cycle.
	ensure_loaded()
	var ids: Array = _modules.keys()
	ids.sort()
	var out := PackedStringArray()
	for m in ids:
		out.append(str(m))
	return out


func is_socket_known(socket_type: String) -> bool:
	ensure_loaded()
	return _sockets.has(socket_type)


func is_normalization_known(norm_id: String) -> bool:
	ensure_loaded()
	return _norms.has(norm_id)


func is_material_slot_known(slot: String) -> bool:
	ensure_loaded()
	return _slots.has(slot)


func is_p1e_material_known(mat_id: String) -> bool:
	ensure_loaded()
	return _materials.has(mat_id)


func is_world_profile_known(profile_id: String) -> bool:
	ensure_loaded()
	return _world_profiles.has(profile_id)


func resolve_material_for_slot(slot: String) -> String:
	ensure_loaded()
	return str(_slot_to_mat.get(slot, ""))


func validate_module_selection(module_id: String) -> Dictionary:
	ensure_loaded()
	if not _load_error.is_empty():
		return {"ok": false, "code": "catalog_unavailable", "reason": _load_error}
	if module_id.is_empty():
		return {"ok": false, "code": "unknown_module", "reason": "empty module_id"}
	if not is_module_allowed(module_id):
		return {
			"ok": false,
			"code": "unknown_module",
			"reason": "module_id not in accepted allowlist: %s" % module_id,
		}
	return {"ok": true, "module_id": module_id}


func validate_material_pair(slot: String, p1e_material_id: String) -> Dictionary:
	ensure_loaded()
	if not is_material_slot_known(slot):
		return {"ok": false, "code": "unknown_material_slot", "reason": "slot=%s" % slot}
	if not is_p1e_material_known(p1e_material_id):
		return {
			"ok": false,
			"code": "unknown_material",
			"reason": "p1e_material_id=%s" % p1e_material_id,
		}
	var expected := resolve_material_for_slot(slot)
	if expected.is_empty() or expected != p1e_material_id:
		# Bidirectional co-require: reverse mapping must match.
		var reverse_slot := str(_mat_to_slot.get(p1e_material_id, ""))
		if reverse_slot != slot and expected != p1e_material_id:
			return {
				"ok": false,
				"code": "material_slot_mismatch",
				"reason": "slot=%s expects=%s got=%s" % [slot, expected, p1e_material_id],
			}
	return {"ok": true, "slot": slot, "p1e_material_id": p1e_material_id}


func validate_budget_transform(x: float, y: float, elevation: float) -> Dictionary:
	## Fail closed when placement escapes accepted bounds_max_m budget.
	if absf(x) > _C.BOUNDS_MAX_WIDTH_M * 0.5:
		return {"ok": false, "code": "budget_fail", "reason": "x outside bounds_max width"}
	if absf(y) > _C.BOUNDS_MAX_DEPTH_M * 0.5:
		return {"ok": false, "code": "budget_fail", "reason": "y outside bounds_max depth"}
	if elevation < 0.0 or elevation > _C.BOUNDS_MAX_HEIGHT_M:
		return {"ok": false, "code": "budget_fail", "reason": "elevation outside bounds_max height"}
	return {"ok": true}


func missing_asset_request(module_id: String, reason: String = "missing_runtime_asset") -> Dictionary:
	## Asset Request proposal only — never executable code / network / fs write.
	return {
		"kind": "asset_request",
		"schema_version": "block_dna_adapt_001_asset_request/1.0",
		"module_id": module_id,
		"reason": reason,
		"executable_code": null,
		"network": false,
		"filesystem_write": false,
		"arbitrary_code": false,
	}


static func _load_json(path: String) -> Variant:
	if not FileAccess.file_exists(path):
		return null
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return null
	var text := f.get_as_text()
	f.close()
	var parsed: Variant = JSON.parse_string(text)
	return parsed

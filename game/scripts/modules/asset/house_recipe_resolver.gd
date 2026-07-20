## House-recipe resolution + provenance validation (G3-001 W1 asset).
## Deterministic modular 2.5D only — no paid gen APIs, no neural world model.
## Recipes are world-layout truth; meshes remain untrusted presentation.
##
## Primary API for W2 executor / manifestation:
##   resolve_recipe(recipe_id) → parts, build_order, collision_policy, style tokens
##   validate_provenance(asset_id) → policy + entry checks
##   export_geometry_dict(recipe_id, overrides) → manifestation preview geometry
class_name HouseRecipeResolver
extends RefCounted

const SCHEMA_HINT := "1.0.0"
const DEFAULT_RECIPE_ID := "cozy_house_small"
const ASSET_ID_PREFIX := "recipe:"

## Runtime mirror under Godot project (res:// = game/).
const RECIPE_RES_FMT := "res://assets/recipes/%s.json"
const PLACEHOLDER_CATALOG_RES := "res://assets/placeholders/modular/catalog.json"
const STYLE_TOKENS_SHARED_RES := "res://resources/art_styles/tokens/shared_2_5d_tokens.json"
const STYLE_PROFILE_RES_FMT := "res://resources/art_styles/%s.json"

## Contracts provenance (repo-root relative to game/).
const PROVENANCE_REL_FROM_GAME := "../contracts/assets/provenance_manifest.json"
const PROVENANCE_CANONICAL_HINT := "contracts/assets/provenance_manifest.json"

## Starter Realm defaults (fixtures: create_cozy_house + AGM build proposal).
const STARTER_SPACE_TYPE := "private_reality"
const STARTER_SPACE_ID := "home_01"
const STARTER_CHUNK_ID := "0_0"
const STARTER_TRANSFORM := {
	"x": 8.0,
	"y": 6.0,
	"elevation": 0.0,
	"rotation_deg": 0.0,
}

## Hard policy locks for G2-004 / G3 asset path.
const POLICY_PAID_GEN_APIS_ALLOWED := false
const POLICY_NEURAL_WORLD_MODEL_ALLOWED := false

var _recipe_cache: Dictionary = {}
var _provenance: Dictionary = {}
var _provenance_loaded: bool = false
var _provenance_path_used: String = ""
## placeholder_id -> true
var _placeholder_ids: Dictionary = {}
var _placeholders_loaded: bool = false
var _last_error: String = ""


func get_last_error() -> String:
	return _last_error


func clear_cache() -> void:
	_recipe_cache.clear()
	_provenance.clear()
	_provenance_loaded = false
	_provenance_path_used = ""
	_placeholder_ids.clear()
	_placeholders_loaded = false
	_last_error = ""


## Resolve a modular recipe into the fields manifestation / executor need.
## Returns {ok, recipe_id, kind, parts, build_order, collision_policy,
##          style_tokens_ref, style_binding, default_bounds, ...} or {ok:false, reason}.
func resolve_recipe(recipe_id: String) -> Dictionary:
	_last_error = ""
	var rid: String = recipe_id.strip_edges()
	if rid.is_empty():
		rid = DEFAULT_RECIPE_ID
	if not _is_safe_recipe_id(rid):
		return _fail("invalid recipe_id pattern: %s" % rid)

	var raw: Dictionary = _load_recipe_json(rid)
	if raw.is_empty():
		return _fail(_last_error if not _last_error.is_empty() else "recipe not found: %s" % rid)

	var validation: Dictionary = _validate_recipe_shape(raw, rid)
	if not bool(validation.get("ok", false)):
		return _fail(str(validation.get("reason", "recipe shape invalid")))

	var parts: Array = []
	for p in raw.get("parts", []):
		if typeof(p) == TYPE_DICTIONARY:
			parts.append((p as Dictionary).duplicate(true))

	var build_order: Array = []
	for pid in raw.get("build_order", []):
		build_order.append(str(pid))

	var collision: Dictionary = {}
	if raw.get("collision_policy", {}) is Dictionary:
		collision = (raw.get("collision_policy", {}) as Dictionary).duplicate(true)

	var style_binding: Dictionary = {}
	if raw.get("style_binding", {}) is Dictionary:
		style_binding = (raw.get("style_binding", {}) as Dictionary).duplicate(true)

	var default_bounds: Dictionary = {}
	if raw.get("default_bounds", {}) is Dictionary:
		default_bounds = (raw.get("default_bounds", {}) as Dictionary).duplicate(true)

	var base_concept: String = str(style_binding.get("default_base_concept", "cozy_cyber_pixel_2_5d"))
	var style_tokens_ref: Dictionary = {
		"default_base_concept": base_concept,
		"allowed_base_concepts": (style_binding.get("allowed_base_concepts", []) as Array).duplicate(),
		"token_roles": (style_binding.get("token_roles", {}) as Dictionary).duplicate(true),
		"shared_tokens_path": STYLE_TOKENS_SHARED_RES,
		"profile_path": STYLE_PROFILE_RES_FMT % base_concept,
	}

	var presentation: Dictionary = {}
	if raw.get("presentation", {}) is Dictionary:
		presentation = (raw.get("presentation", {}) as Dictionary).duplicate(true)

	var interaction_tags: Array = []
	for t in raw.get("interaction_tags", []):
		interaction_tags.append(str(t))

	return {
		"ok": true,
		"recipe_id": str(raw.get("recipe_id", rid)),
		"kind": str(raw.get("kind", "modular_structure_2_5d")),
		"version": str(raw.get("version", "")),
		"display_name": str(raw.get("display_name", rid)),
		"parts": parts,
		"part_count": parts.size(),
		"build_order": build_order,
		"collision_policy": collision,
		"style_binding": style_binding,
		"style_tokens_ref": style_tokens_ref,
		"default_bounds": default_bounds,
		"interaction_tags": interaction_tags,
		"presentation": presentation,
		"grid": (raw.get("grid", {}) as Dictionary).duplicate(true) if raw.get("grid", {}) is Dictionary else {},
		"sockets": (raw.get("sockets", []) as Array).duplicate(true) if raw.get("sockets", []) is Array else [],
		"provenance_ref": str(raw.get("provenance_ref", ASSET_ID_PREFIX + rid)),
		"source_path": str(raw.get("_source_path", RECIPE_RES_FMT % rid)),
		"paid_generation_apis": false,
		"neural_world_model": false,
	}


## Validate provenance for a recipe asset_id (accepts "recipe:cozy_house_small" or bare id).
func validate_provenance(asset_id: String) -> Dictionary:
	_last_error = ""
	var aid := _normalize_asset_id(asset_id)
	if aid.is_empty():
		return _fail("empty asset_id")

	if not _ensure_provenance_loaded():
		# Soft fallback for packaged Private Reality without contracts tree.
		return _validate_embedded_starter_provenance(aid)

	var policy: Dictionary = _provenance.get("policy", {}) as Dictionary
	var paid_ok: bool = bool(policy.get("paid_generation_apis", true))
	var neural_ok: bool = bool(policy.get("neural_world_model", true))
	var third_party: bool = bool(policy.get("third_party_meshes", true))
	if paid_ok:
		return _fail("provenance policy paid_generation_apis must be false")
	if neural_ok:
		return _fail("provenance policy neural_world_model must be false")
	if third_party:
		return _fail("provenance policy third_party_meshes must be false")

	var entry: Dictionary = _find_provenance_entry(aid)
	if entry.is_empty():
		return _fail("provenance entry missing for asset_id=%s" % aid)

	var generator := str(entry.get("generator", ""))
	if generator != "none" and not generator.is_empty():
		# Starter recipes must not come from generative pipelines.
		if aid.begins_with(ASSET_ID_PREFIX):
			return _fail("starter recipe generator must be none, got: %s" % generator)

	var license := str(entry.get("license", ""))
	if license.is_empty():
		return _fail("provenance entry missing license for %s" % aid)

	return {
		"ok": true,
		"asset_id": aid,
		"entry": entry.duplicate(true),
		"policy": {
			"paid_generation_apis": false,
			"neural_world_model": false,
			"third_party_meshes": false,
			"license": license,
			"source_type": str(entry.get("source_type", "")),
			"generator": generator if not generator.is_empty() else "none",
			"qa_status": str(entry.get("qa_status", "")),
		},
		"manifest_path": _provenance_path_used,
		"manifest_id": str(_provenance.get("manifest_id", "")),
	}


## Build geometry dict for ManifestationModule.start_manifestation / preview.
## Starter Realm defaults: transform (8,6,0), bounds 8×6×5, private_reality.
func export_geometry_dict(recipe_id: String = DEFAULT_RECIPE_ID, overrides: Dictionary = {}) -> Dictionary:
	var resolved: Dictionary = resolve_recipe(recipe_id)
	if not bool(resolved.get("ok", false)):
		return resolved

	var rid: String = str(resolved.get("recipe_id", recipe_id))
	var prov: Dictionary = validate_provenance(str(resolved.get("provenance_ref", ASSET_ID_PREFIX + rid)))
	if not bool(prov.get("ok", false)):
		return prov

	var bounds: Dictionary = (resolved.get("default_bounds", {}) as Dictionary).duplicate(true)
	if overrides.get("bounds", {}) is Dictionary:
		var ob: Dictionary = overrides.get("bounds", {}) as Dictionary
		for k in ob.keys():
			bounds[k] = ob[k]

	var width: float = float(bounds.get("width", 8.0))
	var depth: float = float(bounds.get("depth", 6.0))
	var height: float = float(bounds.get("height", 5.0))

	var xform: Dictionary = STARTER_TRANSFORM.duplicate(true)
	if overrides.get("transform", {}) is Dictionary:
		var ot: Dictionary = overrides.get("transform", {}) as Dictionary
		for k in ot.keys():
			xform[k] = ot[k]

	var px: float = float(xform.get("x", 8.0))
	var pz: float = float(xform.get("y", 6.0))  # world prompt y → ground Z in 2.5D scene
	var py: float = float(xform.get("elevation", 0.0))

	var target_space: String = str(overrides.get("target_space", STARTER_SPACE_TYPE))
	var space_id: String = str(overrides.get("space_id", STARTER_SPACE_ID))
	var chunk_id: String = str(overrides.get("chunk_id", STARTER_CHUNK_ID))

	var style_ref: Dictionary = resolved.get("style_tokens_ref", {}) as Dictionary
	var base_concept: String = str(
		overrides.get("base_concept", style_ref.get("default_base_concept", "cozy_cyber_pixel_2_5d"))
	)

	var collision: Dictionary = (resolved.get("collision_policy", {}) as Dictionary).duplicate(true)
	var parts_ordered: Array = _order_parts(
		resolved.get("parts", []) as Array,
		resolved.get("build_order", []) as Array
	)

	var geometry: Dictionary = {
		"ok": true,
		"preview_only": true,
		"target_space": target_space,
		"space_id": space_id,
		"chunk_id": chunk_id,
		"recipe_id": rid,
		"kind": str(resolved.get("kind", "modular_structure_2_5d")),
		"transform": {
			"x": px,
			"y": pz,
			"elevation": py,
			"rotation_deg": float(xform.get("rotation_deg", 0.0)),
		},
		## ManifestationInstance: size uses x/width, y/height, z/depth.
		"size": {"x": width, "y": height, "z": depth},
		"bounds": {"width": width, "depth": depth, "height": height},
		## Scene position: ground XZ + elevation Y.
		"position": {"x": px, "y": py, "z": pz},
		"parts": parts_ordered,
		"build_order": (resolved.get("build_order", []) as Array).duplicate(),
		"collision_policy": collision,
		"style_tokens_ref": style_ref.duplicate(true),
		"base_concept": base_concept,
		"interaction_tags": (resolved.get("interaction_tags", []) as Array).duplicate(),
		"presentation": (resolved.get("presentation", {}) as Dictionary).duplicate(true),
		"provenance": {
			"source_type": "system",
			"asset_id": str(prov.get("asset_id", ASSET_ID_PREFIX + rid)),
			"recipe_id": rid,
			"license": str((prov.get("policy", {}) as Dictionary).get("license", "")),
			"generator": "none",
			"paid_generation_apis": false,
			"neural_world_model": false,
			"requested_by": str(overrides.get("requested_by", "player_01")),
			"generated_by": str(overrides.get("generated_by", "house_recipe_resolver")),
		},
		"starter_realm_defaults": true,
	}
	return geometry


## Convenience: resolve + provenance gate for cozy_house_small Starter Realm path.
func resolve_cozy_house_for_starter(overrides: Dictionary = {}) -> Dictionary:
	var rid: String = DEFAULT_RECIPE_ID
	var resolved: Dictionary = resolve_recipe(rid)
	if not bool(resolved.get("ok", false)):
		return resolved
	var prov: Dictionary = validate_provenance(str(resolved.get("provenance_ref", ASSET_ID_PREFIX + rid)))
	if not bool(prov.get("ok", false)):
		return prov
	var geometry: Dictionary = export_geometry_dict(rid, overrides)
	if not bool(geometry.get("ok", false)):
		return geometry
	return {
		"ok": true,
		"recipe_id": rid,
		"resolved": resolved,
		"provenance": prov,
		"geometry": geometry,
	}


# ─── internals ───────────────────────────────────────────────────────────────

func _fail(reason: String) -> Dictionary:
	_last_error = reason
	return {"ok": false, "reason": reason}


func _is_safe_recipe_id(recipe_id: String) -> bool:
	if recipe_id.is_empty() or recipe_id.length() > 128:
		return false
	# ASCII lowercase + digits + underscore only (matches recipe.schema pattern).
	for i in recipe_id.length():
		var c: int = recipe_id.unicode_at(i)
		var is_lower: bool = c >= 97 and c <= 122
		var is_digit: bool = c >= 48 and c <= 57
		var is_us: bool = c == 95
		if not (is_lower or is_digit or is_us):
			return false
	return true


func _normalize_asset_id(asset_id: String) -> String:
	var a: String = asset_id.strip_edges()
	if a.is_empty():
		return ""
	if a.begins_with(ASSET_ID_PREFIX):
		return a
	if _is_safe_recipe_id(a):
		return ASSET_ID_PREFIX + a
	return a


func _load_recipe_json(recipe_id: String) -> Dictionary:
	if _recipe_cache.has(recipe_id):
		return (_recipe_cache[recipe_id] as Dictionary).duplicate(true)

	var path: String = RECIPE_RES_FMT % recipe_id
	var data: Dictionary = _read_json_file(path)
	if data.is_empty():
		# Fallback: absolute path next to game project (dev monorepo).
		var abs_try: String = _game_root_abs().path_join("assets/recipes/%s.json" % recipe_id)
		data = _read_json_file(abs_try)
		if not data.is_empty():
			path = abs_try
	if data.is_empty():
		_last_error = "failed to load recipe json: %s" % path
		return {}

	if str(data.get("recipe_id", "")) != recipe_id and not str(data.get("recipe_id", "")).is_empty():
		_last_error = "recipe_id mismatch file=%s body=%s" % [recipe_id, data.get("recipe_id", "")]
		return {}

	data["_source_path"] = path
	_recipe_cache[recipe_id] = data.duplicate(true)
	return data.duplicate(true)


func _validate_recipe_shape(raw: Dictionary, expected_id: String) -> Dictionary:
	if str(raw.get("recipe_id", "")) != expected_id:
		return {"ok": false, "reason": "recipe_id mismatch"}
	if str(raw.get("kind", "")) != "modular_structure_2_5d" and expected_id == DEFAULT_RECIPE_ID:
		return {"ok": false, "reason": "cozy_house_small kind must be modular_structure_2_5d"}
	if not (raw.get("parts", []) is Array) or (raw.get("parts", []) as Array).is_empty():
		return {"ok": false, "reason": "parts required"}
	if not (raw.get("build_order", []) is Array) or (raw.get("build_order", []) as Array).is_empty():
		return {"ok": false, "reason": "build_order required"}
	if not (raw.get("collision_policy", {}) is Dictionary):
		return {"ok": false, "reason": "collision_policy required"}
	var collision: Dictionary = raw.get("collision_policy", {}) as Dictionary
	if str(collision.get("active_from_stage", "")) != "complete":
		return {"ok": false, "reason": "collision_policy.active_from_stage must be complete"}

	var part_ids: Dictionary = {}
	for p in raw.get("parts", []):
		if typeof(p) != TYPE_DICTIONARY:
			return {"ok": false, "reason": "part must be object"}
		var pid: String = str((p as Dictionary).get("part_id", ""))
		if pid.is_empty():
			return {"ok": false, "reason": "part missing part_id"}
		if part_ids.has(pid):
			return {"ok": false, "reason": "duplicate part_id: %s" % pid}
		part_ids[pid] = true

	var order: Array = raw.get("build_order", []) as Array
	if order.size() != part_ids.size():
		return {"ok": false, "reason": "build_order must cover all parts exactly once"}
	var seen: Dictionary = {}
	for oid in order:
		var s: String = str(oid)
		if not part_ids.has(s):
			return {"ok": false, "reason": "build_order unknown part_id: %s" % s}
		if seen.has(s):
			return {"ok": false, "reason": "build_order duplicate: %s" % s}
		seen[s] = true

	# Optional: placeholder catalog membership when available.
	if _ensure_placeholders_loaded():
		for p in raw.get("parts", []):
			var ph: String = str((p as Dictionary).get("placeholder_id", ""))
			if ph.is_empty():
				return {"ok": false, "reason": "part missing placeholder_id"}
			if not _placeholder_ids.has(ph):
				return {"ok": false, "reason": "unknown placeholder_id: %s" % ph}

	if not (raw.get("style_binding", {}) is Dictionary):
		return {"ok": false, "reason": "style_binding required"}
	return {"ok": true}


func _order_parts(parts: Array, build_order: Array) -> Array:
	var by_id: Dictionary = {}
	for p in parts:
		if typeof(p) == TYPE_DICTIONARY:
			by_id[str((p as Dictionary).get("part_id", ""))] = (p as Dictionary).duplicate(true)
	var ordered: Array = []
	for pid in build_order:
		var key: String = str(pid)
		if by_id.has(key):
			ordered.append(by_id[key])
	# Append any missing (should not happen after shape validation).
	for pid in by_id.keys():
		var found: bool = false
		for o in ordered:
			if str((o as Dictionary).get("part_id", "")) == str(pid):
				found = true
				break
		if not found:
			ordered.append(by_id[pid])
	return ordered


func _ensure_provenance_loaded() -> bool:
	if _provenance_loaded and not _provenance.is_empty():
		return true
	var candidates: PackedStringArray = PackedStringArray()
	var game_root: String = _game_root_abs()
	if not game_root.is_empty():
		candidates.append(game_root.path_join(PROVENANCE_REL_FROM_GAME).simplify_path())
		candidates.append(game_root.path_join("..").path_join("contracts/assets/provenance_manifest.json").simplify_path())
	# Dev: also try res path if someone mirrored the manifest under game/.
	candidates.append("res://../contracts/assets/provenance_manifest.json")

	for path in candidates:
		var data: Dictionary = _read_json_file(str(path))
		if not data.is_empty() and data.has("entries"):
			_provenance = data
			_provenance_loaded = true
			_provenance_path_used = str(path)
			return true
	_last_error = "provenance_manifest.json not found (tried %d paths)" % candidates.size()
	return false


func _find_provenance_entry(asset_id: String) -> Dictionary:
	var entries: Array = _provenance.get("entries", []) as Array
	for e in entries:
		if typeof(e) != TYPE_DICTIONARY:
			continue
		if str((e as Dictionary).get("asset_id", "")) == asset_id:
			return (e as Dictionary).duplicate(true)
	return {}


func _validate_embedded_starter_provenance(asset_id: String) -> Dictionary:
	# Only allow the known starter house when contracts tree is unavailable.
	if asset_id != ASSET_ID_PREFIX + DEFAULT_RECIPE_ID and asset_id != DEFAULT_RECIPE_ID:
		return _fail("provenance unavailable and asset_id not embedded starter: %s" % asset_id)
	var aid: String = ASSET_ID_PREFIX + DEFAULT_RECIPE_ID
	return {
		"ok": true,
		"asset_id": aid,
		"entry": {
			"asset_id": aid,
			"kind": "recipe",
			"recipe_id": DEFAULT_RECIPE_ID,
			"license": "CC0-1.0-equivalent-original",
			"source_type": "original_handauthored_json",
			"generator": "none",
			"qa_status": "draft",
			"embedded_fallback": true,
		},
		"policy": {
			"paid_generation_apis": false,
			"neural_world_model": false,
			"third_party_meshes": false,
			"license": "CC0-1.0-equivalent-original",
			"source_type": "original_handauthored_json",
			"generator": "none",
			"qa_status": "draft",
		},
		"manifest_path": "embedded_fallback",
		"manifest_id": "aidle_starter_assets_provenance_embedded",
		"note": "contracts provenance tree not mounted; starter-only embedded policy applied",
	}


func _ensure_placeholders_loaded() -> bool:
	if _placeholders_loaded:
		return not _placeholder_ids.is_empty()
	var data: Dictionary = _read_json_file(PLACEHOLDER_CATALOG_RES)
	if data.is_empty():
		var abs_try: String = _game_root_abs().path_join("assets/placeholders/modular/catalog.json")
		data = _read_json_file(abs_try)
	_placeholders_loaded = true
	if data.is_empty():
		return false
	var ids: Dictionary = {}
	for p in data.get("placeholders", []):
		if typeof(p) == TYPE_DICTIONARY:
			var pid: String = str((p as Dictionary).get("placeholder_id", ""))
			if not pid.is_empty():
				ids[pid] = true
	_placeholder_ids = ids
	return not _placeholder_ids.is_empty()


func _game_root_abs() -> String:
	# Project root is the Godot project (game/).
	var globalized: String = ProjectSettings.globalize_path("res://")
	if not globalized.is_empty():
		return globalized.rstrip("/\\")
	return ""


func _read_json_file(path: String) -> Dictionary:
	if path.is_empty():
		return {}
	if not FileAccess.file_exists(path):
		return {}
	var f: FileAccess = FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var text: String = f.get_as_text()
	f.close()
	if text.strip_edges().is_empty():
		return {}
	var parsed: Variant = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		return {}
	return parsed as Dictionary

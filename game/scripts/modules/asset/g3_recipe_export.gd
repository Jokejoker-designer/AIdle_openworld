## Optional G3 handoff: export cozy_house_small geometry dict for manifestation preview.
## Deterministic, no paid gen / neural world model. Callable headless via -s or from AssetModule.
class_name G3RecipeExport
extends RefCounted

const _Resolver = preload("res://scripts/modules/asset/house_recipe_resolver.gd")

const DEFAULT_EXPORT_RES := "res://scripts/modules/asset/exports/cozy_house_geometry_preview.json"
const RECIPE_ID := "cozy_house_small"


## Build + optionally write geometry export. Returns geometry dict (ok field set).
static func export_cozy_house_geometry(write_file: bool = true, overrides: Dictionary = {}) -> Dictionary:
	var resolver: RefCounted = _Resolver.new() as RefCounted
	var geometry: Dictionary = resolver.call("export_geometry_dict", RECIPE_ID, overrides) as Dictionary
	if not bool(geometry.get("ok", false)):
		return geometry
	if write_file:
		var write_result: Dictionary = write_geometry_json(geometry, DEFAULT_EXPORT_RES)
		geometry["export_path"] = DEFAULT_EXPORT_RES
		geometry["export_written"] = bool(write_result.get("ok", false))
		if not bool(write_result.get("ok", false)):
			geometry["export_write_error"] = str(write_result.get("reason", ""))
	return geometry


static func write_geometry_json(geometry: Dictionary, path: String = DEFAULT_EXPORT_RES) -> Dictionary:
	if path.is_empty():
		return {"ok": false, "reason": "empty path"}
	# Drop non-serializable / runtime-only noise if any; geometry is JSON-safe dicts.
	var payload: Dictionary = geometry.duplicate(true)
	var text: String = JSON.stringify(payload, "\t")
	var abs_path: String = path
	if path.begins_with("res://"):
		abs_path = ProjectSettings.globalize_path(path)
	var dir_path: String = abs_path.get_base_dir()
	DirAccess.make_dir_recursive_absolute(dir_path)
	var open_path: String = path if path.begins_with("res://") else abs_path
	var f: FileAccess = FileAccess.open(open_path, FileAccess.WRITE)
	if f == null:
		# Retry absolute
		f = FileAccess.open(abs_path, FileAccess.WRITE)
	if f == null:
		return {"ok": false, "reason": "FileAccess.open failed for %s" % path}
	f.store_string(text)
	f.close()
	return {"ok": true, "path": path, "abs_path": abs_path}


## Headless entry when run as: godot --path game -s res://scripts/modules/asset/g3_recipe_export.gd
func _init() -> void:
	pass

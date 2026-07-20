## Headless smoke for G3-001 W1 asset: resolve_recipe + provenance + geometry export.
## Run:
##   tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://scripts/modules/asset/g3_recipe_smoke.gd
## Exit 0 on pass. Prints G3_W1_ASSET_SMOKE=PASS|FAIL.
extends SceneTree

const RESOLVER_PATH := "res://scripts/modules/asset/house_recipe_resolver.gd"
const MODULE_PATH := "res://scripts/modules/asset/asset_module.gd"
const EXPORT_PATH := "res://scripts/modules/asset/g3_recipe_export.gd"
const RECIPE_ID := "cozy_house_small"
const ASSET_ID := "recipe:cozy_house_small"

var _failures: PackedStringArray = []
var _passed: int = 0


func _initialize() -> void:
	print("[G3-001 W1 asset smoke] starting…")
	var R: Variant = load(RESOLVER_PATH)
	var M: Variant = load(MODULE_PATH)
	var E: Variant = load(EXPORT_PATH)
	if R == null or not (R is GDScript):
		_fail("load_resolver", "could not load %s" % RESOLVER_PATH)
		_finish()
		return
	if M == null or not (M is GDScript):
		_fail("load_module", "could not load %s" % MODULE_PATH)
	if E == null or not (E is GDScript):
		_fail("load_export", "could not load %s" % EXPORT_PATH)

	var resolver: Object = (R as GDScript).new()
	if resolver == null:
		_fail("resolver_new", "HouseRecipeResolver.new failed")
		_finish()
		return
	var resolved: Dictionary = resolver.call("resolve_recipe", RECIPE_ID) as Dictionary
	if not bool(resolved.get("ok", false)):
		_fail("resolve_recipe", str(resolved.get("reason", "unknown")))
	else:
		_pass("resolve_recipe")
		if int(resolved.get("part_count", 0)) != 14:
			_fail("part_count", "expected 14 got %s" % str(resolved.get("part_count", 0)))
		else:
			_pass("part_count_14")
		var bo: Array = resolved.get("build_order", []) as Array
		if bo.size() != 14:
			_fail("build_order_len", "expected 14")
		else:
			_pass("build_order_len")
		var coll: Dictionary = resolved.get("collision_policy", {}) as Dictionary
		if str(coll.get("active_from_stage", "")) != "complete":
			_fail("collision_policy", "active_from_stage must be complete")
		else:
			_pass("collision_active_from_complete")
		var style_ref: Dictionary = resolved.get("style_tokens_ref", {}) as Dictionary
		if str(style_ref.get("default_base_concept", "")).is_empty():
			_fail("style_tokens_ref", "missing default_base_concept")
		else:
			_pass("style_tokens_ref")

	var prov: Dictionary = resolver.call("validate_provenance", ASSET_ID) as Dictionary
	if not bool(prov.get("ok", false)):
		_fail("validate_provenance", str(prov.get("reason", "unknown")))
	else:
		_pass("validate_provenance")
		var pol: Dictionary = prov.get("policy", {}) as Dictionary
		if pol.get("paid_generation_apis", true) != false:
			_fail("policy_paid_gen", "must be false")
		else:
			_pass("policy_paid_gen_false")
		if pol.get("neural_world_model", true) != false:
			_fail("policy_neural", "must be false")
		else:
			_pass("policy_neural_false")

	var geo: Dictionary = resolver.call("export_geometry_dict", RECIPE_ID, {}) as Dictionary
	if not bool(geo.get("ok", false)):
		_fail("export_geometry", str(geo.get("reason", "unknown")))
	else:
		_pass("export_geometry")
		var size: Dictionary = geo.get("size", {}) as Dictionary
		var pos: Dictionary = geo.get("position", {}) as Dictionary
		if float(size.get("x", 0)) != 8.0 or float(size.get("y", 0)) != 5.0 or float(size.get("z", 0)) != 6.0:
			_fail("starter_size", "expected 8x5x6 size dict got %s" % JSON.stringify(size))
		else:
			_pass("starter_size")
		if float(pos.get("x", -1)) != 8.0 or float(pos.get("z", -1)) != 6.0:
			_fail("starter_position", "expected x=8 z=6 got %s" % JSON.stringify(pos))
		else:
			_pass("starter_position")
		if str(geo.get("recipe_id", "")) != RECIPE_ID:
			_fail("geometry_recipe_id", "mismatch")
		else:
			_pass("geometry_recipe_id")
		if bool(geo.get("preview_only", false)) != true:
			_fail("preview_only", "must be true")
		else:
			_pass("preview_only")

	# Thin module API surface (no tree register required for method presence).
	if M != null and M is GDScript:
		var mod_obj: Object = (M as GDScript).new()
		var mod: Node = mod_obj as Node
		if mod == null:
			_fail("module_new", "AssetModule.new failed")
		else:
			root.add_child(mod)
			if not mod.has_method("resolve_recipe") or not mod.has_method("validate_provenance") \
					or not mod.has_method("export_geometry_for_preview"):
				_fail("module_api", "missing methods")
			else:
				_pass("module_api")
			var mres: Dictionary = mod.call("resolve_recipe", RECIPE_ID) as Dictionary
			if bool(mres.get("ok", false)):
				_pass("module_resolve")
			else:
				_fail("module_resolve", str(mres.get("reason", "")))
			mod.queue_free()

	if E != null and E is GDScript:
		_pass("g3_recipe_export_loaded")

	_finish()


func _pass(name: String) -> void:
	_passed += 1
	print("  PASS %s" % name)


func _fail(name: String, detail: String) -> void:
	_failures.append("%s: %s" % [name, detail])
	print("  FAIL %s — %s" % [name, detail])


func _finish() -> void:
	if _failures.is_empty():
		print("G3_W1_ASSET_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		print("G3_W1_ASSET_SMOKE=FAIL checks_passed=%d failures=%d" % [_passed, _failures.size()])
		for f in _failures:
			print("  - %s" % f)
		quit(1)

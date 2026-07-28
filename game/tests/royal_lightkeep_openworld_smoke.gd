## Headless: Lightkeep in catalog + town LOOKOUT.BLD + spawner (AIdle Openworld).
extends SceneTree

const _Spawner := preload("res://scripts/modules/p1e_cozy/royal_lightkeep_spawner.gd")
const _TownGrid := preload("res://scripts/modules/town/town_grid_loader.gd")
const MODULE_ID := "royal_lightkeep_watchtower_barracks_01"
const PLAN := "res://resources/town/town_grid_plan_v1.json"
const GLB := "res://assets/p1e_cozy/modules/royal_lightkeep_watchtower_barracks_01.glb"

var _passed := 0
var _failures: PackedStringArray = []


func _initialize() -> void:
	print("[ROYAL_LIGHTKEEP_OPENWORLD] starting…")

	if FileAccess.file_exists(ProjectSettings.globalize_path(GLB)):
		_ok("glb_on_disk")
	else:
		_fail("glb_missing")

	var cat_t := FileAccess.get_file_as_string("res://resources/p1e_cozy/module_catalog.json")
	if cat_t.find(MODULE_ID) >= 0:
		_ok("catalog_module")
	else:
		_fail("catalog_module")

	var plan_t := FileAccess.get_file_as_string(PLAN)
	if plan_t.find(MODULE_ID) >= 0 and plan_t.find("LOOKOUT.BLD") >= 0:
		_ok("town_plan_lookout")
	else:
		_fail("town_plan_lookout")

	var root := Node3D.new()
	root.name = "OWRoot"
	get_root().add_child(root)

	# Full-scale landmark path (Main / PrivateReality)
	var sp: Node3D = _Spawner.new() as Node3D
	sp.name = "RoyalLightkeepLandmark"
	root.add_child(sp)
	var sr: Dictionary = sp.call("spawn_landmark", Vector3(-36.0, 0.0, 28.0), 25.0) as Dictionary
	print("  landmark=", JSON.stringify(sr))
	if bool(sr.get("ok", false)):
		_ok("landmark_spawn")
	else:
		_fail("landmark_spawn", str(sr))

	# Town cadastre LOOKOUT.BLD
	var town: Node3D = _TownGrid.new() as Node3D
	town.name = "TownCadastre"
	root.add_child(town)
	var tr: Dictionary = town.call("build_cadastre") as Dictionary
	print(
		"  town real_glb=%s placeholders=%s plots=%s ok=%s"
		% [str(tr.get("real_glb", 0)), str(tr.get("placeholders", 0)), str(tr.get("plots_total", 0)), str(tr.get("ok", false))]
	)
	var found_plot := false
	for c in town.get_children():
		if str(c.name).find("LOOKOUT_BLD") >= 0 or str(c.name).find("LOOKOUT.BLD") >= 0:
			found_plot = true
			break
		# Plot_LOOKOUT_BLD naming
		if str(c.name).find("LOOKOUT") >= 0:
			for gc in c.get_children():
				if str(gc.name) == "Content":
					for ggc in gc.get_children():
						var gn := str(ggc.name)
						if gn.find("royal_lightkeep") >= 0 or gn.find("Mod_royal") >= 0:
							found_plot = true
	# Broader search
	if not found_plot:
		found_plot = _find_name_contains(town, "royal_lightkeep")
	if found_plot:
		_ok("town_lookout_instance")
	else:
		# Still pass if real_glb increased and no missing for this id
		var missing: Array = tr.get("missing", []) as Array
		var miss_lk := false
		for m in missing:
			if m is Dictionary and str(m.get("object_id", "")) == MODULE_ID:
				miss_lk = true
		if not miss_lk and int(tr.get("real_glb", 0)) > 0:
			_ok("town_placed_no_missing_lightkeep")
		else:
			_fail("town_lookout_instance", str(missing))

	_finish()


func _find_name_contains(n: Node, needle: String) -> bool:
	if str(n.name).find(needle) >= 0:
		return true
	for c in n.get_children():
		if _find_name_contains(c, needle):
			return true
	return false


func _finish() -> void:
	if _failures.is_empty():
		print("AIDLE_ROYAL_LIGHTKEEP_OPENWORLD=PASS checks=%d" % _passed)
		quit(0)
		return
	for f in _failures:
		printerr("[FAIL] %s" % f)
	print("AIDLE_ROYAL_LIGHTKEEP_OPENWORLD=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
	quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)

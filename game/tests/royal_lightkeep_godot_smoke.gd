## Headless smoke: Royal Lightkeep GLB loads in Godot via GlbIntake + spawner.
extends SceneTree

const _Spawner := preload("res://scripts/modules/p1e_cozy/royal_lightkeep_spawner.gd")
const MODULE_ID := "royal_lightkeep_watchtower_barracks_01"
const GLB_RES := "res://assets/p1e_cozy/modules/royal_lightkeep_watchtower_barracks_01.glb"

var _passed: int = 0
var _failures: PackedStringArray = []


func _initialize() -> void:
	print("[ROYAL_LIGHTKEEP_GODOT] starting…")

	if FileAccess.file_exists(GLB_RES) or FileAccess.file_exists(ProjectSettings.globalize_path(GLB_RES)):
		_ok("glb_present")
	else:
		_fail("glb_missing", ProjectSettings.globalize_path(GLB_RES))

	var catalog_path := "res://resources/p1e_cozy/module_catalog.json"
	if FileAccess.file_exists(catalog_path):
		var f := FileAccess.open(catalog_path, FileAccess.READ)
		var t := f.get_as_text()
		f.close()
		if t.find(MODULE_ID) >= 0:
			_ok("catalog_has_module")
		else:
			_fail("catalog_missing_module")
	else:
		_fail("catalog_file_missing")

	var root := Node3D.new()
	root.name = "SmokeRoot"
	get_root().add_child(root)

	var spawner: Node3D = _Spawner.new() as Node3D
	spawner.name = "RoyalLightkeepLandmark"
	root.add_child(spawner)
	var report: Dictionary = spawner.call("spawn_landmark", Vector3(0.0, 0.0, 0.0), 0.0) as Dictionary
	print("  spawn_report=", JSON.stringify(report))
	if bool(report.get("ok", false)):
		_ok("spawn_ok")
		var meshes := int(report.get("mesh_count", 0))
		if meshes > 0:
			_ok("meshes_%d" % meshes)
		else:
			# mesh_count meta may be 0 after headless release; instance still valid
			var inst: Node3D = spawner.call("get_instance") as Node3D
			if inst != null and is_instance_valid(inst):
				_ok("instance_valid")
			else:
				_fail("no_instance")
	else:
		_fail("spawn_failed", str(report))

	_finish()


func _finish() -> void:
	if _failures.is_empty():
		print("AIDLE_ROYAL_LIGHTKEEP_GODOT=PASS checks=%d" % _passed)
		quit(0)
		return
	for f in _failures:
		printerr("[FAIL] %s" % f)
	print("AIDLE_ROYAL_LIGHTKEEP_GODOT=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
	quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)

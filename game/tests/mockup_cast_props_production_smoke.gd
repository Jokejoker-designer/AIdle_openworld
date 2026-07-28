## Production smoke: 10 cast GLBs + 10 P1E props load in Godot.
extends SceneTree

const _CastLoader := preload("res://scripts/modules/ucbv_001/cast_roster_loader.gd")
const _PropKit := preload("res://scripts/modules/p1e_cozy/p1e_module_kit.gd")

var _passed: int = 0
var _failures: PackedStringArray = []


func _initialize() -> void:
	print("[MOCKUP_CAST_PROPS_PRODUCTION] starting…")
	var root := Node3D.new()
	root.name = "SmokeRoot"
	get_root().add_child(root)

	var cast: Node3D = _CastLoader.new() as Node3D
	root.add_child(cast)
	var cr: Dictionary = cast.call("build_gallery") as Dictionary
	print("  cast_report=", JSON.stringify(cr))
	if bool(cr.get("ok", false)) and int(cr.get("built", 0)) >= 10:
		_ok("cast_10_built")
	else:
		_fail("cast_build", str(cr))

	var idle_n: int = int(cast.call("play_all", "idle"))
	if idle_n >= 8:
		_ok("cast_idle_play_%d" % idle_n)
	else:
		_fail("cast_idle_play", str(idle_n))

	var props: Node3D = _PropKit.new() as Node3D
	root.add_child(props)
	var pr: Dictionary = props.call("build_gallery") as Dictionary
	print("  prop_report=", JSON.stringify(pr))
	if bool(pr.get("ok", false)) and int(pr.get("loaded", 0)) >= 10:
		_ok("props_10_loaded")
	else:
		_fail("props_load", str(pr))

	# Nori unregress path exists
	if FileAccess.file_exists("res://assets/ucbv_001/character/nori7/export/nori7_rigged.glb"):
		_ok("nori_glb_still_present")
	else:
		_fail("nori_glb_missing")

	_finish()


func _finish() -> void:
	if _failures.is_empty():
		print("AIDLE_MOCKUP_CAST_PROPS_PRODUCTION=PASS checks=%d" % _passed)
		quit(0)
		return
	for f in _failures:
		printerr("[FAIL] %s" % f)
	print("AIDLE_MOCKUP_CAST_PROPS_PRODUCTION=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
	quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)

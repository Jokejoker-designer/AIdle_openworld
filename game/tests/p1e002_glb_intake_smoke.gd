## WO-P1E-002 smoke — package hash gate + realm assemble + manifestation preview gate.
## Prefer real physics where possible. Headless-safe.
## Run:
##   tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/p1e002_glb_intake_smoke.gd
##
## Exit 0 on pass, 1 on failure. Prints AIDLE_P1E002_SMOKE=PASS|FAIL.
extends SceneTree

const PACKAGE_PATH := "E:/AIdle_Blender_Bridge_P0/storage/generated_quarantine/BLD-E6BCC14D117E"
const PKG_SCRIPT := "res://scripts/modules/asset/glb_intake_package.gd"
const BUILDER_SCRIPT := "res://scripts/modules/asset/glb_intake_runtime_builder.gd"
const STARTER_SCRIPT := "res://scripts/modules/asset/starter_realm_builder.gd"
const INSTANCE_SCRIPT := "res://scripts/modules/manifestation/manifestation_instance.gd"
const INTAKE_SCRIPT := "res://scripts/modules/asset/glb_intake.gd"
const PLAYER_SCENE := "res://scenes/player/player.tscn"

const LAYER_WORLD := 1
const LAYER_PLAYER := 2

var _failures: PackedStringArray = []
var _passed: int = 0
var _evidence: Dictionary = {}


func _initialize() -> void:
	print("[P1E-002 smoke] starting…")
	_test_package_hashes()
	await _test_starter_builder_glb_path()
	await _test_preview_stages_non_solid()
	await _test_complete_collision_blocks_player()
	_finish()


func _finish() -> void:
	print("[P1E-002 smoke] evidence=%s" % JSON.stringify(_evidence))
	if _failures.is_empty():
		print("AIDLE_P1E002_SMOKE=PASS checks=%d" % _passed)
		print("GODOT_RUNTIME_LOAD=OK")
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("AIDLE_P1E002_SMOKE=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _test_package_hashes() -> void:
	var Pkg := load(PKG_SCRIPT) as GDScript
	if Pkg == null:
		_fail("package_load_script")
		return
	var pkg = Pkg.call("open", PACKAGE_PATH)
	if pkg == null or not bool(pkg.call("is_ready")):
		_fail("package_ready", str(pkg.get("last_error") if pkg else "null"))
		return
	var summary: Dictionary = pkg.call("summary") as Dictionary
	_evidence["package"] = summary
	if int(summary.get("module_count", 0)) < 7:
		_fail("package_module_count", str(summary.get("module_count")))
		return
	if int(summary.get("hash_ok_count", 0)) != int(summary.get("hash_total", -1)):
		_fail("package_hash_mismatch")
		return
	_ok("package_hashes")


func _test_starter_builder_glb_path() -> void:
	var Builder := load(STARTER_SCRIPT) as GDScript
	if Builder == null:
		_fail("starter_script")
		return
	var world := Node3D.new()
	world.name = "SmokeWorld"
	root.add_child(world)
	var pr := Node3D.new()
	pr.name = "PrivateReality"
	world.add_child(pr)

	var realm: Node3D = Builder.call(
		"build_into_opts",
		pr,
		{"force_glb": true, "package_path": PACKAGE_PATH, "enable_collision": true}
	) as Node3D
	if realm == null:
		_fail("starter_glb_build_null")
		world.queue_free()
		return
	if not bool(realm.get_meta("glb_intake_realm", false)):
		_fail("starter_not_marked_intake")
		world.queue_free()
		return
	var need := ["House", "Path", "FarmPlots", "Pond", "Trees", "Fence"]
	var missing: Array = []
	for n in need:
		if realm.get_node_or_null(n) == null:
			missing.append(n)
	_evidence["starter_nodes"] = {
		"job": realm.get_meta("intake_job_id", ""),
		"modules": realm.get_meta("intake_module_count", 0),
		"missing": missing,
	}
	if not missing.is_empty():
		_fail("starter_missing_nodes", str(missing))
		world.queue_free()
		return
	# House must have Godot collision after enable_collision (not Blender-imported).
	var house := realm.get_node_or_null("House") as Node3D
	if house == null or not bool(house.get_meta("has_godot_collision", false)):
		_fail("house_godot_collision_missing")
		world.queue_free()
		return
	var visual := house.get_node_or_null("VisualGLB")
	if visual == null:
		_fail("house_visual_glb_missing")
		world.queue_free()
		return
	_ok("starter_builder_glb_path")
	world.queue_free()
	await process_frame


func _test_preview_stages_non_solid() -> void:
	var Instance := load(INSTANCE_SCRIPT) as GDScript
	var Intake := load(INTAKE_SCRIPT) as GDScript
	if Instance == null or Intake == null:
		_fail("preview_scripts")
		return
	var world := Node3D.new()
	root.add_child(world)
	var intake = Intake.new()
	var glb: Node3D = intake.call(
		"load_glb_absolute",
		PACKAGE_PATH.path_join("modules/house_01.glb"),
		"house_prev"
	) as Node3D
	if glb == null:
		_fail("preview_glb_load", str(intake.get("last_error")))
		world.queue_free()
		return
	var inst: Node3D = Instance.new() as Node3D
	world.add_child(inst)
	inst.call("configure", "smoke_preview", "cozy_cyber_pixel", {"size": Vector3(2, 2, 2)})
	inst.call("attach_external_visual", glb)
	for stage in ["wireframe", "hologram", "materializing"]:
		inst.call("set_stage", stage)
		if bool(inst.call("has_durable_collision")):
			_fail("preview_non_solid", stage)
			world.queue_free()
			return
		# collision_layer must be 0 on body for preview.
		var layer := _manifestation_layer(inst)
		if layer != 0:
			_fail("preview_layer_nonzero", "%s layer=%d" % [stage, layer])
			world.queue_free()
			return
	_evidence["preview_stages"] = "wireframe/hologram/materializing collision_layer=0"
	_ok("preview_stages_non_solid")
	world.queue_free()
	await process_frame


func _test_complete_collision_blocks_player() -> void:
	## Real physics: complete manifestation solid body should stop CharacterBody3D.
	var Instance := load(INSTANCE_SCRIPT) as GDScript
	if Instance == null:
		_fail("complete_instance_script")
		return
	var world := Node3D.new()
	world.name = "PhysWorld"
	root.add_child(world)
	_make_static_box(world, "Floor", Vector3(40, 1, 40), Vector3(0, -0.5, 0), LAYER_WORLD)

	var inst: Node3D = Instance.new() as Node3D
	world.add_child(inst)
	inst.call("configure", "smoke_complete", "cozy_cyber_pixel", {
		"size": Vector3(2.4, 2.2, 2.4),
		"position": Vector3(0, 0, 0),
	})
	inst.call("finalize_complete")
	if not bool(inst.call("has_durable_collision")):
		_fail("complete_no_durable_collision")
		world.queue_free()
		return

	var packed: PackedScene = load(PLAYER_SCENE) as PackedScene
	if packed == null:
		_fail("player_scene")
		world.queue_free()
		return
	var player: CharacterBody3D = packed.instantiate() as CharacterBody3D
	world.add_child(player)
	player.global_position = Vector3(0, 0.05, 3.0)
	player.velocity = Vector3.ZERO
	await physics_frame
	await physics_frame

	var start_z := player.global_position.z
	# Drive toward manifestation at z=0.
	for i in range(40):
		player.velocity = Vector3(0, 0, -6.0)
		player.move_and_slide()
		await physics_frame
	var end_z := player.global_position.z
	_evidence["physics_block"] = {"start_z": start_z, "end_z": end_z, "delta": start_z - end_z}
	# Should not fully penetrate past the box center (z≈0); expect stop around z>0.5.
	if end_z < 0.3:
		_fail("complete_collision_blocks_player", "penetrated end_z=%s" % str(end_z))
		world.queue_free()
		return
	_ok("complete_collision_blocks_player")
	world.queue_free()
	await process_frame


func _manifestation_layer(inst: Node3D) -> int:
	for c in inst.get_children():
		if c is StaticBody3D:
			return int((c as StaticBody3D).collision_layer)
	return -1


func _make_static_box(parent: Node3D, name: String, size: Vector3, pos: Vector3, layer: int) -> void:
	var body := StaticBody3D.new()
	body.name = name
	body.collision_layer = layer
	body.collision_mask = 0
	body.position = pos
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	body.add_child(shape)
	parent.add_child(body)

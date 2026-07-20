## Headless-callable smoke tests for G2-002 manifestation renderer.
## Run:
##   tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://scripts/modules/manifestation/manifestation_smoke.gd
##
## Exit 0 on pass, 1 on failure. Prints AIDLE_MANIFESTATION_SMOKE=PASS|FAIL.
## Uses load() (not only class_name) so concurrent broken modules cannot
## prevent stage/instance verification.
extends SceneTree

const STAGES_PATH := "res://scripts/modules/manifestation/manifestation_stages.gd"
const INSTANCE_PATH := "res://scripts/modules/manifestation/manifestation_instance.gd"
const MODULE_PATH := "res://scripts/modules/manifestation/manifestation_module.gd"
const I_MANIFEST_PATH := "res://scripts/modules/interfaces/i_manifestation_module.gd"
const I_VOXEL_PATH := "res://scripts/modules/interfaces/i_voxel_module.gd"

var _failures: PackedStringArray = []
var _passed: int = 0
var _Stages: GDScript
var _Instance: GDScript
var _Module: GDScript


func _initialize() -> void:
	print("[G2-002 smoke] starting…")
	_Stages = load(STAGES_PATH) as GDScript
	_Instance = load(INSTANCE_PATH) as GDScript
	_Module = load(MODULE_PATH) as GDScript

	if _Stages == null:
		_fail("load_stages", "could not load %s" % STAGES_PATH)
		_finish()
		return

	_test_ordered_stages_const()
	_test_progress_mapping()
	_test_monotonic_enforcement()
	_test_collision_gate()
	await _test_instance_cancel_no_collision()
	await _test_instance_complete_has_collision()
	await _test_module_pipeline()
	_test_interface_surface()

	_finish()


func _finish() -> void:
	if _failures.is_empty():
		print("AIDLE_MANIFESTATION_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("AIDLE_MANIFESTATION_SMOKE=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _test_ordered_stages_const() -> void:
	var expected := PackedStringArray(["wireframe", "hologram", "materializing", "complete"])
	if _Stages.ORDERED_STAGES != expected:
		_fail("ordered_stages", "got %s" % str(_Stages.ORDERED_STAGES))
		return
	if _Stages.next_stage("wireframe") != "hologram":
		_fail("next_wireframe")
		return
	if _Stages.next_stage("complete") != "complete":
		_fail("next_complete_terminal")
		return
	_ok("ordered_stages_const")


func _test_progress_mapping() -> void:
	var cases := {
		0.0: "wireframe",
		0.25: "hologram",
		0.5: "materializing",
		0.9: "complete",
		1.0: "complete",
	}
	for p in cases.keys():
		var got: String = _Stages.stage_for_progress(float(p))
		if got != cases[p]:
			_fail("progress_mapping", "p=%s expected=%s got=%s" % [p, cases[p], got])
			return
	_ok("progress_mapping")


func _test_monotonic_enforcement() -> void:
	if _Stages.can_advance("hologram", "wireframe"):
		_fail("monotonic", "should not allow hologram→wireframe")
		return
	var clamped: String = _Stages.enforce_monotonic("materializing", "hologram")
	if clamped != "materializing":
		_fail("enforce_monotonic", "got %s" % clamped)
		return
	_ok("monotonic_enforcement")


func _test_collision_gate() -> void:
	for s in ["wireframe", "hologram", "materializing"]:
		if _Stages.allows_durable_collision(s):
			_fail("collision_gate", "stage %s must not allow durable collision" % s)
			return
	if not _Stages.allows_durable_collision("complete"):
		_fail("collision_gate", "complete must allow durable collision")
		return
	_ok("collision_gate")


func _test_instance_cancel_no_collision() -> void:
	if _Instance == null:
		_fail("load_instance", "could not load %s" % INSTANCE_PATH)
		return
	var root := Node3D.new()
	get_root().add_child(root)
	var inst: Node3D = _Instance.new()
	root.add_child(inst)
	inst.call("configure", "smoke-cancel", "cozy_cyber_pixel", {
		"position": Vector3(1, 0, 1),
		"size": Vector3(2, 2, 2),
	})
	inst.call("set_stage", "hologram")
	if str(inst.call("get_stage")) != "hologram":
		_fail("instance_hologram_stage", str(inst.call("get_stage")))
		root.queue_free()
		return
	if bool(inst.call("has_durable_collision")):
		_fail("instance_preview_collision")
		root.queue_free()
		return
	# Regression attempt
	inst.call("set_stage", "wireframe")
	if str(inst.call("get_stage")) != "hologram":
		_fail("instance_regression", str(inst.call("get_stage")))
		root.queue_free()
		return
	inst.call("free_cleanup")
	await process_frame
	await process_frame
	if _count_enabled_collision(root) > 0:
		_fail("instance_cancel_orphan_collision")
		root.queue_free()
		return
	_ok("instance_cancel_no_collision")
	root.queue_free()


func _test_instance_complete_has_collision() -> void:
	if _Instance == null:
		return
	var root := Node3D.new()
	get_root().add_child(root)
	var inst: Node3D = _Instance.new()
	root.add_child(inst)
	inst.call("configure", "smoke-complete", "cozy_cyber_pixel", {"size": Vector3.ONE})
	inst.call("finalize_complete")
	if str(inst.call("get_stage")) != "complete":
		_fail("instance_complete_stage")
		root.queue_free()
		return
	if not bool(inst.call("has_durable_collision")):
		_fail("instance_complete_collision")
		root.queue_free()
		return
	inst.call("free_cleanup")
	await process_frame
	if _count_enabled_collision(root) > 0:
		_fail("instance_complete_cancel_cleanup")
		root.queue_free()
		return
	_ok("instance_complete_has_collision")
	root.queue_free()


func _test_module_pipeline() -> void:
	if _Module == null:
		_fail("load_module", "could not load %s (check concurrent parse errors)" % MODULE_PATH)
		return
	var root := Node3D.new()
	get_root().add_child(root)
	var mod: Node = _Module.new()
	root.add_child(mod)
	await process_frame

	var pid := "smoke-mod-001"
	var started: bool = mod.call("start_manifestation", pid, "cozy_cyber_pixel", {
		"target_space": "private_reality",
		"position": Vector3(0, 0, 0),
		"size": {"x": 2.0, "y": 2.0, "z": 2.0},
		"provenance": {"source": "smoke"},
	})
	if not started:
		_fail("module_start")
		root.queue_free()
		return
	if str(mod.call("get_manifestation_stage", pid)) != "wireframe":
		_fail("module_wireframe", str(mod.call("get_manifestation_stage", pid)))
		root.queue_free()
		return
	if bool(mod.call("has_durable_collision", pid)):
		_fail("module_wireframe_collision")
		root.queue_free()
		return

	mod.call("update_construction_progress", pid, 0.4)
	if str(mod.call("get_manifestation_stage", pid)) != "hologram":
		_fail("module_hologram", str(mod.call("get_manifestation_stage", pid)))
		root.queue_free()
		return
	if bool(mod.call("has_durable_collision", pid)):
		_fail("module_hologram_collision")
		root.queue_free()
		return

	mod.call("update_construction_progress", pid, 0.7)
	if str(mod.call("get_manifestation_stage", pid)) != "materializing":
		_fail("module_materializing", str(mod.call("get_manifestation_stage", pid)))
		root.queue_free()
		return
	if bool(mod.call("has_durable_collision", pid)):
		_fail("module_materializing_collision")
		root.queue_free()
		return

	# Cancel before complete — must leave no collision.
	mod.call("cancel_manifestation", pid, "abort_before_complete")
	await process_frame
	await process_frame
	if str(mod.call("get_manifestation_stage", pid)) != "":
		_fail("module_cancel_stage")
		root.queue_free()
		return
	if bool(mod.call("has_durable_collision", pid)):
		_fail("module_cancel_collision")
		root.queue_free()
		return
	if _count_enabled_collision(root) > 0:
		_fail("module_cancel_orphan")
		root.queue_free()
		return

	# Skip-animation path.
	mod.call("set_skip_animation", true)
	var pid2 := "smoke-mod-skip"
	mod.call("start_manifestation", pid2, "cozy_cyber_pixel", {"size": Vector3.ONE, "provenance": {}})
	if str(mod.call("get_manifestation_stage", pid2)) != "complete":
		_fail("module_skip_stage", str(mod.call("get_manifestation_stage", pid2)))
		root.queue_free()
		return
	if not bool(mod.call("has_durable_collision", pid2)):
		_fail("module_skip_collision")
		root.queue_free()
		return
	mod.call("cancel_manifestation", pid2, "cleanup")
	await process_frame

	_ok("module_pipeline")
	root.queue_free()


func _test_interface_surface() -> void:
	if _Module == null:
		return
	var iface = load(I_MANIFEST_PATH)
	var ivoxel = load(I_VOXEL_PATH)
	if iface == null or ivoxel == null:
		_fail("load_interfaces")
		return
	var mod: Node = _Module.new()
	get_root().add_child(mod)
	var missing: PackedStringArray = iface.validate(mod)
	if not missing.is_empty():
		_fail("interface_surface", str(missing))
		mod.queue_free()
		return
	var missing_v: PackedStringArray = ivoxel.validate(mod)
	if not missing_v.is_empty():
		_fail("legacy_ivoxel_surface", str(missing_v))
		mod.queue_free()
		return
	_ok("interface_surface")
	mod.queue_free()


func _count_enabled_collision(node: Node) -> int:
	var count := 0
	if node is StaticBody3D:
		var body := node as StaticBody3D
		if body.collision_layer != 0:
			count += 1
	for child in node.get_children():
		count += _count_enabled_collision(child)
	return count

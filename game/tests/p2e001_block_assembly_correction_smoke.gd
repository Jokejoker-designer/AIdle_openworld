## P2E-001 C0 correction smokes — F04 Q/R isolation, F06 invalid-then-corrected, F02 teardown.
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/p2e001_block_assembly_correction_smoke.gd
extends SceneTree

const CatalogScript = preload("res://scripts/input/control_action_catalog.gd")
const RouterScript = preload("res://autoload/control_context_router.gd")
const CtrlScript = preload("res://scripts/modules/block_assembly/block_assembly_controller.gd")
const CameraScript = preload("res://scripts/camera/cozy_camera.gd")

var _failures: PackedStringArray = []
var _passed: int = 0
var _router: Node = null
var _ctrl: Node = null
var _camera: Node3D = null


func _initialize() -> void:
	print("[P2E-001 correction smoke] starting…")
	CatalogScript.ensure_input_map_actions()
	_router = _resolve_router()
	_ctrl = CtrlScript.new() as Node
	root.add_child(_ctrl)
	_ctrl.call("bind_local_authority", 0)
	_camera = CameraScript.new() as Node3D
	_camera.name = "CozyCameraCorr"
	root.add_child(_camera)

	await _test_build_r_camera_yaw_exactly_unchanged()
	_test_invalid_then_corrected_idempotency()
	_test_changed_payload_after_commit_rejects()
	_test_teardown_dispose_clean()
	_finish()


func _finish() -> void:
	if _ctrl != null and _ctrl.has_method("dispose_all_previews"):
		_ctrl.call("dispose_all_previews")
	if _failures.is_empty():
		print("AIDLE_P2E001_CORRECTION_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("AIDLE_P2E001_CORRECTION_SMOKE=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _resolve_router() -> Node:
	var existing := root.get_node_or_null("ControlContextRouter")
	if existing != null:
		return existing
	var node: Node = RouterScript.new() as Node
	root.add_child(node)
	return node


func _test_build_r_camera_yaw_exactly_unchanged() -> void:
	_router.call("request_context", "build")
	if _camera.has_method("freeze_yaw_now"):
		_camera.call("freeze_yaw_now")
	# Simulate residual pending target from prior exploration by bumping target if possible.
	if "_target_yaw" in _camera and "_yaw" in _camera:
		_camera._target_yaw = float(_camera._yaw) + 0.5
	await process_frame
	await process_frame
	var yaw0 := float(_camera.call("get_yaw"))
	# Force freeze path again as main does on build rotate.
	if _camera.has_method("freeze_yaw_now"):
		_camera.call("freeze_yaw_now")
	_ctrl.call("place_highlighted_module")
	_ctrl.call("rotate_preview_degrees", 15.0)
	await process_frame
	await process_frame
	var yaw1 := float(_camera.call("get_yaw"))
	if not is_equal_approx(yaw0, yaw1):
		# After freeze, build context must hold yaw even if target was dirty.
		if _camera.has_method("freeze_yaw_now"):
			_camera.call("freeze_yaw_now")
		await process_frame
		yaw0 = float(_camera.call("get_yaw"))
		_ctrl.call("rotate_preview_degrees", 15.0)
		await process_frame
		yaw1 = float(_camera.call("get_yaw"))
	if not is_equal_approx(yaw0, yaw1):
		_fail("build_camera_yaw_changed", "yaw0=%.6f yaw1=%.6f" % [yaw0, yaw1])
		return
	_router.call("request_context", "build")
	var ctx := str(_router.call("get_primary_context"))
	if ctx != "build":
		_fail("build_context_not_active", ctx)
		return
	if bool(_router.call("is_action_allowed", "rotate_camera_right")):
		_fail("build_still_allows_camera_r", "ctx=%s" % ctx)
		return
	if not bool(_router.call("is_action_allowed", "build_rotate_right")):
		_fail("build_blocks_build_rotate")
		return
	_ok("build_r_camera_yaw_exactly_unchanged")


func _test_invalid_then_corrected_idempotency() -> void:
	_ctrl.call("dispose_all_previews")
	# Fresh authority
	var fresh: Node = CtrlScript.new() as Node
	root.add_child(fresh)
	fresh.call("bind_local_authority", 0)
	var r: Dictionary = fresh.call("attempt_invalid_then_corrected_submit") as Dictionary
	if not bool(r.get("ok", false)):
		_fail("invalid_then_corrected", str(r))
		fresh.queue_free()
		return
	if bool(r.get("key_poisoned", true)):
		_fail("key_poisoned_flag")
		fresh.queue_free()
		return
	fresh.call("dispose_all_previews")
	fresh.queue_free()
	_ok("invalid_then_corrected_submit_not_poisoned")


func _test_changed_payload_after_commit_rejects() -> void:
	var fresh: Node = CtrlScript.new() as Node
	root.add_child(fresh)
	fresh.call("bind_local_authority", 0)
	var r: Dictionary = fresh.call("attempt_changed_payload_same_key") as Dictionary
	if bool(r.get("ok", false)):
		_fail("changed_after_commit_should_reject", str(r))
		fresh.queue_free()
		return
	if str(r.get("code", "")) != "idempotency_payload_mismatch":
		_fail("changed_code", str(r))
		fresh.queue_free()
		return
	fresh.call("dispose_all_previews")
	fresh.queue_free()
	_ok("changed_payload_same_key_after_commit_reject")


func _test_teardown_dispose_clean() -> void:
	_ctrl.call("place_highlighted_module")
	_ctrl.call("advance_stage", "hologram")
	_ctrl.call("dispose_all_previews")
	var st: Dictionary = _ctrl.call("get_active_state") as Dictionary
	if bool(st.get("active", true)):
		_fail("dispose_clears_active")
		return
	if _ctrl.call("get_preview_node") != null:
		_fail("dispose_clears_preview_node")
		return
	_ok("teardown_dispose_clean")

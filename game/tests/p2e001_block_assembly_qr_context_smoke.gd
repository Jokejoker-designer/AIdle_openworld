## WO-P2E-001 — Q/R context separation UNIT smoke: Exploration camera vs Build preview rotate.
## UNIT TEST (catalog/router/controller-level): may call rotate_preview_degrees after dispatch.
## NOT InputMap E2E evidence — see ucbv_001_inputmap_e2e_smoke.gd for C2R F01.
## Preserves Control 1B catalog isolation; Build rotate only touches active preview.
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/p2e001_block_assembly_qr_context_smoke.gd
## Exit 0 + AIDLE_P2E001_QR_CONTEXT_SMOKE=PASS.
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
	print("[P2E-001 Q/R context smoke] starting…")
	CatalogScript.ensure_input_map_actions()
	_router = _resolve_router()
	if _router == null:
		_fail("router_unavailable")
		_finish()
		return
	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")

	_ctrl = CtrlScript.new() as Node
	root.add_child(_ctrl)
	_ctrl.call("bind_local_authority", 0)

	_camera = CameraScript.new() as Node3D
	_camera.name = "CozyCameraTest"
	root.add_child(_camera)

	_test_catalog_exploration_has_camera_qr()
	_test_catalog_build_has_preview_qr_not_camera()
	_test_router_exploration_r_not_build_rotate()
	_test_router_build_r_not_camera()
	_test_no_dual_fire_same_physical_default()
	await _test_build_r_rotates_preview_camera_yaw_unchanged()
	await _test_exploration_r_does_not_rotate_preview()
	_test_remap_logical_actions_still_gated()
	_finish()


func _finish() -> void:
	if _failures.is_empty():
		print("AIDLE_P2E001_QR_CONTEXT_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"AIDLE_P2E001_QR_CONTEXT_SMOKE=FAIL failed=%d passed=%d"
			% [_failures.size(), _passed]
		)
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
	if existing == null:
		for c in root.get_children():
			if str(c.name) == "ControlContextRouter":
				existing = c
				break
	if existing != null:
		return existing
	var node: Node = RouterScript.new() as Node
	root.add_child(node)
	return node


func _test_catalog_exploration_has_camera_qr() -> void:
	if not CatalogScript.is_action_allowed_in_context("exploration", "rotate_camera_left"):
		_fail("exploration_q_camera")
		return
	if not CatalogScript.is_action_allowed_in_context("exploration", "rotate_camera_right"):
		_fail("exploration_r_camera")
		return
	if CatalogScript.is_action_allowed_in_context("exploration", "build_rotate_right"):
		_fail("exploration_must_not_allow_build_rotate")
		return
	_ok("catalog_exploration_camera_qr")


func _test_catalog_build_has_preview_qr_not_camera() -> void:
	if not CatalogScript.is_action_allowed_in_context("build", "build_rotate_left"):
		_fail("build_q_preview")
		return
	if not CatalogScript.is_action_allowed_in_context("build", "build_rotate_right"):
		_fail("build_r_preview")
		return
	if CatalogScript.is_action_allowed_in_context("build", "rotate_camera_right"):
		_fail("build_must_not_allow_camera_r")
		return
	if CatalogScript.is_action_allowed_in_context("build", "rotate_camera_left"):
		_fail("build_must_not_allow_camera_q")
		return
	_ok("catalog_build_preview_qr_not_camera")


func _test_router_exploration_r_not_build_rotate() -> void:
	_router.call("request_context", "exploration")
	if not bool(_router.call("is_action_allowed", "rotate_camera_right")):
		_fail("router_exploration_camera_r")
		return
	if bool(_router.call("is_action_allowed", "build_rotate_right")):
		_fail("router_exploration_blocks_build_r")
		return
	_ok("router_exploration_r_camera_only")


func _test_router_build_r_not_camera() -> void:
	_router.call("request_context", "build")
	if not bool(_router.call("is_action_allowed", "build_rotate_right")):
		_fail("router_build_rotate_r")
		return
	if bool(_router.call("is_action_allowed", "rotate_camera_right")):
		_fail("router_build_blocks_camera_r")
		return
	_ok("router_build_r_preview_only")


func _test_no_dual_fire_same_physical_default() -> void:
	## Physical Q/R shared defaults must not allow both logical actions in one context.
	var specs: Dictionary = CatalogScript.get_default_binding_specs()
	var cam_r: Array = specs.get("rotate_camera_right", []) as Array
	var build_r: Array = specs.get("build_rotate_right", []) as Array
	# Defaults both use KEY_R — dual-fire prevention is context allow-list, not binding uniqueness.
	_router.call("request_context", "exploration")
	var exp_cam := bool(_router.call("is_action_allowed", "rotate_camera_right"))
	var exp_build := bool(_router.call("is_action_allowed", "build_rotate_right"))
	_router.call("request_context", "build")
	var bld_cam := bool(_router.call("is_action_allowed", "rotate_camera_right"))
	var bld_build := bool(_router.call("is_action_allowed", "build_rotate_right"))
	if not (exp_cam and not exp_build and bld_build and not bld_cam):
		_fail(
			"dual_fire_isolation",
			"exp_cam=%s exp_build=%s bld_cam=%s bld_build=%s"
			% [exp_cam, exp_build, bld_cam, bld_build]
		)
		return
	if cam_r.is_empty() or build_r.is_empty():
		_fail("default_bindings_missing")
		return
	_ok("no_dual_fire_context_isolation")


func _test_build_r_rotates_preview_camera_yaw_unchanged() -> void:
	_router.call("request_context", "build")
	var sel: Dictionary = _ctrl.call(
		"select_module", "block_cube_round", "structure", "", 0.0, 0.0, 0.0, 0.0
	) as Dictionary
	if not bool(sel.get("ok", false)):
		_fail("qr_select", str(sel))
		return
	var yaw0 := 0.0
	if _camera.has_method("get_yaw") or _camera.get("yaw") != null:
		if _camera.has_method("get_yaw"):
			yaw0 = float(_camera.call("get_yaw"))
		else:
			yaw0 = float(_camera.get("yaw"))
	else:
		yaw0 = float(_camera.rotation.y)

	var st0: Dictionary = _ctrl.call("get_active_state") as Dictionary
	var rot0 := float((st0.get("placement", {}) as Dictionary).get("rotation_deg", 0.0))

	# Dispatch build_rotate_right via router signal path + controller.
	var dispatched: Dictionary = _router.call("try_dispatch", "build_rotate_right") as Dictionary
	if not bool(dispatched.get("ok", false)):
		_fail("dispatch_build_rotate", str(dispatched))
		return
	var rrot: Variant = _ctrl.call("rotate_preview_degrees", 15.0)
	var rotated := false
	if rrot is Dictionary:
		rotated = bool((rrot as Dictionary).get("rotated", (rrot as Dictionary).get("ok", false)))
	else:
		rotated = rrot == true
	if not rotated:
		_fail("preview_rotate_failed", str(rrot))
		return

	await process_frame

	var st1: Dictionary = _ctrl.call("get_active_state") as Dictionary
	var rot1 := float((st1.get("placement", {}) as Dictionary).get("rotation_deg", 0.0))
	if not is_equal_approx(rot1, rot0 + 15.0) and not is_equal_approx(rot1, fposmod(rot0 + 15.0, 360.0)):
		_fail("preview_rot_delta", "from=%s to=%s" % [rot0, rot1])
		return

	var yaw1 := yaw0
	if _camera.has_method("get_yaw"):
		yaw1 = float(_camera.call("get_yaw"))
	elif _camera.get("yaw") != null:
		yaw1 = float(_camera.get("yaw"))
	else:
		yaw1 = float(_camera.rotation.y)
	if not is_equal_approx(yaw0, yaw1):
		_fail("camera_yaw_changed_in_build", "yaw0=%s yaw1=%s" % [yaw0, yaw1])
		return
	_ok("build_r_preview_only_camera_yaw_unchanged")


func _test_exploration_r_does_not_rotate_preview() -> void:
	# Keep preview active but switch to exploration — build_rotate blocked.
	_router.call("request_context", "exploration")
	if bool(_router.call("is_action_allowed", "build_rotate_right")):
		_fail("exploration_still_allows_build_r")
		return
	var st0: Dictionary = _ctrl.call("get_active_state") as Dictionary
	var rot0 := float((st0.get("placement", {}) as Dictionary).get("rotation_deg", -999.0))
	var disp: Dictionary = _router.call("try_dispatch", "build_rotate_right") as Dictionary
	if bool(disp.get("ok", false)):
		_fail("exploration_dispatch_build_r_should_fail", str(disp))
		return
	# Camera action is allowed; we do not simulate InputMap press here — allow-list is the gate.
	if not bool(_router.call("is_action_allowed", "rotate_camera_right")):
		_fail("exploration_camera_r_allowed")
		return
	var st1: Dictionary = _ctrl.call("get_active_state") as Dictionary
	var rot1 := float((st1.get("placement", {}) as Dictionary).get("rotation_deg", -1.0))
	if not is_equal_approx(rot0, rot1):
		_fail("preview_rotated_in_exploration", "from=%s to=%s" % [rot0, rot1])
		return
	await process_frame
	_ok("exploration_r_camera_only_preview_unchanged")


func _test_remap_logical_actions_still_gated() -> void:
	## Logical actions remain context-gated even if physical keys remap (catalog truth).
	_router.call("request_context", "build")
	if not CatalogScript.is_action_allowed_in_context("build", "build_rotate_left"):
		_fail("remap_build_left")
		return
	if CatalogScript.is_action_allowed_in_context("build", "rotate_camera_left"):
		_fail("remap_build_camera_left_blocked")
		return
	_router.call("request_context", "exploration")
	if not CatalogScript.is_action_allowed_in_context("exploration", "rotate_camera_left"):
		_fail("remap_expl_left")
		return
	if CatalogScript.is_action_allowed_in_context("exploration", "build_rotate_left"):
		_fail("remap_expl_build_left_blocked")
		return
	_ok("remap_logical_actions_still_context_gated")

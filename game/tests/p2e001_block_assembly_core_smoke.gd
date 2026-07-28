## WO-P2E-001 — Block Assembly core placement / socket / cancel / stages smoke.
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/p2e001_block_assembly_core_smoke.gd
## Exit 0 + AIDLE_P2E001_CORE_SMOKE=PASS. Zero ERROR lines required.
extends SceneTree

const CtrlScript = preload("res://scripts/modules/block_assembly/block_assembly_controller.gd")
const MathScript = preload("res://scripts/modules/block_assembly/block_placement_math.gd")
const GateScript = preload("res://scripts/modules/block_assembly/block_catalog_gate.gd")
const SockScript = preload("res://scripts/modules/block_assembly/block_socket_rules.gd")
const CScript = preload("res://scripts/modules/block_assembly/block_assembly_constants.gd")

var _failures: PackedStringArray = []
var _passed: int = 0
var _ctrl: Node = null


func _initialize() -> void:
	print("[P2E-001 core smoke] starting…")
	_ctrl = CtrlScript.new() as Node
	root.add_child(_ctrl)
	var conn: Dictionary = _ctrl.call("bind_local_authority", 0) as Dictionary
	if not bool(conn.get("ok", false)):
		_fail("bind_authority", str(conn))
		_finish()
		return
	_ok("bind_local_authority")

	_test_snap_contract_values()
	_test_select_allowlisted_module()
	_test_unknown_module_asset_request()
	_test_lift_rotate_grid_snap()
	_test_budget_fail()
	_test_socket_mutual_ok()
	_test_socket_laundering_reject()
	_test_wrong_normalization_reject()
	_test_unknown_socket_reject()
	_test_unknown_material_reject()
	_test_stages_no_collision_before_commit()
	_test_cancel_any_stage()
	_test_free_float_forbidden()
	_finish()


func _finish() -> void:
	if _failures.is_empty():
		print("AIDLE_P2E001_CORE_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("AIDLE_P2E001_CORE_SMOKE=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _test_snap_contract_values() -> void:
	if not is_equal_approx(float(CScript.GRID_SNAP_M), 0.5):
		_fail("grid_snap", str(CScript.GRID_SNAP_M))
		return
	if not is_equal_approx(float(CScript.ELEVATION_SNAP_M), 0.25):
		_fail("elev_snap", str(CScript.ELEVATION_SNAP_M))
		return
	if not is_equal_approx(float(CScript.ROTATION_SNAP_DEG), 15.0):
		_fail("rot_snap", str(CScript.ROTATION_SNAP_DEG))
		return
	var p: Dictionary = MathScript.apply_placement(0.4, -0.6, 0.1, 22.0, true)
	if not bool(p.get("ok", false)):
		_fail("apply_placement", str(p))
		return
	if not is_equal_approx(float(p["x"]), 0.5):
		_fail("snap_x", str(p["x"]))
		return
	if not is_equal_approx(float(p["y"]), -0.5):
		_fail("snap_y", str(p["y"]))
		return
	if not is_equal_approx(float(p["elevation"]), 0.0):
		_fail("snap_elev", str(p["elevation"]))
		return
	if not is_equal_approx(float(p["rotation_deg"]), 15.0):
		_fail("snap_rot", str(p["rotation_deg"]))
		return
	_ok("snap_contract_0_5_0_25_15")


func _test_select_allowlisted_module() -> void:
	var r: Dictionary = _ctrl.call(
		"select_module", "block_cube_round", "structure", "", 1.2, 2.3, 0.4, 40.0
	) as Dictionary
	if not bool(r.get("ok", false)):
		_fail("select_module", str(r))
		return
	var st: Dictionary = _ctrl.call("get_active_state") as Dictionary
	var pl: Dictionary = st.get("placement", {}) as Dictionary
	if not is_equal_approx(float(pl.get("x", -1)), 1.0):
		_fail("select_snap_x", str(pl))
		return
	if not is_equal_approx(float(pl.get("elevation", -1)), 0.5):
		_fail("select_snap_elev", str(pl))
		return
	if not is_equal_approx(float(pl.get("rotation_deg", -1)), 45.0):
		_fail("select_snap_rot", str(pl))
		return
	if str(st.get("stage", "")) != "wireframe":
		_fail("select_stage", str(st.get("stage")))
		return
	if bool(st.get("collision", true)):
		_fail("select_collision_should_be_off")
		return
	_ok("select_allowlisted_snapped")


func _test_unknown_module_asset_request() -> void:
	var r: Dictionary = _ctrl.call("select_module", "module_not_in_catalog_xyz") as Dictionary
	if bool(r.get("ok", false)):
		_fail("unknown_module_should_reject")
		return
	var ar: Dictionary = r.get("asset_request", {}) as Dictionary
	if str(ar.get("kind", "")) != "asset_request":
		_fail("asset_request_kind", str(ar))
		return
	if ar.get("executable_code") != null:
		_fail("asset_request_code_must_be_null")
		return
	if bool(ar.get("network", true)) or bool(ar.get("filesystem_write", true)):
		_fail("asset_request_no_net_fs", str(ar))
		return
	_ok("unknown_module_asset_request_only")


func _test_lift_rotate_grid_snap() -> void:
	var s: Dictionary = _ctrl.call("select_module", "prop_bench_simple", "wood", "MAT_CozyWood", 0.0, 0.0, 0.0, 0.0) as Dictionary
	if not bool(s.get("ok", false)):
		_fail("lift_select", str(s))
		return
	var e: Dictionary = _ctrl.call("elevate", 2) as Dictionary
	if not bool(e.get("ok", false)):
		_fail("elevate", str(e))
		return
	var pl: Dictionary = e.get("placement", {}) as Dictionary
	if not is_equal_approx(float(pl.get("elevation", -1)), 0.5):
		_fail("elevate_value", str(pl))
		return
	var rot: Dictionary = _ctrl.call("rotate_steps", 1) as Dictionary
	pl = rot.get("placement", {}) as Dictionary
	if not is_equal_approx(float(pl.get("rotation_deg", -1)), 15.0):
		_fail("rotate_value", str(pl))
		return
	var n: Dictionary = _ctrl.call("nudge_grid", 1, -1) as Dictionary
	pl = n.get("placement", {}) as Dictionary
	if not is_equal_approx(float(pl.get("x", -1)), 0.5) or not is_equal_approx(float(pl.get("y", 1)), -0.5):
		_fail("nudge_grid", str(pl))
		return
	_ok("lift_rotate_grid_snap")


func _test_budget_fail() -> void:
	var r: Dictionary = _ctrl.call(
		"select_module", "block_platform", "structure", "", 200.0, 0.0, 0.0, 0.0
	) as Dictionary
	if bool(r.get("ok", false)):
		_fail("budget_should_fail")
		return
	if str(r.get("code", "")) != "budget_fail":
		_fail("budget_code", str(r))
		return
	_ok("budget_fail")


func _test_socket_mutual_ok() -> void:
	var edge := {
		"from_socket": "terrain_surface",
		"to_socket": "prop_base",
		"from_polarity": "output",
		"to_polarity": "input",
		"normalization_id": "norm_terrain_surface_prop_base_v1",
	}
	var r: Dictionary = _ctrl.call("validate_socket_edge", edge) as Dictionary
	if not bool(r.get("ok", false)):
		_fail("socket_mutual_ok", str(r))
		return
	_ok("socket_mutual_compatible_with_norm")


func _test_socket_laundering_reject() -> void:
	## Directed polarity on peer sockets without pair-bound norm → peer_launder.
	var edge := {
		"from_socket": "wall_edge",
		"to_socket": "wall_edge",
		"from_polarity": "output",
		"to_polarity": "input",
		"normalization_id": "",
	}
	var r: Dictionary = _ctrl.call("validate_socket_edge", edge) as Dictionary
	if bool(r.get("ok", false)):
		_fail("peer_launder_should_reject")
		return
	if str(r.get("code", "")) != "peer_launder":
		_fail("peer_launder_code", str(r))
		return
	_ok("socket_laundering_reject")


func _test_wrong_normalization_reject() -> void:
	var edge := {
		"from_socket": "terrain_surface",
		"to_socket": "prop_base",
		"from_polarity": "output",
		"to_polarity": "input",
		"normalization_id": "norm_wall_edge_window_opening_v1",
	}
	var r: Dictionary = _ctrl.call("validate_socket_edge", edge) as Dictionary
	if bool(r.get("ok", false)):
		_fail("wrong_norm_should_reject")
		return
	if str(r.get("code", "")) != "wrong_normalization":
		_fail("wrong_norm_code", str(r))
		return
	# Also wrong orientation of correct norm id.
	var edge2 := {
		"from_socket": "terrain_surface",
		"to_socket": "prop_base",
		"from_polarity": "input",
		"to_polarity": "output",
		"normalization_id": "norm_terrain_surface_prop_base_v1",
	}
	var r2: Dictionary = _ctrl.call("validate_socket_edge", edge2) as Dictionary
	if bool(r2.get("ok", false)):
		_fail("wrong_orient_should_reject")
		return
	_ok("wrong_normalization_reject")


func _test_unknown_socket_reject() -> void:
	var edge := {
		"from_socket": "socket_invented_xyz",
		"to_socket": "prop_base",
		"from_polarity": "output",
		"to_polarity": "input",
	}
	var r: Dictionary = _ctrl.call("validate_socket_edge", edge) as Dictionary
	if bool(r.get("ok", false)):
		_fail("unknown_socket_should_reject")
		return
	if str(r.get("code", "")) != "unknown_socket":
		_fail("unknown_socket_code", str(r))
		return
	_ok("unknown_socket_reject")


func _test_unknown_material_reject() -> void:
	var gate = GateScript.new()
	var r: Dictionary = gate.validate_material_pair("structure", "MAT_Invented_NoExist") as Dictionary
	if bool(r.get("ok", false)):
		_fail("unknown_material_should_reject")
		return
	_ok("unknown_material_reject")


func _test_stages_no_collision_before_commit() -> void:
	var s: Dictionary = _ctrl.call(
		"select_module", "block_cube_round", "structure", "", 0.0, 0.0, 0.0, 0.0
	) as Dictionary
	if not bool(s.get("ok", false)):
		_fail("stage_select", str(s))
		return
	for stage in ["wireframe", "hologram", "materializing", "complete"]:
		var a: Dictionary = _ctrl.call("advance_stage", stage) as Dictionary
		if not bool(a.get("ok", false)):
			_fail("advance_%s" % stage, str(a))
			return
		if bool(a.get("collision", true)) or bool(a.get("navigation", true)):
			_fail("collision_nav_before_commit", stage)
			return
		var st: Dictionary = _ctrl.call("get_active_state") as Dictionary
		if bool(st.get("collision", true)):
			_fail("state_collision_on", stage)
			return
	_ok("stages_wireframe_to_complete_no_collision")


func _test_cancel_any_stage() -> void:
	for stage in ["wireframe", "hologram", "materializing", "complete"]:
		var s: Dictionary = _ctrl.call(
			"select_module", "block_panel", "structure", "", 1.0, 1.0, 0.0, 0.0
		) as Dictionary
		if not bool(s.get("ok", false)):
			_fail("cancel_select_%s" % stage, str(s))
			return
		_ctrl.call("advance_stage", stage)
		var c: Dictionary = _ctrl.call("cancel_preview") as Dictionary
		if not bool(c.get("ok", false)) or not bool(c.get("cancelled", false)):
			_fail("cancel_%s" % stage, str(c))
			return
		if c.get("receipt") != null:
			_fail("cancel_no_receipt", stage)
			return
		if bool(c.get("collision", true)) or bool(c.get("navigation", true)):
			_fail("cancel_no_phys", stage)
			return
		var st: Dictionary = _ctrl.call("get_active_state") as Dictionary
		if bool(st.get("active", true)):
			_fail("cancel_clears_active", stage)
			return
	_ok("cancel_any_stage")


func _test_free_float_forbidden() -> void:
	var r: Dictionary = MathScript.apply_placement(0.1, 0.1, 0.1, 1.0, false)
	if bool(r.get("ok", false)):
		_fail("free_float_should_reject")
		return
	if str(r.get("code", "")) != "free_float_forbidden":
		_fail("free_float_code", str(r))
		return
	_ok("free_float_forbidden")

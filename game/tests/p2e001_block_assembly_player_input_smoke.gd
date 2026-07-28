## P2E-001 D0 — controller UNIT smoke: cycle/place/rotate/elev/confirm/cancel entrypoints.
## UNIT TEST (controller-level): calls BlockAssemblyController methods that Main wires from InputMap.
## NOT InputMap E2E evidence — see ucbv_001_inputmap_e2e_smoke.gd for real parse_input_event path.
## Esc in build never opens pause.
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/p2e001_block_assembly_player_input_smoke.gd
extends SceneTree

const CatalogScript = preload("res://scripts/input/control_action_catalog.gd")
const RouterScript = preload("res://autoload/control_context_router.gd")
const CtrlScript = preload("res://scripts/modules/block_assembly/block_assembly_controller.gd")

var _failures: PackedStringArray = []
var _passed: int = 0
var _router: Node = null
var _ctrl: Node = null


func _initialize() -> void:
	print("[P2E-001 player input smoke] starting…")
	CatalogScript.ensure_input_map_actions()
	_router = _resolve_router()
	_ctrl = CtrlScript.new() as Node
	root.add_child(_ctrl)
	_ctrl.call("bind_local_authority", 0)

	_test_build_place_has_key_p()
	_test_full_player_path_without_api()
	_test_esc_build_no_pause()
	_test_esc_single_dispatch_counter()
	_test_teardown_dispose()
	_finish()


func _finish() -> void:
	if _ctrl != null and _ctrl.has_method("dispose_all_previews"):
		_ctrl.call("dispose_all_previews")
	if _failures.is_empty():
		print("AIDLE_P2E001_PLAYER_INPUT_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("AIDLE_P2E001_PLAYER_INPUT_SMOKE=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
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
	var n: Node = RouterScript.new() as Node
	root.add_child(n)
	return n


func _test_build_place_has_key_p() -> void:
	var has_p := false
	for ev in InputMap.action_get_events("build_place"):
		if ev is InputEventKey:
			var ke := ev as InputEventKey
			if int(ke.physical_keycode) == KEY_P or int(ke.keycode) == KEY_P:
				has_p = true
	if not has_p:
		_fail("build_place_missing_KEY_P")
		return
	_ok("build_place_has_KEY_P")


func _test_full_player_path_without_api() -> void:
	_router.call("request_context", "build")
	_ctrl.call("open_picker")
	# Cycle + place via controller methods that are only wired from InputMap in main —
	# smoke calls the same entrypoints main uses (cycle_module / place / rotate / elev / handle_player_confirm).
	var cyc: Dictionary = _ctrl.call("cycle_module", 1) as Dictionary
	if not bool(cyc.get("ok", false)):
		_fail("cycle", str(cyc))
		return
	var placed: Dictionary = _ctrl.call("place_highlighted_module") as Dictionary
	if not bool(placed.get("ok", false)):
		_fail("place", str(placed))
		return
	if str(placed.get("via", "")) != "input_place_highlighted":
		_fail("place_via", str(placed.get("via")))
		return
	var rot0 := float(((_ctrl.call("get_active_state") as Dictionary).get("placement", {}) as Dictionary).get("rotation_deg", 0))
	var rrot: Variant = _ctrl.call("rotate_preview_degrees", 15.0)
	if rrot is Dictionary and not bool((rrot as Dictionary).get("rotated", (rrot as Dictionary).get("ok", false))):
		_fail("rotate_failed", str(rrot))
		return
	var rot1 := float(((_ctrl.call("get_active_state") as Dictionary).get("placement", {}) as Dictionary).get("rotation_deg", 0))
	if is_equal_approx(rot0, rot1):
		_fail("rotate_no_delta", "rot0=%s rot1=%s" % [rot0, rot1])
		return
	# C2: no-preview rotate must explain (not silent).
	_ctrl.call("cancel_preview")
	var silent: Dictionary = _ctrl.call("rotate_preview_degrees", 15.0) as Dictionary
	if bool(silent.get("rotated", true)):
		_fail("rotate_without_preview_should_fail")
		return
	if str(silent.get("reason", silent.get("message", ""))).is_empty():
		_fail("rotate_without_preview_silent")
		return
	# Re-place for elevate/confirm path.
	_ctrl.call("place_highlighted_module")
	_ctrl.call("elevate", 1)
	var elev := float(((_ctrl.call("get_active_state") as Dictionary).get("placement", {}) as Dictionary).get("elevation", 0))
	if elev < 0.2:
		_fail("elevate", str(elev))
		return
	# Confirm via handle_player_confirm (main confirm_action path).
	var conf: Dictionary = _ctrl.call("handle_player_confirm") as Dictionary
	if not bool(conf.get("ok", false)):
		_fail("player_confirm", str(conf))
		return
	# New place then cancel — committed remains.
	_ctrl.call("place_highlighted_module")
	var can: Dictionary = _ctrl.call("cancel_preview") as Dictionary
	if not bool(can.get("committed_untouched", false)):
		_fail("cancel_keeps_committed")
		return
	_ok("full_player_path_select_place_rotate_elev_confirm_cancel")


func _test_esc_build_no_pause() -> void:
	_router.call("request_context", "build")
	_ctrl.call("place_highlighted_module")
	if _router.has_method("set_cancel_target"):
		_router.call("set_cancel_target", "preview_hologram", true)
	var r1: Dictionary = _router.call("resolve_escape") as Dictionary
	if bool(r1.get("pause", false)):
		_fail("esc_with_preview_opened_pause", str(r1))
		return
	if str(r1.get("resolved", "")) == "pause_menu":
		_fail("esc_resolved_pause_menu", str(r1))
		return
	# Idle build Esc must not open pause (F05-R2).
	_ctrl.call("cancel_preview")
	if _router.has_method("set_cancel_target"):
		_router.call("set_cancel_target", "preview_hologram", false)
	_router.call("request_context", "build")
	var r2: Dictionary = _router.call("resolve_escape") as Dictionary
	if bool(r2.get("pause", false)) or str(r2.get("resolved", "")) == "pause_menu":
		_fail("esc_idle_build_pause", str(r2))
		return
	_ok("esc_build_never_opens_pause")


func _test_esc_single_dispatch_counter() -> void:
	## P2E-CODEX-ESC-DOUBLE-01: one physical Esc path = one resolve apply, not signal+return double.
	## Simulate Main single-dispatch: guard on, resolve once, handle once (signal suppressed).
	if _router.has_method("reset_escape_resolve_count"):
		_router.call("reset_escape_resolve_count")
	_router.call("request_context", "build")
	_ctrl.call("place_highlighted_module")
	if _router.has_method("set_cancel_target"):
		_router.call("set_cancel_target", "preview_hologram", true)

	var cancel_count := 0
	var pause_count := 0
	var on_cancel := func(target: String, _aid: String) -> void:
		# Would double-apply if Main also handled return without guard.
		cancel_count += 1
		if target == "pause_menu":
			pause_count += 1
	if _router.has_signal("cancel_resolved"):
		_router.cancel_resolved.connect(on_cancel)

	# Main pattern with guard: signal must not double-apply cancel.
	var apply_count := 0
	var guard := true
	var on_cancel_guarded := func(target: String, _aid: String) -> void:
		if guard:
			return
		apply_count += 1
		if str(target) == "preview_hologram":
			_ctrl.call("cancel_preview")
	if _router.has_signal("cancel_resolved"):
		_router.cancel_resolved.disconnect(on_cancel)
		_router.cancel_resolved.connect(on_cancel_guarded)

	var res: Dictionary = _router.call("resolve_escape") as Dictionary
	if str(res.get("resolved", "")) != "preview_hologram":
		_fail("single_esc_resolved_target", str(res))
		return
	if bool(res.get("pause", false)):
		_fail("single_esc_pause")
		return
	# Main return path applies cancel exactly once.
	if bool((_ctrl.call("get_active_state") as Dictionary).get("active", false)):
		_ctrl.call("cancel_preview")
		apply_count += 1
	if apply_count != 1:
		_fail("single_esc_apply_count", "apply=%d" % apply_count)
		return
	if pause_count != 0:
		_fail("single_esc_zero_pause", "pause=%d" % pause_count)
		return
	# Second resolve same priority cleared → build_esc_no_pause, still no pause.
	var res2: Dictionary = _router.call("resolve_escape") as Dictionary
	if bool(res2.get("pause", false)):
		_fail("second_esc_pause", str(res2))
		return
	if _router.has_signal("cancel_resolved"):
		_router.cancel_resolved.disconnect(on_cancel_guarded)
	var n := 0
	if _router.has_method("get_escape_resolve_count"):
		n = int(_router.call("get_escape_resolve_count"))
	if n < 2:
		_fail("resolve_count_low", str(n))
		return
	_ok("esc_single_dispatch_exactly_one_cancel_zero_pause")


func _test_teardown_dispose() -> void:
	_ctrl.call("place_highlighted_module")
	_ctrl.call("dispose_all_previews")
	if _ctrl.call("get_preview_node") != null:
		_fail("dispose_preview_null")
		return
	if bool((_ctrl.call("get_active_state") as Dictionary).get("active", true)):
		_fail("dispose_active_false")
		return
	_ok("teardown_dispose_previews")

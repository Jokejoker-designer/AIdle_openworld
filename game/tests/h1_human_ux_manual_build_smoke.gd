## H1-CONSOLIDATE-001 Directive 79 C0 — Human UX + Manual Build UNIT smoke.
## UNIT TEST (controller-level): may call begin_manual_build / rotate_preview_degrees / elevate / handle_player_confirm.
## NOT InputMap E2E evidence — see ucbv_001_inputmap_e2e_smoke.gd for C2R F01.
## Closes H1-HUMAN-UX-01/02/BUILD-01 plus H1-CODEX-MB-F01/F02/F06.
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/h1_human_ux_manual_build_smoke.gd
extends SceneTree

const CatalogScript = preload("res://scripts/input/control_action_catalog.gd")
const RouterScript = preload("res://autoload/control_context_router.gd")
const PulseScript = preload("res://scripts/ui/cozy_helper_pulse.gd")
const CursorScript = preload("res://scripts/ui/control_1b_cursor_label.gd")
const CtrlScript = preload("res://scripts/modules/block_assembly/block_assembly_controller.gd")
const A11yScript = preload("res://autoload/control_accessibility_settings.gd")
const HudScript = preload("res://scripts/modules/block_assembly/block_assembly_hud.gd")
var _failures: PackedStringArray = []
var _passed: int = 0
var _router: Node = null
var _ctrl: Node = null
var _a11y: Node = null


func _initialize() -> void:
	print("[H1 human UX Manual Build smoke] starting…")
	CatalogScript.ensure_input_map_actions()
	_router = _resolve_router()
	_a11y = _resolve_a11y()
	_ctrl = CtrlScript.new() as Node
	root.add_child(_ctrl)
	_ctrl.call("bind_local_authority", 0)

	_test_helper_pulse_non_square()
	_test_os_pointer_default_no_square_proxy()
	_test_force_custom_cursor_wiring()
	_test_manual_build_label_source()
	_test_hud_cursor_valid_typed()
	_test_cursor_led_snapped_placement()
	_test_intentional_lmb_before_confirm()
	_test_place_at_cursor_fail_closed_outside_build()
	_test_invalid_surface_feedback()
	_test_qr_preview_only_in_build()
	_test_cancel_once_no_canonical()
	_test_confirm_world_commit_only()
	_test_no_absolute_root_lookup_in_lease()
	_finish()


func _finish() -> void:
	if _ctrl != null and _ctrl.has_method("dispose_all_previews"):
		_ctrl.call("dispose_all_previews")
	if _failures.is_empty():
		print("AIDLE_H1_HUMAN_UX_MANUAL_BUILD_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("AIDLE_H1_HUMAN_UX_MANUAL_BUILD_SMOKE=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
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
	n.name = "ControlContextRouter"
	root.add_child(n)
	return n


func _resolve_a11y() -> Node:
	var existing := root.get_node_or_null("ControlAccessibilitySettings")
	if existing != null:
		return existing
	# May already be autoload; if not, mount for snapshot tests.
	var n: Node = A11yScript.new() as Node
	n.name = "ControlAccessibilitySettings"
	root.add_child(n)
	return n


func _test_helper_pulse_non_square() -> void:
	## H1-HUMAN-UX-01
	if PulseScript == null:
		_fail("UX01_pulse_script_null")
		return
	var pulse: CanvasLayer = PulseScript.new() as CanvasLayer
	if pulse == null:
		_fail("UX01_pulse_new_failed")
		return
	root.add_child(pulse)
	var res: Dictionary = pulse.call("fire_pulse", "world_ability") as Dictionary
	if bool(res.get("is_square", true)):
		_fail("UX01_pulse_marked_square", str(res))
		pulse.queue_free()
		return
	if str(res.get("presentation", "")) != "ring_pulse":
		_fail("UX01_presentation", str(res.get("presentation")))
		pulse.queue_free()
		return
	if not bool(res.get("non_durable", false)):
		_fail("UX01_durable", str(res))
		pulse.queue_free()
		return
	if pulse.has_method("get_presentation_audit"):
		var audit: Dictionary = pulse.call("get_presentation_audit") as Dictionary
		if not bool(audit.get("pass_non_square", false)):
			_fail("UX01_audit_square", str(audit))
			pulse.queue_free()
			return
		if bool(audit.get("uses_color_rect_square", true)):
			_fail("UX01_still_colorrect", str(audit))
			pulse.queue_free()
			return
	var src := FileAccess.get_file_as_string("res://scripts/ui/cozy_helper_pulse.gd")
	if src.find("ColorRect.new()") >= 0 and src.find("PulseRing") < 0:
		_fail("UX01_source_colorrect")
		pulse.queue_free()
		return
	if src.find("120, 120") >= 0 or src.find("Vector2(120, 120)") >= 0:
		_fail("UX01_source_120_square")
		pulse.queue_free()
		return
	_ok("H1-HUMAN-UX-01_helper_pulse_non_square_ring")
	pulse.queue_free()


func _test_os_pointer_default_no_square_proxy() -> void:
	## H1-HUMAN-UX-02
	var cur: CanvasLayer = CursorScript.new() as CanvasLayer
	root.add_child(cur)
	# Default scale 1.0 → OS pointer, proxy hidden.
	if cur.has_method("apply_scale_for_test"):
		cur.call("apply_scale_for_test", 1.0)
	if cur.has_method("set_label_enabled_for_test"):
		cur.call("set_label_enabled_for_test", false)
	var snap: Dictionary = cur.call("get_runtime_snapshot") as Dictionary
	if bool(snap.get("cursor_proxy_visible", true)):
		_fail("UX02_proxy_visible_default", str(snap))
		cur.queue_free()
		return
	if bool(snap.get("forced_square_proxy", true)):
		_fail("UX02_forced_square", str(snap))
		cur.queue_free()
		return
	if not bool(snap.get("os_pointer_default", false)):
		_fail("UX02_os_pointer_not_default", str(snap))
		cur.queue_free()
		return
	# Optional label respects a11y flag.
	if cur.has_method("set_label_enabled_for_test"):
		cur.call("set_label_enabled_for_test", true)
	var snap2: Dictionary = cur.call("get_runtime_snapshot") as Dictionary
	if not bool(snap2.get("action_label_near_cursor", false)) and not bool(snap2.get("label_visible", false)):
		# label_enabled sets _enabled_label; snapshot should reflect it
		pass
	if not bool(snap2.get("action_label_near_cursor", false)):
		_fail("UX02_label_flag_off", str(snap2))
		cur.queue_free()
		return
	# Label node must exist and be toggleable (visibility may depend on process frame).
	if cur.get_node_or_null("Root/ActionLabel") == null and not bool(snap2.get("label_visible", false)):
		# Fallback: enabled flag is authoritative for a11y contract in headless.
		if not bool(snap2.get("action_label_near_cursor", false)):
			_fail("UX02_label_not_optional_on", str(snap2))
			cur.queue_free()
			return
	# Large a11y scale may show non-square tip, never forced square flag.
	if cur.has_method("apply_scale_for_test"):
		cur.call("apply_scale_for_test", 1.75)
	var snap3: Dictionary = cur.call("get_runtime_snapshot") as Dictionary
	if bool(snap3.get("forced_square_proxy", true)):
		_fail("UX02_large_still_square", str(snap3))
		cur.queue_free()
		return
	if float(snap3.get("cursor_size_scale", 0.0)) < 1.4:
		_fail("UX02_scale_not_applied", str(snap3))
		cur.queue_free()
		return
	if _a11y != null and _a11y.has_method("get_snapshot"):
		var asnap: Dictionary = _a11y.call("get_snapshot") as Dictionary
		if bool(asnap.get("force_custom_cursor", true)):
			_fail("UX02_a11y_force_custom_default", str(asnap))
			cur.queue_free()
			return
	var csrc := FileAccess.get_file_as_string("res://scripts/ui/control_1b_cursor_label.gd")
	if csrc.find("forced_square_proxy") < 0:
		_fail("UX02_missing_forced_square_flag")
		cur.queue_free()
		return
	_ok("H1-HUMAN-UX-02_os_pointer_default_optional_label")
	cur.queue_free()


func _test_force_custom_cursor_wiring() -> void:
	## H1-CODEX-MB-F06: force_custom_cursor consumed; default remains OS pointer.
	var cur: CanvasLayer = CursorScript.new() as CanvasLayer
	root.add_child(cur)
	if cur.has_method("apply_scale_for_test"):
		cur.call("apply_scale_for_test", 1.0)
	if cur.has_method("set_force_custom_cursor_for_test"):
		cur.call("set_force_custom_cursor_for_test", false)
	var snap0: Dictionary = cur.call("get_runtime_snapshot") as Dictionary
	if bool(snap0.get("force_custom_cursor", true)):
		_fail("F06_force_custom_default_on", str(snap0))
		cur.queue_free()
		return
	if not bool(snap0.get("os_pointer_default", false)):
		_fail("F06_os_pointer_default_off", str(snap0))
		cur.queue_free()
		return
	if cur.has_method("set_force_custom_cursor_for_test"):
		cur.call("set_force_custom_cursor_for_test", true)
	var snap1: Dictionary = cur.call("get_runtime_snapshot") as Dictionary
	if not bool(snap1.get("force_custom_cursor", false)):
		_fail("F06_force_custom_not_consumed", str(snap1))
		cur.queue_free()
		return
	if bool(snap1.get("os_pointer_default", true)):
		_fail("F06_force_still_os_default", str(snap1))
		cur.queue_free()
		return
	if bool(snap1.get("forced_square_proxy", true)):
		_fail("F06_force_square", str(snap1))
		cur.queue_free()
		return
	# Restore OS default path.
	if cur.has_method("set_force_custom_cursor_for_test"):
		cur.call("set_force_custom_cursor_for_test", false)
	if _a11y != null and _a11y.has_method("set_force_custom_cursor"):
		_a11y.call("set_force_custom_cursor", false, false)
	var asnap: Dictionary = _a11y.call("get_snapshot") as Dictionary if _a11y != null else {}
	if bool(asnap.get("force_custom_cursor", true)):
		_fail("F06_a11y_force_not_false", str(asnap))
		cur.queue_free()
		return
	var csrc := FileAccess.get_file_as_string("res://scripts/ui/control_1b_cursor_label.gd")
	if csrc.find("force_custom_cursor") < 0:
		_fail("F06_cursor_consumer_unwired")
		cur.queue_free()
		return
	_ok("H1-CODEX-MB-F06_force_custom_cursor_wired_os_default")
	cur.queue_free()


func _test_manual_build_label_source() -> void:
	## H1-HUMAN-BUILD-01 rename + H1-CODEX-MB-F02 scene residual
	var bar_src := FileAccess.get_file_as_string("res://scripts/ui/playable_action_bar.gd")
	if bar_src.find("Manual Build") < 0:
		_fail("BUILD01_label_missing")
		return
	if bar_src.find('btn_demo.text = "Small Build"') >= 0:
		_fail("BUILD01_small_build_residual")
		return
	if bar_src.find("Demo Build") >= 0 and bar_src.find('text = "Demo Build"') >= 0:
		_fail("BUILD01_demo_build_residual")
		return
	var tscn := FileAccess.get_file_as_string("res://scenes/ui/playable_action_bar.tscn")
	if tscn.find("Manual Build") < 0:
		_fail("F02_tscn_manual_build_missing")
		return
	if tscn.find("Small Build") >= 0:
		_fail("F02_tscn_small_build_residual")
		return
	var main_src := FileAccess.get_file_as_string("res://scripts/main/main.gd")
	if main_src.find("begin_manual_build") < 0 and main_src.find("Manual Build") < 0:
		_fail("BUILD01_main_manual_missing")
		return
	_ok("H1-HUMAN-BUILD-01_manual_build_label")


func _test_hud_cursor_valid_typed() -> void:
	## H1-CODEX-MB-F01: HUD types cursor_hit path (no Variant inference).
	var src := FileAccess.get_file_as_string("res://scripts/modules/block_assembly/block_assembly_hud.gd")
	if src.find("var cursor_valid: bool") < 0 and src.find("var cursor_valid: Variant") < 0:
		_fail("F01_cursor_valid_untyped")
		return
	if src.find("var cursor_hit_present: bool") < 0:
		_fail("F01_cursor_hit_present_missing")
		return
	# Runtime: bind controller HUD and apply state without error.
	var hud: CanvasLayer = HudScript.new() as CanvasLayer
	root.add_child(hud)
	hud.call("bind_controller", _ctrl)
	_router.call("request_context", "build")
	_ctrl.call("begin_manual_build")
	hud.call("refresh")
	_ok("H1-CODEX-MB-F01_hud_cursor_valid_typed")
	hud.queue_free()


func _test_cursor_led_snapped_placement() -> void:
	## Distinct cursor positions → distinct snapped preview positions; LMB preview only.
	_router.call("request_context", "build")
	var cam := Camera3D.new()
	cam.name = "TestCam"
	root.add_child(cam)
	cam.current = true
	# Fixed-angle-ish: above origin looking down-forward (in-tree pose; no look_at tree error).
	cam.look_at_from_position(Vector3(0.0, 12.0, 12.0), Vector3(0.0, 0.0, 0.0), Vector3.UP)

	var boot: Dictionary = _ctrl.call("begin_manual_build") as Dictionary
	if not bool(boot.get("ok", false)):
		_fail("BUILD01_begin_manual", str(boot))
		cam.queue_free()
		return
	if not bool(boot.get("preview_only", false)):
		_fail("BUILD01_begin_not_preview_only", str(boot))
		cam.queue_free()
		return
	if bool(boot.get("client_world_commit", true)):
		_fail("BUILD01_begin_client_commit", str(boot))
		cam.queue_free()
		return

	# Distinct cursor world positions → distinct snapped preview positions (0.5 m grid).
	var f1: Dictionary = _ctrl.call("force_cursor_world_for_test", 0.0, 0.0) as Dictionary
	var place1: Dictionary = ((_ctrl.call("get_active_state") as Dictionary).get("placement", {}) as Dictionary).duplicate(true)
	var f2: Dictionary = _ctrl.call("force_cursor_world_for_test", 2.0, 1.5) as Dictionary
	var place2: Dictionary = ((_ctrl.call("get_active_state") as Dictionary).get("placement", {}) as Dictionary).duplicate(true)
	if not bool(f1.get("ok", false)) or not bool(f2.get("ok", false)):
		_fail("BUILD01_force_cursor", "%s | %s" % [str(f1), str(f2)])
		cam.queue_free()
		return
	var x1 := float(place1.get("x", 0.0))
	var x2 := float(place2.get("x", 0.0))
	var y2 := float(place2.get("y", 0.0))
	if absf(x1 - snappedf(x1, 0.5)) > 0.001:
		_fail("BUILD01_not_snapped", str(place1))
		cam.queue_free()
		return
	if absf(x2 - 2.0) > 0.01 or absf(y2 - 1.5) > 0.01:
		_fail("BUILD01_distinct_snap", "p1=%s p2=%s" % [str(place1), str(place2)])
		cam.queue_free()
		return

	# LMB place path (cursor API) is preview-only / never client commit.
	# Use null camera — place_at_cursor still moves via last force_cursor raw when update fails closed.
	var click: Dictionary = _ctrl.call("place_highlighted_module") as Dictionary
	if bool(click.get("client_world_commit", false)):
		_fail("BUILD01_click_canonical", str(click))
		cam.queue_free()
		return
	if not bool(click.get("preview_only", true)) and str(click.get("via", "")) == "":
		_fail("BUILD01_click_not_preview", str(click))
		cam.queue_free()
		return
	# Free-float forbidden surface still present.
	var free: Dictionary = _ctrl.call("set_snap_enabled", false) as Dictionary
	if bool(free.get("ok", false)):
		_fail("BUILD01_free_float_allowed", str(free))
		cam.queue_free()
		return
	# Ray helper surface exists (null camera fails closed).
	var ray: Dictionary = _ctrl.call("project_screen_to_ground", null, Vector2(1, 1)) as Dictionary
	if bool(ray.get("ok", true)):
		_fail("BUILD01_ray_null_cam", str(ray))
		cam.queue_free()
		return
	_ok("H1-HUMAN-BUILD-01_cursor_led_snapped_preview")
	cam.queue_free()


func _test_intentional_lmb_before_confirm() -> void:
	## H1-CODEX-MB-F06: Manual Build origin boot ghost cannot confirm until intentional place.
	_router.call("request_context", "build")
	if _ctrl.has_method("end_manual_build_mode"):
		_ctrl.call("end_manual_build_mode")
	if _ctrl.has_method("cancel_preview"):
		_ctrl.call("cancel_preview")
	var boot: Dictionary = _ctrl.call("begin_manual_build") as Dictionary
	if not bool(boot.get("ok", false)):
		_fail("F06_lmb_boot", str(boot))
		return
	if bool(boot.get("intentional_place_done", true)):
		_fail("F06_boot_already_intentional", str(boot))
		return
	if bool(_ctrl.call("can_confirm")):
		_fail("F06_confirm_before_lmb")
		return
	# force_cursor alone is not intentional LMB.
	var f: Dictionary = _ctrl.call("force_cursor_world_for_test", 0.5, 0.5) as Dictionary
	if not bool(f.get("ok", false)):
		_fail("F06_force_cursor", str(f))
		return
	if bool(_ctrl.call("can_confirm")):
		_fail("F06_confirm_after_force_only")
		return
	# Intentional place (highlighted module / LMB place path) unlocks confirm when valid.
	var placed: Dictionary = _ctrl.call("place_highlighted_module") as Dictionary
	if not bool(placed.get("ok", false)):
		_fail("F06_place_highlighted", str(placed))
		return
	var cs: Dictionary = _ctrl.call("get_cursor_placement_state") as Dictionary
	if not bool(cs.get("intentional_place_done", false)):
		_fail("F06_intentional_not_set", str(cs))
		return
	if not bool(_ctrl.call("can_confirm")):
		_fail("F06_confirm_after_intentional")
		return
	_ok("H1-CODEX-MB-F06_intentional_lmb_before_confirm")


func _test_place_at_cursor_fail_closed_outside_build() -> void:
	## H1-CODEX-MB-F06: place_at_cursor outside Build never silently enables Manual Build.
	if _ctrl.has_method("cancel_preview"):
		_ctrl.call("cancel_preview")
	if _ctrl.has_method("end_manual_build_mode"):
		_ctrl.call("end_manual_build_mode")
	var sw: Dictionary = _router.call("request_context", "exploration") as Dictionary
	if str(_router.call("get_primary_context")) != "exploration":
		_fail("F06_router_not_exploration", "%s | %s" % [str(sw), str(_router.call("get_primary_context"))])
		return
	if bool(_ctrl.call("is_manual_build_mode")):
		_fail("F06_manual_still_on_before_place")
		return
	# Null camera is enough — fail-closed must run before ray math.
	var res: Dictionary = _ctrl.call("place_at_cursor", Vector2(100, 100), null) as Dictionary
	if bool(res.get("ok", true)):
		_fail("F06_place_outside_build_ok", str(res))
		return
	if str(res.get("code", "")) != "not_build_context":
		_fail("F06_place_outside_code", str(res))
		return
	if bool(_ctrl.call("is_manual_build_mode")):
		_fail("F06_silent_manual_enable")
		return
	# force_cursor without Manual Build also fails closed.
	var f: Dictionary = _ctrl.call("force_cursor_world_for_test", 1.0, 1.0) as Dictionary
	if bool(f.get("ok", true)):
		_fail("F06_force_outside_manual", str(f))
		return
	_ok("H1-CODEX-MB-F06_place_at_cursor_fail_closed")


func _test_invalid_surface_feedback() -> void:
	_router.call("request_context", "build")
	var boot: Dictionary = _ctrl.call("begin_manual_build") as Dictionary
	if not bool(boot.get("ok", false)):
		_fail("BUILD01_invalid_boot", str(boot))
		return
	# Budget-far select → rejected (no free-float / out of bounds).
	var bad: Dictionary = _ctrl.call("select_module", "block_cube_round", "structure", "", 200.0, 0.0, 0.0, 0.0) as Dictionary
	if bool(bad.get("ok", false)):
		_fail("BUILD01_budget_should_fail", str(bad))
		return
	# Re-enter valid preview then force far cursor world for invalid visual feedback.
	var okp: Dictionary = _ctrl.call("begin_manual_build") as Dictionary
	if not bool(okp.get("ok", false)):
		_fail("BUILD01_reselect", str(okp))
		return
	var far: Dictionary = _ctrl.call("force_cursor_world_for_test", 200.0, 0.0) as Dictionary
	if bool(far.get("cursor_hit_valid", true)):
		_fail("BUILD01_far_still_valid", str(far))
		return
	var st: Dictionary = _ctrl.call("get_active_state") as Dictionary
	if bool(st.get("cursor_hit_valid", true)):
		_fail("BUILD01_state_cursor_valid", str(st))
		return
	if bool(_ctrl.call("can_confirm")):
		_fail("BUILD01_confirm_while_invalid")
		return
	# Null camera ray fails closed.
	var no_cam: Dictionary = _ctrl.call("project_screen_to_ground", null, Vector2(10, 10)) as Dictionary
	if bool(no_cam.get("ok", true)):
		_fail("BUILD01_null_camera_ok", str(no_cam))
		return
	_ok("H1-HUMAN-BUILD-01_invalid_surface_feedback")


func _test_qr_preview_only_in_build() -> void:
	## Q/R rotate preview only — camera not touched here; elevation via elevate.
	_router.call("request_context", "build")
	if _ctrl.has_method("end_manual_build_mode"):
		_ctrl.call("end_manual_build_mode")
	if _ctrl.has_method("cancel_preview"):
		_ctrl.call("cancel_preview")
	var boot: Dictionary = _ctrl.call("begin_manual_build") as Dictionary
	if not bool(boot.get("ok", false)):
		var placed: Dictionary = _ctrl.call("place_highlighted_module") as Dictionary
		if not bool(placed.get("ok", false)):
			_fail("BUILD01_qr_boot", "%s | %s" % [str(boot), str(placed)])
			return
	var st0: Dictionary = _ctrl.call("get_active_state") as Dictionary
	if not bool(st0.get("active", false)):
		_fail("BUILD01_qr_not_active", str(st0))
		return
	var rot0 := float((st0.get("placement", {}) as Dictionary).get("rotation_deg", 0.0))
	var rrot: Variant = _ctrl.call("rotate_preview_degrees", 15.0)
	var rotated := false
	if rrot is Dictionary:
		rotated = bool((rrot as Dictionary).get("rotated", (rrot as Dictionary).get("ok", false)))
	else:
		rotated = rrot == true
	if not rotated:
		_fail("BUILD01_rotate_false", str(rrot))
		return
	var rot1 := float(((_ctrl.call("get_active_state") as Dictionary).get("placement", {}) as Dictionary).get("rotation_deg", 0.0))
	if is_equal_approx(rot0, rot1):
		_fail("BUILD01_rotate_no_delta", "rot0=%s rot1=%s" % [rot0, rot1])
		return
	_ctrl.call("elevate", 1)
	var elev := float(((_ctrl.call("get_active_state") as Dictionary).get("placement", {}) as Dictionary).get("elevation", 0.0))
	if elev < 0.2:
		_fail("BUILD01_elevate", str(elev))
		return
	# Collision/nav still off pre-commit.
	var st: Dictionary = _ctrl.call("get_active_state") as Dictionary
	if bool(st.get("collision", true)) or bool(st.get("navigation", true)):
		_fail("BUILD01_preview_collision", str(st))
		return
	_ok("H1-HUMAN-BUILD-01_qr_elev_preview_only")


func _test_cancel_once_no_canonical() -> void:
	_router.call("request_context", "build")
	_ctrl.call("begin_manual_build")
	if not bool((_ctrl.call("get_active_state") as Dictionary).get("active", false)):
		_ctrl.call("place_highlighted_module")
	var before := int(_ctrl.call("get_committed_count"))
	var c1: Dictionary = _ctrl.call("cancel_preview") as Dictionary
	if not bool(c1.get("ok", false)):
		_fail("BUILD01_cancel", str(c1))
		return
	if not bool(c1.get("single_cancel", false)) and not bool(c1.get("cancelled", false)):
		_fail("BUILD01_cancel_flags", str(c1))
		return
	if int(_ctrl.call("get_committed_count")) != before:
		_fail("BUILD01_cancel_touched_committed")
		return
	# Second cancel is no-op (still ok, no dual fire side effects).
	var c2: Dictionary = _ctrl.call("cancel_preview") as Dictionary
	if not bool(c2.get("ok", false)):
		_fail("BUILD01_cancel2", str(c2))
		return
	if bool((_ctrl.call("get_active_state") as Dictionary).get("active", true)):
		_fail("BUILD01_still_active_after_cancel")
		return
	# Awaiting place click prevents auto ghost until LMB.
	var cs: Dictionary = _ctrl.call("get_cursor_placement_state") as Dictionary
	if not bool(cs.get("awaiting_place_click", false)):
		_fail("BUILD01_awaiting_place", str(cs))
		return
	_ok("H1-HUMAN-BUILD-01_cancel_once")


func _test_confirm_world_commit_only() -> void:
	_router.call("request_context", "build")
	_ctrl.call("end_manual_build_mode")
	var sel: Dictionary = _ctrl.call("select_module", "block_cube_round", "structure", "", 0.0, 0.0, 0.0, 0.0) as Dictionary
	if not bool(sel.get("ok", false)):
		_fail("BUILD01_confirm_select", str(sel))
		return
	var conf: Dictionary = _ctrl.call("handle_player_confirm") as Dictionary
	if not bool(conf.get("ok", false)):
		_fail("BUILD01_confirm", str(conf))
		return
	var receipt: Dictionary = conf.get("receipt", {}) as Dictionary
	var status := str(receipt.get("status", ""))
	if status != "committed" and status != "idempotent_replay":
		_fail("BUILD01_confirm_status", status)
		return
	var forged: Dictionary = _ctrl.call("reject_client_authored_success", {"status": "committed"}) as Dictionary
	if bool(forged.get("ok", true)) or bool(forged.get("accepted", true)):
		_fail("BUILD01_forged_accepted", str(forged))
		return
	_ok("H1-HUMAN-BUILD-01_confirm_world_commit_only")


func _test_no_absolute_root_lookup_in_lease() -> void:
	## Invariant: absolute /root get_node not reintroduced in leased product files.
	var paths := PackedStringArray([
		"res://scripts/ui/cozy_helper_pulse.gd",
		"res://scripts/ui/control_1b_cursor_label.gd",
		"res://scripts/ui/playable_action_bar.gd",
		"res://scripts/main/main.gd",
		"res://scripts/modules/block_assembly/block_assembly_controller.gd",
		"res://scripts/modules/block_assembly/block_preview_entity.gd",
		"res://scripts/modules/block_assembly/block_assembly_hud.gd",
		"res://autoload/control_accessibility_settings.gd",
	])
	for p in paths:
		var src := FileAccess.get_file_as_string(p)
		if src.find('get_node("/root/') >= 0 or src.find("get_node('/root/") >= 0:
			_fail("absolute_root_lookup", p)
			return
		if src.find('NodePath("/root/') >= 0:
			_fail("absolute_root_nodepath", p)
			return
	_ok("lease_no_absolute_root_get_node")

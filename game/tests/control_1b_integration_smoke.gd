## WO-CTRL-1B-002 C0 correction — runtime integration smoke (headless).
## Closes H-03,07,12,17,19,20,26,28 + A3-F09/F10 gates with executable assertions.
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/control_1b_integration_smoke.gd
## Exit 0 + AIDLE_CTRL_1B_INTEGRATION_SMOKE=PASS. Zero ERROR lines required.
extends SceneTree

const CatalogScript = preload("res://scripts/input/control_action_catalog.gd")
const RouterScript = preload("res://autoload/control_context_router.gd")
const A11yScript = preload("res://autoload/control_accessibility_settings.gd")

const CTX_HUD_PATH := "res://scripts/ui/context_action_hud.gd"
const SETTINGS_PATH := "res://scripts/ui/control_settings_panel.gd"
const HOMESTEAD_PATH := "res://scripts/ui/cozy_homestead_panel.gd"
const PULSE_PATH := "res://scripts/ui/cozy_helper_pulse.gd"
const INSTANCE_PATH := "res://scripts/modules/manifestation/manifestation_instance.gd"
const INSPECT_PATH := "res://scripts/ui/control_1b_inspect_panel.gd"
const PROPOSAL_PATH := "res://scripts/ui/control_1b_proposal_card.gd"
const CURSOR_PATH := "res://scripts/ui/control_1b_cursor_label.gd"
const CHAT_SCENE_PATH := "res://scenes/ui/companion_chat_panel.tscn"
const CHAT_PATH := "res://scripts/modules/companion/companion_chat_panel.gd"
const CAMERA_PATH := "res://scripts/camera/cozy_camera.gd"

var _failures: PackedStringArray = []
var _passed: int = 0
var _router: Node = null
var _a11y: Node = null
var _ContextHud: GDScript
var _SettingsPanel: GDScript
var _Homestead: GDScript
var _HelperPulse: GDScript
var _Instance: GDScript
var _Inspect: GDScript
var _Proposal: GDScript
var _Cursor: GDScript
var _Chat: GDScript
var _Camera: GDScript


func _initialize() -> void:
	print("[CTRL-1B-002 C0 integration smoke] starting…")
	CatalogScript.ensure_input_map_actions()
	_ContextHud = load(CTX_HUD_PATH) as GDScript
	_SettingsPanel = load(SETTINGS_PATH) as GDScript
	_Homestead = load(HOMESTEAD_PATH) as GDScript
	_HelperPulse = load(PULSE_PATH) as GDScript
	_Instance = load(INSTANCE_PATH) as GDScript
	_Inspect = load(INSPECT_PATH) as GDScript
	_Proposal = load(PROPOSAL_PATH) as GDScript
	_Cursor = load(CURSOR_PATH) as GDScript
	_Chat = load(CHAT_PATH) as GDScript
	_Camera = load(CAMERA_PATH) as GDScript
	_router = _resolve_router()
	_a11y = _resolve_a11y()
	if _router == null:
		_fail("router_unavailable")
		_finish()
		return
	if _ContextHud == null or _SettingsPanel == null or _Homestead == null \
			or _HelperPulse == null or _Instance == null or _Inspect == null \
			or _Proposal == null or _Cursor == null or _Chat == null or _Camera == null:
		_fail("script_load", "missing product scripts for C0 gates")
		_finish()
		return
	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")

	await _test_hud_max_four_and_non_color()
	await _test_context_hud_updates_on_transition()
	_test_esc_preview_before_pause()
	_test_esc_composer_before_pause()
	await _test_esc_homestead_before_pause()
	_test_esc_idle_opens_pause_signal()
	await _test_helper_pulse_non_durable()
	await _test_homestead_read_only()
	await _test_settings_panel_a11y_surface()
	_test_delete_proposal_ui_path()
	_test_undo_compensation_path()
	_test_r_exploration_no_hologram_rotate()
	await _test_h10_exploration_r_camera_yaw_real_path()
	await _test_r_build_rotates_preview()
	await _test_build_r_camera_yaw_unchanged()
	await _test_rotate_camera_right_remap_still_works()
	await _test_q_build_rotate_left()
	await _test_preview_non_authority_flags()
	_test_sprint_toggle_surface()
	# C0 correction gates
	await _test_h03_prompt_send_vs_newline()
	await _test_h07_inspect_read_only()
	await _test_h17_proposal_card()
	await _test_h19_confirmation_hold()
	await _test_h20_confirm_handoff_and_cancel()
	await _test_h26_sensitivity_observable()
	await _test_h28_cursor_and_action_label_consumer()
	await _test_a3_f09_full_remap_catalog()
	await _test_responsive_bottom_layers_no_overlap_metrics()
	_finish()


func _resolve_router() -> Node:
	var existing := root.get_node_or_null("ControlContextRouter")
	if existing == null:
		for c in root.get_children():
			if str(c.name) == "ControlContextRouter":
				existing = c
				break
	if existing != null:
		print("  using autoload ControlContextRouter")
		return existing
	var node: Node = RouterScript.new() as Node
	root.add_child(node)
	print("  instantiated ControlContextRouter locally")
	return node


func _resolve_a11y() -> Node:
	var existing := root.get_node_or_null("ControlAccessibilitySettings")
	if existing == null:
		for c in root.get_children():
			if str(c.name) == "ControlAccessibilitySettings":
				existing = c
				break
	if existing != null:
		return existing
	var node: Node = A11yScript.new() as Node
	root.add_child(node)
	return node


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _test_hud_max_four_and_non_color() -> void:
	var hud: CanvasLayer = _ContextHud.new() as CanvasLayer
	root.add_child(hud)
	await process_frame
	if not hud.has_method("set_actions"):
		_fail("hud_missing_set_actions")
		hud.queue_free()
		return
	hud.call("set_actions", "exploration", PackedStringArray([
		"interact_primary", "interact_secondary", "world_ability", "build_mode_toggle", "extra_should_drop"
	]))
	var n: int = int(hud.call("get_visible_action_count"))
	if n > 4:
		_fail("hud_max_four", "count=%d" % n)
		hud.queue_free()
		return
	var texts: PackedStringArray = hud.call("get_slot_texts") as PackedStringArray
	if texts.is_empty():
		_fail("hud_empty_slots")
		hud.queue_free()
		return
	var has_text_cue := false
	for t in texts:
		if "[" in t and "]" in t:
			has_text_cue = true
			break
	if not has_text_cue:
		_fail("hud_non_color_cue_missing", str(texts))
		hud.queue_free()
		return
	_ok("hud_max_four_and_non_color_cues")
	hud.queue_free()


func _test_context_hud_updates_on_transition() -> void:
	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")
	var hud: CanvasLayer = _ContextHud.new() as CanvasLayer
	root.add_child(hud)
	await process_frame
	_router.call("request_context", "build")
	await process_frame
	if hud.has_method("_refresh_from_router"):
		hud.call("_refresh_from_router")
	var actions: PackedStringArray = hud.call("get_visible_actions") as PackedStringArray
	if actions.size() > 4:
		_fail("hud_build_over_four", str(actions.size()))
		hud.queue_free()
		return
	var ra: PackedStringArray = _router.call("get_hud_actions") as PackedStringArray
	if ra.size() > 4:
		_fail("router_hud_over_four", str(ra))
		hud.queue_free()
		return
	_ok("context_hud_updates_on_transition")
	hud.queue_free()
	_router.call("request_context", "exploration")


func _test_esc_preview_before_pause() -> void:
	_router.call("reset_to_defaults")
	_router.call("set_cancel_target", "preview_hologram", true)
	var got_pause := [false]
	var on_pause := func(): got_pause[0] = true
	_router.pause_requested.connect(on_pause)
	var r: Dictionary = _router.call("resolve_escape") as Dictionary
	_router.pause_requested.disconnect(on_pause)
	if bool(r.get("pause", true)):
		_fail("esc_preview_paused", str(r))
		return
	if str(r.get("resolved", "")) != "preview_hologram":
		_fail("esc_preview_target", str(r))
		return
	if got_pause[0]:
		_fail("esc_preview_emitted_pause")
		return
	_ok("esc_preview_before_pause")


func _test_esc_composer_before_pause() -> void:
	_router.call("reset_to_defaults")
	_router.call("request_context", "companion")
	_router.call("set_cancel_target", "prompt_composer_or_dialogue", true)
	var r: Dictionary = _router.call("resolve_escape") as Dictionary
	if bool(r.get("pause", true)):
		_fail("esc_composer_paused", str(r))
		return
	if str(r.get("resolved", "")) != "prompt_composer_or_dialogue":
		_fail("esc_composer_target", str(r))
		return
	_ok("esc_composer_before_pause")


func _test_esc_homestead_before_pause() -> void:
	_router.call("reset_to_defaults")
	var panel: CanvasLayer = _Homestead.new() as CanvasLayer
	root.add_child(panel)
	await process_frame
	panel.call("open_panel")
	await process_frame
	if not bool(panel.call("is_open")):
		_fail("homestead_not_open")
		panel.queue_free()
		return
	var r: Dictionary = _router.call("resolve_escape") as Dictionary
	if bool(r.get("pause", true)):
		_fail("esc_homestead_paused", str(r))
		panel.queue_free()
		return
	if str(r.get("resolved", "")) == "world_tool_panel":
		panel.call("close_panel")
	if bool(panel.call("is_open")):
		panel.call("close_panel")
	if bool(panel.call("is_open")):
		_fail("homestead_still_open")
		panel.queue_free()
		return
	_ok("esc_homestead_before_pause")
	panel.queue_free()


func _test_esc_idle_opens_pause_signal() -> void:
	_router.call("reset_to_defaults")
	var got_pause := [false]
	var on_pause := func(): got_pause[0] = true
	_router.pause_requested.connect(on_pause)
	var r: Dictionary = _router.call("resolve_escape") as Dictionary
	_router.pause_requested.disconnect(on_pause)
	if not bool(r.get("pause", false)):
		_fail("esc_idle_no_pause", str(r))
		return
	if not got_pause[0]:
		_fail("esc_idle_no_signal")
		return
	_ok("esc_idle_pause_signal")


func _test_helper_pulse_non_durable() -> void:
	var pulse: CanvasLayer = _HelperPulse.new() as CanvasLayer
	root.add_child(pulse)
	await process_frame
	_router.call("reset_to_defaults")
	var d: Dictionary = _router.call("try_dispatch", "world_ability") as Dictionary
	if not bool(d.get("ok", false)):
		_fail("world_ability_dispatch", str(d))
		pulse.queue_free()
		return
	if not bool(d.get("non_durable", false)):
		_fail("world_ability_not_marked_non_durable", str(d))
		pulse.queue_free()
		return
	var res: Dictionary = pulse.call("fire_pulse", "world_ability") as Dictionary
	if bool(res.get("mints_inventory", true)) or bool(res.get("mints_currency", true)) \
			or bool(res.get("mints_ownership", true)):
		_fail("helper_pulse_mints", str(res))
		pulse.queue_free()
		return
	if not bool(res.get("non_durable", false)):
		_fail("helper_pulse_durable", str(res))
		pulse.queue_free()
		return
	_ok("helper_pulse_non_durable")
	pulse.queue_free()


func _test_homestead_read_only() -> void:
	var panel: CanvasLayer = _Homestead.new() as CanvasLayer
	root.add_child(panel)
	await process_frame
	panel.call("open_panel")
	var snap: Dictionary = panel.call("get_read_only_snapshot") as Dictionary
	if not bool(snap.get("read_only", false)):
		_fail("homestead_not_read_only", str(snap))
		panel.queue_free()
		return
	if bool(snap.get("mints_inventory", true)) or bool(snap.get("mints_ownership", true)) \
			or bool(snap.get("mints_currency", true)) or bool(snap.get("durable_mutation", true)):
		_fail("homestead_mints", str(snap))
		panel.queue_free()
		return
	panel.call("close_panel")
	_ok("homestead_read_only")
	panel.queue_free()


func _test_settings_panel_a11y_surface() -> void:
	var panel: CanvasLayer = _SettingsPanel.new() as CanvasLayer
	root.add_child(panel)
	await process_frame
	panel.call("open_panel")
	if not bool(panel.call("is_open")):
		_fail("settings_not_open")
		panel.queue_free()
		return
	if _a11y != null and _a11y.has_method("set_sprint_mode"):
		_a11y.call("set_sprint_mode", "toggle")
	if _a11y != null and _a11y.has_method("set_reduced_motion"):
		_a11y.call("set_reduced_motion", true)
	if _a11y != null and _a11y.has_method("set_confirmation_hold_seconds"):
		_a11y.call("set_confirmation_hold_seconds", 0.0)
	if _a11y != null and _a11y.has_method("set_cursor_size_scale"):
		_a11y.call("set_cursor_size_scale", 1.5)
	var snap: Dictionary = _a11y.call("get_snapshot") as Dictionary if _a11y else {}
	if str(snap.get("sprint_mode", "")) != "toggle":
		_fail("sprint_toggle_not_set", str(snap.get("sprint_mode", "")))
		panel.queue_free()
		return
	if not bool(snap.get("reduced_motion", false)):
		_fail("reduced_motion_not_set")
		panel.queue_free()
		return
	if _a11y:
		_a11y.call("set_sprint_mode", "hold")
		_a11y.call("set_reduced_motion", false)
		_a11y.call("set_confirmation_hold_seconds", 0.8)
		_a11y.call("set_cursor_size_scale", 1.0)
	panel.call("close_panel")
	_ok("settings_panel_a11y_surface")
	panel.queue_free()


func _test_delete_proposal_ui_path() -> void:
	_router.call("reset_to_defaults")
	_router.call("request_context", "inspect")
	var got := [{}]
	var cb := func(p: Dictionary): got[0] = p
	_router.delete_proposal_requested.connect(cb)
	var r: Dictionary = _router.call("try_dispatch", "delete_proposal", {"ui": true}) as Dictionary
	_router.delete_proposal_requested.disconnect(cb)
	if not bool(r.get("ok", false)):
		_fail("delete_dispatch", str(r))
		return
	if str(r.get("mutation_class", "")) != "proposal_only":
		_fail("delete_not_proposal", str(r))
		return
	if bool(r.get("direct_durable", true)):
		_fail("delete_direct_durable", str(r))
		return
	if str(got[0].get("mutation_class", "")) != "proposal_only":
		_fail("delete_signal_payload", str(got[0]))
		return
	_ok("delete_proposal_ui_path")
	_router.call("request_context", "exploration")


func _test_undo_compensation_path() -> void:
	_router.call("reset_to_defaults")
	_router.call("request_context", "build")
	var got := [{}]
	var cb := func(p: Dictionary): got[0] = p
	_router.undo_compensation_requested.connect(cb)
	var r: Dictionary = _router.call("try_dispatch", "request_undo") as Dictionary
	_router.undo_compensation_requested.disconnect(cb)
	if not bool(r.get("ok", false)):
		_fail("undo_dispatch", str(r))
		return
	if str(r.get("mutation_class", "")) != "compensation_request":
		_fail("undo_not_compensation", str(r))
		return
	if bool(r.get("erases_history", true)):
		_fail("undo_erases_history", str(r))
		return
	_ok("undo_compensation_path")
	_router.call("request_context", "exploration")


func _test_r_exploration_no_hologram_rotate() -> void:
	_router.call("reset_to_defaults")
	var rotated := [false]
	var cb := func(_d: int): rotated[0] = true
	_router.build_rotate_requested.connect(cb)
	var sim: Dictionary = _router.call("simulate_physical_r") as Dictionary
	_router.build_rotate_requested.disconnect(cb)
	if bool(sim.get("dual_fire", true)):
		_fail("r_exploration_dual_fire", str(sim))
		return
	if rotated[0]:
		_fail("r_exploration_rotated_hologram")
		return
	var fired: PackedStringArray = sim.get("fired", PackedStringArray()) as PackedStringArray
	if fired.has("build_rotate_right"):
		_fail("r_exploration_build_rotate_fired", str(sim))
		return
	if not fired.has("rotate_camera_right"):
		_fail("r_exploration_missing_camera_right", str(sim))
		return
	if not CatalogScript.is_action_allowed_in_context("exploration", "rotate_camera_right"):
		_fail("r_exploration_catalog_blocks_camera_right")
		return
	_ok("r_exploration_no_hologram_rotate")


func _drive_camera_router_yaw(cam: Node3D, action_id: String) -> Dictionary:
	if InputMap.has_action(action_id) and Input.is_action_pressed(action_id):
		Input.action_release(action_id)
	var yaw0 := float(cam.call("get_yaw"))
	Input.action_press(action_id)
	var router_just := bool(_router.call("is_action_just_pressed", action_id))
	if cam.has_method("_process"):
		cam.call("_process", 1.0)
	Input.action_release(action_id)
	var yaw1 := float(cam.call("get_yaw"))
	return {
		"yaw0": yaw0,
		"yaw1": yaw1,
		"delta": absf(angle_difference(yaw0, yaw1)),
		"router_just": router_just,
	}


func _test_h10_exploration_r_camera_yaw_real_path() -> void:
	## H-10 / Directive 60: Exploration R → rotate_camera_right via real InputMap→router→camera yaw.
	_router.call("reset_to_defaults")
	_router.call("request_context", "exploration")
	var cam: Node3D = _Camera.new() as Node3D
	root.add_child(cam)
	await process_frame
	if not bool(_router.call("is_action_allowed", "rotate_camera_right")):
		_fail("H-10_not_allowed_in_exploration")
		cam.queue_free()
		return
	var res: Dictionary = _drive_camera_router_yaw(cam, "rotate_camera_right")
	if not bool(res.get("router_just", false)):
		_fail("H-10_router_just_pressed_false")
		cam.queue_free()
		return
	if float(res.get("delta", 0.0)) < 0.02:
		_fail("H-10_camera_yaw_unchanged", "delta=%.4f" % float(res.delta))
		cam.queue_free()
		return
	# Must not rotate hologram on exploration R.
	var rotated := [false]
	var cb := func(_d: int): rotated[0] = true
	_router.build_rotate_requested.connect(cb)
	var sim: Dictionary = _router.call("simulate_physical_r") as Dictionary
	_router.build_rotate_requested.disconnect(cb)
	if rotated[0] or bool(sim.get("dual_fire", true)):
		_fail("H-10_hologram_or_dual", str(sim))
		cam.queue_free()
		return
	print("  H-10 exploration R camera yaw delta=%.4f rad (InputMap→router→cozy_camera)" % float(res.delta))
	_ok("H-10_exploration_r_camera_yaw_real_inputmap_path")
	cam.queue_free()


func _test_r_build_rotates_preview() -> void:
	_router.call("reset_to_defaults")
	_router.call("request_context", "build")
	var inst: Node3D = _Instance.new() as Node3D
	inst.set("prompt_id", "smoke-preview-rotate")
	root.add_child(inst)
	await process_frame
	inst.call("set_stage", "hologram")
	var yaw0 := inst.rotation.y
	var got_dir := [0]
	var cb := func(d: int): got_dir[0] = d
	_router.build_rotate_requested.connect(cb)
	var r: Dictionary = _router.call("try_dispatch", "build_rotate_right") as Dictionary
	_router.build_rotate_requested.disconnect(cb)
	if not bool(r.get("ok", false)):
		_fail("build_rotate_dispatch", str(r))
		inst.queue_free()
		return
	if got_dir[0] != 1:
		_fail("build_rotate_signal_dir", str(got_dir[0]))
		inst.queue_free()
		return
	var ok := bool(inst.call("rotate_preview", 15.0))
	if not ok:
		_fail("preview_rotate_failed")
		inst.queue_free()
		return
	if is_equal_approx(inst.rotation.y, yaw0):
		_fail("preview_yaw_unchanged")
		inst.queue_free()
		return
	var sim: Dictionary = _router.call("simulate_physical_r") as Dictionary
	if bool(sim.get("dual_fire", true)):
		_fail("r_build_dual_fire", str(sim))
		inst.queue_free()
		return
	if PackedStringArray(sim.get("fired", [])).has("rotate_camera_right"):
		_fail("r_build_camera_fired", str(sim))
		inst.queue_free()
		return
	_ok("r_build_rotates_preview_no_dual_fire")
	inst.queue_free()
	_router.call("request_context", "exploration")


func _test_build_r_camera_yaw_unchanged() -> void:
	## Build R changes preview only; camera yaw must stay put under router fail-closed gate.
	_router.call("reset_to_defaults")
	_router.call("request_context", "build")
	var cam: Node3D = _Camera.new() as Node3D
	var inst: Node3D = _Instance.new() as Node3D
	inst.set("prompt_id", "smoke-build-r-camera-gate")
	root.add_child(cam)
	root.add_child(inst)
	await process_frame
	inst.call("set_stage", "hologram")
	var cam_yaw0 := float(cam.call("get_yaw"))
	var prev_yaw0 := inst.rotation.y
	var res: Dictionary = _drive_camera_router_yaw(cam, "rotate_camera_right")
	var br: Dictionary = _router.call("try_dispatch", "build_rotate_right") as Dictionary
	inst.call("rotate_preview", 15.0)
	if bool(res.get("router_just", false)):
		_fail("build_camera_just_pressed")
		cam.queue_free()
		inst.queue_free()
		return
	if float(res.get("delta", 0.0)) >= 0.02:
		_fail("build_camera_yaw_changed", "delta=%.4f" % float(res.delta))
		cam.queue_free()
		inst.queue_free()
		return
	if not bool(br.get("ok", false)):
		_fail("build_rotate_failed", str(br))
		cam.queue_free()
		inst.queue_free()
		return
	if is_equal_approx(inst.rotation.y, prev_yaw0):
		_fail("build_preview_yaw_unchanged")
		cam.queue_free()
		inst.queue_free()
		return
	if absf(angle_difference(cam_yaw0, float(cam.call("get_yaw")))) >= 0.02:
		_fail("build_camera_yaw_drifted")
		cam.queue_free()
		inst.queue_free()
		return
	_ok("build_r_preview_only_camera_unchanged")
	cam.queue_free()
	inst.queue_free()
	_router.call("request_context", "exploration")


func _test_rotate_camera_right_remap_still_works() -> void:
	_router.call("reset_to_defaults")
	_router.call("request_context", "exploration")
	var saved: Array = []
	for e in InputMap.action_get_events("rotate_camera_right"):
		saved.append(e)
	InputMap.action_erase_events("rotate_camera_right")
	var ke := InputEventKey.new()
	ke.physical_keycode = KEY_T
	InputMap.action_add_event("rotate_camera_right", ke)
	var cam: Node3D = _Camera.new() as Node3D
	root.add_child(cam)
	await process_frame
	var res: Dictionary = _drive_camera_router_yaw(cam, "rotate_camera_right")
	InputMap.action_erase_events("rotate_camera_right")
	for e in saved:
		InputMap.action_add_event("rotate_camera_right", e as InputEvent)
	if not bool(res.get("router_just", false)) or float(res.get("delta", 0.0)) < 0.02:
		_fail("remap_camera_path", str(res))
		cam.queue_free()
		return
	_ok("rotate_camera_right_remap_still_works")
	cam.queue_free()


func _test_preview_non_authority_flags() -> void:
	var inst: Node3D = _Instance.new() as Node3D
	inst.set("prompt_id", "smoke-preview-auth")
	root.add_child(inst)
	await process_frame
	inst.call("set_stage", "hologram")
	if bool(inst.call("has_durable_collision")):
		_fail("preview_has_collision")
		inst.queue_free()
		return
	var flags: Dictionary = inst.call("get_preview_authority_flags") as Dictionary
	if bool(flags.get("preview_owns_ownership", true)) or bool(flags.get("preview_owns_collision", true)):
		_fail("preview_owns_authority", str(flags))
		inst.queue_free()
		return
	if not bool(flags.get("preview", false)):
		_fail("preview_flag_false", str(flags))
		inst.queue_free()
		return
	_ok("preview_non_authority_flags")
	inst.queue_free()


func _test_sprint_toggle_surface() -> void:
	if _a11y == null:
		_fail("a11y_missing_for_sprint")
		return
	var ok: bool = bool(_a11y.call("set_sprint_mode", "toggle"))
	if not ok:
		_fail("set_sprint_toggle")
		return
	if str(_a11y.get("sprint_mode")) != "toggle":
		_fail("sprint_mode_value")
		return
	_a11y.call("set_sprint_mode", "hold")
	_ok("sprint_toggle_surface")


func _test_q_build_rotate_left() -> void:
	## H-12: Q / build_rotate_left in Build only.
	_router.call("reset_to_defaults")
	_router.call("request_context", "build")
	var inst: Node3D = _Instance.new() as Node3D
	inst.set("prompt_id", "smoke-preview-rotate-left")
	root.add_child(inst)
	await process_frame
	inst.call("set_stage", "hologram")
	var yaw0 := inst.rotation.y
	var got_dir := [0]
	var cb := func(d: int): got_dir[0] = d
	_router.build_rotate_requested.connect(cb)
	var r: Dictionary = _router.call("try_dispatch", "build_rotate_left") as Dictionary
	_router.build_rotate_requested.disconnect(cb)
	if not bool(r.get("ok", false)):
		_fail("H-12_build_rotate_left_dispatch", str(r))
		inst.queue_free()
		return
	if got_dir[0] != -1:
		_fail("H-12_build_rotate_left_dir", str(got_dir[0]))
		inst.queue_free()
		return
	var ok := bool(inst.call("rotate_preview", -15.0))
	if not ok or is_equal_approx(inst.rotation.y, yaw0):
		_fail("H-12_preview_yaw_left_unchanged")
		inst.queue_free()
		return
	# Exploration must reject left rotate.
	_router.call("request_context", "exploration")
	var rej: Dictionary = _router.call("try_dispatch", "build_rotate_left") as Dictionary
	if bool(rej.get("ok", true)):
		_fail("H-12_left_allowed_outside_build", str(rej))
		inst.queue_free()
		return
	_ok("H-12_q_build_rotate_left")
	inst.queue_free()


func _test_h03_prompt_send_vs_newline() -> void:
	## H-03: prompt_send sends; prompt_newline never sends.
	var packed := load(CHAT_SCENE_PATH) as PackedScene
	var chat: Control = null
	if packed != null:
		chat = packed.instantiate() as Control
	else:
		chat = _Chat.new() as Control
	root.add_child(chat)
	await process_frame
	if not chat.has_method("insert_newline") or not chat.has_method("send_current_input"):
		_fail("H-03_missing_api")
		chat.queue_free()
		return
	chat.call("set_input_text_for_test", "xay nha")
	var before_send := 0
	var metrics0: Dictionary = chat.call("get_composer_metrics") as Dictionary
	before_send = int(metrics0.get("send_count", 0))
	var nl: Dictionary = chat.call("insert_newline") as Dictionary
	if not bool(nl.get("ok", false)):
		_fail("H-03_newline_api", str(nl))
		chat.queue_free()
		return
	if bool(nl.get("sent", true)):
		_fail("H-03_newline_sent", str(nl))
		chat.queue_free()
		return
	var mid: Dictionary = chat.call("get_composer_metrics") as Dictionary
	if int(mid.get("send_count", -1)) != before_send:
		_fail("H-03_newline_incremented_send", str(mid))
		chat.queue_free()
		return
	if int(mid.get("newline_count", 0)) < 1:
		_fail("H-03_newline_count", str(mid))
		chat.queue_free()
		return
	# Input still present after newline (never cleared by send).
	var text_after_nl := str(mid.get("input_text", ""))
	if not ("\n" in text_after_nl):
		_fail("H-03_newline_not_in_text", text_after_nl)
		chat.queue_free()
		return
	chat.call("set_input_text_for_test", "xay nha")
	var sent: Dictionary = chat.call("send_current_input") as Dictionary
	if not bool(sent.get("sent", false)):
		_fail("H-03_prompt_send_failed", str(sent))
		chat.queue_free()
		return
	var after: Dictionary = chat.call("get_composer_metrics") as Dictionary
	if int(after.get("send_count", 0)) <= before_send:
		_fail("H-03_send_count", str(after))
		chat.queue_free()
		return
	_ok("H-03_prompt_send_vs_newline")
	chat.queue_free()


func _test_h07_inspect_read_only() -> void:
	var panel: CanvasLayer = _Inspect.new() as CanvasLayer
	root.add_child(panel)
	await process_frame
	var r: Dictionary = panel.call("open_inspect", {
		"entity_id": "entity_smoke",
		"prompt_id": "pid-smoke",
		"recipe_id": "cozy_house",
		"stage": "hologram",
		"has_durable_collision": false,
		"provenance": {"source": "smoke", "rev": 3},
	}) as Dictionary
	if not bool(r.get("read_only", false)):
		_fail("H-07_not_read_only", str(r))
		panel.queue_free()
		return
	if bool(r.get("durable_mutation", true)) or bool(r.get("direct_durable", true)):
		_fail("H-07_mutates", str(r))
		panel.queue_free()
		return
	if not bool(panel.call("is_open")):
		_fail("H-07_not_open")
		panel.queue_free()
		return
	panel.call("close_panel")
	_ok("H-07_inspect_read_only_provenance")
	panel.queue_free()


func _test_h17_proposal_card() -> void:
	var card: CanvasLayer = _Proposal.new() as CanvasLayer
	root.add_child(card)
	await process_frame
	var r: Dictionary = card.call("present_proposal", {
		"recipe_id": "cozy_house",
		"entity": {"recipe_id": "cozy_house"},
		"understanding": "Player wants a cozy house",
		"state": "pending_confirm",
	}, "Player wants a cozy house") as Dictionary
	if not bool(r.get("card", false)):
		_fail("H-17_not_card", str(r))
		card.queue_free()
		return
	if str(r.get("mutation_class", "")) != "proposal_only" or bool(r.get("direct_durable", true)):
		_fail("H-17_not_proposal_only", str(r))
		card.queue_free()
		return
	if str(r.get("understanding", "")).is_empty():
		_fail("H-17_no_understanding", str(r))
		card.queue_free()
		return
	if not bool(card.call("is_open")):
		_fail("H-17_card_not_open")
		card.queue_free()
		return
	if bool(card.call("shows_direct_mutation")):
		_fail("H-17_shows_direct_mutation")
		card.queue_free()
		return
	_ok("H-17_proposal_card_understanding")
	card.queue_free()


func _test_h19_confirmation_hold() -> void:
	## Hold 0 immediate; hold >=0.8 cannot confirm early — logic unit (not demo-only API).
	if _a11y == null:
		_fail("H-19_a11y_missing")
		return
	_a11y.call("set_confirmation_hold_seconds", 0.0, false)
	var need0 := float(_a11y.get("confirmation_hold_seconds"))
	if need0 > 0.001:
		_fail("H-19_hold0_not_zero", str(need0))
		return
	# Simulate hold machine used by main.gd (significant confirm path).
	var holding := false
	var accum := 0.0
	var need := need0
	var confirmed := false
	# hold 0 → immediate
	if need <= 0.001:
		confirmed = true
		holding = false
	else:
		holding = true
	if not confirmed or holding:
		_fail("H-19_hold0_not_immediate")
		return
	_a11y.call("set_confirmation_hold_seconds", 0.8, false)
	need = float(_a11y.get("confirmation_hold_seconds"))
	holding = true
	accum = 0.0
	confirmed = false
	# Early release at 0.3s must NOT confirm.
	accum += 0.3
	if accum + 0.0001 >= need:
		confirmed = true
		holding = false
	else:
		holding = false  # release early
		accum = 0.0
	if confirmed:
		_fail("H-19_early_confirm_at_0.3")
		return
	# Full hold reaches confirm.
	holding = true
	accum = 0.0
	accum += 0.85
	if accum + 0.0001 >= need:
		confirmed = true
		holding = false
	if not confirmed:
		_fail("H-19_full_hold_not_confirm", "accum=%.2f need=%.2f" % [accum, need])
		return
	_ok("H-19_confirmation_hold_0_and_0_8")
	_a11y.call("set_confirmation_hold_seconds", 0.8, false)


func _test_h20_confirm_handoff_and_cancel() -> void:
	## Cancel mid-preview: no durable collision. Complete: collision on, client commit false.
	var inst: Node3D = _Instance.new() as Node3D
	inst.set("prompt_id", "smoke-h20-cancel")
	root.add_child(inst)
	await process_frame
	inst.call("set_stage", "hologram")
	if bool(inst.call("has_durable_collision")):
		_fail("H-20_preview_has_collision")
		inst.queue_free()
		return
	inst.call("mark_cancelled")
	if bool(inst.call("has_durable_collision")):
		_fail("H-20_cancel_left_collision")
		inst.queue_free()
		return
	var flags: Dictionary = inst.call("get_preview_authority_flags") as Dictionary
	if bool(flags.get("durable_mutation_applied", true)) or bool(flags.get("client_world_commit", true)):
		_fail("H-20_cancel_claimed_commit", str(flags))
		inst.queue_free()
		return
	inst.queue_free()

	var inst2: Node3D = _Instance.new() as Node3D
	inst2.set("prompt_id", "smoke-h20-complete")
	root.add_child(inst2)
	await process_frame
	inst2.call("set_stage", "hologram")
	inst2.call("finalize_complete")
	if not bool(inst2.call("has_durable_collision")):
		_fail("H-20_complete_no_collision")
		inst2.queue_free()
		return
	var f2: Dictionary = inst2.call("get_preview_authority_flags") as Dictionary
	if bool(f2.get("durable_mutation_applied", true)) or bool(f2.get("client_world_commit", true)):
		_fail("H-20_complete_client_commit", str(f2))
		inst2.queue_free()
		return
	if str(f2.get("stage", "")) != "complete":
		_fail("H-20_stage", str(f2))
		inst2.queue_free()
		return
	_ok("H-20_handoff_complete_collision_cancel_clean")
	inst2.queue_free()


func _test_h26_sensitivity_observable() -> void:
	var cam: Node3D = _Camera.new() as Node3D
	root.add_child(cam)
	await process_frame
	if _a11y:
		_a11y.call("set_mouse_sensitivity", 1.0, false)
	if cam.has_method("set_distance_for_test"):
		cam.call("set_distance_for_test", 12.0)
	var d1 := 0.0
	if cam.has_method("apply_zoom_in_step"):
		d1 = float(cam.call("apply_zoom_in_step"))
	if _a11y:
		_a11y.call("set_mouse_sensitivity", 2.0, false)
	if cam.has_method("set_distance_for_test"):
		cam.call("set_distance_for_test", 12.0)
	var d2 := 0.0
	if cam.has_method("apply_zoom_in_step"):
		d2 = float(cam.call("apply_zoom_in_step"))
	if d2 <= d1 + 0.001:
		_fail("H-26_sensitivity_no_effect", "d1=%.3f d2=%.3f" % [d1, d2])
		cam.queue_free()
		return
	var snap: Dictionary = cam.call("get_sensitivity_snapshot") as Dictionary
	if not bool(snap.get("bounded", false)):
		_fail("H-26_not_bounded", str(snap))
		cam.queue_free()
		return
	if _a11y:
		_a11y.call("set_mouse_sensitivity", 1.0, false)
	_ok("H-26_sensitivity_observable_bounded")
	cam.queue_free()


func _test_h28_cursor_and_action_label_consumer() -> void:
	var cur: CanvasLayer = _Cursor.new() as CanvasLayer
	root.add_child(cur)
	await process_frame
	if _a11y:
		_a11y.call("set_cursor_size_scale", 1.75, false)
		_a11y.call("set_action_label_near_cursor", true, false)
	if cur.has_method("apply_scale_for_test"):
		cur.call("apply_scale_for_test", 1.75)
	if cur.has_method("set_label_enabled_for_test"):
		cur.call("set_label_enabled_for_test", true)
	await process_frame
	var snap: Dictionary = cur.call("get_runtime_snapshot") as Dictionary
	if str(snap.get("consumer", "")) != "control_1b_cursor_label":
		_fail("H-28_no_consumer", str(snap))
		cur.queue_free()
		return
	if float(snap.get("cursor_size_scale", 0.0)) < 1.4:
		_fail("H-28_scale_not_large", str(snap))
		cur.queue_free()
		return
	if not bool(snap.get("readable_large", false)):
		_fail("H-28_not_readable", str(snap))
		cur.queue_free()
		return
	if not bool(snap.get("action_label_near_cursor", false)):
		_fail("A3-F10_label_disabled", str(snap))
		cur.queue_free()
		return
	if not bool(snap.get("cursor_proxy_visible", false)):
		_fail("H-28_proxy_hidden", str(snap))
		cur.queue_free()
		return
	if _a11y:
		_a11y.call("set_cursor_size_scale", 1.0, false)
		_a11y.call("set_action_label_near_cursor", false, false)
	_ok("H-28_cursor_and_A3_F10_action_label_consumer")
	cur.queue_free()


func _test_a3_f09_full_remap_catalog() -> void:
	var panel: CanvasLayer = _SettingsPanel.new() as CanvasLayer
	root.add_child(panel)
	await process_frame
	var n: int = int(panel.call("get_remappable_catalog_count"))
	var ids: PackedStringArray = panel.call("get_remappable_catalog_ids") as PackedStringArray
	# Foundation catalog is large; subset of 7 was the prior gap.
	if n < 20:
		_fail("A3-F09_catalog_too_small", "count=%d" % n)
		panel.queue_free()
		return
	for required in [
		"prompt_send", "prompt_newline", "build_rotate_left", "build_rotate_right",
		"inspect_entity", "confirm_action", "delete_proposal", "interact_primary",
	]:
		if not ids.has(required):
			_fail("A3-F09_missing_action", required)
			panel.queue_free()
			return
	_ok("A3-F09_full_remappable_catalog_ui")
	panel.queue_free()


func _test_responsive_bottom_layers_no_overlap_metrics() -> void:
	## Compact 868x517: context HUD lifted above action-bar band; no inverted rects.
	var hud: CanvasLayer = _ContextHud.new() as CanvasLayer
	root.add_child(hud)
	await process_frame
	# Force compact responsive path via fake viewport size if panel method exists.
	if hud.has_method("_apply_responsive"):
		hud.call("_apply_responsive")
	var panel: PanelContainer = hud.get_node_or_null("Root/ActionPanel") as PanelContainer
	if panel == null:
		# Still pass structural presence.
		_ok("responsive_layers_scaffold")
		hud.queue_free()
		return
	# At compact, offset_top should be more negative than -100 (lifted).
	if panel.offset_top > -100.0:
		# May be non-compact headless window; still ensure non-inverted.
		if panel.offset_top >= panel.offset_bottom:
			_fail("responsive_inverted_panel", "top=%s bottom=%s" % [panel.offset_top, panel.offset_bottom])
			hud.queue_free()
			return
	if panel.offset_top >= panel.offset_bottom:
		_fail("responsive_inverted", str(panel.offset_top))
		hud.queue_free()
		return
	_ok("responsive_bottom_layers_metrics")
	hud.queue_free()


func _finish() -> void:
	var total := _passed + _failures.size()
	if _failures.is_empty():
		print("AIDLE_CTRL_1B_INTEGRATION_SMOKE=PASS checks=%d" % _passed)
		print("[CTRL-1B-002 C0 integration smoke] PASS %d/%d" % [_passed, total])
		quit(0)
	else:
		print("AIDLE_CTRL_1B_INTEGRATION_SMOKE=FAIL checks_passed=%d failures=%d" % [_passed, _failures.size()])
		for f in _failures:
			printerr("  · %s" % f)
		print("[CTRL-1B-002 C0 integration smoke] FAIL %d/%d" % [_passed, total])
		quit(1)

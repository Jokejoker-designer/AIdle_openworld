## WO-CTRL-1B-002 B0 — fail-closed context router + catalog + R/Esc/safety smokes.
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/control_1b_context_router_smoke.gd
## Exit 0 + AIDLE_CTRL_1B_ROUTER_SMOKE=PASS. Zero ERROR lines required for QA gate.
extends SceneTree

const CatalogScript = preload("res://scripts/input/control_action_catalog.gd")
const RouterScript = preload("res://autoload/control_context_router.gd")
const CAMERA_PATH := "res://scripts/camera/cozy_camera.gd"

var _failures: PackedStringArray = []
var _passed: int = 0
var _router: Node = null
var _Camera: GDScript


func _initialize() -> void:
	print("[CTRL-1B-002 router smoke] starting…")
	CatalogScript.ensure_input_map_actions()
	_Camera = load(CAMERA_PATH) as GDScript
	_router = _resolve_router()
	if _router == null:
		_fail("router_unavailable")
		_finish()
		return
	if _Camera == null:
		_fail("camera_script_load")
		_finish()
		return
	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")

	_test_catalog_cardinality()
	_test_input_map_required_actions()
	_test_exploration_allows_rotate_camera_right()
	_test_unknown_context_rejected()
	_test_context_transitions()
	_test_action_not_allowed_in_context()
	_test_r_no_dual_fire()
	await _test_exploration_r_camera_yaw_real_inputmap_path()
	await _test_build_r_preview_only_camera_unchanged()
	await _test_rotate_camera_right_remap_still_works()
	_test_esc_priority()
	_test_delete_proposal_only()
	_test_undo_compensation_only()
	_test_hud_max_four()
	_test_jump_vs_ui_accept_preserved()
	_test_wasd_and_arrows_present()
	_finish()


func _resolve_router() -> Node:
	# Prefer project autoload when present (relative to SceneTree root — no absolute /root paths).
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


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _test_catalog_cardinality() -> void:
	var v: Dictionary = CatalogScript.validate_catalog_cardinality()
	if not bool(v.get("ok", false)):
		_fail("catalog_cardinality", str(v))
		return
	if int(v.get("context_count", 0)) != 5:
		_fail("catalog_context_count", str(v.get("context_count", 0)))
		return
	for c in CatalogScript.CONTEXTS:
		if not CatalogScript.is_known_context(c):
			_fail("known_context", c)
			return
	_ok("catalog_cardinality_five_contexts")


func _test_input_map_required_actions() -> void:
	var required := [
		"move_forward", "move_back", "move_left", "move_right",
		"sprint", "jump", "pause_menu", "rotate_camera_left", "rotate_camera_right",
		"interact_primary", "interact_secondary", "companion_call", "prompt_quick_open",
		"prompt_send", "prompt_newline", "build_mode_toggle", "world_ability", "world_panel",
		"inspect_entity", "map_open", "camera_reset", "cancel_action", "confirm_action",
		"request_undo", "request_redo", "delete_proposal",
		"build_place", "build_cancel", "build_rotate_left", "build_rotate_right",
		"build_snap_toggle", "cozy_helper_pulse", "cozy_homestead_panel",
	]
	var missing: PackedStringArray = []
	for a in required:
		if not InputMap.has_action(a):
			missing.append(a)
	if not missing.is_empty():
		_fail("inputmap_missing_actions", ",".join(missing))
		return
	_ok("inputmap_required_actions")


func _test_unknown_context_rejected() -> void:
	var before: String = str(_router.call("get_primary_context"))
	var r: Dictionary = _router.call("request_context", "not_a_real_context") as Dictionary
	var after: String = str(_router.call("get_primary_context"))
	if bool(r.get("ok", true)):
		_fail("unknown_context_accepted")
		return
	if after != before:
		_fail("unknown_context_mutated_state", "%s→%s" % [before, after])
		return
	if not bool(r.get("unchanged", false)):
		_fail("unknown_context_missing_unchanged_flag")
		return
	_ok("unknown_context_rejected_state_unchanged")


func _test_context_transitions() -> void:
	_router.call("reset_to_defaults")
	var r1: Dictionary = _router.call("request_context", "build") as Dictionary
	if not bool(r1.get("ok", false)) or str(_router.call("get_primary_context")) != "build":
		_fail("enter_build", str(r1))
		return
	var r2: Dictionary = _router.call("try_dispatch", "build_mode_toggle") as Dictionary
	if not bool(r2.get("ok", false)):
		_fail("toggle_build", str(r2))
		return
	if str(_router.call("get_primary_context")) != "exploration":
		_fail("exit_build_not_exploration", str(_router.call("get_primary_context")))
		return
	var r3: Dictionary = _router.call("try_dispatch", "companion_call") as Dictionary
	if not bool(r3.get("ok", false)) or str(_router.call("get_primary_context")) != "companion":
		_fail("enter_companion", str(r3))
		return
	var r4: Dictionary = _router.call("request_context", "inspect") as Dictionary
	if not bool(r4.get("ok", false)):
		_fail("enter_inspect", str(r4))
		return
	var r5: Dictionary = _router.call("request_context", "world_tool") as Dictionary
	if not bool(r5.get("ok", false)):
		_fail("enter_world_tool", str(r5))
		return
	_ok("context_transitions")


func _test_action_not_allowed_in_context() -> void:
	_router.call("reset_to_defaults")
	_router.call("request_context", "companion")
	# Locomotion suppressed / not allowed in companion.
	var r: Dictionary = _router.call("try_dispatch", "move_forward") as Dictionary
	if bool(r.get("ok", true)):
		_fail("companion_allowed_move_forward")
		return
	if not _router.call("is_action_allowed", "prompt_send"):
		_fail("companion_should_allow_prompt_send")
		return
	_ok("action_gated_by_context")


func _test_exploration_allows_rotate_camera_right() -> void:
	## Directive 60: Exploration closed allow-list must include rotate_camera_right.
	var allowed: PackedStringArray = CatalogScript.get_context_allowed_actions("exploration")
	if not ("rotate_camera_right" in allowed):
		_fail("exploration_allowlist_missing_rotate_camera_right", str(allowed))
		return
	if not ("rotate_camera_left" in allowed):
		_fail("exploration_allowlist_missing_rotate_camera_left", str(allowed))
		return
	_router.call("reset_to_defaults")
	if not bool(_router.call("is_action_allowed", "rotate_camera_right")):
		_fail("router_exploration_blocks_rotate_camera_right")
		return
	if not InputMap.has_action("rotate_camera_right"):
		_fail("inputmap_missing_rotate_camera_right")
		return
	var has_r := false
	for e in InputMap.action_get_events("rotate_camera_right"):
		if e is InputEventKey and int((e as InputEventKey).physical_keycode) == KEY_R:
			has_r = true
			break
	if not has_r:
		_fail("inputmap_rotate_camera_right_missing_physical_R")
		return
	_ok("exploration_allows_rotate_camera_right")


func _test_r_no_dual_fire() -> void:
	_router.call("reset_to_defaults")
	# Exploration: R fires camera right only; never build rotate; no dual-fire.
	var exp_probe: Dictionary = _router.call("simulate_physical_r") as Dictionary
	if bool(exp_probe.get("dual_fire", true)):
		_fail("exploration_r_dual_fire", str(exp_probe))
		return
	var exp_fired: PackedStringArray = PackedStringArray(exp_probe.get("fired", []))
	if "build_rotate_right" in exp_fired:
		_fail("exploration_r_build_rotate", str(exp_fired))
		return
	if not ("rotate_camera_right" in exp_fired):
		_fail("exploration_r_missing_camera_right", str(exp_fired))
		return
	# Build: only build_rotate_right.
	_router.call("request_context", "build")
	var build_probe: Dictionary = _router.call("simulate_physical_r") as Dictionary
	if bool(build_probe.get("dual_fire", true)):
		_fail("build_r_dual_fire", str(build_probe))
		return
	var build_fired: PackedStringArray = PackedStringArray(build_probe.get("fired", []))
	if not ("build_rotate_right" in build_fired):
		_fail("build_r_missing_rotate", str(build_fired))
		return
	if "rotate_camera_right" in build_fired:
		_fail("build_r_camera_dual", str(build_fired))
		return
	# Direct reject camera rotate in build.
	var cam: Dictionary = _router.call("try_dispatch", "rotate_camera_right") as Dictionary
	if bool(cam.get("ok", true)):
		_fail("build_camera_rotate_accepted")
		return
	_ok("r_no_multi_context_dual_fire")


func _release_action(action_id: String) -> void:
	if InputMap.has_action(action_id) and Input.is_action_pressed(action_id):
		Input.action_release(action_id)


func _drive_camera_router_yaw(cam: Node3D, action_id: String) -> Dictionary:
	## Same-frame InputMap press + CozyCamera._process so is_action_just_pressed is observed.
	## This is the real runtime path (router-gated), not try_dispatch.
	_release_action(action_id)
	var yaw0 := float(cam.call("get_yaw"))
	Input.action_press(action_id)
	var router_just := bool(_router.call("is_action_just_pressed", action_id))
	# Drive the camera process path directly while the just-pressed flag is live.
	if cam.has_method("_process"):
		cam.call("_process", 1.0)
	Input.action_release(action_id)
	var yaw1 := float(cam.call("get_yaw"))
	return {
		"yaw0": yaw0,
		"yaw1": yaw1,
		"delta": absf(angle_difference(yaw0, yaw1)),
		"router_just": router_just,
		"allowed": bool(_router.call("is_action_allowed", action_id)),
	}


func _test_exploration_r_camera_yaw_real_inputmap_path() -> void:
	## Real path: InputMap action → ControlContextRouter.is_action_just_pressed → CozyCamera yaw.
	## Must NOT rely only on try_dispatch.
	_router.call("reset_to_defaults")
	_router.call("request_context", "exploration")
	var cam: Node3D = _Camera.new() as Node3D
	root.add_child(cam)
	await process_frame
	if not bool(_router.call("is_action_allowed", "rotate_camera_right")):
		_fail("real_path_not_allowed", "exploration blocks rotate_camera_right")
		cam.queue_free()
		return
	var res: Dictionary = _drive_camera_router_yaw(cam, "rotate_camera_right")
	if not bool(res.get("router_just", false)):
		_fail("real_path_router_just_pressed_false", "is_action_just_pressed failed after Input.action_press")
		cam.queue_free()
		return
	if float(res.get("delta", 0.0)) < 0.02:
		_fail(
			"real_path_camera_yaw_unchanged",
			"yaw0=%.4f yaw1=%.4f delta=%.4f" % [float(res.yaw0), float(res.yaw1), float(res.delta)]
		)
		cam.queue_free()
		return
	print("  real_path exploration R camera yaw delta=%.4f rad (router-gated InputMap)" % float(res.delta))
	_ok("exploration_r_camera_yaw_real_inputmap_router_path")
	cam.queue_free()


func _test_build_r_preview_only_camera_unchanged() -> void:
	## Build R: build_rotate_right only; camera yaw must not change via router gate.
	_router.call("reset_to_defaults")
	_router.call("request_context", "build")
	_release_action("rotate_camera_right")
	_release_action("build_rotate_right")
	var cam: Node3D = _Camera.new() as Node3D
	root.add_child(cam)
	await process_frame
	var yaw0 := float(cam.call("get_yaw"))
	var got_dir := [0]
	var cb := func(d: int): got_dir[0] = d
	_router.build_rotate_requested.connect(cb)
	# Physical-R dual probe + direct build dispatch.
	var sim: Dictionary = _router.call("simulate_physical_r") as Dictionary
	var br: Dictionary = _router.call("try_dispatch", "build_rotate_right") as Dictionary
	# Press camera action — must fail closed in build (no yaw).
	var cam_res: Dictionary = _drive_camera_router_yaw(cam, "rotate_camera_right")
	_router.build_rotate_requested.disconnect(cb)
	var yaw1 := float(cam.call("get_yaw"))
	var delta := absf(angle_difference(yaw0, yaw1))
	if bool(sim.get("dual_fire", true)):
		_fail("build_r_dual_fire_real", str(sim))
		cam.queue_free()
		return
	if bool(cam_res.get("router_just", false)):
		_fail("build_router_camera_just_pressed", "rotate_camera_right must fail closed in build")
		cam.queue_free()
		return
	if not bool(br.get("ok", false)):
		_fail("build_rotate_right_dispatch", str(br))
		cam.queue_free()
		return
	if got_dir[0] != 1 and not (PackedStringArray(sim.get("fired", [])).has("build_rotate_right")):
		_fail("build_r_no_preview_signal", "dir=%s sim=%s" % [got_dir[0], str(sim)])
		cam.queue_free()
		return
	if delta >= 0.02 or float(cam_res.get("delta", 0.0)) >= 0.02:
		_fail("build_r_camera_yaw_changed", "yaw0=%.4f yaw1=%.4f delta=%.4f" % [yaw0, yaw1, delta])
		cam.queue_free()
		return
	_ok("build_r_preview_only_camera_unchanged")
	cam.queue_free()
	_router.call("request_context", "exploration")


func _test_rotate_camera_right_remap_still_works() -> void:
	## Remap logical rotate_camera_right off R onto T; InputMap→router→camera path still yaws.
	_router.call("reset_to_defaults")
	_router.call("request_context", "exploration")
	_release_action("rotate_camera_right")
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
	# Logical action still drives camera after physical rebinding (no hard-coded R).
	var res: Dictionary = _drive_camera_router_yaw(cam, "rotate_camera_right")
	# Restore original bindings.
	InputMap.action_erase_events("rotate_camera_right")
	for e in saved:
		InputMap.action_add_event("rotate_camera_right", e as InputEvent)
	if not bool(res.get("router_just", false)):
		_fail("remap_router_just_pressed_false")
		cam.queue_free()
		return
	if float(res.get("delta", 0.0)) < 0.02:
		_fail(
			"remap_camera_yaw_unchanged",
			"yaw0=%.4f yaw1=%.4f delta=%.4f" % [float(res.yaw0), float(res.yaw1), float(res.delta)]
		)
		cam.queue_free()
		return
	print("  remap rotate_camera_right→T camera yaw delta=%.4f rad" % float(res.delta))
	_ok("rotate_camera_right_remap_still_works")
	cam.queue_free()


func _test_esc_priority() -> void:
	_router.call("reset_to_defaults")
	# With preview active, Esc must cancel preview and NOT pause.
	_router.call("set_cancel_target", "preview_hologram", true)
	var r1: Dictionary = _router.call("resolve_escape") as Dictionary
	if str(r1.get("resolved", "")) != "preview_hologram":
		_fail("esc_preview_not_first", str(r1))
		return
	if bool(r1.get("pause", true)):
		_fail("esc_preview_opened_pause", str(r1))
		return
	# Composer before pause.
	_router.call("set_cancel_target", "prompt_composer_or_dialogue", true)
	var r2: Dictionary = _router.call("resolve_escape") as Dictionary
	if str(r2.get("resolved", "")) != "prompt_composer_or_dialogue":
		_fail("esc_composer", str(r2))
		return
	if bool(r2.get("pause", true)):
		_fail("esc_composer_pause")
		return
	# No cancel targets → pause.
	for k in ["pending_confirmation", "preview_hologram", "prompt_composer_or_dialogue", "inspect_panel", "world_tool_panel"]:
		_router.call("set_cancel_target", k, false)
	_router.call("request_context", "exploration")
	var r3: Dictionary = _router.call("resolve_escape") as Dictionary
	if str(r3.get("resolved", "")) != "pause_menu":
		_fail("esc_idle_not_pause", str(r3))
		return
	if not bool(r3.get("pause", false)):
		_fail("esc_idle_pause_flag")
		return
	# Pending confirmation beats preview.
	_router.call("set_cancel_target", "pending_confirmation", true)
	_router.call("set_cancel_target", "preview_hologram", true)
	var r4: Dictionary = _router.call("resolve_escape") as Dictionary
	if str(r4.get("resolved", "")) != "pending_confirmation":
		_fail("esc_confirm_priority", str(r4))
		return
	_ok("esc_cancel_before_pause")


func _test_delete_proposal_only() -> void:
	_router.call("reset_to_defaults")
	_router.call("request_context", "build")
	var saw := {"hit": false, "payload": {}}
	var cb := func(payload: Dictionary) -> void:
		saw["hit"] = true
		saw["payload"] = payload
	_router.connect("delete_proposal_requested", cb)
	var r: Dictionary = _router.call("try_dispatch", "delete_proposal") as Dictionary
	_router.disconnect("delete_proposal_requested", cb)
	if not bool(r.get("ok", false)):
		_fail("delete_dispatch", str(r))
		return
	if str(r.get("mutation_class", "")) != "proposal_only":
		_fail("delete_not_proposal_class", str(r))
		return
	if bool(r.get("direct_durable", true)):
		_fail("delete_direct_durable_true")
		return
	if not bool(saw["hit"]):
		_fail("delete_signal_not_emitted")
		return
	var p: Dictionary = saw["payload"] as Dictionary
	if bool(p.get("direct_durable", true)):
		_fail("delete_payload_durable")
		return
	if CatalogScript.get_safety_class("delete_proposal") != CatalogScript.SAFETY_PROPOSAL_ONLY:
		_fail("delete_catalog_safety")
		return
	_ok("delete_proposal_only")


func _test_undo_compensation_only() -> void:
	_router.call("reset_to_defaults")
	_router.call("request_context", "build")
	var saw := {"hit": false, "payload": {}}
	var cb := func(payload: Dictionary) -> void:
		saw["hit"] = true
		saw["payload"] = payload
	_router.connect("undo_compensation_requested", cb)
	var r: Dictionary = _router.call("try_dispatch", "request_undo") as Dictionary
	_router.disconnect("undo_compensation_requested", cb)
	if not bool(r.get("ok", false)):
		_fail("undo_dispatch", str(r))
		return
	if str(r.get("mutation_class", "")) != "compensation_request":
		_fail("undo_class", str(r))
		return
	if bool(r.get("erases_history", true)):
		_fail("undo_erases_history")
		return
	if not bool(saw["hit"]):
		_fail("undo_signal_missing")
		return
	_ok("request_undo_compensation_only")


func _test_hud_max_four() -> void:
	for c in CatalogScript.CONTEXTS:
		_router.call("request_context", c)
		var hud: PackedStringArray = _router.call("get_hud_actions") as PackedStringArray
		if hud.size() > 4:
			_fail("hud_exceeds_four", "%s size=%d" % [c, hud.size()])
			return
		if hud.is_empty():
			_fail("hud_empty", c)
			return
	_ok("hud_max_four_all_contexts")


func _test_jump_vs_ui_accept_preserved() -> void:
	if not InputMap.has_action("jump"):
		_fail("jump_missing")
		return
	var has_space := false
	for e in InputMap.action_get_events("jump"):
		if e is InputEventKey and int((e as InputEventKey).physical_keycode) == KEY_SPACE:
			has_space = true
			break
	if not has_space:
		_fail("jump_not_space")
		return
	# Player script must still use jump not ui_accept.
	var f := FileAccess.open("res://scripts/player/player_controller.gd", FileAccess.READ)
	if f == null:
		_fail("player_script_open")
		return
	var src := f.get_as_text()
	f.close()
	if src.find('is_action_just_pressed("ui_accept")') >= 0:
		_fail("player_uses_ui_accept_for_jump")
		return
	if src.find('is_action_just_pressed("jump")') < 0:
		_fail("player_missing_jump")
		return
	_ok("jump_vs_ui_accept_preserved")


func _test_wasd_and_arrows_present() -> void:
	for a in ["move_forward", "move_back", "move_left", "move_right"]:
		if not InputMap.has_action(a):
			_fail("move_missing", a)
			return
		if InputMap.action_get_events(a).is_empty():
			_fail("move_empty", a)
			return
	for ui_action in ["ui_left", "ui_right", "ui_up", "ui_down"]:
		if not InputMap.has_action(ui_action):
			_fail("ui_nav_not_overridden", ui_action)
			return
		for e in InputMap.action_get_events(ui_action):
			if e is InputEventKey:
				var pk := int((e as InputEventKey).physical_keycode)
				if pk == KEY_LEFT or pk == KEY_RIGHT or pk == KEY_UP or pk == KEY_DOWN:
					_fail("ui_still_has_arrow", "%s key=%d" % [ui_action, pk])
					return
	_ok("wasd_arrows_owned_by_move")


func _finish() -> void:
	var autoload_router := root.get_node_or_null("ControlContextRouter")
	if _router != null and _router.get_parent() == root and _router != autoload_router:
		_router.queue_free()
	if _failures.is_empty():
		print("AIDLE_CTRL_1B_ROUTER_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("AIDLE_CTRL_1B_ROUTER_SMOKE=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
		quit(1)

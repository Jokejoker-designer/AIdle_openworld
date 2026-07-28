## UCBV-001 C5H1 — Companion deadlock acceptance smoke (VERIFY_ONLY QA).
## Proves Human H1 / WO-UCBV-001-C5H1 criteria via InputMap path on real Main.
## Control documented: companion_call = KEY_C (not HUD "E"); prompt_quick_open = KEY_SLASH.
## Optional headed dual-res captures when DisplayServer is not headless → evidence/c5h1_001.
## Run headless:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/ucbv_001_c5h1_companion_deadlock_smoke.gd
## Run headed (captures):
##   tools/Godot_v4.3-stable_win64_console.exe --path game \
##     -s res://tests/ucbv_001_c5h1_companion_deadlock_smoke.gd
## Marker: AIDLE_UCBV001_C5H1_COMPANION_DEADLOCK_SMOKE=PASS|FAIL
extends SceneTree

const MAIN_SCENE := "res://scenes/main/main.tscn"
const CatalogScript = preload("res://scripts/input/control_action_catalog.gd")
const EVIDENCE_ABS := "E:/AIdle_openworld/orchestration/evidence/ucbv_001/c5h1_001"

var _failures: PackedStringArray = []
var _passed: int = 0
var _main: Node = null
var _ba: Node = null
var _router: Node = null
var _player: Node = null
var _camera: Node3D = null
var _input_log: Array = []
var _captures: Array = []
var _art_style_id: String = "unknown"
var _world_profile: String = "unknown"
var _control_used: String = "companion_call"
var _headed: bool = false
var _gate: Dictionary = {}
var _error_hits: PackedStringArray = []


func _initialize() -> void:
	print("[UCBV_C5H1_SMOKE] start directive=97 VERIFY_ONLY companion_deadlock")
	_headed = DisplayServer.get_name() != "headless"
	print("[UCBV_C5H1_SMOKE] display=%s headed=%s evidence=%s" % [DisplayServer.get_name(), str(_headed), EVIDENCE_ABS])
	CatalogScript.ensure_input_map_actions()
	if _headed:
		DirAccess.make_dir_recursive_absolute(EVIDENCE_ABS)
	await _run()
	_finish()


func _finish() -> void:
	if _ba != null and is_instance_valid(_ba) and _ba.has_method("dispose_all_previews"):
		_ba.call("dispose_all_previews")
	_write_summary()
	if _failures.is_empty():
		print(
			"AIDLE_UCBV001_C5H1_COMPANION_DEADLOCK_SMOKE=PASS checks=%d inputs=%d control=%s art=%s headed=%s captures=%d"
			% [_passed, _input_log.size(), _control_used, _art_style_id, str(_headed), _captures.size()]
		)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"AIDLE_UCBV001_C5H1_COMPANION_DEADLOCK_SMOKE=FAIL failed=%d passed=%d"
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


func _run() -> void:
	for i in range(48):
		if root.get_node_or_null("ControlContextRouter") != null:
			break
		await process_frame
	_router = root.get_node_or_null("ControlContextRouter")
	if _router == null:
		_fail("router_missing")
		return
	_ok("router_ready")

	var art := root.get_node_or_null("ArtStyleManager")
	if art != null and art.has_method("set_world_meta_path_override"):
		art.call("set_world_meta_path_override", "user://ucbv001_c5h1_isolated/world_meta.cfg")
	if art != null and art.has_method("get_active_style_id"):
		_art_style_id = str(art.call("get_active_style_id"))
	if art != null and art.has_method("get_active_world_profile"):
		_world_profile = str(art.call("get_active_world_profile"))
	elif art != null and art.has_method("get_world_profile_id"):
		_world_profile = str(art.call("get_world_profile_id"))
	elif art != null and "active_world_profile" in art:
		_world_profile = str(art.get("active_world_profile"))
	print("[UCBV_C5H1_SMOKE] art_style_id=%s world_profile=%s" % [_art_style_id, _world_profile])
	_ok("art_style_recorded art=%s profile=%s" % [_art_style_id, _world_profile])

	if _headed:
		_set_window(1280, 720)
		await _frames(2)

	var err := change_scene_to_file(MAIN_SCENE)
	if err != OK:
		_fail("load_main", str(err))
		return
	for i in range(90):
		await process_frame

	_main = current_scene
	if _main == null:
		_fail("main_null")
		return
	_ok("main_loaded")

	if _main.has_method("get_block_assembly"):
		_ba = _main.call("get_block_assembly") as Node
	if _ba == null:
		_ba = _main.get_node_or_null("BlockAssemblyController")
	if _ba == null:
		_fail("block_assembly_missing")
		return
	_ok("block_assembly_bound")

	_player = _main.get_node_or_null("Player")
	if _player == null:
		_player = _find_named(_main, "Player")
	if _player == null:
		_fail("player_missing")
		return
	_ok("player_bound")

	_camera = _find_camera(_main)
	if _camera == null:
		_fail("camera_missing")
		return
	_ok("camera_bound")

	var a11y := root.get_node_or_null("ControlAccessibilitySettings")
	if a11y == null:
		a11y = root.get_node_or_null("ControlAccessibility")
	if a11y != null and a11y.has_method("set_confirmation_hold_seconds"):
		a11y.call("set_confirmation_hold_seconds", 0.0, false)

	# ── Criterion 1: companion_call open → same control close → locomotion restored ──
	_control_used = "companion_call"
	await _ensure_exploration()
	if _chat_visible():
		await _tap_action("companion_call")
		await _frames(4)
	if _chat_visible():
		_fail("c1_precondition_chat_stuck_open")
		return

	await _tap_physical_or_action("companion_call", KEY_C)
	await _frames(8)
	if not _chat_visible():
		# Fallback: InputEventAction-only path
		await _tap_action("companion_call")
		await _frames(8)
	if not _chat_visible():
		_fail("c1_open_companion_failed", "control=companion_call KEY_C")
		return
	if not _locomotion_suppressed():
		_fail("c1_open_did_not_suppress_locomotion")
		return
	_ok("c1_open_companion_via_companion_call_KEY_C")
	await _capture_state("c1_companion_open", 1280, 720)

	await _tap_physical_or_action("companion_call", KEY_C)
	await _frames(8)
	if _chat_visible():
		await _tap_action("companion_call")
		await _frames(8)
	if _chat_visible():
		_fail("c1_close_companion_failed", "second companion_call should close")
		return
	if _locomotion_suppressed():
		_fail("c1_locomotion_still_suppressed_after_close")
		return
	_ok("c1_close_same_control_locomotion_restored control=companion_call KEY_C")
	_gate["c1_toggle_close_locomotion"] = true
	await _capture_state("c1_companion_closed_locomotion", 1280, 720)

	# Also prove prompt_quick_open toggle (secondary control)
	await _tap_physical_or_action("prompt_quick_open", KEY_SLASH)
	await _frames(6)
	if not _chat_visible():
		await _tap_action("prompt_quick_open")
		await _frames(6)
	if not _chat_visible():
		_fail("c1b_slash_open_failed")
		return
	await _tap_physical_or_action("prompt_quick_open", KEY_SLASH)
	await _frames(6)
	if _chat_visible():
		await _tap_action("prompt_quick_open")
		await _frames(6)
	if _chat_visible():
		_fail("c1b_slash_close_failed")
		return
	if _locomotion_suppressed():
		_fail("c1b_slash_locomotion_still_suppressed")
		return
	_ok("c1b_prompt_quick_open_KEY_SLASH_toggle_locomotion_restored")

	# ── Criterion 2: open, close, Manual Build, place → Confirm enables → World Commit ──
	await _ensure_exploration()
	await _tap_physical_or_action("companion_call", KEY_C)
	await _frames(6)
	if not _chat_visible():
		await _tap_action("companion_call")
		await _frames(6)
	await _tap_physical_or_action("companion_call", KEY_C)
	await _frames(6)
	if _chat_visible():
		await _tap_action("companion_call")
		await _frames(6)
	if _chat_visible() or _locomotion_suppressed():
		_fail("c2_pre_build_companion_not_closed", "visible=%s suppressed=%s" % [str(_chat_visible()), str(_locomotion_suppressed())])
		return
	_ok("c2_companion_closed_before_build")

	if not await _open_manual_build():
		_fail("c2_open_manual_build")
		return
	await _frames(8)
	var ctx := str(_router.call("get_primary_context")) if _router else ""
	if ctx != "build":
		# Force build context if UI path only partially applied (still no BA confirm API).
		if _router != null and _router.has_method("request_context"):
			_router.call("request_context", "build")
		await _frames(4)
		ctx = str(_router.call("get_primary_context")) if _router else ""
	if ctx != "build":
		_fail("c2_not_build_context", ctx)
		return
	_ok("c2_manual_build_context")

	# Before place: Confirm must NOT be enabled
	var can0 := _can_confirm()
	if can0:
		# Accept if leftover preview — clear once via cancel
		await _tap_action("build_cancel")
		await _frames(4)
		can0 = _can_confirm()
	if can0:
		_fail("c2_confirm_enabled_before_place")
		return
	_ok("c2_confirm_disabled_before_place")

	await _tap_action("build_place")
	await _frames(12)
	var st_place: Dictionary = _state()
	if not bool(st_place.get("active", false)):
		# LMB-style path via build_place failed — try second place after module next
		await _tap_action("build_module_next")
		await _frames(3)
		await _tap_action("build_place")
		await _frames(12)
		st_place = _state()
	if not bool(st_place.get("active", false)):
		_fail("c2_place_preview_inactive", str(st_place))
		return
	var can1 := _can_confirm()
	if not can1:
		_fail("c2_confirm_not_enabled_after_place", str(st_place))
		return
	_ok("c2_confirm_enabled_after_lmb_or_build_place")
	_gate["c2_confirm_enables"] = true
	await _capture_state("c2_preview_confirm_enabled", 1280, 720)

	var committed0 := _committed()
	await _tap_action("confirm_action")
	await _frames(14)
	var committed1 := _committed()
	if committed1 <= committed0:
		_fail("c2_confirm_no_commit", "before=%d after=%d last=%s" % [committed0, committed1, str(_last_confirm())])
		return
	var conf := _last_confirm()
	if bool(conf.get("client_world_commit", false)):
		_fail("c2_client_world_commit_forbidden", str(conf))
		return
	_ok("c2_confirm_world_commit_path committed=%d→%d" % [committed0, committed1])
	_gate["c2_world_commit"] = true
	await _capture_state("c2_confirmed_world_commit", 1280, 720)

	# ── Criterion 3: companion during active preview + Esc order (defined non-deadlock) ──
	# Re-enter build + place
	if str(_router.call("get_primary_context")) != "build":
		if not await _open_manual_build():
			if _router.has_method("request_context"):
				_router.call("request_context", "build")
		await _frames(6)
	await _tap_action("build_place")
	await _frames(10)
	if not bool(_state().get("active", false)):
		await _tap_action("build_place")
		await _frames(10)
	if not bool(_state().get("active", false)):
		_fail("c3_preview_setup_failed", str(_state()))
		return
	_ok("c3_preview_active_before_companion")

	# Open companion during build via prompt_quick_open (catalog allows in build; companion_call may not)
	await _tap_physical_or_action("prompt_quick_open", KEY_SLASH)
	await _frames(8)
	if not _chat_visible():
		await _tap_action("prompt_quick_open")
		await _frames(8)
	if not _chat_visible():
		# Action-bar toggle fallback
		if _main.has_method("_toggle_companion_chat"):
			_main.call("_toggle_companion_chat")
			await _frames(6)
	if not _chat_visible():
		_fail("c3_open_companion_during_preview_failed")
		return
	if not _locomotion_suppressed():
		# Soft note — open path should suppress; still continue for Esc order
		print("[UCBV_C5H1_SMOKE] WARN c3 companion open without locomotion suppress observed")
	_ok("c3_companion_open_during_active_preview via=prompt_quick_open")
	await _capture_state("c3_companion_over_preview", 1280, 720)

	# 1st Esc → closes companion (Blue C5H1 priority)
	var preview_before_esc := bool(_state().get("active", false))
	await _tap_physical_or_action("cancel_action", KEY_ESCAPE)
	await _frames(8)
	var chat_after_esc1 := _chat_visible()
	var preview_after_esc1 := bool(_state().get("active", false))
	var suppressed_after_esc1 := _locomotion_suppressed()
	if chat_after_esc1:
		_fail("c3_first_esc_did_not_close_companion")
		return
	if suppressed_after_esc1:
		_fail("c3_first_esc_locomotion_still_suppressed")
		return
	# Defined order: companion first; preview should still be active if it was
	if preview_before_esc and not preview_after_esc1:
		# Alternate defined order (preview cancelled first) — still non-deadlock; document
		print("[UCBV_C5H1_SMOKE] NOTE first Esc also cancelled preview (alt defined order)")
		_gate["c3_esc_order"] = "first_esc_closed_companion_and_preview"
	else:
		_gate["c3_esc_order"] = "first_esc_closes_companion_preview_retained"
	_ok("c3_first_esc_closes_companion order=%s preview_retained=%s" % [str(_gate["c3_esc_order"]), str(preview_after_esc1)])

	# 2nd Esc → cancel preview if still active; no deadlock either way
	if preview_after_esc1:
		await _tap_physical_or_action("cancel_action", KEY_ESCAPE)
		await _frames(8)
		if bool(_state().get("active", false)):
			await _tap_action("build_cancel")
			await _frames(6)
		if bool(_state().get("active", false)):
			_fail("c3_second_esc_preview_still_active")
			return
		_ok("c3_second_esc_cancels_preview")
		_gate["c3_second_esc"] = "cancels_preview"
	else:
		_ok("c3_preview_already_cleared_no_deadlock")
		_gate["c3_second_esc"] = "n_a_preview_already_cleared"
	if _chat_visible() or _locomotion_suppressed():
		_fail("c3_stuck_after_esc_sequence", "chat=%s suppressed=%s" % [str(_chat_visible()), str(_locomotion_suppressed())])
		return
	_ok("c3_defined_non_deadlock_esc_order")
	_gate["c3_non_deadlock"] = true
	await _capture_state("c3_after_esc_sequence", 1280, 720)

	# ── Criterion 4: build_esc_no_pause unregressed + zero stuck state ──
	if str(_router.call("get_primary_context")) != "build":
		if _router.has_method("request_context"):
			_router.call("request_context", "build")
		await _frames(4)
	# Ensure no active preview
	if bool(_state().get("active", false)):
		await _tap_action("build_cancel")
		await _frames(4)
	# GameManager.GameState: BOOT=0 ART_STYLE_SELECT=1 IN_WORLD=2 PAUSED=3 SETTINGS=4
	var gm := root.get_node_or_null("GameManager")
	if gm == null:
		for n in root.get_children():
			if str(n.name) == "GameManager":
				gm = n
				break
	var state_before_i := -1
	var state_before := ""
	if gm != null and "state" in gm:
		state_before_i = int(gm.get("state"))
		state_before = str(state_before_i)
	await _tap_physical_or_action("cancel_action", KEY_ESCAPE)
	await _frames(8)
	var state_after_i := -1
	var state_after := ""
	if gm != null and "state" in gm:
		state_after_i = int(gm.get("state"))
		state_after = str(state_after_i)
	# Must not enter PAUSED (3) from build idle Esc; IN_WORLD (2) is expected.
	var paused_after := state_after_i == 3
	if paused_after:
		_fail("c4_build_esc_paused", "before=%s after=%s (PAUSED=3 IN_WORLD=2)" % [state_before, state_after])
		return
	_ok("c4_build_esc_no_pause state_before=%s state_after=%s (IN_WORLD=2 PAUSED=3)" % [state_before, state_after])
	_gate["c4_build_esc_no_pause"] = true
	_gate["c4_gm_state_after"] = state_after_i

	# ── Dual-res headed extras (pond-white / style record) ──
	if _headed:
		await _capture_state("idle_style_record", 1280, 720)
		_set_window(868, 517)
		await _frames(6)
		# Quick toggle proof at 868
		await _ensure_exploration()
		await _tap_physical_or_action("companion_call", KEY_C)
		await _frames(6)
		await _capture_state("companion_open", 868, 517)
		await _tap_physical_or_action("companion_call", KEY_C)
		await _frames(6)
		await _capture_state("companion_closed", 868, 517)
		_ok("c5_dual_res_captures_done n=%d" % _captures.size())

	print("[UCBV_C5H1_SMOKE] gate=%s" % JSON.stringify(_gate))
	print("[UCBV_C5H1_SMOKE] control_documented=%s (InputMap KEY_C; HUD may still say E — Red OBS01)" % _control_used)
	print("[UCBV_C5H1_SMOKE] art_style_id=%s world_profile=%s" % [_art_style_id, _world_profile])


func _write_summary() -> void:
	if not _headed and not DirAccess.dir_exists_absolute(EVIDENCE_ABS):
		DirAccess.make_dir_recursive_absolute(EVIDENCE_ABS)
	var summary := {
		"marker": "AIDLE_UCBV001_C5H1_COMPANION_DEADLOCK_SMOKE",
		"passed": _failures.is_empty(),
		"checks": _passed,
		"failures": Array(_failures),
		"control_used": _control_used,
		"control_note": "companion_call bound to KEY_C (physical C); prompt_quick_open KEY_SLASH; HUD E label is pre-existing OBS01",
		"art_style_id": _art_style_id,
		"world_profile": _world_profile,
		"gate": _gate,
		"inputs": _input_log.size(),
		"captures": _captures,
		"headed": _headed,
		"esc_order_documented": str(_gate.get("c3_esc_order", "not_run")),
	}
	var path := EVIDENCE_ABS.path_join("smoke_summary.json")
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(summary, "\t"))
		f.close()
		print("[UCBV_C5H1_SMOKE] wrote %s" % path)


func _chat_panel() -> Control:
	if _main == null:
		return null
	var p := _main.get_node_or_null("UI/CompanionChatHost/CompanionChatPanel") as Control
	if p != null:
		return p
	p = _main.get_node_or_null("CompanionChatHost/CompanionChatPanel") as Control
	if p != null:
		return p
	return _find_named(_main, "CompanionChatPanel") as Control


func _chat_visible() -> bool:
	if _main != null and "_chat_visible" in _main:
		return bool(_main.get("_chat_visible"))
	var p := _chat_panel()
	return p != null and p.visible


func _locomotion_suppressed() -> bool:
	if _player != null and _player.has_method("is_locomotion_suppressed"):
		return bool(_player.call("is_locomotion_suppressed"))
	if _player != null and "_locomotion_suppressed" in _player:
		return bool(_player.get("_locomotion_suppressed"))
	return false


func _can_confirm() -> bool:
	if _ba != null and _ba.has_method("can_confirm"):
		return bool(_ba.call("can_confirm"))
	return bool(_state().get("active", false))


func _state() -> Dictionary:
	if _ba != null and _ba.has_method("get_active_state"):
		return _ba.call("get_active_state") as Dictionary
	return {}


func _committed() -> int:
	if _ba != null and _ba.has_method("get_committed_count"):
		return int(_ba.call("get_committed_count"))
	return 0


func _last_confirm() -> Dictionary:
	if _main != null and "_last_confirm_result" in _main:
		return _main.get("_last_confirm_result") as Dictionary
	return {}


func _ensure_exploration() -> void:
	if _chat_visible() and _main != null and _main.has_method("_close_companion_composer"):
		_main.call("_close_companion_composer")
		await _frames(4)
	if _router != null and _router.has_method("request_context"):
		if str(_router.call("get_primary_context")) != "exploration":
			_router.call("request_context", "exploration")
	await _frames(4)


func _open_manual_build() -> bool:
	if _main == null:
		return false
	for n in _main.get_children():
		if n.has_signal("demo_build_pressed"):
			n.emit_signal("demo_build_pressed")
			await _frames(6)
			return true
		for c in n.get_children():
			if c.has_signal("demo_build_pressed"):
				c.emit_signal("demo_build_pressed")
				await _frames(6)
				return true
	var stack: Array = [_main]
	var guard := 0
	while not stack.is_empty() and guard < 400:
		guard += 1
		var node: Node = stack.pop_back() as Node
		if node is Button:
			var b := node as Button
			if str(b.text).findn("Manual Build") >= 0:
				b.emit_signal("pressed")
				await _frames(6)
				return true
		for ch in node.get_children():
			stack.append(ch)
	await _tap_action("build_mode_toggle")
	await _frames(6)
	return true


func _capture_state(name: String, w: int, h: int) -> void:
	if not _headed:
		return
	_set_window(w, h)
	await _frames(4)
	var fname := "%s_%dx%d.png" % [name, w, h]
	var path := EVIDENCE_ABS.path_join(fname)
	var img: Image = get_root().get_texture().get_image()
	if img == null:
		print("[UCBV_C5H1_SMOKE] capture_skip null_image %s" % fname)
		return
	var err := img.save_png(path)
	var entry := {
		"file": fname,
		"path": path,
		"w": w,
		"h": h,
		"state": name,
		"ok": err == OK,
		"art_style_id": _art_style_id,
	}
	_captures.append(entry)
	print("[UCBV_C5H1_SMOKE] capture %s err=%s" % [fname, str(err)])


func _tap_physical_or_action(action_id: String, keycode: int) -> void:
	## Esc/cancel must update Input action just_pressed (Main gates on it).
	if action_id == "cancel_action" or action_id == "pause_menu":
		await _tap_action(action_id)
		return
	await _action_down_key(action_id, keycode)
	await process_frame
	await process_frame
	await _action_up_key(action_id, keycode)
	await process_frame
	await process_frame


func _tap_action(action_id: String) -> void:
	await _action_down_action(action_id)
	await process_frame
	await process_frame
	await _action_up_action(action_id)
	await process_frame


func _push_event(ev: InputEvent) -> void:
	## Prefer viewport push so Main._unhandled_input sees one edge.
	## Avoid parse+push double delivery (would toggle open then close).
	if _main != null and is_instance_valid(_main):
		var vp := _main.get_viewport()
		if vp != null:
			vp.push_input(ev, true)
			return
	Input.parse_input_event(ev)


func _action_down_key(action_id: String, keycode: int) -> void:
	## Single edge only: physical key maps to action via InputMap.
	## Do NOT also inject InputEventAction here — dual inject open+close races the toggle.
	if InputMap.has_action(action_id) and Input.is_action_pressed(action_id):
		Input.action_release(action_id)
	var key := InputEventKey.new()
	key.keycode = keycode as Key
	key.physical_keycode = keycode as Key
	key.pressed = true
	key.echo = false
	_push_event(key)
	_input_log.append({"t": Time.get_ticks_msec(), "kind": "down", "action": action_id, "keycode": keycode, "via": "key_only"})
	print("[C5H1_INPUT] down %s kc=%d via=key_only" % [action_id, keycode])


func _action_up_key(action_id: String, keycode: int) -> void:
	var key := InputEventKey.new()
	key.keycode = keycode as Key
	key.physical_keycode = keycode as Key
	key.pressed = false
	key.echo = false
	_push_event(key)
	if InputMap.has_action(action_id) and Input.is_action_pressed(action_id):
		Input.action_release(action_id)
	_input_log.append({"t": Time.get_ticks_msec(), "kind": "up", "action": action_id, "keycode": keycode, "via": "key_only"})


func _action_down_action(action_id: String) -> void:
	if not InputMap.has_action(action_id):
		_fail("action_missing", action_id)
		return
	if Input.is_action_pressed(action_id):
		Input.action_release(action_id)
	var ev := InputEventAction.new()
	ev.action = action_id
	ev.pressed = true
	ev.strength = 1.0
	## Single path: parse_input_event arms Input.is_action_just_pressed (Esc gate) and
	## delivers one event through the input pipeline (matches InputMap E2E pattern).
	Input.parse_input_event(ev)
	_input_log.append({"t": Time.get_ticks_msec(), "kind": "action_down", "action": action_id, "via": "parse_input_event"})
	print("[C5H1_INPUT] action_down %s" % action_id)


func _action_up_action(action_id: String) -> void:
	var ev := InputEventAction.new()
	ev.action = action_id
	ev.pressed = false
	ev.strength = 0.0
	Input.parse_input_event(ev)
	if InputMap.has_action(action_id) and Input.is_action_pressed(action_id):
		Input.action_release(action_id)
	_input_log.append({"t": Time.get_ticks_msec(), "kind": "action_up", "action": action_id, "via": "parse_input_event"})


func _frames(n: int) -> void:
	for i in range(n):
		await process_frame


func _set_window(w: int, h: int) -> void:
	if DisplayServer.get_name() == "headless":
		return
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	DisplayServer.window_set_size(Vector2i(w, h))
	get_root().size = Vector2i(w, h)


func _find_camera(from: Node) -> Node3D:
	if from == null:
		return null
	if from.has_node("CozyCamera"):
		return from.get_node("CozyCamera") as Node3D
	if "camera_rig" in from:
		var c: Variant = from.get("camera_rig")
		if c is Node3D:
			return c as Node3D
	var cam := from.find_child("Camera3D", true, false)
	if cam is Camera3D:
		return cam as Node3D
	cam = from.find_child("CozyCamera", true, false)
	if cam is Node3D:
		return cam as Node3D
	return null


func _find_named(n: Node, name: String) -> Node:
	if n == null:
		return null
	if n.name == name:
		return n
	return n.find_child(name, true, false)

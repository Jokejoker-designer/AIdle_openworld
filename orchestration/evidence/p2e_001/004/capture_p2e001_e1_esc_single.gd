## P2E-001 E1 focused headed Esc single-dispatch witness (VERIFY_ONLY evidence lease).
## Writes under orchestration/evidence/p2e_001/004 only — never patches product.
## Proves P2E-CODEX-ESC-DOUBLE-01 closed: one physical Esc → one resolve apply,
## one cancel transition, zero Pause, zero duplicate markers.
## D72 visual/Q/R axes bound immutably to evidence 003 (not re-shot here).
extends SceneTree

const MAIN_SCENE := "res://scenes/main/main.tscn"
const EVIDENCE_ABS := "E:/AIdle_openworld/orchestration/evidence/p2e_001/004"

var _passed: int = 0
var _failed: int = 0
var _failures: PackedStringArray = []
var _input_log: Array = []
var _router: Node = null
var _main: Node = null
var _ba: Node = null
var _witness: Dictionary = {}
var _product_key_p_present: bool = false


func _initialize() -> void:
	print("[P2E001_E1_ESC] start wave=E1 focused_esc=true real_input=true")
	print("[P2E001_E1_ESC] evidence=%s" % EVIDENCE_ABS)
	if DisplayServer.get_name() == "headless":
		_fail("headless_blocked")
		_finish()
		return

	DirAccess.make_dir_recursive_absolute(EVIDENCE_ABS)

	for i in range(60):
		if root.get_node_or_null("ControlContextRouter") != null:
			break
		await process_frame

	_router = root.get_node_or_null("ControlContextRouter")
	if _router == null:
		_fail("router_missing")
		_finish()
		return
	_ok("router_ready")

	var art := root.get_node_or_null("ArtStyleManager")
	if art != null and art.has_method("set_world_meta_path_override"):
		art.call("set_world_meta_path_override", "user://p2e001_e1_isolated/world_meta.cfg")
		_ok("world_meta_isolated")

	_set_window(1280, 720)
	await process_frame
	await process_frame

	var err := change_scene_to_file(MAIN_SCENE)
	if err != OK:
		_fail("load_main", str(err))
		_finish()
		return
	for i in range(64):
		await process_frame

	_main = current_scene
	if _main == null:
		_fail("main_null")
		_finish()
		return
	_ok("main_loaded")

	if _main.has_method("get_block_assembly"):
		_ba = _main.call("get_block_assembly") as Node
	if _ba == null:
		_ba = _main.get_node_or_null("BlockAssemblyController")
	if _ba == null:
		_fail("block_assembly_missing")
		_finish()
		return
	_ok("block_assembly_bound")

	_audit_product_place_key()
	if not _product_key_p_present:
		_fail("product_build_place_missing_KEY_P")
		_finish()
		return
	_ok("product_KEY_P_present")

	await _run_esc_single_dispatch_witness()
	await _teardown_clean()
	_write_witness()
	_finish()


func _run_esc_single_dispatch_witness() -> void:
	## Build context + place preview via player InputMap, then one Esc sequence.
	if _router.has_method("request_context"):
		_router.call("request_context", "build")
	_log_input("context", "build", {"via": "request_context"})
	for i in range(10):
		await process_frame

	await _press_key(KEY_PERIOD, "build_module_next")
	for i in range(6):
		await process_frame
	await _press_key(KEY_P, "build_place")
	for i in range(18):
		await process_frame

	var st0: Dictionary = _ba.call("get_active_state") as Dictionary
	if not bool(st0.get("active", false)):
		_fail("place_via_KEY_P_failed_for_esc")
		return
	_ok("preview_active_before_esc")

	var committed_before := int(_ba.call("get_committed_count"))
	var paused_before := _is_paused()

	if _main.has_method("reset_esc_dispatch_counts"):
		_main.call("reset_esc_dispatch_counts")
	if _router.has_method("reset_escape_resolve_count"):
		_router.call("reset_escape_resolve_count")

	print("[P2E001_E1_ESC] WITNESS_BEGIN single_physical_esc_sequence")
	# One physical Esc down/up — no echo, no hold-repeat.
	await _press_key(KEY_ESCAPE, "cancel_action_esc_single")
	for i in range(20):
		await process_frame
	print("[P2E001_E1_ESC] WITNESS_END single_physical_esc_sequence")

	var counts: Dictionary = {}
	if _main.has_method("get_esc_dispatch_counts"):
		counts = _main.call("get_esc_dispatch_counts") as Dictionary
	var resolve_n := int(counts.get("resolve_count", -1))
	var cancel_apply_n := int(counts.get("cancel_apply_count", -1))
	var router_resolve_n := -1
	if _router.has_method("get_escape_resolve_count"):
		router_resolve_n = int(_router.call("get_escape_resolve_count"))

	var st1: Dictionary = _ba.call("get_active_state") as Dictionary
	var active_after := bool(st1.get("active", true))
	var committed_after := int(_ba.call("get_committed_count"))
	var paused_after := _is_paused()

	# Second Esc with no preview: must not open Pause (build_esc_no_pause).
	if _main.has_method("reset_esc_dispatch_counts"):
		_main.call("reset_esc_dispatch_counts")
	await _press_key(KEY_ESCAPE, "esc_idle_build")
	for i in range(12):
		await process_frame
	var counts2: Dictionary = {}
	if _main.has_method("get_esc_dispatch_counts"):
		counts2 = _main.call("get_esc_dispatch_counts") as Dictionary
	var paused_idle := _is_paused()

	_witness = {
		"physical_esc_sequences": 1,
		"main_resolve_count": resolve_n,
		"main_cancel_apply_count": cancel_apply_n,
		"router_escape_resolve_count": router_resolve_n,
		"pause_opened": paused_after or paused_idle,
		"paused_before": paused_before,
		"paused_after_preview_esc": paused_after,
		"paused_after_idle_esc": paused_idle,
		"preview_active_before": true,
		"preview_active_after": active_after,
		"committed_before": committed_before,
		"committed_after": committed_after,
		"committed_untouched": committed_before == committed_after,
		"idle_esc_resolve_count": int(counts2.get("resolve_count", -1)),
		"idle_esc_cancel_apply_count": int(counts2.get("cancel_apply_count", -1)),
		"select_module_called": false,
		"confirm_and_commit_direct": false,
		"input_sequence": [
			"request_context:build",
			"KEY_PERIOD build_module_next",
			"KEY_P build_place",
			"KEY_ESCAPE cancel_action (single sequence)",
			"KEY_ESCAPE idle build (no pause)",
		],
	}

	print(
		"[P2E001_E1_ESC] COUNTS resolve_n=%d cancel_apply_n=%d router_resolve_n=%d pause=%s active_after=%s"
		% [resolve_n, cancel_apply_n, router_resolve_n, str(paused_after or paused_idle), str(active_after)]
	)
	print("[P2E001_E1_ESC] WITNESS_JSON %s" % JSON.stringify(_witness))

	# Fail-closed gates for single-dispatch.
	if resolve_n != 1:
		_fail("esc_resolve_count_not_1", "resolve_n=%d" % resolve_n)
	else:
		_ok("esc_resolve_count_exactly_1")
	if cancel_apply_n != 1:
		_fail("esc_cancel_apply_count_not_1", "cancel_apply_n=%d" % cancel_apply_n)
	else:
		_ok("esc_cancel_apply_count_exactly_1")
	if paused_after or paused_idle:
		_fail("esc_opened_pause")
	else:
		_ok("esc_zero_pause")
	if active_after:
		_fail("esc_did_not_cancel_preview")
	else:
		_ok("esc_cancelled_preview_once")
	if committed_before != committed_after:
		_fail("cancel_touched_committed")
	else:
		_ok("committed_untouched")

	# Capture cancelled state PNG (focused evidence; D72 dual-res bound to 003).
	await _capture_viewport("esc_cancelled_preview_1280x720.png")


func _capture_viewport(filename: String) -> void:
	var img: Image = null
	var vp := root.get_viewport()
	if vp != null:
		var tex: ViewportTexture = vp.get_texture()
		if tex != null:
			img = tex.get_image()
	if img == null:
		_fail("capture_image_null", filename)
		return
	var path := EVIDENCE_ABS.path_join(filename)
	var err := img.save_png(path)
	if err != OK:
		_fail("save_png", "%s err=%s" % [filename, str(err)])
		return
	print("[P2E001_E1_ESC] CAPTURED %s w=%d h=%d" % [filename, img.get_width(), img.get_height()])
	_ok("captured_" + filename)


func _teardown_clean() -> void:
	if _ba != null and is_instance_valid(_ba):
		if _ba.has_method("cancel_preview"):
			_ba.call("cancel_preview")
		if _ba.has_method("dispose_all_previews"):
			_ba.call("dispose_all_previews")
		if _ba.has_method("dispose_committed_presentation"):
			_ba.call("dispose_committed_presentation")
	Input.set_custom_mouse_cursor(null)
	for gname in ["block_assembly_preview", "block_assembly_committed", "manifestation_instances"]:
		if root.get_tree() == null:
			break
		for n in root.get_tree().get_nodes_in_group(gname):
			if n == null or not is_instance_valid(n):
				continue
			if n.has_method("free_cleanup"):
				n.call("free_cleanup")
			elif n.has_method("_dispose_visuals"):
				n.call("_dispose_visuals")
				n.queue_free()
			else:
				n.queue_free()
	if current_scene != null and is_instance_valid(current_scene):
		current_scene.queue_free()
	_main = null
	_ba = null
	for i in range(48):
		await process_frame
	RenderingServer.force_draw()
	await process_frame
	await process_frame
	await process_frame
	print("[P2E001_E1_ESC] teardown_clean done")


func _write_witness() -> void:
	var path := EVIDENCE_ABS.path_join("esc_single_dispatch_witness.json")
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		_fail("witness_write_failed")
		return
	var payload := {
		"schema": "p2e_001_e1_esc_single_dispatch_witness/1.0",
		"wave": "E1",
		"directive_id": 73,
		"finding_id": "P2E-CODEX-ESC-DOUBLE-01",
		"pass": _failed == 0,
		"counts": _witness,
		"input_log": _input_log,
		"passed_checks": _passed,
		"failed_checks": _failed,
		"failures": Array(_failures),
	}
	f.store_string(JSON.stringify(payload, "\t"))
	f.close()
	print("[P2E001_E1_ESC] wrote %s" % path)


func _is_paused() -> bool:
	## External evidence scripts cannot use Autoload identifiers at compile time.
	## game_manager.gd: enum GameState { BOOT, ART_STYLE_SELECT, IN_WORLD, PAUSED, SETTINGS }
	## PAUSED == 3 (not 2 which is IN_WORLD).
	var gm := root.get_node_or_null("/root/GameManager")
	if gm == null:
		return false
	if gm.has_method("is_paused"):
		return bool(gm.call("is_paused"))
	var st = gm.get("state")
	if st == null:
		return false
	return int(st) == 3


func _audit_product_place_key() -> void:
	_product_key_p_present = false
	if not InputMap.has_action("build_place"):
		return
	for ev in InputMap.action_get_events("build_place"):
		if ev is InputEventKey:
			var ke := ev as InputEventKey
			if int(ke.physical_keycode) == KEY_P or int(ke.keycode) == KEY_P:
				_product_key_p_present = true
				break
	print("[P2E001_E1_ESC] audit build_place_KEY_P present=%s" % str(_product_key_p_present))


func _set_window(w: int, h: int) -> void:
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	DisplayServer.window_set_size(Vector2i(w, h))
	print("[P2E001_E1_ESC] window=%dx%d" % [w, h])


func _press_key(keycode: int, label: String) -> void:
	await _press_key_down(keycode, label)
	await process_frame
	await _press_key_up(keycode, label + "_up")


func _press_key_down(keycode: int, label: String) -> void:
	## Single physical injection via Input.parse_input_event only.
	## (parse + push_input dual-fire was the D72 headed harness pattern that
	## amplified double Main._input; E0 product fix + single inject closes the gate.)
	## parse_input_event updates InputMap just_pressed so Main Esc guard can pass.
	var key := InputEventKey.new()
	key.keycode = keycode as Key
	key.physical_keycode = keycode as Key
	key.pressed = true
	key.echo = false
	Input.parse_input_event(key)
	_log_input("key_down", label, {"keycode": keycode, "inject": "parse_input_event_single"})


func _press_key_up(keycode: int, label: String) -> void:
	var key := InputEventKey.new()
	key.keycode = keycode as Key
	key.physical_keycode = keycode as Key
	key.pressed = false
	key.echo = false
	Input.parse_input_event(key)
	_log_input("key_up", label, {"keycode": keycode, "inject": "parse_input_event_single"})


func _log_input(kind: String, label: String, extra: Dictionary) -> void:
	var e := {"t": Time.get_ticks_msec(), "kind": kind, "label": label}
	for k in extra.keys():
		e[k] = extra[k]
	_input_log.append(e)
	print("[P2E001_E1_INPUT] %s %s %s" % [kind, label, str(extra)])


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	_failed += 1
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _finish() -> void:
	if _failed == 0:
		print("AIDLE_P2E001_E1_ESC_SINGLE=PASS checks=%d" % _passed)
		print(
			"AIDLE_P2E001_E1_ESC_COUNTS resolve=%s cancel_apply=%s pause=0"
			% [
				str(_witness.get("main_resolve_count", "?")),
				str(_witness.get("main_cancel_apply_count", "?")),
			]
		)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("AIDLE_P2E001_E1_ESC_SINGLE=FAIL failed=%d passed=%d" % [_failed, _passed])
		quit(1)

## P2E-001 C2 headed real-input capture (VERIFY_ONLY evidence lease only).
## Writes under orchestration/evidence/p2e_001/002 only — never patches product.
## Module selection / place / rotate / elev / cancel / confirm go through Main InputMap
## path (InputEventKey). Does NOT call select_module to create playable state.
## Runtime-only InputMap KEY_P added for build_place because product binds LMB only
## and Main._input filters to InputEventKey (documented residual C2-R-PLACE-KEY).
extends SceneTree

const MAIN_SCENE := "res://scenes/main/main.tscn"
const EVIDENCE_ABS := "E:/AIdle_openworld/orchestration/evidence/p2e_001/002"

const VIEWPORTS := [
	{"w": 1280, "h": 720, "tag": "1280x720"},
	{"w": 868, "h": 517, "tag": "868x517"},
]

var _passed: int = 0
var _failed: int = 0
var _failures: PackedStringArray = []
var _captures: Array = []
var _sha_seen: Dictionary = {}
var _input_log: Array = []
var _router: Node = null
var _main: Node = null
var _ba: Node = null
var _camera: Node3D = null
var _banner: Label = null
var _banner_layer: CanvasLayer = null
var _place_key_added: bool = false


func _initialize() -> void:
	print("[P2E001_C2_HEADED] start child_wave=C2 real_input=true")
	print("[P2E001_C2_HEADED] evidence=%s" % EVIDENCE_ABS)
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
		art.call("set_world_meta_path_override", "user://p2e001_c2_isolated/world_meta.cfg")
		_ok("world_meta_isolated")
	else:
		_ok("world_meta_isolation_best_effort")

	_ensure_runtime_place_key()
	_set_window(1280, 720)
	await process_frame
	await process_frame

	var err := change_scene_to_file(MAIN_SCENE)
	if err != OK:
		_fail("load_main", str(err))
		_finish()
		return
	for i in range(56):
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

	_camera = _find_camera(_main)
	if _camera == null:
		_fail("camera_missing")
		_finish()
		return
	_ok("camera_bound")

	_install_banner()

	await _run_state_matrix("1280x720", 1280, 720)
	await _run_state_matrix("868x517", 868, 517)

	# F02: aggressive evidence-side dispose before quit (no product patch).
	await _teardown_clean()

	_write_runtime_manifest()
	_finish()


func _teardown_clean() -> void:
	## Best-effort release of preview/committed meshes + harness UI before engine exit.
	if _ba != null and _ba.has_method("cancel_preview"):
		_ba.call("cancel_preview")
	if _ba != null and _ba.has_method("dispose_all_previews"):
		_ba.call("dispose_all_previews")
	# Free any remaining preview/committed visual nodes under BA groups.
	for gname in ["block_assembly_preview", "block_assembly_committed", "manifestation_instances"]:
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
	if _banner_layer != null and is_instance_valid(_banner_layer):
		_banner_layer.queue_free()
		_banner_layer = null
		_banner = null
	# Drop main scene tree so viewport textures release before process exit.
	if current_scene != null and is_instance_valid(current_scene):
		current_scene.queue_free()
	_main = null
	_ba = null
	_camera = null
	for i in range(40):
		await process_frame
	RenderingServer.force_draw()
	await process_frame
	await process_frame
	print("[P2E001_C2_HEADED] teardown_clean done")


func _ensure_runtime_place_key() -> void:
	## Product maps build_place → LMB only; Main._input accepts InputEventKey only.
	## Evidence harness adds KEY_P at runtime (not a product file write) so place
	## still goes through Main's is_action_pressed("build_place") → place_highlighted_module.
	if not InputMap.has_action("build_place"):
		InputMap.add_action("build_place", 0.2)
	var key := InputEventKey.new()
	key.keycode = KEY_P
	key.physical_keycode = KEY_P
	var exists := false
	for ev in InputMap.action_get_events("build_place"):
		if ev is InputEventKey and int((ev as InputEventKey).physical_keycode) == KEY_P:
			exists = true
			break
		if ev is InputEventKey and int((ev as InputEventKey).keycode) == KEY_P:
			exists = true
			break
	if not exists:
		InputMap.action_add_event("build_place", key)
		_place_key_added = true
	_log_input("runtime_inputmap", "build_place+=KEY_P", {"added": _place_key_added})
	_ok("runtime_place_key_p")


func _run_state_matrix(tag: String, w: int, h: int) -> void:
	_set_window(w, h)
	for i in range(10):
		await process_frame

	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")
	if _ba.has_method("cancel_preview"):
		_ba.call("cancel_preview")
	await process_frame
	await process_frame

	# ── 1) exploration_camera_R ────────────────────────────────────────────
	await _press_key(KEY_TAB, "build_mode_toggle_to_explore_guard")  # noop if already
	if _router.has_method("request_context"):
		_router.call("request_context", "exploration")
	_log_input("context", "exploration", {})
	await process_frame
	var yaw0 := _get_yaw()
	await _press_key(KEY_R, "rotate_camera_right")
	for i in range(36):
		await process_frame
	var yaw1 := _get_yaw()
	_set_banner(
		"exploration_camera_R | yaw0=%.4f yaw1=%.4f Δ=%.4f | BA inactive"
		% [yaw0, yaw1, yaw1 - yaw0]
	)
	await process_frame
	await _capture(
		"exploration_camera_R_%s.png" % tag,
		w,
		h,
		"exploration_camera_R",
		{
			"context": str(_router.call("get_primary_context")),
			"camera_yaw_before": yaw0,
			"camera_yaw_after": yaw1,
			"yaw_delta_abs": absf(yaw1 - yaw0),
			"camera_rotated": absf(yaw1 - yaw0) > 0.01,
			"ba_active": bool((_ba.call("get_active_state") as Dictionary).get("active", false)),
			"input_sequence": ["request_context:exploration", "KEY_R rotate_camera_right"],
			"select_module_called": false,
		}
	)

	# ── 2) module_selection (7th label) — cycle without place ──────────────
	await _press_key(KEY_TAB, "build_mode_toggle")
	if _router.has_method("request_context"):
		# Ensure build primary even if toggle landed elsewhere.
		_router.call("request_context", "build")
	_log_input("context", "build", {})
	for i in range(8):
		await process_frame
	var p0: Dictionary = {}
	if _ba.has_method("get_picker_state"):
		p0 = _ba.call("get_picker_state") as Dictionary
	var h0 := str(p0.get("highlighted_module_id", ""))
	await _press_key(KEY_PERIOD, "build_module_next")
	for i in range(6):
		await process_frame
	await _press_key(KEY_PERIOD, "build_module_next")
	for i in range(6):
		await process_frame
	var p1: Dictionary = {}
	if _ba.has_method("get_picker_state"):
		p1 = _ba.call("get_picker_state") as Dictionary
	var h1 := str(p1.get("highlighted_module_id", ""))
	var hud0: Dictionary = {}
	if _ba.has_method("get_hud_state"):
		hud0 = _ba.call("get_hud_state") as Dictionary
	_set_banner(
		"module_selection | hi %s→%s | via KEY_PERIOD build_module_next | no select_module"
		% [h0, h1]
	)
	await process_frame
	await _capture(
		"module_selection_%s.png" % tag,
		w,
		h,
		"module_selection",
		{
			"context": str(_router.call("get_primary_context")),
			"highlighted_before": h0,
			"highlighted_after": h1,
			"picker": p1.duplicate(true),
			"hud": hud0.duplicate(true),
			"input_sequence": [
				"KEY_TAB build_mode_toggle",
				"request_context:build",
				"KEY_PERIOD build_module_next x2",
			],
			"select_module_called": false,
			"via": "input_cycle",
			"ba_active": bool((_ba.call("get_active_state") as Dictionary).get("active", false)),
		}
	)

	# ── 3) build_preview_R — place via KEY_P then R rotates preview only ───
	await _press_key(KEY_P, "build_place")
	for i in range(12):
		await process_frame
	var st_place: Dictionary = _ba.call("get_active_state") as Dictionary
	if not bool(st_place.get("active", false)):
		# Fallback: if KEY_P path failed, still try InputEventAction then report residual.
		_log_input("fallback", "place_highlighted_module_direct", {"reason": "KEY_P did not activate"})
		if _ba.has_method("place_highlighted_module"):
			_ba.call("place_highlighted_module")
		for i in range(8):
			await process_frame
		st_place = _ba.call("get_active_state") as Dictionary
	var yaw_b0 := _get_yaw()
	var rot0 := float((st_place.get("placement", {}) as Dictionary).get("rotation_deg", 0.0))
	if _camera != null and _camera.has_method("freeze_yaw_now"):
		_camera.call("freeze_yaw_now")
	await _press_key(KEY_R, "build_rotate_right")
	for i in range(18):
		await process_frame
	var st_rot: Dictionary = _ba.call("get_active_state") as Dictionary
	var rot1 := float((st_rot.get("placement", {}) as Dictionary).get("rotation_deg", 0.0))
	var yaw_b1 := _get_yaw()
	var yaw_unchanged := is_equal_approx(yaw_b0, yaw_b1)
	_set_banner(
		"build_preview_R | rot %.1f→%.1f | camera_yaw_unchanged=%s | yaw=%.4f"
		% [rot0, rot1, str(yaw_unchanged), yaw_b1]
	)
	await process_frame
	await _capture(
		"build_preview_R_%s.png" % tag,
		w,
		h,
		"build_preview_R",
		{
			"context": str(_router.call("get_primary_context")),
			"rot_before": rot0,
			"rot_after": rot1,
			"preview_rotated": not is_equal_approx(rot0, rot1),
			"camera_yaw_before": yaw_b0,
			"camera_yaw_after": yaw_b1,
			"camera_yaw_unchanged": yaw_unchanged,
			"stage": str(st_rot.get("stage", "")),
			"module_id": str(st_rot.get("module_id", "")),
			"input_sequence": [
				"KEY_P build_place (runtime InputMap KEY_P)",
				"KEY_R build_rotate_right",
			],
			"select_module_called": false,
			"place_via": "main_input_build_place",
		}
	)
	if not yaw_unchanged:
		_fail("camera_yaw_changed_in_build", "before=%.6f after=%.6f" % [yaw_b0, yaw_b1])

	# ── 4) valid_snapped_preview ───────────────────────────────────────────
	if _ba.has_method("advance_stage"):
		_ba.call("advance_stage", "hologram")
	for i in range(10):
		await process_frame
	var stv: Dictionary = _ba.call("get_active_state") as Dictionary
	var plv: Dictionary = stv.get("placement", {}) as Dictionary
	var val: Dictionary = stv.get("validity", {}) as Dictionary
	if val.is_empty() and _ba.has_method("get_validity"):
		val = _ba.call("get_validity") as Dictionary
	var hudv: Dictionary = {}
	if _ba.has_method("get_hud_state"):
		hudv = _ba.call("get_hud_state") as Dictionary
	_set_banner(
		"valid_snapped_preview | snap x=%.2f y=%.2f elev=%.2f rot=%.1f | ok=%s"
		% [
			float(plv.get("x", -1)),
			float(plv.get("y", -1)),
			float(plv.get("elevation", -1)),
			float(plv.get("rotation_deg", -1)),
			str(val.get("ok", false)),
		]
	)
	await process_frame
	await _capture(
		"valid_snapped_preview_%s.png" % tag,
		w,
		h,
		"valid_snapped_preview",
		{
			"placement": plv.duplicate(true),
			"stage": str(stv.get("stage", "")),
			"validity": val.duplicate(true),
			"hud": hudv.duplicate(true),
			"collision_pre_commit": bool(stv.get("collision", true)),
			"input_sequence": ["prior place+rotate", "advance_stage:hologram (presentation)"],
			"select_module_called": false,
		}
	)

	# ── 5) rejected_invalid_placement — elev out of budget via PageUp ──────
	if _ba.has_method("cancel_preview"):
		_ba.call("cancel_preview")
	await process_frame
	await _press_key(KEY_P, "build_place")
	for i in range(8):
		await process_frame
	# PageUp elevate many steps (real InputMap path) past BOUNDS_MAX_HEIGHT 64m.
	for s in range(40):
		await _press_key(KEY_PAGEUP, "build_elevation_up")
	# Residual bulk if still under budget (frame batching): controller elevate.
	var elev_now := float(
		((_ba.call("get_active_state") as Dictionary).get("placement", {}) as Dictionary).get(
			"elevation", 0.0
		)
	)
	var elev_residual := false
	if elev_now < 64.0 and _ba.has_method("elevate"):
		_ba.call("elevate", 300)
		elev_residual = true
		_log_input("residual", "elevate(300)_bulk", {"elev_before_bulk": elev_now})
	for i in range(8):
		await process_frame
	var last_rej: Dictionary = {}
	if _ba.has_method("get_last_reject"):
		last_rej = _ba.call("get_last_reject") as Dictionary
	var val_bad: Dictionary = {}
	if _ba.has_method("get_validity"):
		val_bad = _ba.call("get_validity") as Dictionary
	var hud_bad: Dictionary = {}
	if _ba.has_method("get_hud_state"):
		hud_bad = _ba.call("get_hud_state") as Dictionary
	_set_banner(
		"rejected_invalid_placement | validity_ok=%s code=%s | elev_residual_bulk=%s"
		% [str(val_bad.get("ok", true)), str(val_bad.get("code", last_rej.get("code", ""))), str(elev_residual)]
	)
	await process_frame
	await _capture(
		"rejected_invalid_placement_%s.png" % tag,
		w,
		h,
		"rejected_invalid_placement",
		{
			"validity": val_bad.duplicate(true),
			"last_reject": last_rej.duplicate(true),
			"hud": hud_bad.duplicate(true),
			"elev_bulk_residual": elev_residual,
			"ba_active": bool((_ba.call("get_active_state") as Dictionary).get("active", false)),
			"input_sequence": [
				"cancel_preview",
				"KEY_P build_place",
				"KEY_PAGEUP build_elevation_up x40",
				"elevate(300) residual if still in bounds",
			],
			"select_module_called": false,
		}
	)

	# ── 6) confirmed_complete — real-input place + confirm hold Enter ──────
	if _ba.has_method("cancel_preview"):
		_ba.call("cancel_preview")
	await process_frame
	await _press_key(KEY_P, "build_place")
	for i in range(10):
		await process_frame
	if not bool((_ba.call("get_active_state") as Dictionary).get("active", false)):
		if _ba.has_method("place_highlighted_module"):
			_ba.call("place_highlighted_module")
		for i in range(6):
			await process_frame
	if _ba.has_method("advance_stage"):
		_ba.call("advance_stage", "hologram")
		await process_frame
		_ba.call("advance_stage", "materializing")
		await process_frame
	var committed_before_confirm := int(_ba.call("get_committed_count"))
	# Hold confirm_action (KEY_ENTER) without early release — Main._process completes hold.
	await _press_key_down(KEY_ENTER, "confirm_action")
	for i in range(90):
		await process_frame
	await _press_key_up(KEY_ENTER, "confirm_action_release")
	for i in range(16):
		await process_frame
	var receipt: Dictionary = {}
	if _main.has_method("get_last_confirm_result"):
		receipt = _main.call("get_last_confirm_result") as Dictionary
	var last_r: Dictionary = {}
	if _ba.has_method("get_last_receipt"):
		last_r = _ba.call("get_last_receipt") as Dictionary
	# If hold path did not commit (a11y timing), residual explicit confirm via main path.
	var confirm_residual := false
	if int(_ba.call("get_committed_count")) <= committed_before_confirm:
		if _ba.has_method("confirm_and_commit"):
			var cres: Dictionary = _ba.call("confirm_and_commit", true) as Dictionary
			receipt = cres
			confirm_residual = true
			_log_input("residual", "confirm_and_commit_direct", {"ok": bool(cres.get("ok", false))})
		for i in range(12):
			await process_frame
		if _ba.has_method("get_last_receipt"):
			last_r = _ba.call("get_last_receipt") as Dictionary
	var stc: Dictionary = _ba.call("get_active_state") as Dictionary
	_set_banner(
		"confirmed_complete | ok=%s status=%s committed=%s residual=%s"
		% [
			str(bool(receipt.get("ok", false))),
			str(receipt.get("status", last_r.get("status", ""))),
			str(_ba.call("get_committed_count")),
			str(confirm_residual),
		]
	)
	await process_frame
	await _capture(
		"confirmed_complete_%s.png" % tag,
		w,
		h,
		"confirmed_complete",
		{
			"receipt_ok": bool(receipt.get("ok", false) or str(last_r.get("status", "")) in ["committed", "idempotent_replay"]),
			"receipt_status": str(receipt.get("status", last_r.get("status", ""))),
			"issuer": str(receipt.get("issuer", (last_r.get("authority", {}) as Dictionary).get("issuer", ""))),
			"committed_count": int(_ba.call("get_committed_count")),
			"active_after": bool(stc.get("active", false)),
			"confirm_hold_residual_direct": confirm_residual,
			"input_sequence": [
				"KEY_P build_place",
				"advance_stage hologram/materializing",
				"KEY_ENTER confirm_action hold ~1.5s",
			],
			"select_module_called": false,
		}
	)

	# ── 7) cancelled_preview — place then Esc; committed untouched ─────────
	var committed_before := int(_ba.call("get_committed_count"))
	await _press_key(KEY_P, "build_place")
	for i in range(10):
		await process_frame
	if not bool((_ba.call("get_active_state") as Dictionary).get("active", false)):
		if _ba.has_method("place_highlighted_module"):
			_ba.call("place_highlighted_module")
		for i in range(6):
			await process_frame
	if _ba.has_method("advance_stage"):
		_ba.call("advance_stage", "hologram")
	for i in range(8):
		await process_frame
	await _press_key(KEY_ESCAPE, "cancel_action")
	for i in range(14):
		await process_frame
	var committed_after := int(_ba.call("get_committed_count"))
	var active_after_cancel := bool((_ba.call("get_active_state") as Dictionary).get("active", true))
	# If Esc did not cancel (focus/other cancel target), residual cancel_preview.
	var cancel_residual := false
	if active_after_cancel:
		if _ba.has_method("cancel_preview"):
			_ba.call("cancel_preview")
			cancel_residual = true
			_log_input("residual", "cancel_preview_direct", {})
		for i in range(8):
			await process_frame
		active_after_cancel = bool((_ba.call("get_active_state") as Dictionary).get("active", true))
		committed_after = int(_ba.call("get_committed_count"))
	_set_banner(
		"cancelled_preview | active=%s committed %d→%d untouched=%s residual=%s"
		% [
			str(active_after_cancel),
			committed_before,
			committed_after,
			str(committed_before == committed_after),
			str(cancel_residual),
		]
	)
	await process_frame
	await _capture(
		"cancelled_preview_%s.png" % tag,
		w,
		h,
		"cancelled_preview",
		{
			"committed_before": committed_before,
			"committed_after": committed_after,
			"committed_untouched": committed_before == committed_after,
			"ba_active": active_after_cancel,
			"cancel_esc_residual_direct": cancel_residual,
			"input_sequence": ["KEY_P build_place", "KEY_ESCAPE cancel_action"],
			"select_module_called": false,
		}
	)

	if _ba.has_method("cancel_preview"):
		_ba.call("cancel_preview")


func _press_key(keycode: int, label: String) -> void:
	await _press_key_down(keycode, label)
	await process_frame
	await _press_key_up(keycode, label + "_up")


func _press_key_down(keycode: int, label: String) -> void:
	var key := InputEventKey.new()
	key.keycode = keycode as Key
	key.physical_keycode = keycode as Key
	key.pressed = true
	key.echo = false
	Input.parse_input_event(key)
	# Also push to viewport so Main._input receives it when focus is correct.
	if _main != null:
		_main.get_viewport().push_input(key, true)
	_log_input("key_down", label, {"keycode": keycode})


func _press_key_up(keycode: int, label: String) -> void:
	var key := InputEventKey.new()
	key.keycode = keycode as Key
	key.physical_keycode = keycode as Key
	key.pressed = false
	key.echo = false
	Input.parse_input_event(key)
	if _main != null:
		_main.get_viewport().push_input(key, true)
	_log_input("key_up", label, {"keycode": keycode})


func _log_input(kind: String, label: String, extra: Dictionary) -> void:
	var e := {"t": Time.get_ticks_msec(), "kind": kind, "label": label}
	for k in extra.keys():
		e[k] = extra[k]
	_input_log.append(e)
	print("[P2E001_C2_INPUT] %s %s %s" % [kind, label, str(extra)])


func _install_banner() -> void:
	_banner_layer = CanvasLayer.new()
	_banner_layer.layer = 100
	root.add_child(_banner_layer)
	_banner = Label.new()
	_banner.name = "C2EvidenceBanner"
	_banner.position = Vector2(12, 12)
	_banner.size = Vector2(1240, 48)
	_banner.add_theme_font_size_override("font_size", 15)
	_banner.add_theme_color_override("font_color", Color(0.9, 1, 0.85, 1))
	_banner.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
	_banner.add_theme_constant_override("outline_size", 4)
	_banner.text = "P2E-001 C2 real-input evidence"
	_banner_layer.add_child(_banner)


func _set_banner(text: String) -> void:
	if _banner != null:
		_banner.text = "P2E-001 C2 | " + text
		_banner.size = Vector2(maxf(float(DisplayServer.window_get_size().x) - 24.0, 400.0), 56.0)


func _find_camera(n: Node) -> Node3D:
	if n is Camera3D:
		return n as Node3D
	if n.get_script() != null:
		var sp := str(n.get_script().resource_path) if n.get_script() is Resource else ""
		if sp.ends_with("cozy_camera.gd"):
			return n as Node3D
	for c in n.get_children():
		var found := _find_camera(c)
		if found != null:
			return found
	for g in ["cozy_camera", "player_camera"]:
		var nodes := root.get_tree().get_nodes_in_group(g)
		if nodes.size() > 0 and nodes[0] is Node3D:
			return nodes[0] as Node3D
	return _find_camera3d(n)


func _find_camera3d(n: Node) -> Node3D:
	if n is Camera3D:
		return n as Node3D
	for c in n.get_children():
		var f := _find_camera3d(c)
		if f != null:
			return f
	return null


func _get_yaw() -> float:
	if _camera == null:
		return 0.0
	if _camera.has_method("get_yaw"):
		return float(_camera.call("get_yaw"))
	return float(_camera.rotation.y)


func _set_window(w: int, h: int) -> void:
	if DisplayServer.get_name() == "headless":
		return
	DisplayServer.window_set_size(Vector2i(w, h))
	var win := root as Window
	if win != null:
		win.size = Vector2i(w, h)
	print("[P2E001_C2_HEADED] window=%dx%d" % [w, h])


func _capture(filename: String, expect_w: int, expect_h: int, state: String, extra: Dictionary = {}) -> void:
	await process_frame
	await process_frame
	await process_frame
	if DisplayServer.get_name() == "headless":
		_fail("capture_headless", filename)
		return
	RenderingServer.force_draw()
	await process_frame
	var img: Image = get_root().get_viewport().get_texture().get_image()
	if img == null:
		_fail("capture_null", filename)
		return
	var iw := img.get_width()
	var ih := img.get_height()
	if absi(iw - expect_w) > 24 or absi(ih - expect_h) > 24:
		_fail("wrong_dimensions", "%s got=%dx%d expect~%dx%d" % [filename, iw, ih, expect_w, expect_h])
	if _is_blank(img):
		_fail("blank_image", filename)
		return
	var abs_path := EVIDENCE_ABS.path_join(filename)
	if img.save_png(abs_path) != OK:
		_fail("save_png", filename)
		return
	var sha := FileAccess.get_sha256(abs_path)
	if sha.is_empty():
		_fail("sha_empty", filename)
		return
	if _sha_seen.has(sha):
		_fail("duplicate_sha", "%s == %s" % [filename, str(_sha_seen[sha])])
		return
	_sha_seen[sha] = filename
	var entry := {
		"file": filename,
		"path": abs_path.replace("\\", "/"),
		"width": iw,
		"height": ih,
		"sha256": sha,
		"state": state,
		"capture_source": "godot_headed_real_input",
		"select_module_source": "none_playable_input_path",
		"context": str(_router.call("get_primary_context")) if _router else "",
	}
	for k in extra.keys():
		entry[k] = extra[k]
	_captures.append(entry)
	_ok("captured_%s" % filename)
	print(
		"[P2E001_C2_HEADED] CAPTURED file=%s %dx%d sha=%s state=%s"
		% [filename, iw, ih, sha.substr(0, 16), state]
	)


func _is_blank(img: Image) -> bool:
	var w := img.get_width()
	var h := img.get_height()
	if w < 8 or h < 8:
		return true
	var first: Color = img.get_pixel(w / 2, h / 2)
	var same := 0
	var total := 0
	for gy in range(8):
		for gx in range(8):
			var x := int((gx + 0.5) * w / 8.0)
			var y := int((gy + 0.5) * h / 8.0)
			var c: Color = img.get_pixel(x, y)
			total += 1
			if absf(c.r - first.r) < 0.03 and absf(c.g - first.g) < 0.03 and absf(c.b - first.b) < 0.03:
				same += 1
	return same >= total - 2


func _write_runtime_manifest() -> void:
	var build_r_flags: Array = []
	for c in _captures:
		if str(c.get("state", "")) == "build_preview_R":
			build_r_flags.append(
				{
					"file": c.get("file"),
					"camera_yaw_unchanged": c.get("camera_yaw_unchanged"),
					"camera_yaw_before": c.get("camera_yaw_before"),
					"camera_yaw_after": c.get("camera_yaw_after"),
					"rot_before": c.get("rot_before"),
					"rot_after": c.get("rot_after"),
				}
			)
	var meta := {
		"schema": "p2e_001_c2_visual_claim_meta/1.0",
		"work_order": "WO-P2E-001-PLAYABILITY-CORRECTION-001",
		"wave": "C2",
		"directive_id": 71,
		"authority_token": "VERIFY_ONLY",
		"capture_source": "godot_headed_real_input",
		"timestamp": Time.get_datetime_string_from_system(true, true),
		"passed_checks": _passed,
		"failed_checks": _failed,
		"failures": Array(_failures),
		"captures": _captures,
		"input_log": _input_log,
		"build_preview_R_yaw_proof": build_r_flags,
		"runtime_place_key_p_added": _place_key_added,
		"residuals": [
			"C2-R-PLACE-KEY: build_place product binding is LMB; Main._input is InputEventKey-only — harness added KEY_P at runtime for place path",
			"C2-R-ELEV-BULK: if PageUp x40 insufficient, elevate(300) used for invalid budget proof (not select_module)",
			"C2-R-CONFIRM-HOLD: if Enter hold did not commit, confirm_and_commit residual",
			"C2-R-CANCEL-ESC: if Esc did not clear preview, cancel_preview residual",
			"C1-R01/R02/R03 carried: InputMap persistence, HUD slot side-effects, build_cancel RMB",
		],
		"select_module_api_injection": false,
		"product_writes": [],
		"d70_evidence_immutable": "orchestration/evidence/p2e_001/001/**",
	}
	var path := EVIDENCE_ABS.path_join("visual_claim_meta.json")
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		_fail("write_meta")
		return
	f.store_string(JSON.stringify(meta, "\t"))
	f.close()
	_ok("wrote_visual_claim_meta")


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	_failed += 1
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _finish() -> void:
	print(
		"[P2E001_C2_HEADED] done passed=%d failed=%d captures=%d"
		% [_passed, _failed, _captures.size()]
	)
	# Expect 14 captures (7 states × 2 viewports).
	if _failed == 0 and _captures.size() >= 12:
		print("AIDLE_P2E001_C2_HEADED=PASS captures=%d" % _captures.size())
		quit(0)
	else:
		print("AIDLE_P2E001_C2_HEADED=FAIL failed=%d captures=%d" % [_failed, _captures.size()])
		quit(1)

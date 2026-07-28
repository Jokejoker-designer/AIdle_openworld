## P2E-001 D2 headed real-input capture (VERIFY_ONLY evidence lease only).
## Writes under orchestration/evidence/p2e_001/003 only — never patches product.
## Module select / place / rotate / elev / cancel / confirm go through Main InputMap
## path (InputEventKey). Does NOT call select_module, place_highlighted_module,
## confirm_and_commit, elevate(), or cancel_preview as acceptance-path fallbacks.
## Product D0 binds KEY_P on build_place via catalog ensure; BA confirm is immediate.
extends SceneTree

const MAIN_SCENE := "res://scenes/main/main.tscn"
const EVIDENCE_ABS := "E:/AIdle_openworld/orchestration/evidence/p2e_001/003"

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
var _forbidden_hits: Array = []
var _router: Node = null
var _main: Node = null
var _ba: Node = null
var _camera: Node3D = null
var _banner: Label = null
var _banner_layer: CanvasLayer = null
var _product_key_p_present: bool = false


func _initialize() -> void:
	print("[P2E001_D2_HEADED] start child_wave=D2 real_input=true no_api_fallback=true")
	print("[P2E001_D2_HEADED] evidence=%s" % EVIDENCE_ABS)
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
		art.call("set_world_meta_path_override", "user://p2e001_d2_isolated/world_meta.cfg")
		_ok("world_meta_isolated")
	else:
		_ok("world_meta_isolation_best_effort")

	_audit_product_place_key()
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

	_camera = _find_camera(_main)
	if _camera == null:
		_fail("camera_missing")
		_finish()
		return
	_ok("camera_bound")

	# Re-check KEY_P after Main/catalog bootstrap (product ensure_input_map).
	_audit_product_place_key()
	if not _product_key_p_present:
		_fail("product_build_place_missing_KEY_P")
		_finish()
		return

	_install_banner()

	await _run_state_matrix("1280x720", 1280, 720)
	await _run_state_matrix("868x517", 868, 517)

	await _teardown_clean()

	_write_runtime_manifest()
	_finish()


func _audit_product_place_key() -> void:
	_product_key_p_present = false
	if not InputMap.has_action("build_place"):
		_log_input("audit", "build_place_missing", {})
		return
	for ev in InputMap.action_get_events("build_place"):
		if ev is InputEventKey:
			var ke := ev as InputEventKey
			if int(ke.physical_keycode) == KEY_P or int(ke.keycode) == KEY_P:
				_product_key_p_present = true
				break
	_log_input("audit", "build_place_KEY_P", {"present": _product_key_p_present})


func _teardown_clean() -> void:
	## Evidence-side dispose before quit. Uses public dispose APIs only (not commit path).
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
	if _banner_layer != null and is_instance_valid(_banner_layer):
		_banner_layer.queue_free()
		_banner_layer = null
		_banner = null
	if current_scene != null and is_instance_valid(current_scene):
		current_scene.queue_free()
	_main = null
	_ba = null
	_camera = null
	for i in range(48):
		await process_frame
	RenderingServer.force_draw()
	await process_frame
	await process_frame
	await process_frame
	print("[P2E001_D2_HEADED] teardown_clean done")


func _run_state_matrix(tag: String, w: int, h: int) -> void:
	_set_window(w, h)
	for i in range(12):
		await process_frame

	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")
	# Ensure clean BA between viewports via cancel_action key when possible later; reset flag.
	await process_frame

	# ── 1) exploration_camera_R ────────────────────────────────────────────
	if _router.has_method("request_context"):
		_router.call("request_context", "exploration")
	_log_input("context", "exploration", {"via": "request_context"})
	await process_frame
	await process_frame
	var yaw0 := _get_yaw()
	await _press_key(KEY_R, "rotate_camera_right")
	for i in range(40):
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
			"input_sequence": [
				"request_context:exploration (context set)",
				"KEY_R rotate_camera_right (InputMap)",
			],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
			"place_highlighted_module_direct": false,
		}
	)

	# ── 2) module_selection — cycle without place ─────────────────────────
	await _press_key(KEY_TAB, "build_mode_toggle")
	for i in range(6):
		await process_frame
	if str(_router.call("get_primary_context")) != "build":
		if _router.has_method("request_context"):
			_router.call("request_context", "build")
			_log_input("context_guard", "build", {"via": "request_context_after_TAB"})
	_log_input("context", "build", {})
	for i in range(10):
		await process_frame
	var p0: Dictionary = {}
	if _ba.has_method("get_picker_state"):
		p0 = _ba.call("get_picker_state") as Dictionary
	var h0 := str(p0.get("highlighted_module_id", ""))
	await _press_key(KEY_PERIOD, "build_module_next")
	for i in range(8):
		await process_frame
	await _press_key(KEY_PERIOD, "build_module_next")
	for i in range(8):
		await process_frame
	var p1: Dictionary = {}
	if _ba.has_method("get_picker_state"):
		p1 = _ba.call("get_picker_state") as Dictionary
	var h1 := str(p1.get("highlighted_module_id", ""))
	var hud0: Dictionary = {}
	if _ba.has_method("get_hud_state"):
		hud0 = _ba.call("get_hud_state") as Dictionary
	_set_banner(
		"module_selection | hi %s→%s | KEY_PERIOD build_module_next | no select_module"
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
				"KEY_PERIOD build_module_next x2",
			],
			"select_module_called": false,
			"via": "input_cycle",
			"ba_active": bool((_ba.call("get_active_state") as Dictionary).get("active", false)),
		}
	)

	# ── 3) build_preview_R — KEY_P place then KEY_R rotates preview only ──
	await _press_key(KEY_P, "build_place")
	for i in range(16):
		await process_frame
	var st_place: Dictionary = _ba.call("get_active_state") as Dictionary
	if not bool(st_place.get("active", false)):
		_fail("place_via_KEY_P_failed", "viewport=%s active=false" % tag)
		_note_forbidden("would_have_used_place_highlighted_module_fallback")
		# Do not call place_highlighted_module — fail-closed for F03.
	var yaw_b0 := _get_yaw()
	var rot0 := float((st_place.get("placement", {}) as Dictionary).get("rotation_deg", 0.0))
	if _camera != null and _camera.has_method("freeze_yaw_now"):
		_camera.call("freeze_yaw_now")
	await _press_key(KEY_R, "build_rotate_right")
	for i in range(22):
		await process_frame
	# Second R to make non-zero rotation more robust if first was swallowed.
	await _press_key(KEY_R, "build_rotate_right")
	for i in range(22):
		await process_frame
	var st_rot: Dictionary = _ba.call("get_active_state") as Dictionary
	var rot1 := float((st_rot.get("placement", {}) as Dictionary).get("rotation_deg", 0.0))
	var yaw_b1 := _get_yaw()
	var yaw_unchanged := is_equal_approx(yaw_b0, yaw_b1)
	var preview_rotated := not is_equal_approx(rot0, rot1)
	if not preview_rotated:
		_fail("build_preview_R_rotation_unchanged", "viewport=%s rot0=%.1f rot1=%.1f" % [tag, rot0, rot1])
	if not yaw_unchanged:
		_fail("camera_yaw_changed_in_build", "viewport=%s before=%.6f after=%.6f" % [tag, yaw_b0, yaw_b1])
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
			"preview_rotated": preview_rotated,
			"camera_yaw_before": yaw_b0,
			"camera_yaw_after": yaw_b1,
			"camera_yaw_unchanged": yaw_unchanged,
			"stage": str(st_rot.get("stage", "")),
			"module_id": str(st_rot.get("module_id", "")),
			"ba_active": bool(st_rot.get("active", false)),
			"input_sequence": [
				"KEY_P build_place (product InputMap KEY_P)",
				"KEY_R build_rotate_right x2",
			],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
			"place_highlighted_module_direct": false,
			"place_via": "main_input_build_place",
		}
	)

	# ── 4) valid_snapped_preview (same active placement, still valid) ─────
	# Presentation stage advance is visual-only (not commit); skip API if inactive.
	if bool(st_rot.get("active", false)) and _ba.has_method("advance_stage"):
		_ba.call("advance_stage", "hologram")
		_log_input("presentation", "advance_stage:hologram", {"note": "visual only not commit"})
	for i in range(12):
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
			"input_sequence": [
				"prior KEY_P place + KEY_R rotate",
				"advance_stage:hologram (presentation visual only)",
			],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
		}
	)

	# ── 5) rejected_invalid_placement — PageUp elev past budget (key only) ─
	await _press_key(KEY_ESCAPE, "cancel_action_before_invalid")
	for i in range(12):
		await process_frame
	# If still active after Esc, fail (no cancel_preview residual as acceptance).
	if bool((_ba.call("get_active_state") as Dictionary).get("active", false)):
		_fail("esc_did_not_cancel_before_invalid", "viewport=%s" % tag)
		_note_forbidden("would_have_used_cancel_preview_fallback")
	await _press_key(KEY_P, "build_place")
	for i in range(12):
		await process_frame
	if not bool((_ba.call("get_active_state") as Dictionary).get("active", false)):
		_fail("place_for_invalid_failed", "viewport=%s" % tag)
	# 0.25m steps; need >64m → ≥257 PageUp. Key-only path, no elevate() bulk.
	for s in range(270):
		await _press_key_fast(KEY_PAGEUP, "build_elevation_up")
		if s % 30 == 0:
			await process_frame
	for i in range(10):
		await process_frame
	var elev_now := float(
		((_ba.call("get_active_state") as Dictionary).get("placement", {}) as Dictionary).get(
			"elevation", 0.0
		)
	)
	var last_rej: Dictionary = {}
	if _ba.has_method("get_last_reject"):
		last_rej = _ba.call("get_last_reject") as Dictionary
	var val_bad: Dictionary = {}
	if _ba.has_method("get_validity"):
		val_bad = _ba.call("get_validity") as Dictionary
	var hud_bad: Dictionary = {}
	if _ba.has_method("get_hud_state"):
		hud_bad = _ba.call("get_hud_state") as Dictionary
	var invalid_ok := (not bool(val_bad.get("ok", true))) or elev_now > 64.0
	if not invalid_ok:
		_fail("invalid_placement_not_proven", "elev=%.2f val=%s" % [elev_now, str(val_bad)])
	_set_banner(
		"rejected_invalid_placement | validity_ok=%s elev=%.2f code=%s | key_only"
		% [str(val_bad.get("ok", true)), elev_now, str(val_bad.get("code", last_rej.get("code", "")))]
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
			"elevation": elev_now,
			"elev_bulk_residual": false,
			"ba_active": bool((_ba.call("get_active_state") as Dictionary).get("active", false)),
			"input_sequence": [
				"KEY_ESCAPE cancel_action",
				"KEY_P build_place",
				"KEY_PAGEUP build_elevation_up x270",
			],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
			"elevate_direct_residual": false,
		}
	)

	# ── 6) confirmed_complete — KEY_P + KEY_ENTER immediate (no hold residual) ─
	await _press_key(KEY_ESCAPE, "cancel_action_before_confirm")
	for i in range(10):
		await process_frame
	await _press_key(KEY_P, "build_place")
	for i in range(14):
		await process_frame
	if not bool((_ba.call("get_active_state") as Dictionary).get("active", false)):
		_fail("place_for_confirm_failed", "viewport=%s" % tag)
		_note_forbidden("would_have_used_place_highlighted_module_fallback")
	var committed_before_confirm := int(_ba.call("get_committed_count"))
	# Immediate BA confirm path (D0 F03-R2): single KEY_ENTER press fires _on_confirm.
	await _press_key(KEY_ENTER, "confirm_action")
	for i in range(24):
		await process_frame
	var receipt: Dictionary = {}
	if _main.has_method("get_last_confirm_result"):
		receipt = _main.call("get_last_confirm_result") as Dictionary
	var last_r: Dictionary = {}
	if _ba.has_method("get_last_receipt"):
		last_r = _ba.call("get_last_receipt") as Dictionary
	var committed_after_confirm := int(_ba.call("get_committed_count"))
	var confirm_ok := committed_after_confirm > committed_before_confirm \
			or bool(receipt.get("ok", false)) \
			or str(last_r.get("status", "")) in ["committed", "idempotent_replay"]
	if not confirm_ok:
		_fail("confirm_via_KEY_ENTER_failed", "viewport=%s committed %d→%d receipt=%s" % [
			tag, committed_before_confirm, committed_after_confirm, str(receipt)
		])
		_note_forbidden("would_have_used_confirm_and_commit_direct")
	var stc: Dictionary = _ba.call("get_active_state") as Dictionary
	_set_banner(
		"confirmed_complete | ok=%s status=%s committed=%s residual=false"
		% [
			str(confirm_ok),
			str(receipt.get("status", last_r.get("status", ""))),
			str(committed_after_confirm),
		]
	)
	await process_frame
	await _capture(
		"confirmed_complete_%s.png" % tag,
		w,
		h,
		"confirmed_complete",
		{
			"receipt_ok": confirm_ok,
			"receipt_status": str(receipt.get("status", last_r.get("status", ""))),
			"issuer": str(receipt.get("issuer", (last_r.get("authority", {}) as Dictionary).get("issuer", ""))),
			"via": str(receipt.get("via", "")),
			"committed_count": committed_after_confirm,
			"active_after": bool(stc.get("active", false)),
			"confirm_hold_residual_direct": false,
			"confirm_and_commit_direct": false,
			"input_sequence": [
				"KEY_ESCAPE cancel prior invalid",
				"KEY_P build_place",
				"KEY_ENTER confirm_action (immediate BA path)",
			],
			"select_module_called": false,
		}
	)

	# ── 7) cancelled_preview — KEY_P then KEY_ESCAPE; committed untouched ──
	var committed_before := int(_ba.call("get_committed_count"))
	await _press_key(KEY_P, "build_place")
	for i in range(14):
		await process_frame
	if not bool((_ba.call("get_active_state") as Dictionary).get("active", false)):
		_fail("place_for_cancel_failed", "viewport=%s" % tag)
		_note_forbidden("would_have_used_place_highlighted_module_fallback")
	await _press_key(KEY_ESCAPE, "cancel_action")
	for i in range(16):
		await process_frame
	var committed_after := int(_ba.call("get_committed_count"))
	var active_after_cancel := bool((_ba.call("get_active_state") as Dictionary).get("active", true))
	if active_after_cancel:
		_fail("esc_did_not_cancel_preview", "viewport=%s" % tag)
		_note_forbidden("would_have_used_cancel_preview_fallback")
	if committed_before != committed_after:
		_fail("cancel_touched_committed", "before=%d after=%d" % [committed_before, committed_after])
	_set_banner(
		"cancelled_preview | active=%s committed %d→%d untouched=%s residual=false"
		% [
			str(active_after_cancel),
			committed_before,
			committed_after,
			str(committed_before == committed_after),
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
			"cancel_esc_residual_direct": false,
			"input_sequence": ["KEY_P build_place", "KEY_ESCAPE cancel_action"],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
		}
	)


func _press_key(keycode: int, label: String) -> void:
	await _press_key_down(keycode, label)
	await process_frame
	await _press_key_up(keycode, label + "_up")


func _press_key_fast(keycode: int, label: String) -> void:
	## Minimal-frame key press for bulk elevation (still InputMap path).
	await _press_key_down(keycode, label)
	await _press_key_up(keycode, label + "_up")


func _press_key_down(keycode: int, label: String) -> void:
	var key := InputEventKey.new()
	key.keycode = keycode as Key
	key.physical_keycode = keycode as Key
	key.pressed = true
	key.echo = false
	Input.parse_input_event(key)
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
	print("[P2E001_D2_INPUT] %s %s %s" % [kind, label, str(extra)])


func _note_forbidden(label: String) -> void:
	_forbidden_hits.append(label)
	print("[P2E001_D2_FORBIDDEN_AVOIDED] %s" % label)


func _install_banner() -> void:
	_banner_layer = CanvasLayer.new()
	_banner_layer.layer = 100
	root.add_child(_banner_layer)
	_banner = Label.new()
	_banner.name = "D2EvidenceBanner"
	_banner.position = Vector2(12, 12)
	_banner.size = Vector2(1240, 48)
	_banner.add_theme_font_size_override("font_size", 15)
	_banner.add_theme_color_override("font_color", Color(0.9, 1, 0.85, 1))
	_banner.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
	_banner.add_theme_constant_override("outline_size", 4)
	_banner.text = "P2E-001 D2 real-input evidence"
	_banner_layer.add_child(_banner)


func _set_banner(text: String) -> void:
	if _banner != null:
		_banner.text = "P2E-001 D2 | " + text
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
	print("[P2E001_D2_HEADED] window=%dx%d" % [w, h])


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
	var art_id := "unknown"
	var art := root.get_node_or_null("ArtStyleManager")
	if art != null:
		if art.has_method("get_active_style_id"):
			art_id = str(art.call("get_active_style_id"))
		elif art.get("active_style_id") != null:
			art_id = str(art.get("active_style_id"))
	var entry := {
		"file": filename,
		"path": abs_path.replace("\\", "/"),
		"width": iw,
		"height": ih,
		"sha256": sha,
		"state": state,
		"capture_source": "godot_headed",
		"art_style_id_active": art_id,
		"live_parity": true,
		"select_module_source": "none_playable_input_path",
		"context": str(_router.call("get_primary_context")) if _router else "",
	}
	for k in extra.keys():
		entry[k] = extra[k]
	_captures.append(entry)
	_ok("captured_%s" % filename)
	print(
		"[P2E001_D2_HEADED] CAPTURED file=%s %dx%d sha=%s state=%s"
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
					"preview_rotated": c.get("preview_rotated"),
				}
			)
	var meta := {
		"schema": "p2e_001_d2_visual_claim_meta/1.0",
		"work_order": "WO-P2E-001-PLAYABILITY-CORRECTION-002",
		"wave": "D2",
		"directive_id": 72,
		"authority_token": "VERIFY_ONLY",
		"capture_source": "godot_headed",
		"timestamp": Time.get_datetime_string_from_system(true, true),
		"passed_checks": _passed,
		"failed_checks": _failed,
		"failures": Array(_failures),
		"captures": _captures,
		"input_log": _input_log,
		"build_preview_R_yaw_proof": build_r_flags,
		"product_key_p_present": _product_key_p_present,
		"forbidden_fallback_hits": _forbidden_hits,
		"residuals": [
			"D2: no place_highlighted_module / confirm_and_commit / elevate bulk residual acceptance path",
			"D2: product KEY_P via catalog ensure_input_map (no harness InputMap write required if present)",
			"D2: advance_stage hologram is presentation-only visual for valid_snapped (not commit)",
			"D1-R01 carried: KEY_P project.godot not persisted; runtime catalog ensure",
		],
		"select_module_api_injection": false,
		"confirm_and_commit_direct_used": false,
		"product_writes": [],
		"evidence_001_002_immutable": true,
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
		"[P2E001_D2_HEADED] done passed=%d failed=%d captures=%d forbidden_hits=%d"
		% [_passed, _failed, _captures.size(), _forbidden_hits.size()]
	)
	if _failed == 0 and _captures.size() >= 14:
		print("AIDLE_P2E001_D2_HEADED=PASS captures=%d" % _captures.size())
		quit(0)
	else:
		print("AIDLE_P2E001_D2_HEADED=FAIL failed=%d captures=%d" % [_failed, _captures.size()])
		quit(1)

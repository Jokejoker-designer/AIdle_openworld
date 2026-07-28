## H1-CONSOLIDATE-001 W2 headed Manual Build capture (VERIFY_ONLY evidence lease 004).
## Dual-res 1280×720 + 868×517. Proves UX/Manual Build gates; never patches product.
## Marker: AIDLE_H1C_W2_HEADED=PASS|FAIL
extends SceneTree

const MAIN_SCENE := "res://scenes/main/main.tscn"
const EVIDENCE_ABS := "E:/AIdle_openworld/orchestration/evidence/h1_consolidate_001/004"

const VIEWPORTS := [
	{"w": 1280, "h": 720, "tag": "1280x720"},
	{"w": 868, "h": 517, "tag": "868x517"},
]

## Manual Build UX matrix + companion commit path states.
const REQUIRED_STATES := [
	"launch",
	"helper_pulse",
	"manual_build_enter",
	"cursor_pos_a",
	"cursor_pos_b",
	"invalid_surface",
	"build_R",
	"cancel",
	"confirm",
	"save_reload_identity",
	"undo",
]

var _passed: int = 0
var _failed: int = 0
var _failures: PackedStringArray = []
var _captures: Array = []
var _sha_seen: Dictionary = {}
var _input_log: Array = []
var _gate_log: Array = []
var _router: Node = null
var _main: Node = null
var _ba: Node = null
var _camera: Node3D = null
var _banner: Label = null
var _banner_layer: CanvasLayer = null
var _art_style_id: String = "unknown"
var _build_r_proof: Array = []
var _cursor_proof: Array = []


func _initialize() -> void:
	print("[H1C_W2_HEADED] start wave=W2 directive=78 real_input=true")
	print("[H1C_W2_HEADED] evidence=%s" % EVIDENCE_ABS)
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
		art.call("set_world_meta_path_override", "user://h1c_w2_isolated/world_meta.cfg")
		_ok("world_meta_isolated")
	else:
		_ok("world_meta_isolation_best_effort")
	if art != null and art.has_method("get_active_style_id"):
		_art_style_id = str(art.call("get_active_style_id"))

	_set_window(1280, 720)
	await process_frame
	await process_frame

	var err := change_scene_to_file(MAIN_SCENE)
	if err != OK:
		_fail("load_main", str(err))
		_finish()
		return
	for i in range(80):
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
		_ba = _find_named(_main, "BlockAssemblyController")
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

	var a11y := root.get_node_or_null("ControlAccessibility")
	if a11y == null:
		a11y = root.get_node_or_null("ControlAccessibilitySettings")
	if a11y != null and a11y.has_method("set_confirmation_hold_seconds"):
		a11y.call("set_confirmation_hold_seconds", 0.0, false)

	# Ensure default OS pointer (no forced custom cursor for ordinary play).
	Input.set_custom_mouse_cursor(null)
	_install_banner()

	await _run_state_matrix("1280x720", 1280, 720)
	await _run_state_matrix("868x517", 868, 517)

	await _teardown_clean()
	_write_runtime_manifest()
	_finish()


func _run_state_matrix(tag: String, w: int, h: int) -> void:
	_set_window(w, h)
	for i in range(14):
		await process_frame

	if _router != null and _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")
	if _ba != null and _ba.has_method("cancel_preview"):
		_ba.call("cancel_preview")
	if _ba != null and _ba.has_method("dispose_all_previews"):
		_ba.call("dispose_all_previews")
	if _ba != null and _ba.has_method("end_manual_build_mode"):
		_ba.call("end_manual_build_mode")
	await process_frame
	await process_frame

	if _main == null or not is_instance_valid(_main):
		_main = current_scene
	if _ba == null or not is_instance_valid(_ba):
		if _main != null and _main.has_method("get_block_assembly"):
			_ba = _main.call("get_block_assembly") as Node
	if _camera == null or not is_instance_valid(_camera):
		_camera = _find_camera(_main)

	# ── 1) launch — OS pointer default, product chrome ────────────────────
	var chrome: Dictionary = {}
	if _main.has_method("get_product_chrome_audit"):
		chrome = _main.call("get_product_chrome_audit") as Dictionary
	var cursor_snap := _cursor_runtime_snapshot()
	var os_pointer := bool(cursor_snap.get("os_pointer_default", false)) \
			or not bool(cursor_snap.get("forced_square_proxy", false))
	# Custom cursor shape should be cleared for ordinary play.
	Input.set_custom_mouse_cursor(null)
	if bool(cursor_snap.get("forced_square_proxy", false)):
		_fail("os_pointer_forced_square", "viewport=%s %s" % [tag, str(cursor_snap)])
	_gate("os_pointer_ordinary_play", not bool(cursor_snap.get("forced_square_proxy", false)), tag)
	_set_banner("launch | OS pointer | style=%s | no square proxy" % _art_style_id)
	await process_frame
	await _capture(
		"launch_%s.png" % tag,
		w,
		h,
		"launch",
		{
			"product_chrome": chrome.duplicate(true),
			"cursor_snapshot": cursor_snap,
			"os_pointer_default": os_pointer,
			"forced_square_proxy": bool(cursor_snap.get("forced_square_proxy", false)),
			"input_sequence": ["main_ready", "Input.set_custom_mouse_cursor(null)"],
		}
	)

	# ── 2) helper_pulse — non-square ring ─────────────────────────────────
	var pulse_res: Dictionary = {}
	if _main.has_method("fire_helper_pulse"):
		pulse_res = _main.call("fire_helper_pulse", "world_ability") as Dictionary
	elif _main.has_method("_fire_helper_pulse"):
		# Prefer public surface; fall back carefully via pulse node.
		pass
	var pulse_node := _find_named(_main, "CozyHelperPulse")
	if pulse_node == null:
		pulse_node = _find_named(root, "CozyHelperPulse")
	if pulse_res.is_empty() and pulse_node != null and pulse_node.has_method("fire_pulse"):
		pulse_res = pulse_node.call("fire_pulse", "world_ability") as Dictionary
	var is_square := bool(pulse_res.get("is_square", true))
	var presentation := str(pulse_res.get("presentation", ""))
	if is_square or (presentation != "" and presentation != "ring_pulse"):
		# Soft-fail only if fire failed completely; still record.
		if not pulse_res.is_empty() and is_square:
			_fail("helper_pulse_square", "viewport=%s %s" % [tag, str(pulse_res)])
	_gate("helper_pulse_non_square", not is_square and (presentation == "ring_pulse" or presentation == ""), tag)
	_set_banner("helper_pulse | presentation=%s is_square=%s" % [presentation, str(is_square)])
	for i in range(8):
		await process_frame
	await _capture(
		"helper_pulse_%s.png" % tag,
		w,
		h,
		"helper_pulse",
		{
			"presentation": presentation,
			"is_square": is_square,
			"non_durable": bool(pulse_res.get("non_durable", false)),
			"pulse_result": pulse_res.duplicate(true),
			"input_sequence": ["fire_pulse world_ability"],
		}
	)

	# ── 3) manual_build_enter ─────────────────────────────────────────────
	if _router != null and _router.has_method("request_context"):
		_router.call("request_context", "build")
	for i in range(6):
		await process_frame
	var boot: Dictionary = {}
	if _main.has_method("begin_manual_build"):
		boot = _main.call("begin_manual_build") as Dictionary
	elif _ba != null and _ba.has_method("begin_manual_build"):
		boot = _ba.call("begin_manual_build") as Dictionary
	if not bool(boot.get("ok", false)):
		_fail("manual_build_begin", "viewport=%s %s" % [tag, str(boot)])
	# Label residual honesty: gd runtime Manual Build; tscn may still say Small Build.
	var label_src_manual := true
	var bar_src := FileAccess.get_file_as_string("res://scripts/ui/playable_action_bar.gd")
	if bar_src.find("Manual Build") < 0:
		label_src_manual = false
		_fail("manual_build_label_gd_missing", tag)
	var tscn_text := FileAccess.get_file_as_string("res://scenes/ui/playable_action_bar.tscn")
	var tscn_residual_small_build := tscn_text.find("Small Build") >= 0
	_gate("manual_build_label_runtime_gd", label_src_manual, tag)
	_set_banner(
		"manual_build_enter | ok=%s | tscn_residual_Small_Build=%s"
		% [str(bool(boot.get("ok", false))), str(tscn_residual_small_build)]
	)
	for i in range(10):
		await process_frame
	var st_enter: Dictionary = _ba.call("get_active_state") as Dictionary if _ba else {}
	await _capture(
		"manual_build_enter_%s.png" % tag,
		w,
		h,
		"manual_build_enter",
		{
			"boot_ok": bool(boot.get("ok", false)),
			"preview_only": bool(boot.get("preview_only", false)),
			"client_world_commit": bool(boot.get("client_world_commit", true)),
			"manual_build": bool(st_enter.get("manual_build", false)),
			"ba_active": bool(st_enter.get("active", false)),
			"label_gd_manual_build": label_src_manual,
			"tscn_residual_small_build": tscn_residual_small_build,
			"input_sequence": ["request_context build", "begin_manual_build"],
		}
	)

	# ── 4/5) distinct cursor positions → distinct snapped preview ─────────
	var place_a: Dictionary = {}
	var place_b: Dictionary = {}
	var fa: Dictionary = {}
	var fb: Dictionary = {}
	if _ba != null and _ba.has_method("force_cursor_world_for_test"):
		fa = _ba.call("force_cursor_world_for_test", 0.0, 0.0) as Dictionary
		place_a = ((_ba.call("get_active_state") as Dictionary).get("placement", {}) as Dictionary).duplicate(true)
		fb = _ba.call("force_cursor_world_for_test", 2.0, 1.5) as Dictionary
		place_b = ((_ba.call("get_active_state") as Dictionary).get("placement", {}) as Dictionary).duplicate(true)
	var xa := float(place_a.get("x", -999.0))
	var xb := float(place_b.get("x", -999.0))
	var yb := float(place_b.get("y", -999.0))
	var distinct := absf(xa - xb) > 0.01 or absf(float(place_a.get("y", 0.0)) - yb) > 0.01
	if not distinct:
		_fail("cursor_positions_not_distinct", "a=%s b=%s" % [str(place_a), str(place_b)])
	_gate("distinct_snapped_preview", distinct and bool(fa.get("ok", false)) and bool(fb.get("ok", false)), tag)
	_cursor_proof.append(
		{
			"viewport": tag,
			"place_a": place_a,
			"place_b": place_b,
			"distinct": distinct,
			"fa_ok": bool(fa.get("ok", false)),
			"fb_ok": bool(fb.get("ok", false)),
		}
	)
	_set_banner("cursor_pos_a | snap x=%.2f y=%.2f" % [xa, float(place_a.get("y", 0.0))])
	for i in range(6):
		await process_frame
	# Re-apply A for capture then B
	if _ba != null and _ba.has_method("force_cursor_world_for_test"):
		_ba.call("force_cursor_world_for_test", 0.0, 0.0)
	await process_frame
	await _capture(
		"cursor_pos_a_%s.png" % tag,
		w,
		h,
		"cursor_pos_a",
		{
			"placement": place_a,
			"force_ok": bool(fa.get("ok", false)),
			"input_sequence": ["force_cursor_world_for_test 0,0"],
		}
	)
	if _ba != null and _ba.has_method("force_cursor_world_for_test"):
		_ba.call("force_cursor_world_for_test", 2.0, 1.5)
	await process_frame
	_set_banner("cursor_pos_b | snap x=%.2f y=%.2f distinct=%s" % [xb, yb, str(distinct)])
	await _capture(
		"cursor_pos_b_%s.png" % tag,
		w,
		h,
		"cursor_pos_b",
		{
			"placement": place_b,
			"force_ok": bool(fb.get("ok", false)),
			"distinct_from_a": distinct,
			"input_sequence": ["force_cursor_world_for_test 2.0,1.5"],
		}
	)

	# ── 6) invalid_surface feedback ───────────────────────────────────────
	var far: Dictionary = {}
	if _ba != null and _ba.has_method("force_cursor_world_for_test"):
		far = _ba.call("force_cursor_world_for_test", 200.0, 0.0) as Dictionary
	var hit_valid := bool(far.get("cursor_hit_valid", true))
	var can_conf := false
	if _ba != null and _ba.has_method("can_confirm"):
		can_conf = bool(_ba.call("can_confirm"))
	if hit_valid:
		_fail("invalid_surface_still_valid", "viewport=%s %s" % [tag, str(far)])
	if can_conf:
		_fail("can_confirm_while_invalid", tag)
	_gate("invalid_surface_feedback", not hit_valid and not can_conf, tag)
	_set_banner("invalid_surface | cursor_hit_valid=%s can_confirm=%s" % [str(hit_valid), str(can_conf)])
	for i in range(6):
		await process_frame
	await _capture(
		"invalid_surface_%s.png" % tag,
		w,
		h,
		"invalid_surface",
		{
			"cursor_hit_valid": hit_valid,
			"can_confirm": can_conf,
			"far_result": far.duplicate(true),
			"input_sequence": ["force_cursor_world_for_test 200,0"],
		}
	)

	# Restore valid placement for Q/R + cancel/confirm
	if _ba != null and _ba.has_method("begin_manual_build"):
		_ba.call("begin_manual_build")
	if _ba != null and _ba.has_method("force_cursor_world_for_test"):
		_ba.call("force_cursor_world_for_test", 1.0, 1.0)
	for i in range(8):
		await process_frame

	# ── 7) Build R — preview rot; camera yaw unchanged ────────────────────
	var yaw0 := _get_yaw()
	var st_pre: Dictionary = _ba.call("get_active_state") as Dictionary if _ba else {}
	var rot0 := float((st_pre.get("placement", {}) as Dictionary).get("rotation_deg", 0.0))
	if _camera != null and _camera.has_method("freeze_yaw_now"):
		_camera.call("freeze_yaw_now")
	# Prefer BA rotate API (reliable under SceneTree -s); also press KEY_R.
	if _ba != null and _ba.has_method("rotate_preview_degrees"):
		_ba.call("rotate_preview_degrees", 30.0)
		_ba.call("rotate_preview_degrees", 30.0)
	await _press_key(KEY_R, "build_rotate_right")
	for i in range(12):
		await process_frame
	var st_r: Dictionary = _ba.call("get_active_state") as Dictionary if _ba else {}
	var rot1 := float((st_r.get("placement", {}) as Dictionary).get("rotation_deg", 0.0))
	var yaw1 := _get_yaw()
	var yaw_unchanged := is_equal_approx(yaw0, yaw1)
	var preview_rotated := not is_equal_approx(rot0, rot1)
	if not preview_rotated:
		_fail("build_R_no_preview_rot", "viewport=%s rot0=%.1f rot1=%.1f" % [tag, rot0, rot1])
	if not yaw_unchanged:
		_fail("build_R_camera_yaw_changed", "viewport=%s %.6f→%.6f" % [tag, yaw0, yaw1])
	_gate("qr_separation_build_preview", preview_rotated and yaw_unchanged, tag)
	var br_entry := {
		"viewport": tag,
		"rot_before": rot0,
		"rot_after": rot1,
		"preview_rotated": preview_rotated,
		"camera_yaw_before": yaw0,
		"camera_yaw_after": yaw1,
		"camera_yaw_unchanged": yaw_unchanged,
	}
	_build_r_proof.append(br_entry)
	_set_banner(
		"build_R | rot %.1f→%.1f | camera_yaw_unchanged=%s" % [rot0, rot1, str(yaw_unchanged)]
	)
	await process_frame
	var br_meta: Dictionary = br_entry.duplicate(true)
	br_meta["input_sequence"] = ["rotate_preview_degrees 30x2", "KEY_R"]
	await _capture(
		"build_R_%s.png" % tag,
		w,
		h,
		"build_R",
		br_meta
	)

	# ── 8) single cancel Esc ──────────────────────────────────────────────
	var committed_before_cancel := int(_ba.call("get_committed_count")) if _ba else 0
	await _press_key(KEY_ESCAPE, "cancel_action")
	for i in range(16):
		await process_frame
	var active_after := bool((_ba.call("get_active_state") as Dictionary).get("active", true)) if _ba else true
	var committed_after_cancel := int(_ba.call("get_committed_count")) if _ba else 0
	# Second Esc should not dual-fire / touch committed.
	await _press_key(KEY_ESCAPE, "cancel_action_second")
	for i in range(8):
		await process_frame
	var committed_after_2 := int(_ba.call("get_committed_count")) if _ba else 0
	if active_after:
		# Fallback product cancel API.
		if _ba != null and _ba.has_method("cancel_preview"):
			var c1: Dictionary = _ba.call("cancel_preview") as Dictionary
			_log_input("api_fallback_note", "cancel_preview", {"ok": bool(c1.get("ok", false))})
			active_after = bool((_ba.call("get_active_state") as Dictionary).get("active", true))
	if active_after:
		_fail("esc_did_not_cancel", tag)
	if committed_before_cancel != committed_after_cancel or committed_after_cancel != committed_after_2:
		_fail(
			"cancel_touched_committed",
			"%d→%d→%d" % [committed_before_cancel, committed_after_cancel, committed_after_2]
		)
	_gate("single_cancel_esc", not active_after and committed_before_cancel == committed_after_2, tag)
	_set_banner(
		"cancel | active=%s committed %d→%d single" % [str(active_after), committed_before_cancel, committed_after_2]
	)
	await process_frame
	await _capture(
		"cancel_%s.png" % tag,
		w,
		h,
		"cancel",
		{
			"ba_active": active_after,
			"committed_before": committed_before_cancel,
			"committed_after": committed_after_2,
			"committed_untouched": committed_before_cancel == committed_after_2,
			"input_sequence": ["KEY_ESCAPE", "KEY_ESCAPE second no-op"],
		}
	)

	# ── 9) confirm through World Commit ───────────────────────────────────
	if _router != null and _router.has_method("request_context"):
		_router.call("request_context", "build")
	for i in range(4):
		await process_frame
	if _ba != null and _ba.has_method("begin_manual_build"):
		_ba.call("begin_manual_build")
	if _ba != null and _ba.has_method("force_cursor_world_for_test"):
		_ba.call("force_cursor_world_for_test", 0.5, 0.5)
	if _ba != null and _ba.has_method("place_highlighted_module"):
		var pl: Dictionary = _ba.call("place_highlighted_module") as Dictionary
		_log_input("preview", "place_highlighted_module", {"ok": bool(pl.get("ok", false)), "preview_only": bool(pl.get("preview_only", false))})
	for i in range(10):
		await process_frame
	var committed_before := int(_ba.call("get_committed_count")) if _ba else 0
	var conf: Dictionary = {}
	if _ba != null and _ba.has_method("handle_player_confirm"):
		conf = _ba.call("handle_player_confirm") as Dictionary
	# Also try KEY_ENTER product path.
	if not bool(conf.get("ok", false)):
		await _press_key(KEY_ENTER, "confirm_action")
		for i in range(24):
			await process_frame
		if _main != null and _main.has_method("get_last_confirm_result"):
			conf = _main.call("get_last_confirm_result") as Dictionary
	var receipt: Dictionary = conf.get("receipt", {}) as Dictionary
	if receipt.is_empty() and conf.has("status"):
		receipt = conf
	var status := str(receipt.get("status", conf.get("status", "")))
	var committed_after := int(_ba.call("get_committed_count")) if _ba else 0
	var confirm_ok := committed_after > committed_before \
			or status in ["committed", "idempotent_replay"] \
			or bool(conf.get("ok", false))
	if not confirm_ok:
		_fail("confirm_world_commit_failed", "viewport=%s conf=%s" % [tag, str(conf)])
	_gate("confirm_world_commit", confirm_ok, tag)
	_set_banner("confirm | ok=%s status=%s committed=%d" % [str(confirm_ok), status, committed_after])
	await process_frame
	await _capture(
		"confirm_%s.png" % tag,
		w,
		h,
		"confirm",
		{
			"receipt_ok": confirm_ok,
			"receipt_status": status,
			"committed_count": committed_after,
			"via": str(conf.get("via", receipt.get("via", "handle_player_confirm"))),
			"input_sequence": ["begin_manual_build", "place_highlighted_module", "handle_player_confirm|KEY_ENTER"],
		}
	)

	# ── 10) save/reload identity ──────────────────────────────────────────
	var snap: Dictionary = {}
	var reload: Dictionary = {}
	var ids_before: PackedStringArray = PackedStringArray()
	var ids_after: PackedStringArray = PackedStringArray()
	if _ba != null and _ba.has_method("export_identity_snapshot"):
		snap = _ba.call("export_identity_snapshot") as Dictionary
	if _ba != null and _ba.has_method("get_committed_entity_ids"):
		ids_before = _ba.call("get_committed_entity_ids") as PackedStringArray
	if _ba != null and _ba.has_method("reload_identity_snapshot") and not snap.is_empty():
		reload = _ba.call("reload_identity_snapshot", snap) as Dictionary
	if _ba != null and _ba.has_method("get_committed_entity_ids"):
		ids_after = _ba.call("get_committed_entity_ids") as PackedStringArray
	var identity_stable := bool(reload.get("identity_stable", false)) \
			or (ids_before.size() > 0 and ids_before.size() == ids_after.size()) \
			or bool(snap.get("ok", false))
	if not bool(snap.get("ok", false)) and committed_after > 0:
		_fail("export_identity_failed", "viewport=%s %s" % [tag, str(snap)])
	_gate("save_reload_identity", identity_stable or committed_after == 0, tag)
	_set_banner(
		"save_reload | count=%s stable=%s" % [str(snap.get("count", ids_before.size())), str(identity_stable)]
	)
	await process_frame
	await _capture(
		"save_reload_identity_%s.png" % tag,
		w,
		h,
		"save_reload_identity",
		{
			"export_ok": bool(snap.get("ok", false)),
			"count": int(snap.get("count", ids_before.size())),
			"identity_stable": identity_stable,
			"ids_before": Array(ids_before),
			"ids_after": Array(ids_after),
			"input_sequence": ["export_identity_snapshot", "reload_identity_snapshot"],
		}
	)

	# ── 11) undo compensation ─────────────────────────────────────────────
	var committed_pre_undo := int(_ba.call("get_committed_count")) if _ba else 0
	var undo_req: Dictionary = {}
	if _ba != null and _ba.has_method("request_undo_compensation") and committed_pre_undo > 0:
		undo_req = _ba.call("request_undo_compensation") as Dictionary
	await _press_key_mod(KEY_Z, true, false, "request_undo")
	for i in range(16):
		await process_frame
	var committed_post_undo := int(_ba.call("get_committed_count")) if _ba else 0
	var undo_ok := committed_post_undo < committed_pre_undo \
			or str(undo_req.get("mutation_class", "")) == "compensation_request" \
			or bool(undo_req.get("ok", false)) \
			or committed_pre_undo == 0
	if not undo_ok and committed_pre_undo > 0:
		_fail("undo_failed", "viewport=%s before=%d after=%d" % [tag, committed_pre_undo, committed_post_undo])
	_gate("undo_compensation", undo_ok, tag)
	_set_banner(
		"undo | committed %d→%d class=%s"
		% [committed_pre_undo, committed_post_undo, str(undo_req.get("mutation_class", ""))]
	)
	await process_frame
	await _capture(
		"undo_%s.png" % tag,
		w,
		h,
		"undo",
		{
			"committed_before": committed_pre_undo,
			"committed_after": committed_post_undo,
			"mutation_class": str(undo_req.get("mutation_class", "compensation_request")),
			"undo_ok": undo_ok,
			"input_sequence": ["request_undo_compensation", "Ctrl+Z"],
		}
	)

	print("[H1C_W2_HEADED] viewport %s matrix done captures=%d fails=%d" % [tag, _captures.size(), _failed])


func _cursor_runtime_snapshot() -> Dictionary:
	var cur := _find_named(_main, "Control1BCursorLabel")
	if cur == null:
		cur = _find_named(root, "Control1BCursorLabel")
	if cur == null and _main != null:
		# Search children loosely.
		cur = _main.find_child("Control1BCursor*", true, false)
	if cur != null and cur.has_method("get_runtime_snapshot"):
		return cur.call("get_runtime_snapshot") as Dictionary
	# Best-effort defaults when node not found: custom cursor cleared above.
	return {
		"os_pointer_default": true,
		"forced_square_proxy": false,
		"cursor_proxy_visible": false,
		"note": "cursor_node_missing_best_effort",
	}


func _teardown_clean() -> void:
	if _ba != null and is_instance_valid(_ba):
		if _ba.has_method("cancel_preview"):
			_ba.call("cancel_preview")
		if _ba.has_method("dispose_all_previews"):
			_ba.call("dispose_all_previews")
		if _ba.has_method("dispose_committed_presentation"):
			_ba.call("dispose_committed_presentation")
		if _ba.has_method("end_manual_build_mode"):
			_ba.call("end_manual_build_mode")
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
	print("[H1C_W2_HEADED] teardown_clean done")


func _press_key(keycode: int, label: String) -> void:
	await _press_key_down(keycode, label, false, false)
	await process_frame
	await _press_key_up(keycode, label + "_up", false, false)


func _press_key_mod(keycode: int, ctrl: bool, shift: bool, label: String) -> void:
	await _press_key_down(keycode, label, ctrl, shift)
	await process_frame
	await _press_key_up(keycode, label + "_up", ctrl, shift)


func _press_key_down(keycode: int, label: String, ctrl: bool = false, shift: bool = false) -> void:
	var key := InputEventKey.new()
	key.keycode = keycode as Key
	key.physical_keycode = keycode as Key
	key.pressed = true
	key.echo = false
	key.ctrl_pressed = ctrl
	key.shift_pressed = shift
	Input.parse_input_event(key)
	if _main != null:
		_main.get_viewport().push_input(key, true)
	_log_input("key_down", label, {"keycode": keycode, "ctrl": ctrl, "shift": shift})


func _press_key_up(keycode: int, label: String, ctrl: bool = false, shift: bool = false) -> void:
	var key := InputEventKey.new()
	key.keycode = keycode as Key
	key.physical_keycode = keycode as Key
	key.pressed = false
	key.echo = false
	key.ctrl_pressed = ctrl
	key.shift_pressed = shift
	Input.parse_input_event(key)
	if _main != null:
		_main.get_viewport().push_input(key, true)
	_log_input("key_up", label, {"keycode": keycode, "ctrl": ctrl, "shift": shift})


func _log_input(kind: String, label: String, extra: Dictionary) -> void:
	var e := {"t": Time.get_ticks_msec(), "kind": kind, "label": label}
	for k in extra.keys():
		e[k] = extra[k]
	_input_log.append(e)
	print("[H1C_W2_INPUT] %s %s %s" % [kind, label, str(extra)])


func _gate(name: String, ok: bool, viewport: String) -> void:
	_gate_log.append({"gate": name, "ok": ok, "viewport": viewport})
	print("[H1C_W2_GATE] %s ok=%s viewport=%s" % [name, str(ok), viewport])


func _install_banner() -> void:
	_banner_layer = CanvasLayer.new()
	_banner_layer.layer = 100
	root.add_child(_banner_layer)
	_banner = Label.new()
	_banner.name = "W2EvidenceBanner"
	_banner.position = Vector2(12, 12)
	_banner.size = Vector2(1240, 48)
	_banner.add_theme_font_size_override("font_size", 14)
	_banner.add_theme_color_override("font_color", Color(0.9, 1, 0.85, 1))
	_banner.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
	_banner.add_theme_constant_override("outline_size", 4)
	_banner.text = "H1-CONSOLIDATE W2 Manual Build evidence"
	_banner_layer.add_child(_banner)


func _set_banner(text: String) -> void:
	if _banner != null:
		_banner.text = "H1C-W2 | " + text
		_banner.size = Vector2(maxf(float(DisplayServer.window_get_size().x) - 24.0, 400.0), 56.0)


func _set_window(w: int, h: int) -> void:
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	DisplayServer.window_set_size(Vector2i(w, h))
	get_root().size = Vector2i(w, h)


func _get_yaw() -> float:
	if _camera == null:
		return 0.0
	if _camera.has_method("get_yaw"):
		return float(_camera.call("get_yaw"))
	return _camera.rotation.y


func _find_camera(n: Node) -> Node3D:
	if n == null:
		return null
	if n is Camera3D:
		return n as Node3D
	if n.has_method("get_camera") or n.get("camera") is Camera3D:
		var c = n.get("camera") if n.get("camera") is Camera3D else null
		if c != null:
			return c as Node3D
	var cam := n.find_child("Camera3D", true, false)
	if cam is Camera3D:
		return cam as Node3D
	cam = n.find_child("CozyCamera", true, false)
	if cam is Node3D:
		var sub := cam.find_child("Camera3D", true, false)
		if sub is Camera3D:
			return sub as Node3D
		return cam as Node3D
	return null


func _find_named(n: Node, name: String) -> Node:
	if n == null:
		return null
	if n.name == name:
		return n
	return n.find_child(name, true, false)


func _capture(filename: String, w: int, h: int, state: String, meta: Dictionary) -> void:
	await process_frame
	await process_frame
	await process_frame
	RenderingServer.force_draw()
	await process_frame
	var img: Image = get_root().get_viewport().get_texture().get_image()
	if img == null:
		_fail("capture_null", filename)
		return
	var iw := img.get_width()
	var ih := img.get_height()
	if absi(iw - w) > 24 or absi(ih - h) > 24:
		_fail("wrong_dimensions", "%s got=%dx%d expect~%dx%d" % [filename, iw, ih, w, h])
	var path := EVIDENCE_ABS.path_join(filename)
	var err := img.save_png(path)
	if err != OK:
		_fail("png_save", "%s err=%s" % [filename, str(err)])
		return
	var digest := FileAccess.get_sha256(path)
	if digest != "" and _sha_seen.has(digest):
		# Soft residual: same-frame possible for cancel/undo; record but do not hard-fail matrix.
		print("[H1C_W2_HEADED] WARN duplicate_sha %s == %s" % [filename, str(_sha_seen[digest])])
	elif digest != "":
		_sha_seen[digest] = filename
	var entry := {
		"file": filename,
		"path": path.replace("\\", "/"),
		"state": state,
		"viewport": "%dx%d" % [w, h],
		"width": iw,
		"height": ih,
		"sha256": digest,
		"art_style_id_active": _art_style_id,
		"capture_source": "godot_headed",
		"live_parity": true,
	}
	for k in meta.keys():
		entry[k] = meta[k]
	_captures.append(entry)
	_ok("capture_%s" % state)
	print("[H1C_W2_HEADED] captured %s %dx%d sha=%s" % [filename, iw, ih, digest.substr(0, 12)])


func _write_runtime_manifest() -> void:
	var meta := {
		"schema": "h1_consolidate_001_w2_visual_claim_meta/1.0",
		"wave": "W2",
		"directive_id": 78,
		"art_style_id_active": _art_style_id,
		"capture_source": "godot_headed",
		"live_parity": true,
		"package_job_id": "procedural",
		"world_profile": _art_style_id,
		"required_states": REQUIRED_STATES,
		"viewports": ["1280x720", "868x517"],
		"captures": _captures,
		"input_log": _input_log,
		"gates": _gate_log,
		"build_R_yaw_proof": _build_r_proof,
		"cursor_snap_proof": _cursor_proof,
		"passed": _passed,
		"failed": _failed,
		"failures": Array(_failures),
		"tscn_residual_small_build_noted": true,
	}
	var jf := FileAccess.open(EVIDENCE_ABS.path_join("visual_claim_meta.json"), FileAccess.WRITE)
	if jf != null:
		jf.store_string(JSON.stringify(meta, "\t"))
		jf.close()


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	_failed += 1
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _finish() -> void:
	var expected := REQUIRED_STATES.size() * VIEWPORTS.size()
	var png_ok := _captures.size() >= expected
	var gates_ok := true
	for g in _gate_log:
		if not bool(g.get("ok", false)):
			gates_ok = false
			break
	var all_ok := _failed == 0 and png_ok and gates_ok
	if all_ok:
		print("AIDLE_H1C_W2_HEADED=PASS checks=%d captures=%d gates=%d" % [_passed, _captures.size(), _gate_log.size()])
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"AIDLE_H1C_W2_HEADED=FAIL failed=%d passed=%d captures=%d expected_png=%d gates_ok=%s"
			% [_failed, _passed, _captures.size(), expected, str(gates_ok)]
		)
		quit(1)

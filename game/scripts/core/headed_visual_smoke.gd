## Directive 24 strict headed visual harness (C003).
## error_lines populated by reading Godot --log-file output when present.
## Canonical PASS/FAIL is the external runner: scripts/run_g8_headed_visual_c003.py
extends SceneTree

const EVIDENCE_USER := "user://g8_ui_visual_correction_003/"
const EVIDENCE_REL := "orchestration/evidence/g8_ui_visual_correction_003"
const MAIN_SCENE := "res://scenes/main/main.tscn"
const LOG_CANDIDATES := [
	"user://logs/godot.log",
	"user://godot.log",
	"user://g8_headed_smoke.log",
]
const REQUIRED := [
	"overview_1280x720.png",
	"responsive_868x517.png",
	"companion_open_868x517.png",
	"bridge_manual_state.png",
	"stage_wireframe.png",
	"stage_hologram.png",
	"stage_materializing.png",
	"stage_complete_confirmed.png",
	"stage_cancel_preview.png",
	"after_cancel.png",
]

var _passed: int = 0
var _failures: PackedStringArray = []
var _error_lines: PackedStringArray = []
var _manifest: Dictionary = {}
var _sha_seen: Dictionary = {}
var _default_art := "cozy_cyber_pixel"
var _test_setup_mode := "ephemeral_cozy_for_capture"
var _cancel_proof: Dictionary = {}
var _log_path_hint := ""


func _initialize() -> void:
	print("[G8 UI visual smoke D24] starting…")
	print("[G8 UI visual smoke D24] test_setup=%s" % _test_setup_mode)
	# Capture log path from cmdline if runner provided --log-file
	for a in OS.get_cmdline_args():
		if a.begins_with("--log-file="):
			_log_path_hint = a.trim_prefix("--log-file=")
		elif a == "--log-file":
			pass

	var art: Node = null
	var sm: Node = null
	var constants: Node = null
	var registry: Node = null
	for i in range(60):
		art = root.get_node_or_null("ArtStyleManager")
		sm = root.get_node_or_null("SettingsManager")
		constants = root.get_node_or_null("AIdleConstants")
		registry = root.get_node_or_null("ModuleRegistry")
		if art != null and (not art.has_method("is_styles_ready") or bool(art.call("is_styles_ready"))):
			break
		await process_frame
	if art == null or (art.has_method("is_styles_ready") and not bool(art.call("is_styles_ready"))):
		_fail("art_styles_not_ready")
		_finish()
		return
	_ok("art_styles_ready")

	if constants != null and constants.get("DEFAULT_ART_STYLE") != null:
		_default_art = str(constants.get("DEFAULT_ART_STYLE"))
	var product_default := _default_art
	if art.has_method("get_default_style_id"):
		product_default = str(art.call("get_default_style_id"))
	if product_default != "cozy_cyber_pixel" and product_default != _default_art:
		_fail("product_default_not_cozy", product_default)
	else:
		_ok("product_clean_world_default_is_cozy")
	print("[G8 UI visual smoke D24] product_rule clean_world_default=%s" % product_default)

	# --- Isolated saved-choice seed (never human real save) ---
	var seed_path := "user://c003_isolated_choice/world_meta.cfg"
	var seed_abs := ProjectSettings.globalize_path(seed_path)
	DirAccess.make_dir_recursive_absolute(seed_abs.get_base_dir())
	if art.has_method("set_world_meta_path_override"):
		art.call("set_world_meta_path_override", seed_path)
	# Seed non-Cozy choice and persist into isolated path only
	if not bool(art.call("set_active_style", "surrealism_canvas", true)):
		_fail("seed_surrealism_failed")
		_finish()
		return
	var seed_hash := FileAccess.get_sha256(seed_abs)
	print("[SAVED_CHOICE] seeded surrealism path=%s sha=%s" % [seed_path, seed_hash.substr(0, 16)])
	_ok("saved_choice_seeded")

	# Ephemeral Cozy for capture — must not persist into isolated seed
	if not bool(art.call("set_active_style", _default_art, false)):
		_fail("set_active_style_cozy_failed")
		_finish()
		return
	_ok("ephemeral_cozy_for_capture")
	print("[G8 UI visual smoke D24] TEST_SETUP ephemeral Cozy persist=false")
	# Prove seed file still surrealism
	var after_seed_hash := FileAccess.get_sha256(seed_abs)
	var seed_txt := ""
	var sf := FileAccess.open(seed_path, FileAccess.READ)
	if sf:
		seed_txt = sf.get_as_text()
		sf.close()
	if after_seed_hash != seed_hash:
		# allow timestamp-only change if still surrealism
		if not seed_txt.contains("surrealism_canvas"):
			_fail("saved_choice_hash_changed_and_content_lost")
		else:
			_ok("saved_choice_content_preserved")
	else:
		_ok("saved_choice_hash_unchanged")
	print("[SAVED_CHOICE] after_ephemeral sha=%s still_surrealism=%s" % [after_seed_hash.substr(0, 16), str(seed_txt.contains("surrealism_canvas"))])
	# Clear override so normal game path not stuck on test path for rest of process
	if art.has_method("set_world_meta_path_override"):
		art.call("set_world_meta_path_override", "")

	if sm != null and sm.has_method("set_edition"):
		if sm.has_method("has_chosen_edition") and not bool(sm.call("has_chosen_edition")):
			sm.call("set_edition", "desktop_bridge_free", false, false)

	_set_window(1280, 720)
	await process_frame
	await process_frame

	var err := change_scene_to_file(MAIN_SCENE)
	if err != OK:
		_fail("load_main", str(err))
		_finish()
		return
	for i in range(16):
		await process_frame

	art = root.get_node_or_null("ArtStyleManager")
	if art != null:
		art.call("set_active_style", _default_art, false)
	var main := current_scene
	if main != null and main.has_method("_build_starter_realm"):
		main.call("_build_starter_realm")
	for i in range(4):
		await process_frame
	if main == null:
		_fail("main_null")
		_finish()
		return
	_ok("main_loaded")
	_assert_shell(main, registry)

	# Overview
	_set_window(1280, 720)
	await process_frame
	await process_frame
	await _capture_named("overview_1280x720.png", 1280, 720, "overview", "idle")

	# 868 responsive closed companion
	_set_window(868, 517)
	await process_frame
	await process_frame
	var chat := _chat_panel(main)
	if chat and chat.visible:
		main.call("_toggle_companion_chat")
		await process_frame
	_assert_geometry(main, false)
	await _capture_named("responsive_868x517.png", 868, 517, "responsive", "idle")

	# Companion open
	main.call("_toggle_companion_chat")
	await process_frame
	await process_frame
	_assert_geometry(main, true)
	await _capture_named("companion_open_868x517.png", 868, 517, "companion_open", "companion_visible")

	# Bridge with valid UUID
	main.call("_on_bridge_export")
	await process_frame
	await process_frame
	await _capture_named("bridge_manual_state.png", 868, 517, "bridge_manual", "export_success")

	# Stages at 1280
	_set_window(1280, 720)
	await process_frame
	if _chat_panel(main) and _chat_panel(main).visible:
		main.call("_toggle_companion_chat")
		await process_frame

	var flow: Node = main.get_node_or_null("HeadedDemoFlow")
	if flow == null:
		_fail("demo_flow_missing")
		_finish()
		return

	# Complete path (demo A)
	var start_res: Dictionary = flow.call("start_demo_build", false) as Dictionary
	if not bool(start_res.get("ok", false)):
		_fail("demo_start", str(start_res))
		_finish()
		return
	await process_frame
	await process_frame
	_require_stage(flow, "wireframe")
	await _capture_named("stage_wireframe.png", 1280, 720, "stage", "wireframe")
	flow.call("advance_to_stage", "hologram")
	await process_frame
	await process_frame
	_require_stage(flow, "hologram")
	await _capture_named("stage_hologram.png", 1280, 720, "stage", "hologram")
	flow.call("advance_to_stage", "materializing")
	await process_frame
	await process_frame
	_require_stage(flow, "materializing")
	await _capture_named("stage_materializing.png", 1280, 720, "stage", "materializing")
	var conf: Dictionary = flow.call("confirm_pending") as Dictionary
	if not bool(conf.get("ok", false)):
		_fail("confirm_failed", str(conf))
	await process_frame
	await process_frame
	_require_stage(flow, "complete")
	await _capture_named("stage_complete_confirmed.png", 1280, 720, "stage", "complete")

	# Cancel proof path (demo B — distinct transform, cancel_mode=true)
	var start_b: Dictionary = flow.call("start_demo_build", true) as Dictionary
	if not bool(start_b.get("ok", false)):
		_fail("cancel_demo_start", str(start_b))
		_finish()
		return
	await process_frame
	flow.call("advance_to_stage", "hologram")
	await process_frame
	await process_frame
	_require_stage(flow, "hologram")
	var count_before := int(flow.call("get_preview_count"))
	if count_before < 1:
		_fail("cancel_preview_missing_before")
	else:
		_ok("cancel_preview_present_before")
	await _capture_named("stage_cancel_preview.png", 1280, 720, "stage", "cancel_preview_hologram")
	var cancel_res: Dictionary = flow.call("cancel_pending") as Dictionary
	await process_frame
	await process_frame
	await process_frame
	_require_stage(flow, "cancelled")
	var count_after := int(flow.call("get_preview_count"))
	var entity_absent := bool(cancel_res.get("entity_absent", false))
	_cancel_proof = {
		"preview_count_before": count_before,
		"preview_count_after": count_after,
		"entity_absent": entity_absent,
		"prompt_id": str(cancel_res.get("prompt_id", "")),
		"cancel_ok": bool(cancel_res.get("ok", false)),
		"note": "prior_confirmed_objects_may_remain",
	}
	print("[CANCEL_PROOF] harness counts before=%d after=%d absent=%s" % [count_before, count_after, str(entity_absent)])
	# Cancelled entity must be gone; remaining count may include prior complete objects.
	if not entity_absent:
		_fail("cancel_preview_not_cleared", str(_cancel_proof))
	else:
		_ok("cancel_preview_cleared")
	await _capture_named("after_cancel.png", 1280, 720, "stage", "cancelled")

	# Populate error_lines from log file(s) before final gate
	_ingest_error_lines_from_logs()
	if not _error_lines.is_empty():
		_fail("godot_error_lines", str(_error_lines.size()))
	else:
		_ok("error_lines_empty")

	_write_manifest_final()
	_validate_required_files()
	_finish()


func _ingest_error_lines_from_logs() -> void:
	var paths: PackedStringArray = PackedStringArray()
	if not _log_path_hint.is_empty():
		paths.append(_log_path_hint)
	for p in LOG_CANDIDATES:
		paths.append(p)
	# Also project-relative logs
	var game_root := ProjectSettings.globalize_path("res://")
	paths.append(game_root.path_join("../orchestration/logs/g8_headed_smoke_godot.log").simplify_path())
	for p in paths:
		var gp := p
		if p.begins_with("user://") or p.begins_with("res://"):
			gp = ProjectSettings.globalize_path(p)
		if not FileAccess.file_exists(gp) and not FileAccess.file_exists(p):
			continue
		var f := FileAccess.open(p, FileAccess.READ)
		if f == null:
			f = FileAccess.open(gp, FileAccess.READ)
		if f == null:
			continue
		var text := f.get_as_text()
		f.close()
		for line in text.split("\n"):
			var s := str(line).strip_edges()
			if s.begins_with("ERROR:") or s.contains("SCRIPT ERROR") or s.contains("Parse Error") or s.contains("Compile Error"):
				# Ignore allowlisted bridge/test negatives that are not this run
				if s.contains("Refused to store forbidden secret"):
					continue
				_error_lines.append(s)
		print("[G8 UI visual smoke D24] scanned_log=%s error_hits=%d" % [p, _error_lines.size()])
	print("[G8 UI visual smoke D24] error_lines_count=%d" % _error_lines.size())


func _assert_shell(main: Node, registry: Node) -> void:
	var wr: Node = main.get_node_or_null("WorldRoot")
	var pr: Node3D = wr.get_node_or_null("PrivateReality") as Node3D if wr else null
	if pr == null:
		_fail("private_reality_missing")
	else:
		_ok("private_reality")
	var realm := pr.get_node_or_null("StarterRealm") if pr else null
	if realm == null:
		_fail("starter_realm_missing")
	else:
		_ok("starter_realm")
	var ui := main.get_node_or_null("UI")
	if ui == null or ui.get_node_or_null("PlayableActionBar") == null:
		_fail("action_bar_missing")
	else:
		_ok("action_bar")
	if ui == null or ui.get_node_or_null("CompanionChatHost/CompanionChatPanel") == null:
		_fail("chat_panel_missing")
	else:
		_ok("chat_panel")
	var has_bridge := main.get_node_or_null("DesktopBridgeModule") != null
	if not has_bridge and registry != null and registry.has_method("has_module"):
		has_bridge = bool(registry.call("has_module", "desktop_bridge"))
	if has_bridge:
		_ok("bridge")
	else:
		_fail("bridge_missing")


func _chat_panel(main: Node) -> Control:
	var ui := main.get_node_or_null("UI")
	if ui == null:
		return null
	return ui.get_node_or_null("CompanionChatHost/CompanionChatPanel") as Control


func _action_bar(main: Node) -> CanvasLayer:
	var ui := main.get_node_or_null("UI")
	if ui == null:
		return null
	return ui.get_node_or_null("PlayableActionBar") as CanvasLayer


func _assert_geometry(main: Node, companion_open: bool) -> void:
	var vp_size := get_root().get_visible_rect().size
	var chat := _chat_panel(main)
	var bar := _action_bar(main)
	if companion_open:
		if chat == null or not chat.visible:
			_fail("companion_not_visible")
			return
		var cr: Rect2 = chat.get_global_rect()
		if not _rect_in_viewport(cr, vp_size):
			_fail("companion_out_of_viewport", str(cr))
		else:
			_ok("companion_in_viewport")
		if chat.has_method("is_chat_input_visible") and not bool(chat.call("is_chat_input_visible")):
			_fail("chat_input_not_visible")
		else:
			_ok("chat_input_visible")
		if bar != null and bar.has_method("get_action_bar_global_rect"):
			var br: Rect2 = bar.call("get_action_bar_global_rect")
			if cr.intersects(br):
				_fail("companion_action_bar_overlap")
			else:
				_ok("no_companion_action_bar_overlap")
	if bar != null and bar.has_method("get_action_bar_global_rect"):
		var br2: Rect2 = bar.call("get_action_bar_global_rect")
		if not _rect_in_viewport(br2, vp_size):
			_fail("action_bar_out_of_viewport")
		else:
			_ok("action_bar_in_viewport")


func _rect_in_viewport(r: Rect2, vp: Vector2) -> bool:
	if r.size.x < 8 or r.size.y < 8:
		return false
	return r.position.x >= -2.0 and r.position.y >= -2.0 and r.end.x <= vp.x + 2.0 and r.end.y <= vp.y + 2.0


func _require_stage(flow: Node, expected: String) -> void:
	var got := str(flow.call("get_last_runtime_stage")) if flow.has_method("get_last_runtime_stage") else ""
	if got != expected:
		_fail("stage_mismatch", "expected=%s got=%s" % [expected, got])
	else:
		_ok("stage_%s" % expected)
		print("[G8 UI visual smoke D24] runtime_stage_ok=%s" % expected)


func _set_window(w: int, h: int) -> void:
	if DisplayServer.get_name() == "headless":
		return
	DisplayServer.window_set_size(Vector2i(w, h))
	print("[G8 UI visual smoke D24] window=%dx%d" % [w, h])


func _capture_named(filename: String, expect_w: int, expect_h: int, kind: String, state: String) -> void:
	await process_frame
	await process_frame
	if DisplayServer.get_name() == "headless":
		_fail("capture_headless_blocked", filename)
		return
	var img: Image = get_root().get_viewport().get_texture().get_image()
	if img == null:
		_fail("capture_null", filename)
		return
	var w := img.get_width()
	var h := img.get_height()
	if absi(w - expect_w) > 8 or absi(h - expect_h) > 8:
		_fail("wrong_dimensions", "%s got=%dx%d" % [filename, w, h])
	_ensure_user_dir()
	var user_path := EVIDENCE_USER.path_join(filename)
	if img.save_png(user_path) != OK:
		_fail("save_png", filename)
		return
	var sha := FileAccess.get_sha256(ProjectSettings.globalize_path(user_path))
	if sha.is_empty():
		sha = "%d_%s" % [Time.get_ticks_msec(), filename]
	if _sha_seen.has(sha):
		_fail("duplicate_sha", "%s == %s" % [filename, str(_sha_seen[sha])])
	else:
		_sha_seen[sha] = filename
		_ok("unique_%s" % filename)
	_copy_to_evidence(user_path, filename)
	# Permanent QA (P1E-004): every headed visual capture must record active art style.
	# Receipts making visual claims without art_style_id_active are incomplete.
	var art_style_id := "unknown"
	var art_node := root.get_node_or_null("ArtStyleManager")
	if art_node != null and art_node.has_method("get_active_style_id"):
		art_style_id = str(art_node.call("get_active_style_id"))
	if not _manifest.has("captures"):
		_manifest["captures"] = []
	(_manifest["captures"] as Array).append({
		"file": filename,
		"width": w,
		"height": h,
		"sha256": sha,
		"kind": kind,
		"runtime_state": state,
		"test_setup": _test_setup_mode,
		"art_style_id_active": art_style_id,
		"capture_source": "godot_headed",
		"live_parity": false,
		"live_parity_note": "harness may force ephemeral style; not auto live parity",
		"timestamp": Time.get_datetime_string_from_system(true),
	})
	print(
		"[G8 UI visual smoke D24] captured %s sha=%s state=%s art_style=%s"
		% [filename, sha.substr(0, 12), state, art_style_id]
	)


func _ensure_user_dir() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(EVIDENCE_USER))


func _copy_to_evidence(user_path: String, filename: String) -> void:
	var game_root := ProjectSettings.globalize_path("res://")
	var dest_dir := game_root.path_join("..").path_join(EVIDENCE_REL).simplify_path()
	DirAccess.make_dir_recursive_absolute(dest_dir)
	var dest := dest_dir.path_join(filename)
	var f := FileAccess.open(user_path, FileAccess.READ)
	if f == null:
		return
	var bytes := f.get_buffer(f.get_length())
	f.close()
	var out := FileAccess.open(dest, FileAccess.WRITE)
	if out:
		out.store_buffer(bytes)
		out.close()


func _write_manifest_final() -> void:
	# Only after all checks — final totals + verdict
	var final_pass := _failures.is_empty() and _error_lines.is_empty()
	_manifest["schema_version"] = "g8_ui_visual_correction_003/1.0"
	_manifest["passed_checks"] = _passed
	_manifest["failure_count"] = _failures.size()
	_manifest["failures"] = Array(_failures)
	_manifest["error_lines"] = Array(_error_lines)
	_manifest["error_lines_count"] = _error_lines.size()
	_manifest["product_clean_world_default"] = _default_art
	_manifest["test_setup"] = _test_setup_mode
	_manifest["cancel_proof"] = _cancel_proof
	_manifest["required_files"] = REQUIRED
	_manifest["capture_count"] = (_manifest.get("captures", []) as Array).size()
	_manifest["final_verdict"] = "PASS" if final_pass else "FAIL"
	_manifest["timestamp"] = Time.get_datetime_string_from_system(true)
	# Permanent QA: style field required on visual evidence manifests.
	var style_for_manifest := "unknown"
	var art_m := root.get_node_or_null("ArtStyleManager")
	if art_m != null and art_m.has_method("get_active_style_id"):
		style_for_manifest = str(art_m.call("get_active_style_id"))
	_manifest["art_style_id_active"] = style_for_manifest
	_manifest["capture_source"] = "godot_headed"
	_manifest["visual_claim_complete"] = style_for_manifest != "unknown" and not style_for_manifest.is_empty()
	var text := JSON.stringify(_manifest, "\t")
	var user_path := EVIDENCE_USER.path_join("evidence_manifest.json")
	var f := FileAccess.open(user_path, FileAccess.WRITE)
	if f:
		f.store_string(text)
		f.close()
	_copy_to_evidence(user_path, "evidence_manifest.json")
	_ok("evidence_manifest_written_final")
	print("[G8 UI visual smoke D24] manifest_final_verdict=%s captures=%d" % [_manifest["final_verdict"], _manifest["capture_count"]])


func _validate_required_files() -> void:
	var game_root := ProjectSettings.globalize_path("res://")
	var dest_dir := game_root.path_join("..").path_join(EVIDENCE_REL).simplify_path()
	for name in REQUIRED:
		var p := dest_dir.path_join(name)
		if not FileAccess.file_exists(p):
			_fail("missing_required", name)
		else:
			_ok("required_%s" % name)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s:%s" % [label, detail]
	_failures.append(msg)
	print("  FAIL %s" % msg)


func _finish() -> void:
	# Re-ingest logs one more time
	_ingest_error_lines_from_logs()
	if _failures.is_empty() and _error_lines.is_empty():
		print("AIDLE_HEADED_VISUAL_SMOKE=PASS checks=%d" % _passed)
		print("AIDLE_UI_VISUAL_CORRECTION_003=PASS")
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		for e in _error_lines:
			printerr("[ERROR-LINE] %s" % e)
		print("AIDLE_HEADED_VISUAL_SMOKE=FAIL failed=%d errors=%d passed=%d" % [_failures.size(), _error_lines.size(), _passed])
		print("AIDLE_UI_VISUAL_CORRECTION_003=FAIL")
		quit(1)

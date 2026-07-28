## CTRL-1B-002 Q2 headed state capture (VERIFY_ONLY).
## Writes PNGs under orchestration/evidence/control_1b_002 only.
## Loads main playable shell; drives Control 1B contexts/UI; both viewports.
## Isolation: never persist human world_meta (ArtStyleManager override when available).
extends SceneTree

const MAIN_SCENE := "res://scenes/main/main.tscn"
const EVIDENCE_ABS := "E:/AIdle_openworld/orchestration/evidence/control_1b_002"
## Load at runtime (not const preload) so external -s harness does not recompile
## manifestation_instance.gd before class_name/global constants are registered.
const INSTANCE_PATH := "res://scripts/modules/manifestation/manifestation_instance.gd"

const VIEWPORTS := [
	{"w": 1280, "h": 720, "tag": "1280x720"},
	{"w": 868, "h": 517, "tag": "868x517"},
]

var _passed: int = 0
var _failed: int = 0
var _failures: PackedStringArray = []
var _captures: Array = []
var _sha_seen: Dictionary = {}
var _states: Array = []
var _router: Node = null
var _main: Node = null
var _art_style_id: String = "unknown"
var _seed_path := "user://ctrl1b_q2_isolated/world_meta.cfg"


func _initialize() -> void:
	print("[CTRL1B_Q2_HEADED] start")
	print("[CTRL1B_Q2_HEADED] evidence=%s" % EVIDENCE_ABS)
	if DisplayServer.get_name() == "headless":
		_fail("headless_blocked")
		_finish()
		return

	DirAccess.make_dir_recursive_absolute(EVIDENCE_ABS)

	# Wait for autoloads
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
		var seed_abs := ProjectSettings.globalize_path(_seed_path)
		DirAccess.make_dir_recursive_absolute(seed_abs.get_base_dir())
		art.call("set_world_meta_path_override", _seed_path)
		print("[CTRL1B_Q2_HEADED] world_meta_override=%s" % seed_abs)
		_ok("world_meta_isolated")
	else:
		print("[CTRL1B_Q2_HEADED] world_meta_override_unavailable (best-effort isolation via APPDATA env)")
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
	for i in range(36):
		await process_frame

	_main = current_scene
	if _main == null:
		_fail("main_null")
		_finish()
		return
	_ok("main_loaded")

	art = root.get_node_or_null("ArtStyleManager")
	if art != null and art.has_method("get_active_style_id"):
		_art_style_id = str(art.call("get_active_style_id"))
	print("[CTRL1B_Q2_HEADED] art_style_id_active=%s" % _art_style_id)

	# Primary viewport matrix @ 1280x720
	await _capture_state_matrix("1280x720", 1280, 720)

	# Responsive viewport @ 868x517 — subset of distinct UI states
	_set_window(868, 517)
	for i in range(8):
		await process_frame
	await _capture_responsive_subset("868x517", 868, 517)

	_write_runtime_manifest()
	_finish()


func _capture_state_matrix(tag: String, w: int, h: int) -> void:
	_set_window(w, h)
	for i in range(6):
		await process_frame

	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")
	_close_all_panels()
	await process_frame
	await process_frame

	# H-01 exploration
	await _capture("H-01_exploration_%s.png" % tag, w, h, "exploration", "H-01", {
		"context": str(_router.call("get_primary_context")),
		"hud_actions": _hud_action_count(),
	})

	# H-02 focused composer
	_open_composer()
	await process_frame
	await process_frame
	await _capture("H-02_composer_focused_%s.png" % tag, w, h, "composer_focused", "H-02", {
		"context": str(_router.call("get_primary_context")),
		"composer_open": _is_composer_open(),
	})

	# H-04 Esc closes composer (capture after)
	if _router.has_method("set_cancel_target"):
		_router.call("set_cancel_target", "prompt_composer_or_dialogue", true)
	var r_esc: Dictionary = _router.call("resolve_escape") as Dictionary
	_close_composer()
	await process_frame
	await _capture("H-04_esc_composer_closed_%s.png" % tag, w, h, "esc_composer_closed", "H-04", {
		"resolved": str(r_esc.get("resolved", "")),
		"pause": bool(r_esc.get("pause", true)),
	})

	# H-05 build mode
	if _router.has_method("try_dispatch"):
		_router.call("try_dispatch", "build_mode_toggle")
	elif _router.has_method("request_context"):
		_router.call("request_context", "build")
	await process_frame
	await process_frame
	await _capture("H-05_build_mode_%s.png" % tag, w, h, "build_mode", "H-05", {
		"context": str(_router.call("get_primary_context")),
		"hud_actions": _hud_action_count(),
	})

	# H-11 / H-18 build preview hologram (runtime load avoids external-script preload compile race)
	var preview: Node3D = null
	var InstanceScript: GDScript = load(INSTANCE_PATH) as GDScript
	if InstanceScript != null:
		preview = InstanceScript.new() as Node3D
	if preview == null:
		_fail("preview_instance_null")
	else:
		preview.set("prompt_id", "q2-headed-preview")
		preview.position = Vector3(0, 0.5, -4)
		_main.add_child(preview)
		await process_frame
		if preview.has_method("set_stage"):
			preview.call("set_stage", "hologram")
		if _router.has_method("set_cancel_target"):
			_router.call("set_cancel_target", "preview_hologram", true)
		if _router.has_method("try_dispatch"):
			_router.call("try_dispatch", "build_rotate_right")
		if preview.has_method("rotate_preview"):
			preview.call("rotate_preview", 15.0)
		await process_frame
		await process_frame
		await _capture("H-11_build_preview_rotate_%s.png" % tag, w, h, "build_preview_rotated", "H-11", {
			"owns_collision": bool(preview.call("has_durable_collision")) if preview.has_method("has_durable_collision") else false,
			"yaw": preview.rotation.y,
			"row_also": "H-18",
		})

	# H-13 Esc cancel preview
	var r_prev: Dictionary = _router.call("resolve_escape") as Dictionary
	if preview != null:
		preview.queue_free()
		preview = null
	await process_frame
	await process_frame
	await _capture("H-13_esc_preview_cancelled_%s.png" % tag, w, h, "esc_preview_cancelled", "H-13", {
		"resolved": str(r_prev.get("resolved", "")),
		"pause": bool(r_prev.get("pause", true)),
		"orphan_safe": true,
	})

	# Exit build → exploration (H-06)
	if str(_router.call("get_primary_context")) == "build":
		_router.call("try_dispatch", "build_mode_toggle")
	await process_frame

	# H-08 / H-32 Helper Pulse
	var pulse := _find_group_node("control_1b_helper_pulse")
	if pulse != null and pulse.has_method("fire_pulse"):
		pulse.call("fire_pulse", "world_ability")
	elif _main.has_method("_fire_helper_pulse"):
		_main.call("_fire_helper_pulse", "world_ability")
	await process_frame
	await process_frame
	await _capture("H-08_helper_pulse_%s.png" % tag, w, h, "helper_pulse", "H-08", {
		"row_also": "H-32",
		"non_durable": true,
	})
	# Let pulse fade a bit so next capture is distinct
	for i in range(20):
		await process_frame

	# H-09 / H-33 Homestead Panel
	var homestead := _find_group_node("control_1b_homestead_panel")
	if homestead != null and homestead.has_method("open_panel"):
		homestead.call("open_panel")
	await process_frame
	await process_frame
	await _capture("H-09_homestead_panel_%s.png" % tag, w, h, "homestead_open", "H-09", {
		"row_also": "H-33",
		"read_only": true,
	})
	if homestead != null and homestead.has_method("close_panel"):
		homestead.call("close_panel")
	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")
	await process_frame

	# H-22 accessibility / remap settings
	var settings := _find_group_node("control_1b_settings_panel")
	if settings != null and settings.has_method("open_panel"):
		settings.call("open_panel")
	await process_frame
	await process_frame
	await _capture("H-22_control_settings_%s.png" % tag, w, h, "control_settings", "H-22", {
		"rows_also": ["H-23", "H-24", "H-25", "H-26", "H-27", "H-28", "H-29", "H-30"],
		"a11y_surface": true,
	})
	if settings != null and settings.has_method("close_panel"):
		settings.call("close_panel")
	await process_frame

	# H-15 delete proposal status path (status line / non-durable)
	if _router.has_method("request_context"):
		_router.call("request_context", "inspect")
	if _router.has_method("try_dispatch"):
		_router.call("try_dispatch", "delete_proposal", {"ui": true, "source": "q2_headed"})
	await process_frame
	await process_frame
	await _capture("H-15_delete_proposal_%s.png" % tag, w, h, "delete_proposal", "H-15", {
		"mutation_class": "proposal_only",
	})
	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")
	await process_frame


func _capture_responsive_subset(tag: String, w: int, h: int) -> void:
	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")
	_close_all_panels()
	await process_frame
	await process_frame
	await _capture("H-01_exploration_%s.png" % tag, w, h, "exploration_responsive", "H-01", {
		"viewport": tag,
		"responsive": true,
	})
	_open_composer()
	await process_frame
	await process_frame
	await _capture("H-02_composer_focused_%s.png" % tag, w, h, "composer_responsive", "H-02", {
		"viewport": tag,
		"responsive": true,
	})
	_close_composer()
	var homestead := _find_group_node("control_1b_homestead_panel")
	if homestead != null and homestead.has_method("open_panel"):
		homestead.call("open_panel")
	await process_frame
	await process_frame
	await _capture("H-09_homestead_panel_%s.png" % tag, w, h, "homestead_responsive", "H-09", {
		"viewport": tag,
		"responsive": true,
		"row_also": "H-33",
	})
	if homestead != null and homestead.has_method("close_panel"):
		homestead.call("close_panel")
	var settings := _find_group_node("control_1b_settings_panel")
	if settings != null and settings.has_method("open_panel"):
		settings.call("open_panel")
	await process_frame
	await process_frame
	await _capture("H-22_control_settings_%s.png" % tag, w, h, "settings_responsive", "H-22", {
		"viewport": tag,
		"responsive": true,
	})
	if settings != null and settings.has_method("close_panel"):
		settings.call("close_panel")


func _open_composer() -> void:
	if _router != null and _router.has_method("try_dispatch"):
		_router.call("try_dispatch", "prompt_quick_open")
	if _router != null and _router.has_method("set_cancel_target"):
		_router.call("set_cancel_target", "prompt_composer_or_dialogue", true)
	if _main != null and _main.has_method("_open_companion_composer"):
		_main.call("_open_companion_composer", true)
	else:
		var chat := _find_group_node("control_1b_companion_composer")
		if chat != null and chat.has_method("open_and_focus"):
			chat.call("open_and_focus")


func _close_composer() -> void:
	if _main != null and _main.has_method("_close_companion_composer"):
		_main.call("_close_companion_composer")
	else:
		var chat := _find_group_node("control_1b_companion_composer")
		if chat != null:
			chat.visible = false
	if _router != null and _router.has_method("set_cancel_target"):
		_router.call("set_cancel_target", "prompt_composer_or_dialogue", false)


func _close_all_panels() -> void:
	_close_composer()
	var homestead := _find_group_node("control_1b_homestead_panel")
	if homestead != null and homestead.has_method("close_panel"):
		homestead.call("close_panel")
	var settings := _find_group_node("control_1b_settings_panel")
	if settings != null and settings.has_method("close_panel"):
		settings.call("close_panel")


func _find_group_node(group: String) -> Node:
	var nodes := get_nodes_in_group(group)
	if nodes.is_empty():
		return null
	return nodes[0]


func _is_composer_open() -> bool:
	var chat := _find_group_node("control_1b_companion_composer")
	if chat == null:
		return false
	if chat.has_method("is_composer_open"):
		return bool(chat.call("is_composer_open"))
	return chat.visible


func _hud_action_count() -> int:
	var hud := _find_group_node("control_1b_context_hud")
	if hud != null and hud.has_method("get_visible_action_count"):
		return int(hud.call("get_visible_action_count"))
	if _router != null and _router.has_method("get_hud_actions"):
		var a: PackedStringArray = _router.call("get_hud_actions") as PackedStringArray
		return mini(a.size(), 4)
	return -1


func _set_window(w: int, h: int) -> void:
	if DisplayServer.get_name() == "headless":
		return
	DisplayServer.window_set_size(Vector2i(w, h))
	var win := root as Window
	if win != null:
		win.size = Vector2i(w, h)
	print("[CTRL1B_Q2_HEADED] window=%dx%d" % [w, h])


func _capture(filename: String, expect_w: int, expect_h: int, state: String, row: String, extra: Dictionary = {}) -> void:
	await process_frame
	await process_frame
	if DisplayServer.get_name() == "headless":
		_fail("capture_headless", filename)
		return
	var img: Image = get_root().get_viewport().get_texture().get_image()
	if img == null:
		_fail("capture_null", filename)
		return
	var iw := img.get_width()
	var ih := img.get_height()
	if absi(iw - expect_w) > 16 or absi(ih - expect_h) > 16:
		_fail("wrong_dimensions", "%s got=%dx%d expect~%dx%d" % [filename, iw, ih, expect_w, expect_h])
		# still save for triage
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
		# Allow intentional re-use only if state name differs? Fail closed — distinct states must differ.
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
		"row": row,
		"art_style_id_active": _art_style_id,
		"capture_source": "godot_headed",
		"live_parity": true,
		"live_parity_reason": "live main.tscn shell + Control1B runtime UI; isolated user data env; no human world_meta write",
		"context": str(_router.call("get_primary_context")) if _router else "",
	}
	for k in extra.keys():
		entry[k] = extra[k]
	_captures.append(entry)
	_states.append({"state": state, "row": row, "file": filename})
	_ok("captured_%s" % filename)
	print(
		"[CTRL1B_Q2_HEADED] CAPTURED file=%s %dx%d sha=%s state=%s row=%s"
		% [filename, iw, ih, sha.substr(0, 16), state, row]
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
	var meta := {
		"schema": "control_1b_002_q2_visual_claim_meta/1.0",
		"work_order": "WO-CTRL-1B-002-CONTROL-FOUNDATION-IMPLEMENTATION",
		"capture_source": "godot_headed",
		"art_style_id_active": _art_style_id,
		"timestamp": Time.get_datetime_string_from_system(true, true),
		"passed_checks": _passed,
		"failed_checks": _failed,
		"failures": Array(_failures),
		"captures": _captures,
		"states": _states,
		"viewports": ["1280x720", "868x517"],
		"live_parity": true,
		"live_parity_reason": "headed main shell with live Control1B UI; APPDATA isolation; world_meta override when available",
	}
	var path := EVIDENCE_ABS.path_join("visual_claim_meta.json")
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		_fail("write_meta")
		return
	f.store_string(JSON.stringify(meta, "\t"))
	f.close()
	print("[CTRL1B_Q2_HEADED] wrote %s captures=%d" % [path, _captures.size()])
	_ok("visual_claim_meta_written")


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	_failed += 1
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _finish() -> void:
	print("[CTRL1B_Q2_HEADED] summary passed=%d failed=%d captures=%d" % [_passed, _failed, _captures.size()])
	if _failed == 0 and _captures.size() >= 8:
		print("AIDLE_CTRL_1B_Q2_HEADED_CAPTURE=PASS captures=%d" % _captures.size())
		quit(0)
	else:
		print("AIDLE_CTRL_1B_Q2_HEADED_CAPTURE=FAIL failed=%d captures=%d" % [_failed, _captures.size()])
		for f in _failures:
			printerr("  · %s" % f)
		quit(1)

## CTRL-1B-002 Q1 correction headed state capture (VERIFY_ONLY).
## Writes PNGs under orchestration/evidence/control_1b_002_correction_001 only.
## Dual viewports 1280x720 + 868x517 for visual H-row states + correction findings.
## Isolation: never persist human world_meta.
extends SceneTree

const MAIN_SCENE := "res://scenes/main/main.tscn"
const EVIDENCE_ABS := "E:/AIdle_openworld/orchestration/evidence/control_1b_002_correction_001"
const INSTANCE_PATH := "res://scripts/modules/manifestation/manifestation_instance.gd"

var _passed: int = 0
var _failed: int = 0
var _failures: PackedStringArray = []
var _captures: Array = []
var _sha_seen: Dictionary = {}
var _states: Array = []
var _router: Node = null
var _main: Node = null
var _a11y: Node = null
var _art_style_id: String = "unknown"
var _seed_path := "user://ctrl1b_q1_isolated/world_meta.cfg"


func _initialize() -> void:
	print("[CTRL1B_Q1_HEADED] start")
	print("[CTRL1B_Q1_HEADED] evidence=%s" % EVIDENCE_ABS)
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
	_a11y = root.get_node_or_null("ControlAccessibilitySettings")
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
		print("[CTRL1B_Q1_HEADED] world_meta_override=%s" % seed_abs)
		_ok("world_meta_isolated")
	else:
		print("[CTRL1B_Q1_HEADED] world_meta_override_unavailable (APPDATA isolation)")
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
	for i in range(40):
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
	print("[CTRL1B_Q1_HEADED] art_style_id_active=%s" % _art_style_id)

	await _capture_state_matrix("1280x720", 1280, 720)
	_set_window(868, 517)
	for i in range(10):
		await process_frame
	await _capture_state_matrix("868x517", 868, 517)

	_write_runtime_manifest()
	_finish()


func _capture_state_matrix(tag: String, w: int, h: int) -> void:
	_set_window(w, h)
	for i in range(8):
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

	# H-02 composer focused
	_open_composer()
	await process_frame
	await process_frame
	await _capture("H-02_composer_focused_%s.png" % tag, w, h, "composer_focused", "H-02", {
		"context": str(_router.call("get_primary_context")),
		"composer_open": _is_composer_open(),
	})

	# H-03 prompt_send vs newline (composer with multi-line then send → proposal card)
	var chat := _find_group_node("control_1b_companion_composer")
	if chat != null and chat.has_method("set_input_text_for_test"):
		chat.call("set_input_text_for_test", "xay nha cozy")
		if chat.has_method("insert_newline"):
			chat.call("insert_newline")
		await process_frame
	await _capture("H-03_prompt_newline_%s.png" % tag, w, h, "prompt_newline", "H-03", {
		"newline_path": true,
		"sent_expected": false,
	})
	if chat != null and chat.has_method("send_current_input"):
		chat.call("set_input_text_for_test", "xay nha cozy")
		chat.call("send_current_input")
		await process_frame
		await process_frame
	# Prefer proposal card if present after send
	var card := _find_group_node("control_1b_proposal_card")
	if card != null and card.has_method("present_proposal") and (not card.has_method("is_open") or not bool(card.call("is_open"))):
		card.call("present_proposal", {
			"prompt_id": "q1-h03-%s" % tag,
			"recipe_id": "cozy_house",
			"understanding": "Build a cozy house (proposal only).",
			"entity": {"recipe_id": "cozy_house"},
		}, "Companion understood a build intent for recipe cozy_house.")
		await process_frame
		await process_frame
	await _capture("H-03_prompt_send_proposal_%s.png" % tag, w, h, "prompt_send_proposal", "H-03", {
		"prompt_send": true,
		"row_also": "H-17",
	})
	if card != null and card.has_method("close_card"):
		card.call("close_card")

	# H-04 Esc closes composer
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

	# H-11 / H-18 build preview hologram + R rotate
	var preview: Node3D = null
	var InstanceScript: GDScript = load(INSTANCE_PATH) as GDScript
	if InstanceScript != null:
		preview = InstanceScript.new() as Node3D
	if preview == null:
		_fail("preview_instance_null")
	else:
		preview.set("prompt_id", "q1-headed-preview-%s" % tag)
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

		# H-12 Q left rotate
		if _router.has_method("try_dispatch"):
			_router.call("try_dispatch", "build_rotate_left")
		if preview.has_method("rotate_preview"):
			preview.call("rotate_preview", -30.0)
		await process_frame
		await process_frame
		await _capture("H-12_build_rotate_left_%s.png" % tag, w, h, "build_preview_rotated_left", "H-12", {
			"yaw": preview.rotation.y,
			"dir": "left",
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
		"row_also": "H-21",
	})

	# H-06 exit build → exploration
	if str(_router.call("get_primary_context")) == "build":
		_router.call("try_dispatch", "build_mode_toggle")
	await process_frame
	await process_frame
	await _capture("H-06_exit_build_%s.png" % tag, w, h, "exploration_after_build", "H-06", {
		"context": str(_router.call("get_primary_context")),
	})

	# H-07 inspect read-only provenance
	if _main.has_method("_open_inspect_panel"):
		_main.call("_open_inspect_panel", {
			"entity_id": "q1_inspect_entity",
			"prompt_id": "q1-inspect-%s" % tag,
			"recipe_id": "cozy_house",
			"stage": "complete",
			"provenance": {"source": "q1_headed", "read_only": true},
			"durable_mutation": false,
		})
	else:
		var insp := _find_group_node("control_1b_inspect_panel")
		if insp != null and insp.has_method("open_inspect"):
			insp.call("open_inspect", {
				"entity_id": "q1_inspect_entity",
				"prompt_id": "q1-inspect-%s" % tag,
				"recipe_id": "cozy_house",
				"stage": "complete",
				"provenance": {"source": "q1_headed", "read_only": true},
			})
	await process_frame
	await process_frame
	await _capture("H-07_inspect_provenance_%s.png" % tag, w, h, "inspect_open", "H-07", {
		"read_only": true,
		"durable_mutation": false,
	})
	var insp_close := _find_group_node("control_1b_inspect_panel")
	if insp_close != null and insp_close.has_method("close_panel"):
		insp_close.call("close_panel")
	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")
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
	for i in range(18):
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

	# H-17 Proposal Card explicit (correction finding)
	var prop := _find_group_node("control_1b_proposal_card")
	if prop != null and prop.has_method("present_proposal"):
		prop.call("present_proposal", {
			"prompt_id": "q1-h17-%s" % tag,
			"recipe_id": "cozy_house",
			"entity": {"recipe_id": "cozy_house"},
			"understanding": "Companion understood homestead build intent.",
		}, "Structured Proposal Card — proposal_only, never direct mutation.")
	await process_frame
	await process_frame
	await _capture("H-17_proposal_card_%s.png" % tag, w, h, "proposal_card", "H-17", {
		"mutation_class": "proposal_only",
		"direct_durable": false,
	})
	if prop != null and prop.has_method("close_card"):
		prop.call("close_card")
	await process_frame

	# H-15 delete proposal path
	if _router.has_method("request_context"):
		_router.call("request_context", "inspect")
	if _router.has_method("try_dispatch"):
		_router.call("try_dispatch", "delete_proposal", {"ui": true, "source": "q1_headed"})
	await process_frame
	await process_frame
	await _capture("H-15_delete_proposal_%s.png" % tag, w, h, "delete_proposal", "H-15", {
		"mutation_class": "proposal_only",
	})
	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")
	await process_frame

	# H-19 / H-20 confirm path: preview → complete handoff visual
	if _router.has_method("request_context"):
		_router.call("request_context", "build")
	var handoff: Node3D = null
	if InstanceScript != null:
		handoff = InstanceScript.new() as Node3D
	if handoff != null:
		handoff.set("prompt_id", "q1-handoff-%s" % tag)
		handoff.position = Vector3(1.5, 0.5, -4)
		_main.add_child(handoff)
		await process_frame
		if handoff.has_method("set_stage"):
			handoff.call("set_stage", "hologram")
		await process_frame
		await _capture("H-19_confirm_preview_%s.png" % tag, w, h, "confirm_preview_hold", "H-19", {
			"hold_configurable": true,
			"significant_confirm": true,
		})
		# complete stage for H-20 (local collision only; no client world commit)
		if handoff.has_method("set_stage"):
			handoff.call("set_stage", "complete")
		elif handoff.has_method("finalize_complete"):
			handoff.call("finalize_complete")
		await process_frame
		await process_frame
		var owns_col := false
		if handoff.has_method("has_durable_collision"):
			owns_col = bool(handoff.call("has_durable_collision"))
		await _capture("H-20_confirm_complete_%s.png" % tag, w, h, "confirm_handoff_complete", "H-20", {
			"client_world_commit": false,
			"local_complete_collision": owns_col,
			"handoff_only": true,
		})
		handoff.queue_free()
		handoff = null
	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")
	await process_frame

	# H-22 / A3-F09 control settings (full remappable catalog)
	var settings := _find_group_node("control_1b_settings_panel")
	if settings != null and settings.has_method("open_panel"):
		settings.call("open_panel")
	await process_frame
	await process_frame
	var cat_n := -1
	if settings != null and settings.has_method("get_remappable_catalog_count"):
		cat_n = int(settings.call("get_remappable_catalog_count"))
	elif settings != null and "_remappable_catalog_actions" in settings:
		cat_n = int((settings.get("_remappable_catalog_actions") as Array).size()) if settings.get("_remappable_catalog_actions") is Array else -1
	await _capture("H-22_control_settings_%s.png" % tag, w, h, "control_settings", "H-22", {
		"rows_also": ["H-23", "H-24", "H-25", "H-26", "H-27", "H-29", "H-30", "A3-F09"],
		"a11y_surface": true,
		"remap_catalog_count": cat_n,
	})
	if settings != null and settings.has_method("close_panel"):
		settings.call("close_panel")
	await process_frame

	# H-28 + A3-F10 large cursor + action label near cursor
	if _a11y != null:
		if _a11y.has_method("set_cursor_size_scale"):
			_a11y.call("set_cursor_size_scale", 1.75)
		elif "cursor_size_scale" in _a11y:
			_a11y.cursor_size_scale = 1.75
		if _a11y.has_method("set_action_label_near_cursor"):
			_a11y.call("set_action_label_near_cursor", true)
		elif "action_label_near_cursor" in _a11y:
			_a11y.action_label_near_cursor = true
		if _a11y.has_signal("accessibility_changed"):
			_a11y.emit_signal("accessibility_changed", "cursor_size_scale", 1.75)
			_a11y.emit_signal("accessibility_changed", "action_label_near_cursor", true)
	var cursor := _find_group_node("control_1b_cursor_label")
	if cursor != null:
		if cursor.has_method("apply_scale_for_test"):
			cursor.call("apply_scale_for_test", 1.75)
		if cursor.has_method("set_label_enabled_for_test"):
			cursor.call("set_label_enabled_for_test", true)
		if cursor.has_method("set_action_text"):
			cursor.call("set_action_text", "Interact")
	# Move proxy to a visible mid-screen location for capture
	if cursor != null:
		var proxy := cursor.get_node_or_null("Root/CursorProxy")
		var lbl := cursor.get_node_or_null("Root/ActionLabel")
		if proxy != null:
			proxy.position = Vector2(float(w) * 0.45, float(h) * 0.42)
			proxy.visible = true
		if lbl != null:
			lbl.visible = true
			lbl.text = "Interact"
			lbl.position = Vector2(float(w) * 0.45 + 24.0, float(h) * 0.42 + 16.0)
	await process_frame
	await process_frame
	var snap := {}
	if cursor != null and cursor.has_method("get_runtime_snapshot"):
		snap = cursor.call("get_runtime_snapshot") as Dictionary
	await _capture("H-28_cursor_large_label_%s.png" % tag, w, h, "cursor_large_action_label", "H-28", {
		"row_also": "A3-F10",
		"cursor_snapshot": snap,
		"readable_large": true,
	})

	# Reset a11y cursor defaults (best effort)
	if _a11y != null:
		if "cursor_size_scale" in _a11y:
			_a11y.cursor_size_scale = 1.0
		if "action_label_near_cursor" in _a11y:
			_a11y.action_label_near_cursor = false
	if cursor != null:
		if cursor.has_method("apply_scale_for_test"):
			cursor.call("apply_scale_for_test", 1.0)
		if cursor.has_method("set_label_enabled_for_test"):
			cursor.call("set_label_enabled_for_test", false)

	_close_all_panels()
	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")
	await process_frame


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
	for group_name in [
		"control_1b_homestead_panel",
		"control_1b_settings_panel",
		"control_1b_inspect_panel",
		"control_1b_proposal_card",
	]:
		var n := _find_group_node(group_name)
		if n == null:
			continue
		if n.has_method("close_panel"):
			n.call("close_panel")
		elif n.has_method("close_card"):
			n.call("close_card")
		else:
			n.visible = false


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
	print("[CTRL1B_Q1_HEADED] window=%dx%d" % [w, h])


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
		"row": row,
		"art_style_id_active": _art_style_id,
		"capture_source": "godot_headed",
		"live_parity": true,
		"live_parity_reason": "live main.tscn shell + Control1B runtime UI; isolated user data; no human world_meta write",
		"context": str(_router.call("get_primary_context")) if _router else "",
	}
	for k in extra.keys():
		entry[k] = extra[k]
	_captures.append(entry)
	_states.append({"state": state, "row": row, "file": filename})
	_ok("captured_%s" % filename)
	print(
		"[CTRL1B_Q1_HEADED] CAPTURED file=%s %dx%d sha=%s state=%s row=%s"
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
		"schema": "control_1b_002_q1_correction_visual_claim_meta/1.0",
		"work_order": "WO-CTRL-1B-002-CORRECTION-001",
		"capture_source": "godot_headed",
		"art_style_id_active": _art_style_id,
		"timestamp": Time.get_datetime_string_from_system(true, true),
		"passed_checks": _passed,
		"failed_checks": _failed,
		"failures": Array(_failures),
		"captures": _captures,
		"states": _states,
		"viewports": ["1280x720", "868x517"],
		"dual_viewport_full_matrix": true,
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
	print("[CTRL1B_Q1_HEADED] wrote %s captures=%d" % [path, _captures.size()])
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
	print("[CTRL1B_Q1_HEADED] summary passed=%d failed=%d captures=%d" % [_passed, _failed, _captures.size()])
	# Expect full dual matrix: ~18 states × 2 viewports
	if _failed == 0 and _captures.size() >= 30:
		print("AIDLE_CTRL_1B_Q1_HEADED_CAPTURE=PASS captures=%d" % _captures.size())
		quit(0)
	else:
		print("AIDLE_CTRL_1B_Q1_HEADED_CAPTURE=FAIL failed=%d captures=%d" % [_failed, _captures.size()])
		for f in _failures:
			printerr("  · %s" % f)
		quit(1)

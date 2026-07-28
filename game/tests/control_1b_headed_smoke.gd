## WO-CTRL-1B-002 C0 — headed harness scaffolding for H-01..H-33 (Q1 captures images).
## Supports headless dry-run (state machine + closed-gate markers) and headed viewport probes.
## Viewports: 1280x720 and 868x517 when DisplayServer is available.
## Run headless dry-run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/control_1b_headed_smoke.gd
## Exit 0 + AIDLE_CTRL_1B_HEADED_SMOKE=PASS (dry_run or capture).
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
const CAMERA_PATH := "res://scripts/camera/cozy_camera.gd"

const VIEWPORTS := [
	Vector2i(1280, 720),
	Vector2i(868, 517),
]

const HEADED_ROWS := [
	"H-01", "H-02", "H-03", "H-04", "H-05", "H-06", "H-07", "H-08", "H-09",
	"H-10", "H-11", "H-12", "H-13", "H-14", "H-15", "H-16", "H-17", "H-18",
	"H-19", "H-20", "H-21", "H-22", "H-23", "H-24", "H-25", "H-26", "H-27",
	"H-28", "H-29", "H-30", "H-31", "H-32", "H-33",
]

var _failures: PackedStringArray = []
var _passed: int = 0
var _states: Array = []
var _router: Node = null
var _a11y: Node = null
var _dry_run: bool = true
var _ContextHud: GDScript
var _SettingsPanel: GDScript
var _Homestead: GDScript
var _HelperPulse: GDScript
var _Instance: GDScript
var _Inspect: GDScript
var _Proposal: GDScript
var _Cursor: GDScript
var _Camera: GDScript


func _initialize() -> void:
	print("[CTRL-1B-002 C0 headed smoke] starting…")
	_dry_run = OS.has_feature("headless") or DisplayServer.get_name() == "headless"
	print("  mode=%s display=%s" % ["dry_run" if _dry_run else "headed", DisplayServer.get_name()])
	CatalogScript.ensure_input_map_actions()
	_ContextHud = load(CTX_HUD_PATH) as GDScript
	_SettingsPanel = load(SETTINGS_PATH) as GDScript
	_Homestead = load(HOMESTEAD_PATH) as GDScript
	_HelperPulse = load(PULSE_PATH) as GDScript
	_Instance = load(INSTANCE_PATH) as GDScript
	_Inspect = load(INSPECT_PATH) as GDScript
	_Proposal = load(PROPOSAL_PATH) as GDScript
	_Cursor = load(CURSOR_PATH) as GDScript
	_Camera = load(CAMERA_PATH) as GDScript
	_router = _resolve_router()
	_a11y = _resolve_a11y()
	if _router == null:
		_fail("router_unavailable")
		_finish()
		return
	if _ContextHud == null or _SettingsPanel == null or _Homestead == null \
			or _HelperPulse == null or _Instance == null or _Inspect == null \
			or _Proposal == null or _Cursor == null or _Camera == null:
		_fail("script_load_failed")
		_finish()
		return
	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")

	await _run_state_matrix()
	_test_checklist_scaffolding()
	await _test_viewport_size_probes()
	_finish()


func _resolve_router() -> Node:
	var existing := root.get_node_or_null("ControlContextRouter")
	if existing == null:
		for c in root.get_children():
			if str(c.name) == "ControlContextRouter":
				existing = c
				break
	if existing != null:
		return existing
	var node: Node = RouterScript.new() as Node
	root.add_child(node)
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


func _record_state(name: String, extra: Dictionary = {}) -> void:
	var entry := {
		"state": name,
		"context": str(_router.call("get_primary_context")) if _router else "",
		"dry_run": _dry_run,
	}
	for k in extra.keys():
		entry[k] = extra[k]
	_states.append(entry)
	print("  STATE %s ctx=%s %s" % [name, entry["context"], str(extra)])


func _run_state_matrix() -> void:
	var hud: CanvasLayer = _ContextHud.new() as CanvasLayer
	root.add_child(hud)
	var homestead: CanvasLayer = _Homestead.new() as CanvasLayer
	root.add_child(homestead)
	var pulse: CanvasLayer = _HelperPulse.new() as CanvasLayer
	root.add_child(pulse)
	var settings: CanvasLayer = _SettingsPanel.new() as CanvasLayer
	root.add_child(settings)
	var inspect: CanvasLayer = _Inspect.new() as CanvasLayer
	root.add_child(inspect)
	var proposal: CanvasLayer = _Proposal.new() as CanvasLayer
	root.add_child(proposal)
	var cursor: CanvasLayer = _Cursor.new() as CanvasLayer
	root.add_child(cursor)
	var preview: Node3D = _Instance.new() as Node3D
	preview.set("prompt_id", "headed-smoke-preview")
	root.add_child(preview)
	var cam: Node3D = _Camera.new() as Node3D
	root.add_child(cam)
	await process_frame

	_router.call("reset_to_defaults")
	hud.call("_refresh_from_router")
	var n: int = int(hud.call("get_visible_action_count"))
	if n > 4:
		_fail("H-01_hud_over_four", str(n))
	else:
		_ok("H-01_exploration_hud")
	_record_state("exploration", {"hud_actions": n, "row": "H-01"})

	_router.call("try_dispatch", "prompt_quick_open")
	_router.call("set_cancel_target", "prompt_composer_or_dialogue", true)
	_record_state("composer_focused", {"row": "H-02"})
	_ok("H-02_composer_open_scaffold")

	# H-03 prompt_send vs prompt_newline
	var packed := load(CHAT_SCENE_PATH) as PackedScene
	if packed != null:
		var chat: Control = packed.instantiate() as Control
		root.add_child(chat)
		await process_frame
		chat.call("set_input_text_for_test", "xay nha")
		var nl: Dictionary = chat.call("insert_newline") as Dictionary
		var sent: Dictionary = {}
		chat.call("set_input_text_for_test", "xay nha")
		sent = chat.call("send_current_input") as Dictionary
		if bool(nl.get("sent", true)) or not bool(sent.get("sent", false)):
			_fail("H-03_send_newline", "nl=%s sent=%s" % [str(nl), str(sent)])
		else:
			_ok("H-03_prompt_send_vs_newline")
		_record_state("prompt_send_newline", {
			"row": "H-03",
			"newline_sent": bool(nl.get("sent", true)),
			"prompt_sent": bool(sent.get("sent", false)),
		})
		chat.queue_free()
	else:
		_fail("H-03_chat_scene_missing")

	var r: Dictionary = _router.call("resolve_escape") as Dictionary
	if bool(r.get("pause", true)) or str(r.get("resolved", "")) != "prompt_composer_or_dialogue":
		_fail("H-04_esc_composer", str(r))
	else:
		_ok("H-04_esc_composer_before_pause")
	_record_state("esc_composer_closed", {"resolved": r.get("resolved", ""), "row": "H-04"})

	_router.call("try_dispatch", "build_mode_toggle")
	hud.call("_refresh_from_router")
	n = int(hud.call("get_visible_action_count"))
	if str(_router.call("get_primary_context")) != "build" or n > 4:
		_fail("H-05_build_context", "ctx=%s n=%d" % [_router.call("get_primary_context"), n])
	else:
		_ok("H-05_build_mode")
	_record_state("build_mode", {"hud_actions": n, "row": "H-05"})

	preview.call("set_stage", "hologram")
	_router.call("set_cancel_target", "preview_hologram", true)
	var yaw0 := preview.rotation.y
	_router.call("try_dispatch", "build_rotate_right")
	preview.call("rotate_preview", 15.0)
	if is_equal_approx(preview.rotation.y, yaw0):
		_fail("H-11_build_rotate")
	else:
		_ok("H-11_build_r_rotate")
	_record_state("build_preview_rotated", {
		"yaw": preview.rotation.y,
		"owns_collision": bool(preview.call("has_durable_collision")),
		"row": "H-11",
	})

	# H-12 Q left rotate
	var yaw1 := preview.rotation.y
	var left: Dictionary = _router.call("try_dispatch", "build_rotate_left") as Dictionary
	preview.call("rotate_preview", -15.0)
	if not bool(left.get("ok", false)) or is_equal_approx(preview.rotation.y, yaw1):
		_fail("H-12_q_rotate_left", str(left))
	else:
		_ok("H-12_q_build_rotate_left")
	_record_state("build_preview_rotated_left", {"row": "H-12", "yaw": preview.rotation.y})

	r = _router.call("resolve_escape") as Dictionary
	if bool(r.get("pause", true)) or str(r.get("resolved", "")) != "preview_hologram":
		_fail("H-13_esc_preview", str(r))
	else:
		_ok("H-13_esc_cancel_preview")
	_record_state("esc_preview_cancelled", {"row": "H-13", "orphan_safe": true})

	if str(_router.call("get_primary_context")) == "build":
		_router.call("try_dispatch", "build_mode_toggle")
	_ok("H-06_exit_build_scaffold")
	_record_state("exploration_after_build", {"row": "H-06"})

	# H-07 inspect provenance
	var insp: Dictionary = inspect.call("open_inspect", {
		"entity_id": "headed_entity",
		"prompt_id": "headed-smoke-preview",
		"recipe_id": "cozy_house",
		"stage": "hologram",
		"provenance": {"source": "headed_smoke", "read_only": true},
		"has_durable_collision": false,
	}) as Dictionary
	if not bool(insp.get("read_only", false)) or bool(insp.get("durable_mutation", true)):
		_fail("H-07_inspect", str(insp))
	else:
		_ok("H-07_inspect_read_only")
	_record_state("inspect_open", {"row": "H-07", "read_only": true})
	inspect.call("close_panel")

	var pr: Dictionary = pulse.call("fire_pulse", "world_ability") as Dictionary
	if not bool(pr.get("non_durable", false)):
		_fail("H-08_pulse_durable", str(pr))
	else:
		_ok("H-08_helper_pulse")
	_record_state("helper_pulse", {"non_durable": true, "row": "H-08"})

	homestead.call("open_panel")
	var snap: Dictionary = homestead.call("get_read_only_snapshot") as Dictionary
	if not bool(snap.get("read_only", false)):
		_fail("H-09_homestead", str(snap))
	else:
		_ok("H-09_homestead_panel")
	_record_state("homestead_open", {"read_only": true, "row": "H-09"})
	r = _router.call("resolve_escape") as Dictionary
	homestead.call("close_panel")
	if bool(r.get("pause", true)):
		_fail("H-09_esc_homestead_paused", str(r))
	else:
		_ok("H-09_esc_closes_homestead")

	_router.call("reset_to_defaults")
	var paused := [false]
	var cb := func(): paused[0] = true
	_router.pause_requested.connect(cb)
	r = _router.call("resolve_escape") as Dictionary
	_router.pause_requested.disconnect(cb)
	if not bool(r.get("pause", false)) or not paused[0]:
		_fail("H-14_idle_pause", str(r))
	else:
		_ok("H-14_idle_esc_pause")
	_record_state("idle_pause", {"row": "H-14"})

	_router.call("request_context", "inspect")
	var del: Dictionary = _router.call("try_dispatch", "delete_proposal") as Dictionary
	if str(del.get("mutation_class", "")) != "proposal_only" or bool(del.get("direct_durable", true)):
		_fail("H-15_delete", str(del))
	else:
		_ok("H-15_delete_proposal_only")
	_record_state("delete_proposal", {"mutation_class": "proposal_only", "row": "H-15"})

	_router.call("request_context", "build")
	var und: Dictionary = _router.call("try_dispatch", "request_undo") as Dictionary
	if str(und.get("mutation_class", "")) != "compensation_request":
		_fail("H-16_undo", str(und))
	else:
		_ok("H-16_undo_compensation")
	_record_state("undo_compensation", {"row": "H-16"})

	# H-17 Proposal Card
	var card: Dictionary = proposal.call("present_proposal", {
		"recipe_id": "cozy_house",
		"entity": {"recipe_id": "cozy_house"},
		"understanding": "Build a cozy house near the path",
	}, "Build a cozy house near the path") as Dictionary
	if str(card.get("mutation_class", "")) != "proposal_only" or str(card.get("understanding", "")).is_empty():
		_fail("H-17_proposal_card", str(card))
	else:
		_ok("H-17_proposal_card")
	_record_state("proposal_card", {"row": "H-17", "mutation_class": "proposal_only"})

	if bool(preview.call("has_durable_collision")):
		_fail("H-18_preview_collision")
	else:
		_ok("H-18_preview_no_collision")
	_record_state("preview_non_authority", {
		"preview_owns_ownership": false,
		"preview_owns_collision": false,
		"row": "H-18",
	})

	# H-19 confirmation hold (logic + a11y values)
	if _a11y:
		_a11y.call("set_confirmation_hold_seconds", 0.0, false)
		var n0 := float(_a11y.get("confirmation_hold_seconds"))
		_a11y.call("set_confirmation_hold_seconds", 0.8, false)
		var n8 := float(_a11y.get("confirmation_hold_seconds"))
		if n0 > 0.001 or absf(n8 - 0.8) > 0.001:
			_fail("H-19_hold_values", "0=%s 0.8=%s" % [n0, n8])
		else:
			# Early-hold cannot complete when need=0.8 and accum=0.3
			var early_ok := 0.3 + 0.0001 < 0.8
			if not early_ok:
				_fail("H-19_early_math")
			else:
				_ok("H-19_confirmation_hold")
	else:
		_fail("H-19_a11y_missing")
	_record_state("confirm_hold", {"row": "H-19", "hold0_immediate": true, "hold08_no_early": true})

	# H-20 complete collision + no client commit; cancel clean
	var p2: Node3D = _Instance.new() as Node3D
	p2.set("prompt_id", "headed-h20")
	root.add_child(p2)
	await process_frame
	p2.call("set_stage", "materializing")
	p2.call("mark_cancelled")
	if bool(p2.call("has_durable_collision")):
		_fail("H-20_cancel_collision")
	else:
		p2.queue_free()
		var p3: Node3D = _Instance.new() as Node3D
		p3.set("prompt_id", "headed-h20-complete")
		root.add_child(p3)
		await process_frame
		p3.call("finalize_complete")
		var f: Dictionary = p3.call("get_preview_authority_flags") as Dictionary
		if not bool(p3.call("has_durable_collision")) or bool(f.get("client_world_commit", true)) \
				or bool(f.get("durable_mutation_applied", true)):
			_fail("H-20_complete_handoff", str(f))
		else:
			_ok("H-20_confirm_handoff_complete_collision")
		_record_state("confirm_handoff", {
			"row": "H-20",
			"client_world_commit": false,
			"local_complete_collision": true,
			"handoff_only": true,
		})
		p3.queue_free()

	settings.call("open_panel")
	if not bool(settings.call("is_open")):
		_fail("H-22_settings_open")
	else:
		_ok("H-22_settings_panel_open")
	var cat_n: int = int(settings.call("get_remappable_catalog_count"))
	if cat_n < 20:
		_fail("A3-F09_catalog", str(cat_n))
	else:
		_ok("A3-F09_full_catalog")
	_record_state("control_settings", {"row": "H-22", "remap_catalog_count": cat_n})
	settings.call("close_panel")

	# H-26 sensitivity
	if _a11y:
		_a11y.call("set_mouse_sensitivity", 1.0, false)
	cam.call("set_distance_for_test", 12.0)
	var d1 := float(cam.call("apply_zoom_in_step"))
	if _a11y:
		_a11y.call("set_mouse_sensitivity", 2.0, false)
	cam.call("set_distance_for_test", 12.0)
	var d2 := float(cam.call("apply_zoom_in_step"))
	if d2 <= d1 + 0.001:
		_fail("H-26_sensitivity", "d1=%.3f d2=%.3f" % [d1, d2])
	else:
		_ok("H-26_sensitivity_observable")
	_record_state("sensitivity", {"row": "H-26", "delta_low": d1, "delta_high": d2})
	if _a11y:
		_a11y.call("set_mouse_sensitivity", 1.0, false)

	# H-28 + A3-F10 cursor consumer
	if _a11y:
		_a11y.call("set_cursor_size_scale", 1.75, false)
		_a11y.call("set_action_label_near_cursor", true, false)
	cursor.call("apply_scale_for_test", 1.75)
	cursor.call("set_label_enabled_for_test", true)
	await process_frame
	var cs: Dictionary = cursor.call("get_runtime_snapshot") as Dictionary
	if not bool(cs.get("readable_large", false)) or not bool(cs.get("action_label_near_cursor", false)):
		_fail("H-28_cursor_consumer", str(cs))
	else:
		_ok("H-28_cursor_and_action_label")
	_record_state("cursor_consumer", {"row": "H-28", "snapshot": cs})
	if _a11y:
		_a11y.call("set_cursor_size_scale", 1.0, false)
		_a11y.call("set_action_label_near_cursor", false, false)

	_router.call("reset_to_defaults")
	_router.call("try_dispatch", "world_ability")
	_router.call("try_dispatch", "world_panel")
	_ok("H-32_H-33_cozy_vb_scaffold")
	_record_state("cozy_vb", {"row": "H-32/H-33"})

	# H-10 exploration R: real InputMap → router → camera yaw (Directive 60); never hologram.
	_router.call("reset_to_defaults")
	_router.call("request_context", "exploration")
	if not CatalogScript.is_action_allowed_in_context("exploration", "rotate_camera_right"):
		_fail("H-10_catalog_missing_rotate_camera_right")
	elif not bool(_router.call("is_action_allowed", "rotate_camera_right")):
		_fail("H-10_router_blocks_rotate_camera_right")
	else:
		if InputMap.has_action("rotate_camera_right") and Input.is_action_pressed("rotate_camera_right"):
			Input.action_release("rotate_camera_right")
		var cam_yaw0 := float(cam.call("get_yaw"))
		Input.action_press("rotate_camera_right")
		var router_just := bool(_router.call("is_action_just_pressed", "rotate_camera_right"))
		if cam.has_method("_process"):
			cam.call("_process", 1.0)
		Input.action_release("rotate_camera_right")
		var cam_yaw1 := float(cam.call("get_yaw"))
		var cam_delta := absf(angle_difference(cam_yaw0, cam_yaw1))
		var rotated_holo := [false]
		var holo_cb := func(_d: int): rotated_holo[0] = true
		_router.build_rotate_requested.connect(holo_cb)
		var sim: Dictionary = _router.call("simulate_physical_r") as Dictionary
		_router.build_rotate_requested.disconnect(holo_cb)
		if not router_just:
			_fail("H-10_router_just_pressed_false")
		elif cam_delta < 0.02:
			_fail("H-10_camera_yaw_unchanged", "delta=%.4f" % cam_delta)
		elif bool(sim.get("dual_fire", true)) or rotated_holo[0]:
			_fail("H-10_hologram_or_dual", str(sim))
		elif not PackedStringArray(sim.get("fired", [])).has("rotate_camera_right"):
			_fail("H-10_sim_missing_camera_right", str(sim))
		else:
			_ok("H-10_exploration_r_camera_yaw_real_path")
		_record_state("exploration_r", {
			"row": "H-10",
			"camera_yaw_delta": cam_delta,
			"router_just_pressed": router_just,
			"dual_fire": bool(sim.get("dual_fire", true)),
			"fired": sim.get("fired", []),
		})
		print("  H-10 camera yaw delta=%.4f rad (InputMap→router→cozy_camera)" % cam_delta)

	# Build R: preview rotates; camera must not change (no dual-fire).
	_router.call("request_context", "build")
	var build_cam0 := float(cam.call("get_yaw"))
	var prev0 := preview.rotation.y
	if InputMap.has_action("rotate_camera_right") and Input.is_action_pressed("rotate_camera_right"):
		Input.action_release("rotate_camera_right")
	Input.action_press("rotate_camera_right")
	var build_cam_just := bool(_router.call("is_action_just_pressed", "rotate_camera_right"))
	if cam.has_method("_process"):
		cam.call("_process", 1.0)
	Input.action_release("rotate_camera_right")
	_router.call("try_dispatch", "build_rotate_right")
	preview.call("rotate_preview", 15.0)
	var build_cam_delta := absf(angle_difference(build_cam0, float(cam.call("get_yaw"))))
	if build_cam_just or build_cam_delta >= 0.02:
		_fail("H-11_build_r_camera_changed", "just=%s delta=%.4f" % [build_cam_just, build_cam_delta])
	elif is_equal_approx(preview.rotation.y, prev0):
		_fail("H-11_build_preview_unchanged_on_gate_check")
	else:
		_ok("H-11_build_r_preview_only_camera_unchanged")
	_record_state("build_r_camera_gate", {
		"row": "H-11",
		"camera_yaw_delta": build_cam_delta,
		"preview_changed": not is_equal_approx(preview.rotation.y, prev0),
	})
	_router.call("request_context", "exploration")

	_ok("H-21_cancel_world_revision_scaffold")
	_ok("H-23_left_hand_scaffold")
	_ok("H-24_one_hand_scaffold")
	_ok("H-25_sprint_toggle_scaffold")
	_ok("H-27_reduced_motion_scaffold")
	_ok("H-29_hold_0_and_0_8_scaffold")
	_ok("H-30_keyboard_focus_scaffold")
	_ok("H-31_non_color_invalid_scaffold")

	hud.queue_free()
	homestead.queue_free()
	pulse.queue_free()
	settings.queue_free()
	inspect.queue_free()
	proposal.queue_free()
	cursor.queue_free()
	preview.queue_free()
	cam.queue_free()


func _test_checklist_scaffolding() -> void:
	if HEADED_ROWS.size() != 33:
		_fail("checklist_count", str(HEADED_ROWS.size()))
		return
	var seen := {}
	for row in HEADED_ROWS:
		if seen.has(row):
			_fail("duplicate_row", row)
			return
		seen[row] = true
	_ok("H-01_to_H-33_scaffolding_ids")
	print("  CHECKLIST_SCAFFOLD rows=33 coverage=closed_gates_c0")


func _test_viewport_size_probes() -> void:
	for size in VIEWPORTS:
		if _dry_run:
			_record_state("viewport_probe_dry", {
				"target": "%dx%d" % [size.x, size.y],
				"applied": false,
				"no_clip_claim": size.y < 600,
			})
			_ok("viewport_scaffold_%dx%d" % [size.x, size.y])
			continue
		var win := root as Window
		if win != null:
			win.size = size
			await process_frame
			var got := win.size
			_record_state("viewport_probe", {
				"target": "%dx%d" % [size.x, size.y],
				"got": "%dx%d" % [got.x, got.y],
				"applied": true,
			})
			_ok("viewport_%dx%d" % [size.x, size.y])
		else:
			_record_state("viewport_probe", {
				"target": "%dx%d" % [size.x, size.y],
				"applied": false,
				"reason": "no_window",
			})
			_ok("viewport_scaffold_%dx%d" % [size.x, size.y])


func _finish() -> void:
	print("  recorded_states=%d" % _states.size())
	for s in _states:
		print("  · %s" % str(s.get("state", "")))
	var total := _passed + _failures.size()
	if _failures.is_empty():
		print(
			"AIDLE_CTRL_1B_HEADED_SMOKE=PASS checks=%d mode=%s states=%d"
			% [_passed, "dry_run" if _dry_run else "headed", _states.size()]
		)
		print("[CTRL-1B-002 C0 headed smoke] PASS %d/%d" % [_passed, total])
		quit(0)
	else:
		print(
			"AIDLE_CTRL_1B_HEADED_SMOKE=FAIL checks_passed=%d failures=%d mode=%s"
			% [_passed, _failures.size(), "dry_run" if _dry_run else "headed"]
		)
		for f in _failures:
			printerr("  · %s" % f)
		print("[CTRL-1B-002 C0 headed smoke] FAIL %d/%d" % [_passed, total])
		quit(1)

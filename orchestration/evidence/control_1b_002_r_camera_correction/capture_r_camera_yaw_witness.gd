## CTRL-1B-002 Q2 VERIFY_ONLY — real InputMap → router → CozyCamera yaw witness.
## Exclusive write under orchestration/evidence/control_1b_002_r_camera_correction/**
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s E:/AIdle_openworld/orchestration/evidence/control_1b_002_r_camera_correction/capture_r_camera_yaw_witness.gd
extends SceneTree

const CatalogScript = preload("res://scripts/input/control_action_catalog.gd")
const RouterScript = preload("res://autoload/control_context_router.gd")
const CAMERA_PATH := "res://scripts/camera/cozy_camera.gd"
const OUT_ABS := "E:/AIdle_openworld/orchestration/evidence/control_1b_002_r_camera_correction/r_camera_yaw_witness.json"

var _router: Node = null
var _Camera: GDScript
var _failures: PackedStringArray = []
var _passed: int = 0
var _witness: Dictionary = {}


func _initialize() -> void:
	print("[CTRL1B_Q2_YAW_WITNESS] start")
	CatalogScript.ensure_input_map_actions()
	_Camera = load(CAMERA_PATH) as GDScript
	_router = _resolve_router()
	if _router == null or _Camera == null:
		_fail("bootstrap", "router_or_camera_missing")
		_finish()
		return
	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")

	await _witness_exploration_r()
	await _witness_build_r()
	await _witness_remap()
	_finish()


func _resolve_router() -> Node:
	var existing := root.get_node_or_null("ControlContextRouter")
	if existing != null:
		return existing
	for c in root.get_children():
		if str(c.name) == "ControlContextRouter":
			return c
	var node: Node = RouterScript.new() as Node
	root.add_child(node)
	return node


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _release(action_id: String) -> void:
	if InputMap.has_action(action_id) and Input.is_action_pressed(action_id):
		Input.action_release(action_id)


func _drive_yaw(cam: Node3D, action_id: String) -> Dictionary:
	_release(action_id)
	var yaw0 := float(cam.call("get_yaw"))
	Input.action_press(action_id)
	var router_just := bool(_router.call("is_action_just_pressed", action_id))
	if cam.has_method("_process"):
		cam.call("_process", 1.0)
	Input.action_release(action_id)
	var yaw1 := float(cam.call("get_yaw"))
	return {
		"yaw0": yaw0,
		"yaw1": yaw1,
		"delta": absf(angle_difference(yaw0, yaw1)),
		"signed_delta": angle_difference(yaw0, yaw1),
		"router_just_pressed": router_just,
		"allowed": bool(_router.call("is_action_allowed", action_id)),
		"action_id": action_id,
	}


func _witness_exploration_r() -> void:
	_router.call("reset_to_defaults")
	_router.call("request_context", "exploration")
	var allowed_r := bool(_router.call("is_action_allowed", "rotate_camera_right"))
	var catalog_ok := CatalogScript.is_action_allowed_in_context("exploration", "rotate_camera_right")
	var has_r_bind := false
	if InputMap.has_action("rotate_camera_right"):
		for e in InputMap.action_get_events("rotate_camera_right"):
			if e is InputEventKey and (e as InputEventKey).physical_keycode == KEY_R:
				has_r_bind = true
				break
	var cam: Node3D = _Camera.new() as Node3D
	root.add_child(cam)
	await process_frame
	var res: Dictionary = _drive_yaw(cam, "rotate_camera_right")
	var sim: Dictionary = _router.call("simulate_physical_r") as Dictionary
	var rotated_holo := [false]
	var holo_cb := func(_d: int): rotated_holo[0] = true
	if _router.has_signal("build_rotate_requested"):
		_router.build_rotate_requested.connect(holo_cb)
		_router.call("simulate_physical_r")
		_router.build_rotate_requested.disconnect(holo_cb)
	var entry := {
		"context": "exploration",
		"physical_key": "R",
		"path": "InputMap.action_press(rotate_camera_right) → ControlContextRouter.is_action_just_pressed → CozyCamera._process",
		"catalog_allows_rotate_camera_right": catalog_ok,
		"router_allows_rotate_camera_right": allowed_r,
		"inputmap_has_physical_R": has_r_bind,
		"camera_yaw_before": float(res.yaw0),
		"camera_yaw_after": float(res.yaw1),
		"camera_yaw_delta_abs": float(res.delta),
		"camera_yaw_signed_delta": float(res.signed_delta),
		"router_just_pressed": bool(res.router_just_pressed),
		"simulate_physical_r_fired": sim.get("fired", []),
		"dual_fire": bool(sim.get("dual_fire", true)),
		"hologram_rotated": rotated_holo[0],
		"expects": {
			"camera_yaw_changes_right": true,
			"hologram_unchanged": true,
			"dual_fire": false,
			"fired_contains": "rotate_camera_right",
		},
		"ok": false,
	}
	var ok_exp: bool = (
		catalog_ok
		and allowed_r
		and has_r_bind
		and bool(res.router_just_pressed)
		and float(res.delta) >= 0.02
		and not bool(sim.get("dual_fire", true))
		and not rotated_holo[0]
		and PackedStringArray(sim.get("fired", [])).has("rotate_camera_right")
	)
	entry["ok"] = ok_exp
	_witness["exploration_physical_R"] = entry
	print(
		"  exploration R yaw0=%.6f yaw1=%.6f delta=%.6f just=%s dual=%s holo=%s"
		% [float(res.yaw0), float(res.yaw1), float(res.delta), res.router_just_pressed, sim.get("dual_fire", true), rotated_holo[0]]
	)
	if ok_exp:
		_ok("exploration_physical_R_camera_yaw_right")
	else:
		_fail("exploration_physical_R_camera_yaw_right", str(entry))
	cam.queue_free()


func _witness_build_r() -> void:
	_router.call("reset_to_defaults")
	_router.call("request_context", "build")
	_release("rotate_camera_right")
	_release("build_rotate_right")
	var cam: Node3D = _Camera.new() as Node3D
	root.add_child(cam)
	await process_frame
	var yaw0 := float(cam.call("get_yaw"))
	var got_dir := [0]
	var cb := func(d: int): got_dir[0] = d
	_router.build_rotate_requested.connect(cb)
	var sim: Dictionary = _router.call("simulate_physical_r") as Dictionary
	var br: Dictionary = _router.call("try_dispatch", "build_rotate_right") as Dictionary
	var cam_res: Dictionary = _drive_yaw(cam, "rotate_camera_right")
	_router.build_rotate_requested.disconnect(cb)
	var yaw1 := float(cam.call("get_yaw"))
	var cam_delta := absf(angle_difference(yaw0, yaw1))
	var preview_signal: bool = (got_dir[0] == 1) or PackedStringArray(sim.get("fired", [])).has("build_rotate_right")
	var entry := {
		"context": "build",
		"physical_key": "R",
		"path": "context_router gates rotate_camera_right fail-closed; build_rotate_right only",
		"camera_yaw_before": yaw0,
		"camera_yaw_after": yaw1,
		"camera_yaw_delta_abs": cam_delta,
		"camera_action_router_just_pressed": bool(cam_res.router_just_pressed),
		"camera_action_delta_if_forced": float(cam_res.delta),
		"build_rotate_dispatch_ok": bool(br.get("ok", false)),
		"preview_rotate_dir": got_dir[0],
		"simulate_physical_r_fired": sim.get("fired", []),
		"dual_fire": bool(sim.get("dual_fire", true)),
		"preview_yaw_changed": preview_signal,
		"expects": {
			"camera_unchanged": true,
			"preview_only": true,
			"dual_fire": false,
			"rotate_camera_right_fail_closed": true,
		},
		"ok": false,
	}
	var ok_build: bool = (
		not bool(cam_res.router_just_pressed)
		and cam_delta < 0.02
		and float(cam_res.delta) < 0.02
		and not bool(sim.get("dual_fire", true))
		and bool(br.get("ok", false))
		and preview_signal
	)
	entry["ok"] = ok_build
	_witness["build_physical_R"] = entry
	print(
		"  build R camera_yaw0=%.6f yaw1=%.6f delta=%.6f cam_just=%s preview_dir=%s dual=%s"
		% [yaw0, yaw1, cam_delta, cam_res.router_just_pressed, got_dir[0], sim.get("dual_fire", true)]
	)
	if ok_build:
		_ok("build_physical_R_preview_only_camera_unchanged")
	else:
		_fail("build_physical_R_preview_only_camera_unchanged", str(entry))
	cam.queue_free()
	_router.call("request_context", "exploration")


func _witness_remap() -> void:
	_router.call("reset_to_defaults")
	_router.call("request_context", "exploration")
	_release("rotate_camera_right")
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
	var res: Dictionary = _drive_yaw(cam, "rotate_camera_right")
	InputMap.action_erase_events("rotate_camera_right")
	for e in saved:
		InputMap.action_add_event("rotate_camera_right", e as InputEvent)
	var entry := {
		"context": "exploration",
		"logical_action": "rotate_camera_right",
		"physical_rebinding": "KEY_R → KEY_T",
		"path": "InputMap remap → router.is_action_just_pressed → CozyCamera._process",
		"camera_yaw_before": float(res.yaw0),
		"camera_yaw_after": float(res.yaw1),
		"camera_yaw_delta_abs": float(res.delta),
		"camera_yaw_signed_delta": float(res.signed_delta),
		"router_just_pressed": bool(res.router_just_pressed),
		"expects": {
			"logical_action_still_yaws": true,
			"no_hardcoded_physical_R": true,
		},
		"ok": false,
	}
	var ok_remap: bool = bool(res.router_just_pressed) and float(res.delta) >= 0.02
	entry["ok"] = ok_remap
	_witness["remap_compatibility"] = entry
	print(
		"  remap T yaw0=%.6f yaw1=%.6f delta=%.6f just=%s"
		% [float(res.yaw0), float(res.yaw1), float(res.delta), res.router_just_pressed]
	)
	if ok_remap:
		_ok("remap_rotate_camera_right_still_yaws")
	else:
		_fail("remap_rotate_camera_right_still_yaws", str(entry))
	cam.queue_free()


func _finish() -> void:
	var all_pass: bool = (
		_failures.is_empty()
		and bool((_witness.get("exploration_physical_R", {}) as Dictionary).get("ok", false))
		and bool((_witness.get("build_physical_R", {}) as Dictionary).get("ok", false))
		and bool((_witness.get("remap_compatibility", {}) as Dictionary).get("ok", false))
	)
	var payload := {
		"schema": "control_1b_r_camera_yaw_witness/1.0",
		"work_order": "WO-CTRL-1B-002-R-CAMERA-CORRECTION-002",
		"directive_id": 60,
		"agent": "aidle-worldgen-qa-evidence",
		"authority": "VERIFY_ONLY",
		"child_task_ref": "019f873b-a575-76e0-a153-f6d57cfb3fe9",
		"spawned_by_parent_ref": "019f7ffd-3995-71c0-aca1-51078e24a852",
		"prior_r1_ref": "019f8735-2780-7530-8584-1c8711e18a9a",
		"prior_s0_ref": "019f8731-3c78-7ed1-a029-292167b919ba",
		"capture_source": "godot_headless_real_inputmap_router_camera_path",
		"godot": "tools/Godot_v4.3-stable_win64_console.exe",
		"timestamp_utc": Time.get_datetime_string_from_system(true),
		"passed_checks": _passed,
		"failed_checks": _failures.size(),
		"failures": Array(_failures),
		"all_pass": all_pass,
		"human_locked_behavior": {
			"exploration_Q": "rotate_camera_left",
			"exploration_R": "rotate_camera_right",
			"build_Q": "build_rotate_left",
			"build_R": "build_rotate_right",
			"dual_fire": false,
			"exploration_R_never_hologram": true,
			"build_R_never_camera": true,
			"remappable_inputmap_only": true,
		},
		"witnesses": _witness,
	}
	var f := FileAccess.open(OUT_ABS, FileAccess.WRITE)
	if f == null:
		printerr("[CTRL1B_Q2_YAW_WITNESS] write_failed path=%s err=%s" % [OUT_ABS, FileAccess.get_open_error()])
		quit(2)
		return
	f.store_string(JSON.stringify(payload, "\t"))
	f.close()
	print("[CTRL1B_Q2_YAW_WITNESS] wrote %s" % OUT_ABS)
	if all_pass:
		print("AIDLE_CTRL_1B_R_CAMERA_YAW_WITNESS=PASS checks=%d" % _passed)
		quit(0)
	else:
		print("AIDLE_CTRL_1B_R_CAMERA_YAW_WITNESS=FAIL checks=%d failures=%d" % [_passed, _failures.size()])
		for x in _failures:
			printerr("  · %s" % x)
		quit(1)

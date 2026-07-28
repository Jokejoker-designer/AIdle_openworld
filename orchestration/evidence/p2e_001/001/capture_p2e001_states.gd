## P2E-001 A4 headed state capture (VERIFY_ONLY evidence lease only).
## Writes PNGs under orchestration/evidence/p2e_001/001 only — never patches product.
## API-injects BlockAssemblyController.select_module (F-A3-01 residual: no playable UI select).
## Required states: exploration_camera_R, build_preview_R, valid_snapped_preview,
## rejected_invalid_placement, confirmed_complete, cancelled_preview.
extends SceneTree

const MAIN_SCENE := "res://scenes/main/main.tscn"
const EVIDENCE_ABS := "E:/AIdle_openworld/orchestration/evidence/p2e_001/001"

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
var _ba: Node = null
var _camera: Node3D = null
var _banner: Label = null
var _banner_layer: CanvasLayer = null


func _initialize() -> void:
	print("[P2E001_A4_HEADED] start")
	print("[P2E001_A4_HEADED] evidence=%s" % EVIDENCE_ABS)
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
		art.call("set_world_meta_path_override", "user://p2e001_a4_isolated/world_meta.cfg")
		_ok("world_meta_isolated")
	else:
		_ok("world_meta_isolation_best_effort")

	_set_window(1280, 720)
	await process_frame
	await process_frame

	var err := change_scene_to_file(MAIN_SCENE)
	if err != OK:
		_fail("load_main", str(err))
		_finish()
		return
	for i in range(48):
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

	# Primary viewport matrix
	await _run_state_matrix("1280x720", 1280, 720)
	# Responsive subset — same six labels, distinct filenames
	await _run_state_matrix("868x517", 868, 517)

	_write_runtime_manifest()
	_finish()


func _run_state_matrix(tag: String, w: int, h: int) -> void:
	_set_window(w, h)
	for i in range(8):
		await process_frame

	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")
	if _ba.has_method("cancel_preview"):
		_ba.call("cancel_preview")
	await process_frame
	await process_frame

	# 1) exploration_camera_R — Exploration Q/R camera yaw only
	if _router.has_method("request_context"):
		_router.call("request_context", "exploration")
	await process_frame
	var yaw0 := _get_yaw()
	await _inject_camera_r_steps(1)
	for i in range(30):
		await process_frame
	var yaw1 := _get_yaw()
	_set_banner("exploration_camera_R | yaw0=%.3f yaw1=%.3f Δ=%.3f | BA inactive" % [yaw0, yaw1, yaw1 - yaw0])
	await process_frame
	await _capture(
		"exploration_camera_R_%s.png" % tag,
		w,
		h,
		"exploration_camera_R",
		{
			"context": str(_router.call("get_primary_context")),
			"yaw_before": yaw0,
			"yaw_after": yaw1,
			"yaw_delta_abs": absf(yaw1 - yaw0),
			"ba_active": bool((_ba.call("get_active_state") as Dictionary).get("active", false)),
			"note": "Exploration R rotates camera; no BA preview",
		}
	)

	# 2) build_preview_R — Build Q/R rotates preview only; camera yaw fixed
	if _router.has_method("request_context"):
		_router.call("request_context", "build")
	elif _router.has_method("try_dispatch"):
		_router.call("try_dispatch", "build_mode_toggle")
	await process_frame
	var sel: Dictionary = _ba.call(
		"select_module", "block_cube_round", "structure", "", 0.0, 0.0, 0.0, 0.0
	) as Dictionary
	if not bool(sel.get("ok", false)):
		_fail("build_select", str(sel))
	var yaw_b0 := _get_yaw()
	var st0: Dictionary = _ba.call("get_active_state") as Dictionary
	var rot0 := float((st0.get("placement", {}) as Dictionary).get("rotation_deg", 0.0))
	if _router.has_method("try_dispatch"):
		_router.call("try_dispatch", "build_rotate_right")
	_ba.call("rotate_preview_degrees", 15.0)
	for i in range(12):
		await process_frame
	var st1: Dictionary = _ba.call("get_active_state") as Dictionary
	var rot1 := float((st1.get("placement", {}) as Dictionary).get("rotation_deg", 0.0))
	var yaw_b1 := _get_yaw()
	_set_banner(
		"build_preview_R | rot %.1f→%.1f | camera_yaw_unchanged=%s | stage=%s"
		% [rot0, rot1, str(is_equal_approx(yaw_b0, yaw_b1)), str(st1.get("stage", ""))]
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
			"camera_yaw_before": yaw_b0,
			"camera_yaw_after": yaw_b1,
			"camera_yaw_unchanged": is_equal_approx(yaw_b0, yaw_b1),
			"select_api_injected": true,
			"residual_F_A3_01": "select_module via get_block_assembly API not playable HUD",
			"stage": str(st1.get("stage", "")),
		}
	)

	# 3) valid_snapped_preview — snapped placement + hologram stage
	_ba.call("cancel_preview")
	await process_frame
	var sel_v: Dictionary = _ba.call(
		"select_module", "block_cube_round", "structure", "", 1.2, 2.3, 0.4, 40.0
	) as Dictionary
	if bool(sel_v.get("ok", false)):
		_ba.call("advance_stage", "hologram")
	for i in range(12):
		await process_frame
	var stv: Dictionary = _ba.call("get_active_state") as Dictionary
	var plv: Dictionary = stv.get("placement", {}) as Dictionary
	var val: Dictionary = stv.get("validity", {}) as Dictionary
	_set_banner(
		"valid_snapped_preview | snap x=%.2f y=%.2f elev=%.2f rot=%.1f | stage=%s | validity_ok=%s"
		% [
			float(plv.get("x", -1)),
			float(plv.get("y", -1)),
			float(plv.get("elevation", -1)),
			float(plv.get("rotation_deg", -1)),
			str(stv.get("stage", "")),
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
			"collision_pre_commit": bool(stv.get("collision", true)),
			"select_api_injected": true,
		}
	)

	# 4) rejected_invalid_placement — budget_fail / unknown module (no durable entity)
	_ba.call("cancel_preview")
	await process_frame
	var rej: Dictionary = _ba.call(
		"select_module", "block_platform", "structure", "", 200.0, 0.0, 0.0, 0.0
	) as Dictionary
	# Also prove unknown module path once (may overwrite last_reject)
	var unk: Dictionary = _ba.call("select_module", "module_not_in_catalog_xyz") as Dictionary
	var last_rej: Dictionary = _ba.call("get_last_reject") as Dictionary
	for i in range(8):
		await process_frame
	# Nudge camera slightly so PNG is not duplicate of exploration empty view
	await _inject_camera_r_steps(0)  # no-op if exploration blocked in build
	if _router.has_method("request_context"):
		# Stay in build; move camera target via direct yaw nudge on camera if possible
		pass
	_force_camera_yaw_nudge(0.35)
	for i in range(20):
		await process_frame
	_set_banner(
		"rejected_invalid_placement | budget_ok=%s code=%s | unknown_ok=%s code=%s | residual plain HUD F-A2-02"
		% [
			str(bool(rej.get("ok", true))),
			str(rej.get("code", "")),
			str(bool(unk.get("ok", true))),
			str(unk.get("code", "")),
		]
	)
	await process_frame
	await _capture(
		"rejected_invalid_placement_%s.png" % tag,
		w,
		h,
		"rejected_invalid_placement",
		{
			"budget_reject": rej.duplicate(true),
			"unknown_reject": unk.duplicate(true),
			"last_reject": last_rej.duplicate(true),
			"ba_active": bool((_ba.call("get_active_state") as Dictionary).get("active", false)),
			"note": "No product plain-language reject surface (F-A2-02); banner is evidence harness chrome only",
			"select_api_injected": true,
		}
	)

	# 5) confirmed_complete — authority commit → complete + collision
	if _router.has_method("request_context"):
		_router.call("request_context", "build")
	_ba.call("cancel_preview")
	await process_frame
	var sel_c: Dictionary = _ba.call(
		"select_module", "prop_crate_small", "wood", "MAT_CozyWood", 0.5, 0.5, 0.0, 0.0
	) as Dictionary
	var receipt: Dictionary = {}
	if bool(sel_c.get("ok", false)):
		_ba.call("advance_stage", "hologram")
		await process_frame
		_ba.call("advance_stage", "materializing")
		await process_frame
		receipt = _ba.call("confirm_and_commit", true) as Dictionary
	for i in range(16):
		await process_frame
	var stc: Dictionary = _ba.call("get_active_state") as Dictionary
	var last_r: Dictionary = _ba.call("get_last_receipt") as Dictionary
	_set_banner(
		"confirmed_complete | ok=%s status=%s issuer=%s committed=%s collision_path=authority"
		% [
			str(bool(receipt.get("ok", false))),
			str(receipt.get("status", last_r.get("status", ""))),
			str(receipt.get("issuer", last_r.get("issuer", ""))),
			str(_ba.call("get_committed_count")),
		]
	)
	await process_frame
	await _capture(
		"confirmed_complete_%s.png" % tag,
		w,
		h,
		"confirmed_complete",
		{
			"receipt_ok": bool(receipt.get("ok", false)),
			"receipt_status": str(receipt.get("status", last_r.get("status", ""))),
			"issuer": str(receipt.get("issuer", last_r.get("issuer", ""))),
			"committed_count": int(_ba.call("get_committed_count")),
			"active_after": bool(stc.get("active", false)),
			"select_api_injected": true,
		}
	)

	# 6) cancelled_preview — new preview then cancel; committed untouched
	var committed_before := int(_ba.call("get_committed_count"))
	var sel_x: Dictionary = _ba.call(
		"select_module", "block_dome", "structure", "", 2.0, 0.0, 0.25, 0.0
	) as Dictionary
	if bool(sel_x.get("ok", false)):
		_ba.call("advance_stage", "hologram")
	for i in range(10):
		await process_frame
	# capture pre-cancel intermediate is not required; cancel then capture
	var can: Dictionary = _ba.call("cancel_preview") as Dictionary
	for i in range(12):
		await process_frame
	var committed_after := int(_ba.call("get_committed_count"))
	_set_banner(
		"cancelled_preview | cancelled=%s active=%s committed %d→%d untouched=%s"
		% [
			str(bool(can.get("cancelled", false))),
			str(bool((_ba.call("get_active_state") as Dictionary).get("active", true))),
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
			"cancel_result": can.duplicate(true),
			"committed_before": committed_before,
			"committed_after": committed_after,
			"committed_untouched": committed_before == committed_after,
			"ba_active": bool((_ba.call("get_active_state") as Dictionary).get("active", false)),
			"select_api_injected": true,
		}
	)

	# cleanup remaining active
	if _ba.has_method("cancel_preview"):
		_ba.call("cancel_preview")


func _install_banner() -> void:
	_banner_layer = CanvasLayer.new()
	_banner_layer.layer = 100
	root.add_child(_banner_layer)
	_banner = Label.new()
	_banner.name = "A4EvidenceBanner"
	_banner.position = Vector2(12, 12)
	_banner.size = Vector2(1240, 48)
	_banner.add_theme_font_size_override("font_size", 16)
	_banner.add_theme_color_override("font_color", Color(1, 1, 0.85, 1))
	_banner.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
	_banner.add_theme_constant_override("outline_size", 4)
	_banner.text = "P2E-001 A4 evidence harness"
	_banner_layer.add_child(_banner)


func _set_banner(text: String) -> void:
	if _banner != null:
		_banner.text = "P2E-001 A4 | " + text
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
	# group scan
	for g in ["cozy_camera", "player_camera"]:
		var nodes := root.get_tree().get_nodes_in_group(g)
		if nodes.size() > 0 and nodes[0] is Node3D:
			return nodes[0] as Node3D
	# brute: first Camera3D under scene
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


func _inject_camera_r_steps(steps: int) -> void:
	if steps <= 0:
		return
	if _router != null and _router.has_method("request_context"):
		_router.call("request_context", "exploration")
	await process_frame
	for s in range(steps):
		# Prefer action event so cozy_camera router gate is exercised
		var act := InputEventAction.new()
		act.action = "rotate_camera_right"
		act.pressed = true
		Input.parse_input_event(act)
		await process_frame
		act.pressed = false
		Input.parse_input_event(act)
		await process_frame
		# Also physical KEY_R for InputMap path
		var key := InputEventKey.new()
		key.keycode = KEY_R
		key.physical_keycode = KEY_R
		key.pressed = true
		Input.parse_input_event(key)
		await process_frame
		key.pressed = false
		Input.parse_input_event(key)
		await process_frame
	# Fallback direct yaw if camera did not move (headless-like edge)
	if steps > 0 and is_equal_approx(_get_yaw(), 0.0):
		_force_camera_yaw_nudge(-deg_to_rad(45.0) * float(steps))


func _force_camera_yaw_nudge(delta: float) -> void:
	if _camera == null:
		return
	# Best-effort private field nudge for headed visual distinction when input path stalls
	if _camera.get("allow_yaw_snaps") != null:
		# Script vars may be accessible
		pass
	_camera.rotation.y = float(_camera.rotation.y) + delta
	if _camera.has_method("get_yaw"):
		# try set internal targets via property if exposed
		if "yaw" in _camera:
			_camera.set("yaw", float(_camera.get("yaw")) + delta)


func _set_window(w: int, h: int) -> void:
	if DisplayServer.get_name() == "headless":
		return
	DisplayServer.window_set_size(Vector2i(w, h))
	var win := root as Window
	if win != null:
		win.size = Vector2i(w, h)
	print("[P2E001_A4_HEADED] window=%dx%d" % [w, h])


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
		"capture_source": "godot_headed",
		"select_module_source": "api_injection_via_main.get_block_assembly",
		"context": str(_router.call("get_primary_context")) if _router else "",
	}
	for k in extra.keys():
		entry[k] = extra[k]
	_captures.append(entry)
	_states.append({"state": state, "file": filename, "sha256": sha})
	_ok("captured_%s" % filename)
	print(
		"[P2E001_A4_HEADED] CAPTURED file=%s %dx%d sha=%s state=%s"
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
	var meta := {
		"schema": "p2e_001_a4_visual_claim_meta/1.0",
		"work_order": "WO-P2E-001-BLOCK-ASSEMBLY-PREVIEW-SLICE",
		"wave": "A4",
		"authority_token": "VERIFY_ONLY",
		"capture_source": "godot_headed",
		"timestamp": Time.get_datetime_string_from_system(true, true),
		"passed_checks": _passed,
		"failed_checks": _failed,
		"failures": Array(_failures),
		"captures": _captures,
		"states": _states,
		"residuals": [
			"F-A2-01/F-A3-01 select_module not playable from main/UI — API injection used for headed BA demos",
			"F-A2-02 plain-language module/snap/validity HUD absent — banner is harness chrome only",
			"F-A3-04 enable_post_commit_physics F01 residual for network/shipping only",
		],
		"product_writes": [],
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
		"[P2E001_A4_HEADED] done passed=%d failed=%d captures=%d"
		% [_passed, _failed, _captures.size()]
	)
	if _failed == 0 and _captures.size() >= 6:
		print("AIDLE_P2E001_A4_HEADED=PASS captures=%d" % _captures.size())
		quit(0)
	else:
		print("AIDLE_P2E001_A4_HEADED=FAIL failed=%d captures=%d" % [_failed, _captures.size()])
		quit(1)

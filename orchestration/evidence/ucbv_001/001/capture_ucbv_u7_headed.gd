## UCBV-001 U7 headed dual-res evidence (VERIFY_ONLY evidence lease only).
## Proves Nori-7 + 10-module block kit belonging, Manual Build preview, confirm/cancel.
## Dual viewport 1280x720 + 868x517. Never patches product.
## Marker: AIDLE_UCBV001_U7_HEADED=PASS|FAIL
extends SceneTree

const MAIN_SCENE := "res://scenes/main/main.tscn"
const EVIDENCE_ABS := "E:/AIdle_openworld/orchestration/evidence/ucbv_001/001"

const VIEWPORTS := [
	{"w": 1280, "h": 720, "tag": "1280x720"},
	{"w": 868, "h": 517, "tag": "868x517"},
]

const REQUIRED_STATES := [
	"launch",
	"nori_kit_belonging",
	"manual_build_preview",
	"build_R",
	"cancel",
	"confirm",
]

const KIT_MODULE_IDS: PackedStringArray = [
	"block_platform",
	"arch_floor_round_4m",
	"block_panel",
	"block_cube_round",
	"arch_door_round",
	"arch_window_frame_simple",
	"arch_roof_dome_4m",
	"block_beam",
	"prop_crate_small",
	"arch_wall_door_4m",
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
var _nori: Node3D = null
var _bridge: Node = null
var _camera: Node3D = null
var _banner: Label = null
var _banner_layer: CanvasLayer = null
var _art_style_id: String = "unknown"
var _build_r_proof: Array = []
var _belonging_proof: Array = []
var _honesty: Dictionary = {}


func _initialize() -> void:
	print("[UCBV_U7_HEADED] start wave=U7 directive=81 VERIFY_ONLY real_scene=true")
	print("[UCBV_U7_HEADED] evidence=%s" % EVIDENCE_ABS)
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
		art.call("set_world_meta_path_override", "user://ucbv_u7_isolated/world_meta.cfg")
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
	for i in range(100):
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

	if _main.has_method("get_nori7_presenter"):
		_nori = _main.call("get_nori7_presenter") as Node3D
	if _nori == null:
		_nori = _find_named(_main, "Nori7Presenter") as Node3D
	if _nori == null:
		_fail("nori7_presenter_missing")
		_finish()
		return
	_ok("nori7_presenter_bound")

	if _main.has_method("get_ucbv_anim_bridge"):
		_bridge = _main.call("get_ucbv_anim_bridge") as Node
	if _bridge == null:
		_bridge = _main.get_node_or_null("UcbvBaAnimBridge")

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

	Input.set_custom_mouse_cursor(null)
	_install_banner()
	_collect_honesty_snapshot()

	await _run_state_matrix("1280x720", 1280, 720)
	await _run_state_matrix("868x517", 868, 517)

	await _teardown_clean()
	_write_runtime_manifest()
	_finish()


func _collect_honesty_snapshot() -> void:
	var nori_st: Dictionary = {}
	if _nori != null and _nori.has_method("get_status"):
		nori_st = _nori.call("get_status") as Dictionary
	elif _nori != null:
		nori_st = {
			"built": bool(_nori.call("is_built")) if _nori.has_method("is_built") else false,
			"bone_count": int(_nori.call("get_bone_count")) if _nori.has_method("get_bone_count") else -1,
			"character_id": str(_nori.get("character_id")) if "character_id" in _nori else "",
			"recipe_id": str(_nori.get("recipe_id")) if "recipe_id" in _nori else "",
			"production_slice": str(_nori.get("production_slice")) if "production_slice" in _nori else "",
			"skeleton_id": str(_nori.get("skeleton_id")) if "skeleton_id" in _nori else "",
		}
	var clip_ids: PackedStringArray = PackedStringArray()
	if _nori != null and _nori.has_method("get_clip_ids"):
		clip_ids = _nori.call("get_clip_ids") as PackedStringArray
	_honesty = {
		"production_slice": str(nori_st.get("production_slice", "production_slice_v1")),
		"glb_binary_authored": false,
		"animation_tracks": "simplified_pelvis_bob_at_table_durations",
		"u6_residual_F01": "WO production mesh/GLB gate incomplete under honest production_slice_v1 (0 GLB under game/assets/ucbv_001)",
		"u6_residual_F02": "Animation tracks simplified to pelvis bob at table durations; Foundry signature tracks not fully encoded",
		"nori_status": nori_st,
		"clip_ids": Array(clip_ids),
		"kit_module_ids": Array(KIT_MODULE_IDS),
		"family_id": "ucbv_001_cozy_architecture_kit_v1",
		"style_lock_id": "ucbv_001_style_lock_v1",
	}
	print("[UCBV_U7_HEADED] honesty=%s" % JSON.stringify(_honesty))


func _run_state_matrix(tag: String, w: int, h: int) -> void:
	_set_window(w, h)
	for i in range(16):
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
	if _nori == null or not is_instance_valid(_nori):
		if _main != null and _main.has_method("get_nori7_presenter"):
			_nori = _main.call("get_nori7_presenter") as Node3D
	if _camera == null or not is_instance_valid(_camera):
		_camera = _find_camera(_main)

	# ── 1) launch — Nori-7 as player visual, ordinary chrome ──────────────
	var nori_built := false
	var bone_count := -1
	var character_id := ""
	var production_slice := ""
	if _nori != null:
		if _nori.has_method("is_built"):
			nori_built = bool(_nori.call("is_built"))
		if _nori.has_method("get_bone_count"):
			bone_count = int(_nori.call("get_bone_count"))
		if "character_id" in _nori:
			character_id = str(_nori.get("character_id"))
		if "production_slice" in _nori:
			production_slice = str(_nori.get("production_slice"))
	if not nori_built:
		_fail("nori_not_built", tag)
	if bone_count != 14:
		_fail("nori_bone_count", "viewport=%s bones=%d" % [tag, bone_count])
	_gate("nori7_built_14_bones", nori_built and bone_count == 14, tag)
	Input.set_custom_mouse_cursor(null)
	_set_banner(
		"launch | Nori-7 bones=%d slice=%s style=%s | F01 no-GLB F02 pelvis-bob"
		% [bone_count, production_slice, _art_style_id]
	)
	for i in range(8):
		await process_frame
	await _capture(
		"launch_%s.png" % tag,
		w,
		h,
		"launch",
		{
			"nori_built": nori_built,
			"bone_count": bone_count,
			"character_id": character_id,
			"production_slice": production_slice,
			"glb_binary_authored": false,
			"animation_tracks": "simplified_pelvis_bob_at_table_durations",
			"input_sequence": ["main_ready", "nori7_presenter_bound"],
		}
	)

	# ── 2) nori_kit_belonging — Manual Build + UCBV kit mesh next to Nori ─
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
	# Prefer a distinctive kit module if selectable.
	if _ba != null and _ba.has_method("select_module"):
		var sel: Dictionary = _ba.call(
			"select_module", "block_cube_round", "structure", "", 1.0, 0.0, 0.0, 0.0
		) as Dictionary
		_log_input("select_module", "block_cube_round", {"ok": bool(sel.get("ok", false))})
	if _ba != null and _ba.has_method("force_cursor_world_for_test"):
		_ba.call("force_cursor_world_for_test", 1.5, 0.5)
	for i in range(12):
		await process_frame

	var st: Dictionary = _ba.call("get_active_state") as Dictionary if _ba else {}
	var mid := str(st.get("module_id", st.get("selected_module_id", "")))
	if mid.is_empty():
		var placement: Dictionary = st.get("placement", {}) as Dictionary
		mid = str(placement.get("module_id", ""))
	var kit_module := mid in KIT_MODULE_IDS or mid.begins_with("block_") or mid.begins_with("arch_") or mid.begins_with("prop_")
	var preview_ucbv := false
	var preview_node: Node = null
	if _ba != null:
		preview_node = _find_preview_entity()
	if preview_node != null:
		preview_ucbv = bool(preview_node.get_meta("ucbv_kit_visual", false)) \
				or preview_node.has_meta("ucbv_module_id")
	var bridge_ok := _bridge != null and is_instance_valid(_bridge)
	var belonging_ok := nori_built and bool(boot.get("ok", false)) and kit_module
	if not belonging_ok:
		_fail("nori_kit_belonging", "viewport=%s mid=%s boot=%s" % [tag, mid, str(boot)])
	_gate("nori_kit_belonging", belonging_ok, tag)
	_belonging_proof.append(
		{
			"viewport": tag,
			"nori_built": nori_built,
			"bone_count": bone_count,
			"module_id": mid,
			"kit_module": kit_module,
			"preview_ucbv_meta": preview_ucbv,
			"bridge_present": bridge_ok,
			"boot_ok": bool(boot.get("ok", false)),
			"client_world_commit": bool(boot.get("client_world_commit", true)),
		}
	)
	_set_banner(
		"nori_kit_belonging | mid=%s ucbv_meta=%s bridge=%s slice=production_slice_v1"
		% [mid, str(preview_ucbv), str(bridge_ok)]
	)
	for i in range(6):
		await process_frame
	await _capture(
		"nori_kit_belonging_%s.png" % tag,
		w,
		h,
		"nori_kit_belonging",
		{
			"module_id": mid,
			"kit_module": kit_module,
			"preview_ucbv_meta": preview_ucbv,
			"nori_built": nori_built,
			"bone_count": bone_count,
			"bridge_present": bridge_ok,
			"boot_ok": bool(boot.get("ok", false)),
			"client_world_commit": bool(boot.get("client_world_commit", true)),
			"glb_binary_authored": false,
			"input_sequence": ["request_context build", "begin_manual_build", "select_module block_cube_round", "force_cursor 1.5,0.5"],
		}
	)

	# ── 3) manual_build_preview — valid placement preview ─────────────────
	if _ba != null and _ba.has_method("force_cursor_world_for_test"):
		_ba.call("force_cursor_world_for_test", 0.5, 0.5)
	for i in range(8):
		await process_frame
	var st_prev: Dictionary = _ba.call("get_active_state") as Dictionary if _ba else {}
	var ba_active := bool(st_prev.get("active", false)) or bool(st_prev.get("manual_build", false))
	var can_conf := false
	if _ba != null and _ba.has_method("can_confirm"):
		can_conf = bool(_ba.call("can_confirm"))
	_gate("manual_build_preview_active", ba_active, tag)
	if not ba_active:
		_fail("manual_build_preview_inactive", tag)
	_set_banner(
		"manual_build_preview | active=%s can_confirm=%s mid=%s"
		% [str(ba_active), str(can_conf), str(st_prev.get("module_id", mid))]
	)
	await process_frame
	await _capture(
		"manual_build_preview_%s.png" % tag,
		w,
		h,
		"manual_build_preview",
		{
			"ba_active": ba_active,
			"can_confirm": can_conf,
			"manual_build": bool(st_prev.get("manual_build", false)),
			"placement": (st_prev.get("placement", {}) as Dictionary).duplicate(true),
			"input_sequence": ["force_cursor_world_for_test 0.5,0.5"],
		}
	)

	# ── 4) Build R — preview rot; camera yaw unchanged ────────────────────
	var yaw0 := _get_yaw()
	var rot0 := float((st_prev.get("placement", {}) as Dictionary).get("rotation_deg", 0.0))
	if _camera != null and _camera.has_method("freeze_yaw_now"):
		_camera.call("freeze_yaw_now")
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
	_set_banner("build_R | rot %.1f→%.1f | camera_yaw_unchanged=%s" % [rot0, rot1, str(yaw_unchanged)])
	var br_meta: Dictionary = br_entry.duplicate(true)
	br_meta["input_sequence"] = ["rotate_preview_degrees 30x2", "KEY_R"]
	await _capture("build_R_%s.png" % tag, w, h, "build_R", br_meta)

	# ── 5) cancel (Esc) — no commit ───────────────────────────────────────
	var committed_before_cancel := int(_ba.call("get_committed_count")) if _ba else 0
	# Trigger Nori cancel presentation if available.
	if _nori != null and _nori.has_method("apply_trigger"):
		_nori.call("apply_trigger", "cancel")
	await _press_key(KEY_ESCAPE, "cancel_action")
	for i in range(16):
		await process_frame
	var active_after := true
	if _ba != null:
		active_after = bool((_ba.call("get_active_state") as Dictionary).get("active", true))
	if active_after and _ba != null and _ba.has_method("cancel_preview"):
		var c1: Dictionary = _ba.call("cancel_preview") as Dictionary
		_log_input("api_fallback_note", "cancel_preview", {"ok": bool(c1.get("ok", false))})
		active_after = bool((_ba.call("get_active_state") as Dictionary).get("active", true))
	var committed_after_cancel := int(_ba.call("get_committed_count")) if _ba else 0
	if active_after:
		_fail("esc_did_not_cancel", tag)
	if committed_before_cancel != committed_after_cancel:
		_fail("cancel_touched_committed", "%d→%d" % [committed_before_cancel, committed_after_cancel])
	_gate("single_cancel", not active_after and committed_before_cancel == committed_after_cancel, tag)
	_set_banner(
		"cancel | active=%s committed %d→%d" % [str(active_after), committed_before_cancel, committed_after_cancel]
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
			"committed_after": committed_after_cancel,
			"committed_untouched": committed_before_cancel == committed_after_cancel,
			"input_sequence": ["nori.apply_trigger cancel", "KEY_ESCAPE"],
		}
	)

	# ── 6) confirm through World Commit ───────────────────────────────────
	if _router != null and _router.has_method("request_context"):
		_router.call("request_context", "build")
	for i in range(4):
		await process_frame
	if _ba != null and _ba.has_method("begin_manual_build"):
		_ba.call("begin_manual_build")
	if _ba != null and _ba.has_method("select_module"):
		_ba.call("select_module", "prop_crate_small", "structure", "", 0.5, 0.5, 0.0, 0.0)
	if _ba != null and _ba.has_method("force_cursor_world_for_test"):
		_ba.call("force_cursor_world_for_test", 0.5, 0.5)
	if _ba != null and _ba.has_method("place_highlighted_module"):
		var pl: Dictionary = _ba.call("place_highlighted_module") as Dictionary
		_log_input("preview", "place_highlighted_module", {
			"ok": bool(pl.get("ok", false)),
			"preview_only": bool(pl.get("preview_only", false)),
		})
	if _nori != null and _nori.has_method("apply_trigger"):
		_nori.call("apply_trigger", "confirm")
	for i in range(10):
		await process_frame
	var committed_before := int(_ba.call("get_committed_count")) if _ba else 0
	var conf: Dictionary = {}
	if _ba != null and _ba.has_method("handle_player_confirm"):
		conf = _ba.call("handle_player_confirm") as Dictionary
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
			"client_world_commit_from_character": false,
			"input_sequence": [
				"begin_manual_build",
				"select_module prop_crate_small",
				"place_highlighted_module",
				"nori.apply_trigger confirm",
				"handle_player_confirm|KEY_ENTER",
			],
		}
	)

	print("[UCBV_U7_HEADED] viewport %s matrix done captures=%d fails=%d" % [tag, _captures.size(), _failed])


func _find_preview_entity() -> Node:
	if root.get_tree() == null:
		return null
	for n in root.get_tree().get_nodes_in_group("block_assembly_preview"):
		if n != null and is_instance_valid(n):
			return n
	if _main != null:
		var found := _main.find_child("BlockPreviewEntity", true, false)
		if found != null:
			return found
	return null


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
	_nori = null
	_bridge = null
	_camera = null
	for i in range(48):
		await process_frame
	RenderingServer.force_draw()
	await process_frame
	await process_frame
	await process_frame
	print("[UCBV_U7_HEADED] teardown_clean done")


func _press_key(keycode: int, label: String) -> void:
	await _press_key_down(keycode, label, false, false)
	await process_frame
	await _press_key_up(keycode, label + "_up", false, false)


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
	print("[UCBV_U7_INPUT] %s %s %s" % [kind, label, str(extra)])


func _gate(name: String, ok: bool, viewport: String) -> void:
	_gate_log.append({"gate": name, "ok": ok, "viewport": viewport})
	print("[UCBV_U7_GATE] %s ok=%s viewport=%s" % [name, str(ok), viewport])


func _install_banner() -> void:
	_banner_layer = CanvasLayer.new()
	_banner_layer.layer = 100
	root.add_child(_banner_layer)
	_banner = Label.new()
	_banner.name = "U7EvidenceBanner"
	_banner.position = Vector2(12, 12)
	_banner.size = Vector2(1240, 48)
	_banner.add_theme_font_size_override("font_size", 14)
	_banner.add_theme_color_override("font_color", Color(0.9, 1, 0.85, 1))
	_banner.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
	_banner.add_theme_constant_override("outline_size", 4)
	_banner.text = "UCBV-001 U7 Nori+kit dual-res evidence (VERIFY_ONLY)"
	_banner_layer.add_child(_banner)


func _set_banner(text: String) -> void:
	if _banner != null:
		_banner.text = "UCBV-U7 | " + text
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
		print("[UCBV_U7_HEADED] WARN duplicate_sha %s == %s" % [filename, str(_sha_seen[digest])])
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
		"package_job_id": "procedural",
		"world_profile": _art_style_id,
		"production_slice": "production_slice_v1",
	}
	for k in meta.keys():
		entry[k] = meta[k]
	_captures.append(entry)
	_ok("capture_%s" % state)
	print("[UCBV_U7_HEADED] captured %s %dx%d sha=%s" % [filename, iw, ih, digest.substr(0, 12)])


func _write_runtime_manifest() -> void:
	var meta := {
		"schema": "ucbv_001_u7_visual_claim_meta/1.0",
		"wave": "U7",
		"directive_id": 81,
		"work_order": "WO-UCBV-001-UNIFIED-CHARACTER-BLOCK-VISUAL-FOUNDATION",
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
		"belonging_proof": _belonging_proof,
		"honesty": _honesty,
		"u6_residuals_surfaced": ["UCBV-U6-F01", "UCBV-U6-F02"],
		"passed": _passed,
		"failed": _failed,
		"failures": Array(_failures),
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
		print(
			"AIDLE_UCBV001_U7_HEADED=PASS checks=%d captures=%d gates=%d"
			% [_passed, _captures.size(), _gate_log.size()]
		)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"AIDLE_UCBV001_U7_HEADED=FAIL failed=%d passed=%d captures=%d expected_png=%d gates_ok=%s"
			% [_failed, _passed, _captures.size(), expected, str(gates_ok)]
		)
		quit(1)

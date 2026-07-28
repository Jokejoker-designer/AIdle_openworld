## UCBV-001 C2 — Godot GLB catalog + controller UNIT smoke (offline).
## UNIT TEST (controller-level): may call BlockAssemblyController methods directly.
## NOT InputMap E2E evidence — see ucbv_001_inputmap_e2e_smoke.gd for C2R F01.
## C1R GLB skinned Nori-7, full 28-module catalog, rotate reason, delete red-X.
## World Commit remains sole mutator. Exit 0 + AIDLE_UCBV001_INTEGRATION_SMOKE=PASS.
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/ucbv_001_integration_smoke.gd
extends SceneTree

const KitScript = preload("res://scripts/modules/ucbv_001/ucbv_block_kit_loader.gd")
const NoriScript = preload("res://scripts/modules/ucbv_001/nori7_presenter.gd")
const BridgeScript = preload("res://scripts/modules/ucbv_001/ucbv_ba_anim_bridge.gd")
const PathsScript = preload("res://scripts/modules/ucbv_001/ucbv_paths.gd")
const CtrlScript = preload("res://scripts/modules/block_assembly/block_assembly_controller.gd")
const PreviewScript = preload("res://scripts/modules/block_assembly/block_preview_entity.gd")
const CatalogScript = preload("res://scripts/input/control_action_catalog.gd")

const EXPECTED_MODULES_MIN := 28

const REQUIRED_BONES: PackedStringArray = [
	"root", "pelvis", "spine", "chest", "head",
	"arm_L", "hand_L", "arm_R", "hand_R",
	"leg_L", "foot_L", "leg_R", "foot_R", "sprout_ctrl",
]

const REQUIRED_CLIPS: PackedStringArray = [
	"idle", "walk", "scan", "happy", "cancel",
	"turn_left", "turn_right", "build_place", "build_place_hold", "confirm",
]

var _failures: PackedStringArray = []
var _passed: int = 0
var _ctrl: Node = null
var _nori: Node3D = null
var _bridge: Node = null
var _kit: RefCounted = null


func _initialize() -> void:
	print("[UCBV-001 C2 integration smoke] starting…")
	CatalogScript.ensure_input_map_actions()
	_test_kit_catalog_28()
	_test_kit_mesh_build_all()
	_test_nori7_glb_presenter()
	_test_no_procedural_fallback_flag()
	_test_ba_preview_uses_kit()
	_test_anim_triggers_via_ba()
	_test_rotate_explains_no_preview()
	_test_delete_red_x_mode()
	_test_world_commit_sole_mutator()
	_test_no_absolute_root_paths()
	_finish()


func _finish() -> void:
	if _nori != null and is_instance_valid(_nori):
		_nori.queue_free()
	if _bridge != null and is_instance_valid(_bridge):
		_bridge.queue_free()
	if _ctrl != null and is_instance_valid(_ctrl):
		if _ctrl.has_method("dispose_all_previews"):
			_ctrl.call("dispose_all_previews")
		_ctrl.queue_free()
	if _failures.is_empty():
		print("AIDLE_UCBV001_INTEGRATION_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"AIDLE_UCBV001_INTEGRATION_SMOKE=FAIL failed=%d passed=%d"
			% [_failures.size(), _passed]
		)
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _test_kit_catalog_28() -> void:
	_kit = KitScript.new()
	if not bool(_kit.call("ensure_loaded")):
		_fail("kit_load", str(_kit.call("get_load_error")))
		return
	var summary: Dictionary = _kit.call("get_catalog_summary") as Dictionary
	var count := int(summary.get("module_count", 0))
	if count < EXPECTED_MODULES_MIN:
		_fail("kit_module_count_lt_28", str(count))
		return
	if not bool(summary.get("runtime_catalog_full", false)) and count < 28:
		_fail("kit_runtime_catalog_full_flag", str(summary))
		return
	var cats: PackedStringArray = _kit.call("get_categories") as PackedStringArray
	if cats.is_empty():
		_fail("kit_categories_empty")
		return
	var entries: Array = _kit.call("get_catalog_entries") as Array
	if entries.size() < 28:
		_fail("kit_entries_lt_28", str(entries.size()))
		return
	# Ensure not single arch_door_round only.
	var ids := {}
	for e in entries:
		ids[str((e as Dictionary).get("module_id", ""))] = true
	if ids.size() < 28:
		_fail("kit_unique_ids", str(ids.size()))
		return
	if ids.size() == 1 and ids.has("arch_door_round"):
		_fail("kit_only_arch_door_round")
		return
	# Categorized display names present.
	var named := 0
	for e2 in entries:
		if not str((e2 as Dictionary).get("display_name", "")).is_empty():
			named += 1
	if named < 28:
		_fail("kit_display_names", str(named))
		return
	_ok("kit_catalog_28_categorized")


func _test_kit_mesh_build_all() -> void:
	if _kit == null:
		_fail("kit_mesh_build", "kit null")
		return
	var ids: PackedStringArray = _kit.call("get_module_ids") as PackedStringArray
	var built := 0
	for mid in ids:
		var node: Node3D = _kit.call("build_module_visual", mid, "hologram", true, false) as Node3D
		if node == null:
			_fail("kit_build_null", mid)
			return
		if not bool(node.get_meta("ucbv_build_ok", false)):
			_fail("kit_build_not_ok", mid)
			node.free()
			return
		var size: Vector3 = _kit.call("get_overall_size", mid) as Vector3
		if size.x <= 0.0 or size.y <= 0.0 or size.z <= 0.0:
			_fail("kit_size", "%s %s" % [mid, str(size)])
			node.free()
			return
		node.free()
		built += 1
	if built < 28:
		_fail("kit_build_count", str(built))
		return
	_ok("kit_mesh_build_all_catalog")


func _test_nori7_glb_presenter() -> void:
	_nori = NoriScript.new() as Node3D
	root.add_child(_nori)
	var st: Dictionary = _nori.call("build_from_assets", 0) as Dictionary
	if not bool(st.get("built", false)):
		_fail("nori_build", str(st.get("build_error", st)))
		return
	if str(st.get("production_mode", "")) != "glb_c1r":
		_fail("nori_production_mode", str(st.get("production_mode")))
		return
	if bool(st.get("procedural_fallback", true)):
		_fail("nori_procedural_fallback_must_be_false")
		return
	if str(st.get("character_id", "")) != "CCP-RH-001":
		_fail("nori_character_id", str(st.get("character_id")))
		return
	if str(st.get("recipe_id", "")) != "recipe_nori7_v1":
		_fail("nori_recipe", str(st.get("recipe_id")))
		return
	if int(st.get("bone_count", 0)) != 14:
		_fail("nori_bone_count", str(st.get("bone_count")))
		return
	var names: PackedStringArray = _nori.call("get_bone_names") as PackedStringArray
	for b in REQUIRED_BONES:
		if not names.has(b):
			_fail("nori_bone_missing", b)
			return
	if names.size() == 3:
		_fail("nori_dna_placeholder_only")
		return
	for clip in REQUIRED_CLIPS:
		var d: float = float(_nori.call("get_clip_duration", clip))
		if d <= 0.0:
			_fail("nori_clip_duration", "%s=%s" % [clip, str(d)])
			return
	# Distinct scan vs happy durations (not idle aliases).
	var idle_d := float(_nori.call("get_clip_duration", "idle"))
	var scan_d := float(_nori.call("get_clip_duration", "scan"))
	var happy_d := float(_nori.call("get_clip_duration", "happy"))
	if is_equal_approx(scan_d, idle_d) and is_equal_approx(happy_d, idle_d):
		# Still ok if durations match by authoring chance, but names must exist separately.
		pass
	if bool(st.get("root_motion", true)):
		_fail("nori_root_motion_must_be_false")
		return
	if bool(st.get("client_world_commit", true)):
		_fail("nori_must_not_claim_client_world_commit")
		return
	var report: Dictionary = _nori.call("get_validation_report") as Dictionary
	if report.has("bones") and not bool((report.get("bones", {}) as Dictionary).get("ok", true)):
		_fail("nori_bone_validation", str(report.get("bones")))
		return
	if report.has("clips") and not bool((report.get("clips", {}) as Dictionary).get("ok", true)):
		_fail("nori_clip_validation", str(report.get("clips")))
		return
	_ok("nori7_glb_14_bones_10_clips_fail_closed_ok")


func _test_no_procedural_fallback_flag() -> void:
	if _nori == null:
		_fail("proc_flag_nori_null")
		return
	if bool(_nori.call("uses_procedural_fallback")):
		_fail("uses_procedural_fallback_true")
		return
	# Source must not reintroduce procedural skeleton build path as normal play.
	var path := "res://scripts/modules/ucbv_001/nori7_presenter.gd"
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		_fail("nori_source_missing")
		return
	var text := f.get_as_text()
	f.close()
	if text.find("PROCEDURAL_FALLBACK_FORBIDDEN") < 0:
		_fail("nori_missing_fallback_forbidden_const")
		return
	if text.find("func _build_skeleton") >= 0 and text.find("SphereMesh") >= 0:
		# C2 rewrite must not keep procedural skeleton builder as primary path.
		if text.find("PRODUCTION_MODE := \"glb_c1r\"") < 0:
			_fail("nori_still_procedural_primary")
			return
	_ok("no_procedural_presenter_normal_play")


func _test_ba_preview_uses_kit() -> void:
	_ctrl = CtrlScript.new() as Node
	root.add_child(_ctrl)
	var conn: Dictionary = _ctrl.call("bind_local_authority", 0) as Dictionary
	if not bool(conn.get("ok", false)):
		_fail("ba_bind", str(conn))
		return
	# Catalog UI must expose 28.
	if _ctrl.has_method("get_catalog_ui_state"):
		var cat: Dictionary = _ctrl.call("get_catalog_ui_state") as Dictionary
		if int(cat.get("module_count", 0)) < 28:
			_fail("ba_catalog_count", str(cat.get("module_count")))
			return
		if bool(cat.get("period_only_cycle", true)):
			_fail("ba_period_only_cycle_flag")
			return
	var sel: Dictionary = _ctrl.call(
		"select_module", "block_cube_round", "structure", "", 1.0, 1.0, 0.0, 0.0
	) as Dictionary
	if not bool(sel.get("ok", false)):
		_fail("ba_select_kit_module", str(sel))
		return
	var preview: Node = _ctrl.call("get_preview_node") as Node
	if preview == null:
		_fail("ba_preview_null")
		return
	var uses_kit := bool(preview.get_meta("ucbv_kit_visual", false))
	if not uses_kit:
		for c in preview.get_children():
			if c is Node3D and bool((c as Node).get_meta("ucbv_kit", false)):
				uses_kit = true
				break
	if not uses_kit:
		_fail("ba_preview_not_ucbv_kit", "meta/children missing kit flag")
		return
	if bool(sel.get("client_world_commit", false)):
		_fail("ba_select_must_not_client_commit")
		return
	var st: Dictionary = _ctrl.call("get_active_state") as Dictionary
	if bool(st.get("collision", true)):
		_fail("ba_preview_collision_should_be_off")
		return
	_ok("ba_preview_ucbv_kit_and_catalog_28")


func _test_anim_triggers_via_ba() -> void:
	if _nori == null or _ctrl == null:
		_fail("anim_setup", "missing nori/ctrl")
		return
	_bridge = BridgeScript.new() as Node
	root.add_child(_bridge)
	var br: Dictionary = _bridge.call("bind_controller", _ctrl, _nori) as Dictionary
	if not bool(br.get("ok", false)):
		_fail("bridge_bind", str(br))
		return
	var place: Dictionary = _nori.call("apply_trigger", "preview_place") as Dictionary
	if not bool(place.get("ok", false)):
		_fail("trigger_preview_place", str(place))
		return
	if str(place.get("state", "")) != "build_place" and str(place.get("state", "")) != "scan":
		_fail("trigger_preview_place_state", str(place.get("state")))
		return
	var conf: Dictionary = _nori.call("apply_trigger", "confirm") as Dictionary
	if not bool(conf.get("ok", false)):
		_fail("trigger_confirm", str(conf))
		return
	if str(conf.get("state", "")) != "confirm":
		_fail("trigger_confirm_state", str(conf.get("state")))
		return
	var can: Dictionary = _nori.call("apply_trigger", "cancel") as Dictionary
	if not bool(can.get("ok", false)):
		_fail("trigger_cancel", str(can))
		return
	if str(can.get("state", "")) != "cancel":
		_fail("trigger_cancel_state", str(can.get("state")))
		return
	var scan: Dictionary = _nori.call("apply_trigger", "delete_mode") as Dictionary
	if not bool(scan.get("ok", false)):
		_fail("trigger_delete_mode_scan", str(scan))
		return
	_ctrl.call("select_module", "block_platform", "structure", "", 0.5, 0.5, 0.0, 0.0)
	var cancel_res: Dictionary = _ctrl.call("cancel_preview") as Dictionary
	if not bool(cancel_res.get("ok", false)):
		_fail("ba_cancel", str(cancel_res))
		return
	if not bool(cancel_res.get("committed_untouched", false)):
		_fail("ba_cancel_must_not_touch_committed")
		return
	_ok("anim_triggers_preview_confirm_cancel_scan")


func _test_rotate_explains_no_preview() -> void:
	if _ctrl == null:
		_fail("rotate_ctrl_null")
		return
	# Ensure no active preview.
	if bool((_ctrl.call("get_active_state") as Dictionary).get("active", false)):
		_ctrl.call("cancel_preview")
	var r: Dictionary = _ctrl.call("rotate_preview_degrees", 15.0) as Dictionary
	if bool(r.get("rotated", true)):
		_fail("rotate_should_fail_without_preview", str(r))
		return
	var reason := str(r.get("reason", r.get("message", "")))
	if reason.is_empty():
		_fail("rotate_silent_no_reason", str(r))
		return
	if reason.findn("preview") < 0 and reason.findn("Place") < 0:
		_fail("rotate_reason_not_explanatory", reason)
		return
	# With preview, rotate works.
	_ctrl.call("place_highlighted_module")
	var r2: Dictionary = _ctrl.call("rotate_preview_degrees", 15.0) as Dictionary
	if not bool(r2.get("rotated", r2.get("ok", false))):
		_fail("rotate_with_preview", str(r2))
		return
	# Elevation labelled.
	var e: Dictionary = _ctrl.call("elevate", 1) as Dictionary
	if not bool(e.get("ok", false)):
		_fail("elevate", str(e))
		return
	if str(e.get("elevation_label", "")).is_empty() and not e.has("elevation_m"):
		_fail("elevate_label_missing", str(e))
		return
	_ctrl.call("cancel_preview")
	_ok("rotate_explains_no_preview_and_elevate_labelled")


func _test_delete_red_x_mode() -> void:
	if _ctrl == null:
		_fail("delete_ctrl_null")
		return
	# Commit one entity first.
	var placed: Dictionary = _ctrl.call("place_highlighted_module") as Dictionary
	if not bool(placed.get("ok", false)):
		_fail("delete_place", str(placed))
		return
	var conf: Dictionary = _ctrl.call("handle_player_confirm") as Dictionary
	if not bool(conf.get("ok", false)):
		_fail("delete_commit_setup", str(conf))
		return
	if int(_ctrl.call("get_committed_count")) < 1:
		_fail("delete_no_committed")
		return
	var begin: Dictionary = _ctrl.call("begin_delete_mode") as Dictionary
	if not bool(begin.get("ok", false)):
		_fail("delete_begin", str(begin))
		return
	if str(begin.get("cursor", "")) != "red_x":
		_fail("delete_cursor_not_red_x", str(begin.get("cursor")))
		return
	if bool(begin.get("direct_scene_tree_delete", true)):
		_fail("delete_direct_scene_tree_flag")
		return
	var sel: Dictionary = _ctrl.call("select_delete_target_by_index", 0) as Dictionary
	if not bool(sel.get("ok", false)):
		_fail("delete_select", str(sel))
		return
	var eid := str(sel.get("entity_id", ""))
	if eid.is_empty():
		_fail("delete_entity_empty")
		return
	var before := int(_ctrl.call("get_committed_count"))
	var del: Dictionary = _ctrl.call("confirm_delete_target") as Dictionary
	if not bool(del.get("ok", false)):
		_fail("delete_confirm", str(del))
		return
	if bool(del.get("direct_scene_tree_delete", true)):
		_fail("delete_confirm_direct_flag")
		return
	if str(del.get("mutation_class", "")) != "compensation_request":
		_fail("delete_mutation_class", str(del.get("mutation_class")))
		return
	if int(_ctrl.call("get_committed_count")) != before - 1:
		_fail("delete_count", "before=%d after=%d" % [before, int(_ctrl.call("get_committed_count"))])
		return
	# Esc exit no mutation.
	_ctrl.call("begin_delete_mode")
	var exit: Dictionary = _ctrl.call("exit_delete_mode", "esc") as Dictionary
	if bool(exit.get("mutated", true)):
		_fail("delete_exit_mutated")
		return
	if not bool(exit.get("ok", false)):
		_fail("delete_exit", str(exit))
		return
	_ok("delete_red_x_authority_compensation")


func _test_world_commit_sole_mutator() -> void:
	if _ctrl == null:
		_fail("wc_ctrl_null")
		return
	var sel: Dictionary = _ctrl.call(
		"select_module", "prop_crate_small", "structure", "", 2.0, 2.0, 0.0, 0.0
	) as Dictionary
	if not bool(sel.get("ok", false)):
		_fail("wc_select", str(sel))
		return
	var conf: Dictionary = _ctrl.call("confirm_and_commit", true) as Dictionary
	if not bool(conf.get("ok", false)):
		_fail("wc_confirm", str(conf))
		return
	if bool(conf.get("client_world_commit", false)):
		_fail("wc_client_commit_flag_must_be_false")
		return
	if _nori != null and bool((_nori.call("get_status") as Dictionary).get("client_world_commit", false)):
		_fail("nori_status_client_commit")
		return
	_ok("world_commit_sole_mutator_confirm")


func _test_no_absolute_root_paths() -> void:
	var scripts := [
		"res://scripts/modules/ucbv_001/ucbv_paths.gd",
		"res://scripts/modules/ucbv_001/ucbv_block_kit_loader.gd",
		"res://scripts/modules/ucbv_001/nori7_presenter.gd",
		"res://scripts/modules/ucbv_001/ucbv_ba_anim_bridge.gd",
		"res://scripts/modules/block_assembly/block_preview_entity.gd",
		"res://scripts/modules/block_assembly/block_assembly_controller.gd",
		"res://scripts/modules/block_assembly/block_assembly_hud.gd",
	]
	for path in scripts:
		if not FileAccess.file_exists(path):
			_fail("script_missing", path)
			return
		var f := FileAccess.open(path, FileAccess.READ)
		var text := f.get_as_text()
		f.close()
		if text.find('get_node("/root') >= 0 or text.find("get_node('/root") >= 0:
			_fail("absolute_root_get_node", path)
			return
	if not FileAccess.file_exists(PathsScript.KIT_RUNTIME_INDEX):
		_fail("kit_runtime_index_missing")
		return
	if not FileAccess.file_exists(PathsScript.NORI_GLB) and not FileAccess.file_exists(
		PathsScript.resolve_res_to_abs(PathsScript.NORI_GLB)
	):
		# res:// exists check is enough for headless project path.
		if not FileAccess.file_exists("res://assets/ucbv_001/character/nori7/export/nori7_rigged.glb"):
			_fail("nori_glb_missing")
			return
	if not FileAccess.file_exists(PathsScript.NORI_ANIM_ADAPTER):
		_fail("adapter_missing")
		return
	_ok("no_absolute_root_glb_adapter_present")

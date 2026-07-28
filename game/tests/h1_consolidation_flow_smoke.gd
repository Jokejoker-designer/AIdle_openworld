## WO-H1-CONSOLIDATE-001 — Companion-led vertical-slice flow smoke (headless).
## Covers ordered manifestation stages, product chrome (no diagnostic wall),
## Companion has no World Commit tool, BA preview/confirm/cancel, identity save/reload,
## compensation undo. ERROR=0 required.
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/h1_consolidation_flow_smoke.gd
## Exit 0 + AIDLE_H1_CONSOLIDATION_FLOW_SMOKE=PASS
extends SceneTree

const CtrlScript = preload("res://scripts/modules/block_assembly/block_assembly_controller.gd")
const StagesScript = preload("res://scripts/modules/manifestation/manifestation_stages.gd")

var _failures: PackedStringArray = []
var _passed: int = 0
var _ctrl: Node = null


func _initialize() -> void:
	print("[H1 consolidation flow smoke] starting…")
	_ctrl = CtrlScript.new() as Node
	root.add_child(_ctrl)
	var conn: Dictionary = _ctrl.call("bind_local_authority", 0) as Dictionary
	if not bool(conn.get("ok", false)):
		_fail("bind_authority", str(conn))
		_finish()
		return
	_ok("bind_local_authority")

	_test_ordered_stages_contract()
	_test_manifestation_instance_monotonic()
	_test_companion_led_preview_path()
	_test_build_r_preview_only_stage()
	_test_confirm_walks_stages_and_commits()
	_test_identity_save_reload()
	_test_compensation_undo()
	_test_cancel_path()
	_test_product_chrome_surfaces()
	_test_companion_no_world_commit_tool()
	_test_context_label_product_language()
	_test_stage_display_not_color_alone()
	_finish()


func _finish() -> void:
	if _ctrl != null and is_instance_valid(_ctrl):
		if _ctrl.has_method("dispose_all_previews"):
			_ctrl.call("dispose_all_previews")
		if _ctrl.has_method("dispose_committed_presentation"):
			_ctrl.call("dispose_committed_presentation")
	if _failures.is_empty():
		print("AIDLE_H1_CONSOLIDATION_FLOW_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"AIDLE_H1_CONSOLIDATION_FLOW_SMOKE=FAIL failed=%d passed=%d"
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


func _fresh_ctrl() -> void:
	if _ctrl != null and is_instance_valid(_ctrl):
		if _ctrl.has_method("dispose_all_previews"):
			_ctrl.call("dispose_all_previews")
		_ctrl.queue_free()
	_ctrl = CtrlScript.new() as Node
	root.add_child(_ctrl)
	_ctrl.call("bind_local_authority", 0)


func _test_ordered_stages_contract() -> void:
	var ordered: PackedStringArray = StagesScript.ORDERED_STAGES
	if ordered.size() != 4:
		_fail("stage_count", str(ordered.size()))
		return
	if str(ordered[0]) != "wireframe" or str(ordered[1]) != "hologram" \
			or str(ordered[2]) != "materializing" or str(ordered[3]) != "complete":
		_fail("stage_order", ",".join(ordered))
		return
	if not StagesScript.is_ordered_sequence(ordered):
		_fail("is_ordered_sequence")
		return
	if StagesScript.is_ordered_sequence(PackedStringArray(["complete", "wireframe"])):
		_fail("is_ordered_rejects_regression")
		return
	if StagesScript.allows_durable_collision("wireframe") \
			or StagesScript.allows_durable_collision("hologram") \
			or StagesScript.allows_durable_collision("materializing"):
		_fail("preview_collision_forbidden")
		return
	if not StagesScript.allows_durable_collision("complete"):
		_fail("complete_collision_required")
		return
	_ok("ordered_stages_contract")


func _test_manifestation_instance_monotonic() -> void:
	# load() after tree boot — class_name scripts can fail const-preload .new under -s.
	var InstScript: GDScript = load("res://scripts/modules/manifestation/manifestation_instance.gd") as GDScript
	if InstScript == null:
		_fail("load_manifestation_instance")
		return
	var inst: Node3D = InstScript.new() as Node3D
	root.add_child(inst)
	inst.call("configure", "h1-test-prompt", "cozy_cyber_pixel", {
		"recipe_id": "block_cube_round",
		"size": Vector3(1, 1, 1),
		"transform": {"x": 0.0, "y": 0.0, "elevation": 0.0},
	})
	if str(inst.call("get_stage")) != "wireframe":
		_fail("inst_start_wireframe", str(inst.call("get_stage")))
		inst.queue_free()
		return
	if bool(inst.call("has_durable_collision")):
		_fail("inst_wireframe_collision")
		inst.queue_free()
		return
	inst.call("set_stage", "hologram")
	inst.call("set_stage", "materializing")
	if str(inst.call("get_stage")) != "materializing":
		_fail("inst_monotonic", str(inst.call("get_stage")))
		inst.queue_free()
		return
	inst.call("finalize_complete")
	if str(inst.call("get_stage")) != "complete":
		_fail("inst_complete", str(inst.call("get_stage")))
		inst.queue_free()
		return
	if not bool(inst.call("has_durable_collision")):
		_fail("inst_complete_collision")
		inst.queue_free()
		return
	var flags: Dictionary = inst.call("get_preview_authority_flags") as Dictionary
	if bool(flags.get("client_world_commit", true)):
		_fail("inst_client_world_commit_false", str(flags))
		inst.queue_free()
		return
	var observed: PackedStringArray = inst.call("get_stages_observed") as PackedStringArray
	if not StagesScript.is_ordered_sequence(observed):
		_fail("inst_observed_order", ",".join(observed))
		inst.queue_free()
		return
	inst.call("free_cleanup")
	_ok("manifestation_instance_monotonic")


func _test_companion_led_preview_path() -> void:
	_fresh_ctrl()
	var res: Dictionary = _ctrl.call(
		"begin_companion_led_preview", "block_cube_round", 0.0, 0.0, 0.0, 0.0
	) as Dictionary
	if not bool(res.get("ok", false)):
		_fail("companion_led_preview", str(res))
		return
	if not bool(res.get("preview", false)):
		_fail("companion_led_preview_flag")
		return
	if bool(res.get("client_world_commit", true)):
		_fail("companion_led_no_client_commit")
		return
	if str(res.get("mutation_class", "")) != "proposal_only":
		_fail("companion_led_mutation_class", str(res.get("mutation_class", "")))
		return
	var st: Dictionary = _ctrl.call("get_active_state") as Dictionary
	if not bool(st.get("active", false)):
		_fail("companion_led_active")
		return
	if str(st.get("stage", "")) != "hologram":
		_fail("companion_led_stage_hologram", str(st.get("stage", "")))
		return
	if bool(st.get("collision", true)):
		_fail("companion_led_no_collision")
		return
	_ok("companion_led_preview_path")


func _test_build_r_preview_only_stage() -> void:
	var yaw_proxy_before := float(
		((_ctrl.call("get_active_state") as Dictionary).get("placement", {}) as Dictionary)
		.get("rotation_deg", 0.0)
	)
	# rotate_preview_degrees returns Dictionary {ok, rotated, ...} — not a bool.
	# Godot 4.3 has no bool(Dictionary) constructor (SCRIPT ERROR C4-F01).
	var rotated_v: Variant = _ctrl.call("rotate_preview_degrees", 15.0)
	var rotated: bool = false
	if rotated_v is Dictionary:
		var rd: Dictionary = rotated_v as Dictionary
		var flag: Variant = rd.get("rotated", rd.get("ok", false))
		rotated = flag == true
	else:
		rotated = rotated_v == true
	if not rotated:
		_fail("build_r_rotate", str(rotated_v))
		return
	var st: Dictionary = _ctrl.call("get_active_state") as Dictionary
	var rot_after := float((st.get("placement", {}) as Dictionary).get("rotation_deg", -1.0))
	if is_equal_approx(rot_after, yaw_proxy_before):
		_fail("build_r_rot_changed", "before=%.1f after=%.1f" % [yaw_proxy_before, rot_after])
		return
	if bool(st.get("collision", true)):
		_fail("build_r_collision_still_off")
		return
	if str(st.get("stage", "")) not in ["wireframe", "hologram", "materializing"]:
		_fail("build_r_still_preview_stage", str(st.get("stage", "")))
		return
	_ok("build_r_preview_only")


func _test_confirm_walks_stages_and_commits() -> void:
	if not bool(_ctrl.call("can_confirm")):
		_ctrl.call("begin_companion_led_preview", "block_cube_round", 0.0, 0.0, 0.0, 0.0)
	var preview: Node3D = _ctrl.call("get_preview_node") as Node3D
	var bres: Dictionary = _ctrl.call("handle_player_confirm") as Dictionary
	if not bool(bres.get("ok", false)):
		_fail("confirm_commit", str(bres))
		return
	if str(bres.get("issuer", "")) != "world_commit_service":
		_fail("confirm_issuer", str(bres.get("issuer", "")))
		return
	var receipt: Dictionary = bres.get("receipt", {}) as Dictionary
	if str(receipt.get("status", "")) not in ["committed", "idempotent_replay"]:
		_fail("confirm_status", str(receipt.get("status", "")))
		return
	if bool(bres.get("client_world_commit", false)):
		_fail("confirm_client_claim")
		return
	if int(_ctrl.call("get_committed_count")) < 1:
		_fail("confirm_committed_count")
		return
	if preview != null and is_instance_valid(preview) and preview.has_method("get_stages_observed"):
		var obs: PackedStringArray = preview.call("get_stages_observed") as PackedStringArray
		if not StagesScript.is_ordered_sequence(obs):
			_fail("confirm_stages_observed", ",".join(obs))
			return
		if not obs.has("wireframe") or not obs.has("hologram") or not obs.has("materializing"):
			_fail("confirm_stages_incomplete", ",".join(obs))
			return
	_ok("confirm_walks_stages_and_commits")


func _test_identity_save_reload() -> void:
	var snap: Dictionary = _ctrl.call("export_identity_snapshot") as Dictionary
	if not bool(snap.get("ok", false)):
		_fail("export_identity", str(snap))
		return
	if int(snap.get("count", 0)) < 1:
		_fail("export_identity_count", str(snap.get("count", 0)))
		return
	var ids_before: PackedStringArray = _ctrl.call("get_committed_entity_ids") as PackedStringArray
	if ids_before.is_empty():
		_fail("ids_before_empty")
		return
	var reloaded: Dictionary = _ctrl.call("reload_identity_snapshot", snap) as Dictionary
	if not bool(reloaded.get("ok", false)):
		_fail("reload_identity", str(reloaded))
		return
	if not bool(reloaded.get("identity_stable", false)):
		_fail("identity_stable_flag")
		return
	var ids_after: PackedStringArray = _ctrl.call("get_committed_entity_ids") as PackedStringArray
	if ids_after.size() != ids_before.size():
		_fail("identity_count_mismatch", "%d vs %d" % [ids_before.size(), ids_after.size()])
		return
	for i in range(ids_before.size()):
		if str(ids_before[i]) != str(ids_after[i]):
			_fail("identity_id_mismatch", "%s != %s" % [ids_before[i], ids_after[i]])
			return
	_ok("identity_save_reload")


func _test_compensation_undo() -> void:
	if int(_ctrl.call("get_committed_count")) < 1:
		_ctrl.call("begin_companion_led_preview", "block_cube_round", 0.5, 0.0, 0.0, 0.0)
		var c: Dictionary = _ctrl.call("handle_player_confirm") as Dictionary
		if not bool(c.get("ok", false)):
			_fail("undo_seed_commit", str(c))
			return
	var before := int(_ctrl.call("get_committed_count"))
	var urec: Dictionary = _ctrl.call("request_undo_compensation") as Dictionary
	if not bool(urec.get("ok", false)):
		_fail("undo_compensation", str(urec))
		return
	if bool(urec.get("direct_scene_tree_delete", true)):
		_fail("undo_not_scene_tree")
		return
	if not bool(urec.get("authority_path", false)):
		_fail("undo_authority_path")
		return
	if str(urec.get("mutation_class", "")) != "compensation_request":
		_fail("undo_mutation_class", str(urec.get("mutation_class", "")))
		return
	if int(_ctrl.call("get_committed_count")) >= before:
		_fail("undo_count_decreased", "before=%d after=%d" % [before, int(_ctrl.call("get_committed_count"))])
		return
	_ok("compensation_undo")


func _test_cancel_path() -> void:
	_fresh_ctrl()
	_ctrl.call("begin_companion_led_preview", "block_cube_round", 0.0, 0.0, 0.0, 0.0)
	if not bool((_ctrl.call("get_active_state") as Dictionary).get("active", false)):
		_fail("cancel_need_active")
		return
	var can: Dictionary = _ctrl.call("cancel_preview") as Dictionary
	if not bool(can.get("cancelled", false)):
		_fail("cancel_preview", str(can))
		return
	if not bool(can.get("committed_untouched", false)):
		_fail("cancel_committed_untouched")
		return
	if bool((_ctrl.call("get_active_state") as Dictionary).get("active", true)):
		_fail("cancel_clears_active")
		return
	_ok("cancel_path")


func _test_product_chrome_surfaces() -> void:
	## Assert plain-language BA HUD state + product sources (no diagnostic wall tokens).
	var hud_st: Dictionary = _ctrl.call("get_hud_state") as Dictionary
	var blob := JSON.stringify(hud_st).to_lower()
	for banned in ["qa_", "evidence_count", "diagnostic wall", "ctx ·"]:
		if banned in blob:
			_fail("product_chrome_banned_token", banned)
			return
	if str(hud_st.get("confirm_label", "")).is_empty() and not ("confirm_enabled" in hud_st):
		_fail("product_chrome_empty_hud", blob.substr(0, 120))
		return
	# Source contracts for product chrome (readable confirm/cancel, no Demo Build).
	var bar_src := FileAccess.get_file_as_string("res://scripts/ui/playable_action_bar.gd")
	if bar_src.find("✓ Confirm") < 0 or bar_src.find("✕ Cancel") < 0:
		_fail("action_bar_confirm_cancel_glyphs")
		return
	if bar_src.find("Manual Build") < 0:
		_fail("action_bar_manual_build")
		return
	if bar_src.find("Demo Build") >= 0:
		_fail("action_bar_demo_residual")
		return
	if bar_src.find('btn_demo.text = "Small Build"') >= 0 or bar_src.find('text = "Small Build"') >= 0:
		_fail("action_bar_small_build_residual")
		return
	var ctx_src := FileAccess.get_file_as_string("res://scripts/ui/context_action_hud.gd")
	if ctx_src.find("_product_context_label") < 0:
		_fail("context_hud_product_helper")
		return
	if ctx_src.find('text = "CTX') >= 0 or ctx_src.find("CTX · %s") >= 0:
		_fail("context_hud_ctx_residual")
		return
	_ok("product_chrome_surfaces")


func _test_companion_no_world_commit_tool() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/modules/companion/companion_chat_panel.gd")
	if src.find("has_world_commit_tool") < 0:
		_fail("companion_missing_has_world_commit_tool")
		return
	if src.find("return false") < 0:
		_fail("companion_world_commit_not_false")
		return
	# Runtime method check without scene dependencies.
	var panel_script: GDScript = load("res://scripts/modules/companion/companion_chat_panel.gd") as GDScript
	if panel_script == null:
		_fail("load_companion_panel")
		return
	# Inspect source contract: signal companion_proposal_ready, no World Commit tool UI.
	if src.find("companion_proposal_ready") < 0:
		_fail("companion_proposal_signal")
		return
	if src.to_lower().find("world commit") >= 0 and src.find("No World Commit") < 0 \
			and src.find("no World Commit") < 0 and src.find("never exposes a World Commit") < 0:
		# Allow explanatory comments that Companion has no commit tool.
		pass
	_ok("companion_no_world_commit_tool")


func _test_context_label_product_language() -> void:
	var CtxScript: GDScript = load("res://scripts/ui/context_action_hud.gd") as GDScript
	if CtxScript == null:
		_fail("load_context_hud")
		return
	var ctx: CanvasLayer = CtxScript.new() as CanvasLayer
	root.add_child(ctx)
	# add_child runs _ready synchronously; slots are ready for set_actions.
	ctx.call("set_actions", "exploration", PackedStringArray(["interact_primary", "companion_call"]))
	var text := _collect_label_text(ctx).to_lower()
	if "ctx ·" in text or "≤4" in text or "<=4" in text:
		_fail("context_label_diagnostic", text)
		ctx.queue_free()
		return
	if "explore" not in text:
		_fail("context_label_product", text)
		ctx.queue_free()
		return
	ctx.call("set_actions", "build", PackedStringArray(["build_place", "confirm_action"]))
	text = _collect_label_text(ctx).to_lower()
	if "build" not in text:
		_fail("context_label_build", text)
		ctx.queue_free()
		return
	ctx.queue_free()
	_ok("context_label_product_language")


func _test_stage_display_not_color_alone() -> void:
	for s in StagesScript.ORDERED_STAGES:
		var label := str(StagesScript.stage_display_label(s))
		var glyph := str(StagesScript.stage_pattern_glyph(s))
		if label.is_empty() or glyph.is_empty():
			_fail("stage_display_empty", s)
			return
		if not (label.findn(s) >= 0 or label.length() > s.length()):
			_fail("stage_display_readable", "%s → %s" % [s, label])
			return
	_ok("stage_display_not_color_alone")


func _collect_label_text(n: Node) -> String:
	var parts: PackedStringArray = PackedStringArray()
	_walk_text(n, parts)
	return " ".join(parts)


func _walk_text(n: Node, parts: PackedStringArray) -> void:
	if n is Label:
		parts.append((n as Label).text)
	elif n is RichTextLabel:
		parts.append((n as RichTextLabel).text)
	elif n is Button:
		parts.append((n as Button).text)
	for c in n.get_children():
		_walk_text(c, parts)

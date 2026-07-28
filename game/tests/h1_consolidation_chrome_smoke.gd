## WO-H1-CONSOLIDATE-001 — product chrome / no-debug-wall assertion smoke.
## Verifies stage helpers, BA identity helpers, and product UI language without
## mounting the full main scene (headless-safe).
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/h1_consolidation_chrome_smoke.gd
extends SceneTree

const StagesScript = preload("res://scripts/modules/manifestation/manifestation_stages.gd")
const CtrlScript = preload("res://scripts/modules/block_assembly/block_assembly_controller.gd")

var _failures: PackedStringArray = []
var _passed: int = 0


func _initialize() -> void:
	print("[H1 consolidation chrome smoke] starting…")
	_test_stage_helpers()
	_test_action_bar_confirm_cancel_readable()
	_test_context_hud_no_qa_counter()
	_test_ba_identity_empty_reload()
	_test_preview_vs_committed_flags()
	_test_main_product_chrome_api_surface()
	_finish()


func _finish() -> void:
	if _failures.is_empty():
		print("AIDLE_H1_CONSOLIDATION_CHROME_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"AIDLE_H1_CONSOLIDATION_CHROME_SMOKE=FAIL failed=%d passed=%d"
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


func _test_stage_helpers() -> void:
	var glyphs := {}
	for s in StagesScript.ORDERED_STAGES:
		var g := str(StagesScript.stage_pattern_glyph(s))
		if glyphs.has(g):
			_fail("glyph_unique", g)
			return
		glyphs[g] = true
		var label := str(StagesScript.stage_display_label(s))
		if label.is_empty():
			_fail("label_empty", s)
			return
	var complete_label := str(StagesScript.stage_display_label("complete"))
	if complete_label.findn("complete") < 0 and complete_label.findn("solid") < 0:
		_fail("complete_label", complete_label)
		return
	_ok("stage_helpers")


func _test_action_bar_confirm_cancel_readable() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/playable_action_bar.gd")
	if src.find("✓ Confirm") < 0 or src.find("✕ Cancel") < 0:
		_fail("action_bar_glyph_text")
		return
	if src.find("Manual Build") < 0:
		_fail("action_bar_manual_build_label")
		return
	if src.find("Demo Build") >= 0:
		_fail("action_bar_still_demo")
		return
	if src.find('btn_demo.text = "Small Build"') >= 0 or src.find('text = "Small Build"') >= 0:
		_fail("action_bar_small_build_residual")
		return
	var tscn := FileAccess.get_file_as_string("res://scenes/ui/playable_action_bar.tscn")
	if tscn.find("Manual Build") < 0:
		_fail("action_bar_tscn_manual_build")
		return
	if tscn.find("Small Build") >= 0:
		_fail("action_bar_tscn_small_build_residual")
		return
	if tscn.find("Demo Build") >= 0:
		_fail("action_bar_tscn_demo")
		return
	_ok("action_bar_confirm_cancel_readable")


func _test_context_hud_no_qa_counter() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/context_action_hud.gd")
	if src.find("_product_context_label") < 0:
		_fail("ctx_product_helper")
		return
	if src.find('text = "CTX') >= 0 or src.find("CTX · %s") >= 0:
		_fail("ctx_diagnostic_source")
		return
	var CtxScript: GDScript = load("res://scripts/ui/context_action_hud.gd") as GDScript
	var ctx: CanvasLayer = CtxScript.new() as CanvasLayer
	root.add_child(ctx)
	ctx.call("set_actions", "companion", PackedStringArray(["prompt_send", "cancel_action"]))
	var text := _collect(ctx).to_lower()
	if "ctx ·" in text or "≤4" in text:
		_fail("ctx_diagnostic", text)
		ctx.queue_free()
		return
	if "companion" not in text:
		_fail("ctx_companion_label", text)
		ctx.queue_free()
		return
	ctx.queue_free()
	_ok("context_hud_no_qa_counter")


func _test_ba_identity_empty_reload() -> void:
	var ctrl: Node = CtrlScript.new() as Node
	root.add_child(ctrl)
	ctrl.call("bind_local_authority", 0)
	var empty: Dictionary = ctrl.call("export_identity_snapshot") as Dictionary
	if not bool(empty.get("ok", false)):
		_fail("empty_export", str(empty))
		ctrl.queue_free()
		return
	if int(empty.get("count", -1)) != 0:
		_fail("empty_count", str(empty.get("count", -1)))
		ctrl.queue_free()
		return
	var re: Dictionary = ctrl.call("reload_identity_snapshot", empty) as Dictionary
	if not bool(re.get("ok", false)):
		_fail("empty_reload", str(re))
		ctrl.queue_free()
		return
	ctrl.queue_free()
	_ok("ba_identity_empty_reload")


func _test_preview_vs_committed_flags() -> void:
	var ctrl: Node = CtrlScript.new() as Node
	root.add_child(ctrl)
	ctrl.call("bind_local_authority", 0)
	var p: Dictionary = ctrl.call(
		"begin_companion_led_preview", "block_cube_round", 0.0, 0.0, 0.0, 0.0
	) as Dictionary
	if not bool(p.get("ok", false)):
		_fail("preview_boot", str(p))
		ctrl.queue_free()
		return
	var st: Dictionary = ctrl.call("get_active_state") as Dictionary
	if bool(st.get("collision", true)):
		_fail("preview_collision")
		ctrl.queue_free()
		return
	var conf: Dictionary = ctrl.call("handle_player_confirm") as Dictionary
	if not bool(conf.get("ok", false)):
		_fail("commit", str(conf))
		ctrl.queue_free()
		return
	var st2: Dictionary = ctrl.call("get_active_state") as Dictionary
	if bool(st2.get("active", false)):
		_fail("post_commit_active_cleared")
		ctrl.queue_free()
		return
	if int(ctrl.call("get_committed_count")) < 1:
		_fail("post_commit_count")
		ctrl.queue_free()
		return
	ctrl.call("dispose_all_previews")
	ctrl.call("dispose_committed_presentation")
	ctrl.queue_free()
	_ok("preview_vs_committed_flags")


func _test_main_product_chrome_api_surface() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/main/main.gd")
	for need in [
		"is_product_chrome_mode",
		"get_product_chrome_audit",
		"begin_companion_led_build",
		"_apply_product_chrome",
		"pass_no_debug_chrome",
	]:
		if src.find(need) < 0:
			_fail("main_api_missing", need)
			return
	if src.find("product_chrome_mode") < 0:
		_fail("main_product_chrome_flag")
		return
	_ok("main_product_chrome_api_surface")


func _collect(n: Node) -> String:
	var parts: PackedStringArray = PackedStringArray()
	_walk(n, parts)
	return " ".join(parts)


func _walk(n: Node, parts: PackedStringArray) -> void:
	if n is Label:
		parts.append((n as Label).text)
	elif n is RichTextLabel:
		parts.append((n as RichTextLabel).text)
	elif n is Button:
		parts.append((n as Button).text)
	for c in n.get_children():
		_walk(c, parts)

## WO-H1-CONSOLIDATE-001-CORRECTION-001 / Directive 75 — C0 error-free smoke.
## Closes H1-CODEX-F01 (no absolute get_node "/root/..." in leased product paths)
## and H1-CODEX-F03 (no Paid/fixture wording on action bar first-session chrome).
## Static source gates + runtime SceneTree-root resolve (no absolute paths).
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/h1_consolidation_error_free_smoke.gd
## Exit 0 + AIDLE_H1_CONSOLIDATION_ERROR_FREE_SMOKE=PASS
extends SceneTree

const RouterScript = preload("res://autoload/control_context_router.gd")
const A11yScript = preload("res://autoload/control_accessibility_settings.gd")

var _failures: PackedStringArray = []
var _passed: int = 0


func _initialize() -> void:
	print("[H1 consolidation error-free smoke] starting…")
	_test_source_no_absolute_root_get_node()
	_test_action_bar_no_fixture_wording()
	_test_main_has_safe_autoload_helper()
	_test_companion_has_safe_router_resolve()
	_test_orphan_absolute_path_is_unsafe_pattern()
	# SceneTree -s: children enter the tree after first frame (not mid-_initialize).
	await process_frame
	await _test_runtime_tree_root_resolve_no_absolute()
	_finish()


func _finish() -> void:
	if _failures.is_empty():
		print("AIDLE_H1_CONSOLIDATION_ERROR_FREE_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"AIDLE_H1_CONSOLIDATION_ERROR_FREE_SMOKE=FAIL failed=%d passed=%d"
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


func _read(path: String) -> String:
	if not FileAccess.file_exists(path):
		return ""
	return FileAccess.get_file_as_string(path)


func _test_source_no_absolute_root_get_node() -> void:
	## Static gate: leased product scripts must not call get_node(_or_null)("/root/...").
	var paths := PackedStringArray([
		"res://scripts/main/main.gd",
		"res://scripts/modules/companion/companion_chat_panel.gd",
		"res://scripts/ui/playable_action_bar.gd",
	])
	var abs_patterns := PackedStringArray([
		'get_node_or_null("/root/',
		"get_node_or_null('/root/",
		'get_node("/root/',
		"get_node('/root/",
	])
	for p in paths:
		var src := _read(p)
		if src.is_empty():
			_fail("source_missing", p)
			return
		for pat in abs_patterns:
			if src.find(pat) >= 0:
				_fail("absolute_root_get_node", "%s contains %s" % [p, pat])
				return
		if src.find('"/root/Control') >= 0 or src.find("'/root/Control") >= 0:
			_fail("absolute_root_control_literal", p)
			return
	_ok("source_no_absolute_root_get_node")


func _test_action_bar_no_fixture_wording() -> void:
	var src := _read("res://scripts/ui/playable_action_bar.gd")
	if src.is_empty():
		_fail("action_bar_missing")
		return
	# Banned first-session chrome strings (H1-CODEX-F03).
	var banned := PackedStringArray([
		"Paid (fixture)",
		"Paid API (fixture)",
		"(fixture)",
	])
	for b in banned:
		if src.find(b) >= 0:
			_fail("action_bar_banned_chrome", b)
			return
	# Word "fixture" must not appear in product chrome strings/comments of this bar.
	if src.findn("fixture") >= 0:
		_fail("action_bar_contains_fixture_token")
		return
	if src.find("Free Bridge") < 0:
		_fail("action_bar_missing_free_bridge_label")
		return
	if src.find("API Gateway") < 0:
		_fail("action_bar_missing_api_gateway_label")
		return
	_ok("action_bar_no_fixture_wording")


func _test_main_has_safe_autoload_helper() -> void:
	var src := _read("res://scripts/main/main.gd")
	if src.find("func _autoload_node") < 0:
		_fail("main_missing__autoload_node")
		return
	if src.find("func _control_router") < 0 or src.find("func _control_a11y") < 0:
		_fail("main_missing_control_helpers")
		return
	if src.find('_autoload_node("ControlContextRouter")') < 0:
		_fail("main_router_not_using_autoload_helper")
		return
	if src.find('_autoload_node("ControlAccessibilitySettings")') < 0:
		_fail("main_a11y_not_using_autoload_helper")
		return
	# Must use tree.root relative lookup, not absolute /root.
	if src.find("tree.root") < 0 and src.find("get_tree().root") < 0:
		_fail("main_autoload_helper_not_tree_root")
		return
	_ok("main_has_safe_autoload_helper")


func _test_companion_has_safe_router_resolve() -> void:
	var src := _read("res://scripts/modules/companion/companion_chat_panel.gd")
	if src.find("func _resolve_control_router") < 0:
		_fail("companion_missing__resolve_control_router")
		return
	if src.find('_resolve_control_router()') < 0:
		_fail("companion_delete_not_using_safe_resolve")
		return
	if src.find('get_node_or_null("ControlContextRouter")') < 0 \
			and src.find("r.get_node_or_null(\"ControlContextRouter\")") < 0:
		_fail("companion_resolve_not_relative")
		return
	_ok("companion_has_safe_router_resolve")


func _test_runtime_tree_root_resolve_no_absolute() -> void:
	## Runtime proof: relative root lookup finds autoloads without absolute paths.
	var router := _ensure_router()
	var a11y := _ensure_a11y()
	var host := Node.new()
	host.name = "ErrorFreeHost"
	root.add_child(host)
	if not host.is_inside_tree():
		await process_frame
	if not host.is_inside_tree():
		_fail("host_not_in_tree_after_frame")
		host.queue_free()
		return
	# Mimic product _autoload_node: relative under tree.root only.
	var resolved_router := _safe_autoload(host, "ControlContextRouter")
	var resolved_a11y := _safe_autoload(host, "ControlAccessibilitySettings")
	if resolved_router == null:
		_fail("runtime_router_null")
		host.queue_free()
		return
	if resolved_a11y == null:
		_fail("runtime_a11y_null")
		host.queue_free()
		return
	if str(resolved_router.name) != "ControlContextRouter":
		_fail("runtime_router_name", str(resolved_router.name))
		host.queue_free()
		return
	if str(resolved_a11y.name) != "ControlAccessibilitySettings":
		_fail("runtime_a11y_name", str(resolved_a11y.name))
		host.queue_free()
		return
	# Also prove SceneTree.root relative lookup (same safe family as product helpers).
	var via_root := root.get_node_or_null("ControlContextRouter")
	if via_root == null:
		_fail("scene_tree_root_relative_null")
		host.queue_free()
		return
	# Orphan (not in tree) must return null without absolute path call.
	var orphan := Node.new()
	var orphan_r := _safe_autoload(orphan, "ControlContextRouter")
	if orphan_r != null:
		_fail("orphan_should_be_null")
		orphan.free()
		host.queue_free()
		return
	orphan.free()
	host.queue_free()
	if router == null or a11y == null:
		pass
	_ok("runtime_tree_root_resolve_no_absolute")


func _test_orphan_absolute_path_is_unsafe_pattern() -> void:
	## Document the bug class: absolute /root paths from outside tree are unsafe.
	## We do NOT call get_node("/root/...") here (would emit USER ERROR). Instead
	## assert product sources no longer use that pattern (already gated) and that
	## the safe helper short-circuits when !is_inside_tree().
	var n := Node.new()
	if n.is_inside_tree():
		_fail("fresh_node_unexpectedly_in_tree")
		n.free()
		return
	var safe := _safe_autoload(n, "ControlContextRouter")
	if safe != null:
		_fail("safe_autoload_on_orphan_not_null")
		n.free()
		return
	n.free()
	_ok("orphan_safe_short_circuit")


func _safe_autoload(from: Node, node_name: String) -> Node:
	## Mirrors main.gd _autoload_node / companion _resolve_control_router.
	if from == null or not from.is_inside_tree():
		return null
	var tree := from.get_tree()
	if tree == null:
		return null
	var r := tree.root
	if r == null:
		return null
	var direct := r.get_node_or_null(node_name)
	if direct != null:
		return direct
	for c in r.get_children():
		if str(c.name) == node_name:
			return c
	return null


func _ensure_router() -> Node:
	var existing := root.get_node_or_null("ControlContextRouter")
	if existing != null:
		return existing
	for c in root.get_children():
		if str(c.name) == "ControlContextRouter":
			return c
	var r: Node = RouterScript.new() as Node
	r.name = "ControlContextRouter"
	root.add_child(r)
	return r


func _ensure_a11y() -> Node:
	var existing := root.get_node_or_null("ControlAccessibilitySettings")
	if existing != null:
		return existing
	for c in root.get_children():
		if str(c.name) == "ControlAccessibilitySettings":
			return c
	var a: Node = A11yScript.new() as Node
	a.name = "ControlAccessibilitySettings"
	root.add_child(a)
	return a

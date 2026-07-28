## WO-H1-CONSOLIDATE-001-RUNTIME-ROOT-CORRECTION-002 / Directive 76 — R0.
## Whole-runtime static gate: no executable absolute-root get_node in game/scripts.
## Runtime gate: player/router/a11y resolve attached + detached without USER ERROR.
## Product scripts are load()-ed after autoloads (not const preload) for -s safety.
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/h1_runtime_autoload_lookup_smoke.gd
## Exit 0 + AIDLE_H1_RUNTIME_AUTOLOAD_LOOKUP_SMOKE=PASS
extends SceneTree

const RouterScript = preload("res://autoload/control_context_router.gd")
const A11yScript = preload("res://autoload/control_accessibility_settings.gd")

## Lease set from WO R0 (must be zero absolute-root hits).
const LEASED_SCRIPTS := [
	"res://scripts/camera/cozy_camera.gd",
	"res://scripts/player/player_controller.gd",
	"res://scripts/ui/hud.gd",
	"res://scripts/ui/control_1b_cursor_label.gd",
	"res://scripts/ui/control_1b_inspect_panel.gd",
	"res://scripts/modules/block_assembly/block_assembly_controller.gd",
	"res://scripts/modules/manifestation/manifestation_instance.gd",
	"res://scripts/modules/executor/headed_demo_flow.gd",
]

const ABS_PATTERNS := [
	'get_node_or_null("/root/',
	"get_node_or_null('/root/",
	'get_node("/root/',
	"get_node('/root/",
]

## Scripts safe to bare-instantiate under -s (no @onready scene paths).
## hud.gd is scene-bound (@onready $Root/...) — covered by static gates + helper presence.
const PRODUCT_LOAD_PATHS := [
	"res://scripts/player/player_controller.gd",
	"res://scripts/camera/cozy_camera.gd",
	"res://scripts/ui/control_1b_cursor_label.gd",
	"res://scripts/ui/control_1b_inspect_panel.gd",
	"res://scripts/modules/block_assembly/block_assembly_controller.gd",
	"res://scripts/modules/manifestation/manifestation_instance.gd",
	"res://scripts/modules/executor/headed_demo_flow.gd",
]

var _failures: PackedStringArray = []
var _passed: int = 0
var _scan_hits: Array = []
var _runtime_ok_count: int = 0


func _initialize() -> void:
	print("[H1 runtime autoload lookup smoke] starting…")
	_test_static_scan_scripts_tree()
	_test_leased_scripts_clean()
	_test_hud_no_fixture_wording()
	_test_leased_helpers_present()
	# SceneTree -s: children + autoload globals ready after first frame.
	await process_frame
	await process_frame
	await _test_runtime_player_router_a11y_attached_and_detached()
	await _test_runtime_leased_hosts_attached_and_detached()
	if _runtime_ok_count < 2:
		_fail("runtime_gates_incomplete", "runtime_ok=%d expected=2" % _runtime_ok_count)
	_finish()


func _finish() -> void:
	if _failures.is_empty():
		print(
			"AIDLE_H1_RUNTIME_AUTOLOAD_LOOKUP_SMOKE=PASS checks=%d scan_hits=%d runtime_ok=%d"
			% [_passed, _scan_hits.size(), _runtime_ok_count]
		)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"AIDLE_H1_RUNTIME_AUTOLOAD_LOOKUP_SMOKE=FAIL failed=%d passed=%d scan_hits=%d runtime_ok=%d"
			% [_failures.size(), _passed, _scan_hits.size(), _runtime_ok_count]
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


func _collect_gd_files(dir_path: String, acc: PackedStringArray) -> void:
	var d := DirAccess.open(dir_path)
	if d == null:
		return
	d.list_dir_begin()
	var name := d.get_next()
	while name != "":
		if name == "." or name == "..":
			name = d.get_next()
			continue
		var full := dir_path.path_join(name)
		if d.current_is_dir():
			_collect_gd_files(full, acc)
		elif name.ends_with(".gd"):
			acc.append(full)
		name = d.get_next()
	d.list_dir_end()


func _scan_file_for_absolute(path: String) -> Array:
	var hits: Array = []
	var raw := _read(path)
	if raw.is_empty():
		return hits
	var lines := raw.split("\n")
	for li in range(lines.size()):
		var line: String = lines[li]
		var trimmed := line.strip_edges()
		if trimmed.begins_with("#"):
			continue
		for pat in ABS_PATTERNS:
			if line.find(pat) >= 0:
				hits.append({
					"path": path,
					"line": li + 1,
					"snippet": trimmed.substr(0, mini(120, trimmed.length())),
					"pattern": pat,
				})
	return hits


func _test_static_scan_scripts_tree() -> void:
	## Whole-runtime static gate over game/scripts/**/*.gd.
	var files: PackedStringArray = []
	_collect_gd_files("res://scripts", files)
	if files.is_empty():
		_fail("static_scan_no_files")
		return
	_scan_hits.clear()
	var leased_hits := 0
	var outside_hits := 0
	for f in files:
		var hits := _scan_file_for_absolute(f)
		for h in hits:
			_scan_hits.append(h)
			var is_leased := LEASED_SCRIPTS.has(str(h.path))
			if is_leased:
				leased_hits += 1
				print("  LEASED_HIT %s:%s %s" % [h.path, h.line, h.snippet])
			else:
				outside_hits += 1
				print("  OUTSIDE_LEASE_HIT %s:%s %s" % [h.path, h.line, h.snippet])
	print(
		"  static_scan files=%d absolute_hits=%d leased=%d outside_lease=%d"
		% [files.size(), _scan_hits.size(), leased_hits, outside_hits]
	)
	if leased_hits > 0:
		_fail("static_leased_absolute_root_remaining", "count=%d" % leased_hits)
		return
	if outside_hits > 0:
		_fail(
			"static_whole_runtime_absolute_root_remaining",
			"outside_lease_hits=%d (see OUTSIDE_LEASE_HIT lines)" % outside_hits
		)
		return
	_ok("static_scan_scripts_tree_clean files=%d" % files.size())


func _test_leased_scripts_clean() -> void:
	for p in LEASED_SCRIPTS:
		var src := _read(p)
		if src.is_empty():
			_fail("leased_source_missing", p)
			return
		for pat in ABS_PATTERNS:
			if src.find(pat) >= 0:
				var bad := false
				for line in src.split("\n"):
					if line.find(pat) >= 0 and not line.strip_edges().begins_with("#"):
						bad = true
						break
				if bad:
					_fail("leased_absolute_root", "%s contains %s" % [p, pat])
					return
	_ok("leased_scripts_clean n=%d" % LEASED_SCRIPTS.size())


func _test_hud_no_fixture_wording() -> void:
	var src := _read("res://scripts/ui/hud.gd")
	if src.is_empty():
		_fail("hud_missing")
		return
	var banned := PackedStringArray([
		"Paid (fixture)",
		"Paid API (fixture)",
		"(fixture)",
	])
	for b in banned:
		if src.find(b) >= 0:
			_fail("hud_banned_chrome", b)
			return
	if src.findn("fixture") >= 0:
		_fail("hud_contains_fixture_token")
		return
	if src.find("Free Bridge") < 0:
		_fail("hud_missing_free_bridge")
		return
	if src.find("API Gateway") < 0:
		_fail("hud_missing_api_gateway")
		return
	_ok("hud_no_fixture_wording")


func _test_leased_helpers_present() -> void:
	for p in LEASED_SCRIPTS:
		var src := _read(p)
		if src.find("func _autoload_node") < 0:
			_fail("missing__autoload_node", p)
			return
		if src.find("is_inside_tree()") < 0:
			_fail("missing_is_inside_tree_guard", p)
			return
		if src.find("get_node_or_null(node_name)") < 0 and src.find("r.get_node_or_null") < 0:
			_fail("missing_tree_root_relative", p)
			return
	_ok("leased_helpers_present")


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


func _load_script(path: String) -> Script:
	var res = load(path)
	if res == null or not (res is Script):
		return null
	return res as Script


func _test_runtime_player_router_a11y_attached_and_detached() -> void:
	var router := _ensure_router()
	var a11y := _ensure_a11y()
	if router == null or a11y == null:
		_fail("ensure_autoload_failed")
		return

	var player_script := _load_script("res://scripts/player/player_controller.gd")
	if player_script == null:
		_fail("player_script_load_null")
		return
	var player: Node = player_script.new() as Node
	if player == null:
		_fail("player_new_null")
		return
	player.name = "SmokePlayer"
	root.add_child(player)
	if not player.is_inside_tree():
		await process_frame
	if not player.is_inside_tree():
		_fail("player_not_in_tree")
		player.queue_free()
		return

	if not player.has_method("_control_router") or not player.has_method("_control_a11y"):
		_fail("player_missing_control_helpers")
		player.queue_free()
		return
	var pr: Node = player.call("_control_router") as Node
	var pa: Node = player.call("_control_a11y") as Node
	if pr == null or str(pr.name) != "ControlContextRouter":
		_fail("player_router_attached_null", str(pr))
		player.queue_free()
		return
	if pa == null or str(pa.name) != "ControlAccessibilitySettings":
		_fail("player_a11y_attached_null", str(pa))
		player.queue_free()
		return
	# Exercise suppress + sprint paths (must not emit USER ERROR).
	if player.has_method("_should_suppress_from_router"):
		player.call("_should_suppress_from_router")
	if player.has_method("_is_sprinting"):
		player.call("_is_sprinting")

	# Detach: helpers must short-circuit to null (no absolute-path USER ERROR).
	root.remove_child(player)
	if player.is_inside_tree():
		_fail("player_still_in_tree_after_remove")
		player.free()
		return
	var pr2: Node = player.call("_control_router") as Node
	var pa2: Node = player.call("_control_a11y") as Node
	if pr2 != null or pa2 != null:
		_fail("player_detached_should_null", "router=%s a11y=%s" % [str(pr2), str(pa2)])
		player.free()
		return
	if player.has_method("_should_suppress_from_router"):
		var s2: bool = bool(player.call("_should_suppress_from_router"))
		if s2:
			_fail("detached_suppress_should_false")
			player.free()
			return
	player.free()
	_runtime_ok_count += 1
	_ok("runtime_player_router_a11y_attached_and_detached")


func _test_runtime_leased_hosts_attached_and_detached() -> void:
	_ensure_router()
	_ensure_a11y()

	var hosts: Array = []
	for path in PRODUCT_LOAD_PATHS:
		if path.ends_with("player_controller.gd"):
			continue  # covered by dedicated player gate
		var sc := _load_script(path)
		if sc == null:
			_fail("product_script_load_null", path)
			for h in hosts:
				if is_instance_valid(h):
					h.free()
			return
		var n: Node = sc.new() as Node
		if n == null:
			_fail("product_script_new_null", path)
			for h in hosts:
				if is_instance_valid(h):
					h.free()
			return
		n.name = "Smoke_%s" % path.get_file().replace(".gd", "")
		root.add_child(n)
		hosts.append(n)
	await process_frame

	for n in hosts:
		if not n.is_inside_tree():
			_fail("host_not_in_tree", n.name)
			for h in hosts:
				if is_instance_valid(h):
					h.queue_free()
			return
		if n.has_method("_autoload_node"):
			var r: Node = n.call("_autoload_node", "ControlContextRouter") as Node
			if r == null:
				_fail("host_router_null", n.name)
				for h in hosts:
					if is_instance_valid(h):
						h.queue_free()
				return
		if n.has_method("_control_router"):
			var r2: Node = n.call("_control_router") as Node
			if r2 == null:
				_fail("host_control_router_null", n.name)
				for h in hosts:
					if is_instance_valid(h):
						h.queue_free()
				return
		if n.has_method("_control_a11y"):
			var a: Node = n.call("_control_a11y") as Node
			if a == null:
				_fail("host_control_a11y_null", n.name)
				for h in hosts:
					if is_instance_valid(h):
						h.queue_free()
				return
		# Exercise a few known call sites without absolute /root.
		if n.has_method("_is_build_context"):
			n.call("_is_build_context")
		if n.has_method("_mouse_sensitivity"):
			n.call("_mouse_sensitivity")
		if n.has_method("_set_router_preview_flag"):
			n.call("_set_router_preview_flag", false)
		if n.has_method("_set_router_preview_target"):
			n.call("_set_router_preview_target", false)
		if n.has_method("_reduced_motion_active"):
			n.call("_reduced_motion_active")
		if n.has_method("_resolve_action_label"):
			n.call("_resolve_action_label")

	# Detach all; must short-circuit null without absolute get_node USER ERROR.
	for n in hosts:
		if n.get_parent() != null:
			n.get_parent().remove_child(n)
		if n.has_method("_autoload_node"):
			var r3: Node = n.call("_autoload_node", "ControlContextRouter") as Node
			if r3 != null:
				_fail("host_detached_not_null", n.name)
				for h in hosts:
					if is_instance_valid(h):
						h.free()
				return
		n.free()

	_runtime_ok_count += 1
	_ok("runtime_leased_hosts_attached_and_detached")

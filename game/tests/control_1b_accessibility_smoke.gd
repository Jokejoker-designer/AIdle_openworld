## WO-CTRL-1B-002 B0 — accessibility settings + remap/preset persistence smokes.
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/control_1b_accessibility_smoke.gd
## Exit 0 + AIDLE_CTRL_1B_A11Y_SMOKE=PASS.
extends SceneTree

const A11yScript = preload("res://autoload/control_accessibility_settings.gd")
const BindingScript = preload("res://scripts/input/control_binding_manager.gd")
const CatalogScript = preload("res://scripts/input/control_action_catalog.gd")

var _failures: PackedStringArray = []
var _passed: int = 0
var _a11y: Node = null


func _initialize() -> void:
	print("[CTRL-1B-002 a11y smoke] starting…")
	CatalogScript.ensure_input_map_actions()
	_a11y = _resolve_a11y()
	if _a11y == null:
		_fail("a11y_unavailable")
		_finish()
		return
	# Ensure lazy manager + settings even if autoload _ready has not fired yet.
	if _a11y.has_method("_ensure_binding_manager"):
		_a11y.call("_ensure_binding_manager")
	if _a11y.has_method("load_settings") and not bool(_a11y.get("_loaded")):
		_a11y.call("load_settings")

	_test_defaults_snapshot()
	_test_mouse_sensitivity_clamp()
	_test_sprint_hold_toggle()
	_test_reduced_motion_and_shake()
	_test_hide_aura()
	_test_cursor_and_confirm_hold()
	_test_remap_known_action()
	_test_remap_unknown_rejected()
	_test_left_hand_preset()
	_test_one_hand_preset()
	_test_persist_roundtrip()
	_test_binding_manager_defaults()
	_finish()


func _resolve_a11y() -> Node:
	var existing := root.get_node_or_null("ControlAccessibilitySettings")
	if existing == null:
		for c in root.get_children():
			if str(c.name) == "ControlAccessibilitySettings":
				existing = c
				break
	if existing != null:
		print("  using autoload ControlAccessibilitySettings")
		return existing
	var node: Node = A11yScript.new() as Node
	root.add_child(node)
	print("  instantiated ControlAccessibilitySettings locally")
	return node


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _test_defaults_snapshot() -> void:
	var snap: Dictionary = _a11y.call("get_snapshot") as Dictionary
	if not snap.has("mouse_sensitivity"):
		_fail("snapshot_missing_mouse")
		return
	if not snap.has("reduced_motion"):
		_fail("snapshot_missing_reduced_motion")
		return
	if not snap.has("hide_aura"):
		_fail("snapshot_missing_hide_aura")
		return
	if not snap.has("confirmation_hold_seconds"):
		_fail("snapshot_missing_hold")
		return
	if not snap.has("sprint_mode"):
		_fail("snapshot_missing_sprint")
		return
	_ok("defaults_snapshot")


func _test_mouse_sensitivity_clamp() -> void:
	_a11y.call("set_mouse_sensitivity", 9.0, false)
	var s: float = float(_a11y.get("mouse_sensitivity"))
	if s > 3.0 + 0.001:
		_fail("mouse_sens_not_clamped_high", str(s))
		return
	_a11y.call("set_mouse_sensitivity", 0.01, false)
	s = float(_a11y.get("mouse_sensitivity"))
	if s < 0.1 - 0.001:
		_fail("mouse_sens_not_clamped_low", str(s))
		return
	_a11y.call("set_mouse_sensitivity", 1.25, false)
	s = float(_a11y.get("mouse_sensitivity"))
	if absf(s - 1.25) > 0.001:
		_fail("mouse_sens_set", str(s))
		return
	_ok("mouse_sensitivity_clamp")


func _test_sprint_hold_toggle() -> void:
	if not bool(_a11y.call("set_sprint_mode", "toggle", false)):
		_fail("sprint_toggle_set")
		return
	if str(_a11y.get("sprint_mode")) != "toggle":
		_fail("sprint_mode_value")
		return
	if bool(_a11y.call("set_sprint_mode", "invalid_mode", false)):
		_fail("sprint_invalid_accepted")
		return
	if not bool(_a11y.call("set_sprint_mode", "hold", false)):
		_fail("sprint_hold_set")
		return
	_ok("sprint_hold_toggle")


func _test_reduced_motion_and_shake() -> void:
	_a11y.call("set_reduced_motion", false, false)
	_a11y.call("set_screen_shake_enabled", true, false)
	if not bool(_a11y.call("effective_screen_shake")):
		_fail("shake_should_be_on")
		return
	_a11y.call("set_reduced_motion", true, false)
	if bool(_a11y.call("effective_screen_shake")):
		_fail("reduced_motion_should_kill_shake")
		return
	_a11y.call("set_reduced_motion", false, false)
	_a11y.call("set_screen_shake_enabled", false, false)
	if bool(_a11y.call("effective_screen_shake")):
		_fail("shake_disabled_flag")
		return
	_a11y.call("set_screen_shake_enabled", true, false)
	_ok("reduced_motion_screen_shake")



func _test_hide_aura() -> void:
	# Commercial polish residual: blueprint hide-aura privacy setting.
	_a11y.call("set_hide_aura", false, false)
	if bool(_a11y.get("hide_aura")):
		_fail("hide_aura_default_false")
		return
	if not bool(_a11y.call("effective_aura_visible")):
		_fail("effective_aura_should_be_visible")
		return
	_a11y.call("set_hide_aura", true, false)
	if not bool(_a11y.get("hide_aura")):
		_fail("hide_aura_not_set")
		return
	if bool(_a11y.call("effective_aura_visible")):
		_fail("effective_aura_should_hide")
		return
	var snap: Dictionary = _a11y.call("get_snapshot") as Dictionary
	if not bool(snap.get("hide_aura", false)):
		_fail("snapshot_hide_aura_false")
		return
	if bool(snap.get("effective_aura_visible", true)):
		_fail("snapshot_effective_aura_visible")
		return
	_a11y.call("set_hide_aura", false, false)
	_ok("hide_aura_privacy")

func _test_cursor_and_confirm_hold() -> void:
	_a11y.call("set_cursor_size_scale", 5.0, false)
	var c: float = float(_a11y.get("cursor_size_scale"))
	if c > 2.0 + 0.001:
		_fail("cursor_not_clamped", str(c))
		return
	_a11y.call("set_confirmation_hold_seconds", 0.0, false)
	if absf(float(_a11y.get("confirmation_hold_seconds")) - 0.0) > 0.001:
		_fail("hold_zero")
		return
	_a11y.call("set_confirmation_hold_seconds", 0.8, false)
	if absf(float(_a11y.get("confirmation_hold_seconds")) - 0.8) > 0.001:
		_fail("hold_default")
		return
	_a11y.call("set_confirmation_hold_seconds", 9.0, false)
	if float(_a11y.get("confirmation_hold_seconds")) > 2.0 + 0.001:
		_fail("hold_not_clamped")
		return
	_ok("cursor_and_confirmation_hold")


func _test_remap_known_action() -> void:
	# Remap interact_primary away from E to T.
	var r: Dictionary = _a11y.call("remap_action", "interact_primary", KEY_T) as Dictionary
	if not bool(r.get("ok", false)):
		_fail("remap_interact", str(r))
		return
	var events := InputMap.action_get_events("interact_primary")
	var has_t := false
	var has_e := false
	for e in events:
		if e is InputEventKey:
			var pk := int((e as InputEventKey).physical_keycode)
			if pk == KEY_T:
				has_t = true
			if pk == KEY_E:
				has_e = true
	if not has_t:
		_fail("remap_missing_T")
		return
	if has_e:
		_fail("remap_still_has_E")
		return
	# Restore default for other tests.
	_a11y.call("apply_default_bindings", false)
	_ok("remap_known_action")


func _test_remap_unknown_rejected() -> void:
	var r: Dictionary = _a11y.call("remap_action", "not_an_action", KEY_H) as Dictionary
	if bool(r.get("ok", true)):
		_fail("unknown_action_remap_accepted")
		return
	if str(r.get("error", "")) != "unknown_action_id":
		_fail("unknown_action_error", str(r))
		return
	_ok("remap_unknown_rejected")


func _test_left_hand_preset() -> void:
	var r: Dictionary = _a11y.call("apply_left_hand_preset", false) as Dictionary
	if not bool(r.get("ok", false)):
		_fail("left_hand_preset", str(r))
		return
	if str(r.get("preset", "")) != "left_hand":
		_fail("left_hand_id", str(r))
		return
	# Move should still exist with bindings.
	if InputMap.action_get_events("move_forward").is_empty():
		_fail("left_hand_move_empty")
		return
	if not InputMap.has_action("jump"):
		_fail("left_hand_lost_jump")
		return
	_ok("left_hand_preset")


func _test_one_hand_preset() -> void:
	var r: Dictionary = _a11y.call("apply_one_hand_preset", false) as Dictionary
	if not bool(r.get("ok", false)):
		_fail("one_hand_preset", str(r))
		return
	if str(r.get("preset", "")) != "one_hand":
		_fail("one_hand_id", str(r))
		return
	if InputMap.action_get_events("move_left").is_empty():
		_fail("one_hand_move_empty")
		return
	_ok("one_hand_preset")


func _test_persist_roundtrip() -> void:
	# Use isolated values, save, re-read via load_settings on a fresh instance when possible.
	_a11y.call("set_mouse_sensitivity", 1.7, false)
	_a11y.call("set_reduced_motion", true, false)
	_a11y.call("set_hide_aura", true, false)
	_a11y.call("set_confirmation_hold_seconds", 1.2, false)
	_a11y.call("set_sprint_mode", "toggle", false)
	_a11y.call("save_settings")
	# Reload on same node.
	_a11y.call("load_settings")
	if absf(float(_a11y.get("mouse_sensitivity")) - 1.7) > 0.001:
		_fail("persist_mouse", str(_a11y.get("mouse_sensitivity")))
		return
	if not bool(_a11y.get("reduced_motion")):
		_fail("persist_reduced_motion")
		return
	if not bool(_a11y.get("hide_aura")):
		_fail("persist_hide_aura")
		return
	if absf(float(_a11y.get("confirmation_hold_seconds")) - 1.2) > 0.001:
		_fail("persist_hold", str(_a11y.get("confirmation_hold_seconds")))
		return
	if str(_a11y.get("sprint_mode")) != "toggle":
		_fail("persist_sprint")
		return
	# Reset to defaults for project cleanliness.
	_a11y.call("set_mouse_sensitivity", 1.0, false)
	_a11y.call("set_reduced_motion", false, false)
	_a11y.call("set_hide_aura", false, false)
	_a11y.call("set_confirmation_hold_seconds", 0.8, false)
	_a11y.call("set_sprint_mode", "hold", false)
	_a11y.call("apply_default_bindings", false)
	_a11y.call("save_settings")
	_ok("persist_roundtrip")


func _test_binding_manager_defaults() -> void:
	var bm = BindingScript.new()
	var r: Dictionary = bm.apply_default_bindings(false) as Dictionary
	if not bool(r.get("ok", false)):
		_fail("binding_defaults", str(r))
		return
	if not InputMap.has_action("prompt_quick_open"):
		_fail("defaults_missing_slash_action")
		return
	if not InputMap.has_action("build_rotate_right"):
		_fail("defaults_missing_build_rotate")
		return
	# Unknown invent rejection at import.
	var bad: Dictionary = bm.import_overrides({
		"preset": "custom",
		"overrides": {"totally_fake_action": [{"type": "key", "keycode": KEY_H}]},
	}) as Dictionary
	if bool(bad.get("ok", true)):
		_fail("import_unknown_accepted")
		return
	_ok("binding_manager_defaults_and_reject")


func _finish() -> void:
	var autoload_a11y := root.get_node_or_null("ControlAccessibilitySettings")
	if _a11y != null and _a11y.get_parent() == root and _a11y != autoload_a11y:
		_a11y.queue_free()
	if _failures.is_empty():
		print("AIDLE_CTRL_1B_A11Y_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("AIDLE_CTRL_1B_A11Y_SMOKE=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
		quit(1)

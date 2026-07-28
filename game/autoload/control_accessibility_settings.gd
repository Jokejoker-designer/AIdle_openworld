## Control 1B accessibility settings state (persist via user:// — SettingsManager pattern).
## Covers remap hooks, left/one-hand presets, hold/toggle sprint, mouse sensitivity,
## reduced_motion, hide_aura, screen_shake, cursor_size, confirmation_hold (C1B-A11Y-01..15 + commercial aura privacy).
extends Node

const BindingManagerScript = preload("res://scripts/input/control_binding_manager.gd")
const CatalogScript = preload("res://scripts/input/control_action_catalog.gd")

const SETTINGS_PATH := "user://control_a11y.cfg"
const SECTION := "control_a11y"
const SECTION_BINDINGS := "bindings"

signal accessibility_changed(key: String, value: Variant)
signal preset_applied(preset_id: String)

var _config: ConfigFile = ConfigFile.new()
var _binding_manager = null  # ControlBindingManager (RefCounted)
var _loaded: bool = false

# Runtime state (defaults match contract §7)
var mouse_sensitivity: float = 1.0
var invert_zoom: bool = false
var reduced_motion: bool = false
## Companion/expression aura privacy — when true, consumers must not render aura VFX (blueprint 07 hide-aura).
var hide_aura: bool = false
var screen_shake_enabled: bool = true
var cursor_size_scale: float = 1.0
## Optional near-cursor action label (default off). Does not force a custom/square cursor proxy.
var action_label_near_cursor: bool = false
## When false (default), normal OS pointer is used. True enables optional non-square a11y
## pointer via control_1b_cursor_label (H1-CODEX-MB-F06 wiring). Never a forced square proxy.
var force_custom_cursor: bool = false
var confirmation_hold_seconds: float = 0.8
var sprint_mode: String = "hold"  # "hold" | "toggle"
var no_mandatory_double_click: bool = true


func _ready() -> void:
	_ensure_binding_manager()
	CatalogScript.ensure_input_map_actions()
	load_settings()
	print("[ControlAccessibilitySettings] Ready — sprint=%s reduced_motion=%s hold=%.2f" % [
		sprint_mode, reduced_motion, confirmation_hold_seconds
	])


func _ensure_binding_manager() -> void:
	## Headless -s may call methods before _ready; keep manager always available.
	if _binding_manager == null:
		_binding_manager = BindingManagerScript.new()


func get_binding_manager():
	_ensure_binding_manager()
	return _binding_manager


func load_settings() -> void:
	_ensure_binding_manager()
	var err := _config.load(SETTINGS_PATH)
	if err != OK:
		_apply_defaults_to_config()
		save_settings()
	else:
		_read_from_config()
	_loaded = true
	# Align mouse sensitivity with SettingsManager gameplay key when present (non-breaking).
	_sync_mouse_from_settings_manager()


func save_settings() -> void:
	_ensure_binding_manager()
	_write_to_config()
	var err := _config.save(SETTINGS_PATH)
	if err != OK:
		push_warning("[ControlAccessibilitySettings] save failed: %s" % error_string(err))


func _apply_defaults_to_config() -> void:
	mouse_sensitivity = 1.0
	invert_zoom = false
	reduced_motion = false
	hide_aura = false
	screen_shake_enabled = true
	cursor_size_scale = 1.0
	action_label_near_cursor = false
	force_custom_cursor = false
	confirmation_hold_seconds = 0.8
	sprint_mode = "hold"
	no_mandatory_double_click = true
	_write_to_config()


func _write_to_config() -> void:
	_config.set_value(SECTION, "mouse_sensitivity", mouse_sensitivity)
	_config.set_value(SECTION, "invert_zoom", invert_zoom)
	_config.set_value(SECTION, "reduced_motion", reduced_motion)
	_config.set_value(SECTION, "hide_aura", hide_aura)
	_config.set_value(SECTION, "screen_shake_enabled", screen_shake_enabled)
	_config.set_value(SECTION, "cursor_size_scale", cursor_size_scale)
	_config.set_value(SECTION, "action_label_near_cursor", action_label_near_cursor)
	_config.set_value(SECTION, "force_custom_cursor", force_custom_cursor)
	_config.set_value(SECTION, "confirmation_hold_seconds", confirmation_hold_seconds)
	_config.set_value(SECTION, "sprint_mode", sprint_mode)
	_config.set_value(SECTION, "no_mandatory_double_click", no_mandatory_double_click)
	if _binding_manager != null:
		var exported: Dictionary = _binding_manager.export_overrides()
		_config.set_value(SECTION_BINDINGS, "preset", str(exported.get("preset", "default")))
		_config.set_value(SECTION_BINDINGS, "overrides_json", JSON.stringify(exported.get("overrides", {})))


func _read_from_config() -> void:
	mouse_sensitivity = clampf(float(_config.get_value(SECTION, "mouse_sensitivity", 1.0)), 0.1, 3.0)
	invert_zoom = bool(_config.get_value(SECTION, "invert_zoom", false))
	reduced_motion = bool(_config.get_value(SECTION, "reduced_motion", false))
	hide_aura = bool(_config.get_value(SECTION, "hide_aura", false))
	screen_shake_enabled = bool(_config.get_value(SECTION, "screen_shake_enabled", true))
	cursor_size_scale = clampf(float(_config.get_value(SECTION, "cursor_size_scale", 1.0)), 0.75, 2.0)
	action_label_near_cursor = bool(_config.get_value(SECTION, "action_label_near_cursor", false))
	force_custom_cursor = bool(_config.get_value(SECTION, "force_custom_cursor", false))
	confirmation_hold_seconds = clampf(
		float(_config.get_value(SECTION, "confirmation_hold_seconds", 0.8)), 0.0, 2.0
	)
	var sm := str(_config.get_value(SECTION, "sprint_mode", "hold"))
	sprint_mode = sm if sm in ["hold", "toggle"] else "hold"
	no_mandatory_double_click = bool(_config.get_value(SECTION, "no_mandatory_double_click", true))
	if _binding_manager != null:
		var preset := str(_config.get_value(SECTION_BINDINGS, "preset", "default"))
		var ovs_json := str(_config.get_value(SECTION_BINDINGS, "overrides_json", "{}"))
		var parsed: Variant = JSON.parse_string(ovs_json)
		if typeof(parsed) == TYPE_DICTIONARY and not (parsed as Dictionary).is_empty():
			_binding_manager.import_overrides({"preset": preset, "overrides": parsed})
		elif preset == "left_hand":
			_binding_manager.apply_left_hand_preset()
		elif preset == "one_hand":
			_binding_manager.apply_one_hand_preset()


func _sync_mouse_from_settings_manager() -> void:
	## Prefer existing SettingsManager gameplay.mouse_sensitivity when available.
	var sm = _get_settings_manager()
	if sm == null:
		return
	if sm.has_method("get_value"):
		var v: Variant = sm.call("get_value", "gameplay", "mouse_sensitivity", mouse_sensitivity)
		mouse_sensitivity = clampf(float(v), 0.1, 3.0)


func _get_settings_manager() -> Node:
	## Prefer sibling autoload under SceneTree root (no absolute /root paths — headless-safe).
	if not is_inside_tree():
		return null
	var tree := get_tree()
	if tree == null:
		return null
	var r := tree.root
	if r == null:
		return null
	var direct := r.get_node_or_null("SettingsManager")
	if direct != null:
		return direct
	for c in r.get_children():
		if str(c.name) == "SettingsManager":
			return c
	return null


func set_mouse_sensitivity(value: float, persist: bool = true) -> void:
	mouse_sensitivity = clampf(value, 0.1, 3.0)
	# Mirror into SettingsManager when present (non-breaking).
	var sm = _get_settings_manager()
	if sm != null and sm.has_method("set_value"):
		sm.call("set_value", "gameplay", "mouse_sensitivity", mouse_sensitivity, persist)
	if persist:
		save_settings()
	accessibility_changed.emit("mouse_sensitivity", mouse_sensitivity)


func set_invert_zoom(value: bool, persist: bool = true) -> void:
	invert_zoom = value
	if persist:
		save_settings()
	accessibility_changed.emit("invert_zoom", invert_zoom)


func set_reduced_motion(value: bool, persist: bool = true) -> void:
	reduced_motion = value
	if persist:
		save_settings()
	accessibility_changed.emit("reduced_motion", reduced_motion)



func set_hide_aura(value: bool, persist: bool = true) -> void:
	## Blueprint 07: hide companion/expression aura for privacy / sensory preference.
	hide_aura = value
	if persist:
		save_settings()
	accessibility_changed.emit("hide_aura", hide_aura)

func set_screen_shake_enabled(value: bool, persist: bool = true) -> void:
	screen_shake_enabled = value
	if persist:
		save_settings()
	accessibility_changed.emit("screen_shake_enabled", screen_shake_enabled)


func set_cursor_size_scale(value: float, persist: bool = true) -> void:
	cursor_size_scale = clampf(value, 0.75, 2.0)
	if persist:
		save_settings()
	accessibility_changed.emit("cursor_size_scale", cursor_size_scale)


func set_confirmation_hold_seconds(value: float, persist: bool = true) -> void:
	confirmation_hold_seconds = clampf(value, 0.0, 2.0)
	if persist:
		save_settings()
	accessibility_changed.emit("confirmation_hold_seconds", confirmation_hold_seconds)


func set_sprint_mode(mode: String, persist: bool = true) -> bool:
	if mode != "hold" and mode != "toggle":
		return false
	sprint_mode = mode
	if persist:
		save_settings()
	accessibility_changed.emit("sprint_mode", sprint_mode)
	return true


func set_action_label_near_cursor(value: bool, persist: bool = true) -> void:
	action_label_near_cursor = value
	if persist:
		save_settings()
	accessibility_changed.emit("action_label_near_cursor", action_label_near_cursor)


func set_force_custom_cursor(value: bool, persist: bool = true) -> void:
	## Default false: normal OS pointer (H1-HUMAN-UX-02). True only for explicit a11y preference.
	force_custom_cursor = value
	if persist:
		save_settings()
	accessibility_changed.emit("force_custom_cursor", force_custom_cursor)


func apply_left_hand_preset(persist: bool = true) -> Dictionary:
	_ensure_binding_manager()
	var r: Dictionary = _binding_manager.apply_left_hand_preset()
	if persist and bool(r.get("ok", false)):
		save_settings()
	if bool(r.get("ok", false)):
		preset_applied.emit("left_hand")
	return r


func apply_one_hand_preset(persist: bool = true) -> Dictionary:
	_ensure_binding_manager()
	var r: Dictionary = _binding_manager.apply_one_hand_preset()
	if persist and bool(r.get("ok", false)):
		save_settings()
	if bool(r.get("ok", false)):
		preset_applied.emit("one_hand")
	return r


func apply_default_bindings(persist: bool = true) -> Dictionary:
	_ensure_binding_manager()
	var r: Dictionary = _binding_manager.apply_default_bindings(false)
	if persist and bool(r.get("ok", false)):
		save_settings()
	if bool(r.get("ok", false)):
		preset_applied.emit("default")
	return r


func remap_action(action_id: String, keycode: int, ctrl: bool = false, shift: bool = false) -> Dictionary:
	_ensure_binding_manager()
	var r: Dictionary = _binding_manager.remap_action_to_key(action_id, keycode, ctrl, shift)
	if bool(r.get("ok", false)):
		save_settings()
		accessibility_changed.emit("remap", action_id)
	return r


func get_snapshot() -> Dictionary:
	_ensure_binding_manager()
	return {
		"mouse_sensitivity": mouse_sensitivity,
		"invert_zoom": invert_zoom,
		"reduced_motion": reduced_motion,
		"hide_aura": hide_aura,
		"effective_aura_visible": not hide_aura,
		"screen_shake_enabled": screen_shake_enabled,
		"cursor_size_scale": cursor_size_scale,
		"action_label_near_cursor": action_label_near_cursor,
		"force_custom_cursor": force_custom_cursor,
		"os_pointer_default": not force_custom_cursor and is_equal_approx(cursor_size_scale, 1.0),
		"confirmation_hold_seconds": confirmation_hold_seconds,
		"sprint_mode": sprint_mode,
		"no_mandatory_double_click": no_mandatory_double_click,
		"preset": _binding_manager.get_active_preset() if _binding_manager else "default",
	}


func effective_screen_shake() -> bool:
	## Reduced motion disables non-essential shake when combined.
	if reduced_motion:
		return false
	return screen_shake_enabled

func effective_aura_visible() -> bool:
	## Consumers (companion/expression) must honor hide_aura; default visible when false.
	return not hide_aura

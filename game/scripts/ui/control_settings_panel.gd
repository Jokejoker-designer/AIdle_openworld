## Control 1B accessibility / control settings panel.
## Remap hooks, left/one-hand presets, hold/toggle sprint, mouse sensitivity,
## reduced motion, screen shake, cursor size, confirmation hold (C1B-A11Y-01..15).
extends CanvasLayer

signal closed()
signal settings_changed(key: String, value: Variant)

const CatalogScript = preload("res://scripts/input/control_action_catalog.gd")

var _panel: PanelContainer
var _status: Label
var _sensitivity: HSlider
var _confirm_hold: HSlider
var _cursor_size: HSlider
var _sprint_option: OptionButton
var _reduced_motion: CheckBox
var _screen_shake: CheckBox
var _invert_zoom: CheckBox
var _action_label_cursor: CheckBox
var _remap_action: OptionButton
var _open: bool = false
var _a11y: Node = null


func _ready() -> void:
	layer = 20
	process_mode = Node.PROCESS_MODE_ALWAYS
	visible = false
	_build_ui()
	_resolve_a11y()
	add_to_group("control_1b_settings_panel")


func _resolve_a11y() -> void:
	if not is_inside_tree():
		return
	var r := get_tree().root
	_a11y = r.get_node_or_null("ControlAccessibilitySettings")
	if _a11y == null:
		for c in r.get_children():
			if str(c.name) == "ControlAccessibilitySettings":
				_a11y = c
				break


func is_open() -> bool:
	return _open


func open_panel() -> void:
	_resolve_a11y()
	_sync_from_a11y()
	visible = true
	_open = true
	if _sprint_option:
		_sprint_option.grab_focus()


func close_panel() -> void:
	visible = false
	_open = false
	closed.emit()


func toggle_panel() -> void:
	if _open:
		close_panel()
	else:
		open_panel()


func _build_ui() -> void:
	var root := Control.new()
	root.name = "Root"
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(root)

	var dim := ColorRect.new()
	dim.name = "Dim"
	dim.color = Color(0, 0, 0, 0.45)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	root.add_child(dim)

	_panel = PanelContainer.new()
	_panel.name = "Panel"
	_panel.set_anchors_preset(Control.PRESET_CENTER)
	_panel.anchor_left = 0.5
	_panel.anchor_right = 0.5
	_panel.anchor_top = 0.5
	_panel.anchor_bottom = 0.5
	_panel.offset_left = -220
	_panel.offset_right = 220
	_panel.offset_top = -240
	_panel.offset_bottom = 240
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.09, 0.11, 0.15, 0.97)
	sb.set_corner_radius_all(12)
	sb.content_margin_left = 14
	sb.content_margin_right = 14
	sb.content_margin_top = 12
	sb.content_margin_bottom = 12
	sb.border_width_left = 2
	sb.border_width_top = 2
	sb.border_width_right = 2
	sb.border_width_bottom = 2
	sb.border_color = Color("FFF1C7").darkened(0.15)
	_panel.add_theme_stylebox_override("panel", sb)
	root.add_child(_panel)

	var scroll := ScrollContainer.new()
	scroll.name = "Scroll"
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.custom_minimum_size = Vector2(400, 450)
	_panel.add_child(scroll)

	var vbox := VBoxContainer.new()
	vbox.name = "VBox"
	vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vbox.add_theme_constant_override("separation", 8)
	scroll.add_child(vbox)

	var title := Label.new()
	title.text = "Control & Accessibility"
	title.add_theme_font_size_override("font_size", 16)
	title.add_theme_color_override("font_color", Color("FFF8E7"))
	vbox.add_child(title)

	_status = Label.new()
	_status.name = "Status"
	_status.text = "Settings ready"
	_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_status.add_theme_font_size_override("font_size", 11)
	_status.add_theme_color_override("font_color", Color(0.85, 0.9, 0.95))
	vbox.add_child(_status)

	# Presets
	var preset_row := HBoxContainer.new()
	preset_row.add_theme_constant_override("separation", 6)
	vbox.add_child(preset_row)
	_add_btn(preset_row, "Default", func(): _apply_preset("default"))
	_add_btn(preset_row, "Left-hand", func(): _apply_preset("left_hand"))
	_add_btn(preset_row, "One-hand", func(): _apply_preset("one_hand"))

	# Sprint hold/toggle
	var sprint_row := HBoxContainer.new()
	sprint_row.add_theme_constant_override("separation", 8)
	vbox.add_child(sprint_row)
	var sprint_l := Label.new()
	sprint_l.text = "Sprint mode"
	sprint_l.custom_minimum_size = Vector2(120, 0)
	sprint_row.add_child(sprint_l)
	_sprint_option = OptionButton.new()
	_sprint_option.focus_mode = Control.FOCUS_ALL
	_sprint_option.add_item("Hold", 0)
	_sprint_option.add_item("Toggle", 1)
	_sprint_option.item_selected.connect(_on_sprint_selected)
	sprint_row.add_child(_sprint_option)

	# Mouse sensitivity
	_sensitivity = _add_slider_row(vbox, "Mouse sensitivity", 0.1, 3.0, 1.0, _on_sensitivity)
	_confirm_hold = _add_slider_row(vbox, "Confirm hold (s)", 0.0, 2.0, 0.8, _on_confirm_hold)
	_cursor_size = _add_slider_row(vbox, "Cursor size", 0.75, 2.0, 1.0, _on_cursor_size)

	_reduced_motion = _add_check(vbox, "Reduced motion", _on_reduced_motion)
	_screen_shake = _add_check(vbox, "Screen shake enabled", _on_screen_shake)
	_invert_zoom = _add_check(vbox, "Invert zoom", _on_invert_zoom)
	_action_label_cursor = _add_check(vbox, "Action label near cursor", _on_action_label)

	# Remap: complete remappable Control 1B foundation catalog (A3-F09 / C1B-A11Y-01).
	var remap_title := Label.new()
	remap_title.text = "Remap action → key (full foundation catalog)"
	remap_title.add_theme_font_size_override("font_size", 12)
	vbox.add_child(remap_title)

	var remap_row := HBoxContainer.new()
	remap_row.add_theme_constant_override("separation", 6)
	vbox.add_child(remap_row)
	_remap_action = OptionButton.new()
	_remap_action.focus_mode = Control.FOCUS_ALL
	_remap_action.custom_minimum_size = Vector2(220, 0)
	for aid in _remappable_catalog_actions():
		_remap_action.add_item(aid)
	remap_row.add_child(_remap_action)
	_add_btn(remap_row, "→ F", func(): _remap_selected(KEY_F))
	_add_btn(remap_row, "→ G", func(): _remap_selected(KEY_G))
	_add_btn(remap_row, "→ H", func(): _remap_selected(KEY_H))

	var close_row := HBoxContainer.new()
	vbox.add_child(close_row)
	var close_btn := Button.new()
	close_btn.text = "Close (Esc / Back)"
	close_btn.focus_mode = Control.FOCUS_ALL
	close_btn.pressed.connect(close_panel)
	close_row.add_child(close_btn)


func _add_btn(parent: Node, text: String, cb: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.focus_mode = Control.FOCUS_ALL
	b.custom_minimum_size = Vector2(0, 28)
	b.pressed.connect(cb)
	parent.add_child(b)
	return b


func _add_check(parent: Node, text: String, cb: Callable) -> CheckBox:
	var c := CheckBox.new()
	c.text = text
	c.focus_mode = Control.FOCUS_ALL
	c.toggled.connect(cb)
	parent.add_child(c)
	return c


func _add_slider_row(
	parent: Node, label: String, min_v: float, max_v: float, def: float, cb: Callable
) -> HSlider:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	parent.add_child(row)
	var l := Label.new()
	l.text = label
	l.custom_minimum_size = Vector2(140, 0)
	l.add_theme_font_size_override("font_size", 12)
	row.add_child(l)
	var s := HSlider.new()
	s.min_value = min_v
	s.max_value = max_v
	s.step = 0.05
	s.value = def
	s.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	s.custom_minimum_size = Vector2(160, 0)
	s.focus_mode = Control.FOCUS_ALL
	s.value_changed.connect(cb)
	row.add_child(s)
	return s


func _sync_from_a11y() -> void:
	if _a11y == null:
		return
	var snap: Dictionary = {}
	if _a11y.has_method("get_snapshot"):
		snap = _a11y.call("get_snapshot") as Dictionary
	if _sensitivity:
		_sensitivity.set_value_no_signal(float(snap.get("mouse_sensitivity", 1.0)))
	if _confirm_hold:
		_confirm_hold.set_value_no_signal(float(snap.get("confirmation_hold_seconds", 0.8)))
	if _cursor_size:
		_cursor_size.set_value_no_signal(float(snap.get("cursor_size_scale", 1.0)))
	if _sprint_option:
		var sm := str(snap.get("sprint_mode", "hold"))
		_sprint_option.select(1 if sm == "toggle" else 0)
	if _reduced_motion:
		_reduced_motion.set_pressed_no_signal(bool(snap.get("reduced_motion", false)))
	if _screen_shake:
		_screen_shake.set_pressed_no_signal(bool(snap.get("screen_shake_enabled", true)))
	if _invert_zoom:
		_invert_zoom.set_pressed_no_signal(bool(snap.get("invert_zoom", false)))
	if _action_label_cursor:
		_action_label_cursor.set_pressed_no_signal(bool(snap.get("action_label_near_cursor", false)))
	if _status:
		_status.text = "Preset: %s · sprint=%s · hold=%.2fs" % [
			str(snap.get("preset", "default")),
			str(snap.get("sprint_mode", "hold")),
			float(snap.get("confirmation_hold_seconds", 0.8)),
		]


func _apply_preset(preset_id: String) -> void:
	if _a11y == null:
		_status.text = "A11y unavailable"
		return
	var r: Dictionary = {}
	match preset_id:
		"left_hand":
			if _a11y.has_method("apply_left_hand_preset"):
				r = _a11y.call("apply_left_hand_preset") as Dictionary
		"one_hand":
			if _a11y.has_method("apply_one_hand_preset"):
				r = _a11y.call("apply_one_hand_preset") as Dictionary
		_:
			if _a11y.has_method("apply_default_bindings"):
				r = _a11y.call("apply_default_bindings") as Dictionary
	_status.text = "Preset %s → %s" % [preset_id, "OK" if bool(r.get("ok", false)) else str(r)]
	settings_changed.emit("preset", preset_id)
	_sync_from_a11y()


func _remap_selected(keycode: int) -> void:
	if _a11y == null or _remap_action == null:
		return
	var aid := _remap_action.get_item_text(_remap_action.selected)
	if not CatalogScript.is_known_action(aid):
		_status.text = "Reject unknown action"
		return
	var r: Dictionary = {}
	if _a11y.has_method("remap_action"):
		r = _a11y.call("remap_action", aid, keycode) as Dictionary
	_status.text = "Remap %s → %s : %s" % [
		aid, OS.get_keycode_string(keycode), "OK" if bool(r.get("ok", false)) else str(r.get("error", r))
	]
	settings_changed.emit("remap", aid)


func _on_sprint_selected(idx: int) -> void:
	if _a11y == null:
		return
	var mode := "toggle" if idx == 1 else "hold"
	if _a11y.has_method("set_sprint_mode"):
		_a11y.call("set_sprint_mode", mode)
	settings_changed.emit("sprint_mode", mode)
	_status.text = "Sprint mode: %s" % mode


func _on_sensitivity(v: float) -> void:
	if _a11y and _a11y.has_method("set_mouse_sensitivity"):
		_a11y.call("set_mouse_sensitivity", v)
	settings_changed.emit("mouse_sensitivity", v)


func _on_confirm_hold(v: float) -> void:
	if _a11y and _a11y.has_method("set_confirmation_hold_seconds"):
		_a11y.call("set_confirmation_hold_seconds", v)
	settings_changed.emit("confirmation_hold_seconds", v)


func _on_cursor_size(v: float) -> void:
	if _a11y and _a11y.has_method("set_cursor_size_scale"):
		_a11y.call("set_cursor_size_scale", v)
	settings_changed.emit("cursor_size_scale", v)


func _on_reduced_motion(pressed: bool) -> void:
	if _a11y and _a11y.has_method("set_reduced_motion"):
		_a11y.call("set_reduced_motion", pressed)
	settings_changed.emit("reduced_motion", pressed)


func _on_screen_shake(pressed: bool) -> void:
	if _a11y and _a11y.has_method("set_screen_shake_enabled"):
		_a11y.call("set_screen_shake_enabled", pressed)
	settings_changed.emit("screen_shake_enabled", pressed)


func _on_invert_zoom(pressed: bool) -> void:
	if _a11y and _a11y.has_method("set_invert_zoom"):
		_a11y.call("set_invert_zoom", pressed)
	settings_changed.emit("invert_zoom", pressed)


func _on_action_label(pressed: bool) -> void:
	if _a11y and _a11y.has_method("set_action_label_near_cursor"):
		_a11y.call("set_action_label_near_cursor", pressed)
	settings_changed.emit("action_label_near_cursor", pressed)


func get_panel_status() -> String:
	return _status.text if _status else ""


func get_remappable_catalog_count() -> int:
	return _remappable_catalog_actions().size()


func get_remappable_catalog_ids() -> PackedStringArray:
	return _remappable_catalog_actions()


func _remappable_catalog_actions() -> PackedStringArray:
	## Full Control 1B foundation catalog exposed in settings UI (A3-F09).
	## Locomotion/camera/system included so remaps stay catalog-closed.
	var out := PackedStringArray()
	for aid in CatalogScript.ACTION_IDS:
		# Exclude pure movement axes that are multi-event; still remappable via binding manager
		# but always listed for foundation completeness except debug-only noise.
		if aid == "toggle_debug":
			continue
		out.append(aid)
	return out

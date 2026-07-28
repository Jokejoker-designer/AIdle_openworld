## Control 1B Context Action HUD — at most 4 actions; text + icon/pattern (never color alone).
## C1B-HUD-01..05. Updates on ControlContextRouter.context_changed.
extends CanvasLayer

const CatalogScript = preload("res://scripts/input/control_action_catalog.gd")
const MAX_ACTIONS := 4

signal action_slot_activated(action_id: String)

## Glyph/pattern per action (non-color cue). Text always accompanies.
const ACTION_META := {
	"interact_primary": {"glyph": "◎", "label": "Interact", "pattern": "circle"},
	"interact_secondary": {"glyph": "◇", "label": "Secondary", "pattern": "diamond"},
	"world_ability": {"glyph": "✦", "label": "Helper Pulse", "pattern": "star"},
	"world_panel": {"glyph": "⌂", "label": "Homestead", "pattern": "house"},
	"build_mode_toggle": {"glyph": "▣", "label": "Build", "pattern": "square"},
	"build_place": {"glyph": "↓", "label": "Place", "pattern": "arrow_down"},
	"build_module_next": {"glyph": "»", "label": "Next module", "pattern": "chevron"},
	"build_module_prev": {"glyph": "«", "label": "Prev module", "pattern": "chevron"},
	"build_rotate_right": {"glyph": "↻", "label": "Rotate", "pattern": "rotate"},
	"build_snap_toggle": {"glyph": "⊞", "label": "Snap", "pattern": "grid"},
	"cancel_action": {"glyph": "✕", "label": "Cancel", "pattern": "x"},
	"confirm_action": {"glyph": "✓", "label": "Confirm", "pattern": "check"},
	"prompt_send": {"glyph": "➤", "label": "Send", "pattern": "send"},
	"companion_call": {"glyph": "◉", "label": "Companion", "pattern": "ring"},
	"inspect_entity": {"glyph": "?", "label": "Inspect", "pattern": "query"},
	"delete_proposal": {"glyph": "⌫", "label": "Delete Prop.", "pattern": "delete"},
	"cozy_helper_pulse": {"glyph": "✦", "label": "Helper Pulse", "pattern": "star"},
	"cozy_homestead_panel": {"glyph": "⌂", "label": "Homestead", "pattern": "house"},
}

var _root: Control
var _panel: PanelContainer
var _row: HBoxContainer
var _context_label: Label
var _slots: Array = []  # Button
var _current_actions: PackedStringArray = PackedStringArray()
var _router: Node = null


func _ready() -> void:
	layer = 11
	process_mode = Node.PROCESS_MODE_ALWAYS
	_build_ui()
	_resolve_router()
	_refresh_from_router()
	if _router != null and _router.has_signal("context_changed"):
		if not _router.context_changed.is_connected(_on_context_changed):
			_router.context_changed.connect(_on_context_changed)
	get_viewport().size_changed.connect(_apply_responsive)
	_apply_responsive()
	add_to_group("control_1b_context_hud")


func _resolve_router() -> void:
	if not is_inside_tree():
		return
	var r := get_tree().root
	_router = r.get_node_or_null("ControlContextRouter")
	if _router == null:
		for c in r.get_children():
			if str(c.name) == "ControlContextRouter":
				_router = c
				break


func _build_ui() -> void:
	_root = Control.new()
	_root.name = "Root"
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_root)

	_panel = PanelContainer.new()
	_panel.name = "ActionPanel"
	_panel.mouse_filter = Control.MOUSE_FILTER_STOP
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.07, 0.09, 0.12, 0.9)
	sb.set_corner_radius_all(10)
	sb.content_margin_left = 10
	sb.content_margin_right = 10
	sb.content_margin_top = 6
	sb.content_margin_bottom = 6
	sb.border_width_left = 1
	sb.border_width_top = 1
	sb.border_width_right = 1
	sb.border_width_bottom = 1
	sb.border_color = Color("FFF1C7").darkened(0.25)
	_panel.add_theme_stylebox_override("panel", sb)
	_root.add_child(_panel)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 4)
	_panel.add_child(vbox)

	_context_label = Label.new()
	_context_label.name = "ContextLabel"
	# Product chrome: plain context name (no diagnostic counter wall).
	_context_label.text = "Explore"
	_context_label.add_theme_font_size_override("font_size", 11)
	_context_label.add_theme_color_override("font_color", Color("FFF8E7"))
	_context_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.75))
	_context_label.add_theme_constant_override("outline_size", 2)
	vbox.add_child(_context_label)

	_row = HBoxContainer.new()
	_row.name = "Slots"
	_row.add_theme_constant_override("separation", 6)
	vbox.add_child(_row)

	_slots.clear()
	for i in range(MAX_ACTIONS):
		var btn := Button.new()
		btn.name = "Slot%d" % i
		btn.focus_mode = Control.FOCUS_ALL  # C1B-HUD-05 / A11Y-15 keyboard focusable
		btn.custom_minimum_size = Vector2(96, 36)
		btn.add_theme_font_size_override("font_size", 12)
		btn.visible = false
		var idx := i
		btn.pressed.connect(func(): _on_slot_pressed(idx))
		_row.add_child(btn)
		_slots.append(btn)


var _build_compact: bool = false


func _product_context_label(context_id: String) -> String:
	## Player-facing context title — never diagnostic counters or QA tags.
	match context_id:
		"exploration":
			return "Explore"
		"companion":
			return "Companion"
		"build":
			return "Build"
		"inspect":
			return "Inspect"
		"world_tool":
			return "Homestead"
		_:
			return context_id.replace("_", " ").capitalize()


func set_compact_build_mode(compact: bool) -> void:
	## Shrink bottom action strip in Build so BA top HUD does not collide at 868x517 (F05-R2).
	_build_compact = compact
	if _panel == null:
		return
	_panel.modulate = Color(1, 1, 1, 0.88 if compact else 1.0)
	if _context_label != null:
		_context_label.visible = not compact
	_apply_responsive()


func _apply_responsive() -> void:
	if _panel == null:
		return
	var vp := get_viewport().get_visible_rect().size
	var compact := vp.x < 1000.0 or vp.y < 600.0 or _build_compact
	# Sit above the two-row playable action bar so 868x517 does not clip/overlap help layers.
	_panel.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	_panel.anchor_left = 0.5
	_panel.anchor_right = 0.5
	_panel.anchor_top = 1.0
	_panel.anchor_bottom = 1.0
	var w := minf(vp.x - 16.0, 360.0 if compact else 520.0)
	_panel.offset_left = -w * 0.5
	_panel.offset_right = w * 0.5
	# Compact/build: lift higher above action bar to avoid BA top-left panel overlap.
	_panel.offset_top = -128.0 if compact else -92.0
	_panel.offset_bottom = -70.0 if compact else -12.0
	for btn in _slots:
		if btn is Button:
			(btn as Button).custom_minimum_size = Vector2(72 if compact else 96, 26 if compact else 36)
			(btn as Button).add_theme_font_size_override("font_size", 10 if compact else 12)


func _on_context_changed(_prev: String, _new: String) -> void:
	_refresh_from_router()


func _refresh_from_router() -> void:
	if _router == null:
		_resolve_router()
	var ctx := "exploration"
	var actions: PackedStringArray = PackedStringArray()
	if _router != null:
		if _router.has_method("get_primary_context"):
			ctx = str(_router.call("get_primary_context"))
		if _router.has_method("get_hud_actions"):
			actions = _router.call("get_hud_actions") as PackedStringArray
	else:
		actions = CatalogScript.get_context_hud_actions(ctx)
	set_actions(ctx, actions)


func set_actions(context_id: String, actions: PackedStringArray) -> void:
	## Clamp to MAX_ACTIONS (C1B-HUD-01). Never dump full keymap (C1B-HUD-04).
	var clamped: PackedStringArray = actions
	if clamped.size() > MAX_ACTIONS:
		clamped = clamped.slice(0, MAX_ACTIONS)
	_current_actions = clamped
	if _context_label == null or _slots.is_empty():
		# Headless early call or pre-_ready: ensure UI exists.
		if _root == null:
			_build_ui()
		if _context_label == null:
			return
	if _context_label:
		_context_label.text = _product_context_label(context_id)
	for i in range(MAX_ACTIONS):
		if i >= _slots.size():
			break
		var btn: Button = _slots[i] as Button
		if btn == null:
			continue
		if i >= clamped.size():
			btn.visible = false
			btn.text = ""
			btn.set_meta("action_id", "")
			continue
		var aid: String = clamped[i]
		var meta: Dictionary = ACTION_META.get(aid, {
			"glyph": "·",
			"label": aid.replace("_", " "),
			"pattern": "dot",
		}) as Dictionary
		var binding := _binding_hint(aid)
		# Text + glyph + pattern name — color is never sole cue (C1B-HUD-02 / A11Y-14).
		btn.text = "%s %s  [%s]" % [str(meta.get("glyph", "·")), str(meta.get("label", aid)), binding]
		btn.tooltip_text = "%s · pattern=%s · action=%s" % [
			str(meta.get("label", aid)), str(meta.get("pattern", "")), aid
		]
		btn.set_meta("action_id", aid)
		btn.set_meta("pattern", str(meta.get("pattern", "")))
		btn.visible = true
		btn.focus_mode = Control.FOCUS_ALL


func get_visible_action_count() -> int:
	return _current_actions.size()


func get_visible_actions() -> PackedStringArray:
	return _current_actions.duplicate()


func get_slot_texts() -> PackedStringArray:
	var out := PackedStringArray()
	for btn in _slots:
		if btn is Button and (btn as Button).visible:
			out.append((btn as Button).text)
	return out


func _binding_hint(action_id: String) -> String:
	if not InputMap.has_action(action_id):
		return "?"
	var events := InputMap.action_get_events(action_id)
	if events.is_empty():
		return "—"
	var ev: InputEvent = events[0]
	if ev is InputEventKey:
		var k := ev as InputEventKey
		var parts: PackedStringArray = PackedStringArray()
		if k.ctrl_pressed:
			parts.append("Ctrl")
		if k.shift_pressed:
			parts.append("Shift")
		if k.alt_pressed:
			parts.append("Alt")
		parts.append(OS.get_keycode_string(k.keycode if k.keycode != KEY_NONE else k.physical_keycode))
		return "+".join(parts)
	if ev is InputEventMouseButton:
		var mb := ev as InputEventMouseButton
		match mb.button_index:
			MOUSE_BUTTON_LEFT:
				return "LMB"
			MOUSE_BUTTON_RIGHT:
				return "RMB"
			MOUSE_BUTTON_WHEEL_UP:
				return "Wheel+"
			MOUSE_BUTTON_WHEEL_DOWN:
				return "Wheel-"
			_:
				return "Mouse"
	return "?"


func _on_slot_pressed(idx: int) -> void:
	if idx < 0 or idx >= _current_actions.size():
		return
	var aid: String = _current_actions[idx]
	action_slot_activated.emit(aid)
	if _router != null and _router.has_method("try_dispatch"):
		_router.call("try_dispatch", aid)

## Cozy Homestead Panel (B / world_panel) — READ-ONLY.
## No inventory mint, ownership, or currency. Esc closes before pause (cancel target).
extends CanvasLayer

signal opened()
signal closed()

var _panel: PanelContainer
var _body: RichTextLabel
var _open: bool = false
var _router: Node = null


func _ready() -> void:
	layer = 14
	process_mode = Node.PROCESS_MODE_ALWAYS
	visible = false
	_build_ui()
	_resolve_router()
	add_to_group("control_1b_homestead_panel")


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


func is_open() -> bool:
	return _open


func open_panel() -> void:
	_resolve_router()
	_refresh_read_only_content()
	visible = true
	_open = true
	if _router != null and _router.has_method("set_cancel_target"):
		_router.call("set_cancel_target", "world_tool_panel", true)
	if _router != null and _router.has_method("get_primary_context"):
		if str(_router.call("get_primary_context")) == "exploration":
			if _router.has_method("request_context"):
				_router.call("request_context", "world_tool")
	opened.emit()
	print("[CozyHomesteadPanel] open (read-only · no mint/ownership)")


func close_panel() -> void:
	if not _open:
		return
	visible = false
	_open = false
	if _router != null and _router.has_method("set_cancel_target"):
		_router.call("set_cancel_target", "world_tool_panel", false)
	if _router != null and _router.has_method("get_primary_context"):
		if str(_router.call("get_primary_context")) == "world_tool":
			if _router.has_method("request_context"):
				_router.call("request_context", "exploration")
	closed.emit()
	print("[CozyHomesteadPanel] closed")


func toggle_panel() -> void:
	if _open:
		close_panel()
	else:
		open_panel()


func _build_ui() -> void:
	var root := Control.new()
	root.name = "Root"
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)

	_panel = PanelContainer.new()
	_panel.name = "Panel"
	_panel.mouse_filter = Control.MOUSE_FILTER_STOP
	_panel.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	_panel.anchor_left = 1.0
	_panel.anchor_right = 1.0
	_panel.anchor_top = 0.0
	_panel.anchor_bottom = 0.0
	_panel.offset_left = -320
	_panel.offset_right = -12
	_panel.offset_top = 52
	_panel.offset_bottom = 280
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.1, 0.12, 0.14, 0.95)
	sb.set_corner_radius_all(10)
	sb.content_margin_left = 12
	sb.content_margin_right = 12
	sb.content_margin_top = 10
	sb.content_margin_bottom = 10
	sb.border_width_left = 2
	sb.border_width_top = 2
	sb.border_width_right = 2
	sb.border_width_bottom = 2
	sb.border_color = Color("F7B267")
	_panel.add_theme_stylebox_override("panel", sb)
	root.add_child(_panel)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 6)
	_panel.add_child(vbox)

	var title := Label.new()
	title.text = "⌂ Homestead"
	title.add_theme_font_size_override("font_size", 14)
	title.add_theme_color_override("font_color", Color("FFF8E7"))
	title.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.7))
	title.add_theme_constant_override("outline_size", 2)
	vbox.add_child(title)

	var badge := Label.new()
	badge.text = "Read-only · no currency · no ownership mint"
	badge.add_theme_font_size_override("font_size", 10)
	badge.add_theme_color_override("font_color", Color(0.8, 0.85, 0.9))
	vbox.add_child(badge)

	_body = RichTextLabel.new()
	_body.name = "Body"
	_body.bbcode_enabled = true
	_body.fit_content = false
	_body.scroll_active = true
	_body.custom_minimum_size = Vector2(280, 160)
	_body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(_body)

	var close_btn := Button.new()
	close_btn.text = "Close [Esc]"
	close_btn.focus_mode = Control.FOCUS_ALL
	close_btn.pressed.connect(close_panel)
	vbox.add_child(close_btn)

	get_viewport().size_changed.connect(_apply_responsive)
	_apply_responsive()


func _apply_responsive() -> void:
	if _panel == null:
		return
	var vp := get_viewport().get_visible_rect().size
	var compact := vp.x < 1000.0 or vp.y < 600.0
	var w := 260.0 if compact else 308.0
	var h := 200.0 if compact else 228.0
	_panel.offset_left = -w - 12
	_panel.offset_right = -12
	_panel.offset_top = 48.0 if compact else 52.0
	_panel.offset_bottom = _panel.offset_top + h
	if _body:
		_body.custom_minimum_size = Vector2(w - 28, h - 90)


func _refresh_read_only_content() -> void:
	if _body == null:
		return
	var style := "cozy"
	var asm := _autoload("ArtStyleManager")
	if asm != null and asm.has_method("get_active_style_id"):
		style = str(asm.call("get_active_style_id"))
	var space := "private_reality"
	var gm := _autoload("GameManager")
	if gm != null and "current_space_id" in gm:
		space = str(gm.current_space_id)
	_body.clear()
	_body.append_text("[b]Your Cozy Homestead[/b]\n")
	_body.append_text("Space: %s\n" % space.replace("_", " "))
	_body.append_text("Style: %s\n\n" % style)
	_body.append_text("• Garden beds — view only\n")
	_body.append_text("• Workshop shelf — view only\n")
	_body.append_text("• Helper stations — view only\n\n")
	_body.append_text("[i]Read-only panel. Does not mint inventory, ownership, or currency.[/i]\n")
	_body.append_text("[i]World mutations require proposal → confirm → World Commit.[/i]\n")


func get_read_only_snapshot() -> Dictionary:
	return {
		"open": _open,
		"read_only": true,
		"mints_inventory": false,
		"mints_ownership": false,
		"mints_currency": false,
		"durable_mutation": false,
	}


func _autoload(node_name: String) -> Node:
	if not is_inside_tree():
		return null
	var r := get_tree().root
	if r == null:
		return null
	var n := r.get_node_or_null(node_name)
	if n != null:
		return n
	for c in r.get_children():
		if str(c.name) == node_name:
			return c
	return null

## Control 1B read-only Inspect / provenance surface (H-07).
## Opens on inspect_entity; never mutates durable world state.
extends CanvasLayer

signal closed()

var _root: Control
var _panel: PanelContainer
var _title: Label
var _body: RichTextLabel
var _status: Label
var _open: bool = false
var _last_payload: Dictionary = {}


func _ready() -> void:
	layer = 16
	process_mode = Node.PROCESS_MODE_ALWAYS
	visible = false
	_build_ui()
	get_viewport().size_changed.connect(_apply_responsive)
	_apply_responsive()
	add_to_group("control_1b_inspect_panel")


func is_open() -> bool:
	return _open


func get_last_payload() -> Dictionary:
	return _last_payload.duplicate(true)


func is_read_only() -> bool:
	return true


func open_inspect(payload: Dictionary = {}) -> Dictionary:
	## Read-only provenance surface. Never applies durable mutation.
	_last_payload = {
		"read_only": true,
		"durable_mutation": false,
		"direct_durable": false,
		"mutation_class": "inspect_read_only",
		"entity_id": str(payload.get("entity_id", payload.get("id", "selected_entity"))),
		"prompt_id": str(payload.get("prompt_id", "")),
		"recipe_id": str(payload.get("recipe_id", "")),
		"stage": str(payload.get("stage", "unknown")),
		"provenance": (payload.get("provenance", {}) as Dictionary).duplicate(true) if payload.get("provenance", {}) is Dictionary else {},
		"preview_owns_ownership": false,
		"preview_owns_collision": bool(payload.get("preview_owns_collision", false)),
		"has_durable_collision": bool(payload.get("has_durable_collision", false)),
	}
	_refresh_body()
	visible = true
	_open = true
	var router := _control_router()
	if router != null:
		if router.has_method("request_context"):
			router.call("request_context", "inspect")
		if router.has_method("set_cancel_target"):
			router.call("set_cancel_target", "inspect_panel", true)
	print("[Control1BInspect] open read_only=true durable_mutation=false entity=%s" % _last_payload.get("entity_id", ""))
	return _last_payload.duplicate(true)


func close_panel() -> void:
	visible = false
	_open = false
	var router := _control_router()
	if router != null and router.has_method("set_cancel_target"):
		router.call("set_cancel_target", "inspect_panel", false)
	closed.emit()


func _autoload_node(node_name: String) -> Node:
	## SceneTree-root relative lookup — never absolute "/root/..." (H1-CODEX-F01).
	if not is_inside_tree():
		return null
	var tree := get_tree()
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


func _control_router() -> Node:
	return _autoload_node("ControlContextRouter")


func _build_ui() -> void:
	_root = Control.new()
	_root.name = "Root"
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_root)

	_panel = PanelContainer.new()
	_panel.name = "Panel"
	_panel.mouse_filter = Control.MOUSE_FILTER_STOP
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.08, 0.1, 0.14, 0.96)
	sb.set_corner_radius_all(10)
	sb.content_margin_left = 12
	sb.content_margin_right = 12
	sb.content_margin_top = 10
	sb.content_margin_bottom = 10
	sb.border_width_left = 2
	sb.border_width_top = 2
	sb.border_width_right = 2
	sb.border_width_bottom = 2
	sb.border_color = Color("62E6FF").darkened(0.15)
	_panel.add_theme_stylebox_override("panel", sb)
	_root.add_child(_panel)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 6)
	_panel.add_child(vbox)

	_title = Label.new()
	_title.text = "Inspect · read-only provenance"
	_title.add_theme_font_size_override("font_size", 14)
	_title.add_theme_color_override("font_color", Color("FFF8E7"))
	vbox.add_child(_title)

	_status = Label.new()
	_status.text = "No durable mutation · Esc closes"
	_status.add_theme_font_size_override("font_size", 11)
	_status.add_theme_color_override("font_color", Color("9ad7c2"))
	vbox.add_child(_status)

	_body = RichTextLabel.new()
	_body.bbcode_enabled = true
	_body.fit_content = false
	_body.scroll_active = true
	_body.custom_minimum_size = Vector2(280, 120)
	_body.add_theme_font_size_override("normal_font_size", 12)
	vbox.add_child(_body)

	var close_btn := Button.new()
	close_btn.text = "Close (Esc)"
	close_btn.focus_mode = Control.FOCUS_ALL
	close_btn.pressed.connect(close_panel)
	vbox.add_child(close_btn)


func _refresh_body() -> void:
	if _body == null:
		return
	var prov: Dictionary = _last_payload.get("provenance", {}) as Dictionary
	var lines: PackedStringArray = PackedStringArray()
	lines.append("[b]Entity[/b]: %s" % str(_last_payload.get("entity_id", "—")))
	lines.append("[b]Prompt[/b]: %s" % str(_last_payload.get("prompt_id", "—")))
	lines.append("[b]Recipe[/b]: %s" % str(_last_payload.get("recipe_id", "—")))
	lines.append("[b]Stage[/b]: %s" % str(_last_payload.get("stage", "—")))
	lines.append("[b]Durable collision[/b]: %s" % str(_last_payload.get("has_durable_collision", false)))
	lines.append("[b]Read-only[/b]: true · mutation_class=inspect_read_only")
	if not prov.is_empty():
		lines.append("[b]Provenance[/b]:")
		for k in prov.keys():
			lines.append("  · %s = %s" % [str(k), str(prov[k])])
	else:
		lines.append("[i]Provenance empty or unavailable — still non-mutating.[/i]")
	_body.text = "\n".join(lines)
	if _status:
		_status.text = "read_only=true · durable_mutation=false · Esc closes before pause"


func _apply_responsive() -> void:
	if _panel == null:
		return
	var vp := get_viewport().get_visible_rect().size
	var compact := vp.x < 1000.0 or vp.y < 600.0
	_panel.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	_panel.anchor_left = 1.0
	_panel.anchor_right = 1.0
	_panel.anchor_top = 0.0
	_panel.anchor_bottom = 0.0
	var w := 300.0 if compact else 340.0
	var h := 200.0 if compact else 240.0
	_panel.offset_left = -w - 8.0
	_panel.offset_right = -8.0
	_panel.offset_top = 48.0 if compact else 56.0
	_panel.offset_bottom = _panel.offset_top + h
	if _body:
		_body.custom_minimum_size = Vector2(w - 24.0, 100.0 if compact else 130.0)

extends CanvasLayer

## Player-facing HUD with high-contrast pill (Directive 23). Debug behind F3.
## CTRL-1B B1: hosts context action HUD updates; hints reflect active context.

@onready var root_ctrl: Control = $Root
@onready var top_pill: PanelContainer = $Root/TopPill
@onready var top_bar: HBoxContainer = $Root/TopPill/TopBar
@onready var art_label: Label = $Root/TopPill/TopBar/ArtStyleLabel
@onready var space_label: Label = $Root/TopPill/TopBar/SpaceLabel
@onready var edition_label: Label = $Root/TopPill/TopBar/EditionLabel
@onready var hint_label: Label = $Root/HintLabel

var _context_hint: String = "WASD move · E Companion · V Pulse · B Homestead · Esc cancel/pause"


func _ready() -> void:
	_apply_player_theme()
	_refresh()
	_apply_responsive()
	get_viewport().size_changed.connect(_apply_responsive)
	EventBus.art_style_changed.connect(func(_s): _refresh())
	EventBus.player_entered_space.connect(func(space_id, _inst, _p): space_label.text = "Space: %s" % _pretty_space(space_id))
	EventBus.debug_toggled.connect(func(_on): _refresh())
	_wire_router()
	add_to_group("control_1b_hud")
	add_to_group("h1_product_hud")


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


func _wire_router() -> void:
	var router := _control_router()
	if router == null:
		return
	if router.has_signal("context_changed") and not router.context_changed.is_connected(_on_context_changed):
		router.context_changed.connect(_on_context_changed)
	_on_context_changed("", str(router.call("get_primary_context")) if router.has_method("get_primary_context") else "exploration")


func _on_context_changed(_prev: String, new_ctx: String) -> void:
	match new_ctx:
		"companion":
			_context_hint = "Companion · Ctrl+Enter send · Esc close"
		"build":
			_context_hint = "Build · Q/R rotate hologram only · Esc cancel preview"
		"inspect":
			_context_hint = "Inspect · Esc deselect · Delete = proposal only"
		"world_tool":
			_context_hint = "V Helper Pulse · B Homestead · Esc close panel"
		_:
			_context_hint = "WASD move · E Companion · V Pulse · B Homestead · Esc cancel/pause"
	if hint_label:
		hint_label.text = _context_hint


func _apply_player_theme() -> void:
	if top_pill:
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(0.08, 0.1, 0.14, 0.88)
		sb.set_corner_radius_all(10)
		sb.content_margin_left = 12
		sb.content_margin_right = 12
		sb.content_margin_top = 6
		sb.content_margin_bottom = 6
		sb.border_width_left = 1
		sb.border_width_top = 1
		sb.border_width_right = 1
		sb.border_width_bottom = 1
		sb.border_color = Color("FFF1C7").darkened(0.2)
		top_pill.add_theme_stylebox_override("panel", sb)
	var fg := Color("FFF8E7")
	for lbl in [art_label, space_label, edition_label]:
		if lbl == null:
			continue
		lbl.add_theme_color_override("font_color", fg)
		lbl.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.75))
		lbl.add_theme_constant_override("outline_size", 3)
	if hint_label:
		hint_label.add_theme_color_override("font_color", Color(1, 1, 1, 0.9))
		hint_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.7))
		hint_label.add_theme_constant_override("outline_size", 3)


func _apply_responsive() -> void:
	var vp := get_viewport().get_visible_rect().size
	var compact := vp.x < 1000.0 or vp.y < 600.0
	var fs := 11 if compact else 13
	for lbl in [art_label, space_label, edition_label, hint_label]:
		if lbl:
			lbl.add_theme_font_size_override("font_size", fs)
	if top_pill:
		top_pill.offset_left = 8.0 if compact else 12.0
		top_pill.offset_right = -8.0 if compact else -12.0
		top_pill.offset_top = 6.0 if compact else 8.0
		top_pill.offset_bottom = 36.0 if compact else 42.0
	if hint_label:
		# Compact: sit above context HUD + action bar (no clip/overlap at 868x517).
		hint_label.offset_top = -178.0 if compact else -118.0
		hint_label.offset_bottom = -158.0 if compact else -98.0
		hint_label.offset_left = -160.0 if compact else -240.0
		hint_label.offset_right = 160.0 if compact else 240.0
		hint_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART if compact else TextServer.AUTOWRAP_OFF


func _refresh() -> void:
	var style := ArtStyleManager.get_active_style()
	if art_label:
		art_label.text = "Art: %s" % str(style.get("display_name", ArtStyleManager.get_active_style_id()))
	if space_label:
		space_label.text = "Space: %s" % _pretty_space(GameManager.current_space_id)
	if edition_label:
		var ed := "—"
		if SettingsManager != null and SettingsManager.has_method("get_edition"):
			ed = _pretty_edition(str(SettingsManager.get_edition()))
		edition_label.text = "Edition: %s" % ed
	if hint_label:
		hint_label.text = _context_hint


func _pretty_space(space_id: String) -> String:
	match space_id:
		"private_reality":
			return "Private Reality"
		_:
			return space_id.replace("_", " ")


func _pretty_edition(ed: String) -> String:
	match ed:
		"desktop_bridge_free":
			return "Free Bridge (manual)"
		"api_paid":
			return "API Gateway"
		_:
			return ed


func get_context_hint() -> String:
	return _context_hint

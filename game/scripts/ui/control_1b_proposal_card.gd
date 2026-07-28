## Control 1B structured Proposal Card (H-17).
## Companion understanding → card only. Never direct durable mutation.
extends CanvasLayer

signal confirm_requested()
signal cancel_requested()
signal closed()

var _root: Control
var _panel: PanelContainer
var _title: Label
var _understanding: RichTextLabel
var _fields: RichTextLabel
var _status: Label
var _open: bool = false
var _last_proposal: Dictionary = {}


func _ready() -> void:
	layer = 17
	process_mode = Node.PROCESS_MODE_ALWAYS
	visible = false
	_build_ui()
	get_viewport().size_changed.connect(_apply_responsive)
	_apply_responsive()
	add_to_group("control_1b_proposal_card")


func is_open() -> bool:
	return _open


func get_last_proposal() -> Dictionary:
	return _last_proposal.duplicate(true)


func shows_direct_mutation() -> bool:
	return false


func present_proposal(proposal: Dictionary, understanding: String = "") -> Dictionary:
	## Structured card from Companion interpretation. Proposal-only boundary.
	var entity: Dictionary = {}
	if proposal.get("entity", {}) is Dictionary:
		entity = proposal.get("entity", {}) as Dictionary
	elif proposal.get("world_prompt", {}) is Dictionary:
		var wp: Dictionary = proposal.get("world_prompt", {}) as Dictionary
		if wp.get("entity", {}) is Dictionary:
			entity = wp.get("entity", {}) as Dictionary
	var recipe := str(
		entity.get("recipe_id", proposal.get("recipe_id", proposal.get("entity_kind", "build")))
	)
	var prompt_id := str(proposal.get("prompt_id", proposal.get("id", "")))
	var understand := understanding
	if understand.is_empty():
		understand = str(proposal.get("understanding", proposal.get("summary", "")))
	if understand.is_empty():
		understand = "Companion understood a build intent for recipe '%s' (proposal only)." % recipe

	_last_proposal = {
		"card": true,
		"mutation_class": "proposal_only",
		"direct_durable": false,
		"durable_mutation": false,
		"state": "pending_confirm",
		"routes_through": "preview_confirm_commit",
		"recipe_id": recipe,
		"prompt_id": prompt_id,
		"understanding": understand,
		"entity": entity.duplicate(true) if not entity.is_empty() else {},
		"raw_keys": proposal.keys(),
	}
	_refresh()
	visible = true
	_open = true
	print(
		"[Control1BProposalCard] present recipe=%s mutation_class=proposal_only direct_durable=false"
		% recipe
	)
	return _last_proposal.duplicate(true)


func close_card() -> void:
	visible = false
	_open = false
	closed.emit()


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
	sb.bg_color = Color(0.09, 0.11, 0.16, 0.97)
	sb.set_corner_radius_all(12)
	sb.content_margin_left = 12
	sb.content_margin_right = 12
	sb.content_margin_top = 10
	sb.content_margin_bottom = 10
	sb.border_width_left = 2
	sb.border_width_top = 2
	sb.border_width_right = 2
	sb.border_width_bottom = 2
	sb.border_color = Color("FFB86B").darkened(0.1)
	_panel.add_theme_stylebox_override("panel", sb)
	_root.add_child(_panel)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 6)
	_panel.add_child(vbox)

	_title = Label.new()
	_title.text = "Proposal Card · pending confirm"
	_title.add_theme_font_size_override("font_size", 14)
	_title.add_theme_color_override("font_color", Color("FFB86B"))
	vbox.add_child(_title)

	_understanding = RichTextLabel.new()
	_understanding.bbcode_enabled = true
	_understanding.fit_content = true
	_understanding.scroll_active = false
	_understanding.custom_minimum_size = Vector2(260, 40)
	_understanding.add_theme_font_size_override("normal_font_size", 12)
	vbox.add_child(_understanding)

	_fields = RichTextLabel.new()
	_fields.bbcode_enabled = true
	_fields.fit_content = true
	_fields.scroll_active = false
	_fields.custom_minimum_size = Vector2(260, 56)
	_fields.add_theme_font_size_override("normal_font_size", 11)
	vbox.add_child(_fields)

	_status = Label.new()
	_status.text = "No direct mutation · confirm/cancel required"
	_status.add_theme_font_size_override("font_size", 11)
	_status.add_theme_color_override("font_color", Color("9ad7c2"))
	vbox.add_child(_status)

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	vbox.add_child(row)
	var confirm_btn := Button.new()
	confirm_btn.text = "Confirm path"
	confirm_btn.focus_mode = Control.FOCUS_ALL
	confirm_btn.pressed.connect(func(): confirm_requested.emit())
	row.add_child(confirm_btn)
	var cancel_btn := Button.new()
	cancel_btn.text = "Dismiss"
	cancel_btn.focus_mode = Control.FOCUS_ALL
	cancel_btn.pressed.connect(func():
		cancel_requested.emit()
		close_card()
	)
	row.add_child(cancel_btn)


func _refresh() -> void:
	if _understanding:
		_understanding.text = "[b]Understanding[/b]: %s" % str(_last_proposal.get("understanding", ""))
	if _fields:
		_fields.text = (
			"[b]Recipe[/b]: %s\n[b]State[/b]: %s\n[b]Route[/b]: %s\n[b]mutation_class[/b]: proposal_only · direct_durable=false"
			% [
				str(_last_proposal.get("recipe_id", "—")),
				str(_last_proposal.get("state", "pending_confirm")),
				str(_last_proposal.get("routes_through", "preview_confirm_commit")),
			]
		)
	if _status:
		_status.text = "Proposal Card only — never direct durable mutation"


func _apply_responsive() -> void:
	if _panel == null:
		return
	var vp := get_viewport().get_visible_rect().size
	var compact := vp.x < 1000.0 or vp.y < 600.0
	# Top-center, clear of bottom action/help layers at 868x517.
	_panel.set_anchors_preset(Control.PRESET_CENTER_TOP)
	_panel.anchor_left = 0.5
	_panel.anchor_right = 0.5
	_panel.anchor_top = 0.0
	_panel.anchor_bottom = 0.0
	var w := 300.0 if compact else 360.0
	_panel.offset_left = -w * 0.5
	_panel.offset_right = w * 0.5
	_panel.offset_top = 44.0 if compact else 52.0
	_panel.offset_bottom = _panel.offset_top + (168.0 if compact else 190.0)

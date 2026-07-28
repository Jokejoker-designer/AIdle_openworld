## First-run Art Direction picker (Visual Concept Pillars §1).
extends Control

@onready var list: ItemList = $Center/Panel/VBox/StyleList
@onready var desc: Label = $Center/Panel/VBox/Description
@onready var confirm_btn: Button = $Center/Panel/VBox/Confirm

var _style_ids: PackedStringArray = []


func _ready() -> void:
	_populate()
	_apply_responsive()
	get_viewport().size_changed.connect(_apply_responsive)
	list.item_selected.connect(_on_selected)
	confirm_btn.pressed.connect(_on_confirm)
	if list.item_count > 0:
		list.select(0)
		_on_selected(0)


func _apply_responsive() -> void:
	## Keep panel fully visible at 868x517 and 1280x720 (Codex headed gate).
	var panel := get_node_or_null("Center/Panel") as Control
	if panel == null:
		return
	var vp := get_viewport().get_visible_rect().size
	var max_w: float = minf(520.0, vp.x - 24.0)
	var max_h: float = minf(420.0, vp.y - 24.0)
	panel.custom_minimum_size = Vector2(maxf(280.0, max_w), maxf(260.0, max_h))
	var list_node := get_node_or_null("Center/Panel/VBox/StyleList") as Control
	if list_node:
		list_node.custom_minimum_size = Vector2(0, 100.0 if vp.y < 600.0 else 180.0)


func _populate() -> void:
	list.clear()
	_style_ids.clear()
	for style in ArtStyleManager.list_styles():
		var id: String = str(style.get("id", ""))
		var name: String = str(style.get("display_name", id))
		_style_ids.append(id)
		list.add_item(name)


func _on_selected(index: int) -> void:
	if index < 0 or index >= _style_ids.size():
		return
	var style := ArtStyleManager.get_style(_style_ids[index])
	desc.text = str(style.get("description", ""))


func _on_confirm() -> void:
	var selected := list.get_selected_items()
	if selected.is_empty():
		return
	var style_id := _style_ids[selected[0]]
	ArtStyleManager.set_active_style(style_id, true)
	# Enter main world.
	get_tree().change_scene_to_file("res://scenes/main/main.tscn")

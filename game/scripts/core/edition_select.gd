## First-run AGM edition selector (Free Desktop Bridge vs Paid API).
## Transport choice only — same World State Snapshot + Decision Envelope schemas.
## Paid path never prompts for or stores a provider API key / client secret.
extends Control

@onready var list: ItemList = $Center/Panel/VBox/EditionList
@onready var desc: Label = $Center/Panel/VBox/Description
@onready var confirm_btn: Button = $Center/Panel/VBox/Confirm
@onready var secret_note: Label = $Center/Panel/VBox/SecretNote

## id -> { display_name, description }
var _editions: Array[Dictionary] = []


func _ready() -> void:
	_editions = [
		{
			"id": AIdleConstants.EDITION_DESKTOP_BRIDGE_FREE,
			"display_name": "Free — Desktop Bridge",
			"description": (
				"Copy a redacted world snapshot to your AI Desktop (Grok / ChatGPT), "
				+ "then paste the Decision Envelope JSON back. No account API key in the game. "
				+ "Same AGM contracts as Paid."
			),
		},
		{
			"id": AIdleConstants.EDITION_API_PAID,
			"display_name": "Paid — API Gateway",
			"description": (
				"Godot talks to a trusted AIdle gateway later (G5). Provider credentials "
				+ "live only on the gateway — never in this client or world files. "
				+ "Same AGM contracts as Free."
			),
		},
	]
	_populate()
	list.item_selected.connect(_on_selected)
	confirm_btn.pressed.connect(_on_confirm)
	secret_note.text = (
		"Neither mode stores an API key or client secret in Godot. "
		+ "You can change edition later in settings with explicit consent."
	)
	if list.item_count > 0:
		list.select(0)
		_on_selected(0)


func _populate() -> void:
	list.clear()
	for entry in _editions:
		list.add_item(str(entry.get("display_name", entry.get("id", ""))))


func _on_selected(index: int) -> void:
	if index < 0 or index >= _editions.size():
		return
	desc.text = str(_editions[index].get("description", ""))


func _on_confirm() -> void:
	var selected := list.get_selected_items()
	if selected.is_empty():
		return
	var edition_id := str(_editions[selected[0]].get("id", ""))
	# First-run: consent not required when no prior choice is stored.
	var ok := SettingsManager.set_edition(edition_id, true, false)
	if not ok:
		# Existing choice conflict — require consent path (settings later).
		push_warning("[EditionSelect] Could not set edition without consent.")
		return
	_continue_boot()


func _continue_boot() -> void:
	if ArtStyleManager.has_chosen_style():
		get_tree().change_scene_to_file("res://scenes/main/main.tscn")
	else:
		get_tree().change_scene_to_file("res://scenes/ui/art_style_select.tscn")

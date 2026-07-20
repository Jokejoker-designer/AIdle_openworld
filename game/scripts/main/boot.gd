## Boot: load settings → if art style chosen go main, else art select.
extends Control


func _ready() -> void:
	GameManager.notify_booted()
	# Small delay so autoloads finish first-frame setup.
	await get_tree().process_frame
	if ArtStyleManager.has_chosen_style():
		get_tree().change_scene_to_file("res://scenes/main/main.tscn")
	else:
		get_tree().change_scene_to_file("res://scenes/ui/art_style_select.tscn")

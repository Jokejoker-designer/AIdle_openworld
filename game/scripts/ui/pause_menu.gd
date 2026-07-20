extends CanvasLayer

@onready var panel: Control = $Center/Panel


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	visible = false
	EventBus.game_paused.connect(_on_paused)


func _on_paused(is_paused: bool) -> void:
	visible = is_paused


func _on_resume_pressed() -> void:
	GameManager.set_paused(false)


func _on_settings_pressed() -> void:
	# Settings panel is sibling; show it.
	var settings := get_parent().get_node_or_null("SettingsMenu")
	if settings and settings.has_method("open_menu"):
		settings.open_menu()
	GameManager.open_settings_from_pause()


func _on_quit_pressed() -> void:
	get_tree().paused = false
	get_tree().quit()

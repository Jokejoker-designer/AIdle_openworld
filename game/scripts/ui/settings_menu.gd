extends CanvasLayer

@onready var master_slider: HSlider = $Center/Panel/VBox/MasterVolume
@onready var fullscreen_check: CheckBox = $Center/Panel/VBox/Fullscreen
@onready var vsync_check: CheckBox = $Center/Panel/VBox/VSync
@onready var debug_check: CheckBox = $Center/Panel/VBox/DebugOverlay


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	visible = false
	_load_ui()


func open_menu() -> void:
	_load_ui()
	visible = true


func close_menu() -> void:
	visible = false
	GameManager.close_settings_to_pause()


func _load_ui() -> void:
	master_slider.value = float(SettingsManager.get_value(SettingsManager.SECTION_AUDIO, "master_volume", 0.8)) * 100.0
	fullscreen_check.button_pressed = bool(SettingsManager.get_value(SettingsManager.SECTION_GRAPHICS, "fullscreen", false))
	vsync_check.button_pressed = bool(SettingsManager.get_value(SettingsManager.SECTION_GRAPHICS, "vsync", true))
	debug_check.button_pressed = bool(SettingsManager.get_value(SettingsManager.SECTION_DEBUG, "show_overlay", false))


func _on_master_changed(value: float) -> void:
	SettingsManager.set_value(SettingsManager.SECTION_AUDIO, "master_volume", value / 100.0)


func _on_fullscreen_toggled(pressed: bool) -> void:
	SettingsManager.set_value(SettingsManager.SECTION_GRAPHICS, "fullscreen", pressed)


func _on_vsync_toggled(pressed: bool) -> void:
	SettingsManager.set_value(SettingsManager.SECTION_GRAPHICS, "vsync", pressed)


func _on_debug_toggled(pressed: bool) -> void:
	SettingsManager.set_value(SettingsManager.SECTION_DEBUG, "show_overlay", pressed)
	EventBus.debug_toggled.emit(pressed)


func _on_back_pressed() -> void:
	close_menu()

## Persistent settings (graphics, audio, input prefs) + load order before GameManager.
extends Node

const SECTION_AUDIO := "audio"
const SECTION_GRAPHICS := "graphics"
const SECTION_GAMEPLAY := "gameplay"
const SECTION_DEBUG := "debug"

var _config: ConfigFile = ConfigFile.new()
var _loaded: bool = false


func _ready() -> void:
	load_settings()


func load_settings() -> void:
	var err := _config.load(AIdleConstants.SETTINGS_PATH)
	if err != OK:
		_apply_defaults()
		save_settings()
	_loaded = true
	_apply_runtime()


func save_settings() -> void:
	var err := _config.save(AIdleConstants.SETTINGS_PATH)
	if err != OK:
		push_warning("[SettingsManager] Failed to save settings: %s" % error_string(err))


func _apply_defaults() -> void:
	_config.set_value(SECTION_AUDIO, "master_volume", 0.8)
	_config.set_value(SECTION_AUDIO, "music_volume", 0.7)
	_config.set_value(SECTION_AUDIO, "sfx_volume", 0.85)
	_config.set_value(SECTION_GRAPHICS, "fullscreen", false)
	_config.set_value(SECTION_GRAPHICS, "vsync", true)
	_config.set_value(SECTION_GRAPHICS, "shadows", true)
	_config.set_value(SECTION_GAMEPLAY, "mouse_sensitivity", 1.0)
	_config.set_value(SECTION_GAMEPLAY, "camera_zoom", 1.0)
	_config.set_value(SECTION_DEBUG, "show_overlay", false)
	_config.set_value(SECTION_DEBUG, "verbose_logs", true)


func _apply_runtime() -> void:
	var master: float = float(get_value(SECTION_AUDIO, "master_volume", 0.8))
	AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Master"), linear_to_db(clampf(master, 0.0, 1.0)))
	var fs: bool = bool(get_value(SECTION_GRAPHICS, "fullscreen", false))
	if fs:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	var vsync: bool = bool(get_value(SECTION_GRAPHICS, "vsync", true))
	DisplayServer.window_set_vsync_mode(
		DisplayServer.VSYNC_ENABLED if vsync else DisplayServer.VSYNC_DISABLED
	)


func get_value(section: String, key: String, default: Variant = null) -> Variant:
	if _config.has_section_key(section, key):
		return _config.get_value(section, key, default)
	return default


func set_value(section: String, key: String, value: Variant, persist: bool = true) -> void:
	_config.set_value(section, key, value)
	if persist:
		save_settings()
	_apply_runtime()
	EventBus.settings_changed.emit(section, key, value)


func is_debug_overlay_enabled() -> bool:
	return bool(get_value(SECTION_DEBUG, "show_overlay", false))

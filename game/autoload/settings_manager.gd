## Persistent settings (graphics, audio, input prefs) + AGM edition choice.
## Paid edition never stores provider API keys / client secrets (gateway owns auth).
extends Node

const SECTION_AUDIO := "audio"
const SECTION_GRAPHICS := "graphics"
const SECTION_GAMEPLAY := "gameplay"
const SECTION_DEBUG := "debug"
## AGM transport edition only (desktop_bridge_free | api_paid). No secrets here.
const SECTION_AGM := "agm"
const KEY_EDITION := "edition"
const KEY_EDITION_CHOSEN_AT := "edition_chosen_at"

## Keys that must never appear in client settings (paid or free path).
const FORBIDDEN_SECRET_KEYS: PackedStringArray = [
	"api_key",
	"api_key_secret",
	"provider_api_key",
	"openai_api_key",
	"anthropic_api_key",
	"xai_api_key",
	"client_secret",
	"authorization",
	"bearer_token",
	"password",
	"credentials",
	"secret",
	"access_token",
	"refresh_token",
	"provider_token",
]

var _config: ConfigFile = ConfigFile.new()
var _loaded: bool = false
## Runtime-only edition when headless/smoke sets without persist.
var _runtime_edition: String = ""


func _ready() -> void:
	load_settings()


func load_settings() -> void:
	var err := _config.load(AIdleConstants.SETTINGS_PATH)
	if err != OK:
		_apply_defaults()
		save_settings()
	else:
		_strip_forbidden_secrets()
	_loaded = true
	_apply_runtime()


func save_settings() -> void:
	_strip_forbidden_secrets()
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
	# Edition is intentionally NOT defaulted: first-run selector must run.


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
	if _is_forbidden_secret_key(key) or _is_forbidden_secret_key(section):
		push_error(
			"[SettingsManager] Refused to store forbidden secret key '%s' (section=%s)." % [key, section]
		)
		return
	_config.set_value(section, key, value)
	if persist:
		save_settings()
	_apply_runtime()
	EventBus.settings_changed.emit(section, key, value)


func is_debug_overlay_enabled() -> bool:
	return bool(get_value(SECTION_DEBUG, "show_overlay", false))


# ─── AGM edition (G2-007) ────────────────────────────────────────────────────


func is_valid_edition(edition_id: String) -> bool:
	return edition_id in AIdleConstants.AGM_EDITIONS


## True when the player has completed first-run (or consented settings) choice.
func has_chosen_edition() -> bool:
	if not _runtime_edition.is_empty() and is_valid_edition(_runtime_edition):
		return true
	if not _config.has_section_key(SECTION_AGM, KEY_EDITION):
		return false
	return is_valid_edition(str(_config.get_value(SECTION_AGM, KEY_EDITION, "")))


## Active transport edition. Defaults to Free Desktop Bridge if unset.
func get_edition() -> String:
	if not _runtime_edition.is_empty() and is_valid_edition(_runtime_edition):
		return _runtime_edition
	if _config.has_section_key(SECTION_AGM, KEY_EDITION):
		var saved := str(_config.get_value(SECTION_AGM, KEY_EDITION, AIdleConstants.DEFAULT_EDITION))
		if is_valid_edition(saved):
			return saved
	return AIdleConstants.DEFAULT_EDITION


## Free and Paid share identical AGM snapshot/decision contract semantics.
func uses_same_agm_contracts() -> bool:
	return true


## Persist first-run choice, or change an existing choice when consent=true.
## Never accepts or stores provider API keys / client secrets.
func set_edition(edition_id: String, persist: bool = true, consent: bool = false) -> bool:
	if not is_valid_edition(edition_id):
		push_error("[SettingsManager] Unknown AGM edition: %s" % edition_id)
		return false
	var prior_chosen := _config.has_section_key(SECTION_AGM, KEY_EDITION)
	var prior := ""
	if prior_chosen:
		prior = str(_config.get_value(SECTION_AGM, KEY_EDITION, ""))
	if prior_chosen and prior != edition_id and not consent:
		push_warning(
			"[SettingsManager] Edition change from %s → %s requires consent." % [prior, edition_id]
		)
		return false
	if persist:
		_config.set_value(SECTION_AGM, KEY_EDITION, edition_id)
		_config.set_value(
			SECTION_AGM,
			KEY_EDITION_CHOSEN_AT,
			Time.get_datetime_string_from_system(true)
		)
		_runtime_edition = ""
		save_settings()
	else:
		# Headless / ephemeral: do not write user://settings.cfg
		_runtime_edition = edition_id
	EventBus.settings_changed.emit(SECTION_AGM, KEY_EDITION, edition_id)
	print("[SettingsManager] AGM edition → %s (persist=%s)" % [edition_id, persist])
	return true


## Returns only transport metadata safe to attach to snapshots (no secrets).
func get_edition_export() -> Dictionary:
	return {
		"edition": get_edition(),
		"contract_semantics": "identical",
		"stores_client_secret": false,
		"stores_api_key": false,
	}


## True when no forbidden secret keys exist in the in-memory config.
func has_no_client_secrets() -> bool:
	for section in _config.get_sections():
		for key in _config.get_section_keys(section):
			if _is_forbidden_secret_key(str(key)):
				return false
			# Values that look like API keys must not be stored either.
			var val: Variant = _config.get_value(section, key, null)
			if typeof(val) == TYPE_STRING and _looks_like_secret_value(str(val)):
				return false
	return true


func _is_forbidden_secret_key(key: String) -> bool:
	var k := key.strip_edges().to_lower()
	if k.is_empty():
		return false
	if k in FORBIDDEN_SECRET_KEYS:
		return true
	# Catch compound names (e.g. gateway_api_key, xai_client_secret).
	for forbidden in FORBIDDEN_SECRET_KEYS:
		if forbidden in k:
			return true
	return false


func _looks_like_secret_value(value: String) -> bool:
	var v := value.strip_edges()
	if v.begins_with("sk-") or v.begins_with("sk_"):
		return true
	if v.begins_with("Bearer ") or v.begins_with("bearer "):
		return true
	return false


func _strip_forbidden_secrets() -> void:
	var removed: PackedStringArray = []
	for section in _config.get_sections():
		for key in _config.get_section_keys(section):
			var key_s := str(key)
			if _is_forbidden_secret_key(key_s):
				_config.erase_section_key(section, key_s)
				removed.append("%s/%s" % [section, key_s])
				continue
			var val: Variant = _config.get_value(section, key_s, null)
			if typeof(val) == TYPE_STRING and _looks_like_secret_value(str(val)):
				_config.erase_section_key(section, key_s)
				removed.append("%s/%s(value)" % [section, key_s])
	if not removed.is_empty():
		push_warning("[SettingsManager] Stripped forbidden secret keys: %s" % ", ".join(removed))

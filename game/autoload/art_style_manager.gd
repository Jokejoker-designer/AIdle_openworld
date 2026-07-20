## Art Style singleton – Visual Concept Pillars §1.
## Chosen at game start, stored in world metadata, queried by all generators.
extends Node

## style_id -> Dictionary of palette / mood hints for other agents.
var _styles: Dictionary = {}
var _active_style_id: String = AIdleConstants.DEFAULT_ART_STYLE
var _world_meta: ConfigFile = ConfigFile.new()


func _ready() -> void:
	_register_builtin_styles()
	_load_world_meta()
	print("[ArtStyleManager] Active style: %s" % _active_style_id)


func _register_builtin_styles() -> void:
	_styles[AIdleConstants.ART_COZY_CYBER_PIXEL] = {
		"id": AIdleConstants.ART_COZY_CYBER_PIXEL,
		"display_name": "Cozy Cyber-Pixel / Dreamy Low-Poly",
		"description": "Warm, rounded low-poly with soft neon accents. Default recommended.",
		"palette": {
			"primary": Color("F7B267"),
			"secondary": Color("7EC8E3"),
			"accent": Color("E07A5F"),
			"ground": Color("8FBC8F"),
			"sky": Color("8EC5E8"),
			"shadow": Color(0.2, 0.18, 0.25, 0.35),
		},
		"mood": "warm_cozy",
		"geometry_bias": "soft_low_poly",
		"neon_intensity": 0.25,
	}
	_styles[AIdleConstants.ART_SURREALISM_CANVAS] = {
		"id": AIdleConstants.ART_SURREALISM_CANVAS,
		"display_name": "Surrealism Canvas",
		"description": "Floating forms, shifting color, dreamlike proportions.",
		"palette": {
			"primary": Color("C77DFF"),
			"secondary": Color("7B2CBF"),
			"accent": Color("FF9E00"),
			"ground": Color("3C096C"),
			"sky": Color("240046"),
			"shadow": Color(0.1, 0.05, 0.2, 0.5),
		},
		"mood": "dreamlike",
		"geometry_bias": "surreal_scale",
		"neon_intensity": 0.6,
	}
	_styles[AIdleConstants.ART_CYBERPUNK_DENSE] = {
		"id": AIdleConstants.ART_CYBERPUNK_DENSE,
		"display_name": "Cyberpunk Dense",
		"description": "Dense neon city, cool rain tones. Extension style.",
		"palette": {
			"primary": Color("00F5D4"),
			"secondary": Color("FF006E"),
			"accent": Color("FEE440"),
			"ground": Color("1A1A2E"),
			"sky": Color("0F0E17"),
			"shadow": Color(0.0, 0.0, 0.0, 0.6),
		},
		"mood": "neon_night",
		"geometry_bias": "angular_dense",
		"neon_intensity": 0.9,
	}
	_styles[AIdleConstants.ART_PASTORAL_FANTASY] = {
		"id": AIdleConstants.ART_PASTORAL_FANTASY,
		"display_name": "Pastoral Fantasy",
		"description": "Soft pastoral fields, gentle fantasy accents.",
		"palette": {
			"primary": Color("A7C957"),
			"secondary": Color("F2E8CF"),
			"accent": Color("BC4749"),
			"ground": Color("6A994E"),
			"sky": Color("A8DADC"),
			"shadow": Color(0.15, 0.2, 0.1, 0.3),
		},
		"mood": "pastoral",
		"geometry_bias": "soft_organic",
		"neon_intensity": 0.05,
	}


func _load_world_meta() -> void:
	var err := _world_meta.load(AIdleConstants.WORLD_META_PATH)
	if err == OK:
		var saved: String = str(_world_meta.get_value("world", "art_style", AIdleConstants.DEFAULT_ART_STYLE))
		if _styles.has(saved):
			_active_style_id = saved


func save_world_meta() -> void:
	_world_meta.set_value("world", "art_style", _active_style_id)
	_world_meta.set_value("world", "schema_version", AIdleConstants.SCHEMA_VERSION)
	_world_meta.set_value("world", "updated_at", Time.get_datetime_string_from_system(true))
	var err := _world_meta.save(AIdleConstants.WORLD_META_PATH)
	if err != OK:
		push_warning("[ArtStyleManager] Could not save world meta: %s" % error_string(err))


func get_active_style_id() -> String:
	return _active_style_id


func get_active_style() -> Dictionary:
	return _styles.get(_active_style_id, _styles[AIdleConstants.DEFAULT_ART_STYLE]).duplicate(true)


func get_style(style_id: String) -> Dictionary:
	return _styles.get(style_id, {}).duplicate(true)


func list_styles() -> Array:
	var out: Array = []
	for k in _styles.keys():
		out.append(_styles[k].duplicate(true))
	return out


## Called from Art Style select UI at first boot / new world.
func set_active_style(style_id: String, persist: bool = true) -> bool:
	if not _styles.has(style_id):
		push_error("[ArtStyleManager] Unknown art style: %s" % style_id)
		return false
	if _active_style_id == style_id:
		if persist:
			save_world_meta()
		return true
	_active_style_id = style_id
	if persist:
		save_world_meta()
	EventBus.art_style_changed.emit(style_id)
	print("[ArtStyleManager] Style set → %s" % style_id)
	return true


## Hard constraint: generators must call this before creating content.
func query_art_style_for_generation() -> Dictionary:
	return get_active_style()


func has_chosen_style() -> bool:
	return _world_meta.has_section_key("world", "art_style")

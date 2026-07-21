## Art Style singleton – Visual Concept Pillars §1.
## Chosen at game start, stored in world metadata, queried by all generators.
extends Node

## style_id -> Dictionary of palette / mood hints for other agents.
var _styles: Dictionary = {}
var _active_style_id: String = AIdleConstants.DEFAULT_ART_STYLE
var _world_meta: ConfigFile = ConfigFile.new()
## Test-only override so saved-choice proofs never touch the human user's real meta.
var _meta_path_override: String = ""


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
		"description": "Dreamlike accents over a readable ground — purple is accent, not a void field.",
		"palette": {
			"primary": Color("C77DFF"),
			"secondary": Color("9B6BCF"),
			"accent": Color("FF9E00"),
			# Readable diorama base (DESIGN.md: purple as bounded accent, not full field).
			"ground": Color("8B7AA8"),
			"sky": Color("A8B4E0"),
			"shadow": Color(0.12, 0.08, 0.18, 0.4),
		},
		"mood": "dreamlike",
		"geometry_bias": "surreal_scale",
		"neon_intensity": 0.45,
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


func get_world_meta_path() -> String:
	if not _meta_path_override.is_empty():
		return _meta_path_override
	return AIdleConstants.WORLD_META_PATH


## Headed/isolation tests only — never point at the human's real save by accident.
func set_world_meta_path_override(path: String) -> void:
	_meta_path_override = path


func _load_world_meta() -> void:
	var err := _world_meta.load(get_world_meta_path())
	if err == OK:
		var saved: String = str(_world_meta.get_value("world", "art_style", AIdleConstants.DEFAULT_ART_STYLE))
		if _styles.has(saved):
			_active_style_id = saved


func save_world_meta() -> void:
	_world_meta.set_value("world", "art_style", _active_style_id)
	_world_meta.set_value("world", "schema_version", AIdleConstants.SCHEMA_VERSION)
	_world_meta.set_value("world", "updated_at", Time.get_datetime_string_from_system(true))
	var path := get_world_meta_path()
	var abs_path := ProjectSettings.globalize_path(path)
	var parent := abs_path.get_base_dir()
	if not DirAccess.dir_exists_absolute(parent):
		DirAccess.make_dir_recursive_absolute(parent)
	var err := _world_meta.save(path)
	if err != OK:
		push_warning("[ArtStyleManager] Could not save world meta: %s" % error_string(err))


func get_active_style_id() -> String:
	return _active_style_id


func get_active_style() -> Dictionary:
	# ROOT CAUSE (R-MED-06 / WO-P1E-004): GDScript evaluates .get() default args eagerly.
	# `_styles.get(id, _styles[DEFAULT])` always indexes `_styles[DEFAULT]` even when
	# `id` is present. Before `_ready` → `_register_builtin_styles()`, `_styles` is empty,
	# so `_styles["cozy_cyber_pixel"]` (DEFAULT_ART_STYLE) throws:
	#   Invalid access to property or key 'cozy_cyber_pixel' on a base object of type 'Dictionary'
	# The cozy_cyber_pixel entry is NOT missing/malformed — it is registered in
	# `_register_builtin_styles`. Callers (StarterRealmBuilder GLB path, HUD) can run
	# during early boot / headless -s before this autoload's _ready finishes.
	# Fix: ensure builtins exist, then index safely without eager default indexing.
	if _styles.is_empty():
		_register_builtin_styles()
	if _styles.has(_active_style_id):
		return _styles[_active_style_id].duplicate(true)
	if _styles.has(AIdleConstants.DEFAULT_ART_STYLE):
		return _styles[AIdleConstants.DEFAULT_ART_STYLE].duplicate(true)
	push_error("[ArtStyleManager] get_active_style: no styles registered (unexpected)")
	return {}


func get_style(style_id: String) -> Dictionary:
	return _styles.get(style_id, {}).duplicate(true)


func list_styles() -> Array:
	var out: Array = []
	for k in _styles.keys():
		out.append(_styles[k].duplicate(true))
	return out


## Called from Art Style select UI at first boot / new world.
func set_active_style(style_id: String, persist: bool = true) -> bool:
	# Safe when called before _ready completes (headed smoke / early boot).
	if _styles.is_empty():
		_register_builtin_styles()
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


## True when builtins are registered (smoke may wait on this).
func is_styles_ready() -> bool:
	if _styles.is_empty():
		_register_builtin_styles()
	return not _styles.is_empty()


## Product rule: clean world (no prior choice) uses DEFAULT_ART_STYLE.
func get_default_style_id() -> String:
	return AIdleConstants.DEFAULT_ART_STYLE


## Hard constraint: generators must call this before creating content.
func query_art_style_for_generation() -> Dictionary:
	return get_active_style()


func has_chosen_style() -> bool:
	return _world_meta.has_section_key("world", "art_style")

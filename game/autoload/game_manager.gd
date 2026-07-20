## GameManager – session lifecycle, pause, current space, player reference.
## Orchestrates high-level flow; does NOT execute world prompts (that's Agent-Executor).
extends Node

enum GameState { BOOT, ART_STYLE_SELECT, IN_WORLD, PAUSED, SETTINGS }

var state: GameState = GameState.BOOT
var current_space_id: String = AIdleConstants.SPACE_PRIVATE_REALITY
var player: Node3D = null
var world_root: Node3D = null

var _pause_locked: bool = false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	print("[GameManager] AIdle Core %s booting…" % AIdleConstants.CORE_VERSION)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("pause_menu"):
		if state == GameState.IN_WORLD:
			set_paused(true)
			get_viewport().set_input_as_handled()
		elif state == GameState.PAUSED:
			set_paused(false)
			get_viewport().set_input_as_handled()
	elif event.is_action_pressed("toggle_debug"):
		var show_dbg: bool = not SettingsManager.is_debug_overlay_enabled()
		SettingsManager.set_value(SettingsManager.SECTION_DEBUG, "show_overlay", show_dbg)
		EventBus.debug_toggled.emit(show_dbg)
		get_viewport().set_input_as_handled()


func notify_booted() -> void:
	state = GameState.ART_STYLE_SELECT if not ArtStyleManager.has_chosen_style() else GameState.IN_WORLD
	EventBus.game_booted.emit()


func enter_world(world: Node3D, player_node: Node3D) -> void:
	world_root = world
	player = player_node
	state = GameState.IN_WORLD
	current_space_id = AIdleConstants.SPACE_PRIVATE_REALITY
	EventBus.world_ready.emit(world)
	print("[GameManager] World ready. Art style=%s" % ArtStyleManager.get_active_style_id())


func set_current_space(space_id: String) -> void:
	current_space_id = space_id


func set_paused(paused: bool) -> void:
	if _pause_locked:
		return
	if paused:
		state = GameState.PAUSED
		get_tree().paused = true
	else:
		state = GameState.IN_WORLD
		get_tree().paused = false
	EventBus.game_paused.emit(paused)


func open_settings_from_pause() -> void:
	state = GameState.SETTINGS


func close_settings_to_pause() -> void:
	state = GameState.PAUSED


func get_debug_snapshot() -> Dictionary:
	return {
		"core_version": AIdleConstants.CORE_VERSION,
		"state": GameState.keys()[state],
		"space": current_space_id,
		"art_style": ArtStyleManager.get_active_style_id(),
		"modules": ModuleRegistry.list_modules(),
		"fps": Engine.get_frames_per_second(),
		"paused": get_tree().paused,
	}

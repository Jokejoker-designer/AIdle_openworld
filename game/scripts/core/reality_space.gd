## Reality space metadata + authority model (Master Blueprint §3, §2.6).
## Each child under WorldRoot uses this script (or extends it).
class_name RealitySpace
extends Node3D

## Matches Structured World Prompt `target_space` enum values.
@export var space_id: String = AIdleConstants.SPACE_PRIVATE_REALITY

## Display name for UI / debug.
@export var display_name: String = "Private Reality"

## Authority: client | server | owner | system
@export_enum("client", "server", "owner", "system") var authority: String = "client"

## Whether progressive manifestation is allowed in this space.
@export var allows_manifestation: bool = true

## Active art style for this space (mirrors World meta; may diverge later per space).
@export var art_style: String = AIdleConstants.DEFAULT_ART_STYLE

## Optional world / district identifier for multiplayer hubs.
@export var instance_key: String = "default"

signal player_entered(player: Node)
signal player_exited(player: Node)


func _ready() -> void:
	add_to_group("reality_spaces")
	# Hook point: Agent-Network may listen for enter/exit to sync presence.
	if not EventBus.player_entered_space.is_connected(_on_bus_entered):
		pass  # spaces emit via notify_player_entered; bus is global


func get_target_space_key() -> String:
	return space_id


func get_authority() -> String:
	return authority


func is_client_authoritative() -> bool:
	return authority == "client"


func notify_player_entered(player: Node) -> void:
	player_entered.emit(player)
	EventBus.player_entered_space.emit(space_id, instance_key, player)


func notify_player_exited(player: Node) -> void:
	player_exited.emit(player)


func set_art_style(style_id: String) -> void:
	art_style = style_id


func _on_bus_entered(_space: String, _instance: String, _player: Node) -> void:
	pass

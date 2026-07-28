class_name AIdleElementalState
extends Resource

@export var entity_id: StringName
@export var module_id: StringName
@export var elements: Array[StringName] = []
@export var physical_profile_id: StringName
@export_range(0.0, 1.0) var temperature: float = 0.5
@export_range(0.0, 1.0) var wetness: float = 0.0
@export_range(0.0, 1.0) var integrity: float = 1.0
@export_range(0.0, 1.0) var charge: float = 0.0
@export_range(0.0, 1.0) var pressure: float = 0.0
@export_range(0.0, 1.0) var growth: float = 0.0
@export_range(0.0, 1.0) var health: float = 1.0
@export var states: Array[StringName] = []
@export_range(0, 3) var simulation_lod_tier: int = 0

func has_element(element_id: StringName) -> bool:
    return elements.has(element_id)

func add_state(state_id: StringName) -> void:
    if not states.has(state_id):
        states.append(state_id)

func remove_state(state_id: StringName) -> void:
    states.erase(state_id)

func clamp_values() -> void:
    temperature = clampf(temperature, 0.0, 1.0)
    wetness = clampf(wetness, 0.0, 1.0)
    integrity = clampf(integrity, 0.0, 1.0)
    charge = clampf(charge, 0.0, 1.0)
    pressure = clampf(pressure, 0.0, 1.0)
    growth = clampf(growth, 0.0, 1.0)
    health = clampf(health, 0.0, 1.0)

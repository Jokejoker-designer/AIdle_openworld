class_name AIdleElementalBody3D
extends Node3D

signal elemental_state_changed(entity_id: StringName, state: AIdleElementalState)

@export var elemental_state: AIdleElementalState
@export var reaction_enabled := false
@export var canonical_committed := false

func configure_preview(state: AIdleElementalState) -> void:
    elemental_state = state
    reaction_enabled = false
    canonical_committed = false
    _set_physics_enabled(false)

func activate_after_commit() -> void:
    canonical_committed = true
    reaction_enabled = true
    _set_physics_enabled(true)

func set_simulation_lod(tier: int) -> void:
    if elemental_state == null:
        return
    elemental_state.simulation_lod_tier = clampi(tier, 0, 3)
    for child in get_children():
        if child is RigidBody3D:
            child.freeze = tier >= 2
        elif child is GPUParticles3D:
            child.emitting = tier <= 1

func notify_state_changed() -> void:
    elemental_state.clamp_values()
    elemental_state_changed.emit(elemental_state.entity_id, elemental_state)

func _set_physics_enabled(enabled: bool) -> void:
    for child in get_children():
        if child is CollisionShape3D:
            child.disabled = not enabled
        elif child is RigidBody3D:
            child.freeze = not enabled
        elif child is Area3D:
            child.monitoring = enabled
            child.monitorable = enabled

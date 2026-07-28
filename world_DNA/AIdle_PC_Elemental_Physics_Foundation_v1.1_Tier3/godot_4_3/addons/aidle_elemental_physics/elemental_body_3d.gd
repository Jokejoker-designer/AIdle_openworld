class_name AIdleElementalBody3D
extends Node3D

signal elemental_state_changed(entity_id: StringName, state: AIdleElementalState)

@export var elemental_state: AIdleElementalState
@export var chunk_id: StringName
@export var reaction_enabled := false
@export var canonical_committed := false
@export var simulation_update_hz := 60.0
@export var visual_variant_selector_path: NodePath

func configure_preview(state: AIdleElementalState) -> void:
    elemental_state = state
    reaction_enabled = false
    canonical_committed = false
    _set_interaction_enabled(false)

func activate_after_commit() -> void:
    # Called only by the authoritative manifestation/commit path.
    canonical_committed = true
    reaction_enabled = true
    _set_interaction_enabled(true)

func set_simulation_lod(tier: int) -> void:
    if elemental_state == null:
        return
    elemental_state.simulation_lod_tier = clampi(tier, 0, 3)
    match elemental_state.simulation_lod_tier:
        0:
            simulation_update_hz = 60.0
            _set_animation_rate(1.0)
        1:
            simulation_update_hz = 15.0
            _set_animation_rate(0.5)
        2:
            simulation_update_hz = 2.0
            _set_animation_rate(0.0)
        3:
            simulation_update_hz = 0.0
            _set_animation_rate(0.0)

func apply_visual_variant_from_state(wet_threshold: float = 0.6) -> StringName:
    var selector := get_node_or_null(visual_variant_selector_path) as AIdleVisualVariantSelector
    if selector == null or elemental_state == null:
        return &"default"
    return selector.select_from_state({"wetness": elemental_state.wetness}, wet_threshold)

func notify_state_changed() -> void:
    if elemental_state == null:
        return
    elemental_state.clamp_values()
    elemental_state_changed.emit(elemental_state.entity_id, elemental_state)

func set_reconciliation_interactable(enabled: bool) -> void:
    _set_interaction_enabled(enabled and canonical_committed)

func _set_animation_rate(rate: float) -> void:
    for child in find_children("*", "AnimationPlayer", true, false):
        var player := child as AnimationPlayer
        player.speed_scale = rate
        if rate <= 0.0:
            player.pause()
        elif not player.is_playing():
            player.play()

func _set_interaction_enabled(enabled: bool) -> void:
    for child in get_tree().get_nodes_in_group("aidle_interaction"):
        if is_ancestor_of(child):
            child.process_mode = Node.PROCESS_MODE_INHERIT if enabled else Node.PROCESS_MODE_DISABLED

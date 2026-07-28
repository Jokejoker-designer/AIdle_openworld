class_name AIdleReactionResolver
extends Node

signal reaction_applied(reaction_id: StringName, source_id: StringName, target_id: StringName)

@export var registry_path: NodePath
var _cooldowns: Dictionary = {}

func resolve_pair(source: AIdleElementalBody3D, target: AIdleElementalBody3D, allowlist: Array) -> void:
    if source == null or target == null:
        return
    if not source.reaction_enabled or not target.reaction_enabled:
        return
    var registry := get_node_or_null(registry_path) as AIdleElementalRegistry
    if registry == null:
        return
    var sorted_ids := allowlist.duplicate()
    sorted_ids.sort()
    for reaction_id in sorted_ids:
        if not registry.reactions.has(reaction_id):
            continue
        var rule: Dictionary = registry.reactions[reaction_id]
        if _matches(rule, source.elemental_state, target.elemental_state):
            _apply(rule, target.elemental_state)
            target.notify_state_changed()
            reaction_applied.emit(reaction_id, source.elemental_state.entity_id, target.elemental_state.entity_id)

func _matches(rule: Dictionary, a: AIdleElementalState, b: AIdleElementalState) -> bool:
    var combined: Array[StringName] = []
    combined.append_array(a.elements)
    combined.append_array(b.elements)
    for required in rule.get("inputs", []):
        if not combined.has(StringName(required)):
            return false
    return true

func _apply(rule: Dictionary, state: AIdleElementalState) -> void:
    var changes: Dictionary = rule.get("state_changes", {})
    for pair in [["integrity_delta","integrity"],["wetness_delta","wetness"],["charge_delta","charge"]]:
        if changes.has(pair[0]):
            state.set(pair[1], clampf(float(state.get(pair[1])) + float(changes[pair[0]]), 0.0, 1.0))
    if changes.get("burning", false):
        state.add_state(&"BURNING")
    if changes.get("leaking", false):
        state.add_state(&"LEAKING")

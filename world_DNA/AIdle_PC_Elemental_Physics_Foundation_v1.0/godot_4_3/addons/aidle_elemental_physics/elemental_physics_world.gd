class_name AIdleElementalPhysicsWorld
extends Node

@export var lod_controller_path: NodePath
var bodies: Dictionary = {}

func register_body(body: AIdleElementalBody3D) -> void:
    if body == null or body.elemental_state == null:
        return
    bodies[body.elemental_state.entity_id] = body
    var lod := get_node_or_null(lod_controller_path) as AIdleSimulationLODController
    if lod != null:
        lod.register_body(body)

func activate_committed_entity(entity_id: StringName) -> bool:
    var body: AIdleElementalBody3D = bodies.get(entity_id)
    if body == null:
        return false
    body.activate_after_commit()
    return true

func cancel_preview_entity(entity_id: StringName) -> bool:
    var body: AIdleElementalBody3D = bodies.get(entity_id)
    if body == null or body.canonical_committed:
        return false
    bodies.erase(entity_id)
    body.queue_free()
    return true

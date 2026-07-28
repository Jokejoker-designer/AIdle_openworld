class_name AIdleSimulationLODController
extends Node

@export var observer_path: NodePath
@export var tier_distances: Array[float] = [48.0, 144.0, 384.0]
@export var refresh_interval_s := 0.25
var _elapsed := 0.0
var _registered: Array[AIdleElementalBody3D] = []

func register_body(body: AIdleElementalBody3D) -> void:
    if body != null and not _registered.has(body):
        _registered.append(body)

func _process(delta: float) -> void:
    _elapsed += delta
    if _elapsed < refresh_interval_s:
        return
    _elapsed = 0.0
    var observer := get_node_or_null(observer_path) as Node3D
    if observer == null:
        return
    for body in _registered:
        if is_instance_valid(body):
            body.set_simulation_lod(_tier(observer.global_position.distance_to(body.global_position)))

func _tier(distance: float) -> int:
    if distance < tier_distances[0]: return 0
    if distance < tier_distances[1]: return 1
    if distance < tier_distances[2]: return 2
    return 3

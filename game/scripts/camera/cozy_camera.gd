## Cozy 2.5D fixed-angle camera (ARCHITECTURE_LOCK: no free 3D camera in MVP).
## Locked three-quarter pitch; optional discrete 45° yaw snaps (Q/R); zoom only.
## No mouse-look, free orbit, FPS, or continuous yaw drag.
class_name CozyCamera
extends Node3D

@export var target_path: NodePath
@export var follow_offset: Vector3 = Vector3(0.0, 1.1, 0.0)
@export var distance: float = 10.0
@export var min_distance: float = 5.0
@export var max_distance: float = 18.0
## Fixed three-quarter elevation; not player-controlled in MVP.
@export var pitch_degrees: float = 42.0
@export var follow_smooth: float = 8.0
## Discrete compass steps only (not free orbit).
@export var yaw_step_degrees: float = 45.0
@export var yaw_rotate_speed: float = 6.0
## When false, Q/R snaps are ignored (strict fixed yaw).
@export var allow_yaw_snaps: bool = true

var _target: Node3D
var _yaw: float = 0.0
var _target_yaw: float = 0.0
var _distance: float = 10.0
var _camera: Camera3D


func _ready() -> void:
	add_to_group("cozy_camera")
	_camera = get_node_or_null("Camera3D") as Camera3D
	if _camera == null:
		_camera = Camera3D.new()
		_camera.name = "Camera3D"
		add_child(_camera)
	_camera.current = true
	# Perspective FOV kept narrow for soft-isometric read; pitch is the angle lock.
	_camera.fov = 42.0
	_distance = distance
	_yaw = rotation.y
	_target_yaw = _yaw
	if target_path != NodePath(""):
		_target = get_node_or_null(target_path) as Node3D
	if _target == null:
		_target = get_tree().get_first_node_in_group("player") as Node3D
	_apply_camera_transform(1.0)


func _process(delta: float) -> void:
	# Discrete yaw only — never continuous free-look / mouse orbit.
	if allow_yaw_snaps:
		if Input.is_action_just_pressed("rotate_camera_left"):
			_target_yaw += deg_to_rad(yaw_step_degrees)
		if Input.is_action_just_pressed("rotate_camera_right"):
			_target_yaw -= deg_to_rad(yaw_step_degrees)
	if Input.is_action_just_pressed("camera_zoom_in"):
		_distance = clampf(_distance - 1.0, min_distance, max_distance)
	if Input.is_action_just_pressed("camera_zoom_out"):
		_distance = clampf(_distance + 1.0, min_distance, max_distance)

	_yaw = lerp_angle(_yaw, _target_yaw, clampf(yaw_rotate_speed * delta, 0.0, 1.0))
	_apply_camera_transform(delta)


func _apply_camera_transform(delta: float) -> void:
	if _target == null or not is_instance_valid(_target):
		_target = get_tree().get_first_node_in_group("player") as Node3D
		if _target == null:
			return

	# Spherical offset with locked pitch → fixed-angle three-quarter view.
	var pitch := deg_to_rad(pitch_degrees)
	var pivot := _target.global_position + follow_offset
	var offset := Vector3(
		sin(_yaw) * cos(pitch),
		sin(pitch),
		cos(_yaw) * cos(pitch)
	) * _distance
	var desired := pivot + offset
	if delta >= 1.0:
		global_position = desired
	else:
		global_position = global_position.lerp(desired, clampf(follow_smooth * delta, 0.0, 1.0))
	# Face pivot; keep exported pitch lock (no free pitch control).
	look_at(pivot, Vector3.UP)


func get_yaw() -> float:
	## Movement basis for PlayerController (camera-relative XZ).
	return _yaw


func set_target(node: Node3D) -> void:
	_target = node


func get_camera() -> Camera3D:
	return _camera


func is_fixed_angle() -> bool:
	## Acceptance helper: MVP camera is never free 3D orbit/FPS.
	return true

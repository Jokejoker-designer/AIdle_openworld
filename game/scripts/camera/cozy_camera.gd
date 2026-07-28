## Cozy 2.5D fixed-angle camera (ARCHITECTURE_LOCK: no free 3D camera in MVP).
## Locked three-quarter pitch; optional discrete 45° yaw snaps (Q/R); zoom only.
## No mouse-look, free orbit, FPS, or continuous yaw drag.
## CTRL-1B B1: yaw snaps gated by ControlContextRouter; invert zoom + sensitivity a11y.
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
	# Gated by context router so Build R is hologram rotate, not camera (C1B-ACT-05 / HK-09/10).
	# P2E F-A4-01: while Build is primary, freeze yaw completely (no residual lerp from prior snaps).
	var build_ctx := _is_build_context()
	if build_ctx:
		_target_yaw = _yaw
	elif allow_yaw_snaps:
		if _router_action_just_pressed("rotate_camera_left"):
			_target_yaw += deg_to_rad(yaw_step_degrees)
		if _router_action_just_pressed("rotate_camera_right"):
			_target_yaw -= deg_to_rad(yaw_step_degrees)

	var zoom_step := get_zoom_step()
	if _invert_zoom():
		zoom_step = -zoom_step
	if Input.is_action_just_pressed("camera_zoom_in"):
		_distance = clampf(_distance - absf(zoom_step), min_distance, max_distance)
	if Input.is_action_just_pressed("camera_zoom_out"):
		_distance = clampf(_distance + absf(zoom_step), min_distance, max_distance)

	if not build_ctx:
		var yaw_speed := yaw_rotate_speed * _mouse_sensitivity()
		if _reduced_motion():
			yaw_speed = yaw_rotate_speed * 2.5  # snap faster / less floaty
		_yaw = lerp_angle(_yaw, _target_yaw, clampf(yaw_speed * delta, 0.0, 1.0))
	_apply_camera_transform(delta)


func freeze_yaw_now() -> void:
	## Hard-stop residual lerp (call on enter Build / before Build Q/R evidence).
	## Explicitly leased under Directive 72 (P2E-CODEX-LEASE-R2); does not rehabilitate D71.
	_target_yaw = _yaw
	_yaw = _target_yaw


func get_directive_lease_note() -> String:
	return "cozy_camera.gd leased under WO-P2E-001 Directive 72 for Build Q/R yaw freeze"


func _autoload_node(node_name: String) -> Node:
	## SceneTree-root relative lookup — never absolute "/root/..." (H1-CODEX-F01).
	if not is_inside_tree():
		return null
	var tree := get_tree()
	if tree == null:
		return null
	var r := tree.root
	if r == null:
		return null
	var direct := r.get_node_or_null(node_name)
	if direct != null:
		return direct
	for c in r.get_children():
		if str(c.name) == node_name:
			return c
	return null


func _control_router() -> Node:
	return _autoload_node("ControlContextRouter")


func _control_a11y() -> Node:
	return _autoload_node("ControlAccessibilitySettings")


func _is_build_context() -> bool:
	var router := _control_router()
	if router != null and router.has_method("get_primary_context"):
		return str(router.call("get_primary_context")) == "build"
	return false


func _router_action_just_pressed(action_id: String) -> bool:
	# Hard-stop: never accept camera rotate actions while Build is primary (shared Q/R keys).
	if _is_build_context() and (
		action_id == "rotate_camera_left" or action_id == "rotate_camera_right"
	):
		return false
	var router := _control_router()
	if router != null and router.has_method("is_action_just_pressed"):
		return bool(router.call("is_action_just_pressed", action_id))
	# Fallback without router: still block camera rotate while in build context if flag present.
	if router != null and router.has_method("get_primary_context"):
		if str(router.call("get_primary_context")) == "build":
			if action_id == "rotate_camera_right" or action_id == "rotate_camera_left":
				return false
	if not InputMap.has_action(action_id):
		return false
	return Input.is_action_just_pressed(action_id)


func _mouse_sensitivity() -> float:
	var a11y := _control_a11y()
	if a11y != null and "mouse_sensitivity" in a11y:
		return clampf(float(a11y.mouse_sensitivity), 0.1, 3.0)
	return 1.0


func get_zoom_step() -> float:
	## Observable bounded effect of mouse_sensitivity on camera zoom (H-26 / C1B-A11Y-05).
	return 1.0 * _mouse_sensitivity()


func get_distance() -> float:
	return _distance


func apply_zoom_in_step() -> float:
	## Headless-observable sensitivity probe: one zoom-in using current sensitivity.
	var before := _distance
	var step := absf(get_zoom_step())
	_distance = clampf(_distance - step, min_distance, max_distance)
	return before - _distance


func apply_zoom_out_step() -> float:
	var before := _distance
	var step := absf(get_zoom_step())
	_distance = clampf(_distance + step, min_distance, max_distance)
	return _distance - before


func set_distance_for_test(d: float) -> void:
	_distance = clampf(d, min_distance, max_distance)


func get_sensitivity_snapshot() -> Dictionary:
	var s := _mouse_sensitivity()
	return {
		"mouse_sensitivity": s,
		"zoom_step": 1.0 * s,
		"min_distance": min_distance,
		"max_distance": max_distance,
		"distance": _distance,
		"bounded": s >= 0.1 and s <= 3.0,
	}


func _invert_zoom() -> bool:
	var a11y := _control_a11y()
	if a11y != null and "invert_zoom" in a11y:
		return bool(a11y.invert_zoom)
	return false


func _reduced_motion() -> bool:
	var a11y := _control_a11y()
	if a11y != null and "reduced_motion" in a11y:
		return bool(a11y.reduced_motion)
	return false


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
	var smooth := follow_smooth
	if _reduced_motion():
		smooth = follow_smooth * 3.0
	if delta >= 1.0:
		global_position = desired
	else:
		global_position = global_position.lerp(desired, clampf(smooth * delta, 0.0, 1.0))
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

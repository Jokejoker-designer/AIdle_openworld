## Cozy 2.5D player controller (MVP shell).
## CharacterBody3D on ground plane; camera-relative XZ locomotion; soft gravity.
## Not free-fly / FPS / combat-twitch.
## CTRL-1B B1: context-aware locomotion suppress; sprint hold/toggle from a11y.
class_name PlayerController
extends CharacterBody3D

@export var walk_speed: float = 4.2
@export var sprint_speed: float = 6.8
@export var acceleration: float = 18.0
@export var friction: float = 22.0
@export var jump_velocity: float = 5.5
@export var rotation_speed: float = 12.0
## Optional short hop; still constrained to ground plane locomotion.
@export var allow_jump: bool = true

## Optional external camera rig (CozyCamera). If null, uses sibling/group.
@export var camera_rig_path: NodePath

var _camera_rig: Node3D
var _gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity")
var _locomotion_suppressed: bool = false
var _sprint_toggled_on: bool = false


func _ready() -> void:
	add_to_group("player")
	# Stay on layered world collision (layer 1); player is layer 2.
	if camera_rig_path != NodePath(""):
		_camera_rig = get_node_or_null(camera_rig_path) as Node3D
	if _camera_rig == null:
		_camera_rig = get_tree().get_first_node_in_group("cozy_camera") as Node3D
	# Presentation-only capsule mesh: clear under headless/dummy to avoid dummy ERROR.
	# Locomotion / collision capsule stay intact.
	_disable_presentation_mesh_if_headless()


func _disable_presentation_mesh_if_headless() -> void:
	var headless := false
	if AIdleConstants != null and AIdleConstants.has_method("is_headless_or_dummy_presentation"):
		headless = bool(AIdleConstants.is_headless_or_dummy_presentation())
	else:
		headless = OS.has_feature("headless") or DisplayServer.get_name() == "headless"
	if not headless:
		return
	var visual := get_node_or_null("MeshInstance3D") as MeshInstance3D
	if visual != null:
		visual.mesh = null
		visual.material_override = null
		visual.visible = false


func set_camera_rig(rig: Node3D) -> void:
	_camera_rig = rig
	if rig:
		camera_rig_path = get_path_to(rig)


func set_locomotion_suppressed(suppressed: bool) -> void:
	## Companion composer / modal focus — no silent multi-context fire (C1B-CTX / CF-04).
	_locomotion_suppressed = suppressed
	if suppressed:
		velocity.x = 0.0
		velocity.z = 0.0


func is_locomotion_suppressed() -> bool:
	return _locomotion_suppressed


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= _gravity * delta

	# Suppress world movement while composer owns focus.
	if _locomotion_suppressed or _should_suppress_from_router():
		velocity.x = move_toward(velocity.x, 0.0, friction * delta)
		velocity.z = move_toward(velocity.z, 0.0, friction * delta)
		move_and_slide()
		return

	var input_dir := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var direction := _camera_relative_direction(input_dir)

	var target_speed := walk_speed
	if _is_sprinting():
		target_speed = sprint_speed

	if direction.length_squared() > 0.001:
		var target_vel := direction * target_speed
		# XZ only — 2.5D ground plane navigation (no free 3D flight).
		velocity.x = move_toward(velocity.x, target_vel.x, acceleration * delta)
		velocity.z = move_toward(velocity.z, target_vel.z, acceleration * delta)
		_face_direction(direction, delta)
	else:
		velocity.x = move_toward(velocity.x, 0.0, friction * delta)
		velocity.z = move_toward(velocity.z, 0.0, friction * delta)

	# Dedicated gameplay jump — never ui_accept (Space/Enter also activate UI focus).
	if allow_jump and Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = jump_velocity

	move_and_slide()


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


func _should_suppress_from_router() -> bool:
	var router := _control_router()
	if router == null:
		return false
	if not router.has_method("get_primary_context"):
		return false
	var ctx := str(router.call("get_primary_context"))
	if ctx != "companion":
		return false
	if router.has_method("get_cancel_targets"):
		var t: Dictionary = router.call("get_cancel_targets") as Dictionary
		return bool(t.get("prompt_composer_or_dialogue", false))
	return true


func _is_sprinting() -> bool:
	var mode := "hold"
	var a11y := _control_a11y()
	if a11y != null and "sprint_mode" in a11y:
		mode = str(a11y.sprint_mode)
	if mode == "toggle":
		if Input.is_action_just_pressed("sprint"):
			_sprint_toggled_on = not _sprint_toggled_on
		return _sprint_toggled_on
	_sprint_toggled_on = false
	return Input.is_action_pressed("sprint")


func _camera_relative_direction(input_dir: Vector2) -> Vector3:
	var basis_yaw := 0.0
	if _camera_rig and _camera_rig.has_method("get_yaw"):
		basis_yaw = float(_camera_rig.call("get_yaw"))
	elif _camera_rig:
		basis_yaw = _camera_rig.rotation.y
	# input: x = strafe, y = forward (negative in get_vector for W)
	var forward := Vector3(-sin(basis_yaw), 0.0, -cos(basis_yaw))
	var right := Vector3(cos(basis_yaw), 0.0, -sin(basis_yaw))
	var dir := (right * input_dir.x + forward * -input_dir.y)
	dir.y = 0.0
	if dir.length_squared() > 1.0:
		dir = dir.normalized()
	return dir


func _face_direction(direction: Vector3, delta: float) -> void:
	if direction.length_squared() < 0.0001:
		return
	var target_yaw := atan2(direction.x, direction.z)
	rotation.y = lerp_angle(rotation.y, target_yaw, clampf(rotation_speed * delta, 0.0, 1.0))


func get_interaction_origin() -> Vector3:
	return global_position + Vector3.UP * 1.2

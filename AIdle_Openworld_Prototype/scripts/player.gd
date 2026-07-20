extends CharacterBody2D
class_name Player

@export var speed: float = 200.0

@onready var sprite: ColorRect = $ColorRect
@onready var label: Label = $Label

var can_move: bool = true

func _ready():
	label.text = "You"

func _physics_process(_delta):
	if not can_move:
		velocity = Vector2.ZERO
		move_and_slide()
		return

	var direction = Vector2.ZERO
	
	if Input.is_action_pressed("move_left") or Input.is_action_pressed("ui_left"):
		direction.x -= 1
	if Input.is_action_pressed("move_right") or Input.is_action_pressed("ui_right"):
		direction.x += 1
	if Input.is_action_pressed("move_up") or Input.is_action_pressed("ui_up"):
		direction.y -= 1
	if Input.is_action_pressed("move_down") or Input.is_action_pressed("ui_down"):
		direction.y += 1

	direction = direction.normalized()
	velocity = direction * speed
	move_and_slide()

func set_movement_enabled(enabled: bool):
	can_move = enabled

extends Node2D
class_name BuildingSystem

signal progress_changed(value: float)
signal build_finished

enum State { IDLE, WIREFRAME, HOLOGRAM, MATERIALIZING, COMPLETE }

var current_state: State = State.IDLE
var progress: float = 0.0
var duration: float = 9.0  # seconds

@onready var wireframe: ColorRect = $Wireframe
@onready var hologram: ColorRect = $Hologram
@onready var solid: ColorRect = $Solid
@onready var label: Label = $Label

func _ready():
	_reset_visuals()
	label.text = ""

func start_build(building_type: String = "small_cozy_house"):
	if current_state != State.IDLE and current_state != State.COMPLETE:
		return
	
	print("Starting progressive manifestation: ", building_type)
	current_state = State.WIREFRAME
	progress = 0.0
	set_process(true)
	_update_visuals()
	label.text = "Manifesting..."

func _process(delta):
	if current_state == State.IDLE or current_state == State.COMPLETE:
		return
	
	progress += delta / duration
	progress = clampf(progress, 0.0, 1.0)
	progress_changed.emit(progress)
	
	if progress < 0.28:
		current_state = State.WIREFRAME
	elif progress < 0.58:
		current_state = State.HOLOGRAM
	elif progress < 1.0:
		current_state = State.MATERIALIZING
	else:
		current_state = State.COMPLETE
		set_process(false)
		label.text = "Hoàn thành!"
		build_finished.emit()
	
	_update_visuals()

func _update_visuals():
	wireframe.visible = current_state in [State.WIREFRAME, State.HOLOGRAM]
	hologram.visible = current_state in [State.HOLOGRAM, State.MATERIALIZING]
	solid.visible = current_state in [State.MATERIALIZING, State.COMPLETE]
	
	# Progressive opacity for solid
	if solid.visible:
		var alpha = clampf((progress - 0.55) / 0.45, 0.0, 1.0)
		solid.color.a = alpha
	else:
		solid.color.a = 0.0
	
	# Hologram pulse
	if hologram.visible:
		hologram.color.a = 0.35 + sin(Time.get_ticks_msec() * 0.008) * 0.1

func _reset_visuals():
	wireframe.visible = false
	hologram.visible = false
	solid.visible = false
	solid.color.a = 0.0
	label.text = ""
	current_state = State.IDLE
	progress = 0.0

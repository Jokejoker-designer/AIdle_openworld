## Spawns ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01 into the live Godot world.
## Presentation landmark only — no World Commit. Loads GLB via GlbIntake.
extends Node3D

const _GlbIntake = preload("res://scripts/modules/asset/glb_intake.gd")

const MODULE_ID := "royal_lightkeep_watchtower_barracks_01"
const GLB_RES := "res://assets/p1e_cozy/modules/royal_lightkeep_watchtower_barracks_01.glb"
## World placement: offset from origin so it does not collide with town cadastre (±12).
const DEFAULT_POSITION := Vector3(-36.0, 0.0, 28.0)
const DEFAULT_YAW_DEG := 25.0

var _instance: Node3D = null
var _last_report: Dictionary = {}


func get_report() -> Dictionary:
	return _last_report.duplicate(true)


func get_instance() -> Node3D:
	return _instance


## Load GLB and parent under this node. Returns report dict.
func spawn_landmark(
	world_pos: Vector3 = DEFAULT_POSITION,
	yaw_deg: float = DEFAULT_YAW_DEG
) -> Dictionary:
	_clear()
	var abs_path := ProjectSettings.globalize_path(GLB_RES)
	if not FileAccess.file_exists(abs_path):
		_last_report = {
			"ok": false,
			"error": "glb_missing",
			"path": GLB_RES,
			"abs": abs_path,
			"module_id": MODULE_ID,
		}
		return _last_report

	var intake: RefCounted = _GlbIntake.new()
	var node: Node3D = intake.call("load_glb_absolute", abs_path, MODULE_ID) as Node3D
	if node == null:
		_last_report = {
			"ok": false,
			"error": "intake_failed",
			"detail": str(intake.get("last_error")),
			"module_id": MODULE_ID,
		}
		return _last_report

	node.name = MODULE_ID
	add_child(node)
	# Local pose (Main / smoke root at world origin → world-aligned placement).
	position = world_pos
	rotation_degrees = Vector3(0.0, yaw_deg, 0.0)
	_instance = node

	var mesh_n := 0
	if node.has_meta("mesh_count"):
		mesh_n = int(node.get_meta("mesh_count"))

	_last_report = {
		"ok": true,
		"module_id": MODULE_ID,
		"glb": GLB_RES,
		"position": {"x": world_pos.x, "y": world_pos.y, "z": world_pos.z},
		"yaw_deg": yaw_deg,
		"mesh_count": mesh_n,
		"materials_resolve": node.get_meta("materials_resolve") if node.has_meta("materials_resolve") else {},
		"runtime_load": "OK",
	}
	return _last_report


func _clear() -> void:
	if _instance != null and is_instance_valid(_instance):
		_instance.queue_free()
	_instance = null
	for c in get_children():
		c.queue_free()

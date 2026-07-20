## Single progressive 2.5D manifestation entity.
## Wireframe → hologram → materializing: visual only (no collision).
## Complete: local solid collision enabled on LAYER_MANIFESTATION.
## Cancel: caller must free this node; free_cleanup disables collision first.
class_name ManifestationInstance
extends Node3D

const META_PREVIEW := "manifestation_preview"
const META_PROMPT_ID := "prompt_id"
const META_STAGE := "manifestation_stage"
const _Stages = preload("res://scripts/modules/manifestation/manifestation_stages.gd")

## physics layer 3 (manifestation) → bit value 1 << 2
const COLLISION_LAYER_MANIFESTATION := 4

var prompt_id: String = ""
var art_style: String = ""
var target_space: String = "private_reality"
var provenance: Dictionary = {}
var entity_size: Vector3 = Vector3(2.0, 2.0, 2.0)

var _stage: String = "wireframe"
var _progress: float = 0.0
var _mesh_instance: MeshInstance3D
var _static_body: StaticBody3D
var _collision_shape: CollisionShape3D
var _material: StandardMaterial3D
var _finalized: bool = false
var _cancelled: bool = false
## When true, skip Mesh/Material (presentation-only) under headless/dummy renderer.
var _presentation_enabled: bool = true


func _ready() -> void:
	set_meta(META_PREVIEW, true)
	set_meta(META_PROMPT_ID, prompt_id)
	set_meta(META_STAGE, _stage)
	_build_visuals_if_needed()
	_apply_stage_visuals()
	_set_collision_enabled(false)


func configure(
	p_prompt_id: String,
	p_art_style: String,
	geometry: Dictionary
) -> void:
	prompt_id = p_prompt_id
	art_style = p_art_style
	target_space = str(geometry.get("target_space", "private_reality"))
	if geometry.get("provenance", {}) is Dictionary:
		provenance = (geometry.get("provenance", {}) as Dictionary).duplicate(true)
	else:
		provenance = {}
	entity_size = _parse_size(geometry.get("size", geometry.get("bounds", null)))
	# Use local position — safe before entering the scene tree.
	position = _parse_vec3(geometry.get("position", Vector3.ZERO))
	_build_visuals_if_needed()
	set_meta(META_PROMPT_ID, prompt_id)
	_apply_stage_visuals()
	_set_collision_enabled(false)


func get_stage() -> String:
	return _stage


func get_progress() -> float:
	return _progress


func is_cancelled() -> bool:
	return _cancelled


func is_finalized() -> bool:
	return _finalized


func has_durable_collision() -> bool:
	if _cancelled or not is_instance_valid(_collision_shape):
		return false
	if not _Stages.allows_durable_collision(_stage):
		return false
	return not _collision_shape.disabled and _static_body != null and _static_body.collision_layer != 0


func set_stage(stage: String) -> bool:
	if _cancelled or _finalized:
		return false
	var next: String = _Stages.enforce_monotonic(_stage, stage)
	if next == _stage and _Stages.is_valid_stage(stage) and stage != _stage:
		return false
	_stage = next
	_progress = maxf(_progress, _Stages.progress_for_stage(_stage))
	set_meta(META_STAGE, _stage)
	set_meta(META_PREVIEW, not _Stages.allows_durable_collision(_stage))
	_apply_stage_visuals()
	_set_collision_enabled(_Stages.allows_durable_collision(_stage))
	return true


func set_progress(progress: float) -> void:
	if _cancelled or _finalized:
		return
	_progress = clampf(progress, 0.0, 1.0)
	var stage: String = _Stages.stage_for_progress(_progress)
	set_stage(stage)


func finalize_complete() -> void:
	if _cancelled:
		return
	_stage = "complete"
	_progress = 1.0
	_finalized = true
	set_meta(META_STAGE, _stage)
	set_meta(META_PREVIEW, false)
	_apply_stage_visuals()
	_set_collision_enabled(true)


func mark_cancelled() -> void:
	_cancelled = true
	_finalized = false
	_set_collision_enabled(false)
	set_meta(META_PREVIEW, true)


func free_cleanup() -> void:
	mark_cancelled()
	if is_instance_valid(_static_body):
		_static_body.collision_layer = 0
		_static_body.collision_mask = 0
	if is_instance_valid(_collision_shape):
		_collision_shape.disabled = true
	queue_free()


func _presentation_allowed() -> bool:
	# Prefer autoload when available; fall back to DisplayServer for pure -s smoke.
	if AIdleConstants != null and AIdleConstants.has_method("is_headless_or_dummy_presentation"):
		return not bool(AIdleConstants.is_headless_or_dummy_presentation())
	if OS.has_feature("headless"):
		return false
	return DisplayServer.get_name() != "headless"


func _build_visuals_if_needed() -> void:
	_presentation_enabled = _presentation_allowed()

	# Collision body is always built (logic + cancel/preview tests). Mesh is presentation-only.
	if _static_body == null:
		_static_body = StaticBody3D.new()
		_static_body.name = "CollisionBody"
		_static_body.collision_layer = 0
		_static_body.collision_mask = 0
		add_child(_static_body)

		_collision_shape = CollisionShape3D.new()
		_collision_shape.name = "Shape"
		var shape := BoxShape3D.new()
		shape.size = entity_size
		_collision_shape.shape = shape
		_collision_shape.position = Vector3(0.0, entity_size.y * 0.5, 0.0)
		_collision_shape.disabled = true
		_static_body.add_child(_collision_shape)
	else:
		_update_mesh_size()

	if not _presentation_enabled:
		# Headless/dummy: do not construct BoxMesh / StandardMaterial3D (avoids dummy ERROR: m is null).
		# Stage ordering, cancel, reduced-motion, and collision gating still run.
		return

	if _mesh_instance != null:
		_update_mesh_size()
		return

	_mesh_instance = MeshInstance3D.new()
	_mesh_instance.name = "Visual"
	var box := BoxMesh.new()
	box.size = entity_size
	_mesh_instance.mesh = box
	_mesh_instance.position = Vector3(0.0, entity_size.y * 0.5, 0.0)

	_material = StandardMaterial3D.new()
	_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_material.cull_mode = BaseMaterial3D.CULL_DISABLED
	_material.albedo_color = Color(0.45, 0.85, 1.0, 0.22)
	_material.emission_enabled = true
	_material.emission = Color(0.35, 0.75, 1.0)
	_mesh_instance.material_override = _material
	add_child(_mesh_instance)


func _update_mesh_size() -> void:
	if _presentation_enabled and _mesh_instance and _mesh_instance.mesh is BoxMesh:
		(_mesh_instance.mesh as BoxMesh).size = entity_size
		_mesh_instance.position = Vector3(0.0, entity_size.y * 0.5, 0.0)
	if _collision_shape and _collision_shape.shape is BoxShape3D:
		(_collision_shape.shape as BoxShape3D).size = entity_size
		_collision_shape.position = Vector3(0.0, entity_size.y * 0.5, 0.0)


func _apply_stage_visuals() -> void:
	# Stage state always updates via set_stage / meta; material tint is presentation-only.
	if not _presentation_enabled or _material == null:
		return
	var opacity: float = _Stages.visual_opacity(_stage)
	var emission_e: float = _Stages.visual_emission_energy(_stage)
	var base := _style_tint()
	match _stage:
		"wireframe":
			_material.albedo_color = Color(base.r, base.g, base.b, opacity)
			_material.emission = base
			_material.emission_energy_multiplier = emission_e
		"hologram":
			_material.albedo_color = Color(base.r, base.g, base.b, opacity)
			_material.emission = base.lightened(0.15)
			_material.emission_energy_multiplier = emission_e
		"materializing":
			_material.albedo_color = Color(base.r * 0.9, base.g * 0.85, base.b * 0.75, opacity)
			_material.emission = base.darkened(0.2)
			_material.emission_energy_multiplier = emission_e
		"complete":
			_material.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED
			_material.albedo_color = Color(base.r * 0.85, base.g * 0.75, base.b * 0.65, 1.0)
			_material.emission_enabled = false
			_material.emission_energy_multiplier = 0.0
			_material.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL
		_:
			pass
	if _stage != "complete":
		_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		_material.emission_enabled = true
		_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED


func _style_tint() -> Color:
	match art_style:
		"cyberpunk_dense":
			return Color(0.35, 0.95, 1.0)
		"pastoral_fantasy":
			return Color(0.55, 0.9, 0.55)
		"surrealism_canvas":
			return Color(0.85, 0.55, 0.95)
		_:
			return Color(0.45, 0.85, 1.0)


func _set_collision_enabled(enabled: bool) -> void:
	if not is_instance_valid(_static_body) or not is_instance_valid(_collision_shape):
		return
	if enabled and _Stages.allows_durable_collision(_stage) and not _cancelled:
		_collision_shape.disabled = false
		_static_body.collision_layer = COLLISION_LAYER_MANIFESTATION
		_static_body.collision_mask = 0
	else:
		_collision_shape.disabled = true
		_static_body.collision_layer = 0
		_static_body.collision_mask = 0


func _parse_size(raw: Variant) -> Vector3:
	var v := _parse_vec3(raw)
	if v == Vector3.ZERO:
		return Vector3(2.0, 2.0, 2.0)
	return Vector3(maxf(v.x, 0.25), maxf(v.y, 0.25), maxf(v.z, 0.25))


func _parse_vec3(raw: Variant) -> Vector3:
	if raw is Vector3:
		return raw
	if raw is Dictionary:
		var d: Dictionary = raw
		return Vector3(
			float(d.get("x", d.get("width", 0.0))),
			float(d.get("y", d.get("height", 0.0))),
			float(d.get("z", d.get("depth", 0.0)))
		)
	if raw is Array and raw.size() >= 3:
		return Vector3(float(raw[0]), float(raw[1]), float(raw[2]))
	return Vector3.ZERO

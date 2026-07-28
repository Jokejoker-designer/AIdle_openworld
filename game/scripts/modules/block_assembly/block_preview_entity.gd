## Non-durable Block Assembly preview presentation.
## Stages wireframe→hologram→materializing→complete visual only.
## Collision/navigation stay disabled until post-commit authority enable.
## U5: prefers UCBV-001 kit mesh descriptors when module is in the ten-module family.
class_name BlockPreviewEntity
extends Node3D

const _C = preload("res://scripts/modules/block_assembly/block_assembly_constants.gd")
const _Stages = preload("res://scripts/modules/manifestation/manifestation_stages.gd")
const _UcbvKit = preload("res://scripts/modules/ucbv_001/ucbv_block_kit_loader.gd")

var module_id: String = ""
var request_id: String = ""
var prompt_id: String = ""
var material_slot: String = "structure"
var p1e_material_id: String = "MAT_CozyStoneWarm"

var _stage: String = "wireframe"
var _cancelled: bool = false
var _committed: bool = false
var _collision_enabled: bool = false
var _nav_enabled: bool = false
var _mesh: MeshInstance3D
var _body: StaticBody3D
var _shape: CollisionShape3D
var _mat: StandardMaterial3D
var _stages_observed: PackedStringArray = PackedStringArray()
var _presentation: bool = true
var _placement_valid: bool = true
var _ucbv_root: Node3D = null
var _ucbv_kit: RefCounted = null
var _uses_ucbv_kit: bool = false


func _ready() -> void:
	add_to_group(_C.PREVIEW_GROUP)
	add_to_group("manifestation_instances")
	set_meta("manifestation_preview", true)
	set_meta("preview_owns_ownership", false)
	set_meta("preview_owns_collision", false)
	set_meta("durable_mutation_applied", false)
	set_meta("client_world_commit", false)
	set_meta("block_assembly_preview", true)
	# Headless / dummy renderer: skip MeshInstance (avoids mesh_get_surface_count ERROR noise).
	_presentation = str(DisplayServer.get_name()) != "headless"
	_record_stage(_stage)
	_build_visuals()
	_apply_stage_visuals()
	_set_collision(false)
	_set_nav(false)


func configure(
	p_module_id: String,
	p_request_id: String,
	p_prompt_id: String,
	placement: Dictionary
) -> void:
	module_id = p_module_id
	request_id = p_request_id
	prompt_id = p_prompt_id
	position = Vector3(
		float(placement.get("x", 0.0)),
		float(placement.get("elevation", 0.0)),
		float(placement.get("y", 0.0))
	)
	rotation_degrees.y = float(placement.get("rotation_deg", 0.0))
	set_meta("prompt_id", prompt_id)
	set_meta("module_id", module_id)
	# Always ensure body + UCBV kit after module is known (works pre/post enter-tree).
	if _body == null:
		_build_visuals()
	_try_rebuild_ucbv_visual()


func get_stage() -> String:
	return _stage


func get_stages_observed() -> PackedStringArray:
	return _stages_observed.duplicate()


func is_cancelled() -> bool:
	return _cancelled


func is_committed() -> bool:
	return _committed


func has_collision() -> bool:
	return _collision_enabled and not _cancelled


func has_navigation() -> bool:
	return _nav_enabled and not _cancelled


func is_finalized() -> bool:
	return _committed


func set_stage(stage: String) -> bool:
	if _cancelled or _committed:
		return false
	if not _Stages.is_valid_stage(stage):
		return false
	var next := _Stages.enforce_monotonic(_stage, stage)
	if next != stage and stage != _stage:
		return false
	_stage = next
	_record_stage(_stage)
	set_meta("manifestation_stage", _stage)
	set_meta("manifestation_preview", not _Stages.allows_durable_collision(_stage))
	_apply_stage_visuals()
	# Preview never enables collision/nav before authority receipt.
	_set_collision(false)
	_set_nav(false)
	return true


func rotate_preview(degrees: float) -> void:
	if _cancelled or _committed:
		return
	rotation_degrees.y = fposmod(rotation_degrees.y + degrees, 360.0)


func apply_placement(placement: Dictionary) -> void:
	if _cancelled or _committed:
		return
	position = Vector3(
		float(placement.get("x", position.x)),
		float(placement.get("elevation", position.y)),
		float(placement.get("y", position.z))
	)
	if placement.has("rotation_deg"):
		rotation_degrees.y = float(placement["rotation_deg"])


func set_validity_visual(valid: bool) -> void:
	## Cursor-led Manual Build feedback: greenish-valid / warm-invalid hologram (preview only).
	_placement_valid = valid
	_apply_stage_visuals()


func is_placement_valid() -> bool:
	return _placement_valid


func mark_cancelled() -> void:
	_cancelled = true
	_set_collision(false)
	_set_nav(false)
	set_meta("manifestation_preview", true)
	set_meta("durable_mutation_applied", false)
	visible = false


func enable_post_commit_physics() -> void:
	## Only after successful authority receipt.
	if _cancelled:
		return
	_committed = true
	_stage = "complete"
	_record_stage("complete")
	set_meta("manifestation_preview", false)
	set_meta("preview_owns_collision", true)
	set_meta("durable_mutation_applied", true)
	set_meta("client_world_commit", false)
	remove_from_group(_C.PREVIEW_GROUP)
	add_to_group(_C.COMMITTED_GROUP)
	_apply_stage_visuals()
	_set_collision(true)
	_set_nav(true)


func free_cleanup() -> void:
	mark_cancelled()
	_dispose_visuals()
	# queue_free only — never free() while signals/call stack may hold the node (SCRIPT ERROR).
	if is_inside_tree():
		queue_free()


func _exit_tree() -> void:
	_dispose_visuals()


func _dispose_visuals() -> void:
	## F02-R2: drop mesh/material/collision RID ownership before renderer teardown.
	## Detach resources immediately; queue_free nodes so RenderingServer still exists.
	if _ucbv_root != null and is_instance_valid(_ucbv_root):
		if _ucbv_root.get_parent() == self:
			remove_child(_ucbv_root)
		_ucbv_root.queue_free()
	_ucbv_root = null
	_uses_ucbv_kit = false
	if _mesh != null and is_instance_valid(_mesh):
		_mesh.material_override = null
		_mesh.mesh = null
		_mesh.visible = false
		if _mesh.get_parent() == self:
			remove_child(_mesh)
		_mesh.queue_free()
	_mesh = null
	_mat = null
	if _body != null and is_instance_valid(_body):
		_body.collision_layer = 0
		_body.collision_mask = 0
		if _shape != null and is_instance_valid(_shape):
			_shape.disabled = true
			_shape.shape = null
		if _body.get_parent() == self:
			remove_child(_body)
		_body.queue_free()
	_body = null
	_shape = null


func _ensure_kit() -> RefCounted:
	if _ucbv_kit == null:
		_ucbv_kit = _UcbvKit.new()
		if _ucbv_kit.has_method("ensure_loaded"):
			_ucbv_kit.call("ensure_loaded")
	return _ucbv_kit


func _try_rebuild_ucbv_visual() -> void:
	if module_id.is_empty():
		return
	var kit := _ensure_kit()
	if kit == null or not bool(kit.call("has_module", module_id)):
		return
	# Remove legacy single box if present.
	if _mesh != null and is_instance_valid(_mesh):
		_mesh.material_override = null
		_mesh.mesh = null
		if _mesh.get_parent() == self:
			remove_child(_mesh)
		_mesh.queue_free()
		_mesh = null
		_mat = null
	if _ucbv_root != null and is_instance_valid(_ucbv_root):
		if _ucbv_root.get_parent() == self:
			remove_child(_ucbv_root)
		_ucbv_root.queue_free()
		_ucbv_root = null
	# Headless/dummy: never spawn MeshInstance surfaces (avoids mesh_get_surface_count ERROR).
	var want_presentation := _presentation and _Paths_is_safe_presentation()
	_ucbv_root = kit.call(
		"build_module_visual", module_id, _stage, _placement_valid, want_presentation
	) as Node3D
	if _ucbv_root != null:
		add_child(_ucbv_root)
		_uses_ucbv_kit = true
		set_meta("ucbv_kit_visual", true)
		set_meta("ucbv_module_id", module_id)
		var size: Vector3 = kit.call("get_overall_size", module_id) as Vector3
		if _shape != null and _shape.shape is BoxShape3D:
			(_shape.shape as BoxShape3D).size = Vector3(
				maxf(size.x, 0.2), maxf(size.y, 0.2), maxf(size.z, 0.2)
			)
			if _body != null:
				_body.position.y = size.y * 0.5


func _Paths_is_safe_presentation() -> bool:
	if OS.has_feature("headless"):
		return false
	var ds := str(DisplayServer.get_name())
	if ds == "headless" or ds == "dummy":
		return false
	return true


func _build_visuals() -> void:
	if _body != null:
		return
	# Collision/nav bookkeeping body always available (disabled until post-commit).
	_body = StaticBody3D.new()
	_body.collision_layer = 0
	_body.collision_mask = 0
	_shape = CollisionShape3D.new()
	var cs := BoxShape3D.new()
	cs.size = Vector3(1.0, 1.0, 1.0)
	_shape.shape = cs
	_shape.disabled = true
	_body.add_child(_shape)
	add_child(_body)
	# U5 kit path when module known and allowlisted in U3 family.
	if not module_id.is_empty():
		var kit := _ensure_kit()
		if kit != null and bool(kit.call("has_module", module_id)):
			_try_rebuild_ucbv_visual()
			return
	if not _presentation:
		return
	if _mesh != null:
		return
	_mesh = MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(1.0, 1.0, 1.0)
	_mesh.mesh = box
	_mat = StandardMaterial3D.new()
	_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_mesh.material_override = _mat
	add_child(_mesh)


func _apply_stage_visuals() -> void:
	if _uses_ucbv_kit and _ucbv_root != null and is_instance_valid(_ucbv_root):
		var kit := _ensure_kit()
		if kit != null and kit.has_method("apply_stage_to_visual"):
			kit.call("apply_stage_to_visual", _ucbv_root, _stage, _placement_valid)
		return
	if _mat == null:
		return
	var base := Color(0.4, 0.85, 1.0) if _placement_valid else Color(0.95, 0.35, 0.28)
	var emit := Color(0.3, 0.7, 1.0) if _placement_valid else Color(0.95, 0.25, 0.2)
	_mat.albedo_color = Color(base.r, base.g, base.b, _Stages.visual_opacity(_stage))
	_mat.emission_enabled = _Stages.visual_emission_energy(_stage) > 0.01
	_mat.emission = emit
	_mat.emission_energy_multiplier = _Stages.visual_emission_energy(_stage)


func _set_collision(enabled: bool) -> void:
	_collision_enabled = enabled
	if _shape != null:
		_shape.disabled = not enabled
	if _body != null:
		_body.collision_layer = 4 if enabled else 0
		_body.collision_mask = 0


func _set_nav(enabled: bool) -> void:
	_nav_enabled = enabled
	set_meta("navigation_enabled", enabled)


func _record_stage(stage: String) -> void:
	if stage in _stages_observed:
		return
	_stages_observed.append(stage)

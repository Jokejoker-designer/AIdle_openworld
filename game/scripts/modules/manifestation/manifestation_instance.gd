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
var recipe_id: String = ""

var _stage: String = "wireframe"
var _progress: float = 0.0
var _mesh_instance: MeshInstance3D
var _static_body: StaticBody3D
var _collision_shape: CollisionShape3D
var _material: StandardMaterial3D
var _finalized: bool = false
var _cancelled: bool = false
## Ordered stages entered this attempt (for G3 complete/cancel receipts).
var _stages_observed: PackedStringArray = PackedStringArray()
## When true, skip Mesh/Material (presentation-only) under headless/dummy renderer.
var _presentation_enabled: bool = true
## Optional runtime-loaded GLB (or other) visual; preview stages stay non-solid.
var _external_visual: Node3D = null


func _ready() -> void:
	add_to_group("manifestation_instances")
	set_meta(META_PREVIEW, true)
	set_meta(META_PROMPT_ID, prompt_id)
	set_meta(META_STAGE, _stage)
	# Explicit non-authority flags for preview (C1B-SAFE-04).
	set_meta("preview_owns_ownership", false)
	set_meta("preview_owns_collision", false)
	set_meta("durable_mutation_applied", false)
	_record_stage(_stage)
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
	recipe_id = str(geometry.get("recipe_id", ""))
	if geometry.get("provenance", {}) is Dictionary:
		provenance = (geometry.get("provenance", {}) as Dictionary).duplicate(true)
	else:
		provenance = {}
	entity_size = _parse_size(geometry.get("size", geometry.get("bounds", null)))
	# Use local position — safe before entering the scene tree.
	# Accept Godot Vector3 position OR World Prompt 2.5D transform {x,y,elevation}.
	position = _position_from_geometry(geometry)
	_build_visuals_if_needed()
	set_meta(META_PROMPT_ID, prompt_id)
	_apply_stage_visuals()
	_set_collision_enabled(false)


func get_stage() -> String:
	return _stage


func get_progress() -> float:
	return _progress


func get_stages_observed() -> PackedStringArray:
	return _stages_observed.duplicate()


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
	_record_stage(_stage)
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
	# Ordered stage history for complete path (monotonic wireframe→…→complete).
	# Rebuild so jump-to-complete never records stages out of order.
	_stages_observed = PackedStringArray()
	for s in _Stages.ORDERED_STAGES:
		_stages_observed.append(s)
	_stage = "complete"
	_progress = 1.0
	_finalized = true
	set_meta(META_STAGE, _stage)
	set_meta(META_PREVIEW, false)
	# Local solid presentation only — not client World Commit (H-20).
	set_meta("preview_owns_ownership", false)
	set_meta("preview_owns_collision", true)  # local complete collision body
	set_meta("durable_mutation_applied", false)
	set_meta("client_world_commit", false)
	_apply_stage_visuals()
	_set_collision_enabled(true)


func mark_cancelled() -> void:
	_cancelled = true
	_finalized = false
	_set_collision_enabled(false)
	set_meta(META_PREVIEW, true)


func _record_stage(stage: String) -> void:
	if not _Stages.is_valid_stage(stage):
		return
	if not _stages_observed.has(stage):
		_stages_observed.append(stage)


func free_cleanup() -> void:
	mark_cancelled()
	if is_instance_valid(_static_body):
		_static_body.collision_layer = 0
		_static_body.collision_mask = 0
	if is_instance_valid(_collision_shape):
		_collision_shape.disabled = true
	if is_instance_valid(_external_visual):
		# Ensure no leftover solid bodies under external visual on cancel.
		_zero_collision_recursive(_external_visual)
	queue_free()


func rotate_preview(degrees: float) -> bool:
	## Build-context hologram rotate only. No-op when finalized/cancelled.
	## Preview remains non-authoritative (no ownership / no official collision).
	if _cancelled or _finalized:
		return false
	if _Stages.allows_durable_collision(_stage):
		return false
	rotate_y(deg_to_rad(degrees))
	set_meta(META_PREVIEW, true)
	set_meta("preview_owns_ownership", false)
	set_meta("preview_owns_collision", false)
	return true


func get_preview_authority_flags() -> Dictionary:
	return {
		"preview": bool(get_meta(META_PREVIEW, true)),
		"preview_owns_ownership": false,
		"preview_owns_collision": bool(get_meta("preview_owns_collision", false)),
		"has_durable_collision": has_durable_collision(),
		"stage": _stage,
		"finalized": _finalized,
		"cancelled": _cancelled,
		"durable_mutation_applied": bool(get_meta("durable_mutation_applied", false)),
		"client_world_commit": bool(get_meta("client_world_commit", false)),
		"collision_only_at_complete": _Stages.allows_durable_collision(_stage) == has_durable_collision()
			or not has_durable_collision(),
	}


## Attach a runtime-loaded visual (e.g. quarantine GLB root). Does NOT enable
## collision. Preview stages keep collision_layer=0 (WO-G8-UX-001 invariant).
## Hides the default box mesh when an external visual is present.
func attach_external_visual(visual: Node3D) -> bool:
	if visual == null or _cancelled:
		return false
	if _external_visual != null and is_instance_valid(_external_visual):
		remove_child(_external_visual)
		_external_visual.free()
		_external_visual = null
	if visual.get_parent():
		visual.get_parent().remove_child(visual)
	visual.name = "ExternalVisual"
	add_child(visual)
	_external_visual = visual
	_zero_collision_recursive(visual)
	# Prefer external mesh for presentation; keep stage collision gate on box body.
	if is_instance_valid(_mesh_instance):
		_mesh_instance.visible = false
	set_meta("has_external_visual", true)
	# Re-apply stage visuals / collision gate (still non-solid until complete).
	_apply_stage_visuals()
	_set_collision_enabled(_Stages.allows_durable_collision(_stage) and not _cancelled)
	return true


func has_external_visual() -> bool:
	return _external_visual != null and is_instance_valid(_external_visual)


func _zero_collision_recursive(n: Node) -> void:
	if n is StaticBody3D:
		(n as StaticBody3D).collision_layer = 0
		(n as StaticBody3D).collision_mask = 0
	if n is CollisionShape3D:
		(n as CollisionShape3D).disabled = true
	if n is AnimatableBody3D:
		(n as AnimatableBody3D).collision_layer = 0
		(n as AnimatableBody3D).collision_mask = 0
	for c in n.get_children():
		_zero_collision_recursive(c)


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
	# Minimum readable volume at game distance (Directive 23).
	var sz := entity_size
	sz.x = maxf(sz.x, 2.4)
	sz.y = maxf(sz.y, 2.2)
	sz.z = maxf(sz.z, 2.4)
	entity_size = sz
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


func _reduced_motion_active() -> bool:
	var a11y := _autoload_node("ControlAccessibilitySettings")
	if a11y != null and "reduced_motion" in a11y:
		return bool(a11y.reduced_motion)
	var sm := _autoload_node("SettingsManager")
	if sm != null and sm.has_method("get_value"):
		return bool(sm.call("get_value", "gameplay", "reduced_motion", false))
	return false


func _apply_stage_visuals() -> void:
	# Object-level stage language (DESIGN.md): cyan light construction, not banner-only.
	if not _presentation_enabled or _material == null or _mesh_instance == null:
		return
	var opacity: float = _Stages.visual_opacity(_stage)
	var emission_e: float = _Stages.visual_emission_energy(_stage)
	var base := _style_tint()
	var reduced := _reduced_motion_active()
	# Distinct scale/opacity so stages read at a glance (geometry-stable collision box).
	# Reduced motion: skip non-essential scale pops (C1B-A11Y-07).
	match _stage:
		"wireframe":
			_mesh_instance.scale = Vector3.ONE if reduced else Vector3(1.08, 1.08, 1.08)
			_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			_material.albedo_color = Color(base.r, base.g, base.b, maxf(0.12, opacity * 0.55))
			_material.emission_enabled = true
			_material.emission = base
			_material.emission_energy_multiplier = maxf(0.55, emission_e)
			# Hollow-read: no depth write so it feels like construction lines.
		"hologram":
			_mesh_instance.scale = Vector3.ONE if reduced else Vector3(1.02, 1.02, 1.02)
			_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			_material.albedo_color = Color(base.r, base.g, base.b, maxf(0.35, opacity))
			_material.emission_enabled = true
			_material.emission = base.lightened(0.2)
			_material.emission_energy_multiplier = maxf(1.2, emission_e)
		"materializing":
			_mesh_instance.scale = Vector3.ONE
			_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			_material.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL
			# Mix cyan construction into cream surface (readable progress).
			var cream := Color("FFF1C7")
			var mixed := base.lerp(cream, 0.45)
			_material.albedo_color = Color(mixed.r, mixed.g, mixed.b, maxf(0.65, opacity))
			_material.emission_enabled = true
			_material.emission = base.darkened(0.1)
			_material.emission_energy_multiplier = 0.45
		"complete":
			_mesh_instance.scale = Vector3.ONE
			_material.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED
			_material.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL
			_material.albedo_color = Color("F7B267")  # cozy surface_primary
			_material.emission_enabled = false
			_material.emission_energy_multiplier = 0.0
			_material.roughness = 0.82
		_:
			pass


func _style_tint() -> Color:
	## Manifestation cyan is the construction light (DESIGN.md #62E6FF), not world purple.
	match art_style:
		"cyberpunk_dense":
			return Color(0.2, 0.95, 0.9)
		"pastoral_fantasy":
			return Color(0.45, 0.9, 0.65)
		"surrealism_canvas":
			return Color(0.55, 0.85, 1.0)  # keep cyan construction even on surreal worlds
		_:
			return Color("62E6FF")



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


func _position_from_geometry(geometry: Dictionary) -> Vector3:
	if geometry.has("position") and geometry.get("position") != null:
		var p: Variant = geometry.get("position")
		# Explicit zero is valid; only fall through when key absent.
		return _parse_vec3(p)
	var t: Variant = geometry.get("transform", null)
	if t is Dictionary:
		return _position_from_transform(t as Dictionary)
	return Vector3.ZERO


func _position_from_transform(t: Dictionary) -> Vector3:
	## World Prompt 2.5D transform: ground (x, y) + elevation → Godot (x, elevation, y).
	var gx := float(t.get("x", 0.0))
	var elev := float(t.get("elevation", 0.0))
	var gz: float
	if t.has("z"):
		gz = float(t.get("z", 0.0))
	else:
		gz = float(t.get("y", 0.0))
	return Vector3(gx, elev, gz)


func _parse_size(raw: Variant) -> Vector3:
	var v := _parse_size_vec3(raw)
	if v == Vector3.ZERO:
		return Vector3(2.0, 2.0, 2.0)
	return Vector3(maxf(v.x, 0.25), maxf(v.y, 0.25), maxf(v.z, 0.25))


func _parse_size_vec3(raw: Variant) -> Vector3:
	## Bounds dict uses width/depth/height; Vector3 uses x/y/z.
	if raw is Vector3:
		return raw
	if raw is Dictionary:
		var d: Dictionary = raw
		var sx := float(d.get("x", d.get("width", 0.0)))
		var sy := float(d.get("y", d.get("height", 0.0)))
		var sz := float(d.get("z", d.get("depth", 0.0)))
		return Vector3(sx, sy, sz)
	if raw is Array and raw.size() >= 3:
		return Vector3(float(raw[0]), float(raw[1]), float(raw[2]))
	return Vector3.ZERO


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

## Agent-Manifestation module root — 2.5D progressive construction renderer.
## Stages: wireframe → hologram → materializing → complete (schema-locked).
## Preview never creates durable collision; cancel removes all preview geometry.
##
## Mount: ModuleRegistry MODULE_VOXEL (legacy slot name; not voxel digging).
## Host:  WorldRoot.get_manifestation_host(space_id)
##
## Reduced-motion / skip-animation:
##   - Call set_skip_animation(true), or
##   - SettingsManager gameplay/reduced_motion or gameplay/skip_manifestation_animation
##
## G3 house preview (executor-friendly):
##   start_house_preview(prompt_or_geometry [, options]) → stage walk
##   cancel_preview(prompt_id) → free preview, no durable collision
## Prefer g3_preview_bridge.gd so coordinator code does not own module internals.
class_name ManifestationModule
extends Node

const MODULE_ID := "voxel"  # ModuleRegistry slot (AIdleConstants.MODULE_VOXEL)
const _Stages = preload("res://scripts/modules/manifestation/manifestation_stages.gd")
const _Instance = preload("res://scripts/modules/manifestation/manifestation_instance.gd")
const _IManifestation = preload("res://scripts/modules/interfaces/i_manifestation_module.gd")

## prompt_id -> ManifestationInstance
var _active: Dictionary = {}
var _skip_animation: bool = false
## When true, start_manifestation will not re-read SettingsManager (call-site override).
var _suppress_settings_refresh: bool = false
var _host_fallback: Node3D


func _ready() -> void:
	_refresh_skip_flag_from_settings()
	_try_register()
	var missing: PackedStringArray = _IManifestation.validate(self)
	if not missing.is_empty():
		push_error("[ManifestationModule] Missing API methods: %s" % str(missing))
	print("[ManifestationModule] Ready | skip_animation=%s" % _skip_animation)


## ─── IManifestationModule / IVoxelModule surface ─────────────────────────────

func start_manifestation(prompt_id: String, art_style: String, geometry: Dictionary) -> bool:
	if prompt_id.is_empty():
		push_warning("[ManifestationModule] start_manifestation: empty prompt_id")
		return false
	if _active.has(prompt_id):
		push_warning("[ManifestationModule] Already active: %s" % prompt_id)
		return false

	if not _suppress_settings_refresh:
		_refresh_skip_flag_from_settings()

	var instance: Node3D = _Instance.new()
	instance.name = "Manifestation_%s" % prompt_id.substr(0, 8)
	instance.call("configure", prompt_id, art_style, geometry)

	var host := _resolve_host(str(geometry.get("target_space", "private_reality")))
	if host == null:
		# Expected in isolated smoke / before WorldRoot binds mounts.
		push_warning("[ManifestationModule] No manifestation host; using local fallback.")
		if _host_fallback == null:
			_host_fallback = Node3D.new()
			_host_fallback.name = "ManifestationHostFallback"
			add_child(_host_fallback)
		host = _host_fallback
	host.add_child(instance)
	_active[prompt_id] = instance

	var provenance: Dictionary = {}
	if geometry.get("provenance", {}) is Dictionary:
		provenance = geometry.get("provenance", {})
	var space: String = str(instance.get("target_space"))
	_emit_started(prompt_id, space, provenance)

	if _skip_animation:
		instance.call("finalize_complete")
		_emit_progress(prompt_id, 1.0, "complete")
		_emit_completed(prompt_id, provenance)
	else:
		instance.call("set_stage", "wireframe")
		_emit_progress(prompt_id, 0.0, "wireframe")

	return true


## ─── G3 house preview lifecycle ──────────────────────────────────────────────

## Start a house (or structure) preview from a Structured World Prompt dict
## OR a geometry dict (prompt_id + bounds/transform/size).
##
## Default: advances wireframe → hologram → materializing → complete (sync).
## Reduced-motion / skip_animation jumps to complete with all stages recorded.
##
## options:
##   auto_advance (bool, default true) — walk stages after start
##   stop_at_stage / stop_at (String) — halt at/before stage (cancel demos)
##   skip_animation (bool) — temporary override for this call only when set
##
## Returns snapshot dict: ok, prompt_id, stage, stages_observed, has_durable_collision, …
func start_house_preview(prompt_or_geometry: Variant, options: Dictionary = {}) -> Dictionary:
	_refresh_skip_flag_from_settings()
	var prior_skip := _skip_animation
	var prior_suppress := _suppress_settings_refresh
	if options.has("skip_animation"):
		_skip_animation = bool(options.get("skip_animation"))
		# Keep explicit option across start_manifestation (do not re-apply settings).
		_suppress_settings_refresh = true

	var parsed := _normalize_house_preview_input(prompt_or_geometry)
	if not bool(parsed.get("ok", false)):
		_skip_animation = prior_skip
		_suppress_settings_refresh = prior_suppress
		return {
			"ok": false,
			"reason": str(parsed.get("reason", "invalid_input")),
			"prompt_id": str(parsed.get("prompt_id", "")),
			"stage": "",
			"stages_observed": [],
			"has_durable_collision": false,
			"durable_mutation_applied": false,
		}

	var prompt_id: String = str(parsed["prompt_id"])
	var art_style: String = str(parsed["art_style"])
	var geometry: Dictionary = parsed["geometry"] as Dictionary

	if _active.has(prompt_id):
		_skip_animation = prior_skip
		_suppress_settings_refresh = prior_suppress
		var snap := get_preview_snapshot(prompt_id)
		snap["ok"] = false
		snap["reason"] = "already_active"
		return snap

	var started: bool = start_manifestation(prompt_id, art_style, geometry)
	if not started:
		_skip_animation = prior_skip
		_suppress_settings_refresh = prior_suppress
		return {
			"ok": false,
			"reason": "start_failed",
			"prompt_id": prompt_id,
			"stage": "",
			"stages_observed": [],
			"has_durable_collision": false,
			"durable_mutation_applied": false,
		}

	var auto_advance: bool = bool(options.get("auto_advance", true))
	var stop_at: String = str(options.get("stop_at_stage", options.get("stop_at", "")))

	if auto_advance and not _skip_animation:
		_advance_preview_stages(prompt_id, stop_at)
	# skip_animation path already finalized inside start_manifestation

	var result := get_preview_snapshot(prompt_id)
	result["ok"] = true
	result["reason"] = ""
	result["durable_mutation_applied"] = false
	result["recipe_id"] = str(geometry.get("recipe_id", ""))
	_skip_animation = prior_skip
	_suppress_settings_refresh = prior_suppress
	return result


## Cancel a preview by prompt_id. Tears down geometry; leaves no durable collision.
## Idempotent when prompt is already absent.
func cancel_preview(prompt_id: String, reason: String = "player_cancel") -> Dictionary:
	if prompt_id.is_empty():
		return {
			"ok": false,
			"reason": "empty_prompt_id",
			"prompt_id": "",
			"status": "error",
			"has_durable_collision": false,
			"durable_mutation_applied": false,
		}
	if not _active.has(prompt_id):
		return {
			"ok": true,
			"prompt_id": prompt_id,
			"status": "already_absent",
			"stage": "",
			"stages_observed": [],
			"has_durable_collision": false,
			"durable_mutation_applied": false,
			"cancel_reason": reason if not reason.is_empty() else "player_cancel",
		}

	var stages_before: Array = []
	var stage_before := ""
	var inst := _get_instance(prompt_id)
	if inst != null:
		stage_before = str(inst.call("get_stage"))
		var observed: Variant = inst.call("get_stages_observed")
		if observed is PackedStringArray:
			for s in observed as PackedStringArray:
				stages_before.append(s)
		elif observed is Array:
			stages_before = (observed as Array).duplicate()

	var cancel_reason := reason if not reason.is_empty() else "player_cancel"
	cancel_manifestation(prompt_id, cancel_reason)

	return {
		"ok": true,
		"prompt_id": prompt_id,
		"status": "cancelled",
		"stage": "cancelled",
		"cancelled_during_stage": stage_before,
		"stages_observed": stages_before,
		"has_durable_collision": false,
		"durable_mutation_applied": false,
		"cancel_reason": cancel_reason,
	}


## Snapshot for executor/G3 receipts (does not mutate).
func get_preview_snapshot(prompt_id: String) -> Dictionary:
	var instance := _get_instance(prompt_id)
	if instance == null:
		return {
			"ok": false,
			"prompt_id": prompt_id,
			"active": false,
			"stage": "",
			"progress": 0.0,
			"stages_observed": [],
			"has_durable_collision": false,
			"finalized": false,
			"cancelled": false,
		}
	var stages: Array = []
	var observed: Variant = instance.call("get_stages_observed")
	if observed is PackedStringArray:
		for s in observed as PackedStringArray:
			stages.append(s)
	elif observed is Array:
		stages = (observed as Array).duplicate()
	return {
		"ok": true,
		"prompt_id": prompt_id,
		"active": true,
		"stage": str(instance.call("get_stage")),
		"progress": float(instance.call("get_progress")),
		"stages_observed": stages,
		"has_durable_collision": bool(instance.call("has_durable_collision")),
		"finalized": bool(instance.call("is_finalized")),
		"cancelled": bool(instance.call("is_cancelled")),
		"recipe_id": str(instance.get("recipe_id")),
		"target_space": str(instance.get("target_space")),
	}


## Build geometry dict from a Structured World Prompt (G3 house path).
func geometry_from_world_prompt(world_prompt: Dictionary) -> Dictionary:
	var entity: Dictionary = {}
	if world_prompt.get("entity", {}) is Dictionary:
		entity = world_prompt.get("entity", {}) as Dictionary
	var target: Dictionary = {}
	if world_prompt.get("target", {}) is Dictionary:
		target = world_prompt.get("target", {}) as Dictionary
	var manifestation: Dictionary = {}
	if world_prompt.get("manifestation", {}) is Dictionary:
		manifestation = world_prompt.get("manifestation", {}) as Dictionary
	var transform: Variant = entity.get("transform", {})
	var bounds: Variant = entity.get("bounds", {})
	var geometry := {
		"target_space": str(target.get("space_type", "private_reality")),
		"space_id": str(target.get("space_id", "")),
		"recipe_id": str(entity.get("recipe_id", "")),
		"transform": transform if transform is Dictionary else {},
		"bounds": bounds if bounds is Dictionary else bounds,
		"size": bounds,
		"provenance": world_prompt.get("provenance", {}),
		"preview_only": true,
		"presentation_duration_seconds": float(
			manifestation.get("presentation_duration_seconds", 12.0)
		),
	}
	if transform is Dictionary:
		geometry["position"] = _position_dict_from_transform(transform as Dictionary)
	return geometry


func _position_dict_from_transform(t: Dictionary) -> Dictionary:
	## Mirror instance 2.5D mapping for explicit position field.
	var gz: float = float(t.get("z", t.get("y", 0.0))) if t.has("z") else float(t.get("y", 0.0))
	return {
		"x": float(t.get("x", 0.0)),
		"y": float(t.get("elevation", 0.0)),
		"z": gz,
	}


func _normalize_house_preview_input(prompt_or_geometry: Variant) -> Dictionary:
	if not (prompt_or_geometry is Dictionary):
		return {"ok": false, "reason": "invalid_input"}
	var d: Dictionary = prompt_or_geometry as Dictionary

	# Structured World Prompt shape (has entity/manifestation/operation).
	if d.has("prompt_id") and (
		d.has("entity") or d.has("manifestation") or d.has("operation") or d.has("confirmation")
	):
		var prompt_id := str(d.get("prompt_id", ""))
		if prompt_id.is_empty():
			return {"ok": false, "reason": "missing_prompt_id"}
		var style := "cozy_cyber_pixel_2_5d"
		var sp: Variant = d.get("style_profile", {})
		if sp is Dictionary:
			style = str((sp as Dictionary).get("base_concept", style))
		return {
			"ok": true,
			"prompt_id": prompt_id,
			"art_style": style,
			"geometry": geometry_from_world_prompt(d),
		}

	# Nested geometry wrapper: {prompt_id, art_style?, geometry:{…}}
	var prompt_id2 := str(d.get("prompt_id", d.get("id", "")))
	var style2 := str(d.get("art_style", d.get("base_concept", "cozy_cyber_pixel_2_5d")))
	var geom: Dictionary
	if d.get("geometry", null) is Dictionary:
		geom = (d.get("geometry") as Dictionary).duplicate(true)
		if not geom.has("provenance") and d.get("provenance", null) is Dictionary:
			geom["provenance"] = d.get("provenance")
		if not geom.has("recipe_id") and d.has("recipe_id"):
			geom["recipe_id"] = d.get("recipe_id")
	else:
		geom = d.duplicate(true)

	if prompt_id2.is_empty():
		return {"ok": false, "reason": "missing_prompt_id", "prompt_id": ""}
	return {"ok": true, "prompt_id": prompt_id2, "art_style": style2, "geometry": geom}


func _advance_preview_stages(prompt_id: String, stop_at: String) -> void:
	## Sync walk: hologram → materializing → complete (wireframe already set).
	var stop_i := _Stages.stage_index(stop_at) if not stop_at.is_empty() else -1
	for stage in _Stages.ORDERED_STAGES:
		if stage == "wireframe":
			continue
		var si := _Stages.stage_index(stage)
		if stop_i >= 0 and si > stop_i:
			break
		var instance := _get_instance(prompt_id)
		if instance == null or bool(instance.call("is_cancelled")):
			return
		if stage == "complete":
			finalize_manifestation(prompt_id)
			return
		instance.call("set_stage", stage)
		_emit_progress(prompt_id, _Stages.progress_for_stage(stage), stage)


func update_construction_progress(prompt_id: String, progress: float) -> void:
	var instance := _get_instance(prompt_id)
	if instance == null:
		return
	if _skip_animation:
		if not bool(instance.call("is_finalized")):
			finalize_manifestation(prompt_id)
		return
	var p := clampf(progress, 0.0, 1.0)
	instance.call("set_progress", p)
	var stage: String = str(instance.call("get_stage"))
	_emit_progress(prompt_id, p, stage)
	if stage == "complete" and not bool(instance.call("is_finalized")):
		instance.call("finalize_complete")
		_emit_completed(prompt_id, instance.get("provenance"))


func finalize_manifestation(prompt_id: String) -> void:
	var instance := _get_instance(prompt_id)
	if instance == null:
		return
	if bool(instance.call("is_cancelled")):
		return
	if not _skip_animation and not bool(instance.call("is_finalized")):
		var current: String = str(instance.call("get_stage"))
		for stage in _Stages.ORDERED_STAGES:
			if _Stages.stage_index(stage) <= _Stages.stage_index(current):
				continue
			instance.call("set_stage", stage)
			_emit_progress(prompt_id, _Stages.progress_for_stage(stage), stage)
			current = stage
	instance.call("finalize_complete")
	_emit_progress(prompt_id, 1.0, "complete")
	_emit_completed(prompt_id, instance.get("provenance"))


func cancel_manifestation(prompt_id: String, reason: String) -> void:
	var instance := _get_instance(prompt_id)
	if instance == null:
		return
	instance.call("free_cleanup")
	_active.erase(prompt_id)
	_emit_cancelled(prompt_id, reason if not reason.is_empty() else "cancelled")


func get_manifestation_stage(prompt_id: String) -> String:
	var instance := _get_instance(prompt_id)
	if instance == null:
		return ""
	return str(instance.call("get_stage"))


func has_durable_collision(prompt_id: String) -> bool:
	var instance := _get_instance(prompt_id)
	if instance == null:
		return false
	return bool(instance.call("has_durable_collision"))


func set_skip_animation(enabled: bool) -> void:
	_skip_animation = enabled


func get_skip_animation() -> bool:
	return _skip_animation


func get_active_prompt_ids() -> PackedStringArray:
	return PackedStringArray(_active.keys())


func is_stub() -> bool:
	return false


func get_status() -> String:
	return "ManifestationModule active=%d skip=%s" % [_active.size(), _skip_animation]


## ─── Internals ───────────────────────────────────────────────────────────────

func _get_instance(prompt_id: String) -> Node:
	if not _active.has(prompt_id):
		return null
	var node: Variant = _active[prompt_id]
	if not is_instance_valid(node):
		_active.erase(prompt_id)
		return null
	return node as Node


func _resolve_host(space_id: String) -> Node3D:
	var gm := _autoload("GameManager")
	if gm != null:
		var wr: Variant = gm.get("world_root")
		if wr != null and is_instance_valid(wr) and wr.has_method("get_manifestation_host"):
			var host: Variant = wr.call("get_manifestation_host", space_id)
			if host != null and host is Node3D:
				return host as Node3D
	var tree := get_tree()
	if tree:
		for n in tree.get_nodes_in_group("reality_spaces"):
			if n is Node and n.has_node("ManifestationHost"):
				return n.get_node("ManifestationHost") as Node3D
	return null


func _refresh_skip_flag_from_settings() -> void:
	var settings := _autoload("SettingsManager")
	if settings == null:
		return
	var reduced: bool = bool(settings.call("get_value", "gameplay", "reduced_motion", false))
	var skip_key: bool = bool(settings.call("get_value", "gameplay", "skip_manifestation_animation", false))
	if reduced or skip_key:
		_skip_animation = true


func _try_register() -> void:
	var reg := _autoload("ModuleRegistry")
	if reg == null:
		return
	var existing: Variant = reg.call("get_module", MODULE_ID) if reg.has_method("get_module") else null
	var should_register := true
	if existing != null and is_instance_valid(existing) and existing != self:
		# Duck-type stub detection — avoid hard dependency on ModuleStub class_name
		# (concurrent agents may leave stubs temporarily unparseable).
		if existing.has_method("is_stub") and bool(existing.call("is_stub")):
			should_register = true
		else:
			should_register = false
	if not should_register:
		return
	if reg.has_method("attach_to_mount"):
		reg.call("attach_to_mount", MODULE_ID, self)
	if reg.has_method("register_module"):
		reg.call("register_module", MODULE_ID, self)


func _autoload(name: String) -> Node:
	var tree := get_tree()
	if tree == null:
		# Early _ready race: fall back to root via Engine main loop.
		var ml := Engine.get_main_loop()
		if ml is SceneTree:
			tree = ml as SceneTree
	if tree == null or tree.root == null:
		return null
	return tree.root.get_node_or_null(NodePath(name))


func _emit_started(prompt_id: String, space: String, provenance: Dictionary) -> void:
	var bus := _autoload("EventBus")
	if bus and bus.has_signal("manifestation_started"):
		bus.emit_signal("manifestation_started", prompt_id, space, provenance)


func _emit_progress(prompt_id: String, progress: float, stage: String) -> void:
	var bus := _autoload("EventBus")
	if bus and bus.has_signal("manifestation_progress_updated"):
		bus.emit_signal("manifestation_progress_updated", prompt_id, progress, stage)


func _emit_completed(prompt_id: String, provenance: Variant) -> void:
	var bus := _autoload("EventBus")
	var prov: Dictionary = provenance if provenance is Dictionary else {}
	if bus and bus.has_signal("manifestation_completed"):
		bus.emit_signal("manifestation_completed", prompt_id, prov)


func _emit_cancelled(prompt_id: String, reason: String) -> void:
	var bus := _autoload("EventBus")
	if bus and bus.has_signal("manifestation_cancelled"):
		bus.emit_signal("manifestation_cancelled", prompt_id, reason)

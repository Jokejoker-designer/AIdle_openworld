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
class_name ManifestationModule
extends Node

const MODULE_ID := "voxel"  # ModuleRegistry slot (AIdleConstants.MODULE_VOXEL)
const _Stages = preload("res://scripts/modules/manifestation/manifestation_stages.gd")
const _Instance = preload("res://scripts/modules/manifestation/manifestation_instance.gd")
const _IManifestation = preload("res://scripts/modules/interfaces/i_manifestation_module.gd")

## prompt_id -> ManifestationInstance
var _active: Dictionary = {}
var _skip_animation: bool = false
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

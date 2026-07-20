## Thin G3 facade over ManifestationModule for the onboarding vertical slice.
## Executor / transaction coordinator call this without owning module internals.
##
## Lifecycle:
##   start_house_preview(prompt_or_geometry) → wireframe→hologram→materializing→complete
##   cancel_preview(prompt_id) → no durable collision / no durable_mutation_applied
##
## Reduced-motion: set_skip_animation(true) or SettingsManager gameplay flags
## (honoured by the bound module). Headless presentation skip stays in the instance.
##
## Not a World Commit path. Local complete collision is presentation only.
class_name G3PreviewBridge
extends RefCounted

const MODULE_PATH := "res://scripts/modules/manifestation/manifestation_module.gd"
const DEFAULT_MODULE_ID := "voxel"

var _module: Node = null


## Bind an existing ManifestationModule node (preferred when already mounted).
func bind(module: Node) -> G3PreviewBridge:
	_module = module
	return self


## Resolve module from ModuleRegistry, then optional parent child, else instantiate.
## When create_if_missing is true and parent is given, attaches a new module under parent.
func resolve(
	parent: Node = null,
	create_if_missing: bool = true,
	module_id: String = DEFAULT_MODULE_ID
) -> bool:
	if _module != null and is_instance_valid(_module):
		return true

	var reg := _autoload("ModuleRegistry")
	if reg != null and reg.has_method("get_module"):
		var existing: Variant = reg.call("get_module", module_id)
		if existing != null and is_instance_valid(existing) and existing is Node:
			if not (existing.has_method("is_stub") and bool(existing.call("is_stub"))):
				if existing.has_method("start_house_preview") or existing.has_method("start_manifestation"):
					_module = existing as Node
					return true

	if parent != null and is_instance_valid(parent):
		for child in parent.get_children():
			if child.has_method("start_house_preview") or child.has_method("start_manifestation"):
				if child.has_method("is_stub") and bool(child.call("is_stub")):
					continue
				_module = child
				return true

	if create_if_missing and parent != null and is_instance_valid(parent):
		var script: GDScript = load(MODULE_PATH) as GDScript
		if script == null:
			push_error("[G3PreviewBridge] could not load %s" % MODULE_PATH)
			return false
		var mod: Node = script.new() as Node
		mod.name = "ManifestationModule"
		parent.add_child(mod)
		_module = mod
		return true

	return _module != null and is_instance_valid(_module)


func is_bound() -> bool:
	return _module != null and is_instance_valid(_module)


func get_module() -> Node:
	return _module


## Accepts Structured World Prompt dict OR geometry dict (+ optional options).
## See ManifestationModule.start_house_preview for options (auto_advance, stop_at_stage, skip_animation).
func start_house_preview(prompt_or_geometry: Variant, options: Dictionary = {}) -> Dictionary:
	if not is_bound():
		return _unbound("start_house_preview")
	if not _module.has_method("start_house_preview"):
		return {
			"ok": false,
			"reason": "module_missing_start_house_preview",
			"prompt_id": "",
			"stage": "",
			"stages_observed": [],
			"has_durable_collision": false,
			"durable_mutation_applied": false,
		}
	return _module.call("start_house_preview", prompt_or_geometry, options) as Dictionary


## Cancel preview; guarantees has_durable_collision=false and durable_mutation_applied=false.
func cancel_preview(prompt_id: String, reason: String = "player_cancel") -> Dictionary:
	if not is_bound():
		return _unbound("cancel_preview", prompt_id)
	if _module.has_method("cancel_preview"):
		return _module.call("cancel_preview", prompt_id, reason) as Dictionary
	# Fallback to core cancel API.
	if _module.has_method("cancel_manifestation"):
		_module.call("cancel_manifestation", prompt_id, reason if not reason.is_empty() else "player_cancel")
		return {
			"ok": true,
			"prompt_id": prompt_id,
			"status": "cancelled",
			"has_durable_collision": false,
			"durable_mutation_applied": false,
			"cancel_reason": reason if not reason.is_empty() else "player_cancel",
		}
	return {
		"ok": false,
		"reason": "module_missing_cancel",
		"prompt_id": prompt_id,
		"has_durable_collision": false,
		"durable_mutation_applied": false,
	}


func get_stage(prompt_id: String) -> String:
	if not is_bound() or not _module.has_method("get_manifestation_stage"):
		return ""
	return str(_module.call("get_manifestation_stage", prompt_id))


func has_durable_collision(prompt_id: String) -> bool:
	if not is_bound() or not _module.has_method("has_durable_collision"):
		return false
	return bool(_module.call("has_durable_collision", prompt_id))


func get_preview_snapshot(prompt_id: String) -> Dictionary:
	if not is_bound():
		return _unbound("get_preview_snapshot", prompt_id)
	if _module.has_method("get_preview_snapshot"):
		return _module.call("get_preview_snapshot", prompt_id) as Dictionary
	return {
		"ok": is_bound(),
		"prompt_id": prompt_id,
		"stage": get_stage(prompt_id),
		"has_durable_collision": has_durable_collision(prompt_id),
		"stages_observed": [],
	}


func set_skip_animation(enabled: bool) -> void:
	if is_bound() and _module.has_method("set_skip_animation"):
		_module.call("set_skip_animation", enabled)


func get_skip_animation() -> bool:
	if is_bound() and _module.has_method("get_skip_animation"):
		return bool(_module.call("get_skip_animation"))
	return false


func geometry_from_world_prompt(world_prompt: Dictionary) -> Dictionary:
	if is_bound() and _module.has_method("geometry_from_world_prompt"):
		return _module.call("geometry_from_world_prompt", world_prompt) as Dictionary
	return {}


func _unbound(op: String, prompt_id: String = "") -> Dictionary:
	return {
		"ok": false,
		"reason": "bridge_unbound",
		"op": op,
		"prompt_id": prompt_id,
		"stage": "",
		"stages_observed": [],
		"has_durable_collision": false,
		"durable_mutation_applied": false,
	}


func _autoload(name: String) -> Node:
	var ml := Engine.get_main_loop()
	if ml is SceneTree:
		var tree := ml as SceneTree
		if tree.root != null:
			return tree.root.get_node_or_null(NodePath(name))
	return null

## Placeholder stub modules so mounts are non-null and debug shows pending agents.
## Real agents REPLACE these by registering over the same module_id.
## G2-003: companion slot auto-upgrades to CompanionModule (stub replacement only).
class_name ModuleStub
extends Node

@export var module_id: String = ""
@export var agent_name: String = "Pending Agent"
@export var status_message: String = "Awaiting agent integration"


func _ready() -> void:
	if module_id.is_empty():
		return
	# Companion stub replacement (WO-G2-003 allowed path).
	if module_id == AIdleConstants.MODULE_COMPANION:
		_replace_with_companion_module()
		return
	# Executor stub replacement (WO-G2-006 allowed path).
	if module_id == AIdleConstants.MODULE_EXECUTOR:
		_replace_with_executor_module()
		return
	# Manifestation module uses legacy MODULE_VOXEL slot (not voxel digging).
	if module_id == AIdleConstants.MODULE_VOXEL:
		_replace_with_manifestation_module()
		return
	# Only register if no real module present yet.
	if not ModuleRegistry.has_module(module_id):
		ModuleRegistry.register_module(module_id, self)
		print("[ModuleStub] %s mounted as stub (%s)." % [module_id, agent_name])


func is_stub() -> bool:
	return true


func get_status() -> String:
	return status_message


func _replace_with_companion_module() -> void:
	# If a non-stub companion is already registered, do nothing.
	if ModuleRegistry.has_module(module_id):
		var existing: Node = ModuleRegistry.get_module(module_id)
		if existing != null and not (existing is ModuleStub) and existing != self:
			queue_free()
			return
	# load() avoids hard class_name dependency at parse time for ModuleStub.
	var companion_script: Script = load("res://scripts/modules/companion/companion_module.gd") as Script
	if companion_script == null:
		push_error("[ModuleStub] Failed to load CompanionModule script.")
		if not ModuleRegistry.has_module(module_id):
			ModuleRegistry.register_module(module_id, self)
		return
	var companion: Node = companion_script.new() as Node
	companion.name = "CompanionModule"
	if companion.get("companion_id") != null:
		companion.set("companion_id", "companion_lumi")
	var parent_node := get_parent()
	if parent_node:
		parent_node.add_child(companion)
	else:
		add_child(companion)
	# CompanionModule registers itself in _ready; drop this stub.
	if ModuleRegistry.has_module(module_id) and ModuleRegistry.get_module(module_id) == self:
		ModuleRegistry.unregister_module(module_id)
	if not ModuleRegistry.has_module(module_id):
		ModuleRegistry.register_module(module_id, companion)
	print("[ModuleStub] companion slot upgraded to CompanionModule (G2-003).")
	queue_free()


func _replace_with_executor_module() -> void:
	# If a non-stub executor is already registered, do nothing.
	if ModuleRegistry.has_module(module_id):
		var existing: Node = ModuleRegistry.get_module(module_id)
		if existing != null and not (existing is ModuleStub) and existing != self:
			queue_free()
			return
	# load() avoids hard class_name dependency at parse time for ModuleStub.
	var executor_script: Script = load("res://scripts/modules/executor/executor_module.gd") as Script
	if executor_script == null:
		push_error("[ModuleStub] Failed to load ExecutorModule script.")
		if not ModuleRegistry.has_module(module_id):
			ModuleRegistry.register_module(module_id, self)
		return
	var executor: Node = executor_script.new() as Node
	executor.name = "ExecutorModule"
	var parent_node := get_parent()
	if parent_node:
		parent_node.add_child(executor)
	else:
		add_child(executor)
	# ExecutorModule registers itself in _ready; drop this stub.
	if ModuleRegistry.has_module(module_id) and ModuleRegistry.get_module(module_id) == self:
		ModuleRegistry.unregister_module(module_id)
	if not ModuleRegistry.has_module(module_id):
		ModuleRegistry.register_module(module_id, executor)
	print("[ModuleStub] executor slot upgraded to ExecutorModule (G2-006).")
	queue_free()


func _replace_with_manifestation_module() -> void:
	if ModuleRegistry.has_module(module_id):
		var existing: Node = ModuleRegistry.get_module(module_id)
		if existing != null and not (existing is ModuleStub) and existing != self:
			queue_free()
			return
	var script: Script = load("res://scripts/modules/manifestation/manifestation_module.gd") as Script
	if script == null:
		push_error("[ModuleStub] Failed to load ManifestationModule script.")
		if not ModuleRegistry.has_module(module_id):
			ModuleRegistry.register_module(module_id, self)
		return
	var man: Node = script.new() as Node
	man.name = "ManifestationModule"
	var parent_node := get_parent()
	if parent_node:
		parent_node.add_child(man)
	else:
		add_child(man)
	if ModuleRegistry.has_module(module_id) and ModuleRegistry.get_module(module_id) == self:
		ModuleRegistry.unregister_module(module_id)
	if not ModuleRegistry.has_module(module_id):
		ModuleRegistry.register_module(module_id, man)
	print("[ModuleStub] voxel slot upgraded to ManifestationModule (progressive construction).")
	queue_free()

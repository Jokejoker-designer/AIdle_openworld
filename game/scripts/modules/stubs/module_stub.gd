## Placeholder stub modules so mounts are non-null and debug shows pending agents.
## Real agents REPLACE these by registering over the same module_id.
class_name ModuleStub
extends Node

@export var module_id: String = ""
@export var agent_name: String = "Pending Agent"
@export var status_message: String = "Awaiting agent integration"


func _ready() -> void:
	if module_id.is_empty():
		return
	# Only register if no real module present yet.
	if not ModuleRegistry.has_module(module_id):
		ModuleRegistry.register_module(module_id, self)
		print("[ModuleStub] %s mounted as stub (%s)." % [module_id, agent_name])


func is_stub() -> bool:
	return true


func get_status() -> String:
	return status_message

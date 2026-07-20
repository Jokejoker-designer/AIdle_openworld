## ModuleRegistry – clean attach points for Agent-Voxel / Companion / Network / Executor / etc.
## Other agents register their root node here; Core never hard-depends on their internals.
extends Node

## module_id -> Node implementing the expected interface (duck-typed + group).
var _modules: Dictionary = {}

## Reserved empty mount paths under WorldRoot (filled by scene).
var _mount_paths: Dictionary = {}


func _ready() -> void:
	print("[ModuleRegistry] Ready – waiting for Agent modules.")


## Register a live module node. Safe to call from module _ready().
func register_module(module_id: String, module: Node) -> void:
	if module_id.is_empty() or module == null:
		push_error("[ModuleRegistry] Invalid register_module call.")
		return
	if _modules.has(module_id):
		push_warning("[ModuleRegistry] Replacing module: %s" % module_id)
		unregister_module(module_id)
	_modules[module_id] = module
	module.add_to_group("aidle_module_%s" % module_id)
	EventBus.module_registered.emit(module_id, module)
	print("[ModuleRegistry] Registered module: %s (%s)" % [module_id, module.name])


func unregister_module(module_id: String) -> void:
	if not _modules.has(module_id):
		return
	var m: Node = _modules[module_id]
	if is_instance_valid(m) and m.is_in_group("aidle_module_%s" % module_id):
		m.remove_from_group("aidle_module_%s" % module_id)
	_modules.erase(module_id)
	EventBus.module_unregistered.emit(module_id)


func get_module(module_id: String) -> Node:
	return _modules.get(module_id, null)


func has_module(module_id: String) -> bool:
	return _modules.has(module_id) and is_instance_valid(_modules[module_id])


func list_modules() -> PackedStringArray:
	return PackedStringArray(_modules.keys())


## WorldRoot calls this once so agents know where to parent their runtime nodes.
func bind_mount(module_id: String, mount_node: Node) -> void:
	if mount_node == null:
		return
	_mount_paths[module_id] = mount_node.get_path()
	mount_node.set_meta("module_mount_id", module_id)
	mount_node.set_meta("awaiting_agent", true)


func get_mount(module_id: String) -> Node:
	if not _mount_paths.has(module_id):
		return null
	var tree := get_tree()
	if tree == null:
		return null
	return tree.root.get_node_or_null(_mount_paths[module_id])


## Parent `child` under the reserved mount. Returns false if mount missing.
func attach_to_mount(module_id: String, child: Node) -> bool:
	var mount := get_mount(module_id)
	if mount == null:
		push_warning("[ModuleRegistry] No mount for module: %s" % module_id)
		return false
	if child.get_parent():
		child.get_parent().remove_child(child)
	mount.add_child(child)
	mount.set_meta("awaiting_agent", false)
	return true


func is_mount_empty(module_id: String) -> bool:
	var mount := get_mount(module_id)
	if mount == null:
		return true
	return mount.get_child_count() == 0

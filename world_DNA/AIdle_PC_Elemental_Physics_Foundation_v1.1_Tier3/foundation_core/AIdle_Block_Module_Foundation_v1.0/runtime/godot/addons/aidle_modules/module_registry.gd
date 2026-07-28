class_name AIdleModuleRegistry
extends Node
var modules: Dictionary = {}
func load_json_catalog(path: String, root_key: String) -> Dictionary:
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null: return {}
    var parsed: Variant = JSON.parse_string(file.get_as_text())
    if typeof(parsed) != TYPE_DICTIONARY: return {}
    return parsed
func has_module(module_id: String) -> bool: return modules.has(module_id)
func get_module(module_id: String) -> Dictionary: return modules.get(module_id,{})

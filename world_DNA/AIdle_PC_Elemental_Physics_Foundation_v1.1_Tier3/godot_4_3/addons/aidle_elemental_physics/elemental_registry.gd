class_name AIdleElementalRegistry
extends Node

var elements: Dictionary = {}
var physical_profiles: Dictionary = {}
var reactions: Dictionary = {}
var forces: Dictionary = {}
var platform_profiles: Dictionary = {}
var simulation_lod_profiles: Dictionary = {}

func load_catalog(path: String, root_key: String, id_key: String) -> Dictionary:
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null:
        push_error("Cannot open catalog: %s" % path)
        return {}
    var parsed: Variant = JSON.parse_string(file.get_as_text())
    if typeof(parsed) != TYPE_DICTIONARY:
        return {}
    var indexed: Dictionary = {}
    for item in parsed.get(root_key, []):
        if typeof(item) == TYPE_DICTIONARY and item.has(id_key):
            indexed[item[id_key]] = item
    return indexed

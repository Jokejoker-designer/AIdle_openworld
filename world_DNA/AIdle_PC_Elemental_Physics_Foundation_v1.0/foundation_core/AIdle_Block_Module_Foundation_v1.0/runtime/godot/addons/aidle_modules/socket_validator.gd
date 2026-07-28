class_name AIdleSocketValidator
extends RefCounted
static func are_compatible(a: String,b: String,catalog: Dictionary)->bool:
    if not catalog.has(a): return false
    return catalog[a].get("compatible_with",[]).has(b)

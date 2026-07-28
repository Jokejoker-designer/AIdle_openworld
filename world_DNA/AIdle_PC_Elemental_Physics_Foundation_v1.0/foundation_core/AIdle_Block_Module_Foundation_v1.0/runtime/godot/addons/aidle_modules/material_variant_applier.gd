class_name AIdleMaterialVariantApplier
extends RefCounted
static func set_parameter_safe(mat: ShaderMaterial,name: StringName,value: Variant,allowlist: Array[StringName])->bool:
    if not allowlist.has(name): return false
    mat.set_shader_parameter(name,value)
    return true

class_name AIdleSkeletonAnimationResolver
extends RefCounted
static func validate_binding(module_def: Dictionary, animation_def: Dictionary)->Dictionary:
    var a: String=module_def.get("skeleton_id","")
    var b: String=animation_def.get("skeleton_id","")
    return {"passed":a==b,"error":"" if a==b else "Skeleton mismatch"}

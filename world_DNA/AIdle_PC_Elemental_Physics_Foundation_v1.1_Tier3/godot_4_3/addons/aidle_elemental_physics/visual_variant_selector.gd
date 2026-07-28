class_name AIdleVisualVariantSelector
extends Node

@export var default_variant_name: StringName = &"default"
@export var wet_variant_name: StringName = &"wet"
var current_variant: StringName = &"default"

func select_from_state(state: Dictionary, wet_threshold: float = 0.6) -> StringName:
    var selected := wet_variant_name if float(state.get("wetness", 0.0)) >= wet_threshold else default_variant_name
    select_variant(selected)
    return selected

func select_variant(variant_name: StringName) -> void:
    current_variant = variant_name
    for child in get_children():
        if child is Node3D:
            child.visible = StringName(child.name) == variant_name

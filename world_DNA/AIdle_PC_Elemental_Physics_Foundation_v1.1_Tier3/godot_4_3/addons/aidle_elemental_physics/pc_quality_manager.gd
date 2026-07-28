class_name AIdlePCQualityManager
extends Node

signal quality_profile_changed(profile_id: StringName)
var current_profile_id: StringName = &"pc_forward_plus_high_v1"
var current_profile: Dictionary = {}

func apply_profile(profile: Dictionary) -> void:
    current_profile = profile.duplicate(true)
    current_profile_id = StringName(profile.get("profile_id",""))
    Engine.physics_ticks_per_second = int(profile.get("physics_ticks_per_second",60))
    quality_profile_changed.emit(current_profile_id)

import bpy
act = bpy.data.actions.new("probe_act")
print("Action attrs sample:", [a for a in dir(act) if not a.startswith("_")][:40])
print("has fcurves", hasattr(act, "fcurves"))
print("has layers", hasattr(act, "layers"))
print("has slots", hasattr(act, "slots"))
if hasattr(act, "layers"):
    print("layers", list(act.layers))
# keyframe via pose to see structure
bpy.ops.object.armature_add()
arm = bpy.context.active_object
bpy.ops.object.mode_set(mode="POSE")
pb = arm.pose.bones[0]
pb.keyframe_insert("location", frame=1)
arm.animation_data_create()
arm.animation_data.action = act
pb.keyframe_insert("location", frame=1)
print("after keyframe action", arm.animation_data.action)
act2 = arm.animation_data.action
print("act2 type", type(act2), "attrs fcurves", hasattr(act2, "fcurves"), "layers", hasattr(act2, "layers"))
if hasattr(act2, "layers") and len(act2.layers):
    print("layer0", act2.layers[0], dir(act2.layers[0])[:20])
    if hasattr(act2.layers[0], "strips"):
        print("strips", list(act2.layers[0].strips))
print("DONE")

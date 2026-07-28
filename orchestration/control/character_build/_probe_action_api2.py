import bpy
bpy.ops.object.armature_add()
arm = bpy.context.active_object
bpy.ops.object.mode_set(mode="POSE")
pb = arm.pose.bones[0]
arm.animation_data_create()
act = bpy.data.actions.new("probe2")
arm.animation_data.action = act
pb.keyframe_insert("location", frame=1)
pb.keyframe_insert("location", frame=10)
layer = act.layers[0]
strip = layer.strips[0]
print("strip type", type(strip), [a for a in dir(strip) if not a.startswith("_")])
# try channelbag
if hasattr(strip, "channelbags"):
    print("channelbags", list(strip.channelbags))
if hasattr(act, "slots"):
    print("slots", list(act.slots))
    for s in act.slots:
        print("slot", s, [a for a in dir(s) if "channel" in a.lower() or "fcurve" in a.lower()])
# fcurve_ensure
print("is_layered", act.is_action_layered, "is_legacy", act.is_action_legacy)
# try convert to legacy?
if hasattr(act, "convert_to_legacy"):
    print("has convert_to_legacy")
# enumerate all fcurves via channelbag
for layer in act.layers:
    for strip in layer.strips:
        print("strip attrs channelbag methods")
        for attr in dir(strip):
            if "channel" in attr.lower() or "fcurve" in attr.lower() or "curve" in attr.lower():
                print(" ", attr, getattr(strip, attr, None))
# slots + channelbag API from docs
try:
    slot = act.slots[0]
    cb = strip.channelbag(slot)
    print("cb", cb, "fcurves", len(cb.fcurves) if hasattr(cb, "fcurves") else None)
    print("fcurve count", len(cb.fcurves))
except Exception as e:
    print("channelbag err", type(e), e)
print("DONE2")

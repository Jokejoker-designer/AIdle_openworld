import bpy
import addon_utils
wanted = ["fspy_blender", "real_scale_references"]
for name in wanted:
    try:
        addon_utils.enable(name, default_set=True, persistent=True)
        print(f"ENABLED {name}")
    except Exception as e:
        print(f"ENABLE_FAIL {name}: {e}")
# list modules matching
mods = [m.module for m in addon_utils.modules() if "fspy" in m.module.lower() or "scale" in m.module.lower() or "real_scale" in m.module.lower()]
print("MATCHING_MODULES", mods)
# verify load
for name in wanted:
    loaded = name in bpy.context.preferences.addons.keys()
    print(f"LOADED {name}={loaded}")
bpy.ops.wm.save_userpref()
print("SAVED_USERPREF")

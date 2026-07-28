import bpy
import addon_utils
import os
print("USER", bpy.utils.user_resource("SCRIPTS"))
print("ADDON_PATHS", list(bpy.utils.script_paths(subdir="addons"))[:10])
for m in addon_utils.modules():
    mod = getattr(m, "__name__", None) or getattr(m, "module", None) or str(m)
    name = str(mod)
    if "fspy" in name.lower() or "scale" in name.lower() or "real_scale" in name.lower():
        print("FOUND_MOD", name, getattr(m, "__file__", ""))
# try enable again
for name in ["fspy_blender", "real_scale_references"]:
    try:
        addon_utils.enable(name, default_set=True, persistent=True)
        print("EN", name, name in bpy.context.preferences.addons)
    except Exception as e:
        print("FAIL", name, type(e), e)
bpy.ops.wm.save_userpref()
print("prefs keys with f/s", [k for k in bpy.context.preferences.addons.keys() if "fspy" in k or "scale" in k or "real" in k])

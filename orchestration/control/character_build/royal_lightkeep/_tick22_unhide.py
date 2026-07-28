import bpy, os, shutil
from mathutils import Vector
BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
path = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend")
bpy.ops.wm.open_mainfile(filepath=path)
o = bpy.data.objects.get("LEVEL0_GROUND")
if o:
    o.hide_render = False
    o.hide_viewport = False
    print("UNHIDE LEVEL0_GROUND", tuple(round(v,2) for v in o.dimensions))
# any other outer base should stay visible
for name in ("OUTER_WALL", "OUTER_RING", "BASE_PLINTH", "LEVEL0_GROUND"):
    for obj in bpy.data.objects:
        if name in obj.name.upper() and obj.type=="MESH":
            obj.hide_render = False
            obj.hide_viewport = False
            print("SHOW", obj.name)
scene = bpy.context.scene
try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except Exception:
    scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 960
out = os.path.join(BASE, "renders_final")
for cam, fn in [("CAM_01_FRONT","final_front.png"),("CAM_05_FRONT_3Q","final_front_3q.png"),("CAM_TOP_PLAN","final_top.png")]:
    c = bpy.data.objects.get(cam)
    if not c: continue
    scene.camera = c
    scene.render.filepath = os.path.join(out, fn)
    bpy.ops.render.render(write_still=True)
    print("OK", fn)
bpy.ops.wm.save_as_mainfile(filepath=path)
shutil.copy2(path, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_FINAL.blend"))
shutil.copy2(path, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend"))
print("SAVED")

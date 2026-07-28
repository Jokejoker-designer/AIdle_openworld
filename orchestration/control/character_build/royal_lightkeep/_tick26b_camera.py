import bpy, os, math
from mathutils import Vector, Euler
BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
path = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V04_SCALE.blend")
bpy.ops.wm.open_mainfile(filepath=path)

def aim(cam, target=Vector((0, 1, 12))):
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

# Pull cameras back for full 24x19x38 building
positions = {
    "CAM_01_FRONT": Vector((1.0, 55.0, 22.0)),
    "CAM_02_REAR": Vector((1.0, -52.0, 22.0)),
    "CAM_03_LEFT": Vector((-52.0, 1.0, 22.0)),
    "CAM_04_RIGHT": Vector((52.0, 1.0, 22.0)),
    "CAM_05_FRONT_3Q": Vector((36.0, 40.0, 24.0)),
    "CAM_06_REAR_3Q": Vector((-36.0, -38.0, 24.0)),
    "CAM_TOP_PLAN": Vector((0.0, 1.0, 60.0)),
}
for name, loc in positions.items():
    c = bpy.data.objects.get(name)
    if not c:
        continue
    c.location = loc
    if name == "CAM_TOP_PLAN":
        direction = Vector((0, 1, 0)) - c.location
        c.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        c.data.type = "ORTHO"
        c.data.ortho_scale = 32
    else:
        aim(c)
        c.data.type = "PERSP"
        c.data.lens = 32

scene = bpy.context.scene
try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except Exception:
    scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 960
out = os.path.join(BASE, "renders_final")
work = os.path.join(BASE, "renders_pass1d")
for cam, dest, fn in [
    ("CAM_01_FRONT", out, "final_front.png"),
    ("CAM_05_FRONT_3Q", out, "final_front_3q.png"),
    ("CAM_02_REAR", out, "final_rear.png"),
    ("CAM_03_LEFT", out, "final_left.png"),
    ("CAM_04_RIGHT", out, "final_right.png"),
    ("CAM_TOP_PLAN", out, "final_top.png"),
    ("CAM_01_FRONT", work, "current_front_work.png"),
    ("CAM_05_FRONT_3Q", work, "current_front_3q_work.png"),
    ("CAM_TOP_PLAN", work, "current_top_plan_work.png"),
]:
    scene.camera = bpy.data.objects.get(cam)
    scene.render.filepath = os.path.join(dest, fn)
    bpy.ops.render.render(write_still=True)
    print("OK", fn)

bpy.ops.wm.save_as_mainfile(filepath=path)
import shutil
shutil.copy2(path, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend"))
shutil.copy2(path, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("CAM_FIX_DONE")

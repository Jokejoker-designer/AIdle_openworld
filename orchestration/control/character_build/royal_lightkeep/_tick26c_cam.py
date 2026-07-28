import bpy, os
from mathutils import Vector
BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
path = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V04_SCALE.blend")
bpy.ops.wm.open_mainfile(filepath=path)

def aim(cam, target):
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

target = Vector((0.5, 1.0, 16.0))
# Full building framing
setup = {
    "CAM_01_FRONT": (Vector((0.5, 72.0, 30.0)), 28),
    "CAM_05_FRONT_3Q": (Vector((42.0, 52.0, 32.0)), 28),
    "CAM_02_REAR": (Vector((0.5, -68.0, 30.0)), 28),
    "CAM_03_LEFT": (Vector((-68.0, 1.0, 30.0)), 28),
    "CAM_04_RIGHT": (Vector((68.0, 1.0, 30.0)), 28),
    "CAM_06_REAR_3Q": (Vector((-42.0, -50.0, 32.0)), 28),
}
for name, (loc, lens) in setup.items():
    c = bpy.data.objects.get(name)
    if not c: continue
    c.location = loc
    aim(c, target)
    c.data.lens = lens
    c.data.type = "PERSP"

c = bpy.data.objects.get("CAM_TOP_PLAN")
if c:
    c.location = Vector((0, 1, 70))
    direction = Vector((0, 1, 0)) - c.location
    c.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    c.data.type = "ORTHO"
    c.data.ortho_scale = 30

scene = bpy.context.scene
try: scene.render.engine = "BLENDER_EEVEE_NEXT"
except: scene.render.engine = "BLENDER_EEVEE"
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
]:
    scene.camera = bpy.data.objects.get(cam)
    scene.render.filepath = os.path.join(dest, fn)
    bpy.ops.render.render(write_still=True)
    print("OK", fn)
bpy.ops.wm.save_as_mainfile(filepath=path)
import shutil
shutil.copy2(path, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend"))
shutil.copy2(path, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("DONE")

# -*- coding: utf-8 -*-
"""Tick #63: soft camera pull-back for full silhouette proofs. No geometry rebuild."""
import bpy
import os
import shutil
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V40_MAT.blend")
LOOP = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bpy.ops.wm.open_mainfile(filepath=WORK)
print("OPEN", bpy.data.filepath)

backup = os.path.join(BASE, f"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_BACKUP_LOOP_{STAMP}.blend")
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True)
print("BACKUP", backup)

# Pull cameras slightly farther from center (CX~1, CY~1.5)
CENTER = Vector((1.0, 1.5, 12.0))
pull = {
    "CAM_01_FRONT": 1.08,
    "CAM_02_REAR": 1.08,
    "CAM_03_LEFT": 1.08,
    "CAM_04_RIGHT": 1.08,
    "CAM_05_FRONT_3Q": 1.10,
    "CAM_06_REAR_3Q": 1.10,
    "CAM_TOP_PLAN": 1.05,
}

for name, factor in pull.items():
    cam = bpy.data.objects.get(name)
    if not cam:
        print("MISS", name)
        continue
    # move away from center in XY (and slightly Z for ortho/perspective)
    offset = cam.location - CENTER
    cam.location = CENTER + offset * factor
    # slight lens widen if camera data exists
    if cam.type == "CAMERA" and cam.data:
        if cam.data.type == "PERSP":
            cam.data.lens = max(24.0, min(cam.data.lens * 0.95, 50.0))
        elif cam.data.type == "ORTHO":
            cam.data.ortho_scale = cam.data.ortho_scale * 1.06
    print("CAM", name, [round(v, 2) for v in cam.location])

# Bounds check only (no geometry change)
minx = miny = minz = 1e9
maxx = maxy = maxz = -1e9
SKIP = {"PRES_GROUND", "SCALE_HUMAN"}
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render or o.name in SKIP:
        continue
    for corner in o.bound_box:
        w = o.matrix_world @ Vector(corner)
        minx = min(minx, w.x); maxx = max(maxx, w.x)
        miny = min(miny, w.y); maxy = max(maxy, w.y)
        minz = min(minz, w.z); maxz = max(maxz, w.z)
print("BOUNDS", round(maxx-minx,2), round(maxy-miny,2), round(maxz-minz,2), "Z", round(minz,2), round(maxz,2))

scene = bpy.context.scene
try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except Exception:
    try:
        scene.render.engine = "BLENDER_EEVEE"
    except Exception:
        scene.render.engine = "CYCLES"
scene.render.resolution_x = 1280
scene.render.resolution_y = 960

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V41_CAM.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V41")

out_final = os.path.join(BASE, "renders_final")
out_work = os.path.join(BASE, "renders_pass1d")
for d in (out_final, out_work):
    os.makedirs(d, exist_ok=True)

jobs = [
    ("CAM_01_FRONT", out_work, "current_front_work.png"),
    ("CAM_05_FRONT_3Q", out_work, "current_front_3q_work.png"),
    ("CAM_06_REAR_3Q", out_work, "current_rear_3q_work.png"),
    ("CAM_TOP_PLAN", out_work, "current_top_plan_work.png"),
    ("CAM_01_FRONT", out_final, "final_front.png"),
    ("CAM_05_FRONT_3Q", out_final, "final_front_3q.png"),
    ("CAM_02_REAR", out_final, "final_rear.png"),
    ("CAM_03_LEFT", out_final, "final_left.png"),
    ("CAM_04_RIGHT", out_final, "final_right.png"),
    ("CAM_06_REAR_3Q", out_final, "final_rear_3q.png"),
    ("CAM_TOP_PLAN", out_final, "final_top.png"),
]
for cam, dest, fn in jobs:
    c = bpy.data.objects.get(cam)
    if not c:
        continue
    scene.camera = c
    scene.render.filepath = os.path.join(dest, fn)
    bpy.ops.render.render(write_still=True)
    print("OK", fn)

print("TICK63_SCRIPT_READY")

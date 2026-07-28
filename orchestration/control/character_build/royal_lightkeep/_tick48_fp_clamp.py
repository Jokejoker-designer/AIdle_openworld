# -*- coding: utf-8 -*-
"""Tick #48 P0: hard footprint clamp back to 24x19x38. Scale lock restore."""
import bpy
import os
import shutil
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V25_TURRETS.blend")
LOOP = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bpy.ops.wm.open_mainfile(filepath=WORK)
print("OPEN", bpy.data.filepath)

backup = os.path.join(BASE, f"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_BACKUP_LOOP_{STAMP}.blend")
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True)
print("BACKUP", backup)

# Target envelope (centered near CX=1, CY=1.5 → X -11..13? sheet is 24 wide → X span 24)
# Use absolute world box: X in [-11.5, 12.5], Y in [-8.5, 10.5] ≈ 24x19 around CX~0.5 CY~1
X_MIN, X_MAX = -11.5, 12.5  # span 24.0
Y_MIN, Y_MAX = -8.5, 10.5   # span 19.0
H_MAX = 38.2
SKIP = {"PRES_GROUND", "LEVEL0_GROUND", "SCALE_HUMAN"}

# Shrink/move objects that violate envelope
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name in SKIP:
        continue
    bpy.context.view_layer.update()
    corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
    minx = min(c.x for c in corners); maxx = max(c.x for c in corners)
    miny = min(c.y for c in corners); maxy = max(c.y for c in corners)
    # translate inward first
    if minx < X_MIN:
        o.location.x += (X_MIN - minx)
    if maxx > X_MAX:
        o.location.x += (X_MAX - maxx)
    if miny < Y_MIN:
        o.location.y += (Y_MIN - miny)
    if maxy > Y_MAX:
        o.location.y += (Y_MAX - maxy)
    bpy.context.view_layer.update()
    # if still oversized, scale down XY
    corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
    minx = min(c.x for c in corners); maxx = max(c.x for c in corners)
    miny = min(c.y for c in corners); maxy = max(c.y for c in corners)
    w = maxx - minx; d = maxy - miny
    sx = 1.0; sy = 1.0
    if w > 23.8:
        sx = 23.8 / w
    if d > 18.8:
        sy = 18.8 / d
    if sx < 1.0 or sy < 1.0:
        o.scale.x *= sx
        o.scale.y *= sy
        bpy.context.view_layer.update()
        # re-center into box
        corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
        minx = min(c.x for c in corners); maxx = max(c.x for c in corners)
        miny = min(c.y for c in corners); maxy = max(c.y for c in corners)
        if minx < X_MIN:
            o.location.x += (X_MIN - minx)
        if maxx > X_MAX:
            o.location.x += (X_MAX - maxx)
        if miny < Y_MIN:
            o.location.y += (Y_MIN - miny)
        if maxy > Y_MAX:
            o.location.y += (Y_MAX - maxy)

# Height clamp
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    top = o.location.z + o.dimensions.z / 2.0
    if top > H_MAX:
        o.location.z -= (top - H_MAX)

# Second pass translate clamp (post-scale)
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render or o.name in SKIP:
        continue
    corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
    minx = min(c.x for c in corners); maxx = max(c.x for c in corners)
    miny = min(c.y for c in corners); maxy = max(c.y for c in corners)
    if minx < X_MIN:
        o.location.x += (X_MIN - minx)
    if maxx > X_MAX:
        o.location.x += (X_MAX - maxx)
    if miny < Y_MIN:
        o.location.y += (Y_MIN - miny)
    if maxy > Y_MAX:
        o.location.y += (Y_MAX - maxy)

# Tighten plinth/bastion/turret specifically if present
for name in list(bpy.data.objects.keys()):
    o = bpy.data.objects.get(name)
    if not o or o.type != "MESH":
        continue
    if name.startswith(("PLINTH_", "BASTION_", "TURRET_BODY", "TURRET_ROOF")):
        corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
        minx = min(c.x for c in corners); maxx = max(c.x for c in corners)
        miny = min(c.y for c in corners); maxy = max(c.y for c in corners)
        if minx < X_MIN:
            o.location.x += (X_MIN - minx + 0.05)
        if maxx > X_MAX:
            o.location.x += (X_MAX - maxx - 0.05)
        if miny < Y_MIN:
            o.location.y += (Y_MIN - miny + 0.05)
        if maxy > Y_MAX:
            o.location.y += (Y_MAX - maxy - 0.05)

bpy.context.view_layer.update()
minx = miny = minz = 1e9
maxx = maxy = maxz = -1e9
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render or o.name in SKIP:
        continue
    for corner in o.bound_box:
        w = o.matrix_world @ Vector(corner)
        minx = min(minx, w.x); maxx = max(maxx, w.x)
        miny = min(miny, w.y); maxy = max(maxy, w.y)
        minz = min(minz, w.z); maxz = max(maxz, w.z)
print("BOUNDS", round(maxx-minx,2), round(maxy-miny,2), round(maxz-minz,2), "Z", round(minz,2), round(maxz,2))
print("RAW", round(minx,2), round(maxx,2), round(miny,2), round(maxy,2))

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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V26_CLAMP.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V26")

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

print("TICK48_SCRIPT_READY")

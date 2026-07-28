# -*- coding: utf-8 -*-
"""Tick #70: inventory + deviation snapshot after string pass. Re-render only."""
import bpy
import os
import shutil
from datetime import datetime
from mathutils import Vector
from collections import Counter

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V47_STRING.blend")
LOOP = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bpy.ops.wm.open_mainfile(filepath=WORK)
print("OPEN", bpy.data.filepath)

backup = os.path.join(BASE, f"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_BACKUP_LOOP_{STAMP}.blend")
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True)
print("BACKUP", backup)

meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.hide_render]
cams = [o for o in bpy.data.objects if o.type == "CAMERA"]
lights = [o for o in bpy.data.objects if o.type == "LIGHT"]
beveled = sum(1 for o in meshes if any(m.type == "BEVEL" for m in o.modifiers))

pref = Counter()
for o in meshes:
    pref[o.name.split("_")[0]] += 1

SKIP = {"PRES_GROUND", "SCALE_HUMAN"}
minx = miny = minz = 1e9
maxx = maxy = maxz = -1e9
for o in meshes:
    if o.name in SKIP:
        continue
    for corner in o.bound_box:
        w = o.matrix_world @ Vector(corner)
        minx = min(minx, w.x); maxx = max(maxx, w.x)
        miny = min(miny, w.y); maxy = max(maxy, w.y)
        minz = min(minz, w.z); maxz = max(maxz, w.z)
bw, bd, bh = maxx - minx, maxy - miny, maxz - minz
print("BOUNDS", round(bw, 2), round(bd, 2), round(bh, 2))
print("MESHES", len(meshes), "BEVEL", beveled, "CAMS", len(cams), "LIGHTS", len(lights))

top = pref.most_common(15)
with open(os.path.join(BASE, "INTERMEDIATE_DEVIATION_REPORT.md"), "w", encoding="utf-8") as f:
    f.write(f"""# INTERMEDIATE DEVIATION REPORT — tick #70

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V48_SNAP2 / PASS1D
**ASSET_FINAL_COMPLETE:** false
**accepted (user):** false

## Inventory
- Mesh objects (visible): **{len(meshes)}**
- With Bevel modifier: **{beveled}**
- Cameras: **{len(cams)}** · Lights: **{len(lights)}**
- Top prefixes: {", ".join(f"{k}:{v}" for k, v in top)}

## Sheet targets
- Footprint 24×19 m · Height 38 m · Wall 6.5 m
- Achieved: **{bw:.2f}×{bd:.2f}×{bh:.2f}** m · Z {minz:.2f}..{maxz:.2f}

## Matches
- Scale lock near sheet
- Tower setbacks, fort wall 6.5, portal, gallery, arcade, merlons
- Hip ridges, dormers, flags, paving, sills/lintels, string courses
- Bevel soft edges on structural masses
- Presentation cameras + lights + scale human

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Geometry still modular box — not carved gothic of sheet |
| D2 | P1 | Roof surfaces approximate, not continuous organic form |
| D3 | P2 | Tracery/opening density still below full sheet fidelity |
| D4 | P2 | No vegetation / true ground dressing |
| D5 | P3 | UV/LOD not authored |

## Overall ~7.85 — not FINAL until Human overlay
Modular plateau remains. Next value needs mesh-language change (boolean carve / sculpt), not more cubes.
""")
print("WROTE_DEVIATION")

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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V48_SNAP2.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V48")

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

print("TICK70_SCRIPT_READY")

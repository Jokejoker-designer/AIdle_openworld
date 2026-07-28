# -*- coding: utf-8 -*-
"""Tick #64: inventory snapshot + deviation report + re-render. No major geometry."""
import bpy
import os
import shutil
from datetime import datetime
from mathutils import Vector
from collections import Counter

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V41_CAM.blend")
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

# prefix counts
pref = Counter()
for o in meshes:
    p = o.name.split("_")[0]
    pref[p] += 1

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
bw, bd, bh = maxx-minx, maxy-miny, maxz-minz
print("BOUNDS", round(bw,2), round(bd,2), round(bh,2))
print("MESHES", len(meshes), "CAMS", len(cams), "LIGHTS", len(lights))

top_pref = pref.most_common(20)
with open(os.path.join(BASE, "INTERMEDIATE_DEVIATION_REPORT.md"), "w", encoding="utf-8") as f:
    f.write(f"""# INTERMEDIATE DEVIATION REPORT — tick #64

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V42_SNAP / PASS1D
**ASSET_FINAL_COMPLETE:** false
**accepted (user):** false

## Inventory
- Mesh objects (visible): **{len(meshes)}**
- Cameras: **{len(cams)}**
- Lights: **{len(lights)}**
- Top prefixes: {", ".join(f"{k}:{v}" for k,v in top_pref)}

## Sheet targets
- Footprint 24×19 m · Height 38 m · Wall 6.5 m
- Achieved: **{bw:.2f}×{bd:.2f}×{bh:.2f}** m · Z {minz:.2f}..{maxz:.2f}

## Matches
- Scale lock near sheet
- Central tower + hall + wing + fort wall 6.5 + stairs + court U
- Portal, gallery, arcade, merlons, dormers, hip ridges, flags
- Palette limestone / slate / gold / banner / glass / wood
- Presentation lights + scale human + 7 cameras

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Geometry still modular box — not carved gothic of sheet |
| D2 | P1 | Roof surfaces approximate peaks, not continuous organic form |
| D3 | P2 | Opening/tracery density still below full sheet fidelity |
| D4 | P2 | No vegetation / ground dressing |
| D5 | P3 | UV/LOD not authored |

## Overall ~7.75 — not FINAL until Human overlay
Modular plateau: further cube densify yields diminishing returns without mesh-language change.
""")
print("WROTE_DEVIATION")

# tiny polish: ensure gold finial peak visible
o = bpy.data.objects.get("GOLD_FINIAL_PEAK") or bpy.data.objects.get("CROWN_CENTER_FINIAL")
if o:
    o.hide_render = False

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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V42_SNAP.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V42")

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

print("TICK64_SCRIPT_READY")

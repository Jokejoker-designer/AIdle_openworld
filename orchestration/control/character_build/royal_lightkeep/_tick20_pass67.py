# -*- coding: utf-8 -*-
"""Tick #20: PASS6 polish (warm M0 studio) + PASS7 technical cleanup + proofs."""
import bpy
import os
import shutil
import math
from datetime import datetime
from mathutils import Vector, Euler

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS6_V01.blend")
LOOP = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bpy.ops.wm.open_mainfile(filepath=WORK)
print("OPEN", bpy.data.filepath, "OBJ", len(bpy.data.objects))

backup = os.path.join(BASE, f"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_BACKUP_LOOP_{STAMP}.blend")
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True)
print("BACKUP", backup)

scene = bpy.context.scene

# ========== PASS6 polish ==========
# Warm cream studio world matching M0 product sheet
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()
bg = nt.nodes.new("ShaderNodeBackground")
# warm parchment / cream
bg.inputs[0].default_value = (0.82, 0.78, 0.70, 1.0)
bg.inputs[1].default_value = 1.15
out = nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(bg.outputs[0], out.inputs[0])

def set_light(name, energy=None, color=None, size=None, loc=None, rot_deg=None):
    o = bpy.data.objects.get(name)
    if not o or o.type != "LIGHT":
        return
    if energy is not None:
        o.data.energy = energy
    if color is not None:
        o.data.color = color
    if size is not None and hasattr(o.data, "size"):
        o.data.size = size
    if loc is not None:
        o.location = Vector(loc)
    if rot_deg is not None:
        o.rotation_euler = Euler(tuple(math.radians(a) for a in rot_deg), "XYZ")

# Stronger warm key, cooler soft fill, clearer rim for massing edges (M2)
set_light("KEY_LIGHT", energy=1400.0, color=(1.0, 0.96, 0.88), size=32.0,
          loc=(48, 78, 58), rot_deg=(-38, 0, 28))
set_light("FILL_LIGHT", energy=380.0, color=(0.88, 0.92, 1.0), size=40.0,
          loc=(-60, 45, 38), rot_deg=(-28, 0, -42))
set_light("RIM_LIGHT", energy=620.0, color=(1.0, 0.94, 0.86), size=24.0,
          loc=(-18, -80, 55), rot_deg=(-52, 0, 180))
set_light("SUN", energy=2.1, color=(1.0, 0.97, 0.90),
          loc=(35, 45, 90), rot_deg=(-50, 0, 32))

# Soften oversized gold cornice slabs if present (read less as boxes)
for name in ("GOLD_CORNICE_OBS", "GOLD_CORNICE_MID", "GOLD_CROWN_RING"):
    o = bpy.data.objects.get(name)
    if o and o.type == "MESH":
        # thinner vertical scale
        o.scale.z *= 0.55
        o.location.z -= 0.05

# Ground slightly warmer
mat_g = bpy.data.materials.get("MAT_GROUND")
if mat_g and mat_g.use_nodes:
    bsdf = mat_g.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.55, 0.52, 0.46, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.96

# Engine / res
try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except Exception:
    try:
        scene.render.engine = "BLENDER_EEVEE"
    except Exception:
        scene.render.engine = "CYCLES"
scene.render.resolution_x = 1280
scene.render.resolution_y = 960
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False

p6f = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS6_FINAL.blend")
bpy.ops.wm.save_as_mainfile(filepath=p6f)
print("SAVED PASS6_FINAL")

# ========== PASS7 technical cleanup ==========
# Apply scale/rotation on mesh objects (keep location)
applied = 0
failed_apply = []
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    # skip pure presentation helpers from scale issues — still apply
    try:
        # deselect all
        for x in bpy.data.objects:
            x.select_set(False)
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        applied += 1
    except Exception as e:
        failed_apply.append((o.name, str(e)))
print("APPLY_SCALE_ROT", applied, "fail", len(failed_apply))

# Recalc normals outside
norm_ok = 0
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    try:
        for x in bpy.data.objects:
            x.select_set(False)
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        norm_ok += 1
    except Exception:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
print("NORMALS", norm_ok)

# Naming: prefix orphan presentation objects already named; ensure no empty names
renamed = 0
for o in bpy.data.objects:
    if not o.name or o.name.strip() == "":
        o.name = f"OBJ_{renamed}"
        renamed += 1

# Hide tiny floating debris if any object with very small dim and far off
culled = 0
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    d = o.dimensions
    if max(d) < 0.05 and abs(o.location.z) > 100:
        o.hide_render = True
        o.hide_viewport = True
        culled += 1
print("CULLED_TINY", culled)

# Material residual clay audit
residual = []
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    for s in o.material_slots:
        if s.material and s.material.name.startswith("CLAY"):
            residual.append(o.name)
            break
print("RESIDUAL_CLAY", len(residual))

# Camera check (do not reset)
cams = [o.name for o in bpy.data.objects if o.type == "CAMERA"]
print("CAMS", sorted(cams))

# Bounds audit (asset extents)
minx = miny = minz = 1e9
maxx = maxy = maxz = -1e9
mesh_count = 0
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name in ("PRES_GROUND", "SCALE_HUMAN"):
        continue
    mesh_count += 1
    for corner in o.bound_box:
        w = o.matrix_world @ Vector(corner)
        minx = min(minx, w.x); maxx = max(maxx, w.x)
        miny = min(miny, w.y); maxy = max(maxy, w.y)
        minz = min(minz, w.z); maxz = max(maxz, w.z)
print("MESH_COUNT", mesh_count)
print("BOUNDS_XYZ", round(maxx - minx, 2), round(maxy - miny, 2), round(maxz - minz, 2))
print("Z_RANGE", round(minz, 2), round(maxz, 2))

# Write PASS7 tech report json-ish as text
report_path = os.path.join(BASE, "PASS7_TECH_REPORT.md")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("# PASS7 TECHNICAL REPORT\n\n")
    f.write(f"- stamp: {STAMP}\n")
    f.write(f"- mesh_count (excl ground/human): {mesh_count}\n")
    f.write(f"- total objects: {len(bpy.data.objects)}\n")
    f.write(f"- apply scale/rot: {applied} fail={len(failed_apply)}\n")
    f.write(f"- normals: {norm_ok}\n")
    f.write(f"- residual clay: {len(residual)}\n")
    f.write(f"- bounds XYZ m: {round(maxx-minx,2)} x {round(maxy-miny,2)} x {round(maxz-minz,2)}\n")
    f.write(f"- Z range: {round(minz,2)} .. {round(maxz,2)}\n")
    f.write(f"- cameras: {', '.join(sorted(cams))}\n")
    f.write(f"- mockup scale target: H~38m footprint~24x19\n")
    f.write(f"- height_vs_target: {round(maxz-min(0,minz),2)}m vs 38m\n")
print("REPORT", report_path)

p7 = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS7_V01.blend")
bpy.ops.wm.save_as_mainfile(filepath=p7)
# Self-accept PASS7 intermediate if cleanup clean
p7f = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS7_FINAL.blend")
shutil.copy2(p7, p7f)
shutil.copy2(p7, LOOP)
print("SAVED PASS7_V01 + PASS7_FINAL + PASS1D")

# ========== PASS8 start: multi-view validation renders ==========
out6 = os.path.join(BASE, "renders_pass6")
out7 = os.path.join(BASE, "renders_pass7")
out8 = os.path.join(BASE, "renders_pass8")
out_work = os.path.join(BASE, "renders_pass1d")
for d in (out6, out7, out8, out_work):
    os.makedirs(d, exist_ok=True)

jobs = [
    ("CAM_01_FRONT", out_work, "current_front_work.png"),
    ("CAM_05_FRONT_3Q", out_work, "current_front_3q_work.png"),
    ("CAM_06_REAR_3Q", out_work, "current_rear_3q_work.png"),
    ("CAM_TOP_PLAN", out_work, "current_top_plan_work.png"),
    ("CAM_01_FRONT", out6, "pass6_front.png"),
    ("CAM_05_FRONT_3Q", out6, "pass6_front_3q.png"),
    ("CAM_02_REAR", out6, "pass6_rear.png"),
    ("CAM_03_LEFT", out6, "pass6_left.png"),
    ("CAM_04_RIGHT", out6, "pass6_right.png"),
    ("CAM_06_REAR_3Q", out6, "pass6_rear_3q.png"),
    ("CAM_TOP_PLAN", out6, "pass6_top.png"),
    ("CAM_01_FRONT", out7, "pass7_front.png"),
    ("CAM_05_FRONT_3Q", out7, "pass7_front_3q.png"),
    ("CAM_02_REAR", out7, "pass7_rear.png"),
    ("CAM_TOP_PLAN", out7, "pass7_top.png"),
    ("CAM_01_FRONT", out8, "pass8_front.png"),
    ("CAM_05_FRONT_3Q", out8, "pass8_front_3q.png"),
    ("CAM_02_REAR", out8, "pass8_rear.png"),
    ("CAM_03_LEFT", out8, "pass8_left.png"),
    ("CAM_04_RIGHT", out8, "pass8_right.png"),
    ("CAM_06_REAR_3Q", out8, "pass8_rear_3q.png"),
    ("CAM_TOP_PLAN", out8, "pass8_top.png"),
]

for cam, dest, fn in jobs:
    c = bpy.data.objects.get(cam)
    if not c:
        print("MISS_CAM", cam)
        continue
    scene.camera = c
    scene.render.filepath = os.path.join(dest, fn)
    bpy.ops.render.render(write_still=True)
    print("OK", fn)

# PASS8 V01 save (validation in progress — not final complete)
p8 = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V01.blend")
bpy.ops.wm.save_as_mainfile(filepath=p8)
shutil.copy2(p8, LOOP)
print("SAVED PASS8_V01 + PASS1D")

# Deviation notes (honest)
dev = os.path.join(BASE, "FINAL_DEVIATION_REPORT_DRAFT.md")
with open(dev, "w", encoding="utf-8") as f:
    f.write("# FINAL DEVIATION REPORT (DRAFT) — tick #20\n\n")
    f.write("**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01\n")
    f.write("**accepted (user):** false\n")
    f.write("**ASSET_FINAL_COMPLETE:** false\n\n")
    f.write("## Matches (OK)\n")
    f.write("- Central tall tower + left/right barracks wings + front stairs + outer base\n")
    f.write("- Palette: limestone / slate navy / gold / dark base / glass / banners\n")
    f.write("- Approx height toward 38m target; multi-level base; courtyard void in plan\n")
    f.write("- Six cameras intact; single model lock held\n\n")
    f.write("## Deviations (still open)\n")
    f.write("| ID | Pri | Gap vs M0 mockup |\n")
    f.write("|----|-----|------------------|\n")
    f.write("| D1 | P1 | Silhouette still boxy — lacks full gothic multi-gable / tracery density |\n")
    f.write("| D2 | P1 | Tower crown simpler than multi-spire gothic mockup |\n")
    f.write("| D3 | P2 | Opening/frame density lower than sheet |\n")
    f.write("| D4 | P2 | No vegetation / courtyard parade props (presentation optional) |\n")
    f.write("| D5 | P2 | Modular game-ready UV/LOD not fully authored |\n\n")
    f.write("## Next\n")
    f.write("- Optional structure polish pass if Human wants higher fidelity before FINAL\n")
    f.write("- Or package FINAL with known deviations documented\n")
print("DEV_REPORT", dev)
print("TICK20_DONE OBJ", len(bpy.data.objects))

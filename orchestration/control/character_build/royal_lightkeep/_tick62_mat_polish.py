# -*- coding: utf-8 -*-
"""Tick #62: material contrast polish across scene. Scale lock 24x19x38."""
import bpy
import os
import shutil
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V39_FLAGS.blend")
LOOP = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bpy.ops.wm.open_mainfile(filepath=WORK)
print("OPEN", bpy.data.filepath)

backup = os.path.join(BASE, f"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_BACKUP_LOOP_{STAMP}.blend")
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True)
print("BACKUP", backup)

def make_mat(name, color, rough=0.7, metal=0.0):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    if m.use_nodes:
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*color, 1.0)
            bsdf.inputs["Roughness"].default_value = rough
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = metal
    return m

# Refresh palette with stronger contrast
MAT_STONE = make_mat("MAT_LIMESTONE", (0.82, 0.78, 0.70), 0.78, 0.0)
MAT_DARK = make_mat("MAT_FOUNDATION_DARK", (0.18, 0.16, 0.14), 0.90, 0.0)
MAT_ROOF = make_mat("MAT_SLATE_NAVY", (0.08, 0.12, 0.26), 0.45, 0.05)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.90, 0.68, 0.22), 0.22, 0.95)
MAT_GLASS = make_mat("MAT_GLASS", (0.40, 0.55, 0.75), 0.08, 0.0)
MAT_BANNER = make_mat("MAT_BANNER_BLUE", (0.05, 0.10, 0.38), 0.55, 0.0)
MAT_WOOD = make_mat("MAT_WOOD", (0.38, 0.24, 0.12), 0.70, 0.0)

def assign_prefix(prefixes, mat):
    n = 0
    for o in bpy.data.objects:
        if o.type != "MESH" or o.hide_render:
            continue
        if any(o.name.startswith(p) for p in prefixes):
            if o.data.materials:
                o.data.materials[0] = mat
            else:
                o.data.materials.append(mat)
            n += 1
    return n

# Prefix → material map
c1 = assign_prefix(("WALL65_", "MERLON_", "WMERLON_", "BUTT", "ARCADE_PIER", "ARCADE_LINT", "ARCADE_ENTAB",
                    "PORTAL_ARCH", "PORTAL_COL", "GALLERY_FLOOR", "GALLERY_POST", "PLINTH_L2", "COURT_U_",
                    "MAIN_STAIR", "BASTION_", "TURRET_BODY"), MAT_STONE)
c2 = assign_prefix(("PLINTH_L0", "PLINTH_L1", "COURT_FLOOR", "PORTAL_VOID", "OGATE_VOID", "GALLERY_VOID",
                    "GALLERY_ROOF", "ARCADE_VOID", "WALL65_CAP"), MAT_DARK)
c3 = assign_prefix(("HIP_", "CROWN_RIDGE", "CROWN_GABLE", "CROWN_CENTER_SPIRE", "CROWN_EDGE", "HALL_ROOF",
                    "WING_ROOF", "DORM2_", "TURRET_ROOF", "CROWN_"), MAT_ROOF)
c4 = assign_prefix(("GOLD_", "MAT_GOLD", "TRACERY_", "EMBLEM_", "PORTAL_GOLD", "PORTAL_CAP", "PORTAL_ROSE_FRAME",
                    "STAIR_CAP", "GALLERY_GOLD", "FLAG_POLE", "CROWN_FLAG_POLE", "GATE_FINIAL", "HIP_GOLD",
                    "ARCADE_KEY", "WIN_FRAME", "TFR_", "BANNER_POLE", "MERLON_GOLD"), MAT_GOLD)
c5 = assign_prefix(("WIN_", "TWIN_", "GLASS", "PORTAL_ROSE_GLASS", "HALL_SIDE_L_WIN", "WING_SIDE_R_WIN",
                    "HALL_FRONT_WIN", "HALL_REAR_WIN", "TURRET_WIN", "DORM2_HALL_WIN", "DORM2_WING_WIN",
                    "TOWER_WIN"), MAT_GLASS)
c6 = assign_prefix(("BANNER_", "FLAG_CLOTH", "CROWN_FLAG_", "EMBLEM_FRONT_CORE"), MAT_BANNER)
c7 = assign_prefix(("PORTAL_DOOR", "GATE_THRESH", "GALLERY_RAIL"), MAT_WOOD)

print("ASSIGN", c1, c2, c3, c4, c5, c6, c7)

# Soft envelope recheck
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
SKIP = {"PRES_GROUND", "LEVEL0_GROUND", "SCALE_HUMAN"}
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
    top = o.location.z + o.dimensions.z / 2.0
    if top > H_MAX:
        o.location.z -= (top - H_MAX)

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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V40_MAT.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V40")

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

print("TICK62_SCRIPT_READY")

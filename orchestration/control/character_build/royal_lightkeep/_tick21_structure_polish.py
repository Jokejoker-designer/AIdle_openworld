# -*- coding: utf-8 -*-
"""Tick #21: P1 structure polish — tower crown density + wing multi-gable roofs + stair read."""
import bpy
import os
import shutil
import math
import bmesh
from datetime import datetime
from mathutils import Vector, Euler

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V01.blend")
LOOP = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bpy.ops.wm.open_mainfile(filepath=WORK)
print("OPEN", bpy.data.filepath, "OBJ", len(bpy.data.objects))

backup = os.path.join(BASE, f"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_BACKUP_LOOP_{STAMP}.blend")
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True)
print("BACKUP", backup)

def mesh_local_size(obj):
    me = obj.data
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    return Vector((max(xs) - min(xs) or 1e-6, max(ys) - min(ys) or 1e-6, max(zs) - min(zs) or 1e-6))

def set_size(obj, sx, sy, sz, bottom_z=None, center_xy=None):
    loc = mesh_local_size(obj)
    obj.scale = Vector((sx / loc.x, sy / loc.y, sz / loc.z))
    bpy.context.view_layer.update()
    if center_xy is not None:
        obj.location.x, obj.location.y = center_xy
    if bottom_z is not None:
        # after scale, dimensions.z should be ~sz
        obj.location.z = bottom_z + obj.dimensions.z / 2.0

def ensure_cube(name):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        o.hide_viewport = False
        return o
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(o)
    return o

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
    m.diffuse_color = (*color, 1.0)
    return m

def assign(obj, mat):
    if not obj or obj.type != "MESH":
        return
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

MAT_STONE = make_mat("MAT_LIMESTONE", (0.78, 0.74, 0.66), 0.82, 0.0)
MAT_DARK = make_mat("MAT_DARK_STONE", (0.22, 0.21, 0.20), 0.92, 0.0)
MAT_ROOF = make_mat("MAT_SLATE_NAVY", (0.10, 0.16, 0.30), 0.50, 0.04)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.82, 0.62, 0.24), 0.28, 0.90)
MAT_GLASS = make_mat("MAT_GLASS", (0.45, 0.58, 0.72), 0.12, 0.0)

CX, CY = 1.5, 5.0

# ========== 1) TOWER CROWN — taller multi-spire gothic silhouette ==========
# Hip layers (stepped crown reading)
set_size(ensure_cube("TOWER_HIP_BASE"), 13.0, 13.0, 1.6, bottom_z=32.6, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_HIP_BASE"], MAT_ROOF)

set_size(ensure_cube("TOWER_HIP_EW"), 13.2, 5.0, 3.6, bottom_z=33.4, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_HIP_EW"], MAT_ROOF)

# NS hip bar (new if missing)
o = ensure_cube("TOWER_HIP_NS")
set_size(o, 5.0, 13.2, 3.6, bottom_z=33.4, center_xy=(CX, CY))
assign(o, MAT_ROOF)

# Main roof block + peak
set_size(ensure_cube("TOWER_ROOF_BLOCK"), 7.5, 7.5, 2.8, bottom_z=35.4, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_ROOF_BLOCK"], MAT_ROOF)
set_size(ensure_cube("TOWER_ROOF_PEAK"), 3.2, 3.2, 2.6, bottom_z=37.6, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_ROOF_PEAK"], MAT_ROOF)

# Corner corner masses + tall conical-ish spires (taller than before)
corners = [
    ("TOWER_CORNER_MASS_0", "TOWER_SPIRE_0", "TOWER_CORNER_CAP_0", -4.2, -0.7),
    ("TOWER_CORNER_MASS_1", "TOWER_SPIRE_1", "TOWER_CORNER_CAP_1", 7.2, -0.7),
    ("TOWER_CORNER_MASS_2", "TOWER_SPIRE_2", "TOWER_CORNER_CAP_2", -4.2, 10.7),
    ("TOWER_CORNER_MASS_3", "TOWER_SPIRE_3", "TOWER_CORNER_CAP_3", 7.2, 10.7),
]
for mass, spire, cap, x, y in corners:
    set_size(ensure_cube(mass), 3.2, 3.2, 4.5, bottom_z=32.0, center_xy=(x, y))
    assign(bpy.data.objects[mass], MAT_STONE)
    set_size(ensure_cube(spire), 2.0, 2.0, 5.5, bottom_z=35.5, center_xy=(x, y))
    assign(bpy.data.objects[spire], MAT_ROOF)
    set_size(ensure_cube(cap), 1.3, 1.3, 2.2, bottom_z=40.2, center_xy=(x, y))
    assign(bpy.data.objects[cap], MAT_ROOF)
    # gold tip
    tip = ensure_cube(f"GOLD_SPIRE_TIP_{mass[-1]}")
    set_size(tip, 0.35, 0.35, 1.1, bottom_z=42.0, center_xy=(x, y))
    assign(tip, MAT_GOLD)

# Mid crown peaks ring — taller pointed volumes
peak_xy = [
    (CX, CY + 3.4), (CX, CY - 3.4), (CX + 3.4, CY), (CX - 3.4, CY),
    (CX + 2.4, CY + 2.4), (CX - 2.4, CY + 2.4), (CX + 2.4, CY - 2.4), (CX - 2.4, CY - 2.4),
]
for i, (px, py) in enumerate(peak_xy):
    name = f"TOWER_CROWN_PEAK_{i}"
    set_size(ensure_cube(name), 1.8, 1.8, 3.2, bottom_z=35.0, center_xy=(px, py))
    assign(bpy.data.objects[name], MAT_ROOF)

# Front twin spires (mockup twin front turrets on crown)
set_size(ensure_cube("TOWER_FRONT_SPIRE_L"), 2.2, 2.2, 4.0, bottom_z=34.5, center_xy=(CX - 3.0, CY + 4.5))
assign(bpy.data.objects["TOWER_FRONT_SPIRE_L"], MAT_ROOF)
set_size(ensure_cube("TOWER_FRONT_SPIRE_R"), 2.2, 2.2, 4.0, bottom_z=34.5, center_xy=(CX + 3.0, CY + 4.5))
assign(bpy.data.objects["TOWER_FRONT_SPIRE_R"], MAT_ROOF)

# Cardinal gables — larger
for name, x, y, sx, sy in [
    ("TOWER_GABLE_FRONT", CX, CY + 5.2, 4.5, 2.2),
    ("TOWER_GABLE_REAR", CX, CY - 5.2, 4.5, 2.2),
    ("TOWER_GABLE_LEFT", CX - 5.2, CY, 2.2, 4.5),
    ("TOWER_GABLE_RIGHT", CX + 5.2, CY, 2.2, 4.5),
]:
    set_size(ensure_cube(name), sx, sy, 3.5, bottom_z=33.8, center_xy=(x, y))
    assign(bpy.data.objects[name], MAT_ROOF)

# Central gold finial stack
set_size(ensure_cube("GOLD_FINIAL_PEAK"), 0.5, 0.5, 1.8, bottom_z=39.8, center_xy=(CX, CY))
assign(bpy.data.objects["GOLD_FINIAL_PEAK"], MAT_GOLD)
set_size(ensure_cube("FINIAL_MAIN"), 0.35, 0.35, 1.6, bottom_z=41.2, center_xy=(CX, CY))
assign(bpy.data.objects["FINIAL_MAIN"], MAT_GOLD)

# ========== 2) LEFT BARRACKS — more multi-gable roof density ==========
# Raise ridge + extra dormers along front eave
set_size(ensure_cube("BARRACKS_LEFT_ROOF"), 23.5, 11.5, 4.8, bottom_z=14.2, center_xy=(-13.0, 2.0))
assign(bpy.data.objects["BARRACKS_LEFT_ROOF"], MAT_ROOF)
set_size(ensure_cube("BARRACKS_RIDGE_CORE"), 20.0, 2.2, 2.4, bottom_z=18.2, center_xy=(-13.0, 2.0))
assign(bpy.data.objects["BARRACKS_RIDGE_CORE"], MAT_ROOF)

# Front-facing gable dormers (mockup multi-gable)
gable_xs = [-21.0, -17.5, -14.0, -10.5, -7.0]
for i, gx in enumerate(gable_xs):
    name = f"BARRACKS_ROOF_GABLE_{i}"
    set_size(ensure_cube(name), 3.2, 5.5, 3.8, bottom_z=17.2, center_xy=(gx, 5.5))
    assign(bpy.data.objects[name], MAT_ROOF)
    # small peak cap
    cap = ensure_cube(f"BARRACKS_GABLE_CAP_{i}")
    set_size(cap, 1.4, 1.4, 1.6, bottom_z=20.6, center_xy=(gx, 5.5))
    assign(cap, MAT_ROOF)

# Gold eaves line
set_size(ensure_cube("GOLD_EAVES_BAR_F"), 22.5, 0.25, 0.28, bottom_z=14.35, center_xy=(-13.0, 7.0))
assign(bpy.data.objects["GOLD_EAVES_BAR_F"], MAT_GOLD)

# ========== 3) RIGHT WING — multi-gable + pavilion peak ==========
set_size(ensure_cube("RIGHT_WING_ROOF"), 14.5, 12.0, 4.5, bottom_z=14.0, center_xy=(14.0, -1.0))
assign(bpy.data.objects["RIGHT_WING_ROOF"], MAT_ROOF)

right_gables = [
    ("RIGHT_ROOF_GABLE_0", 10.0, 2.5, 3.4, 4.2, 3.4),
    ("RIGHT_ROOF_GABLE_1", 14.5, 1.8, 3.4, 4.2, 3.4),
    ("RIGHT_ROOF_GABLE_2", 12.5, -4.0, 3.4, 4.2, 3.4),
    ("RIGHT_ROOF_GABLE_3", 16.5, -2.5, 3.4, 4.2, 3.4),
]
for name, x, y, sx, sy, sz in right_gables:
    set_size(ensure_cube(name), sx, sy, sz, bottom_z=16.8, center_xy=(x, y))
    assign(bpy.data.objects[name], MAT_ROOF)

# Pavilion taller peak
set_size(ensure_cube("RIGHT_PAVILION_ROOF"), 10.5, 10.5, 4.5, bottom_z=14.5, center_xy=(16.0, -6.0))
assign(bpy.data.objects["RIGHT_PAVILION_ROOF"], MAT_ROOF)
set_size(ensure_cube("RIGHT_PAVILION_PEAK"), 3.0, 3.0, 2.8, bottom_z=18.5, center_xy=(16.0, -6.0))
assign(bpy.data.objects["RIGHT_PAVILION_PEAK"], MAT_ROOF)
pav_tip = ensure_cube("GOLD_PAVILION_TIP")
set_size(pav_tip, 0.4, 0.4, 1.2, bottom_z=21.0, center_xy=(16.0, -6.0))
assign(pav_tip, MAT_GOLD)

# Turret roofs taller cones
for name, x, y, bz in [
    ("RIGHT_TURRET_A_ROOF", 18.0, 2.5, 18.5),
    ("RIGHT_TURRET_B_ROOF", 16.0, -11.0, 17.5),
    ("BAR_TURRET_FRONT_L_ROOF", -23.0, 5.5, 16.0),
    ("BAR_TURRET_REAR_L_ROOF", -20.8, -3.4, 18.0),
]:
    set_size(ensure_cube(name), 2.4, 2.4, 3.8, bottom_z=bz, center_xy=(x, y))
    assign(bpy.data.objects[name], MAT_ROOF)

# ========== 4) MAIN STAIR — stronger cascade (mockup wide stairs) ==========
# Prefer existing STAIR objects if named differently
stair_names = [o.name for o in bpy.data.objects if "STAIR" in o.name.upper() and "RAIL" not in o.name.upper() and o.type == "MESH"]
print("EXISTING_STAIRS", stair_names[:30])

# Build / resize front cascade steps
for i, (y, z, depth) in enumerate([
    (24.0, 0.0, 3.5),
    (22.0, 1.0, 3.2),
    (20.0, 2.0, 3.0),
    (18.2, 3.0, 2.8),
    (16.6, 4.0, 2.6),
    (15.2, 5.0, 2.4),
    (14.0, 6.0, 2.2),
]):
    name = f"MAIN_STAIR_STEP_{i}"
    o = ensure_cube(name)
    set_size(o, 8.5 - i * 0.25, depth, 1.05, bottom_z=z, center_xy=(CX, y))
    assign(o, MAT_STONE)

# Stair side walls
for side, x in [("L", CX - 4.6), ("R", CX + 4.6)]:
    o = ensure_cube(f"MAIN_STAIR_WALL_{side}")
    set_size(o, 0.7, 12.0, 3.5, bottom_z=0.0, center_xy=(x, 18.5))
    assign(o, MAT_STONE)

# Rails already exist — reposition
for side, x in [("L", CX - 4.3), ("R", CX + 4.3)]:
    o = bpy.data.objects.get(f"STAIR_RAIL_{side}")
    if o:
        set_size(o, 0.3, 12.5, 0.9, bottom_z=2.8, center_xy=(x, 17.5))
        assign(o, MAT_GOLD)

# ========== Material sweep for any new cubes still default ==========
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    n = o.name.upper()
    if any(k in n for k in ("ROOF", "HIP", "SPIRE", "GABLE", "PEAK", "CAP", "RIDGE")) and "GOLD" not in n:
        assign(o, MAT_ROOF)
    elif "GOLD" in n or "FINIAL" in n or "RAIL" in n:
        assign(o, MAT_GOLD)
    elif "STAIR" in n or "STEP" in n:
        assign(o, MAT_STONE)

# Apply scale on new objects
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    if o.name.startswith(("MAIN_STAIR", "BARRACKS_GABLE_CAP", "GOLD_SPIRE", "GOLD_PAVILION", "TOWER_HIP_NS")):
        try:
            for x in bpy.data.objects:
                x.select_set(False)
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        except Exception:
            pass

# ========== Render settings keep PASS6 lighting ==========
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
scene.render.image_settings.file_format = "PNG"

# Save
p8 = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V02.blend")
bpy.ops.wm.save_as_mainfile(filepath=p8)
shutil.copy2(p8, LOOP)
print("SAVED PASS8_V02 + PASS1D")

out8 = os.path.join(BASE, "renders_pass8")
out_work = os.path.join(BASE, "renders_pass1d")
os.makedirs(out8, exist_ok=True)
os.makedirs(out_work, exist_ok=True)

jobs = [
    ("CAM_01_FRONT", out_work, "current_front_work.png"),
    ("CAM_05_FRONT_3Q", out_work, "current_front_3q_work.png"),
    ("CAM_06_REAR_3Q", out_work, "current_rear_3q_work.png"),
    ("CAM_TOP_PLAN", out_work, "current_top_plan_work.png"),
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
        print("MISS", cam)
        continue
    scene.camera = c
    scene.render.filepath = os.path.join(dest, fn)
    bpy.ops.render.render(write_still=True)
    print("OK", fn)

# bounds
minz = minx = miny = 1e9
maxz = maxx = maxy = -1e9
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render or o.name in ("PRES_GROUND", "SCALE_HUMAN"):
        continue
    for corner in o.bound_box:
        w = o.matrix_world @ Vector(corner)
        minx = min(minx, w.x); maxx = max(maxx, w.x)
        miny = min(miny, w.y); maxy = max(maxy, w.y)
        minz = min(minz, w.z); maxz = max(maxz, w.z)
print("BOUNDS", round(maxx-minx,1), round(maxy-miny,1), round(maxz-minz,1), "Z", round(minz,1), round(maxz,1))
print("TICK21_DONE OBJ", len(bpy.data.objects))

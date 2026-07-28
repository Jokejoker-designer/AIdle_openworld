# -*- coding: utf-8 -*-
"""Tick #27: gothic density + courtyard U-wrap + stair break in front wall. Keep scale 24x19x38."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V04_SCALE.blend")
LOOP = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bpy.ops.wm.open_mainfile(filepath=WORK)
print("OPEN", bpy.data.filepath)

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
    return m

def assign(obj, mat):
    if not obj or obj.type != "MESH":
        return
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

MAT_STONE = make_mat("MAT_LIMESTONE", (0.78, 0.74, 0.66), 0.82, 0.0)
MAT_ROOF = make_mat("MAT_SLATE_NAVY", (0.10, 0.16, 0.30), 0.50, 0.04)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.82, 0.62, 0.24), 0.28, 0.90)
MAT_DARK = make_mat("MAT_DARK_STONE", (0.22, 0.21, 0.20), 0.92, 0.0)
MAT_BANNER = make_mat("MAT_BANNER_BLUE", (0.07, 0.14, 0.42), 0.62, 0.0)
MAT_GLASS = make_mat("MAT_GLASS", (0.45, 0.58, 0.72), 0.12, 0.0)
MAT_WOOD = make_mat("MAT_WOOD", (0.28, 0.16, 0.08), 0.72, 0.0)

CX, CY = 1.0, 1.5

# ========== 1) FRONT WALL GATE OPENING so stairs read (mockup) ==========
# Split outer front wall into L/R with center gap for stairs
ow = bpy.data.objects.get("OUTER_WALL_FRONT")
if ow:
    # left segment
    set_size(ensure_cube("OUTER_WALL_FRONT_L"), 6.5, 1.2, 5.5, bottom_z=0.0, center_xy=(-6.5, 9.5))
    assign(bpy.data.objects["OUTER_WALL_FRONT_L"], MAT_DARK)
    set_size(ensure_cube("OUTER_WALL_FRONT_R"), 6.5, 1.2, 5.5, bottom_z=0.0, center_xy=(7.5, 9.5))
    assign(bpy.data.objects["OUTER_WALL_FRONT_R"], MAT_DARK)
    # gate piers
    set_size(ensure_cube("GATE_PIER_L"), 1.4, 1.6, 7.0, bottom_z=0.0, center_xy=(-3.0, 9.5))
    assign(bpy.data.objects["GATE_PIER_L"], MAT_STONE)
    set_size(ensure_cube("GATE_PIER_R"), 1.4, 1.6, 7.0, bottom_z=0.0, center_xy=(4.0, 9.5))
    assign(bpy.data.objects["GATE_PIER_R"], MAT_STONE)
    # lintel over stair gap
    set_size(ensure_cube("GATE_LINTEL"), 7.5, 1.4, 1.2, bottom_z=6.2, center_xy=(CX, 9.5))
    assign(bpy.data.objects["GATE_LINTEL"], MAT_STONE)
    # hide solid full front wall
    ow.hide_render = True
    ow.hide_viewport = True

# ========== 2) STAIRS more prominent through gate ==========
for i in range(10):
    t = i / 9.0
    y = 9.0 - t * 5.2
    z = i * 0.68
    w = 6.5 - i * 0.1
    o = ensure_cube(f"MAIN_STAIR_STEP_{i}")
    set_size(o, w, 0.9, 0.72, bottom_z=z, center_xy=(CX, y))
    assign(o, MAT_STONE)

for side, x in [("L", CX - 3.6), ("R", CX + 3.6)]:
    set_size(ensure_cube(f"MAIN_STAIR_WALL_{side}"), 0.5, 6.0, 2.6, bottom_z=0.8, center_xy=(x, 6.2))
    assign(bpy.data.objects[f"MAIN_STAIR_WALL_{side}"], MAT_STONE)
    set_size(ensure_cube(f"STAIR_RAIL_{side}"), 0.18, 5.5, 0.5, bottom_z=2.4, center_xy=(x, 6.2))
    assign(bpy.data.objects[f"STAIR_RAIL_{side}"], MAT_GOLD)

# ========== 3) LEFT HALL — denser multi-gable + windows (mockup gothic) ==========
# Extra pointed gables along ridge
for i, gx in enumerate([-10.5, -9.0, -7.5, -6.0, -4.5, -3.2]):
    o = ensure_cube(f"BARRACKS_ROOF_GABLE_{i}")
    set_size(o, 1.8, 3.6, 3.2, bottom_z=13.2, center_xy=(gx, 4.6))
    assign(o, MAT_ROOF)
    cap = ensure_cube(f"BARRACKS_GABLE_CAP_{i}")
    set_size(cap, 0.9, 0.9, 1.4, bottom_z=16.0, center_xy=(gx, 4.6))
    assign(cap, MAT_ROOF)
    # gold tip
    tip = ensure_cube(f"GOLD_GABLE_TIP_L_{i}")
    set_size(tip, 0.2, 0.2, 0.7, bottom_z=17.2, center_xy=(gx, 4.6))
    assign(tip, MAT_GOLD)

# Steeper main roof ridge
set_size(ensure_cube("BARRACKS_RIDGE"), 10.0, 1.5, 2.0, bottom_z=14.5, center_xy=(-6.5, 1.5))
assign(bpy.data.objects["BARRACKS_RIDGE"], MAT_ROOF)

# Barracks front windows (2 rows x 4)
for row, z in enumerate([5.5, 9.0]):
    for col, x in enumerate([-9.5, -7.5, -5.5, -3.5]):
        w = ensure_cube(f"BAR_WIN_{row}_{col}")
        set_size(w, 1.1, 0.35, 1.6, bottom_z=z, center_xy=(x, 5.6))
        assign(w, MAT_GLASS)
        fr = ensure_cube(f"BAR_WIN_FRAME_{row}_{col}")
        set_size(fr, 1.3, 0.22, 1.85, bottom_z=z - 0.05, center_xy=(x, 5.7))
        assign(fr, MAT_GOLD)

# Barracks banners
for i, x in enumerate([-9.0, -6.0, -3.5]):
    b = ensure_cube(f"BANNER_BAR_{i}")
    set_size(b, 0.9, 0.08, 1.8, bottom_z=7.0, center_xy=(x, 5.85))
    assign(b, MAT_BANNER)

# ========== 4) TOWER CROWN density + mid banners ==========
# Extra mid crown peaks (mockup multi-spire)
for i, (dx, dy) in enumerate([(0, 3.5), (0, -3.5), (3.5, 0), (-3.5, 0)]):
    o = ensure_cube(f"TOWER_CROWN_PEAK_{i}")
    set_size(o, 1.5, 1.5, 2.8, bottom_z=31.5, center_xy=(CX + dx, CY + dy))
    assign(o, MAT_ROOF)

# Gold cornice under crown
set_size(ensure_cube("GOLD_CORNICE_OBS"), 9.0, 9.0, 0.35, bottom_z=29.2, center_xy=(CX, CY))
assign(bpy.data.objects["GOLD_CORNICE_OBS"], MAT_GOLD)

# Observation arcade arches front
for i, xoff in enumerate([-2.5, -0.8, 0.8, 2.5]):
    a = ensure_cube(f"TOWER_OBS_ARCH_{i}")
    set_size(a, 1.2, 0.5, 2.0, bottom_z=26.0, center_xy=(CX + xoff, CY + 4.2))
    assign(a, MAT_GLASS)
    f = ensure_cube(f"TOWER_OBS_FRAME_{i}")
    set_size(f, 1.4, 0.3, 2.3, bottom_z=25.9, center_xy=(CX + xoff, CY + 4.3))
    assign(f, MAT_GOLD)

# Portal side banners larger (mockup)
set_size(ensure_cube("BANNER_PANEL_L"), 1.1, 0.1, 2.8, bottom_z=8.0, center_xy=(CX - 3.0, CY + 4.2))
assign(bpy.data.objects["BANNER_PANEL_L"], MAT_BANNER)
set_size(ensure_cube("BANNER_PANEL_R"), 1.1, 0.1, 2.8, bottom_z=8.0, center_xy=(CX + 3.0, CY + 4.2))
assign(bpy.data.objects["BANNER_PANEL_R"], MAT_BANNER)

# ========== 5) COURTYARD U-WRAP — rear arm left + right lower ==========
# Left rear arm (U wrap)
set_size(ensure_cube("COURTYARD_REAR_ARM_L"), 8.0, 3.5, 7.0, bottom_z=2.5, center_xy=(-5.0, -4.5))
assign(bpy.data.objects["COURTYARD_REAR_ARM_L"], MAT_STONE)
set_size(ensure_cube("COURTYARD_REAR_ARM_L_ROOF"), 9.0, 4.2, 2.8, bottom_z=9.0, center_xy=(-5.0, -4.5))
assign(bpy.data.objects["COURTYARD_REAR_ARM_L_ROOF"], MAT_ROOF)

# Right rear lower connector
set_size(ensure_cube("COURTYARD_REAR_ARM_R"), 5.0, 3.0, 6.0, bottom_z=2.5, center_xy=(6.5, -4.0))
assign(bpy.data.objects["COURTYARD_REAR_ARM_R"], MAT_STONE)
set_size(ensure_cube("COURTYARD_REAR_ARM_R_ROOF"), 5.5, 3.5, 2.4, bottom_z=8.2, center_xy=(6.5, -4.0))
assign(bpy.data.objects["COURTYARD_REAR_ARM_R_ROOF"], MAT_ROOF)

# Courtyard open floor (inner void)
set_size(ensure_cube("COURTYARD_FLOOR"), 9.0, 5.5, 0.25, bottom_z=2.3, center_xy=(0.5, -1.5))
assign(bpy.data.objects["COURTYARD_FLOOR"], MAT_DARK)

# ========== 6) RIGHT WING — more gables lower density ==========
for i, (gx, gy) in enumerate([(5.0, 2.8), (7.0, 2.5), (9.0, 1.5), (6.5, -0.5)]):
    o = ensure_cube(f"RIGHT_ROOF_GABLE_{i}")
    set_size(o, 1.8, 2.4, 2.2, bottom_z=11.8, center_xy=(gx, gy))
    assign(o, MAT_ROOF)

# Gold eaves right
set_size(ensure_cube("GOLD_EAVES_RIGHT"), 7.5, 0.18, 0.22, bottom_z=9.6, center_xy=(7.5, 3.8))
assign(bpy.data.objects["GOLD_EAVES_RIGHT"], MAT_GOLD)

# Apply scale on new objects
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name.startswith((
        "OUTER_WALL_FRONT_", "GATE_", "BARRACKS_ROOF", "BARRACKS_GABLE", "BARRACKS_RIDGE",
        "BAR_WIN", "BANNER_BAR", "TOWER_CROWN", "TOWER_OBS", "GOLD_", "COURTYARD_",
        "RIGHT_ROOF", "MAIN_STAIR", "STAIR_RAIL", "BANNER_PANEL",
    )):
        try:
            for x in bpy.data.objects:
                x.select_set(False)
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        except Exception:
            pass

# Bounds audit
minx = miny = minz = 1e9
maxx = maxy = maxz = -1e9
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render or o.name in ("PRES_GROUND", "SCALE_HUMAN"):
        continue
    for corner in o.bound_box:
        w = o.matrix_world @ Vector(corner)
        minx = min(minx, w.x); maxx = max(maxx, w.x)
        miny = min(miny, w.y); maxy = max(maxy, w.y)
        minz = min(minz, w.z); maxz = max(maxz, w.z)
print("BOUNDS", round(maxx - minx, 2), round(maxy - miny, 2), round(maxz - minz, 2), "Z", round(minz, 2), round(maxz, 2))

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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V05_DENSITY.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V05")

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

print("TICK27_DONE OBJ", len(bpy.data.objects))

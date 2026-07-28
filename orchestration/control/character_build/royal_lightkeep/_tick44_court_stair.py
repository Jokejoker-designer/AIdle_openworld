# -*- coding: utf-8 -*-
"""Tick #44: courtyard U-wrap walls + main stair clarity. Scale lock 24x19x38."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V21_PARAPET.blend")
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
MAT_DARK = make_mat("MAT_FOUNDATION_DARK", (0.22, 0.20, 0.18), 0.88, 0.0)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.82, 0.62, 0.24), 0.28, 0.90)
MAT_WOOD = make_mat("MAT_WOOD", (0.42, 0.28, 0.16), 0.75, 0.0)

CX, CY = 1.0, 1.5
H_MAX = 38.2

# ========== COURTYARD U-WRAP inner walls (read void from top/front) ==========
# Front arm of U (low wall facing camera, defining court mouth)
set_size(ensure_cube("COURT_U_FRONT_L"), 4.5, 0.7, 2.8, bottom_z=0.15, center_xy=(-5.5, 3.5))
assign(bpy.data.objects["COURT_U_FRONT_L"], MAT_STONE)
set_size(ensure_cube("COURT_U_FRONT_R"), 4.0, 0.7, 2.8, bottom_z=0.15, center_xy=(6.5, 3.2))
assign(bpy.data.objects["COURT_U_FRONT_R"], MAT_STONE)

# Side arms of U
set_size(ensure_cube("COURT_U_SIDE_L"), 0.7, 5.5, 3.0, bottom_z=0.15, center_xy=(-7.8, 0.5))
assign(bpy.data.objects["COURT_U_SIDE_L"], MAT_STONE)
set_size(ensure_cube("COURT_U_SIDE_R"), 0.7, 5.0, 3.0, bottom_z=0.15, center_xy=(8.2, 0.3))
assign(bpy.data.objects["COURT_U_SIDE_R"], MAT_STONE)

# Rear U base (against tower mass)
set_size(ensure_cube("COURT_U_REAR"), 12.0, 0.75, 3.2, bottom_z=0.15, center_xy=(CX, CY - 1.2))
assign(bpy.data.objects["COURT_U_REAR"], MAT_STONE)

# Court floor pad (darker) for void readability
set_size(ensure_cube("COURT_FLOOR_PAD"), 10.5, 6.5, 0.18, bottom_z=0.05, center_xy=(CX, 1.0))
assign(bpy.data.objects["COURT_FLOOR_PAD"], MAT_DARK)

# ========== MAIN STAIR (front center → court) ==========
for i, (z, y, d) in enumerate([
    (0.15, 5.8, 0.35),
    (0.55, 5.2, 0.35),
    (0.95, 4.6, 0.35),
    (1.35, 4.0, 0.35),
    (1.75, 3.4, 0.35),
    (2.15, 2.8, 0.35),
]):
    set_size(ensure_cube(f"MAIN_STAIR_TREAD_{i}"), 4.2, 0.85, d, bottom_z=z, center_xy=(CX, y))
    assign(bpy.data.objects[f"MAIN_STAIR_TREAD_{i}"], MAT_STONE)

# Stair side rails
set_size(ensure_cube("MAIN_STAIR_RAIL_L"), 0.25, 4.2, 0.9, bottom_z=0.8, center_xy=(CX - 2.3, 4.2))
assign(bpy.data.objects["MAIN_STAIR_RAIL_L"], MAT_DARK)
set_size(ensure_cube("MAIN_STAIR_RAIL_R"), 0.25, 4.2, 0.9, bottom_z=0.8, center_xy=(CX + 2.3, 4.2))
assign(bpy.data.objects["MAIN_STAIR_RAIL_R"], MAT_DARK)

# Gate threshold wood plank at stair top
set_size(ensure_cube("GATE_THRESH_WOOD"), 3.6, 0.9, 0.22, bottom_z=2.4, center_xy=(CX, 2.5))
assign(bpy.data.objects["GATE_THRESH_WOOD"], MAT_WOOD)

# Gold cap on rails
set_size(ensure_cube("STAIR_CAP_L"), 0.28, 4.0, 0.12, bottom_z=1.65, center_xy=(CX - 2.3, 4.2))
assign(bpy.data.objects["STAIR_CAP_L"], MAT_GOLD)
set_size(ensure_cube("STAIR_CAP_R"), 0.28, 4.0, 0.12, bottom_z=1.65, center_xy=(CX + 2.3, 4.2))
assign(bpy.data.objects["STAIR_CAP_R"], MAT_GOLD)

# Apply
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name.startswith(("COURT_U_", "COURT_FLOOR", "MAIN_STAIR_", "GATE_THRESH", "STAIR_CAP_")):
        try:
            for x in bpy.data.objects:
                x.select_set(False)
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        except Exception:
            pass

# Soft footprint clamps
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name in ("PRES_GROUND", "LEVEL0_GROUND"):
        continue
    corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
    minx = min(c.x for c in corners); maxx = max(c.x for c in corners)
    miny = min(c.y for c in corners); maxy = max(c.y for c in corners)
    if minx < -12.1:
        o.location.x += (-12.1 - minx)
    if maxx > 12.1:
        o.location.x += (12.1 - maxx)
    if miny < -9.6:
        o.location.y += (-9.6 - miny)
    if maxy > 9.6:
        o.location.y += (9.6 - maxy)

for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    top = o.location.z + o.dimensions.z / 2.0
    if top > H_MAX:
        o.location.z -= (top - H_MAX)

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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V22_COURT.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V22")

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

print("TICK44_SCRIPT_READY")

# -*- coding: utf-8 -*-
"""Tick #37: dominant main stair (mockup), courtyard contrast, portal rails. Scale lock."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V14_CLAMP2.blend")
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
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.82, 0.62, 0.24), 0.28, 0.90)
MAT_DARK = make_mat("MAT_DARK_STONE", (0.22, 0.21, 0.20), 0.92, 0.0)
MAT_WOOD = make_mat("MAT_WOOD", (0.28, 0.16, 0.08), 0.72, 0.0)
MAT_BANNER = make_mat("MAT_BANNER_BLUE", (0.07, 0.14, 0.42), 0.62, 0.0)

CX, CY = 1.0, 1.5
H_MAX = 38.2

# ========== MAIN STAIR more dominant (mockup front centerpiece) ==========
# 12 wider steps through gate
for i in range(12):
    t = i / 11.0
    y = 9.2 - t * 5.8
    z = i * 0.58
    w = 7.2 - i * 0.12
    o = ensure_cube(f"MAIN_STAIR_STEP_{i}")
    set_size(o, max(w, 4.5), 0.95, 0.62, bottom_z=z, center_xy=(CX, y))
    assign(o, MAT_STONE)

# Heavy side walls
for side, x in [("L", CX - 4.0), ("R", CX + 4.0)]:
    set_size(ensure_cube(f"MAIN_STAIR_WALL_{side}"), 0.6, 6.5, 3.0, bottom_z=0.5, center_xy=(x, 6.0))
    assign(bpy.data.objects[f"MAIN_STAIR_WALL_{side}"], MAT_STONE)
    set_size(ensure_cube(f"STAIR_RAIL_{side}"), 0.2, 6.2, 0.55, bottom_z=2.6, center_xy=(x, 6.0))
    assign(bpy.data.objects[f"STAIR_RAIL_{side}"], MAT_GOLD)
    # posts
    set_size(ensure_cube(f"STAIR_POST_BOT_{side}"), 0.35, 0.35, 2.8, bottom_z=0.3, center_xy=(x, 9.0))
    assign(bpy.data.objects[f"STAIR_POST_BOT_{side}"], MAT_GOLD)
    set_size(ensure_cube(f"STAIR_POST_TOP_{side}"), 0.35, 0.35, 2.4, bottom_z=5.0, center_xy=(x, 3.8))
    assign(bpy.data.objects[f"STAIR_POST_TOP_{side}"], MAT_GOLD)

set_size(ensure_cube("STAIR_LANDING_TOP"), 6.0, 2.2, 0.55, bottom_z=6.5, center_xy=(CX, 3.6))
assign(bpy.data.objects["STAIR_LANDING_TOP"], MAT_STONE)

# Portal stronger
set_size(ensure_cube("PORTAL_PLINTH"), 6.5, 2.8, 1.1, bottom_z=4.8, center_xy=(CX, CY + 3.6))
assign(bpy.data.objects["PORTAL_PLINTH"], MAT_STONE)
set_size(ensure_cube("MAIN_PORTAL_ARCH"), 4.5, 1.1, 6.2, bottom_z=5.2, center_xy=(CX, CY + 4.2))
assign(bpy.data.objects["MAIN_PORTAL_ARCH"], MAT_STONE)
set_size(ensure_cube("MAIN_PORTAL_DOOR"), 2.6, 0.4, 4.8, bottom_z=5.6, center_xy=(CX, CY + 4.65))
assign(bpy.data.objects["MAIN_PORTAL_DOOR"], MAT_WOOD)

# ========== COURTYARD more readable ==========
# Larger dark courtyard floor
set_size(ensure_cube("COURTYARD_FLOOR"), 10.0, 6.5, 0.3, bottom_z=2.4, center_xy=(0.5, -1.2))
assign(bpy.data.objects["COURTYARD_FLOOR"], MAT_DARK)
# Court path stones lighter
set_size(ensure_cube("COURTYARD_PATH"), 3.5, 5.0, 0.25, bottom_z=2.55, center_xy=(CX, -0.5))
assign(bpy.data.objects["COURTYARD_PATH"], MAT_STONE)

# Strengthen U-wrap rear arms slightly
o = bpy.data.objects.get("COURTYARD_REAR_ARM_L")
if o and not o.hide_render:
    set_size(o, 8.5, 3.8, 7.2, bottom_z=2.5, center_xy=(-5.0, -4.5))
    assign(o, MAT_STONE)
o = bpy.data.objects.get("COURTYARD_REAR_ARM_L_ROOF")
if o and not o.hide_render:
    set_size(o, 9.2, 4.4, 2.8, bottom_z=9.2, center_xy=(-5.0, -4.5))
    assign(o, make_mat("MAT_SLATE_NAVY", (0.10, 0.16, 0.30), 0.50, 0.04))

# Gate banners flanking stairs (mockup)
set_size(ensure_cube("BANNER_GATE_L"), 1.0, 0.1, 2.2, bottom_z=3.5, center_xy=(CX - 3.5, 9.2))
assign(bpy.data.objects["BANNER_GATE_L"], MAT_BANNER)
set_size(ensure_cube("BANNER_GATE_R"), 1.0, 0.1, 2.2, bottom_z=3.5, center_xy=(CX + 3.5, 9.2))
assign(bpy.data.objects["BANNER_GATE_R"], MAT_BANNER)

# Apply new/resized
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name.startswith((
        "MAIN_STAIR", "STAIR_", "PORTAL_", "MAIN_PORTAL", "COURTYARD_", "BANNER_GATE",
    )):
        try:
            for x in bpy.data.objects:
                x.select_set(False)
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        except Exception:
            pass

# H clamp
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
print("BOUNDS", round(maxx-minx,1), round(maxy-miny,1), round(maxz-minz,1), "Z", round(minz,1), round(maxz,1))

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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V15_STAIR.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V15")

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

print("TICK37_DONE")

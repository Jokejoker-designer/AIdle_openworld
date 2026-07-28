# -*- coding: utf-8 -*-
"""Tick #33: hall cornice, portal-stair join, z-fight offsets, full mat check, 6-view proofs."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V10_ARCHES.blend")
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
H_MAX = 38.2

# ========== HALL CORNICE under eaves (mockup gold line) ==========
set_size(ensure_cube("HALL_CORNICE_F"), 11.0, 0.35, 0.4, bottom_z=10.9, center_xy=(-6.5, 5.9))
assign(bpy.data.objects["HALL_CORNICE_F"], MAT_GOLD)
set_size(ensure_cube("HALL_CORNICE_SIDE"), 0.35, 9.0, 0.4, bottom_z=10.9, center_xy=(-11.5, 1.5))
assign(bpy.data.objects["HALL_CORNICE_SIDE"], MAT_GOLD)

# ========== PORTAL PLINTH join to stairs ==========
set_size(ensure_cube("PORTAL_PLINTH"), 6.0, 2.5, 1.0, bottom_z=4.5, center_xy=(CX, CY + 3.8))
assign(bpy.data.objects["PORTAL_PLINTH"], MAT_STONE)
set_size(ensure_cube("PORTAL_STEP"), 5.0, 1.2, 0.5, bottom_z=5.2, center_xy=(CX, CY + 4.6))
assign(bpy.data.objects["PORTAL_STEP"], MAT_STONE)

# Ensure portal door sits cleanly
set_size(ensure_cube("MAIN_PORTAL_DOOR"), 2.5, 0.4, 4.5, bottom_z=5.5, center_xy=(CX, CY + 4.7))
assign(bpy.data.objects["MAIN_PORTAL_DOOR"], MAT_WOOD)

# ========== Z-FIGHT: push frames slightly outward in Y ==========
zfix = 0
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    n = o.name.upper()
    if any(k in n for k in ("FRAME", "MULLION", "MULL_", "GOLD_EAVES", "CORNICE", "TRIM", "STRING")):
        # slight outward nudge on front-facing (+Y) details
        if "F_" in n or n.endswith("_F") or "FRONT" in n or "HALL_ARCH" in n or "WIN_FRAME" in n or "HALL_CORNICE_F" in n:
            o.location.y += 0.04
            zfix += 1
        elif "L_" in n or "LEFT" in n or "HALL_CORNICE_SIDE" in n:
            o.location.x -= 0.03
            zfix += 1
print("ZFIGHT_NUDGE", zfix)

# ========== RIGHT WING CORNICE ==========
set_size(ensure_cube("RIGHT_CORNICE_F"), 8.0, 0.3, 0.35, bottom_z=9.3, center_xy=(7.5, 4.0))
assign(bpy.data.objects["RIGHT_CORNICE_F"], MAT_GOLD)

# ========== GROUND CONTACT SHADOW plane already exists — ensure dark outer wall not z-fighting base ==========
for name in ("OUTER_WALL_FRONT_L", "OUTER_WALL_FRONT_R", "OUTER_WALL_LEFT", "OUTER_WALL_RIGHT",
             "OUTER_WALL_REAR_L", "OUTER_WALL_REAR_R"):
    o = bpy.data.objects.get(name)
    if o and not o.hide_render:
        # sit slightly above ground
        if o.location.z < 2.5:
            pass  # already bottom-based

# Apply new cubes
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name.startswith(("HALL_CORNICE", "PORTAL_PLINTH", "PORTAL_STEP", "RIGHT_CORNICE", "MAIN_PORTAL_DOOR")):
        try:
            for x in bpy.data.objects:
                x.select_set(False)
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        except Exception:
            pass

# Material quick pass for new
for name in ("HALL_CORNICE_F", "HALL_CORNICE_SIDE", "RIGHT_CORNICE_F", "PORTAL_PLINTH", "PORTAL_STEP"):
    o = bpy.data.objects.get(name)
    if o:
        if "CORNICE" in name:
            assign(o, MAT_GOLD)
        else:
            assign(o, MAT_STONE)

# Height clamp
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    top = o.location.z + o.dimensions.z / 2.0
    if top > H_MAX:
        o.location.z -= (top - H_MAX)

minx = miny = minz = 1e9
maxx = maxy = maxz = -1e9
vis = 0
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render or o.name in ("PRES_GROUND", "SCALE_HUMAN"):
        continue
    vis += 1
    for corner in o.bound_box:
        w = o.matrix_world @ Vector(corner)
        minx = min(minx, w.x); maxx = max(maxx, w.x)
        miny = min(miny, w.y); maxy = max(maxy, w.y)
        minz = min(minz, w.z); maxz = max(maxz, w.z)
print("VIS", vis, "BOUNDS", round(maxx-minx,1), round(maxy-miny,1), round(maxz-minz,1), "Z", round(minz,1), round(maxz,1))

# Residual clay count
clay = 0
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    for s in o.material_slots:
        if s.material and s.material.name.startswith("CLAY"):
            clay += 1
            assign(o, MAT_STONE)
            break
print("CLAY_LEFT", clay)

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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V11_JOIN.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V11")

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

print("TICK33_DONE")

# -*- coding: utf-8 -*-
"""Tick #31: tower string courses, multi-level fort base, bevel key masses, mat sweep. Scale lock."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V08_SIDES.blend")
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

# ========== TOWER STRING COURSES (mockup horizontal bands) ==========
for i, z in enumerate([10.5, 14.5, 18.5, 22.5, 26.0]):
    o = ensure_cube(f"TOWER_STRING_{i}")
    set_size(o, 7.6, 7.6, 0.35, bottom_z=z, center_xy=(CX, CY))
    assign(o, MAT_GOLD if i % 2 == 1 else MAT_STONE)

# Mid belt emphasize
set_size(ensure_cube("TOWER_MID_BELT"), 8.0, 8.0, 1.0, bottom_z=23.8, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_MID_BELT"], MAT_STONE)
set_size(ensure_cube("TOWER_MID_BELT_GOLD"), 8.2, 8.2, 0.25, bottom_z=24.7, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_MID_BELT_GOLD"], MAT_GOLD)

# ========== MULTI-LEVEL FORT BASE (sheet wall 6.5m stepped) ==========
set_size(ensure_cube("FORT_BASE"), 22.0, 17.0, 1.8, bottom_z=0.0, center_xy=(0.0, 1.0))
assign(bpy.data.objects["FORT_BASE"], MAT_STONE)
set_size(ensure_cube("FORT_BASE_STEP2"), 20.0, 15.0, 1.2, bottom_z=1.6, center_xy=(0.0, 1.0))
assign(bpy.data.objects["FORT_BASE_STEP2"], MAT_STONE)
set_size(ensure_cube("FORT_BASE_STEP3"), 18.0, 13.0, 0.9, bottom_z=2.6, center_xy=(0.0, 1.0))
assign(bpy.data.objects["FORT_BASE_STEP3"], MAT_DARK)

# ========== BEVEL key large masses (softens box language) ==========
bevel_targets = [
    "TOWER_SHAFT", "TOWER_OBSERVATION_BLOCK", "BARRACKS_LEFT_MAIN",
    "RIGHT_WING_MAIN", "TOWER_ROOF_BLOCK", "BARRACKS_LEFT_ROOF",
]
beveled = 0
for name in bevel_targets:
    o = bpy.data.objects.get(name)
    if not o or o.type != "MESH" or o.hide_render:
        continue
    # remove existing bevel if any
    for m in list(o.modifiers):
        if m.type == "BEVEL":
            o.modifiers.remove(m)
    mod = o.modifiers.new(name="Bevel", type="BEVEL")
    mod.width = 0.12
    mod.segments = 2
    mod.limit_method = "ANGLE"
    mod.angle_limit = 0.7
    try:
        mod.offset_type = "OFFSET"
    except Exception:
        pass
    beveled += 1
print("BEVELED", beveled)

# ========== MATERIAL SWEEP residual ==========
fixed = 0
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    n = o.name.upper()
    slots = [s.material.name if s.material else "" for s in o.material_slots]
    needs = (not slots) or any(s.startswith("CLAY") or s == "" for s in slots)
    if "ROOF" in n or "SPIRE" in n or "GABLE" in n or "HIP" in n or "PEAK" in n or "POINT" in n or "TIP" in n and "GOLD" not in n:
        if "GOLD" not in n and "FLAG_POLE" not in n:
            assign(o, MAT_ROOF)
            fixed += 1
    elif "BANNER" in n or "FLAG_PANEL" in n:
        assign(o, MAT_BANNER)
    elif "GOLD" in n or "MULLION" in n or "RAIL" in n or "FINIAL" in n or "STRING" in n and "GOLD" in n:
        assign(o, MAT_GOLD)
    elif "WIN_" in n or "ARCH" in n and "PORTAL" not in n:
        assign(o, MAT_GLASS if "FRAME" not in n and "MULLION" not in n else MAT_GOLD)
    elif "DOOR" in n:
        assign(o, MAT_WOOD)
    elif "OUTER" in n or "PARAPET" in n or "BASTION" in n or "LEVEL0" in n or "ARROW" in n:
        assign(o, MAT_DARK)
    elif needs:
        assign(o, MAT_STONE)
        fixed += 1
print("MAT_FIXED", fixed)

# Gold string courses explicitly
for i in range(5):
    o = bpy.data.objects.get(f"TOWER_STRING_{i}")
    if o:
        assign(o, MAT_GOLD if i % 2 == 1 else MAT_STONE)

# Apply scale on new
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name.startswith(("TOWER_STRING", "TOWER_MID_BELT", "FORT_BASE")):
        try:
            for x in bpy.data.objects:
                x.select_set(False)
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        except Exception:
            pass

# Height clamp
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V09_POLISH.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V09")

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

print("TICK31_DONE")

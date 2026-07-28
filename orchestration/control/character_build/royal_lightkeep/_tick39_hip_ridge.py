# -*- coding: utf-8 -*-
"""Tick #39: tower hip layers + hall ridge denser + right roof ridge. Scale lock."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V16_OBS.blend")
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

MAT_ROOF = make_mat("MAT_SLATE_NAVY", (0.10, 0.16, 0.30), 0.50, 0.04)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.82, 0.62, 0.24), 0.28, 0.90)
MAT_STONE = make_mat("MAT_LIMESTONE", (0.78, 0.74, 0.66), 0.82, 0.0)

CX, CY = 1.0, 1.5
H_MAX = 38.2

# ========== TOWER HIP STACK (more layered crown read) ==========
set_size(ensure_cube("TOWER_HIP_BASE"), 9.8, 9.8, 1.2, bottom_z=29.6, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_HIP_BASE"], MAT_ROOF)
set_size(ensure_cube("TOWER_HIP_MID"), 8.0, 8.0, 1.4, bottom_z=30.5, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_HIP_MID"], MAT_ROOF)
# EW/NS hip bars for cross-gable read
set_size(ensure_cube("TOWER_HIP_EW"), 10.0, 3.5, 2.0, bottom_z=30.8, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_HIP_EW"], MAT_ROOF)
set_size(ensure_cube("TOWER_HIP_NS"), 3.5, 10.0, 2.0, bottom_z=30.8, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_HIP_NS"], MAT_ROOF)
set_size(ensure_cube("GOLD_CROWN_RING"), 9.5, 9.5, 0.28, bottom_z=29.5, center_xy=(CX, CY))
assign(bpy.data.objects["GOLD_CROWN_RING"], MAT_GOLD)

# ========== LEFT HALL continuous ridge + secondary ridge ==========
set_size(ensure_cube("BARRACKS_LEFT_ROOF"), 11.8, 10.0, 3.4, bottom_z=11.3, center_xy=(-6.5, 1.5))
assign(bpy.data.objects["BARRACKS_LEFT_ROOF"], MAT_ROOF)
set_size(ensure_cube("GOLD_RIDGE_LEFT"), 11.0, 0.22, 0.25, bottom_z=14.5, center_xy=(-6.5, 1.5))
assign(bpy.data.objects["GOLD_RIDGE_LEFT"], MAT_GOLD)
# front eave gold thicker
set_size(ensure_cube("GOLD_EAVES_BAR_F"), 11.2, 0.22, 0.28, bottom_z=11.4, center_xy=(-6.5, 6.0))
assign(bpy.data.objects["GOLD_EAVES_BAR_F"], MAT_GOLD)

# ========== RIGHT continuous ridge ==========
set_size(ensure_cube("RIGHT_WING_ROOF"), 9.0, 8.5, 2.9, bottom_z=9.7, center_xy=(7.5, 0.5))
assign(bpy.data.objects["RIGHT_WING_ROOF"], MAT_ROOF)
set_size(ensure_cube("GOLD_RIDGE_RIGHT"), 8.0, 0.2, 0.22, bottom_z=12.4, center_xy=(7.5, 0.5))
assign(bpy.data.objects["GOLD_RIDGE_RIGHT"], MAT_GOLD)

# Apply
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name.startswith(("TOWER_HIP", "GOLD_CROWN", "GOLD_RIDGE", "GOLD_EAVES", "BARRACKS_LEFT_ROOF", "RIGHT_WING_ROOF")):
        try:
            for x in bpy.data.objects:
                x.select_set(False)
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        except Exception:
            pass

# Bevel new hip
for name in ("TOWER_HIP_BASE", "TOWER_HIP_MID", "TOWER_HIP_EW", "TOWER_HIP_NS"):
    o = bpy.data.objects.get(name)
    if not o:
        continue
    if not any(m.type == "BEVEL" for m in o.modifiers):
        m = o.modifiers.new("Bevel", "BEVEL")
        m.width = 0.1
        m.segments = 2
        m.limit_method = "ANGLE"

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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V17_HIP.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V17")

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

print("TICK39_DONE")

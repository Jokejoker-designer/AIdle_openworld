# -*- coding: utf-8 -*-
"""Tick #29: height clamp H<=38.5, roof continuity, gold ridges. Keep FP 24x19."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V06_CROWN.blend")
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

CX, CY = 1.0, 1.5
H_MAX = 38.2

# ========== HEIGHT CLAMP: anything top > H_MAX pull down ==========
clamped = 0
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name in ("PRES_GROUND",):
        continue
    top = o.location.z + o.dimensions.z / 2.0
    if top > H_MAX:
        o.location.z -= (top - H_MAX)
        clamped += 1
print("CLAMPED", clamped)

# Explicitly place crown tops within 38m
set_size(ensure_cube("GOLD_FINIAL_PEAK"), 0.3, 0.3, 0.9, bottom_z=36.8, center_xy=(CX, CY))
assign(bpy.data.objects["GOLD_FINIAL_PEAK"], MAT_GOLD)
set_size(ensure_cube("FLAG_POLE"), 0.1, 0.1, 1.5, bottom_z=36.5, center_xy=(CX, CY))
assign(bpy.data.objects["FLAG_POLE"], MAT_GOLD)
set_size(ensure_cube("FLAG_PANEL"), 1.2, 0.07, 0.75, bottom_z=37.3, center_xy=(CX + 0.75, CY))
assign(bpy.data.objects["FLAG_PANEL"], MAT_BANNER)

for i in range(4):
    o = bpy.data.objects.get(f"GOLD_SPIRE_TIP_{i}")
    if o:
        top = o.location.z + o.dimensions.z / 2.0
        if top > H_MAX:
            o.location.z -= (top - H_MAX + 0.1)

# ========== ROOF CONTINUITY — left hall unified main roof ==========
set_size(ensure_cube("BARRACKS_LEFT_ROOF"), 11.5, 9.8, 3.6, bottom_z=11.2, center_xy=(-6.5, 1.5))
assign(bpy.data.objects["BARRACKS_LEFT_ROOF"], MAT_ROOF)
# continuous gold ridge line
set_size(ensure_cube("GOLD_RIDGE_LEFT"), 10.5, 0.2, 0.22, bottom_z=14.6, center_xy=(-6.5, 1.5))
assign(bpy.data.objects["GOLD_RIDGE_LEFT"], MAT_GOLD)
# gold eaves continuous front
set_size(ensure_cube("GOLD_EAVES_BAR_F"), 11.0, 0.18, 0.22, bottom_z=11.3, center_xy=(-6.5, 5.8))
assign(bpy.data.objects["GOLD_EAVES_BAR_F"], MAT_GOLD)

# connector roof continuous to tower
set_size(ensure_cube("CONNECTOR_ROOF"), 4.2, 5.8, 2.0, bottom_z=10.8, center_xy=(-2.3, CY))
assign(bpy.data.objects["CONNECTOR_ROOF"], MAT_ROOF)
set_size(ensure_cube("GOLD_RIDGE_CONN"), 4.0, 0.18, 0.2, bottom_z=12.6, center_xy=(-2.3, CY))
assign(bpy.data.objects["GOLD_RIDGE_CONN"], MAT_GOLD)

# right wing continuous roof
set_size(ensure_cube("RIGHT_WING_ROOF"), 8.8, 8.2, 3.0, bottom_z=9.6, center_xy=(7.5, 0.5))
assign(bpy.data.objects["RIGHT_WING_ROOF"], MAT_ROOF)
set_size(ensure_cube("GOLD_RIDGE_RIGHT"), 7.5, 0.18, 0.2, bottom_z=12.4, center_xy=(7.5, 0.5))
assign(bpy.data.objects["GOLD_RIDGE_RIGHT"], MAT_GOLD)

# tower hip gold ring
set_size(ensure_cube("GOLD_CROWN_RING"), 9.2, 9.2, 0.28, bottom_z=29.4, center_xy=(CX, CY))
assign(bpy.data.objects["GOLD_CROWN_RING"], MAT_GOLD)

# ========== BUTTRESSES left hall front (mockup vertical rhythm) ==========
for i, x in enumerate([-9.5, -7.0, -4.5]):
    o = ensure_cube(f"BARRACKS_BUTTRESS_{i}")
    set_size(o, 0.9, 1.4, 7.5, bottom_z=2.8, center_xy=(x, 5.5))
    assign(o, MAT_STONE)

# ========== STAIR landing polish ==========
set_size(ensure_cube("STAIR_LANDING_TOP"), 5.5, 2.0, 0.6, bottom_z=6.2, center_xy=(CX, 4.2))
assign(bpy.data.objects["STAIR_LANDING_TOP"], MAT_STONE)

# Apply new
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name.startswith(("GOLD_RIDGE", "GOLD_CROWN", "GOLD_EAVES", "BARRACKS_BUTTRESS", "STAIR_LANDING",
                          "FLAG_", "GOLD_FINIAL", "BARRACKS_LEFT_ROOF", "CONNECTOR_ROOF", "RIGHT_WING_ROOF")):
        try:
            for x in bpy.data.objects:
                x.select_set(False)
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        except Exception:
            pass

# Final clamp pass after edits
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V07_CLAMP.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V07")

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

print("TICK29_DONE")

# -*- coding: utf-8 -*-
"""Tick #42: left/right facade windows for sheet views 3-4. Scale lock 24x19x38."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V19_REAR.blend")
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

MAT_GLASS = make_mat("MAT_GLASS", (0.45, 0.58, 0.72), 0.12, 0.0)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.82, 0.62, 0.24), 0.28, 0.90)
MAT_BANNER = make_mat("MAT_BANNER_BLUE", (0.07, 0.14, 0.42), 0.62, 0.0)
MAT_STONE = make_mat("MAT_LIMESTONE", (0.78, 0.74, 0.66), 0.82, 0.0)

CX, CY = 1.0, 1.5
H_MAX = 38.2

# ========== LEFT FACADE windows on hall outer wall (view 3) ==========
# along -X face of barracks, y varying
for row, z in enumerate([5.5, 8.5]):
    for col, y in enumerate([-1.0, 1.5, 4.0]):
        set_size(ensure_cube(f"HALL_SIDE_L_WIN_{row}_{col}"), 0.35, 1.1, 1.7, bottom_z=z, center_xy=(-11.2, y))
        assign(bpy.data.objects[f"HALL_SIDE_L_WIN_{row}_{col}"], MAT_GLASS)
        set_size(ensure_cube(f"HALL_SIDE_L_FR_{row}_{col}"), 0.22, 1.3, 2.0, bottom_z=z - 0.08, center_xy=(-11.35, y))
        assign(bpy.data.objects[f"HALL_SIDE_L_FR_{row}_{col}"], MAT_GOLD)

# Left side banners
for i, y in enumerate([0.0, 3.0]):
    set_size(ensure_cube(f"BANNER_SIDE_L_{i}"), 0.1, 0.9, 1.8, bottom_z=7.0, center_xy=(-11.4, y))
    assign(bpy.data.objects[f"BANNER_SIDE_L_{i}"], MAT_BANNER)

# ========== RIGHT FACADE windows (view 4) ==========
for row, z in enumerate([5.0, 8.0]):
    for col, y in enumerate([-2.0, 0.5, 2.5]):
        set_size(ensure_cube(f"WING_SIDE_R_WIN_{row}_{col}"), 0.35, 1.0, 1.6, bottom_z=z, center_xy=(11.0, y))
        assign(bpy.data.objects[f"WING_SIDE_R_WIN_{row}_{col}"], MAT_GLASS)
        set_size(ensure_cube(f"WING_SIDE_R_FR_{row}_{col}"), 0.22, 1.2, 1.9, bottom_z=z - 0.08, center_xy=(11.15, y))
        assign(bpy.data.objects[f"WING_SIDE_R_FR_{row}_{col}"], MAT_GOLD)

# Right side banners
for i, y in enumerate([-1.0, 2.0]):
    set_size(ensure_cube(f"BANNER_SIDE_R_{i}"), 0.1, 0.85, 1.7, bottom_z=6.5, center_xy=(11.2, y))
    assign(bpy.data.objects[f"BANNER_SIDE_R_{i}"], MAT_BANNER)

# Corner turret left more windows
for i, z in enumerate([5.0, 9.0]):
    set_size(ensure_cube(f"TURRET_L_WIN_{i}"), 0.9, 0.35, 1.4, bottom_z=z, center_xy=(-10.5, 7.0))
    assign(bpy.data.objects[f"TURRET_L_WIN_{i}"], MAT_GLASS)

# Apply
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name.startswith(("HALL_SIDE_L", "WING_SIDE_R", "BANNER_SIDE", "TURRET_L_WIN")):
        try:
            for x in bpy.data.objects:
                x.select_set(False)
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        except Exception:
            pass

# Footprint soft clamp X
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name in ("PRES_GROUND", "LEVEL0_GROUND"):
        continue
    corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
    minx = min(c.x for c in corners); maxx = max(c.x for c in corners)
    if minx < -12.1:
        o.location.x += (-12.1 - minx)
    if maxx > 12.1:
        o.location.x += (12.1 - maxx)

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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V20_SIDES2.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V20")

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

print("TICK42_DONE")

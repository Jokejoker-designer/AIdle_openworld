# -*- coding: utf-8 -*-
"""Tick #35: roof dormers on hall, tech cleanup batch, validation metrics, proofs."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V12_PRESENT.blend")
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
MAT_GLASS = make_mat("MAT_GLASS", (0.45, 0.58, 0.72), 0.12, 0.0)
MAT_DARK = make_mat("MAT_DARK_STONE", (0.22, 0.21, 0.20), 0.92, 0.0)

H_MAX = 38.2

# ========== ROOF DORMERS on left hall (mockup dormer rhythm) ==========
for i, x in enumerate([-9.5, -7.0, -4.5]):
    # dormer body
    set_size(ensure_cube(f"DORMER_BODY_{i}"), 1.6, 1.8, 1.6, bottom_z=13.5, center_xy=(x, 4.2))
    assign(bpy.data.objects[f"DORMER_BODY_{i}"], MAT_STONE)
    # dormer roof peak
    set_size(ensure_cube(f"DORMER_ROOF_{i}"), 1.9, 2.0, 1.2, bottom_z=14.9, center_xy=(x, 4.2))
    assign(bpy.data.objects[f"DORMER_ROOF_{i}"], MAT_ROOF)
    set_size(ensure_cube(f"DORMER_POINT_{i}"), 0.7, 0.7, 0.9, bottom_z=15.9, center_xy=(x, 4.2))
    assign(bpy.data.objects[f"DORMER_POINT_{i}"], MAT_ROOF)
    # small window
    set_size(ensure_cube(f"DORMER_WIN_{i}"), 0.9, 0.3, 1.0, bottom_z=13.7, center_xy=(x, 5.0))
    assign(bpy.data.objects[f"DORMER_WIN_{i}"], MAT_GLASS)
    set_size(ensure_cube(f"DORMER_FRAME_{i}"), 1.1, 0.2, 1.2, bottom_z=13.6, center_xy=(x, 5.1))
    assign(bpy.data.objects[f"DORMER_FRAME_{i}"], MAT_GOLD)

# Right wing dormers (2)
for i, x in enumerate([6.0, 8.5]):
    set_size(ensure_cube(f"DORMER_R_BODY_{i}"), 1.4, 1.5, 1.4, bottom_z=11.5, center_xy=(x, 2.5))
    assign(bpy.data.objects[f"DORMER_R_BODY_{i}"], MAT_STONE)
    set_size(ensure_cube(f"DORMER_R_ROOF_{i}"), 1.7, 1.7, 1.0, bottom_z=12.7, center_xy=(x, 2.5))
    assign(bpy.data.objects[f"DORMER_R_ROOF_{i}"], MAT_ROOF)
    set_size(ensure_cube(f"DORMER_R_WIN_{i}"), 0.8, 0.25, 0.9, bottom_z=11.7, center_xy=(x, 3.2))
    assign(bpy.data.objects[f"DORMER_R_WIN_{i}"], MAT_GLASS)

# ========== TECH CLEANUP ==========
# Hide pure helper empties none; rename unnamed
renamed = 0
for o in bpy.data.objects:
    if not o.name or o.name.strip() == "":
        o.name = f"OBJ_{renamed}"
        renamed += 1

# Apply scale on dormers
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name.startswith("DORMER"):
        try:
            for x in bpy.data.objects:
                x.select_set(False)
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        except Exception:
            pass

# Bevel dormers
bev = 0
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name.startswith("DORMER") and not any(m.type == "BEVEL" for m in o.modifiers):
        mod = o.modifiers.new("Bevel", "BEVEL")
        mod.width = 0.06
        mod.segments = 2
        mod.limit_method = "ANGLE"
        bev += 1
print("DORMER_BEVEL", bev)

# Height clamp
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    top = o.location.z + o.dimensions.z / 2.0
    if top > H_MAX:
        o.location.z -= (top - H_MAX)

# Metrics
minx = miny = minz = 1e9
maxx = maxy = maxz = -1e9
vis = 0
mesh_total = 0
hidden = 0
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    mesh_total += 1
    if o.hide_render:
        hidden += 1
        continue
    if o.name in ("PRES_GROUND", "SCALE_HUMAN"):
        continue
    vis += 1
    for corner in o.bound_box:
        w = o.matrix_world @ Vector(corner)
        minx = min(minx, w.x); maxx = max(maxx, w.x)
        miny = min(miny, w.y); maxy = max(maxy, w.y)
        minz = min(minz, w.z); maxz = max(maxz, w.z)

cams = sorted(o.name for o in bpy.data.objects if o.type == "CAMERA")
print("VIS", vis, "MESH_TOTAL", mesh_total, "HIDDEN", hidden)
print("BOUNDS", round(maxx-minx,1), round(maxy-miny,1), round(maxz-minz,1), "Z", round(minz,1), round(maxz,1))
print("CAMS", len(cams), cams)

# Write tech snapshot
report = os.path.join(BASE, "PASS8_V13_TECH_SNAPSHOT.md")
with open(report, "w", encoding="utf-8") as f:
    f.write("# PASS8 V13 TECH SNAPSHOT\n\n")
    f.write(f"- stamp: {STAMP}\n")
    f.write(f"- visible_mesh: {vis}\n")
    f.write(f"- total_mesh: {mesh_total} (hidden {hidden})\n")
    f.write(f"- bounds: {round(maxx-minx,1)} x {round(maxy-miny,1)} x {round(maxz-minz,1)} m\n")
    f.write(f"- Z: {round(minz,1)} .. {round(maxz,1)} (target H 38, FP 24x19)\n")
    f.write(f"- cameras: {', '.join(cams)}\n")
    f.write(f"- ASSET_FINAL_COMPLETE: false\n")
    f.write(f"- accepted: false\n")
    f.write(f"- note: dormers added; still modular box gothic vs M0 sheet\n")
print("REPORT", report)

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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V13_DORMERS.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V13")

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

print("TICK35_DONE")

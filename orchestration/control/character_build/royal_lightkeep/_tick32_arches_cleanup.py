# -*- coding: utf-8 -*-
"""Tick #32: hall tall arched windows, corner turret caps, apply bevels wider, normals. Scale lock."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V09_POLISH.blend")
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

CX, CY = 1.0, 1.5
H_MAX = 38.2

# ========== TALL ARCHED WINDOW BAYS on left hall (mockup gothic) ==========
# Replace small grid with taller arch-like stacks (glass + gold frame + pointed top)
for i, x in enumerate([-9.5, -7.5, -5.5, -3.5]):
    # tall glass
    set_size(ensure_cube(f"HALL_ARCH_GLASS_{i}"), 1.3, 0.4, 3.5, bottom_z=5.0, center_xy=(x, 5.65))
    assign(bpy.data.objects[f"HALL_ARCH_GLASS_{i}"], MAT_GLASS)
    # gold frame
    set_size(ensure_cube(f"HALL_ARCH_FRAME_{i}"), 1.55, 0.28, 3.9, bottom_z=4.85, center_xy=(x, 5.75))
    assign(bpy.data.objects[f"HALL_ARCH_FRAME_{i}"], MAT_GOLD)
    # pointed arch top (roof-color or gold)
    set_size(ensure_cube(f"HALL_ARCH_POINT_{i}"), 1.0, 0.35, 1.0, bottom_z=8.6, center_xy=(x, 5.7))
    assign(bpy.data.objects[f"HALL_ARCH_POINT_{i}"], MAT_GOLD)
    # mullion
    set_size(ensure_cube(f"HALL_ARCH_MULL_{i}"), 0.12, 0.3, 3.4, bottom_z=5.05, center_xy=(x, 5.8))
    assign(bpy.data.objects[f"HALL_ARCH_MULL_{i}"], MAT_GOLD)

# Hide smaller BAR_WIN that conflict visually (optional keep lower row only hidden if overlap)
for row in (0, 1):
    for col in range(4):
        o = bpy.data.objects.get(f"BAR_WIN_{row}_{col}")
        if o:
            o.hide_render = True
            o.hide_viewport = True
        o = bpy.data.objects.get(f"BAR_WIN_FRAME_{row}_{col}")
        if o:
            o.hide_render = True
            o.hide_viewport = True

# ========== CORNER TURRETS on tower observation more cap-like ==========
for i, (dx, dy) in enumerate([(-3.2, -3.2), (3.2, -3.2), (-3.2, 3.2), (3.2, 3.2)]):
    set_size(ensure_cube(f"TOWER_CORNER_MASS_{i}"), 2.5, 2.5, 4.5, bottom_z=28.8, center_xy=(CX + dx, CY + dy))
    assign(bpy.data.objects[f"TOWER_CORNER_MASS_{i}"], MAT_STONE)
    # battlement cubes
    set_size(ensure_cube(f"TOWER_BATTLEMENT_{i}"), 2.7, 2.7, 0.8, bottom_z=33.0, center_xy=(CX + dx, CY + dy))
    assign(bpy.data.objects[f"TOWER_BATTLEMENT_{i}"], MAT_STONE)

# ========== MORE BEVELS ==========
bevel_names = []
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    n = o.name.upper()
    if any(k in n for k in ("TOWER_SHAFT", "TOWER_OBS", "BARRACKS_LEFT_MAIN", "RIGHT_WING_MAIN",
                             "HALL_ARCH", "TOWER_CORNER", "FORT_BASE", "MAIN_PORTAL",
                             "BARRACKS_LEFT_ROOF", "RIGHT_WING_ROOF", "TOWER_ROOF")):
        bevel_names.append(o.name)

beveled = 0
for name in bevel_names:
    o = bpy.data.objects.get(name)
    if not o:
        continue
    has = any(m.type == "BEVEL" for m in o.modifiers)
    if not has:
        mod = o.modifiers.new(name="Bevel", type="BEVEL")
        mod.width = 0.1
        mod.segments = 2
        mod.limit_method = "ANGLE"
        mod.angle_limit = 0.7
        beveled += 1
print("NEW_BEVELS", beveled)

# ========== NORMALS on visible meshes (batch, skip if too many failures) ==========
norm_ok = 0
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    if not o.name.startswith(("HALL_ARCH", "TOWER_BATTLEMENT", "TOWER_CORNER", "TOWER_STRING")):
        continue
    try:
        for x in bpy.data.objects:
            x.select_set(False)
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        norm_ok += 1
    except Exception:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
print("NORMALS", norm_ok)

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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V10_ARCHES.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V10")

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

print("TICK32_DONE")

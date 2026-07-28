# -*- coding: utf-8 -*-
"""Tick #28: pointed crown/spires + tower window rhythm + portal polish. Scale lock 24x19x38."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V05_DENSITY.blend")
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

# ========== POINTED SPIRES (tapered stacks, mockup multi-spire crown) ==========
# 4 corner spires: base wide → tip narrow, total height to ~38m
corners = [(-3.2, -3.2, 0), (3.2, -3.2, 1), (-3.2, 3.2, 2), (3.2, 3.2, 3)]
for dx, dy, i in corners:
    # base
    set_size(ensure_cube(f"TOWER_SPIRE_{i}"), 2.0, 2.0, 2.2, bottom_z=32.0, center_xy=(CX + dx, CY + dy))
    assign(bpy.data.objects[f"TOWER_SPIRE_{i}"], MAT_ROOF)
    # mid taper
    set_size(ensure_cube(f"TOWER_SPIRE_MID_{i}"), 1.3, 1.3, 2.0, bottom_z=34.0, center_xy=(CX + dx, CY + dy))
    assign(bpy.data.objects[f"TOWER_SPIRE_MID_{i}"], MAT_ROOF)
    # tip
    set_size(ensure_cube(f"TOWER_SPIRE_TIP_{i}"), 0.7, 0.7, 1.8, bottom_z=35.8, center_xy=(CX + dx, CY + dy))
    assign(bpy.data.objects[f"TOWER_SPIRE_TIP_{i}"], MAT_ROOF)
    set_size(ensure_cube(f"GOLD_SPIRE_TIP_{i}"), 0.22, 0.22, 0.9, bottom_z=37.4, center_xy=(CX + dx, CY + dy))
    assign(bpy.data.objects[f"GOLD_SPIRE_TIP_{i}"], MAT_GOLD)

# Central spire stack (taller, mockup central peak + flag)
set_size(ensure_cube("TOWER_ROOF_BLOCK"), 5.5, 5.5, 2.5, bottom_z=30.5, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_ROOF_BLOCK"], MAT_ROOF)
set_size(ensure_cube("TOWER_ROOF_PEAK"), 3.2, 3.2, 2.4, bottom_z=32.8, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_ROOF_PEAK"], MAT_ROOF)
set_size(ensure_cube("TOWER_CENTRAL_SPIRE"), 1.6, 1.6, 2.5, bottom_z=34.8, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_CENTRAL_SPIRE"], MAT_ROOF)
set_size(ensure_cube("TOWER_CENTRAL_TIP"), 0.8, 0.8, 1.6, bottom_z=37.0, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_CENTRAL_TIP"], MAT_ROOF)
set_size(ensure_cube("GOLD_FINIAL_PEAK"), 0.35, 0.35, 1.2, bottom_z=38.3, center_xy=(CX, CY))
assign(bpy.data.objects["GOLD_FINIAL_PEAK"], MAT_GOLD)
# Flag panel
set_size(ensure_cube("FLAG_PANEL"), 1.4, 0.08, 0.9, bottom_z=38.8, center_xy=(CX + 0.9, CY))
assign(bpy.data.objects["FLAG_PANEL"], MAT_BANNER)
set_size(ensure_cube("FLAG_POLE"), 0.12, 0.12, 2.0, bottom_z=37.5, center_xy=(CX, CY))
assign(bpy.data.objects["FLAG_POLE"], MAT_GOLD)

# Cardinal mid peaks more pointed
for i, (dx, dy) in enumerate([(0, 3.3), (0, -3.3), (3.3, 0), (-3.3, 0)]):
    set_size(ensure_cube(f"TOWER_CROWN_PEAK_{i}"), 1.4, 1.4, 2.2, bottom_z=31.2, center_xy=(CX + dx, CY + dy))
    assign(bpy.data.objects[f"TOWER_CROWN_PEAK_{i}"], MAT_ROOF)
    set_size(ensure_cube(f"TOWER_CROWN_PEAK_TIP_{i}"), 0.65, 0.65, 1.4, bottom_z=33.2, center_xy=(CX + dx, CY + dy))
    assign(bpy.data.objects[f"TOWER_CROWN_PEAK_TIP_{i}"], MAT_ROOF)

# ========== TOWER WINDOW RHYTHM (mockup: regular grid) ==========
# Front: 3 rows x 2 + center upper banner zone
for row, z in enumerate([12.0, 15.5, 19.0, 22.5]):
    for col, xoff in enumerate([-1.7, 1.7]):
        set_size(ensure_cube(f"TOWER_WIN_F_{row}_{col}"), 1.15, 0.35, 1.7, bottom_z=z, center_xy=(CX + xoff, CY + 3.55))
        assign(bpy.data.objects[f"TOWER_WIN_F_{row}_{col}"], MAT_GLASS)
        set_size(ensure_cube(f"WIN_FRAME_F_{row}_{col}"), 1.4, 0.22, 2.0, bottom_z=z - 0.08, center_xy=(CX + xoff, CY + 3.65))
        assign(bpy.data.objects[f"WIN_FRAME_F_{row}_{col}"], MAT_GOLD)

# Side windows L/R on shaft
for side, x, ysign in [("L", CX - 3.5, 1), ("R", CX + 3.5, 1)]:
    for row, z in enumerate([13.0, 17.0, 21.0]):
        for col, yoff in enumerate([-1.2, 1.2]):
            n = f"TOWER_WIN_{side}_{row}_{col}"
            set_size(ensure_cube(n), 0.35, 1.1, 1.6, bottom_z=z, center_xy=(x, CY + yoff))
            assign(bpy.data.objects[n], MAT_GLASS)

# Big mid banner taller (mockup signature)
set_size(ensure_cube("BANNER_PANEL_MID"), 2.2, 0.12, 5.5, bottom_z=15.5, center_xy=(CX, CY + 3.65))
assign(bpy.data.objects["BANNER_PANEL_MID"], MAT_BANNER)
set_size(ensure_cube("EMBLEM_PLATE_MAIN"), 1.5, 0.14, 1.7, bottom_z=17.8, center_xy=(CX, CY + 3.72))
assign(bpy.data.objects["EMBLEM_PLATE_MAIN"], MAT_GOLD)
set_size(ensure_cube("BANNER_MOUNT_MID"), 2.4, 0.2, 0.25, bottom_z=20.9, center_xy=(CX, CY + 3.7))
assign(bpy.data.objects["BANNER_MOUNT_MID"], MAT_GOLD)

# ========== LEFT HALL GABLES more pointed ==========
for i, gx in enumerate([-10.5, -9.0, -7.5, -6.0, -4.5, -3.2]):
    set_size(ensure_cube(f"BARRACKS_ROOF_GABLE_{i}"), 1.6, 3.2, 2.8, bottom_z=13.0, center_xy=(gx, 4.6))
    assign(bpy.data.objects[f"BARRACKS_ROOF_GABLE_{i}"], MAT_ROOF)
    set_size(ensure_cube(f"BARRACKS_GABLE_CAP_{i}"), 0.85, 0.85, 1.6, bottom_z=15.5, center_xy=(gx, 4.6))
    assign(bpy.data.objects[f"BARRACKS_GABLE_CAP_{i}"], MAT_ROOF)
    set_size(ensure_cube(f"BARRACKS_GABLE_POINT_{i}"), 0.45, 0.45, 1.1, bottom_z=16.9, center_xy=(gx, 4.6))
    assign(bpy.data.objects[f"BARRACKS_GABLE_POINT_{i}"], MAT_ROOF)
    set_size(ensure_cube(f"GOLD_GABLE_TIP_L_{i}"), 0.18, 0.18, 0.6, bottom_z=17.9, center_xy=(gx, 4.6))
    assign(bpy.data.objects[f"GOLD_GABLE_TIP_L_{i}"], MAT_GOLD)

# Central hall gable taller
set_size(ensure_cube("BARRACKS_GABLE_ROOF"), 4.0, 4.5, 4.0, bottom_z=13.0, center_xy=(-6.0, 4.8))
assign(bpy.data.objects["BARRACKS_GABLE_ROOF"], MAT_ROOF)
set_size(ensure_cube("BARRACKS_GABLE_PEAK"), 1.8, 1.8, 2.4, bottom_z=16.8, center_xy=(-6.0, 4.8))
assign(bpy.data.objects["BARRACKS_GABLE_PEAK"], MAT_ROOF)
set_size(ensure_cube("BARRACKS_GABLE_APEX"), 0.7, 0.7, 1.2, bottom_z=19.0, center_xy=(-6.0, 4.8))
assign(bpy.data.objects["BARRACKS_GABLE_APEX"], MAT_ROOF)

# Corner turret roof pointed
set_size(ensure_cube("BAR_TURRET_FRONT_L_ROOF"), 2.6, 2.6, 2.2, bottom_z=12.5, center_xy=(-10.5, 5.5))
assign(bpy.data.objects["BAR_TURRET_FRONT_L_ROOF"], MAT_ROOF)
set_size(ensure_cube("BAR_TURRET_L_POINT"), 1.2, 1.2, 1.8, bottom_z=14.5, center_xy=(-10.5, 5.5))
assign(bpy.data.objects["BAR_TURRET_L_POINT"], MAT_ROOF)
set_size(ensure_cube("GOLD_TURRET_L_TIP"), 0.2, 0.2, 0.7, bottom_z=16.1, center_xy=(-10.5, 5.5))
assign(bpy.data.objects["GOLD_TURRET_L_TIP"], MAT_GOLD)

# ========== PORTAL more mockup-like ==========
set_size(ensure_cube("MAIN_PORTAL_ARCH"), 4.2, 1.0, 6.0, bottom_z=5.0, center_xy=(CX, CY + 4.3))
assign(bpy.data.objects["MAIN_PORTAL_ARCH"], MAT_STONE)
set_size(ensure_cube("MAIN_PORTAL_DOOR"), 2.6, 0.35, 4.8, bottom_z=5.2, center_xy=(CX, CY + 4.55))
assign(bpy.data.objects["MAIN_PORTAL_DOOR"], MAT_WOOD)
set_size(ensure_cube("PORTAL_GOLD_TRIM"), 4.5, 0.25, 0.3, bottom_z=10.8, center_xy=(CX, CY + 4.4))
assign(bpy.data.objects["PORTAL_GOLD_TRIM"], MAT_GOLD)

# Apply new meshes
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    n = o.name
    if any(n.startswith(p) for p in (
        "TOWER_SPIRE", "TOWER_CENTRAL", "TOWER_CROWN", "TOWER_WIN", "WIN_FRAME",
        "FLAG_", "BANNER_", "EMBLEM_", "BARRACKS_GABLE", "BARRACKS_ROOF_GABLE",
        "BAR_TURRET", "GOLD_", "MAIN_PORTAL", "PORTAL_GOLD", "BARRACKS_GABLE_POINT",
        "BARRACKS_GABLE_APEX", "BARRACKS_GABLE_CAP",
    )):
        try:
            for x in bpy.data.objects:
                x.select_set(False)
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        except Exception:
            pass

# Soft clamp anything above 40m
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    top = o.location.z + o.dimensions.z / 2.0
    if top > 40.5:
        o.location.z -= (top - 39.8)

# Bounds
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V06_CROWN.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V06")

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

print("TICK28_DONE")

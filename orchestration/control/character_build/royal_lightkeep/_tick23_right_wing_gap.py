# -*- coding: utf-8 -*-
"""Tick #23: reopen FINAL — fix right-wing roof overlap (blue slab on tower) + courtyard gap."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend")
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

# Tower right face approx x ≈ 6.5 (center 1.5, half ~5)
# Keep right wing LEFT EDGE >= 10.5 for courtyard gap
DX = 4.0  # shift right cluster +X

def shift(name, dx=DX, dy=0.0):
    o = bpy.data.objects.get(name)
    if not o:
        return
    o.location.x += dx
    o.location.y += dy
    print("SHIFT", name, round(o.location.x, 2), round(o.location.y, 2))

right_cluster = [
    "RIGHT_WING_MAIN", "RIGHT_WING_ROOF", "RIGHT_WING_APRON",
    "RIGHT_PAVILION", "RIGHT_PAVILION_ROOF", "RIGHT_PAVILION_PEAK", "GOLD_PAVILION_TIP",
    "RIGHT_GATEHOUSE", "RIGHT_GATE_ROOF", "RIGHT_GATE_SIDE_L", "RIGHT_GATE_SIDE_R",
    "RIGHT_GATE_TUNNEL", "RIGHT_GATE_TUNNEL_TOP", "RIGHT_TUNNEL_TOP",
    "RIGHT_TUNNEL_WALL_L", "RIGHT_TUNNEL_WALL_R", "RIGHT_TUNNEL_VOID",
    "RIGHT_L_ARM", "RIGHT_L_ARM_ROOF",
    "RIGHT_TURRET_A", "RIGHT_TURRET_A_ROOF", "RIGHT_TURRET_B", "RIGHT_TURRET_B_ROOF",
    "RIGHT_ROOF_GABLE_0", "RIGHT_ROOF_GABLE_1", "RIGHT_ROOF_GABLE_2", "RIGHT_ROOF_GABLE_3",
    "RIGHT_BUTTRESS_0", "RIGHT_BUTTRESS_1", "RIGHT_BUTTRESS_2",
    "RIGHT_COURTYARD_FACE", "RIGHT_WIN_0", "RIGHT_WIN_1", "RIGHT_WIN_2",
    "CONNECTOR_TO_RIGHT",
]
for n in right_cluster:
    shift(n, DX, 0.0)

# Also shift side stairs if present
for i in range(6):
    shift(f"RIGHT_SIDE_STAIR_{i}", DX, 0.0)

# Resize wing roof smaller in X so it stays on the wing (left edge clear of tower)
o = bpy.data.objects.get("RIGHT_WING_ROOF")
if o:
    # place center further right, width 11 → left edge ~ center-5.5
    set_size(o, 11.0, 10.5, 3.5, bottom_z=14.2, center_xy=(18.5, -1.5))
    assign(o, MAT_ROOF)
    print("RESIZE RIGHT_WING_ROOF", o.location, o.dimensions)

o = bpy.data.objects.get("RIGHT_WING_MAIN")
if o:
    set_size(o, 11.0, 10.5, 8.0, bottom_z=6.0, center_xy=(18.5, -1.0))
    assign(o, MAT_STONE)

# Connector: thin bridge only, limestone, not a blue wall
o = bpy.data.objects.get("CONNECTOR_TO_RIGHT")
if o:
    set_size(o, 5.5, 3.0, 5.5, bottom_z=6.5, center_xy=(10.5, 4.0))
    assign(o, MAT_STONE)

# Slim GH right wall so it doesn't read as mass against tower
o = bpy.data.objects.get("GH_WALL_R")
if o:
    set_size(o, 1.2, 8.0, 9.0, bottom_z=6.5, center_xy=(6.2, 4.5))
    assign(o, MAT_STONE)

# Courtyard ground pad (visual void between tower and right wing)
pad = ensure_cube("COURTYARD_PAD_RIGHT")
set_size(pad, 6.0, 14.0, 0.35, bottom_z=0.4, center_xy=(11.5, 0.0))
assign(pad, MAT_DARK)

# Ensure no vertical wall has slate roof mat by mistake
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    n = o.name.upper()
    mats = [s.material.name if s.material else "" for s in o.material_slots]
    if any("SLATE" in m for m in mats):
        # if tall thin vertical (not roof-like flat), reassign to stone
        d = o.dimensions
        if d.z > 6.0 and d.z > d.x and d.z > d.y and "ROOF" not in n and "SPIRE" not in n and "HIP" not in n and "GABLE" not in n and "PEAK" not in n and "CAP" not in n:
            assign(o, MAT_STONE)
            print("DE-SLATE", o.name)

# Apply scale on edited
for name in ("RIGHT_WING_ROOF", "RIGHT_WING_MAIN", "CONNECTOR_TO_RIGHT", "GH_WALL_R", "COURTYARD_PAD_RIGHT"):
    o = bpy.data.objects.get(name)
    if not o:
        continue
    try:
        for x in bpy.data.objects:
            x.select_set(False)
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    except Exception:
        pass

# Verify left edge of RIGHT_WING_ROOF
o = bpy.data.objects.get("RIGHT_WING_ROOF")
if o:
    left = o.location.x - o.dimensions.x / 2
    print("WING_ROOF_LEFT_EDGE", round(left, 2), "OK" if left >= 10.0 else "STILL_OVERLAP")

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
scene.render.image_settings.file_format = "PNG"

final_path = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend")
p8f = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_FINAL.blend")
bpy.ops.wm.save_as_mainfile(filepath=final_path)
shutil.copy2(final_path, p8f)
shutil.copy2(final_path, LOOP)
print("SAVED FINAL")

out_final = os.path.join(BASE, "renders_final")
out_work = os.path.join(BASE, "renders_pass1d")
out8 = os.path.join(BASE, "renders_pass8")
for d in (out_final, out_work, out8):
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
    ("CAM_05_FRONT_3Q", out8, "pass8_front_3q.png"),
    ("CAM_01_FRONT", out8, "pass8_front.png"),
    ("CAM_TOP_PLAN", out8, "pass8_top.png"),
]
for cam, dest, fn in jobs:
    c = bpy.data.objects.get(cam)
    if not c:
        continue
    scene.camera = c
    scene.render.filepath = os.path.join(dest, fn)
    bpy.ops.render.render(write_still=True)
    print("OK", fn)

# Update deviation note
dev = os.path.join(BASE, "FINAL_DEVIATION_REPORT.md")
with open(dev, "a", encoding="utf-8") as f:
    f.write(f"\n\n## Patch tick #23 ({STAMP})\n")
    f.write("- Reopened FINAL: right wing cluster shifted +4m X; wing roof resized; connector slimmed\n")
    f.write("- Goal: remove blue vertical slab (RIGHT_WING_ROOF overlap on tower) + courtyard gap\n")
    f.write("- accepted (user) still false\n")
print("TICK23_DONE")

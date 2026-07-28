# -*- coding: utf-8 -*-
"""
Tick #25 — Human overlay reject: rebuild FRONT silhouette toward M0 mockup.
Primary ref: mockup_royal_lightkeep front + mockup_overlay_front_compare.png
"""
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
print("OPEN", bpy.data.filepath, "OBJ", len(bpy.data.objects))

backup = os.path.join(BASE, f"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_BACKUP_LOOP_{STAMP}.blend")
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True)
print("BACKUP", backup)

# Clear FINAL flag — Human rejected overlay match
flag = os.path.join(BASE, "ASSET_FINAL_COMPLETE.flag")
with open(flag, "w", encoding="utf-8") as f:
    f.write("false\nREOPENED_HUMAN_OVERLAY_REJECT\naccepted=false\n")

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
    m.diffuse_color = (*color, 1.0)
    return m

def assign(obj, mat):
    if not obj or obj.type != "MESH":
        return
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def hide(name):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = True
        o.hide_viewport = True

MAT_STONE = make_mat("MAT_LIMESTONE", (0.78, 0.74, 0.66), 0.82, 0.0)
MAT_ROOF = make_mat("MAT_SLATE_NAVY", (0.10, 0.16, 0.30), 0.50, 0.04)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.82, 0.62, 0.24), 0.28, 0.90)
MAT_DARK = make_mat("MAT_DARK_STONE", (0.22, 0.21, 0.20), 0.92, 0.0)
MAT_BANNER = make_mat("MAT_BANNER_BLUE", (0.07, 0.14, 0.42), 0.62, 0.0)
MAT_GLASS = make_mat("MAT_GLASS", (0.45, 0.58, 0.72), 0.12, 0.0)
MAT_WOOD = make_mat("MAT_WOOD", (0.28, 0.16, 0.08), 0.72, 0.0)

# ============================================================
# FRONT SILHOUETTE TARGET (mockup)
# - Tower CENTER, tall ~38m, relatively narrow shaft
# - Left hall: wide multi-gable, lower than tower, steep roofs
# - Right of tower: LOWER secondary mass (not tall blue wall)
# - Wide central stairs to main portal
# - Continuous fort base / outer wall
# World: +Y front, origin-ish tower at CX
# ============================================================
CX, CY = 0.0, 4.0  # shift tower slightly to match mockup center-right feel → keep 0 for simplicity

# ---------- TOWER: taller, narrower shaft (mockup proportion) ----------
set_size(ensure_cube("TOWER_SHAFT"), 8.0, 8.0, 16.0, bottom_z=10.0, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_SHAFT"], MAT_STONE)

set_size(ensure_cube("TOWER_PORTAL_SHOULDER"), 10.0, 4.0, 10.0, bottom_z=4.0, center_xy=(CX, CY + 3.5))
assign(bpy.data.objects["TOWER_PORTAL_SHOULDER"], MAT_STONE)

# Base plinth under tower
set_size(ensure_cube("TOWER_BASE_PLINTH"), 12.0, 12.0, 4.0, bottom_z=0.0, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_BASE_PLINTH"], MAT_STONE)

# Mid observation / upper block
set_size(ensure_cube("TOWER_OBSERVATION_BLOCK"), 10.0, 10.0, 5.0, bottom_z=26.0, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_OBSERVATION_BLOCK"], MAT_STONE)

set_size(ensure_cube("TOWER_MID_BELT"), 9.0, 9.0, 1.4, bottom_z=24.5, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_MID_BELT"], MAT_STONE)

# Crown multi-spire (mockup: central + 4 corners + finials)
set_size(ensure_cube("TOWER_HIP_BASE"), 11.0, 11.0, 1.5, bottom_z=30.5, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_HIP_BASE"], MAT_ROOF)
set_size(ensure_cube("TOWER_ROOF_BLOCK"), 7.0, 7.0, 3.0, bottom_z=31.8, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_ROOF_BLOCK"], MAT_ROOF)
set_size(ensure_cube("TOWER_ROOF_PEAK"), 3.0, 3.0, 2.5, bottom_z=34.5, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_ROOF_PEAK"], MAT_ROOF)

# 4 corner turrets on crown
for i, (dx, dy) in enumerate([(-4.0, -4.0), (4.0, -4.0), (-4.0, 4.0), (4.0, 4.0)]):
    mass = ensure_cube(f"TOWER_CORNER_MASS_{i}")
    set_size(mass, 2.8, 2.8, 5.0, bottom_z=29.5, center_xy=(CX + dx, CY + dy))
    assign(mass, MAT_STONE)
    sp = ensure_cube(f"TOWER_SPIRE_{i}")
    set_size(sp, 2.0, 2.0, 4.5, bottom_z=34.0, center_xy=(CX + dx, CY + dy))
    assign(sp, MAT_ROOF)
    tip = ensure_cube(f"GOLD_SPIRE_TIP_{i}")
    set_size(tip, 0.35, 0.35, 1.2, bottom_z=38.2, center_xy=(CX + dx, CY + dy))
    assign(tip, MAT_GOLD)

# Central flag finial
set_size(ensure_cube("GOLD_FINIAL_PEAK"), 0.45, 0.45, 2.0, bottom_z=36.5, center_xy=(CX, CY))
assign(bpy.data.objects["GOLD_FINIAL_PEAK"], MAT_GOLD)
set_size(ensure_cube("FINIAL_MAIN"), 0.3, 0.3, 1.5, bottom_z=38.2, center_xy=(CX, CY))
assign(bpy.data.objects["FINIAL_MAIN"], MAT_GOLD)

# Front big blue banner (mockup hero element)
set_size(ensure_cube("BANNER_PANEL_MID"), 2.2, 0.12, 5.5, bottom_z=18.0, center_xy=(CX, CY + 4.2))
assign(bpy.data.objects["BANNER_PANEL_MID"], MAT_BANNER)
set_size(ensure_cube("EMBLEM_PLATE_MAIN"), 1.6, 0.15, 1.8, bottom_z=20.5, center_xy=(CX, CY + 4.25))
assign(bpy.data.objects["EMBLEM_PLATE_MAIN"], MAT_GOLD)

# Side banners portal
for side, x in [("L", CX - 3.5), ("R", CX + 3.5)]:
    o = ensure_cube(f"BANNER_PANEL_{side}")
    set_size(o, 1.2, 0.1, 2.5, bottom_z=10.0, center_xy=(x, CY + 4.5))
    assign(o, MAT_BANNER)

# Portal door wood
set_size(ensure_cube("MAIN_PORTAL_DOOR"), 3.5, 0.4, 5.5, bottom_z=5.5, center_xy=(CX, CY + 5.2))
assign(bpy.data.objects["MAIN_PORTAL_DOOR"], MAT_WOOD)
set_size(ensure_cube("MAIN_PORTAL_ARCH"), 4.5, 1.0, 6.5, bottom_z=5.0, center_xy=(CX, CY + 5.0))
assign(bpy.data.objects["MAIN_PORTAL_ARCH"], MAT_STONE)

# ---------- MAIN STAIRS (mockup: wide, central, dominant) ----------
# Hide old scattered steps that fight silhouette
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    n = o.name.upper()
    if n.startswith("MAIN_STAIR") or n.startswith("STAIR_RAIL"):
        # keep and rebuild key ones below
        pass

# Wide cascade — mockup has ~10+ wide steps
for i in range(12):
    y = 22.0 - i * 1.15
    z = i * 0.55
    w = 11.0 - i * 0.15
    o = ensure_cube(f"MAIN_STAIR_STEP_{i}")
    set_size(o, w, 1.2, 0.6, bottom_z=z, center_xy=(CX, y))
    assign(o, MAT_STONE)

# Stair side walls
for side, x in [("L", CX - 6.0), ("R", CX + 6.0)]:
    o = ensure_cube(f"MAIN_STAIR_WALL_{side}")
    set_size(o, 0.8, 14.0, 3.2, bottom_z=0.0, center_xy=(x, 15.0))
    assign(o, MAT_STONE)
    r = ensure_cube(f"STAIR_RAIL_{side}")
    set_size(r, 0.25, 13.0, 0.8, bottom_z=2.5, center_xy=(x, 15.0))
    assign(r, MAT_GOLD)

# ---------- LEFT BARRACKS HALL (mockup: multi-gable gothic hall) ----------
# Body lower than tower, wide on -X
set_size(ensure_cube("BARRACKS_LEFT_MAIN"), 20.0, 10.0, 10.0, bottom_z=4.0, center_xy=(-14.0, 2.0))
assign(bpy.data.objects["BARRACKS_LEFT_MAIN"], MAT_STONE)

# Steep multi-gable roof planes (front-facing peaks)
set_size(ensure_cube("BARRACKS_LEFT_ROOF"), 21.0, 11.0, 5.0, bottom_z=13.5, center_xy=(-14.0, 2.0))
assign(bpy.data.objects["BARRACKS_LEFT_ROOF"], MAT_ROOF)

# Central tall gable (mockup middle gable on hall)
set_size(ensure_cube("BARRACKS_GABLE_ROOF"), 8.0, 6.0, 5.5, bottom_z=15.5, center_xy=(-12.0, 5.5))
assign(bpy.data.objects["BARRACKS_GABLE_ROOF"], MAT_ROOF)
set_size(ensure_cube("BARRACKS_GABLE_PEAK"), 3.5, 3.0, 3.0, bottom_z=20.5, center_xy=(-12.0, 5.5))
assign(bpy.data.objects["BARRACKS_GABLE_PEAK"], MAT_ROOF)

# Side gables along front
for i, gx in enumerate([-20.0, -16.0, -8.0, -4.5]):
    o = ensure_cube(f"BARRACKS_ROOF_GABLE_{i}")
    set_size(o, 3.5, 5.0, 4.0, bottom_z=16.0, center_xy=(gx, 5.5))
    assign(o, MAT_ROOF)
    cap = ensure_cube(f"BARRACKS_GABLE_CAP_{i}")
    set_size(cap, 1.4, 1.4, 1.8, bottom_z=19.5, center_xy=(gx, 5.5))
    assign(cap, MAT_ROOF)

# Left corner turret (mockup far-left round turret)
set_size(ensure_cube("BAR_TURRET_FRONT_L"), 4.0, 4.0, 12.0, bottom_z=3.0, center_xy=(-24.0, 5.0))
assign(bpy.data.objects["BAR_TURRET_FRONT_L"], MAT_STONE)
set_size(ensure_cube("BAR_TURRET_FRONT_L_ROOF"), 3.5, 3.5, 3.5, bottom_z=14.5, center_xy=(-24.0, 5.0))
assign(bpy.data.objects["BAR_TURRET_FRONT_L_ROOF"], MAT_ROOF)

# Gold eaves
set_size(ensure_cube("GOLD_EAVES_BAR_F"), 20.0, 0.25, 0.3, bottom_z=13.8, center_xy=(-14.0, 7.0))
assign(bpy.data.objects["GOLD_EAVES_BAR_F"], MAT_GOLD)

# ---------- RIGHT SIDE (mockup: LOWER secondary, not tall blue wall) ----------
# Pull right mass DOWN and more compact for front silhouette
set_size(ensure_cube("RIGHT_WING_MAIN"), 10.0, 9.0, 8.0, bottom_z=4.0, center_xy=(12.0, 0.0))
assign(bpy.data.objects["RIGHT_WING_MAIN"], MAT_STONE)

# Roof low and multi-peak, not a tall vertical slab
set_size(ensure_cube("RIGHT_WING_ROOF"), 11.0, 10.0, 3.5, bottom_z=11.5, center_xy=(12.0, 0.0))
assign(bpy.data.objects["RIGHT_WING_ROOF"], MAT_ROOF)

for i, (gx, gy) in enumerate([(9.0, 2.0), (14.0, 1.0), (11.0, -2.0)]):
    o = ensure_cube(f"RIGHT_ROOF_GABLE_{i}")
    set_size(o, 3.0, 3.5, 2.8, bottom_z=14.0, center_xy=(gx, gy))
    assign(o, MAT_ROOF)

# Small pavilion lower
set_size(ensure_cube("RIGHT_PAVILION"), 6.0, 6.0, 7.0, bottom_z=3.5, center_xy=(16.0, -5.0))
assign(bpy.data.objects["RIGHT_PAVILION"], MAT_STONE)
set_size(ensure_cube("RIGHT_PAVILION_ROOF"), 7.0, 7.0, 3.0, bottom_z=10.0, center_xy=(16.0, -5.0))
assign(bpy.data.objects["RIGHT_PAVILION_ROOF"], MAT_ROOF)
set_size(ensure_cube("RIGHT_PAVILION_PEAK"), 2.2, 2.2, 2.0, bottom_z=12.8, center_xy=(16.0, -5.0))
assign(bpy.data.objects["RIGHT_PAVILION_PEAK"], MAT_ROOF)

# Hide objects that create the bad tall blue slab / sprawl on right front
for name in [
    "RIGHT_L_ARM", "RIGHT_L_ARM_ROOF",
    "RIGHT_GATEHOUSE", "RIGHT_GATE_ROOF", "RIGHT_GATE_SIDE_L", "RIGHT_GATE_SIDE_R",
    "RIGHT_GATE_TUNNEL", "RIGHT_GATE_TUNNEL_TOP", "RIGHT_TUNNEL_TOP",
    "RIGHT_TUNNEL_WALL_L", "RIGHT_TUNNEL_WALL_R", "RIGHT_TUNNEL_VOID",
    "RIGHT_TURRET_A", "RIGHT_TURRET_A_ROOF", "RIGHT_TURRET_B", "RIGHT_TURRET_B_ROOF",
    "RIGHT_ROOF_GABLE_3", "RIGHT_COURTYARD_FACE",
    "RIGHT_WING_APRON", "CONNECTOR_TO_RIGHT",
    "COURTYARD_PAD_RIGHT",
]:
    hide(name)

# Small right corner fort turret (mockup low right)
set_size(ensure_cube("RIGHT_CORNER_TURRET"), 3.5, 3.5, 6.0, bottom_z=1.5, center_xy=(18.0, 8.0))
assign(bpy.data.objects["RIGHT_CORNER_TURRET"], MAT_STONE)
set_size(ensure_cube("RIGHT_CORNER_TURRET_ROOF"), 3.0, 3.0, 2.5, bottom_z=7.2, center_xy=(18.0, 8.0))
assign(bpy.data.objects["RIGHT_CORNER_TURRET_ROOF"], MAT_ROOF)

# ---------- OUTER WALL / BASE (mockup fortified platform) ----------
set_size(ensure_cube("LEVEL0_GROUND"), 55.0, 40.0, 0.8, bottom_z=-0.4, center_xy=(0.0, 2.0))
assign(bpy.data.objects["LEVEL0_GROUND"], MAT_DARK)

# Front fort wall
set_size(ensure_cube("OUTER_WALL_FRONT"), 40.0, 2.0, 3.5, bottom_z=0.0, center_xy=(0.0, 20.0))
assign(bpy.data.objects["OUTER_WALL_FRONT"], MAT_DARK)

# Corner bastions front
set_size(ensure_cube("BASTION_FL"), 4.0, 4.0, 5.0, bottom_z=0.0, center_xy=(-18.0, 18.0))
assign(bpy.data.objects["BASTION_FL"], MAT_DARK)
set_size(ensure_cube("BASTION_FR"), 4.0, 4.0, 5.0, bottom_z=0.0, center_xy=(18.0, 18.0))
assign(bpy.data.objects["BASTION_FR"], MAT_DARK)

# Tower shoulders L/R lower attachment
set_size(ensure_cube("TOWER_SHOULDER_L"), 5.0, 5.0, 8.0, bottom_z=4.0, center_xy=(CX - 6.5, CY + 1.0))
assign(bpy.data.objects["TOWER_SHOULDER_L"], MAT_STONE)
set_size(ensure_cube("TOWER_SHOULDER_R"), 5.0, 5.0, 8.0, bottom_z=4.0, center_xy=(CX + 6.5, CY + 1.0))
assign(bpy.data.objects["TOWER_SHOULDER_R"], MAT_STONE)

# Connector left hall to tower
set_size(ensure_cube("CONNECTOR_TO_BARRACKS"), 6.0, 5.0, 9.0, bottom_z=4.0, center_xy=(-5.0, CY))
assign(bpy.data.objects["CONNECTOR_TO_BARRACKS"], MAT_STONE)
set_size(ensure_cube("CONNECTOR_ROOF"), 7.0, 6.0, 2.5, bottom_z=12.5, center_xy=(-5.0, CY))
assign(bpy.data.objects["CONNECTOR_ROOF"], MAT_ROOF)

# Windows on tower front (rows)
for row, z in enumerate([14.0, 18.0, 22.0]):
    for col, xoff in enumerate([-2.0, 2.0]):
        w = ensure_cube(f"TOWER_WIN_F_{row}_{col}")
        set_size(w, 1.4, 0.5, 2.0, bottom_z=z, center_xy=(CX + xoff, CY + 4.1))
        assign(w, MAT_GLASS)
        fr = ensure_cube(f"WIN_FRAME_F_{row}_{col}")
        set_size(fr, 1.7, 0.3, 2.3, bottom_z=z - 0.1, center_xy=(CX + xoff, CY + 4.2))
        assign(fr, MAT_GOLD)

# Hide old crown peaks that float wrong
for i in range(8):
    hide(f"TOWER_CROWN_PEAK_{i}")
for name in ["TOWER_HIP_EW", "TOWER_HIP_NS", "TOWER_GABLE_FRONT", "TOWER_GABLE_REAR",
             "TOWER_GABLE_LEFT", "TOWER_GABLE_RIGHT", "TOWER_FRONT_SPIRE_L", "TOWER_FRONT_SPIRE_R",
             "TOWER_OCT_SPIRE_0", "TOWER_OCT_SPIRE_1", "TOWER_OCT_SPIRE_2", "TOWER_OCT_SPIRE_3",
             "TOWER_OCT_SPIRE_4", "TOWER_OCT_SPIRE_5", "TOWER_OCT_SPIRE_6", "TOWER_OCT_SPIRE_7",
             "GOLD_CROWN_RING", "GOLD_CORNICE_OBS", "GOLD_CORNICE_MID"]:
    hide(name)

# Apply scale on key edited
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name.startswith(("MAIN_STAIR", "TOWER_", "BARRACKS_", "RIGHT_WING", "RIGHT_PAV", "RIGHT_CORNER",
                          "BANNER_", "MAIN_PORTAL", "BASTION_", "CONNECTOR_", "BAR_TURRET", "GOLD_", "FINIAL")):
        try:
            for x in bpy.data.objects:
                x.select_set(False)
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        except Exception:
            pass

# Cameras: keep, slight front adjust if needed — do NOT reset all
cam = bpy.data.objects.get("CAM_01_FRONT")
if cam:
    cam.location = Vector((0.0, 95.0, 28.0))
cam3 = bpy.data.objects.get("CAM_05_FRONT_3Q")
if cam3:
    cam3.location = Vector((55.0, 70.0, 32.0))

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

# Save as reopened work (not claiming FINAL complete)
out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V03_SILHOUETTE.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
# Update loop + working FINAL candidate (human still must accept)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V03 + FINAL + PASS1D")

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
    ("CAM_TOP_PLAN", out_final, "final_top.png"),
    ("CAM_01_FRONT", out8, "pass8_front.png"),
    ("CAM_05_FRONT_3Q", out8, "pass8_front_3q.png"),
]
for cam_name, dest, fn in jobs:
    c = bpy.data.objects.get(cam_name)
    if not c:
        print("MISS", cam_name)
        continue
    scene.camera = c
    scene.render.filepath = os.path.join(dest, fn)
    bpy.ops.render.render(write_still=True)
    print("OK", fn)

print("TICK25_DONE OBJ", len(bpy.data.objects))

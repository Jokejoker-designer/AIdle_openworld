# -*- coding: utf-8 -*-
"""
Tick #26 — P0 scale lock + front massing toward M0 sheet.
Sheet: H=38m, footprint 24x19m, wall 6.5m.
World: +Y = front, 1 BU = 1 m.
"""
import bpy
import os
import shutil
import bmesh
import math
from datetime import datetime
from mathutils import Vector, Euler

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V03_SILHOUETTE.blend")
LOOP = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Sheet scale
FP_X, FP_Y = 24.0, 19.0  # footprint
H_MAX = 38.0
WALL_H = 6.5

bpy.ops.wm.open_mainfile(filepath=WORK)
print("OPEN", bpy.data.filepath, "OBJ", len(bpy.data.objects))

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
    m.diffuse_color = (*color, 1.0)
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

# Hide ALL meshes first — then unhide/build only massing set
for o in bpy.data.objects:
    if o.type == "MESH":
        o.hide_render = True
        o.hide_viewport = True

# ============================================================
# COORDINATE SYSTEM for 24x19 footprint
# Center complex at origin; +Y front; ground z=0
# Tower near center-front of mass; left hall -X; right wing +X lower
# Footprint: X -12..+12, Y -8..+11 (approx 24 x 19)
# ============================================================
CX, CY = 1.0, 1.5  # tower center (slightly +X like mockup front)

# --- Ground / fort base (sheet wall 6.5m outer) ---
set_size(ensure_cube("LEVEL0_GROUND"), 24.0, 19.0, 0.6, bottom_z=-0.3, center_xy=(0.0, 1.0))
assign(bpy.data.objects["LEVEL0_GROUND"], MAT_DARK)

set_size(ensure_cube("FORT_BASE"), 22.0, 17.0, 2.2, bottom_z=0.0, center_xy=(0.0, 1.0))
assign(bpy.data.objects["FORT_BASE"], MAT_STONE)

# Outer wall ring segments (height ~6.5 from ground for outer fort)
set_size(ensure_cube("OUTER_WALL_FRONT"), 20.0, 1.2, WALL_H, bottom_z=0.0, center_xy=(0.0, 9.5))
assign(bpy.data.objects["OUTER_WALL_FRONT"], MAT_DARK)
set_size(ensure_cube("OUTER_WALL_REAR"), 20.0, 1.2, WALL_H, bottom_z=0.0, center_xy=(0.0, -7.5))
assign(bpy.data.objects["OUTER_WALL_REAR"], MAT_DARK)
set_size(ensure_cube("OUTER_WALL_LEFT"), 1.2, 16.0, WALL_H, bottom_z=0.0, center_xy=(-11.0, 1.0))
assign(bpy.data.objects["OUTER_WALL_LEFT"], MAT_DARK)
set_size(ensure_cube("OUTER_WALL_RIGHT"), 1.2, 16.0, WALL_H, bottom_z=0.0, center_xy=(11.0, 1.0))
assign(bpy.data.objects["OUTER_WALL_RIGHT"], MAT_DARK)

# Corner bastions
for name, x, y in [
    ("BASTION_FL", -10.0, 8.5),
    ("BASTION_FR", 10.0, 8.5),
    ("BASTION_RL", -10.0, -6.5),
    ("BASTION_RR", 10.0, -6.5),
]:
    set_size(ensure_cube(name), 3.0, 3.0, 7.5, bottom_z=0.0, center_xy=(x, y))
    assign(bpy.data.objects[name], MAT_DARK)
    set_size(ensure_cube(name + "_ROOF"), 2.6, 2.6, 1.8, bottom_z=7.2, center_xy=(x, y))
    assign(bpy.data.objects[name + "_ROOF"], MAT_ROOF)

# --- MAIN STAIRS (wide, front center, mockup dominant) ---
# From fort wall up to portal ~ z 6-7
for i in range(10):
    # y from 9.0 stepping toward tower front CY+3
    t = i / 9.0
    y = 9.2 - t * 5.5
    z = i * 0.65
    w = 7.5 - i * 0.12
    o = ensure_cube(f"MAIN_STAIR_STEP_{i}")
    set_size(o, w, 0.95, 0.7, bottom_z=z, center_xy=(CX, y))
    assign(o, MAT_STONE)

for side, x in [("L", CX - 4.2), ("R", CX + 4.2)]:
    set_size(ensure_cube(f"MAIN_STAIR_WALL_{side}"), 0.55, 6.5, 2.8, bottom_z=0.5, center_xy=(x, 6.5))
    assign(bpy.data.objects[f"MAIN_STAIR_WALL_{side}"], MAT_STONE)
    set_size(ensure_cube(f"STAIR_RAIL_{side}"), 0.2, 6.0, 0.55, bottom_z=2.2, center_xy=(x, 6.5))
    assign(bpy.data.objects[f"STAIR_RAIL_{side}"], MAT_GOLD)

# --- TOWER (sheet total 38m) ---
# Levels: base 0-8, shaft 8-24, obs 24-30, crown 30-38
set_size(ensure_cube("TOWER_BASE_PLINTH"), 9.0, 9.0, 3.0, bottom_z=2.0, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_BASE_PLINTH"], MAT_STONE)

set_size(ensure_cube("TOWER_PORTAL_SHOULDER"), 8.5, 4.0, 8.0, bottom_z=4.5, center_xy=(CX, CY + 2.8))
assign(bpy.data.objects["TOWER_PORTAL_SHOULDER"], MAT_STONE)

set_size(ensure_cube("MAIN_PORTAL_DOOR"), 2.8, 0.35, 4.5, bottom_z=5.5, center_xy=(CX, CY + 4.5))
assign(bpy.data.objects["MAIN_PORTAL_DOOR"], MAT_WOOD)

set_size(ensure_cube("MAIN_PORTAL_ARCH"), 3.8, 0.9, 5.5, bottom_z=5.0, center_xy=(CX, CY + 4.3))
assign(bpy.data.objects["MAIN_PORTAL_ARCH"], MAT_STONE)

set_size(ensure_cube("TOWER_SHAFT"), 7.0, 7.0, 14.0, bottom_z=10.0, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_SHAFT"], MAT_STONE)

set_size(ensure_cube("TOWER_MID_BELT"), 7.8, 7.8, 1.2, bottom_z=23.5, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_MID_BELT"], MAT_STONE)

set_size(ensure_cube("TOWER_OBSERVATION_BLOCK"), 8.5, 8.5, 4.5, bottom_z=24.8, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_OBSERVATION_BLOCK"], MAT_STONE)

# Corner buttress masses on observation
for i, (dx, dy) in enumerate([(-3.2, -3.2), (3.2, -3.2), (-3.2, 3.2), (3.2, 3.2)]):
    set_size(ensure_cube(f"TOWER_CORNER_MASS_{i}"), 2.4, 2.4, 5.0, bottom_z=28.5, center_xy=(CX + dx, CY + dy))
    assign(bpy.data.objects[f"TOWER_CORNER_MASS_{i}"], MAT_STONE)

# Crown roofs + spires → top ~38m
set_size(ensure_cube("TOWER_HIP_BASE"), 9.5, 9.5, 1.4, bottom_z=29.5, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_HIP_BASE"], MAT_ROOF)
set_size(ensure_cube("TOWER_ROOF_BLOCK"), 6.0, 6.0, 2.8, bottom_z=30.8, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_ROOF_BLOCK"], MAT_ROOF)
set_size(ensure_cube("TOWER_ROOF_PEAK"), 2.6, 2.6, 2.2, bottom_z=33.2, center_xy=(CX, CY))
assign(bpy.data.objects["TOWER_ROOF_PEAK"], MAT_ROOF)

for i, (dx, dy) in enumerate([(-3.2, -3.2), (3.2, -3.2), (-3.2, 3.2), (3.2, 3.2)]):
    set_size(ensure_cube(f"TOWER_SPIRE_{i}"), 1.8, 1.8, 4.0, bottom_z=32.5, center_xy=(CX + dx, CY + dy))
    assign(bpy.data.objects[f"TOWER_SPIRE_{i}"], MAT_ROOF)
    set_size(ensure_cube(f"GOLD_SPIRE_TIP_{i}"), 0.28, 0.28, 1.0, bottom_z=36.3, center_xy=(CX + dx, CY + dy))
    assign(bpy.data.objects[f"GOLD_SPIRE_TIP_{i}"], MAT_GOLD)

set_size(ensure_cube("GOLD_FINIAL_PEAK"), 0.4, 0.4, 1.8, bottom_z=35.2, center_xy=(CX, CY))
assign(bpy.data.objects["GOLD_FINIAL_PEAK"], MAT_GOLD)
set_size(ensure_cube("FINIAL_MAIN"), 0.25, 0.25, 1.2, bottom_z=36.8, center_xy=(CX, CY))
assign(bpy.data.objects["FINIAL_MAIN"], MAT_GOLD)

# Big front banner (mockup signature)
set_size(ensure_cube("BANNER_PANEL_MID"), 2.0, 0.1, 5.0, bottom_z=16.5, center_xy=(CX, CY + 3.6))
assign(bpy.data.objects["BANNER_PANEL_MID"], MAT_BANNER)
set_size(ensure_cube("EMBLEM_PLATE_MAIN"), 1.4, 0.12, 1.6, bottom_z=18.5, center_xy=(CX, CY + 3.65))
assign(bpy.data.objects["EMBLEM_PLATE_MAIN"], MAT_GOLD)

for side, x in [("L", CX - 2.8), ("R", CX + 2.8)]:
    set_size(ensure_cube(f"BANNER_PANEL_{side}"), 1.0, 0.08, 2.2, bottom_z=8.5, center_xy=(x, CY + 4.0))
    assign(bpy.data.objects[f"BANNER_PANEL_{side}"], MAT_BANNER)

# Tower windows front
for row, z in enumerate([12.5, 16.5, 20.5]):
    for col, xoff in enumerate([-1.6, 1.6]):
        set_size(ensure_cube(f"TOWER_WIN_F_{row}_{col}"), 1.2, 0.4, 1.8, bottom_z=z, center_xy=(CX + xoff, CY + 3.55))
        assign(bpy.data.objects[f"TOWER_WIN_F_{row}_{col}"], MAT_GLASS)
        set_size(ensure_cube(f"WIN_FRAME_F_{row}_{col}"), 1.45, 0.25, 2.1, bottom_z=z - 0.1, center_xy=(CX + xoff, CY + 3.65))
        assign(bpy.data.objects[f"WIN_FRAME_F_{row}_{col}"], MAT_GOLD)

# --- LEFT BARRACKS HALL (mockup: multi-gable, lower than tower) ---
# Occupies roughly X -11..-2, Y -3..+6
set_size(ensure_cube("BARRACKS_LEFT_MAIN"), 10.0, 8.5, 9.0, bottom_z=2.5, center_xy=(-6.5, 1.5))
assign(bpy.data.objects["BARRACKS_LEFT_MAIN"], MAT_STONE)

set_size(ensure_cube("BARRACKS_LEFT_ROOF"), 11.0, 9.5, 4.0, bottom_z=11.0, center_xy=(-6.5, 1.5))
assign(bpy.data.objects["BARRACKS_LEFT_ROOF"], MAT_ROOF)

# Front multi-gables (steep peaks like mockup)
for i, gx in enumerate([-10.0, -7.5, -5.0, -2.8]):
    set_size(ensure_cube(f"BARRACKS_ROOF_GABLE_{i}"), 2.4, 4.0, 3.5, bottom_z=13.5, center_xy=(gx, 4.5))
    assign(bpy.data.objects[f"BARRACKS_ROOF_GABLE_{i}"], MAT_ROOF)
    set_size(ensure_cube(f"BARRACKS_GABLE_CAP_{i}"), 1.1, 1.1, 1.5, bottom_z=16.5, center_xy=(gx, 4.5))
    assign(bpy.data.objects[f"BARRACKS_GABLE_CAP_{i}"], MAT_ROOF)

# Central tall gable on hall
set_size(ensure_cube("BARRACKS_GABLE_ROOF"), 4.5, 5.0, 4.5, bottom_z=13.0, center_xy=(-6.0, 4.8))
assign(bpy.data.objects["BARRACKS_GABLE_ROOF"], MAT_ROOF)
set_size(ensure_cube("BARRACKS_GABLE_PEAK"), 2.0, 2.0, 2.2, bottom_z=17.0, center_xy=(-6.0, 4.8))
assign(bpy.data.objects["BARRACKS_GABLE_PEAK"], MAT_ROOF)

# Far-left corner turret
set_size(ensure_cube("BAR_TURRET_FRONT_L"), 3.2, 3.2, 11.0, bottom_z=2.0, center_xy=(-10.5, 5.5))
assign(bpy.data.objects["BAR_TURRET_FRONT_L"], MAT_STONE)
set_size(ensure_cube("BAR_TURRET_FRONT_L_ROOF"), 2.8, 2.8, 2.8, bottom_z=12.5, center_xy=(-10.5, 5.5))
assign(bpy.data.objects["BAR_TURRET_FRONT_L_ROOF"], MAT_ROOF)

set_size(ensure_cube("GOLD_EAVES_BAR_F"), 10.5, 0.2, 0.25, bottom_z=11.2, center_xy=(-6.5, 5.5))
assign(bpy.data.objects["GOLD_EAVES_BAR_F"], MAT_GOLD)

# Connector tower-left
set_size(ensure_cube("CONNECTOR_TO_BARRACKS"), 3.5, 5.0, 8.0, bottom_z=3.0, center_xy=(-2.5, CY))
assign(bpy.data.objects["CONNECTOR_TO_BARRACKS"], MAT_STONE)
set_size(ensure_cube("CONNECTOR_ROOF"), 4.0, 5.5, 2.2, bottom_z=10.5, center_xy=(-2.5, CY))
assign(bpy.data.objects["CONNECTOR_ROOF"], MAT_ROOF)

# --- RIGHT WING (mockup: lower secondary, not tall slab) ---
set_size(ensure_cube("RIGHT_WING_MAIN"), 7.5, 7.0, 7.5, bottom_z=2.5, center_xy=(7.5, 0.5))
assign(bpy.data.objects["RIGHT_WING_MAIN"], MAT_STONE)
set_size(ensure_cube("RIGHT_WING_ROOF"), 8.5, 8.0, 3.2, bottom_z=9.5, center_xy=(7.5, 0.5))
assign(bpy.data.objects["RIGHT_WING_ROOF"], MAT_ROOF)

for i, (gx, gy) in enumerate([(5.5, 2.5), (8.5, 2.0), (7.0, -1.0)]):
    set_size(ensure_cube(f"RIGHT_ROOF_GABLE_{i}"), 2.2, 2.8, 2.4, bottom_z=12.0, center_xy=(gx, gy))
    assign(bpy.data.objects[f"RIGHT_ROOF_GABLE_{i}"], MAT_ROOF)

set_size(ensure_cube("RIGHT_PAVILION"), 4.5, 4.5, 6.5, bottom_z=2.5, center_xy=(9.0, -4.0))
assign(bpy.data.objects["RIGHT_PAVILION"], MAT_STONE)
set_size(ensure_cube("RIGHT_PAVILION_ROOF"), 5.2, 5.2, 2.5, bottom_z=8.5, center_xy=(9.0, -4.0))
assign(bpy.data.objects["RIGHT_PAVILION_ROOF"], MAT_ROOF)
set_size(ensure_cube("RIGHT_PAVILION_PEAK"), 1.8, 1.8, 1.6, bottom_z=10.8, center_xy=(9.0, -4.0))
assign(bpy.data.objects["RIGHT_PAVILION_PEAK"], MAT_ROOF)

set_size(ensure_cube("TOWER_SHOULDER_L"), 3.5, 4.0, 7.0, bottom_z=3.0, center_xy=(CX - 5.0, CY + 0.5))
assign(bpy.data.objects["TOWER_SHOULDER_L"], MAT_STONE)
set_size(ensure_cube("TOWER_SHOULDER_R"), 3.5, 4.0, 7.0, bottom_z=3.0, center_xy=(CX + 5.0, CY + 0.5))
assign(bpy.data.objects["TOWER_SHOULDER_R"], MAT_STONE)

# Courtyard void hint (dark floor behind front wall)
set_size(ensure_cube("COURTYARD_FLOOR"), 10.0, 6.0, 0.3, bottom_z=2.2, center_xy=(0.0, -2.0))
assign(bpy.data.objects["COURTYARD_FLOOR"], MAT_DARK)

# Presentation ground (outside footprint)
pg = ensure_cube("PRES_GROUND")
set_size(pg, 60.0, 50.0, 0.15, bottom_z=-0.5, center_xy=(0.0, 0.0))
assign(pg, make_mat("MAT_GROUND", (0.55, 0.52, 0.46), 0.95, 0.0))

# Scale human 1.8m at stair base
sh = ensure_cube("SCALE_HUMAN")
set_size(sh, 0.5, 0.35, 1.8, bottom_z=0.0, center_xy=(CX, 10.5))
assign(sh, make_mat("MAT_SCALE_HUMAN", (0.15, 0.15, 0.18), 0.8, 0.0))

# Apply scale on all visible meshes
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    try:
        for x in bpy.data.objects:
            x.select_set(False)
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    except Exception:
        pass

# Cameras — framing for 24x19 / 38m (do not wipe names)
def aim(cam, target=Vector((0, 1, 14))):
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

cams = {
    "CAM_01_FRONT": Vector((1.0, 42.0, 18.0)),
    "CAM_02_REAR": Vector((1.0, -40.0, 18.0)),
    "CAM_03_LEFT": Vector((-40.0, 1.0, 18.0)),
    "CAM_04_RIGHT": Vector((40.0, 1.0, 18.0)),
    "CAM_05_FRONT_3Q": Vector((28.0, 32.0, 20.0)),
    "CAM_06_REAR_3Q": Vector((-28.0, -30.0, 20.0)),
    "CAM_TOP_PLAN": Vector((0.0, 1.0, 55.0)),
}
for name, loc in cams.items():
    c = bpy.data.objects.get(name)
    if not c:
        # create if missing
        data = bpy.data.cameras.new(name)
        c = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(c)
    c.location = loc
    if name == "CAM_TOP_PLAN":
        c.rotation_euler = Euler((0, 0, 0), "XYZ")
        c.rotation_euler.x = math.radians(0)
        # top down
        c.rotation_euler = Euler((0, 0, 0), "XYZ")
        direction = Vector((0, 1, 0)) - c.location
        c.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    else:
        aim(c)
    if c.data:
        c.data.lens = 35 if "3Q" in name else 40
        if name == "CAM_TOP_PLAN":
            c.data.type = "ORTHO"
            c.data.ortho_scale = 40
        else:
            c.data.type = "PERSP"

# Lighting soft cream (keep if exist else create)
scene = bpy.context.scene
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()
bg = nt.nodes.new("ShaderNodeBackground")
bg.inputs[0].default_value = (0.82, 0.78, 0.70, 1.0)
bg.inputs[1].default_value = 1.1
out = nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(bg.outputs[0], out.inputs[0])

for lname in ("KEY_LIGHT", "FILL_LIGHT", "RIM_LIGHT", "SUN"):
    lo = bpy.data.objects.get(lname)
    if lo and lo.type == "LIGHT":
        bpy.data.objects.remove(lo, do_unlink=True)

def add_light(name, ltype, energy, loc, rot_deg, color=(1, 1, 1), size=10.0):
    data = bpy.data.lights.new(name=name, type=ltype)
    data.energy = energy
    data.color = color
    if ltype == "AREA":
        data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = Vector(loc)
    obj.rotation_euler = Euler(tuple(math.radians(a) for a in rot_deg), "XYZ")
    return obj

add_light("KEY_LIGHT", "AREA", 1200, (30, 40, 35), (-40, 0, 25), (1.0, 0.96, 0.9), 25)
add_light("FILL_LIGHT", "AREA", 350, (-35, 25, 25), (-30, 0, -35), (0.88, 0.92, 1.0), 30)
add_light("RIM_LIGHT", "AREA", 500, (-10, -40, 35), (-50, 0, 180), (1.0, 0.95, 0.88), 20)
add_light("SUN", "SUN", 1.8, (20, 30, 50), (-48, 0, 30), (1.0, 0.98, 0.94))

# Bounds check
minx = miny = minz = 1e9
maxx = maxy = maxz = -1e9
vis = 0
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name in ("PRES_GROUND", "SCALE_HUMAN"):
        continue
    vis += 1
    for corner in o.bound_box:
        w = o.matrix_world @ Vector(corner)
        minx = min(minx, w.x); maxx = max(maxx, w.x)
        miny = min(miny, w.y); maxy = max(maxy, w.y)
        minz = min(minz, w.z); maxz = max(maxz, w.z)
print("VISIBLE_MESH", vis)
print("BOUNDS_XYZ", round(maxx - minx, 2), round(maxy - miny, 2), round(maxz - minz, 2))
print("Z_RANGE", round(minz, 2), round(maxz, 2))
print("TARGET_FP", FP_X, FP_Y, "H", H_MAX)

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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V04_SCALE.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V04")

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
    ("CAM_01_FRONT", out8, "pass8_front.png"),
    ("CAM_05_FRONT_3Q", out8, "pass8_front_3q.png"),
    ("CAM_TOP_PLAN", out8, "pass8_top.png"),
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

print("TICK26_DONE")

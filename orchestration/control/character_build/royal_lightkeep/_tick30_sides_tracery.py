# -*- coding: utf-8 -*-
"""Tick #30: side stairs (mockup L), rear portal, parapet, more wall openings. Scale 24x19x38."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V07_CLAMP.blend")
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

# ========== LEFT SIDE STAIR (mockup view 3 — ramp along left) ==========
for i in range(8):
    # climb along -X side toward tower, y from front to mid
    t = i / 7.0
    y = 8.5 - t * 6.0
    z = i * 0.55
    o = ensure_cube(f"SIDE_STAIR_L_{i}")
    set_size(o, 2.2, 1.0, 0.55, bottom_z=z, center_xy=(-9.5, y))
    assign(o, MAT_STONE)
set_size(ensure_cube("SIDE_STAIR_L_RAIL"), 0.2, 7.0, 0.45, bottom_z=2.0, center_xy=(-10.6, 5.0))
assign(bpy.data.objects["SIDE_STAIR_L_RAIL"], MAT_GOLD)

# ========== RIGHT SIDE STAIR (mockup view 4 — smaller) ==========
for i in range(6):
    t = i / 5.0
    y = 7.5 - t * 5.0
    z = i * 0.5
    o = ensure_cube(f"SIDE_STAIR_R_{i}")
    set_size(o, 2.0, 0.9, 0.5, bottom_z=z, center_xy=(9.5, y))
    assign(o, MAT_STONE)

# ========== REAR PORTAL (mockup view 2) ==========
set_size(ensure_cube("REAR_PORTAL_ARCH"), 4.0, 1.0, 5.0, bottom_z=2.5, center_xy=(CX, CY - 3.5))
assign(bpy.data.objects["REAR_PORTAL_ARCH"], MAT_STONE)
set_size(ensure_cube("REAR_PORTAL_DOOR"), 2.5, 0.35, 4.0, bottom_z=2.8, center_xy=(CX, CY - 3.7))
assign(bpy.data.objects["REAR_PORTAL_DOOR"], MAT_WOOD)
set_size(ensure_cube("BANNER_REAR_L"), 1.0, 0.1, 2.0, bottom_z=6.0, center_xy=(CX - 2.8, CY - 3.6))
assign(bpy.data.objects["BANNER_REAR_L"], MAT_BANNER)
set_size(ensure_cube("BANNER_REAR_R"), 1.0, 0.1, 2.0, bottom_z=6.0, center_xy=(CX + 2.8, CY - 3.6))
assign(bpy.data.objects["BANNER_REAR_R"], MAT_BANNER)

# Split rear outer wall for rear gate gap
owr = bpy.data.objects.get("OUTER_WALL_REAR")
if owr:
    set_size(ensure_cube("OUTER_WALL_REAR_L"), 6.0, 1.2, 5.5, bottom_z=0.0, center_xy=(-6.0, -7.5))
    assign(bpy.data.objects["OUTER_WALL_REAR_L"], MAT_DARK)
    set_size(ensure_cube("OUTER_WALL_REAR_R"), 6.0, 1.2, 5.5, bottom_z=0.0, center_xy=(7.0, -7.5))
    assign(bpy.data.objects["OUTER_WALL_REAR_R"], MAT_DARK)
    owr.hide_render = True
    owr.hide_viewport = True

# ========== PARAPET on outer walls ==========
for name, x, y, sx, sy in [
    ("PARAPET_FRONT_L", -6.5, 9.5, 6.0, 0.9),
    ("PARAPET_FRONT_R", 7.5, 9.5, 6.0, 0.9),
    ("PARAPET_LEFT", -11.0, 1.0, 0.9, 14.0),
    ("PARAPET_RIGHT", 11.0, 1.0, 0.9, 14.0),
]:
    set_size(ensure_cube(name), sx, sy, 1.2, bottom_z=5.5, center_xy=(x, y))
    assign(bpy.data.objects[name], MAT_DARK)

# ========== ARROW SLITS on outer walls (mockup) ==========
for i, x in enumerate([-8.0, -5.0, 5.5, 8.5]):
    o = ensure_cube(f"ARROW_SLIT_F_{i}")
    set_size(o, 0.35, 0.5, 1.2, bottom_z=3.0, center_xy=(x, 9.3 if x < 0 else 9.3))
    # place on correct wall segment
    assign(o, MAT_DARK)
    # dark recess looks like slit
    o2 = ensure_cube(f"ARROW_SLIT_F_VOID_{i}")
    set_size(o2, 0.25, 0.6, 1.0, bottom_z=3.1, center_xy=(x, 9.55))
    assign(o2, MAT_GLASS)

# ========== TOWER MID TRACERY — vertical mullions on front windows ==========
for row, z in enumerate([12.0, 15.5, 19.0, 22.5]):
    for col, xoff in enumerate([-1.7, 1.7]):
        m = ensure_cube(f"WIN_MULLION_F_{row}_{col}")
        set_size(m, 0.12, 0.28, 1.7, bottom_z=z, center_xy=(CX + xoff, CY + 3.7))
        assign(m, MAT_GOLD)

# ========== MORE BANNERS on outer bastions ==========
for name, x, y in [("BANNER_BAST_FL", -10.0, 8.8), ("BANNER_BAST_FR", 10.0, 8.8)]:
    set_size(ensure_cube(name), 0.9, 0.1, 1.8, bottom_z=4.5, center_xy=(x, y))
    assign(bpy.data.objects[name], MAT_BANNER)

# ========== COURTYARD clarity — lower inner wall segments ==========
set_size(ensure_cube("COURTYARD_INNER_L"), 0.8, 4.0, 4.0, bottom_z=2.5, center_xy=(-3.5, -1.0))
assign(bpy.data.objects["COURTYARD_INNER_L"], MAT_STONE)
set_size(ensure_cube("COURTYARD_INNER_R"), 0.8, 4.0, 4.0, bottom_z=2.5, center_xy=(4.5, -1.0))
assign(bpy.data.objects["COURTYARD_INNER_R"], MAT_STONE)

# Apply
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name.startswith((
        "SIDE_STAIR", "REAR_PORTAL", "BANNER_REAR", "OUTER_WALL_REAR_",
        "PARAPET_", "ARROW_SLIT", "WIN_MULLION", "BANNER_BAST", "COURTYARD_INNER",
    )):
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V08_SIDES.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V08")

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

print("TICK30_DONE")

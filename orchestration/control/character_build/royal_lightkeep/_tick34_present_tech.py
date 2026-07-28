# -*- coding: utf-8 -*-
"""Tick #34: hero lighting, lower outer wall height (mockup fort), tech apply batch, proofs."""
import bpy
import os
import shutil
import math
from datetime import datetime
from mathutils import Vector, Euler

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V11_JOIN.blend")
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
    import bmesh
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

# ========== Lower outer fort walls (mockup: wall ~6.5 but not dominate facade) ==========
# Reduce height slightly so tower/hall read larger in frame
for name, sx, sy, x, y in [
    ("OUTER_WALL_FRONT_L", 6.5, 1.2, -6.5, 9.5),
    ("OUTER_WALL_FRONT_R", 6.5, 1.2, 7.5, 9.5),
    ("OUTER_WALL_LEFT", 1.2, 16.0, -11.0, 1.0),
    ("OUTER_WALL_RIGHT", 1.2, 16.0, 11.0, 1.0),
    ("OUTER_WALL_REAR_L", 6.0, 1.2, -6.0, -7.5),
    ("OUTER_WALL_REAR_R", 6.0, 1.2, 7.0, -7.5),
]:
    o = bpy.data.objects.get(name)
    if o and not o.hide_render:
        set_size(o, sx, sy, 4.8, bottom_z=0.0, center_xy=(x, y))
        assign(o, MAT_DARK)

# parapets sit on lowered walls
for name, x, y, sx, sy in [
    ("PARAPET_FRONT_L", -6.5, 9.5, 6.0, 0.9),
    ("PARAPET_FRONT_R", 7.5, 9.5, 6.0, 0.9),
    ("PARAPET_LEFT", -11.0, 1.0, 0.9, 14.0),
    ("PARAPET_RIGHT", 11.0, 1.0, 0.9, 14.0),
]:
    o = bpy.data.objects.get(name)
    if o and not o.hide_render:
        set_size(o, sx, sy, 1.1, bottom_z=4.6, center_xy=(x, y))
        assign(o, MAT_DARK)

# Bastions slightly shorter
for name in ("BASTION_FL", "BASTION_FR", "BASTION_RL", "BASTION_RR"):
    o = bpy.data.objects.get(name)
    if o and not o.hide_render:
        # keep xy, reduce height
        set_size(o, o.dimensions.x, o.dimensions.y, 6.2, bottom_z=0.0, center_xy=(o.location.x, o.location.y))
        assign(o, MAT_DARK)

# Gate piers / lintel
for name, h, bz in [("GATE_PIER_L", 6.0, 0.0), ("GATE_PIER_R", 6.0, 0.0)]:
    o = bpy.data.objects.get(name)
    if o:
        set_size(o, 1.4, 1.6, h, bottom_z=bz, center_xy=(o.location.x, o.location.y))
        assign(o, MAT_STONE)
o = bpy.data.objects.get("GATE_LINTEL")
if o:
    set_size(o, 7.5, 1.4, 1.1, bottom_z=5.4, center_xy=(1.0, 9.5))
    assign(o, MAT_STONE)

# ========== HERO LIGHTING refresh ==========
scene = bpy.context.scene
for lname in list(bpy.data.objects):
    if lname.type == "LIGHT" and lname.name in ("KEY_LIGHT", "FILL_LIGHT", "RIM_LIGHT", "SUN"):
        bpy.data.objects.remove(lname, do_unlink=True)

def add_light(name, ltype, energy, loc, rot_deg, color=(1, 1, 1), size=20.0):
    data = bpy.data.lights.new(name=name, type=ltype)
    data.energy = energy
    data.color = color
    if ltype == "AREA":
        data.size = size
    if ltype == "SUN":
        data.angle = math.radians(6.0)
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = Vector(loc)
    obj.rotation_euler = Euler(tuple(math.radians(a) for a in rot_deg), "XYZ")
    return obj

add_light("KEY_LIGHT", "AREA", 1400, (28, 45, 38), (-42, 0, 28), (1.0, 0.97, 0.90), 28)
add_light("FILL_LIGHT", "AREA", 400, (-32, 28, 28), (-28, 0, -38), (0.88, 0.92, 1.0), 32)
add_light("RIM_LIGHT", "AREA", 550, (-8, -42, 40), (-52, 0, 180), (1.0, 0.95, 0.88), 22)
add_light("SUN", "SUN", 2.0, (18, 28, 55), (-50, 0, 32), (1.0, 0.98, 0.94))

world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()
bg = nt.nodes.new("ShaderNodeBackground")
bg.inputs[0].default_value = (0.84, 0.80, 0.72, 1.0)
bg.inputs[1].default_value = 1.15
out = nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(bg.outputs[0], out.inputs[0])

# ========== TECH: apply scale on all visible meshes (sample batch) ==========
applied = 0
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    # skip if already unit scale
    if abs(o.scale.x - 1.0) < 1e-4 and abs(o.scale.y - 1.0) < 1e-4 and abs(o.scale.z - 1.0) < 1e-4:
        continue
    try:
        for x in bpy.data.objects:
            x.select_set(False)
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        applied += 1
    except Exception:
        pass
print("APPLY_SCALE", applied)

# Height clamp
H_MAX = 38.2
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

try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except Exception:
    try:
        scene.render.engine = "BLENDER_EEVEE"
    except Exception:
        scene.render.engine = "CYCLES"
scene.render.resolution_x = 1280
scene.render.resolution_y = 960

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V12_PRESENT.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V12")

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

print("TICK34_DONE")

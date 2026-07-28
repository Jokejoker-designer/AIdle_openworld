# -*- coding: utf-8 -*-
"""Tick #51: presentation lighting boost + scale human ensure. Scale lock 24x19x38."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector, Euler

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V28_ARCADE.blend")
LOOP = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bpy.ops.wm.open_mainfile(filepath=WORK)
print("OPEN", bpy.data.filepath)

backup = os.path.join(BASE, f"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_BACKUP_LOOP_{STAMP}.blend")
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True)
print("BACKUP", backup)

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

def ensure_sun(name, energy, location, rotation_euler):
    o = bpy.data.objects.get(name)
    if o and o.type == "LIGHT":
        o.data.energy = energy
        o.location = location
        o.rotation_euler = rotation_euler
        return o
    if o and o.type != "LIGHT":
        bpy.data.objects.remove(o, do_unlink=True)
    light = bpy.data.lights.new(name=name + "_data", type="SUN")
    light.energy = energy
    o = bpy.data.objects.new(name, light)
    bpy.context.scene.collection.objects.link(o)
    o.location = location
    o.rotation_euler = rotation_euler
    return o

def ensure_area(name, energy, size, location, rotation_euler):
    o = bpy.data.objects.get(name)
    if o and o.type == "LIGHT":
        o.data.energy = energy
        if hasattr(o.data, "size"):
            o.data.size = size
        o.location = location
        o.rotation_euler = rotation_euler
        return o
    light = bpy.data.lights.new(name=name + "_data", type="AREA")
    light.energy = energy
    light.size = size
    o = bpy.data.objects.new(name, light)
    bpy.context.scene.collection.objects.link(o)
    o.location = location
    o.rotation_euler = rotation_euler
    return o

# Key sun (warm) + fill + rim
ensure_sun("LIGHT_KEY_SUN", 4.5, Vector((20, -25, 40)), Euler((0.9, 0.2, 0.6), "XYZ"))
ensure_sun("LIGHT_FILL_SUN", 1.2, Vector((-15, 10, 25)), Euler((1.1, -0.3, -0.8), "XYZ"))
ensure_area("LIGHT_RIM_AREA", 800, 12.0, Vector((1, 20, 25)), Euler((1.2, 0, 3.14), "XYZ"))
ensure_area("LIGHT_GROUND_BOUNCE", 200, 20.0, Vector((1, 1, 0.5)), Euler((0, 0, 0), "XYZ"))

# World soft sky
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
nt = world.node_tree
bg = nt.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.55, 0.62, 0.72, 1.0)
    bg.inputs[1].default_value = 0.6

# Scale human figure at front for contact
MAT_HUMAN = make_mat("MAT_SCALE_HUMAN", (0.35, 0.32, 0.30), 0.7, 0.0)
set_size(ensure_cube("SCALE_HUMAN"), 0.45, 0.35, 1.75, bottom_z=0.15, center_xy=(1.0, 8.2))
assign(bpy.data.objects["SCALE_HUMAN"], MAT_HUMAN)

# Contact shadow ground plane reinforce
MAT_GROUND = make_mat("MAT_PRES_GROUND", (0.35, 0.42, 0.28), 0.9, 0.0)
g = ensure_cube("PRES_GROUND")
set_size(g, 40, 40, 0.08, bottom_z=-0.35, center_xy=(1.0, 1.0))
assign(g, MAT_GROUND)

# EEVEE quality
scene = bpy.context.scene
try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except Exception:
    try:
        scene.render.engine = "BLENDER_EEVEE"
    except Exception:
        scene.render.engine = "CYCLES"

# Soft clamps height only for new human
H_MAX = 38.2
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name in ("PRES_GROUND",):
        continue
    corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
    minx = min(c.x for c in corners); maxx = max(c.x for c in corners)
    miny = min(c.y for c in corners); maxy = max(c.y for c in corners)
    if o.name != "SCALE_HUMAN":
        if minx < X_MIN:
            o.location.x += (X_MIN - minx)
        if maxx > X_MAX:
            o.location.x += (X_MAX - maxx)
        if miny < Y_MIN:
            o.location.y += (Y_MIN - miny)
        if maxy > Y_MAX:
            o.location.y += (Y_MAX - maxy)
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

scene.render.resolution_x = 1280
scene.render.resolution_y = 960

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V29_PRESENT.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V29")

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

print("TICK51_SCRIPT_READY")

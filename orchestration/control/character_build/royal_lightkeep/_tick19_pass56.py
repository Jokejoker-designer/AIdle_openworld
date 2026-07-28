# -*- coding: utf-8 -*-
"""Tick #19 autonomous: PASS5 polish residual clay + gold ridges + PASS6 lighting/presentation."""
import bpy
import os
import shutil
from datetime import datetime
from mathutils import Vector, Euler
import math
import bmesh

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS5_V01.blend")
LOOP = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bpy.ops.wm.open_mainfile(filepath=WORK)
print("OPEN", bpy.data.filepath, "OBJ", len(bpy.data.objects))

# --- backup ---
backup = os.path.join(BASE, f"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_BACKUP_LOOP_{STAMP}.blend")
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True)
print("BACKUP", backup)

# ---------- helpers ----------
def mesh_local_size(obj):
    me = obj.data
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    return Vector((max(xs) - min(xs) or 1e-6, max(ys) - min(ys) or 1e-6, max(zs) - min(zs) or 1e-6))

def set_size(obj, sx, sy, sz, bottom_z=None, center_xy=None):
    loc = mesh_local_size(obj)
    obj.scale = Vector((sx / loc.x, sy / loc.y, sz / loc.z))
    if center_xy is not None:
        obj.location.x, obj.location.y = center_xy
    if bottom_z is not None:
        obj.location.z = bottom_z + sz / 2.0

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

def make_mat(name, color, rough=0.7, metal=0.0, alpha=1.0):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metal
        if "Alpha" in bsdf.inputs and alpha < 1.0:
            bsdf.inputs["Alpha"].default_value = alpha
            m.blend_method = "BLEND"
        # Specular optional across versions
        for key, val in (("Specular IOR Level", 0.5), ("Specular", 0.5)):
            if key in bsdf.inputs:
                try:
                    bsdf.inputs[key].default_value = val
                except Exception:
                    pass
    m.diffuse_color = (*color, 1.0)
    return m

def assign(obj, mat):
    if not obj or obj.type != "MESH":
        return
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

# ---------- PASS5 polish: warmer palette (M3) ----------
MAT_STONE = make_mat("MAT_LIMESTONE", (0.78, 0.74, 0.66), 0.82, 0.0)   # warmer cream
MAT_DARK = make_mat("MAT_DARK_STONE", (0.22, 0.21, 0.20), 0.92, 0.0)
MAT_ROOF = make_mat("MAT_SLATE_NAVY", (0.10, 0.16, 0.30), 0.50, 0.04)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.82, 0.62, 0.24), 0.28, 0.90)
MAT_WOOD = make_mat("MAT_WOOD", (0.28, 0.16, 0.08), 0.72, 0.0)
MAT_GLASS = make_mat("MAT_GLASS", (0.45, 0.58, 0.72), 0.12, 0.0)
MAT_BANNER = make_mat("MAT_BANNER_BLUE", (0.07, 0.14, 0.42), 0.62, 0.0)

clay_fixed = 0
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    n = o.name.upper()
    slots = [s.material.name if s.material else "" for s in o.material_slots]
    is_clay = (not slots) or any(s.startswith("CLAY") or s == "" for s in slots)

    if any(k in n for k in (
        "ROOF", "HIP", "RIDGE", "GABLE_PEAK", "GABLE_ROOF",
        "PAVILION_ROOF", "PAVILION_PEAK", "CORNER_CAP", "SPIRE", "OCT_SPIRE",
    )):
        assign(o, MAT_ROOF)
        clay_fixed += 1 if is_clay else 0
    elif "BANNER_PANEL" in n:
        assign(o, MAT_BANNER)
    elif any(k in n for k in (
        "BANNER_MOUNT", "TRIM", "CORNICE", "EMBLEM", "FRAME", "FINIAL", "RAIL", "GOLD",
    )):
        assign(o, MAT_GOLD)
    elif any(k in n for k in ("WIN_", "ARCH", "RECESS", "SLIT")) and "FRAME" not in n:
        assign(o, MAT_GLASS)
    elif any(k in n for k in ("VOID", "INNER_DARK", "TUNNEL_VOID", "PORTAL_PROXY")):
        assign(o, MAT_DARK)
    elif any(k in n for k in ("BASE_", "OUTER_", "BASTION", "PARAPET", "LEVEL0", "GROUND", "PODIUM")):
        assign(o, MAT_DARK)
    elif "STAIR" in n and "RAIL" not in n:
        assign(o, MAT_STONE)
    elif any(k in n for k in (
        "TOWER", "GH_", "BARRACKS", "RIGHT_", "BAR_", "GATE", "WALL", "PIER",
        "LINTEL", "SHOULDER", "CONNECTOR", "PAVILION", "COURT", "TERRACE", "LEVEL",
        "SPIRE_BASE", "OBSERVATION", "MID_", "SHAFT", "DOOR",
    )):
        assign(o, MAT_STONE)
        clay_fixed += 1 if is_clay else 0
    elif is_clay:
        # catch-all residual clay
        assign(o, MAT_STONE)
        clay_fixed += 1

print("CLAY_FIXED_OR_REASSIGNED_approx", clay_fixed)

# ---------- Gold ridge / cornice accents (M3 density) ----------
# Tower roof ridge ring + peak finial gold
ridges = [
    ("GOLD_RIDGE_TOWER_N", 1.5, 7.8, 37.3, 5.5, 0.28, 0.28),
    ("GOLD_RIDGE_TOWER_S", 1.5, 2.2, 37.3, 5.5, 0.28, 0.28),
    ("GOLD_RIDGE_TOWER_E", 4.0, 5.0, 37.3, 0.28, 5.5, 0.28),
    ("GOLD_RIDGE_TOWER_W", -1.0, 5.0, 37.3, 0.28, 5.5, 0.28),
    ("GOLD_FINIAL_PEAK", 1.5, 5.0, 39.3, 0.55, 0.55, 1.4),
    ("GOLD_CORNICE_OBS", 1.5, 5.0, 32.85, 12.6, 12.6, 0.35),
    ("GOLD_CORNICE_MID", 1.5, 5.0, 28.2, 10.0, 10.0, 0.32),
    # Barracks eaves accents (left wing approx)
    ("GOLD_EAVES_BAR_F", -13.0, 7.0, 14.55, 22.0, 0.28, 0.28),
    ("GOLD_EAVES_BAR_SIDE", -2.0, 2.0, 14.55, 0.28, 10.0, 0.28),
    # Emblem gold boosts already exist — add top crown ring
    ("GOLD_CROWN_RING", 1.5, 5.0, 34.05, 8.5, 8.5, 0.30),
]
for name, x, y, z, sx, sy, sz in ridges:
    o = ensure_cube(name)
    set_size(o, sx, sy, sz, bottom_z=z - sz / 2.0, center_xy=(x, y))
    assign(o, MAT_GOLD)

# ---------- PASS6 lighting + world ----------
scene = bpy.context.scene

# remove old simple sun if present; rebuild presentation rig
for lname in ("SUN", "KEY_LIGHT", "FILL_LIGHT", "RIM_LIGHT", "SKY_LIGHT"):
    lo = bpy.data.objects.get(lname)
    if lo and lo.type == "LIGHT":
        bpy.data.objects.remove(lo, do_unlink=True)

def add_light(name, ltype, energy, loc, rot_euler_deg, color=(1, 1, 1), size=5.0):
    data = bpy.data.lights.new(name=name, type=ltype)
    data.energy = energy
    data.color = color
    if ltype == "AREA":
        data.size = size
    if ltype == "SUN":
        data.angle = math.radians(8.0)
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = Vector(loc)
    obj.rotation_euler = Euler(tuple(math.radians(a) for a in rot_euler_deg), "XYZ")
    return obj

# Soft key (front-right elevated) — M3 soft daylight feel
add_light("KEY_LIGHT", "AREA", 900.0, (45, 70, 55), (-35, 0, 30), (1.0, 0.97, 0.92), size=28.0)
# Cool fill left
add_light("FILL_LIGHT", "AREA", 280.0, (-55, 40, 35), (-25, 0, -40), (0.85, 0.90, 1.0), size=35.0)
# Rim back (M2 massing edge readability)
add_light("RIM_LIGHT", "AREA", 450.0, (-20, -75, 50), (-50, 0, 180), (1.0, 0.95, 0.88), size=22.0)
# Gentle sun for ground contact
add_light("SUN", "SUN", 1.6, (30, 40, 80), (-48, 0, 35), (1.0, 0.98, 0.94))

# World soft grey-blue
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()
bg = nt.nodes.new("ShaderNodeBackground")
bg.inputs[0].default_value = (0.55, 0.60, 0.68, 1.0)
bg.inputs[1].default_value = 0.85
out = nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(bg.outputs[0], out.inputs[0])

# Ground plane for contact shadow (presentation only)
gp = bpy.data.objects.get("PRES_GROUND")
if not gp:
    mesh = bpy.data.meshes.new("PRES_GROUND")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=80.0)
    bm.to_mesh(mesh)
    bm.free()
    gp = bpy.data.objects.new("PRES_GROUND", mesh)
    bpy.context.scene.collection.objects.link(gp)
gp.location = (1.0, 2.0, 0.0)
mat_g = make_mat("MAT_GROUND", (0.42, 0.43, 0.45), 0.95, 0.0)
assign(gp, mat_g)

# Scale ref human proxy (optional, near front)
human = bpy.data.objects.get("SCALE_HUMAN")
if not human:
    mesh = bpy.data.meshes.new("SCALE_HUMAN")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    bm.to_mesh(mesh)
    bm.free()
    human = bpy.data.objects.new("SCALE_HUMAN", mesh)
    bpy.context.scene.collection.objects.link(human)
set_size(human, 0.55, 0.35, 1.8, bottom_z=0.0, center_xy=(1.5, 28.0))
mat_h = make_mat("MAT_SCALE_HUMAN", (0.15, 0.15, 0.18), 0.8, 0.0)
assign(human, mat_h)

# ---------- Engine / render settings ----------
try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except Exception:
    try:
        scene.render.engine = "BLENDER_EEVEE"
    except Exception:
        scene.render.engine = "CYCLES"

scene.render.resolution_x = 1280
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False

# EEVEE-ish toggles (best effort)
try:
    ee = scene.eevee
    if hasattr(ee, "use_gtao"):
        ee.use_gtao = True
    if hasattr(ee, "use_ssr"):
        ee.use_ssr = True
except Exception:
    pass

# ---------- Save PASS5_FINAL then PASS6_V01 ----------
p5f = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS5_FINAL.blend")
bpy.ops.wm.save_as_mainfile(filepath=p5f)
print("SAVED PASS5_FINAL")

p6 = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS6_V01.blend")
bpy.ops.wm.save_as_mainfile(filepath=p6)
shutil.copy2(p6, LOOP)
print("SAVED PASS6_V01 + synced PASS1D")

# ---------- Renders ----------
out5 = os.path.join(BASE, "renders_pass5")
out6 = os.path.join(BASE, "renders_pass6")
out_work = os.path.join(BASE, "renders_pass1d")
os.makedirs(out5, exist_ok=True)
os.makedirs(out6, exist_ok=True)
os.makedirs(out_work, exist_ok=True)

jobs = [
    ("CAM_01_FRONT", out_work, "current_front_work.png"),
    ("CAM_05_FRONT_3Q", out_work, "current_front_3q_work.png"),
    ("CAM_06_REAR_3Q", out_work, "current_rear_3q_work.png"),
    ("CAM_TOP_PLAN", out_work, "current_top_plan_work.png"),
    ("CAM_01_FRONT", out5, "pass5_front.png"),
    ("CAM_05_FRONT_3Q", out5, "pass5_front_3q.png"),
    ("CAM_02_REAR", out5, "pass5_rear.png"),
    ("CAM_03_LEFT", out5, "pass5_left.png"),
    ("CAM_04_RIGHT", out5, "pass5_right.png"),
    ("CAM_01_FRONT", out6, "pass6_front.png"),
    ("CAM_05_FRONT_3Q", out6, "pass6_front_3q.png"),
    ("CAM_02_REAR", out6, "pass6_rear.png"),
    ("CAM_03_LEFT", out6, "pass6_left.png"),
    ("CAM_04_RIGHT", out6, "pass6_right.png"),
    ("CAM_06_REAR_3Q", out6, "pass6_rear_3q.png"),
    ("CAM_TOP_PLAN", out6, "pass6_top.png"),
]

for cam, dest, fn in jobs:
    c = bpy.data.objects.get(cam)
    if not c:
        print("MISS_CAM", cam)
        continue
    scene.camera = c
    scene.render.filepath = os.path.join(dest, fn)
    bpy.ops.render.render(write_still=True)
    print("OK", fn)

# residual clay audit
residual = []
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    for s in o.material_slots:
        if s.material and s.material.name.startswith("CLAY"):
            residual.append(o.name)
            break
print("RESIDUAL_CLAY_COUNT", len(residual))
if residual:
    print("RESIDUAL_SAMPLE", residual[:25])

print("TICK19_DONE OBJ", len(bpy.data.objects))

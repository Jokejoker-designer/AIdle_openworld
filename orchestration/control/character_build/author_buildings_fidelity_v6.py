# -*- coding: utf-8 -*-
"""BUILDINGS_FIDELITY_V6 — continuous iteration; NEW mesh strategies for stuck 3.

GARDEN  petal-plate roof (flat discs on rings) — NOT sphere fishscales
WELL    solid masonry cylinder + plank-plate A-frame — NOT brick cubes
WINDMILL truncated-cone stack + lattice sail frames — NOT soft sphere tiers
MARKET  more individual fruit on apron (polish)
BRIDGE  clear arch void + voussoirs (polish V5b)
LOOKOUT irregular brown thatch fringe (polish)

HOME.BLD untouched. accepted=false, self_accept=false.
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
from pathlib import Path

import bpy

TAU = math.tau
JOB = "BUILDINGS_FIDELITY_V6"
GAME_DIR = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules")
CAT = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
QUAR.mkdir(parents=True, exist_ok=True)
RECEIPT = Path(r"E:\AIdle_openworld\orchestration\receipts\town_grid_import_001\BUILDINGS_FIDELITY_V6.json")

MODULES = [
    "cozy_market_stall_A",
    "cozy_gazebo_A",
    "cozy_well_house_A",
    "cozy_windmill_A",
    "cozy_bridge_arch_A",
    "cozy_watchtower_A",
]


def log(m):
    print(f"[{JOB}] {m}", flush=True)


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, rgb, rough=0.55, emit=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*rgb[:3], alpha)
    b = next((x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED"), None)
    if b:
        b.inputs["Base Color"].default_value = (*rgb[:3], alpha)
        if "Roughness" in b.inputs:
            b.inputs["Roughness"].default_value = rough
        if emit > 0:
            if "Emission Color" in b.inputs:
                b.inputs["Emission Color"].default_value = (*rgb[:3], 1.0)
            if "Emission Strength" in b.inputs:
                b.inputs["Emission Strength"].default_value = emit
        if alpha < 0.99:
            m.blend_method = "BLEND"
            if "Alpha" in b.inputs:
                b.inputs["Alpha"].default_value = alpha
    return m


def setm(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)
    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass


def cube(n, loc, sc, m, bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = n
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    setm(o, m)
    if bevel > 0:
        try:
            bpy.context.view_layer.objects.active = o
            o.select_set(True)
            bpy.ops.object.modifier_add(type="BEVEL")
            md = o.modifiers[-1]
            md.width = bevel
            md.segments = 2
            bpy.ops.object.modifier_apply(modifier=md.name)
            o.select_set(False)
        except Exception:
            pass
    return o


def sph(n, loc, r, m, sc=(1, 1, 1), segs=12):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=segs, ring_count=max(6, segs // 2))
    o = bpy.context.active_object
    o.name = n
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    setm(o, m)
    return o


def cyl(n, loc, r, d, m, verts=12):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=verts)
    o = bpy.context.active_object
    o.name = n
    setm(o, m)
    return o


def cone(n, loc, r1, r2, d, m, verts=12):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=d, location=loc, vertices=verts)
    o = bpy.context.active_object
    o.name = n
    setm(o, m)
    return o


def apply_rot(o, euler):
    o.rotation_euler = euler
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    try:
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    except Exception:
        pass
    o.select_set(False)


def parent_all(root):
    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            mw = o.matrix_world.copy()
            o.parent = root
            o.matrix_world = mw


def root_empty(module_id):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    r = bpy.context.active_object
    r.name = f"MOD_{module_id}"
    return r


# ───────────────────────── V6 builders ─────────────────────────


def build_market():
    """Polish: denser individual fruits, multi-color piles, front-readable."""
    Mw = mat("wood", (0.70, 0.45, 0.28), 0.55)
    Mw2 = mat("wood2", (0.82, 0.58, 0.36), 0.55)
    Mpink = mat("awn_p", (0.96, 0.62, 0.75), 0.48)
    Mcream = mat("awn_c", (0.99, 0.95, 0.88), 0.48)
    Mred = mat("apple", (0.92, 0.22, 0.22), 0.4)
    Myel = mat("lemon", (0.96, 0.90, 0.18), 0.4)
    Mor = mat("orange", (0.98, 0.52, 0.12), 0.4)
    Mgreen = mat("lime", (0.45, 0.78, 0.30), 0.45)
    Mpur = mat("grape", (0.55, 0.30, 0.65), 0.4)
    Mreg = mat("reg", (0.55, 0.85, 0.68), 0.42)
    Mbase = mat("base", (0.78, 0.70, 0.90), 0.65)
    Mcloth = mat("cloth", (0.98, 0.92, 0.80), 0.5)
    Mstem = mat("stem", (0.45, 0.70, 0.30), 0.55)
    Mgold = mat("gold", (0.95, 0.80, 0.30), 0.4, emit=0.5)

    r = root_empty("cozy_market_stall_A")
    cube("Base", (0, 0, 0.04), (2.5, 2.1, 0.08), Mbase, 0.1)
    for i, z in enumerate([0.22, 0.48, 0.72]):
        cube(f"Body{i}", (0, -0.05, z), (1.90, 1.10, 0.24), Mw if i % 2 == 0 else Mw2, 0.05)
    for x, y in [(-0.88, 0.45), (0.88, 0.45), (-0.88, -0.50), (0.88, -0.50)]:
        cyl(f"Post_{x}_{y}", (x, y, 1.20), 0.07, 1.2, Mw, 8)
    for i in range(9):
        t = i / 8.0
        cube(f"Awn{i}", (-1.15 + t * 2.3, 0.05, 1.65), (0.26, 1.50, 0.18), Mpink if i % 2 == 0 else Mcream, 0.06)
    cube("Val", (0, 0.88, 1.45), (2.30, 0.34, 0.18), Mpink, 0.06)
    cube("Apron", (0, 0.88, 0.55), (1.95, 0.58, 0.10), Mw2, 0.04)
    cube("Cloth", (0, 0.90, 0.62), (1.80, 0.50, 0.04), Mcloth, 0.02)
    # denser produce — more individual orbs
    piles = [
        (-0.60, Mred, 0.13, 14),
        (-0.05, Myel, 0.12, 12),
        (0.50, Mor, 0.13, 14),
    ]
    for i, (x, fm, rad, nfr) in enumerate(piles):
        for j in range(nfr):
            layer = j // 4
            k = j % 4
            fx = x + ((k % 2) - 0.5) * rad * 1.6 + layer * 0.02
            fy = 0.88 + ((k // 2) - 0.5) * rad * 1.4
            fz = 0.72 + layer * rad * 1.1
            sph(f"F{i}_{j}", (fx, fy, fz), rad * (0.9 if layer else 1.05), fm, segs=12)
            if j % 2 == 0:
                cyl(f"St{i}_{j}", (fx, fy, fz + rad * 0.65), 0.015, 0.05, Mstem, 5)
    # greens + grapes side baskets
    cube("BskL", (-0.98, 0.80, 0.72), (0.34, 0.30, 0.16), Mw, 0.02)
    for j in range(12):
        sph(f"Gr{j}", (-0.98 + (j % 3 - 1) * 0.07, 0.80 + (j // 3 - 1.5) * 0.05, 0.88), 0.05, Mpur if j % 2 else Mgreen, segs=8)
    cube("BskR", (0.98, 0.78, 0.72), (0.30, 0.28, 0.16), Mw, 0.02)
    for j in range(6):
        sph(f"Lm{j}", (0.98 + (j % 2 - 0.5) * 0.08, 0.78, 0.88), 0.07, Mgreen, segs=8)
    for i, x in enumerate([-0.55, 0.10, 0.70]):
        cube(f"Back{i}", (x, -0.15, 0.95), (0.42, 0.40, 0.28), Mw2, 0.03)
    cube("Reg", (0.90, 0.35, 1.00), (0.28, 0.22, 0.30), Mreg, 0.03)
    sph("Knob", (0.98, 0.42, 1.05), 0.04, Mgold)
    parent_all(r)
    return r


def build_gazebo():
    """V6 NEW: petal-plate roof — flat green discs on concentric rings (not sphere scales)."""
    Mw = mat("wood", (0.78, 0.55, 0.35), 0.55)
    Mf = mat("floor", (0.92, 0.78, 0.55), 0.5)
    Mg1 = mat("g1", (0.38, 0.78, 0.45), 0.5)
    Mg2 = mat("g2", (0.30, 0.68, 0.38), 0.5)
    Mg3 = mat("g3", (0.48, 0.86, 0.52), 0.5)
    Me = mat("emit", (1.0, 0.85, 0.45), 0.4, emit=2.2)
    Mbase = mat("base", (0.82, 0.75, 0.92), 0.65)
    Mpot = mat("pot", (0.85, 0.50, 0.32), 0.55)
    Mleaf = mat("leaf", (0.35, 0.72, 0.40), 0.55)
    Mlav = mat("lav", (0.70, 0.45, 0.85), 0.5)

    r = root_empty("cozy_gazebo_A")
    cyl("Pad", (0, 0, 0.04), 1.45, 0.08, Mbase, 24)
    cyl("Floor", (0, 0, 0.18), 1.10, 0.10, Mf, 20)
    # soft under-glow
    sph("Glow", (0, 0, 0.95), 0.50, Me, (1.0, 1.0, 0.35))
    # 8 posts (more open silhouette)
    for i in range(8):
        ang = TAU * i / 8.0
        x, y = 0.92 * math.cos(ang), 0.92 * math.sin(ang)
        cyl(f"Post{i}", (x, y, 0.78), 0.07, 1.20, Mw, 8)
    # rail rings
    for i in range(16):
        ang = TAU * i / 16.0
        x, y = 0.95 * math.cos(ang), 0.95 * math.sin(ang)
        cube(f"Rail{i}", (x, y, 0.52), (0.14, 0.06, 0.05), Mw, 0.02)
    # wood roof frame rings
    for ri, (rad, z) in enumerate([(0.35, 1.55), (0.70, 1.40), (1.05, 1.22)]):
        for i in range(12):
            ang = TAU * i / 12.0
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            cube(f"Frame{ri}_{i}", (x, y, z), (0.12, 0.06, 0.05), Mw, 0.01)
    # PETAL PLATES — flat thin discs (squashed cylinders) overlapping
    mats = [Mg1, Mg2, Mg3]
    rings = [
        (0.15, 1.95, 6, 0.22),
        (0.40, 1.82, 10, 0.20),
        (0.65, 1.68, 14, 0.19),
        (0.88, 1.52, 16, 0.18),
        (1.08, 1.35, 18, 0.17),
        (1.22, 1.20, 20, 0.16),
    ]
    for ring, (rad, z, n, pr) in enumerate(rings):
        for i in range(n):
            ang = TAU * i / n + (0.12 if ring % 2 else 0.0)
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            # thin petal: flat cylinder
            o = cyl(f"Petal{ring}_{i}", (x, y, z), pr, 0.04, mats[(i + ring) % 3], 10)
            # tip petal slightly outward/down
            apply_rot(o, (0.35, 0, ang))
    # cap
    cyl("Cap", (0, 0, 2.05), 0.22, 0.08, Mg3, 12)
    sph("CapBall", (0, 0, 2.15), 0.12, Mg1, (1.2, 1.2, 0.7))
    for i in range(8):
        ang = TAU * i / 8.0 + 0.2
        x, y = 1.25 * math.cos(ang), 1.25 * math.sin(ang)
        cyl(f"Pot{i}", (x, y, 0.12), 0.08, 0.14, Mpot, 8)
        sph(f"Pl{i}", (x, y, 0.28), 0.10, Mleaf if i % 2 == 0 else Mlav)
    parent_all(r)
    return r


def build_well():
    """V6 NEW: solid cream cylinder + groove rings + PLANK shingle A-frame (boxes on slope)."""
    Ms = mat("stone", (0.94, 0.90, 0.82), 0.62)
    Ms2 = mat("stone2", (0.88, 0.84, 0.76), 0.62)
    Mw = mat("wood", (0.80, 0.55, 0.32), 0.52)
    Mw2 = mat("wood2", (0.88, 0.64, 0.40), 0.52)
    Mbase = mat("base", (0.96, 0.92, 0.84), 0.65)
    Mrope = mat("rope", (0.92, 0.85, 0.70), 0.6)
    Mdark = mat("dark", (0.22, 0.26, 0.30), 0.75)
    Msh = mat("shingle", (0.72, 0.48, 0.28), 0.55)
    Msh2 = mat("shingle2", (0.65, 0.42, 0.24), 0.55)

    r = root_empty("cozy_well_house_A")
    cyl("Pad", (0, 0, 0.03), 1.30, 0.07, Mbase, 24)
    # solid masonry body (one piece look) + horizontal groove rings
    cyl("Body", (0, 0, 0.42), 0.55, 0.75, Ms, 20)
    for i, z in enumerate([0.20, 0.38, 0.56, 0.72]):
        cyl(f"Groove{i}", (0, 0, z), 0.56, 0.04, Ms2 if i % 2 else Ms, 20)
    cyl("Coping", (0, 0, 0.82), 0.58, 0.10, Ms, 18)
    cyl("Hole", (0, 0, 0.40), 0.32, 0.70, Mdark, 14)
    # A-frame posts + cross
    cyl("PostL", (-0.65, 0, 1.15), 0.085, 1.65, Mw, 8)
    cyl("PostR", (0.65, 0, 1.15), 0.085, 1.65, Mw, 8)
    cube("Cross", (0, 0, 1.70), (1.40, 0.12, 0.12), Mw, 0.03)
    cube("BraceL", (-0.35, 0, 1.45), (0.60, 0.08, 0.08), Mw2, 0.02)
    cube("BraceR", (0.35, 0, 1.45), (0.60, 0.08, 0.08), Mw2, 0.02)
    # PLANK shingles on two slopes (boxes, not spheres)
    for side, y_sign in (("F", 1.0), ("B", -1.0)):
        for row in range(5):
            t = (row + 0.5) / 5.0
            y = y_sign * 0.45 * (1.0 - t * 0.9)
            z = 1.75 + t * 0.55
            for col in range(5):
                u = (col + 0.5) / 5.0
                x = (u - 0.5) * 1.25
                m = Msh if (row + col) % 2 == 0 else Msh2
                o = cube(f"Plank{side}{row}_{col}", (x, y, z), (0.26, 0.18, 0.04), m, 0.01)
                ang = math.atan2(0.55, 0.45) * (1 if y_sign > 0 else -1) * 0.9
                apply_rot(o, (ang, 0, 0))
    cube("Ridge", (0, 0, 2.32), (1.20, 0.14, 0.08), Mw2, 0.02)
    # winch + bucket
    cyl("Drum", (0.65, 0, 1.70), 0.12, 0.24, Mw2, 10)
    cyl("Handle", (0.80, 0, 1.70), 0.03, 0.28, Mw, 6)
    cyl("Bucket", (0, 0, 1.05), 0.15, 0.22, Mw2, 10)
    cube("Bail", (0, 0, 1.25), (0.03, 0.03, 0.30), Mrope, 0.0)
    for i, (x, y) in enumerate([(-0.45, 0.95), (0.0, 1.05), (0.45, 0.95)]):
        sph(f"Path{i}", (x, y, 0.05), 0.13, Ms, (1.25, 1.0, 0.3), segs=8)
    parent_all(r)
    return r


def build_windmill():
    """V6 NEW: truncated-cone tiers + lattice sail frames (frame + cloth panel)."""
    Mc = mat("clay", (0.97, 0.93, 0.88), 0.6)
    Mc2 = mat("clay2", (0.92, 0.88, 0.82), 0.6)
    Mr = mat("roof", (0.90, 0.48, 0.35), 0.55)
    Mw = mat("wood", (0.75, 0.52, 0.32), 0.5)
    Mcloth = mat("sail", (0.96, 0.92, 0.82), 0.45)
    Md = mat("door", (0.80, 0.52, 0.32), 0.5)
    Me = mat("emit", (1.0, 0.82, 0.40), 0.3, emit=3.2)
    Mbase = mat("base", (0.96, 0.92, 0.84), 0.65)
    Mstone = mat("stone", (0.78, 0.74, 0.70), 0.65)
    Mband = mat("band", (0.85, 0.52, 0.35), 0.55)
    Mhub = mat("hub", (0.70, 0.48, 0.28), 0.5)

    r = root_empty("cozy_windmill_A")
    cube("Pad", (0, 0, 0.04), (2.2, 2.2, 0.08), Mbase, 0.1)
    # stone base ring
    cyl("StoneBase", (0, 0, 0.18), 1.05, 0.28, Mstone, 18)
    # truncated cone stack (hard silhouette, not soft spheres)
    cone("Tier0", (0, 0, 0.70), 0.95, 0.72, 0.85, Mc, 16)
    cone("Tier1", (0, 0, 1.45), 0.72, 0.55, 0.70, Mc2, 16)
    cone("Tier2", (0, 0, 2.05), 0.55, 0.42, 0.55, Mc, 14)
    cyl("Band0", (0, 0, 1.10), 0.78, 0.10, Mband, 16)
    cyl("Band1", (0, 0, 1.75), 0.60, 0.09, Mband, 16)
    sph("Roof", (0, 0, 2.45), 0.52, Mr, (1.15, 1.15, 0.75), segs=14)
    cyl("Chim", (0.38, -0.28, 2.70), 0.10, 0.42, mat("chim", (0.96, 0.92, 0.88), 0.55), 8)
    cube("Door", (0, 0.95, 0.55), (0.42, 0.10, 0.65), Md, 0.05)
    sph("Arch", (0, 0.95, 0.92), 0.22, Md, (1.0, 0.35, 0.55), segs=10)
    # windows as flat panels
    for i, (x, z) in enumerate([(-0.45, 1.35), (0.45, 1.35), (0.0, 1.90), (-0.35, 1.90), (0.35, 1.90)]):
        cube(f"Win{i}", (x, 0.55, z), (0.22, 0.08, 0.28), Me, 0.02)
    # hub + lattice sails
    hub = (0.0, 0.75, 2.10)
    sph("Hub", hub, 0.16, Mhub)
    cyl("HubPlate", (hub[0], hub[1] + 0.03, hub[2]), 0.20, 0.07, Mhub, 12)
    for i in range(4):
        ang = math.radians(i * 90 + 20)
        # main spar
        length = 1.15
        mx = hub[0] + (length * 0.5) * math.cos(ang)
        mz = hub[2] + (length * 0.5) * math.sin(ang)
        spar = cube(f"Spar{i}", (mx, hub[1] + 0.08, mz), (0.08, 0.06, length), Mw, 0.02)
        apply_rot(spar, (0, -ang, 0))
        # cross bars
        for k, t in enumerate([0.35, 0.65, 0.90]):
            cx = hub[0] + length * t * math.cos(ang)
            cz = hub[2] + length * t * math.sin(ang)
            bar = cube(f"Bar{i}_{k}", (cx, hub[1] + 0.10, cz), (0.32, 0.04, 0.05), Mw, 0.01)
            apply_rot(bar, (0, -ang, 0))
        # cloth sail panel
        sx = hub[0] + length * 0.55 * math.cos(ang)
        sz = hub[2] + length * 0.55 * math.sin(ang)
        sail = cube(f"Sail{i}", (sx, hub[1] + 0.12, sz), (0.38, 0.03, 0.85), Mcloth, 0.01)
        apply_rot(sail, (0, -ang, 0))
    parent_all(r)
    return r


def build_bridge():
    """Polish: clear arch void, box voussoirs, solid abutments, deck on top only."""
    Ms1 = mat("s1", (0.90, 0.86, 0.88), 0.55)
    Ms2 = mat("s2", (0.80, 0.76, 0.82), 0.55)
    Ms3 = mat("s3", (0.94, 0.90, 0.92), 0.55)
    Mpk = mat("pk", (0.95, 0.55, 0.70), 0.5)
    Mleaf = mat("leaf", (0.40, 0.75, 0.45), 0.55)

    r = root_empty("cozy_bridge_arch_A")
    mats = [Ms1, Ms2, Ms3]
    # tall abutments — open space between for arch void
    for side, x in (("L", -1.20), ("R", 1.20)):
        cube(f"Abut{side}", (x, 0, 0.40), (0.55, 0.85, 0.80), Ms2, 0.06)
        cube(f"Cap{side}", (x, 0, 0.85), (0.52, 0.82, 0.14), Ms1, 0.04)
    # arch ring elevated — leaves center void under
    n = 11
    for i in range(n):
        t = i / (n - 1)
        ang = math.pi * t
        x = 1.05 * math.cos(ang)
        z = 0.70 + 0.85 * math.sin(ang)
        o = cube(f"V{i}", (x, 0, z), (0.24, 0.62, 0.18), mats[i % 3], 0.04)
        apply_rot(o, (0, ang - math.pi / 2, 0))
    cube("Key", (0, 0, 1.55), (0.28, 0.65, 0.22), Ms3, 0.05)
    # deck only on top of arch crown
    for i in range(6):
        t = (i + 0.5) / 6.0
        x = -0.85 + t * 1.7
        cube(f"Deck{i}", (x, 0, 1.68), (0.30, 0.75, 0.12), mats[i % 3], 0.03)
    for side, y in (("L", 0.42), ("R", -0.42)):
        for i, t in enumerate([0.2, 0.5, 0.8]):
            x = -0.75 + t * 1.5
            cube(f"Rail{side}{i}", (x, y, 1.85), (0.16, 0.12, 0.20), mats[i % 3], 0.03)
    for i, (x, y) in enumerate([(-1.40, 0.55), (1.40, -0.5)]):
        cyl(f"St{i}", (x, y, 0.08), 0.025, 0.18, Mleaf, 5)
        sph(f"Bl{i}", (x, y, 0.20), 0.08, Mpk, segs=8)
    parent_all(r)
    return r


def build_watchtower():
    """Polish: darker brown thatch, more layers, irregular fringe tips."""
    Mc = mat("clay", (0.96, 0.92, 0.86), 0.6)
    Mr1 = mat("t1", (0.48, 0.32, 0.16), 0.68)
    Mr2 = mat("t2", (0.42, 0.28, 0.14), 0.68)
    Mr3 = mat("t3", (0.55, 0.38, 0.18), 0.68)
    Mr4 = mat("t4", (0.38, 0.24, 0.12), 0.68)
    Mw = mat("wood", (0.58, 0.40, 0.22), 0.5)
    Me = mat("emit", (1.0, 0.85, 0.45), 0.35, emit=2.8)
    Mband = mat("band", (0.62, 0.44, 0.26), 0.55)

    r = root_empty("cozy_watchtower_A")
    cyl("Lo", (0, 0, 0.70), 0.55, 1.30, Mc, 14)
    cyl("Hi", (0, 0, 1.75), 0.48, 0.85, Mc, 14)
    cube("Cabin", (0, 0, 2.35), (0.95, 0.95, 0.70), Mc, 0.06)
    cyl("Band", (0, 0, 2.05), 0.58, 0.10, Mband, 14)
    # more thatch layers
    layers = [
        (2.52, 1.00, 0.82, 0.16),
        (2.66, 0.88, 0.68, 0.15),
        (2.80, 0.72, 0.52, 0.15),
        (2.94, 0.55, 0.36, 0.14),
        (3.08, 0.38, 0.20, 0.14),
        (3.20, 0.22, 0.06, 0.12),
    ]
    mats = [Mr1, Mr2, Mr3, Mr4]
    for i, (z, r1, r2, d) in enumerate(layers):
        cone(f"Th{i}", (0, 0, z), r1, r2, d, mats[i % 4], 16)
    # fringe tips around eave
    for i in range(14):
        ang = TAU * i / 14.0
        x, y = 0.98 * math.cos(ang), 0.98 * math.sin(ang)
        cube(f"Fringe{i}", (x, y, 2.48), (0.12, 0.06, 0.10), mats[i % 4], 0.01)
    cyl("Finial", (0, 0, 3.35), 0.04, 0.24, Mw, 6)
    cyl("Eave", (0, 0, 2.45), 0.95, 0.07, Mband, 16)
    cube("OpenF", (0, 0.50, 2.35), (0.35, 0.08, 0.40), Me, 0.02)
    cube("OpenR", (0.50, 0, 2.35), (0.08, 0.35, 0.35), Me, 0.02)
    for i in range(7):
        cube(f"Rung{i}", (0, -0.58, 0.25 + i * 0.28), (0.35, 0.06, 0.05), Mw, 0.02)
    cyl("RailL", (-0.18, -0.58, 1.15), 0.04, 2.0, Mw, 6)
    cyl("RailR", (0.18, -0.58, 1.15), 0.04, 2.0, Mw, 6)
    parent_all(r)
    return r


BUILDERS = {
    "cozy_market_stall_A": build_market,
    "cozy_gazebo_A": build_gazebo,
    "cozy_well_house_A": build_well,
    "cozy_windmill_A": build_windmill,
    "cozy_bridge_arch_A": build_bridge,
    "cozy_watchtower_A": build_watchtower,
}


def export_module(module_id: str) -> dict:
    clear()
    log(f"build {module_id}")
    BUILDERS[module_id]()
    q = QUAR / f"{module_id}.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(q),
        export_format="GLB",
        use_selection=False,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        export_materials="EXPORT",
    )
    dest = GAME_DIR / f"{module_id}.glb"
    shutil.copy2(q, dest)
    dig = sha(dest)
    size = dest.stat().st_size
    log(f"  wrote {dest.name} sha={dig[:16]} bytes={size}")
    return {
        "module_id": module_id,
        "glb_sha256": dig,
        "bytes": size,
        "source": JOB,
        "visual": f"mockup_{module_id}_v6",
        "mockup_ssot": module_id,
    }


def update_catalog(rows: list[dict]) -> None:
    data = json.loads(CAT.read_text(encoding="utf-8"))
    by_id = {m.get("module_id"): m for m in data.get("modules", [])}
    for row in rows:
        mid = row["module_id"]
        entry = {
            "module_id": mid,
            "glb": f"res://assets/p1e_cozy/modules/{mid}.glb",
            "glb_sha256": row["glb_sha256"],
            "bytes": row["bytes"],
            "source": row["source"],
            "visual": row["visual"],
            "mockup_ssot": row["mockup_ssot"],
        }
        if mid in by_id:
            by_id[mid].update(entry)
        else:
            data["modules"].append(entry)
    data["accepted"] = False
    data["self_accept"] = False
    data["buildings_fidelity_v6"] = JOB
    CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"catalog modules={len(data['modules'])}")


def main():
    log("start BUILDINGS_FIDELITY_V6 continuous n=6 new strategies")
    rows = []
    for mid in MODULES:
        rows.append(export_module(mid))
    update_catalog(rows)
    report = {
        "schema_version": "buildings_fidelity/1.0",
        "receipt_id": "BUILDINGS_FIDELITY_V6",
        "job": JOB,
        "work_order": "WO-TOWN-GRID-IMPORT-001",
        "authority": "PATCH_DRAFT",
        "human_authorization": "continuous_iteration_authorization",
        "accepted": False,
        "self_accept": False,
        "purple": "WAITING",
        "matching_100_pct_count": 0,
        "matching_100_pct": [],
        "modules": rows,
        "strategies": {
            "cozy_gazebo_A": "petal_plate_discs_not_sphere_fishscales",
            "cozy_well_house_A": "solid_cylinder_groove_rings_plank_shingle_aframe",
            "cozy_windmill_A": "truncated_cone_stack_lattice_sails",
            "cozy_market_stall_A": "denser_individual_fruit_apron_polish",
            "cozy_bridge_arch_A": "clear_void_elevated_voussoirs",
            "cozy_watchtower_A": "darker_thatch_more_layers_fringe",
        },
        "home_bld": "UNTOUCHED_CLOSED_PERMANENTLY",
        "note": "GLBs rewritten; fidelity after headed QA — not auto-claimed 100%.",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    (QUAR / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    log(f"DONE count={len(rows)} receipt={RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

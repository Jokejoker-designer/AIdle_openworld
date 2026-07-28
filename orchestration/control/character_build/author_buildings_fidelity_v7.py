# -*- coding: utf-8 -*-
"""BUILDINGS_FIDELITY_V7 — continuous iteration + architecture/story identity tone.

Geometry positions FROZEN (town_grid_plan_v1). Identity from
AIDLE_TOWN_ARCHITECTURE_DESIGN_001 / AIDLE_STORY_BIBLE_001:

  GARDEN  rest/quiet (Bụi Mơ) — soft petal canopy, low rest deck read
  WELL    water/depth (Nereu-5) — cooler stone, deeper hole, water cue
  WINDMILL energy/mechanism (Cinder-04) — denser lattice sails, bands
  MARKET  trade (Mây Mạch) — produce + scale/weights flavor on apron
  BRIDGE  threshold (Trúc Nhi) — clear arch crossing silhouette
  LOOKOUT vantage (Luma) — taller thatch, open lookout windows

HOME.BLD untouched. No new systems. accepted=false, self_accept=false.
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
from pathlib import Path

import bpy

TAU = math.tau
JOB = "BUILDINGS_FIDELITY_V7"
GAME_DIR = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules")
CAT = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
QUAR.mkdir(parents=True, exist_ok=True)
RECEIPT = Path(r"E:\AIdle_openworld\orchestration\receipts\town_grid_import_001\BUILDINGS_FIDELITY_V7.json")

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
    """MARKET / Mây Mạch trader identity: produce + balance-scale flavor (no economy system)."""
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
    Mmetal = mat("metal", (0.55, 0.58, 0.62), 0.35)

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
    piles = [(-0.55, Mred, 0.12, 16), (0.0, Myel, 0.11, 14), (0.52, Mor, 0.12, 16)]
    for i, (x, fm, rad, nfr) in enumerate(piles):
        for j in range(nfr):
            layer = j // 4
            k = j % 4
            fx = x + ((k % 2) - 0.5) * rad * 1.7 + layer * 0.02
            fy = 0.88 + ((k // 2) - 0.5) * rad * 1.5
            fz = 0.72 + layer * rad * 1.15
            sph(f"F{i}_{j}", (fx, fy, fz), rad * (0.9 if layer else 1.05), fm, segs=12)
            if j % 2 == 0:
                cyl(f"St{i}_{j}", (fx, fy, fz + rad * 0.65), 0.015, 0.05, Mstem, 5)
    # trader scale (flavor only — not an economy system)
    cube("ScaleBase", (0.85, 0.95, 0.78), (0.18, 0.14, 0.06), Mmetal, 0.01)
    cyl("ScalePole", (0.85, 0.95, 0.92), 0.02, 0.22, Mmetal, 6)
    cube("ScaleArm", (0.85, 0.95, 1.02), (0.36, 0.03, 0.03), Mmetal, 0.01)
    cyl("PanL", (0.70, 0.95, 0.95), 0.07, 0.02, Mgold, 8)
    cyl("PanR", (1.00, 0.95, 0.95), 0.07, 0.02, Mgold, 8)
    cube("BskL", (-0.98, 0.80, 0.72), (0.34, 0.30, 0.16), Mw, 0.02)
    for j in range(12):
        sph(f"Gr{j}", (-0.98 + (j % 3 - 1) * 0.07, 0.80 + (j // 3 - 1.5) * 0.05, 0.88), 0.05, Mpur if j % 2 else Mgreen, segs=8)
    for i, x in enumerate([-0.55, 0.10, 0.70]):
        cube(f"Back{i}", (x, -0.15, 0.95), (0.42, 0.40, 0.28), Mw2, 0.03)
    cube("Reg", (0.90, 0.30, 1.00), (0.28, 0.22, 0.30), Mreg, 0.03)
    sph("Knob", (0.98, 0.38, 1.05), 0.04, Mgold)
    parent_all(r)
    return r


def build_gazebo():
    """GARDEN rest identity (Bụi Mơ quiet): softer petal canopy, open rest deck."""
    Mw = mat("wood", (0.78, 0.55, 0.35), 0.55)
    Mf = mat("floor", (0.94, 0.82, 0.60), 0.5)
    Mg1 = mat("g1", (0.42, 0.82, 0.50), 0.48)
    Mg2 = mat("g2", (0.34, 0.72, 0.42), 0.48)
    Mg3 = mat("g3", (0.52, 0.90, 0.58), 0.48)
    Me = mat("emit", (1.0, 0.88, 0.55), 0.4, emit=1.6)
    Mbase = mat("base", (0.85, 0.80, 0.94), 0.65)
    Mpot = mat("pot", (0.85, 0.50, 0.32), 0.55)
    Mleaf = mat("leaf", (0.35, 0.72, 0.40), 0.55)
    Mlav = mat("lav", (0.70, 0.45, 0.85), 0.5)

    r = root_empty("cozy_gazebo_A")
    cyl("Pad", (0, 0, 0.04), 1.48, 0.08, Mbase, 24)
    cyl("Floor", (0, 0, 0.18), 1.12, 0.10, Mf, 20)
    # soft warm rest glow (quiet, not marketplace bright)
    sph("Glow", (0, 0, 0.90), 0.48, Me, (1.0, 1.0, 0.32))
    for i in range(8):
        ang = TAU * i / 8.0
        x, y = 0.92 * math.cos(ang), 0.92 * math.sin(ang)
        cyl(f"Post{i}", (x, y, 0.78), 0.07, 1.20, Mw, 8)
    # low rest rail (social deck, not barrier)
    for i in range(16):
        ang = TAU * i / 16.0
        x, y = 0.95 * math.cos(ang), 0.95 * math.sin(ang)
        cube(f"Rail{i}", (x, y, 0.48), (0.14, 0.06, 0.05), Mw, 0.02)
    for ri, (rad, z) in enumerate([(0.30, 1.58), (0.65, 1.42), (1.00, 1.24)]):
        for i in range(12):
            ang = TAU * i / 12.0
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            cube(f"Frame{ri}_{i}", (x, y, z), (0.12, 0.06, 0.05), Mw, 0.01)
    mats = [Mg1, Mg2, Mg3]
    rings = [
        (0.12, 1.98, 7, 0.24),
        (0.38, 1.85, 12, 0.21),
        (0.62, 1.70, 16, 0.20),
        (0.85, 1.54, 18, 0.19),
        (1.05, 1.38, 20, 0.17),
        (1.20, 1.22, 22, 0.16),
    ]
    for ring, (rad, z, n, pr) in enumerate(rings):
        for i in range(n):
            ang = TAU * i / n + (0.1 if ring % 2 else 0.0)
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            o = cyl(f"Petal{ring}_{i}", (x, y, z), pr, 0.035, mats[(i + ring) % 3], 10)
            apply_rot(o, (0.32, 0, ang))
    cyl("Cap", (0, 0, 2.08), 0.24, 0.08, Mg3, 12)
    sph("CapBall", (0, 0, 2.18), 0.13, Mg1, (1.2, 1.2, 0.7))
    for i in range(8):
        ang = TAU * i / 8.0 + 0.2
        x, y = 1.28 * math.cos(ang), 1.28 * math.sin(ang)
        cyl(f"Pot{i}", (x, y, 0.12), 0.08, 0.14, Mpot, 8)
        sph(f"Pl{i}", (x, y, 0.28), 0.10, Mleaf if i % 2 == 0 else Mlav)
    parent_all(r)
    return r


def build_well():
    """WELL water/depth identity (Nereu-5 visitor): cooler stone, deep hole, water rim cue."""
    Ms = mat("stone", (0.90, 0.92, 0.94), 0.58)  # cooler cream-blue stone
    Ms2 = mat("stone2", (0.82, 0.86, 0.90), 0.58)
    Mw = mat("wood", (0.80, 0.55, 0.32), 0.52)
    Mw2 = mat("wood2", (0.88, 0.64, 0.40), 0.52)
    Mbase = mat("base", (0.92, 0.94, 0.96), 0.65)
    Mrope = mat("rope", (0.92, 0.85, 0.70), 0.6)
    Mdark = mat("dark", (0.12, 0.18, 0.28), 0.8)  # deep water dark
    Mwater = mat("water", (0.35, 0.55, 0.85), 0.25, alpha=0.7)
    Msh = mat("shingle", (0.72, 0.48, 0.28), 0.55)
    Msh2 = mat("shingle2", (0.65, 0.42, 0.24), 0.55)

    r = root_empty("cozy_well_house_A")
    cyl("Pad", (0, 0, 0.03), 1.30, 0.07, Mbase, 24)
    cyl("Body", (0, 0, 0.42), 0.55, 0.75, Ms, 20)
    for i, z in enumerate([0.20, 0.38, 0.56, 0.72]):
        cyl(f"Groove{i}", (0, 0, z), 0.56, 0.04, Ms2 if i % 2 else Ms, 20)
    cyl("Coping", (0, 0, 0.82), 0.58, 0.10, Ms, 18)
    # deeper dark shaft + water plane cue (depth read for oceanpunk visitor)
    cyl("Hole", (0, 0, 0.35), 0.30, 0.80, Mdark, 14)
    cyl("Water", (0, 0, 0.22), 0.28, 0.04, Mwater, 14)
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
    """WINDMILL energy/mechanism identity (Cinder-04 construct): denser lattice, more bands."""
    Mc = mat("clay", (0.97, 0.93, 0.88), 0.6)
    Mc2 = mat("clay2", (0.92, 0.88, 0.82), 0.6)
    Mr = mat("roof", (0.90, 0.48, 0.35), 0.55)
    Mw = mat("wood", (0.70, 0.48, 0.28), 0.5)
    Mcloth = mat("sail", (0.96, 0.92, 0.82), 0.45)
    Md = mat("door", (0.80, 0.52, 0.32), 0.5)
    Me = mat("emit", (1.0, 0.82, 0.40), 0.3, emit=3.2)
    Mbase = mat("base", (0.96, 0.92, 0.84), 0.65)
    Mstone = mat("stone", (0.78, 0.74, 0.70), 0.65)
    Mband = mat("band", (0.78, 0.48, 0.30), 0.45)  # slightly more metal-warm for construct tone
    Mhub = mat("hub", (0.55, 0.50, 0.48), 0.4)

    r = root_empty("cozy_windmill_A")
    cube("Pad", (0, 0, 0.04), (2.2, 2.2, 0.08), Mbase, 0.1)
    cyl("StoneBase", (0, 0, 0.18), 1.05, 0.28, Mstone, 18)
    cone("Tier0", (0, 0, 0.70), 0.95, 0.72, 0.85, Mc, 16)
    cone("Tier1", (0, 0, 1.45), 0.72, 0.55, 0.70, Mc2, 16)
    cone("Tier2", (0, 0, 2.05), 0.55, 0.42, 0.55, Mc, 14)
    for zi, (z, rad) in enumerate([(0.95, 0.82), (1.25, 0.75), (1.60, 0.65), (1.90, 0.55)]):
        cyl(f"Band{zi}", (0, 0, z), rad, 0.08, Mband, 16)
    sph("Roof", (0, 0, 2.45), 0.52, Mr, (1.15, 1.15, 0.75), segs=14)
    cyl("Chim", (0.38, -0.28, 2.70), 0.10, 0.42, mat("chim", (0.96, 0.92, 0.88), 0.55), 8)
    cube("Door", (0, 0.95, 0.55), (0.42, 0.10, 0.65), Md, 0.05)
    sph("Arch", (0, 0.95, 0.92), 0.22, Md, (1.0, 0.35, 0.55), segs=10)
    for i, (x, z) in enumerate([(-0.45, 1.35), (0.45, 1.35), (0.0, 1.90), (-0.35, 1.90), (0.35, 1.90), (0.0, 1.50)]):
        cube(f"Win{i}", (x, 0.55, z), (0.20, 0.08, 0.26), Me, 0.02)
    hub = (0.0, 0.75, 2.10)
    sph("Hub", hub, 0.17, Mhub)
    cyl("HubPlate", (hub[0], hub[1] + 0.03, hub[2]), 0.22, 0.08, Mhub, 12)
    for i in range(4):
        ang = math.radians(i * 90 + 18)
        length = 1.20
        mx = hub[0] + (length * 0.5) * math.cos(ang)
        mz = hub[2] + (length * 0.5) * math.sin(ang)
        spar = cube(f"Spar{i}", (mx, hub[1] + 0.08, mz), (0.09, 0.06, length), Mw, 0.02)
        apply_rot(spar, (0, -ang, 0))
        for k, t in enumerate([0.25, 0.45, 0.65, 0.85]):
            cx = hub[0] + length * t * math.cos(ang)
            cz = hub[2] + length * t * math.sin(ang)
            bar = cube(f"Bar{i}_{k}", (cx, hub[1] + 0.10, cz), (0.36, 0.04, 0.05), Mw, 0.01)
            apply_rot(bar, (0, -ang, 0))
        sx = hub[0] + length * 0.55 * math.cos(ang)
        sz = hub[2] + length * 0.55 * math.sin(ang)
        sail = cube(f"Sail{i}", (sx, hub[1] + 0.12, sz), (0.40, 0.03, 0.90), Mcloth, 0.01)
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
        "visual": f"mockup_{module_id}_v7_identity",
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
    data["buildings_fidelity_v7"] = JOB
    CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"catalog modules={len(data['modules'])}")


def main():
    log("start BUILDINGS_FIDELITY_V7 identity-aligned continuous n=6")
    rows = []
    for mid in MODULES:
        rows.append(export_module(mid))
    update_catalog(rows)
    report = {
        "schema_version": "buildings_fidelity/1.0",
        "receipt_id": "BUILDINGS_FIDELITY_V7",
        "job": JOB,
        "work_order": "WO-TOWN-GRID-IMPORT-001",
        "authority": "PATCH_DRAFT",
        "human_authorization": "continuous_iteration_authorization + architecture/story adherence",
        "architecture_ref": "orchestration/control/AIDLE_TOWN_ARCHITECTURE_DESIGN_001.md",
        "story_bible_ref": "orchestration/control/AIDLE_STORY_BIBLE_001.md",
        "geometry_frozen": True,
        "accepted": False,
        "self_accept": False,
        "purple": "WAITING",
        "matching_100_pct_count": 0,
        "matching_100_pct": [],
        "modules": rows,
        "identity_alignment": {
            "cozy_gazebo_A": {
                "district": "GARDEN",
                "character": "Bụi Mơ CCP-CT-004 non-verbal quiet",
                "tone": "rest_soft_petal_canopy",
            },
            "cozy_well_house_A": {
                "district": "WELL",
                "character": "Nereu-5 OA-RG-021 oceanpunk visitor",
                "tone": "water_depth_cool_stone_deep_shaft",
            },
            "cozy_windmill_A": {
                "district": "WINDMILL",
                "character": "Cinder-04 AC-CO-015 construct visitor",
                "tone": "mechanism_lattice_bands",
            },
            "cozy_market_stall_A": {
                "district": "MARKET",
                "character": "Mây Mạch CCP-NS-002 trader",
                "tone": "produce_plus_scale_flavor_no_economy_system",
            },
            "cozy_bridge_arch_A": {
                "district": "BRIDGE",
                "character": "Trúc Nhi SV-NW-019 visitor threshold",
                "tone": "crossing_arch_void",
            },
            "cozy_watchtower_A": {
                "district": "LOOKOUT",
                "character": "Luma SPH-NG-009 horizon watch",
                "tone": "vantage_thatch_fringe",
            },
        },
        "home_bld": "UNTOUCHED_CLOSED_PERMANENTLY",
        "visitor_origins": "UNRESOLVED_ON_PURPOSE_per_story_bible_§5",
        "note": "Presentation only; positions frozen; fidelity after headed QA — not 100% claimed.",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    (QUAR / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    log(f"DONE count={len(rows)} receipt={RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

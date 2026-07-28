# -*- coding: utf-8 -*-
"""BUILDINGS_FIDELITY_V8 — mockup-topology remesh (not density re-export).

Read MOCKUP_SSOT_V2 building jpgs; change mesh family vs V6–V7 hard geometry:

  MARKET   solid soft counter + continuous thick awning stripes (not plank strips)
  GARDEN   solid green half-dome + tight overlapping scale petals
  WELL     discrete brick rings + thick A-frame wood shingles + hanging bucket
  WINDMILL soft bulbous sphere tiers + 4 SOLID wood sails (not lattice)
  BRIDGE   soft rounded cobble pile arch (mockup SSOT) — reverse of box voussoirs
  LOOKOUT  tapered soft tower + large overlapping thatch scales (not cone layers)

Positions frozen. HOME.BLD untouched. accepted=false, self_accept=false.
Architecture/story identity preserved (districts/characters not reassigned).
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
from pathlib import Path

import bpy

TAU = math.tau
JOB = "BUILDINGS_FIDELITY_V8"
GAME_DIR = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules")
CAT = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
QUAR.mkdir(parents=True, exist_ok=True)
RECEIPT = Path(r"E:\AIdle_openworld\orchestration\receipts\town_grid_import_001\BUILDINGS_FIDELITY_V8.json")

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


def cube(n, loc, sc, m, bevel=0.04):
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
            md.segments = 3
            bpy.ops.object.modifier_apply(modifier=md.name)
            o.select_set(False)
        except Exception:
            pass
    return o


def sph(n, loc, r, m, sc=(1, 1, 1), segs=14):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=segs, ring_count=max(8, segs // 2))
    o = bpy.context.active_object
    o.name = n
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    setm(o, m)
    return o


def cyl(n, loc, r, d, m, verts=14):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=verts)
    o = bpy.context.active_object
    o.name = n
    setm(o, m)
    return o


def cone(n, loc, r1, r2, d, m, verts=14):
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


# ───────────────────────── V8 builders (mockup topology) ─────────────────────────


def build_market():
    """SSOT bld_05: solid wood counter, continuous pink/cream awning, crates, register."""
    Mw = mat("wood", (0.72, 0.50, 0.32), 0.52)
    Mw2 = mat("wood2", (0.82, 0.58, 0.38), 0.52)
    Mpink = mat("awn_p", (0.96, 0.68, 0.78), 0.45)
    Mcream = mat("awn_c", (0.99, 0.94, 0.86), 0.45)
    Mred = mat("apple", (0.92, 0.22, 0.22), 0.38)
    Myel = mat("lemon", (0.96, 0.90, 0.18), 0.38)
    Mor = mat("orange", (0.98, 0.55, 0.15), 0.38)
    Mreg = mat("reg", (0.55, 0.82, 0.68), 0.4)
    Mbase = mat("base", (0.82, 0.75, 0.92), 0.65)
    Mstem = mat("stem", (0.40, 0.68, 0.30), 0.55)
    Mgold = mat("gold", (0.95, 0.80, 0.30), 0.4, emit=0.4)
    Mpot = mat("pot", (0.85, 0.50, 0.32), 0.55)
    Mleaf = mat("leaf", (0.40, 0.75, 0.45), 0.5)
    Mstone = mat("stone", (0.78, 0.74, 0.70), 0.65)

    r = root_empty("cozy_market_stall_A")
    # soft lavender pad
    sph("Pad", (0, 0, 0.02), 1.35, Mbase, (1.15, 1.0, 0.08), segs=16)
    # SOLID counter body (mockup: one soft wood mass with plank seams as shallow cubes)
    cube("Counter", (0, 0.05, 0.55), (1.85, 1.15, 0.95), Mw, 0.12)
    for i, z in enumerate([0.35, 0.55, 0.75]):
        cube(f"Seam{i}", (0, 0.62, z), (1.82, 0.04, 0.06), Mw2, 0.02)
    # posts
    for x in (-0.75, 0.75):
        cyl(f"Post{x}", (x, 0.35, 1.25), 0.08, 0.95, Mw, 10)
    # CONTINUOUS awning: thick curved stripe slabs (not thin separate planks)
    for i in range(6):
        t = (i + 0.5) / 6.0
        x = -0.95 + t * 1.9
        m = Mpink if i % 2 == 0 else Mcream
        # thick rounded stripe
        o = cube(f"Awn{i}", (x, 0.15, 1.72), (0.34, 1.35, 0.22), m, 0.10)
        apply_rot(o, (0.12, 0, 0))  # slight slope
    # front overhang valance
    cube("Val", (0, 0.85, 1.55), (2.0, 0.25, 0.18), Mpink, 0.08)
    # three crates under awning
    crates = [(-0.55, Mred, 6), (-0.05, Myel, 5), (0.50, Mor, 7)]
    for i, (x, fm, nfr) in enumerate(crates):
        cube(f"Crate{i}", (x, 0.25, 1.05), (0.42, 0.42, 0.22), Mw2, 0.04)
        for j in range(nfr):
            layer = j // 3
            k = j % 3
            fx = x + (k - 1) * 0.12
            fy = 0.20 + (layer % 2) * 0.06
            fz = 1.22 + layer * 0.14
            sph(f"Fr{i}_{j}", (fx, fy, fz), 0.10, fm, segs=12)
            if j % 2 == 0 and fm is Mred:
                cyl(f"St{i}_{j}", (fx, fy, fz + 0.09), 0.015, 0.04, Mstem, 5)
    # mint register (mockup center-right)
    cube("Reg", (0.15, 0.55, 1.12), (0.28, 0.22, 0.22), Mreg, 0.05)
    cube("RegTop", (0.15, 0.55, 1.26), (0.18, 0.14, 0.08), Mreg, 0.03)
    sph("Knob", (0.22, 0.62, 1.18), 0.03, Mgold)
    # pots + stones
    for i, (x, y) in enumerate([(-1.0, 0.75), (0.85, 0.85)]):
        cyl(f"Pot{i}", (x, y, 0.12), 0.09, 0.14, Mpot, 8)
        sph(f"Pl{i}", (x, y, 0.28), 0.10, Mleaf)
    for i, (x, y) in enumerate([(-0.3, 0.95), (0.1, 1.05), (0.4, 0.95)]):
        sph(f"Stn{i}", (x, y, 0.05), 0.12, Mstone, (1.3, 1.0, 0.35), segs=8)
    parent_all(r)
    return r


def build_gazebo():
    """SSOT bld_10: solid green scale dome, warm glow, wood posts+rail, plank floor."""
    Mw = mat("wood", (0.80, 0.55, 0.35), 0.5)
    Mf = mat("floor", (0.92, 0.78, 0.55), 0.48)
    Mg1 = mat("g1", (0.45, 0.82, 0.52), 0.48)
    Mg2 = mat("g2", (0.38, 0.75, 0.45), 0.48)
    Mg3 = mat("g3", (0.55, 0.88, 0.58), 0.48)
    Me = mat("emit", (1.0, 0.85, 0.45), 0.35, emit=2.8)
    Mbase = mat("base", (0.82, 0.75, 0.92), 0.65)
    Mpot = mat("pot", (0.85, 0.50, 0.32), 0.55)
    Mleaf = mat("leaf", (0.35, 0.72, 0.40), 0.5)
    Mlav = mat("lav", (0.70, 0.45, 0.85), 0.5)

    r = root_empty("cozy_gazebo_A")
    sph("Pad", (0, 0, 0.02), 1.40, Mbase, (1.1, 1.1, 0.08), segs=16)
    # plank floor disc
    cyl("Floor", (0, 0, 0.16), 1.05, 0.10, Mf, 20)
    for i in range(8):
        ang = TAU * i / 8.0
        x, y = 0.55 * math.cos(ang), 0.55 * math.sin(ang)
        pl = cube(f"Plank{i}", (x, y, 0.18), (0.95, 0.14, 0.03), Mw, 0.02)
        apply_rot(pl, (0, 0, ang))
    # warm interior glow
    sph("Glow", (0, 0, 0.85), 0.55, Me, (1.0, 1.0, 0.45))
    # thick posts
    for i in range(6):
        ang = TAU * i / 6.0
        x, y = 0.88 * math.cos(ang), 0.88 * math.sin(ang)
        cyl(f"Post{i}", (x, y, 0.72), 0.09, 1.10, Mw, 10)
    # curved rail ring (thick wood)
    for i in range(18):
        ang = TAU * i / 18.0
        x, y = 0.92 * math.cos(ang), 0.92 * math.sin(ang)
        cube(f"Rail{i}", (x, y, 0.55), (0.18, 0.08, 0.08), Mw, 0.03)
    # SOLID green dome base
    sph("DomeCore", (0, 0, 1.15), 1.05, Mg2, (1.05, 1.05, 0.55), segs=20)
    # tight overlapping scale petals ON dome surface
    mats = [Mg1, Mg2, Mg3]
    for ring, (elev, rad, n, sc) in enumerate([
        (1.75, 0.25, 8, 0.20),
        (1.62, 0.50, 12, 0.19),
        (1.48, 0.72, 16, 0.18),
        (1.32, 0.90, 18, 0.17),
        (1.18, 1.05, 20, 0.16),
    ]):
        for i in range(n):
            ang = TAU * i / n + (0.08 if ring % 2 else 0.0)
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            # half-disc scale sitting on dome
            o = sph(f"Scale{ring}_{i}", (x, y, elev), sc, mats[(i + ring) % 3], (1.4, 1.1, 0.45), segs=10)
            # tip outward
            apply_rot(o, (0.55, 0, ang))
    sph("Cap", (0, 0, 1.88), 0.28, Mg3, (1.2, 1.2, 0.6))
    for i in range(8):
        ang = TAU * i / 8.0 + 0.15
        x, y = 1.22 * math.cos(ang), 1.22 * math.sin(ang)
        cyl(f"Pot{i}", (x, y, 0.12), 0.08, 0.14, Mpot, 8)
        sph(f"Fl{i}", (x, y, 0.28), 0.10, Mleaf if i % 2 == 0 else Mlav)
    for i, (x, y) in enumerate([(0.15, 1.45), (-0.1, 1.55), (0.35, 1.50)]):
        sph(f"Path{i}", (x, y, 0.04), 0.10, mat(f"st{i}", (0.80, 0.76, 0.72), 0.65), (1.2, 0.9, 0.3), segs=8)
    parent_all(r)
    return r


def build_well():
    """SSOT bld_07: brick-ring well, A-frame with thick wood shingles, hanging bucket."""
    Ms = mat("stone", (0.96, 0.92, 0.86), 0.55)
    Ms2 = mat("stone2", (0.90, 0.86, 0.80), 0.55)
    Mw = mat("wood", (0.85, 0.60, 0.38), 0.48)
    Mw2 = mat("wood2", (0.78, 0.52, 0.32), 0.48)
    Mbase = mat("base", (0.96, 0.92, 0.86), 0.65)
    Mrope = mat("rope", (0.95, 0.90, 0.75), 0.55)
    Mdark = mat("dark", (0.25, 0.28, 0.32), 0.7)
    Msh = mat("sh", (0.88, 0.62, 0.40), 0.5)
    Msh2 = mat("sh2", (0.80, 0.55, 0.35), 0.5)

    r = root_empty("cozy_well_house_A")
    sph("Pad", (0, 0, 0.02), 1.25, Mbase, (1.15, 1.15, 0.08), segs=16)
    # DISCRETE brick rings (mockup: rounded masonry blocks)
    for ring, z in enumerate([0.15, 0.32, 0.48, 0.64]):
        n = 10
        for i in range(n):
            ang = TAU * i / n + (ring * 0.15)
            x, y = 0.50 * math.cos(ang), 0.50 * math.sin(ang)
            cube(f"Br{ring}_{i}", (x, y, z), (0.28, 0.22, 0.18), Ms if (i + ring) % 2 == 0 else Ms2, 0.06)
    cyl("Coping", (0, 0, 0.78), 0.52, 0.12, Ms, 16)
    cyl("Hole", (0, 0, 0.40), 0.32, 0.70, Mdark, 14)
    # A-frame posts
    cyl("PostL", (-0.70, 0, 1.15), 0.09, 1.70, Mw, 10)
    cyl("PostR", (0.70, 0, 1.15), 0.09, 1.70, Mw, 10)
    cube("Cross", (0, 0, 1.85), (1.50, 0.14, 0.14), Mw, 0.04)
    # ridge log
    ridge = cyl("Ridge", (0, 0, 2.15), 0.08, 1.35, Mw2, 10)
    apply_rot(ridge, (0, math.pi / 2, 0))
    # THICK wood shingles on two slopes (large rounded plates)
    for side, y_sign in (("F", 1.0), ("B", -1.0)):
        for row in range(4):
            t = (row + 0.5) / 4.0
            y = y_sign * 0.48 * (1.0 - t * 0.85)
            z = 1.85 + t * 0.45
            for col in range(4):
                u = (col + 0.5) / 4.0
                x = (u - 0.5) * 1.15
                m = Msh if (row + col) % 2 == 0 else Msh2
                o = cube(f"Sh{side}{row}_{col}", (x, y, z), (0.32, 0.22, 0.06), m, 0.04)
                ang = math.atan2(0.45, 0.48) * (1 if y_sign > 0 else -1)
                apply_rot(o, (ang * 0.9, 0, 0))
    # hanging bucket + rope
    cyl("Drum", (0.70, 0, 1.85), 0.12, 0.22, Mw2, 10)
    cyl("Bucket", (0, 0, 1.05), 0.16, 0.24, Mw, 12)
    # staves on bucket
    for i in range(6):
        ang = TAU * i / 6.0
        x, y = 0.15 * math.cos(ang), 0.15 * math.sin(ang)
        cube(f"Stave{i}", (x, y, 1.05), (0.04, 0.04, 0.22), Mw2, 0.01)
    # rope lines
    for sx in (-0.06, 0.06):
        cyl(f"Rope{sx}", (sx, 0, 1.45), 0.015, 0.55, Mrope, 6)
    for i, (x, y) in enumerate([(-0.45, 0.95), (0.0, 1.05), (0.45, 0.95)]):
        sph(f"Path{i}", (x, y, 0.04), 0.13, Ms, (1.3, 1.0, 0.3), segs=8)
    parent_all(r)
    return r


def build_windmill():
    """SSOT bld_06: soft bulbous clay body, 4 SOLID wood sails, pink dome, glow windows."""
    Mc = mat("clay", (0.97, 0.93, 0.88), 0.55)
    Mc2 = mat("clay2", (0.94, 0.90, 0.84), 0.55)
    Mr = mat("roof", (0.92, 0.58, 0.48), 0.5)  # pinkish cap
    Mw = mat("blade", (0.82, 0.60, 0.40), 0.48)
    Md = mat("door", (0.82, 0.55, 0.35), 0.48)
    Me = mat("emit", (1.0, 0.85, 0.45), 0.3, emit=3.5)
    Mbase = mat("base", (0.96, 0.92, 0.86), 0.65)
    Mband = mat("band", (0.88, 0.60, 0.42), 0.5)
    Mhub = mat("hub", (0.75, 0.50, 0.32), 0.45)
    Mpot = mat("pot", (0.85, 0.50, 0.32), 0.55)
    Mleaf = mat("leaf", (0.45, 0.72, 0.50), 0.5)
    Mlav = mat("lav", (0.70, 0.50, 0.85), 0.5)

    r = root_empty("cozy_windmill_A")
    sph("Pad", (0, 0, 0.02), 1.25, Mbase, (1.15, 1.15, 0.08), segs=16)
    # SOFT bulbous lower body (mockup sphere squash)
    sph("BodyLo", (0, 0, 0.65), 0.95, Mc, (1.15, 1.15, 0.85), segs=18)
    # mid waist
    sph("BodyMid", (0, 0, 1.35), 0.72, Mc2, (1.05, 1.05, 0.75), segs=16)
    # upper
    sph("BodyHi", (0, 0, 1.85), 0.55, Mc, (1.0, 1.0, 0.75), segs=14)
    cyl("BandLo", (0, 0, 1.05), 0.85, 0.12, Mband, 16)
    cyl("BandHi", (0, 0, 1.65), 0.62, 0.10, Mband, 14)
    # pink dome cap
    sph("Roof", (0, 0, 2.25), 0.55, Mr, (1.15, 1.15, 0.75), segs=16)
    # chimney
    cyl("Chim", (0.35, -0.25, 2.55), 0.12, 0.45, mat("chim", (0.96, 0.92, 0.88), 0.55), 10)
    # arched door
    cube("Door", (0, 0.95, 0.45), (0.38, 0.10, 0.55), Md, 0.06)
    sph("DoorArch", (0, 0.95, 0.78), 0.20, Md, (1.0, 0.35, 0.55), segs=10)
    # glowing windows (mockup: multiple small arches)
    for i, (x, z, s) in enumerate([
        (-0.55, 0.55, 0.14), (0.55, 0.55, 0.14),
        (0.0, 1.25, 0.12), (-0.40, 1.35, 0.11), (0.40, 1.35, 0.11),
        (0.0, 1.85, 0.12),
    ]):
        sph(f"Win{i}", (x, 0.70, z), s, Me, (1.0, 0.4, 1.1), segs=10)
    # 4 SOLID wood sails (mockup: thick tapered blades, not lattice)
    hub = (0.0, 0.78, 2.05)
    sph("Hub", hub, 0.16, Mhub)
    for i in range(4):
        ang = math.radians(i * 90 + 22)
        length = 1.25
        mx = hub[0] + (length * 0.48) * math.cos(ang)
        mz = hub[2] + (length * 0.48) * math.sin(ang)
        # solid thick blade
        o = cube(f"Blade{i}", (mx, hub[1] + 0.10, mz), (0.28, 0.08, length), Mw, 0.05)
        apply_rot(o, (0, -ang, 0))
    # pots
    for i, (x, y) in enumerate([(-0.95, 0.70), (0.95, 0.65), (-0.2, 1.0), (0.25, 1.0)]):
        cyl(f"Pot{i}", (x, y, 0.12), 0.08, 0.14, Mpot, 8)
        sph(f"Pl{i}", (x, y, 0.28), 0.09, Mleaf if i % 2 else Mlav)
    parent_all(r)
    return r


def build_bridge():
    """SSOT bld_09: soft rounded cobble pile arch (lavender-grey), not hard boxes."""
    Ms1 = mat("s1", (0.88, 0.84, 0.88), 0.5)
    Ms2 = mat("s2", (0.82, 0.78, 0.84), 0.5)
    Ms3 = mat("s3", (0.92, 0.88, 0.92), 0.5)
    Mpk = mat("pk", (0.95, 0.55, 0.70), 0.45)
    Mpu = mat("pu", (0.70, 0.50, 0.90), 0.45)
    Mleaf = mat("leaf", (0.40, 0.75, 0.45), 0.5)

    r = root_empty("cozy_bridge_arch_A")
    mats = [Ms1, Ms2, Ms3]
    # soft cobble arch — larger rounded spheres/squashed spheres stacked
    n = 9
    for i in range(n):
        t = i / (n - 1)
        ang = math.pi * t
        x = 1.05 * math.cos(ang)
        z = 0.25 + 0.95 * math.sin(ang)
        rad = 0.28 + 0.04 * math.sin(i * 1.7)
        o = sph(f"Cob{i}", (x, 0, z), rad, mats[i % 3], (1.15, 1.05, 0.95), segs=12)
    # second layer for depth (pile read)
    for i in range(7):
        t = (i + 0.5) / 7.0
        ang = math.pi * t
        x = 0.95 * math.cos(ang)
        z = 0.40 + 0.85 * math.sin(ang)
        y = 0.18 if i % 2 == 0 else -0.18
        sph(f"Cob2_{i}", (x, y, z), 0.24, mats[(i + 1) % 3], (1.1, 1.0, 0.9), segs=10)
    # apex keystone larger
    sph("Key", (0, 0, 1.15), 0.32, Ms3, (1.2, 1.1, 1.0), segs=12)
    # abutment piles
    for side, x in (("L", -1.15), ("R", 1.15)):
        for j, (dz, r0) in enumerate([(0.15, 0.32), (0.40, 0.28), (0.60, 0.24)]):
            sph(f"Ab{side}{j}", (x, (j - 1) * 0.12, dz), r0, mats[j % 3], (1.1, 1.0, 0.85), segs=10)
    # deck stones on top
    for i in range(5):
        t = (i + 0.5) / 5.0
        x = -0.75 + t * 1.5
        sph(f"Deck{i}", (x, 0, 1.05), 0.22, mats[i % 3], (1.25, 1.1, 0.5), segs=10)
    # flowers
    for i, (x, y) in enumerate([(-1.25, 0.55), (1.25, -0.5), (-0.9, -0.55), (0.9, 0.55)]):
        cyl(f"Stem{i}", (x, y, 0.08), 0.02, 0.16, Mleaf, 5)
        sph(f"Bl{i}", (x, y, 0.20), 0.07, Mpk if i % 2 == 0 else Mpu, segs=8)
    parent_all(r)
    return r


def build_watchtower():
    """SSOT bld_08: soft cream tower, cabin glow windows, large brown thatch scales, ladder."""
    Mc = mat("clay", (0.97, 0.94, 0.90), 0.55)
    Mr1 = mat("t1", (0.72, 0.48, 0.30), 0.55)
    Mr2 = mat("t2", (0.65, 0.42, 0.26), 0.55)
    Mr3 = mat("t3", (0.78, 0.52, 0.34), 0.55)
    Mw = mat("wood", (0.75, 0.52, 0.32), 0.5)
    Me = mat("emit", (1.0, 0.88, 0.50), 0.3, emit=3.2)
    Mband = mat("band", (0.82, 0.58, 0.38), 0.5)

    r = root_empty("cozy_watchtower_A")
    # tapered soft tower (sphere-squash stack)
    sph("BodyLo", (0, 0, 0.70), 0.62, Mc, (1.05, 1.05, 1.15), segs=16)
    sph("BodyHi", (0, 0, 1.55), 0.52, Mc, (1.0, 1.0, 0.95), segs=14)
    # cabin
    cube("Cabin", (0, 0, 2.25), (0.95, 0.95, 0.65), Mc, 0.10)
    cyl("Band", (0, 0, 1.95), 0.58, 0.10, Mband, 14)
    # glowing windows (mockup: large open arches)
    sph("WinF", (0, 0.48, 2.25), 0.22, Me, (1.2, 0.35, 1.0), segs=10)
    sph("WinR", (0.48, 0, 2.25), 0.18, Me, (0.35, 1.2, 0.9), segs=10)
    # LARGE overlapping thatch scales on conical roof (mockup look)
    for ring, (elev, rad, n, sc) in enumerate([
        (2.95, 0.15, 6, 0.18),
        (2.82, 0.35, 10, 0.17),
        (2.68, 0.52, 12, 0.16),
        (2.55, 0.68, 14, 0.16),
        (2.45, 0.82, 14, 0.15),
    ]):
        for i in range(n):
            ang = TAU * i / n + (0.1 if ring % 2 else 0.0)
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            o = sph(f"Th{ring}_{i}", (x, y, elev), sc, [Mr1, Mr2, Mr3][(i + ring) % 3], (1.35, 1.1, 0.42), segs=8)
            apply_rot(o, (0.5, 0, ang))
    sph("Cap", (0, 0, 3.10), 0.18, Mr3, (1.1, 1.1, 0.7))
    # ladder (thick rungs)
    for i in range(8):
        z = 0.20 + i * 0.26
        cube(f"Rung{i}", (0, -0.58, z), (0.38, 0.07, 0.06), Mw, 0.02)
    cyl("RailL", (-0.18, -0.58, 1.10), 0.045, 2.0, Mw, 8)
    cyl("RailR", (0.18, -0.58, 1.10), 0.045, 2.0, Mw, 8)
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
        "visual": f"mockup_topology_v8_{module_id}",
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
    data["buildings_fidelity_v8"] = JOB
    CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"catalog modules={len(data['modules'])}")


def main():
    log("start BUILDINGS_FIDELITY_V8 mockup-topology remesh n=6")
    rows = []
    for mid in MODULES:
        rows.append(export_module(mid))
    update_catalog(rows)
    report = {
        "schema_version": "buildings_fidelity/1.0",
        "receipt_id": "BUILDINGS_FIDELITY_V8",
        "job": JOB,
        "work_order": "WO-TOWN-GRID-IMPORT-001",
        "authority": "PATCH_DRAFT",
        "human_authorization": "continuous_iteration_authorization",
        "architecture_ref": "orchestration/control/AIDLE_TOWN_ARCHITECTURE_DESIGN_001.md",
        "story_bible_ref": "orchestration/control/AIDLE_STORY_BIBLE_001.md",
        "geometry_frozen": True,
        "accepted": False,
        "self_accept": False,
        "purple": "WAITING",
        "matching_100_pct_count": 0,
        "matching_100_pct": [],
        "modules": rows,
        "mesh_strategy_change": {
            "cozy_market_stall_A": "solid_counter_continuous_awning_vs_plank_strips",
            "cozy_gazebo_A": "solid_dome_tight_scale_petals_vs_loose_plates",
            "cozy_well_house_A": "discrete_brick_rings_thick_shingles_vs_solid_cylinder",
            "cozy_windmill_A": "soft_bulbous_body_solid_sails_vs_cones_lattice",
            "cozy_bridge_arch_A": "soft_cobble_pile_arch_vs_box_voussoirs",
            "cozy_watchtower_A": "large_thatch_scales_soft_tower_vs_cone_layers",
        },
        "mockup_ssot_refs": {
            "market": "bld_05_market.jpg",
            "gazebo": "bld_10_gazebo.jpg",
            "well": "bld_07_well.jpg",
            "windmill": "bld_06_windmill.jpg",
            "bridge": "bld_09_bridge.jpg",
            "watchtower": "bld_08_watchtower.jpg",
        },
        "home_bld": "UNTOUCHED_CLOSED_PERMANENTLY",
        "note": "Genuinely different mesh families from V6/V7 hard geometry; fidelity after headed QA.",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    (QUAR / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    log(f"DONE count={len(rows)} receipt={RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

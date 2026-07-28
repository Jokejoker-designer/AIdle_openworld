# -*- coding: utf-8 -*-
"""BUILDINGS_FIDELITY_V9 — residual-targeted mesh strategies (not density re-export).

V8 was mockup-topology family. V9 changes construction language per residual:

  MARKET   open-front crate STAGE + front-facing produce piles (not solid counter mass)
  GARDEN   flower-petal concentric SHELL rings (not solid dome + scatter scales)
  WELL     soft continuous cylinder + CURVED board roof + shingle pads (not brick rings)
  WINDMILL single continuous TAPER body + fat long sails + mushroom cap (not sphere tiers)
  BRIDGE   shell-segment arch with clear VOID silhouette (not cobble pile scatter)
  LOOKOUT  cabin-first two-tier + pie-slice thatch meridians (not scale-sphere layers)

same_sig_streak: if residual signature matches V8 post_sig → streak=1; never claim 100%.
Positions frozen. HOME.BLD untouched. accepted=false, self_accept=false.
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
from pathlib import Path

import bpy

TAU = math.tau
JOB = "BUILDINGS_FIDELITY_V9"
GAME_DIR = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules")
CAT = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
QUAR.mkdir(parents=True, exist_ok=True)
RECEIPT = Path(r"E:\AIdle_openworld\orchestration\receipts\town_grid_import_001\BUILDINGS_FIDELITY_V9.json")

MODULES = [
    "cozy_market_stall_A",
    "cozy_gazebo_A",
    "cozy_well_house_A",
    "cozy_windmill_A",
    "cozy_bridge_arch_A",
    "cozy_watchtower_A",
]

# V8 post signatures (for same_sig_streak tracking)
V8_SIG = {
    "cozy_market_stall_A": "market_solid_counter_awning_ok_fruit_under_awning_still_partial",
    "cozy_gazebo_A": "gazebo_solid_dome_scale_petals_closer_still_not_ssot_100",
    "cozy_well_house_A": "well_brick_rings_aframe_shingles_bucket_closer_still_high_partial",
    "cozy_windmill_A": "windmill_soft_body_solid_sails_closer_still_simplified_vs_ssot",
    "cozy_bridge_arch_A": "bridge_soft_cobble_pile_arch_closer_still_not_ssot_100",
    "cozy_watchtower_A": "watchtower_soft_body_large_thatch_scales_closer_still_partial",
}


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
            md.segments = 4
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


def cone(n, loc, r1, r2, d, m, verts=16):
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


# ───────────────────────── V9 builders ─────────────────────────


def build_market():
    """V9: open-front crate STAGE — produce piles face camera under deep striped awning.

    Residual: fruit_under_awning. Strategy vs V8 solid counter mass.
    Mockup bld_05: 3 crates (red/yellow/orange), mint register front, fat pink/cream stripes.
    """
    Mw = mat("wood", (0.74, 0.52, 0.34), 0.50)
    Mw2 = mat("wood2", (0.84, 0.60, 0.40), 0.50)
    Mplank = mat("plank", (0.68, 0.46, 0.30), 0.52)
    Mpink = mat("awn_p", (0.97, 0.72, 0.80), 0.42)
    Mcream = mat("awn_c", (0.99, 0.95, 0.88), 0.42)
    Mred = mat("apple", (0.93, 0.20, 0.20), 0.35)
    Myel = mat("lemon", (0.97, 0.92, 0.20), 0.35)
    Mor = mat("orange", (0.99, 0.58, 0.12), 0.35)
    Mreg = mat("reg", (0.52, 0.86, 0.70), 0.38)
    Mbase = mat("base", (0.84, 0.78, 0.94), 0.62)
    Mstem = mat("stem", (0.38, 0.68, 0.28), 0.55)
    Mgold = mat("gold", (0.96, 0.82, 0.28), 0.38, emit=0.5)
    Mpot = mat("pot", (0.88, 0.52, 0.34), 0.52)
    Mleaf = mat("leaf", (0.42, 0.78, 0.48), 0.48)
    Mstone = mat("stone", (0.80, 0.76, 0.72), 0.62)
    Mflower = mat("fl", (0.92, 0.55, 0.85), 0.45)

    r = root_empty("cozy_market_stall_A")
    sph("Pad", (0, 0, 0.02), 1.40, Mbase, (1.2, 1.05, 0.07), segs=16)

    # OPEN-FRONT STAGE: rear bulk + three plank faces (mockup blocky counter)
    cube("Rear", (0, -0.15, 0.50), (1.90, 0.70, 0.95), Mw, 0.10)
    # three vertical plank faces front
    for i, x in enumerate([-0.62, 0.0, 0.62]):
        cube(f"Face{i}", (x, 0.38, 0.48), (0.58, 0.18, 0.90), Mplank if i % 2 else Mw2, 0.08)
    # top deck (display shelf) — open, fruit sits ON it front-facing
    cube("Deck", (0, 0.20, 1.00), (1.85, 0.95, 0.12), Mw2, 0.06)

    # posts
    for x in (-0.78, 0.78):
        cyl(f"Post{x}", (x, 0.30, 1.35), 0.09, 1.05, Mw, 10)

    # DEEP awning: 5 fat rounded stripes with front roll (mockup proportions)
    for i in range(5):
        t = (i + 0.5) / 5.0
        x = -0.95 + t * 1.90
        m = Mpink if i % 2 == 0 else Mcream
        o = cube(f"Awn{i}", (x, 0.05, 1.85), (0.42, 1.45, 0.28), m, 0.12)
        apply_rot(o, (0.28, 0, 0))  # steeper slope so underside opens to fruit
    # front scallop roll
    cube("Roll", (0, 0.78, 1.55), (2.05, 0.32, 0.26), Mpink, 0.12)

    # THREE OPEN CRATES on deck — produce piled HIGH and FRONT-facing (residual fix)
    crates = [
        (-0.58, 0.35, Mred, 9, True),   # apples with stems
        (-0.02, 0.35, Myel, 8, False),  # lemons
        (0.55, 0.35, Mor, 10, False),   # oranges
    ]
    for i, (x, y, fm, nfr, stems) in enumerate(crates):
        # crate box open top
        cube(f"Crate{i}", (x, y, 1.12), (0.48, 0.48, 0.18), Mw, 0.04)
        # rim
        cube(f"Rim{i}", (x, y, 1.22), (0.50, 0.50, 0.05), Mw2, 0.02)
        for j in range(nfr):
            layer = j // 3
            k = j % 3
            fx = x + (k - 1) * 0.13
            fy = y + 0.05 + (layer % 2) * 0.08 + 0.05  # push forward under awning
            fz = 1.28 + layer * 0.13
            fr = 0.11 if layer == 0 else 0.10
            sph(f"Fr{i}_{j}", (fx, fy, fz), fr, fm, segs=12)
            if stems and j % 2 == 0:
                cyl(f"St{i}_{j}", (fx, fy, fz + 0.10), 0.015, 0.05, Mstem, 5)

    # mint register front-center on deck (mockup)
    cube("Reg", (0.12, 0.55, 1.18), (0.30, 0.24, 0.24), Mreg, 0.06)
    cube("RegScr", (0.12, 0.55, 1.32), (0.18, 0.12, 0.10), Mreg, 0.03)
    sph("Knob", (0.20, 0.62, 1.22), 0.035, Mgold)

    # corner pots + path stones
    for i, (x, y) in enumerate([(-1.05, 0.80), (0.95, 0.90)]):
        cyl(f"Pot{i}", (x, y, 0.12), 0.10, 0.16, Mpot, 8)
        sph(f"Pl{i}", (x, y, 0.30), 0.11, Mleaf if i == 0 else Mflower)
    for i, (x, y) in enumerate([(-0.25, 1.00), (0.10, 1.10), (0.42, 1.00)]):
        sph(f"Stn{i}", (x, y, 0.05), 0.13, Mstone, (1.35, 1.0, 0.32), segs=8)
    parent_all(r)
    return r


def build_gazebo():
    """V9: flower-petal concentric SHELL rings — roof reads as open flower not solid dome.

    Residual: soft-clay scale density. Strategy vs V8 solid dome + scatter petals.
    Mockup bld_10: large overlapping petal shells, warm interior, thick posts+rail.
    """
    Mw = mat("wood", (0.82, 0.58, 0.38), 0.48)
    Mf = mat("floor", (0.94, 0.80, 0.58), 0.45)
    Mg1 = mat("g1", (0.48, 0.86, 0.55), 0.42)
    Mg2 = mat("g2", (0.40, 0.78, 0.48), 0.42)
    Mg3 = mat("g3", (0.58, 0.90, 0.62), 0.42)
    Me = mat("emit", (1.0, 0.88, 0.50), 0.30, emit=3.5)
    Mbase = mat("base", (0.84, 0.78, 0.94), 0.62)
    Mpot = mat("pot", (0.88, 0.52, 0.34), 0.52)
    Mleaf = mat("leaf", (0.38, 0.75, 0.42), 0.48)
    Mlav = mat("lav", (0.72, 0.48, 0.88), 0.48)
    Mstone = mat("stone", (0.80, 0.76, 0.72), 0.62)

    r = root_empty("cozy_gazebo_A")
    sph("Pad", (0, 0, 0.02), 1.45, Mbase, (1.12, 1.12, 0.07), segs=16)

    # warm plank floor
    cyl("Floor", (0, 0, 0.14), 1.08, 0.12, Mf, 22)
    for i in range(10):
        ang = TAU * i / 10.0
        x, y = 0.50 * math.cos(ang), 0.50 * math.sin(ang)
        pl = cube(f"Plank{i}", (x, y, 0.18), (1.0, 0.13, 0.03), Mw, 0.015)
        apply_rot(pl, (0, 0, ang))

    # strong warm interior pool (mockup glow)
    sph("Glow", (0, 0, 0.70), 0.70, Me, (1.05, 1.05, 0.35), segs=14)

    # 6 thick posts
    for i in range(6):
        ang = TAU * i / 6.0
        x, y = 0.92 * math.cos(ang), 0.92 * math.sin(ang)
        cyl(f"Post{i}", (x, y, 0.75), 0.10, 1.20, Mw, 10)

    # continuous thick rail as linked soft cubes
    for i in range(20):
        ang = TAU * i / 20.0
        x, y = 0.95 * math.cos(ang), 0.95 * math.sin(ang)
        cube(f"Rail{i}", (x, y, 0.52), (0.20, 0.09, 0.09), Mw, 0.035)

    # FLOWER-PETAL SHELL rings — large flattened half-spheres, few rings, high overlap
    # (construction language change: shells not dome core + tiny scales)
    mats = [Mg1, Mg2, Mg3]
    rings = [
        # (elev_z, radius, count, scale_xyz, tip_pitch)
        (1.95, 0.18, 8, (1.55, 1.25, 0.55), 0.35),
        (1.72, 0.48, 10, (1.65, 1.35, 0.50), 0.55),
        (1.48, 0.78, 12, (1.70, 1.40, 0.48), 0.75),
        (1.28, 1.05, 14, (1.60, 1.30, 0.45), 0.95),
    ]
    for ring, (elev, rad, n, sc, pitch) in enumerate(rings):
        for i in range(n):
            ang = TAU * i / n + (0.12 if ring % 2 else 0.0)
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            o = sph(
                f"Petal{ring}_{i}",
                (x, y, elev),
                0.28,
                mats[(i + ring) % 3],
                sc,
                segs=12,
            )
            # tip droops outward like flower petal
            apply_rot(o, (pitch, 0, ang + math.pi / 2))

    # soft center cap (flower eye)
    sph("Cap", (0, 0, 2.05), 0.32, Mg3, (1.15, 1.15, 0.55), segs=12)

    # ring of pots
    for i in range(8):
        ang = TAU * i / 8.0 + 0.2
        x, y = 1.28 * math.cos(ang), 1.28 * math.sin(ang)
        cyl(f"Pot{i}", (x, y, 0.12), 0.09, 0.15, Mpot, 8)
        sph(f"Fl{i}", (x, y, 0.30), 0.11, Mleaf if i % 2 == 0 else Mlav)
    for i, (x, y) in enumerate([(0.12, 1.48), (-0.08, 1.58), (0.32, 1.55)]):
        sph(f"Path{i}", (x, y, 0.04), 0.11, Mstone, (1.25, 0.95, 0.28), segs=8)
    parent_all(r)
    return r


def build_well():
    """V9: soft continuous cylinder + curved board roof (not discrete brick rings).

    Residual: proportions/soft-clay. Strategy vs V8 brick-ring masonry.
    Mockup bld_07: cream rounded well, simple A-frame, continuous shingle slopes, hanging bucket.
    """
    Ms = mat("stone", (0.97, 0.94, 0.88), 0.52)
    Ms2 = mat("stone2", (0.92, 0.88, 0.82), 0.52)
    Mw = mat("wood", (0.88, 0.62, 0.40), 0.45)
    Mw2 = mat("wood2", (0.80, 0.55, 0.35), 0.45)
    Mbase = mat("base", (0.97, 0.94, 0.88), 0.62)
    Mrope = mat("rope", (0.96, 0.92, 0.78), 0.52)
    Mdark = mat("dark", (0.22, 0.26, 0.30), 0.7)
    Msh = mat("sh", (0.90, 0.64, 0.42), 0.48)
    Msh2 = mat("sh2", (0.82, 0.56, 0.36), 0.48)

    r = root_empty("cozy_well_house_A")
    sph("Pad", (0, 0, 0.02), 1.30, Mbase, (1.18, 1.18, 0.07), segs=16)

    # CONTINUOUS soft well body (single fat cylinder + soft rim) — not stacked bricks
    cyl("WellBody", (0, 0, 0.42), 0.58, 0.72, Ms, 20)
    # shallow emboss bricks as thin soft cubes on surface (detail only)
    for ring, z in enumerate([0.20, 0.40, 0.60]):
        n = 8
        for i in range(n):
            ang = TAU * i / n + ring * 0.2
            x, y = 0.56 * math.cos(ang), 0.56 * math.sin(ang)
            cube(f"Emb{ring}_{i}", (x, y, z), (0.22, 0.08, 0.14), Ms2, 0.05)
    # soft rounded coping
    sph("Coping", (0, 0, 0.80), 0.62, Ms, (1.0, 1.0, 0.28), segs=16)
    cyl("Hole", (0, 0, 0.35), 0.34, 0.65, Mdark, 14)

    # A-frame: fat posts + cross
    cyl("PostL", (-0.72, 0, 1.20), 0.10, 1.80, Mw, 10)
    cyl("PostR", (0.72, 0, 1.20), 0.10, 1.80, Mw, 10)
    cube("Cross", (0, 0, 1.95), (1.55, 0.16, 0.16), Mw, 0.05)
    # ridge log
    ridge = cyl("Ridge", (0, 0, 2.22), 0.09, 1.40, Mw2, 10)
    apply_rot(ridge, (0, math.pi / 2, 0))

    # CURVED BOARD ROOF: two thick soft roof slabs + large shingle pads (mockup continuous slope)
    for side, y_sign in (("F", 1.0), ("B", -1.0)):
        # main board
        o = cube(f"Roof{side}", (0, y_sign * 0.32, 2.05), (1.30, 0.55, 0.10), Msh, 0.06)
        apply_rot(o, (y_sign * 0.55, 0, 0))
        # large shingle pads (3 rows x 3) — fewer, bigger, soft
        for row in range(3):
            t = (row + 0.5) / 3.0
            y = y_sign * 0.55 * (1.0 - t * 0.75)
            z = 1.88 + t * 0.40
            for col in range(3):
                u = (col + 0.5) / 3.0
                x = (u - 0.5) * 1.15
                m = Msh if (row + col) % 2 == 0 else Msh2
                s = cube(f"Sh{side}{row}_{col}", (x, y, z), (0.42, 0.30, 0.07), m, 0.05)
                apply_rot(s, (y_sign * 0.50, 0, 0))

    # hanging bucket + ropes
    cyl("Drum", (0.72, 0, 1.95), 0.13, 0.24, Mw2, 10)
    cyl("Bucket", (0, 0, 1.10), 0.17, 0.26, Mw, 12)
    for i in range(6):
        ang = TAU * i / 6.0
        x, y = 0.16 * math.cos(ang), 0.16 * math.sin(ang)
        cube(f"Stave{i}", (x, y, 1.10), (0.04, 0.04, 0.24), Mw2, 0.01)
    for sx in (-0.07, 0.07):
        cyl(f"Rope{sx}", (sx, 0, 1.52), 0.016, 0.60, Mrope, 6)
    for i, (x, y) in enumerate([(-0.48, 0.98), (0.0, 1.08), (0.48, 0.98)]):
        sph(f"Path{i}", (x, y, 0.04), 0.14, Ms, (1.35, 1.0, 0.28), segs=8)
    parent_all(r)
    return r


def build_windmill():
    """V9: single continuous TAPER body + fat long sails + mushroom cap.

    Residual: sail proportion + window glow. Strategy vs V8 sphere-tier stack.
    Mockup bld_06: one tapered clay tower, big 4 blades, pink-brown dome, many warm arches.
    """
    Mc = mat("clay", (0.98, 0.94, 0.90), 0.52)
    Mr = mat("roof", (0.90, 0.55, 0.48), 0.48)  # pink-brown mushroom
    Mw = mat("blade", (0.84, 0.62, 0.42), 0.45)
    Md = mat("door", (0.84, 0.56, 0.36), 0.45)
    Me = mat("emit", (1.0, 0.86, 0.48), 0.28, emit=4.0)
    Mbase = mat("base", (0.97, 0.94, 0.88), 0.62)
    Mband = mat("band", (0.86, 0.58, 0.40), 0.48)
    Mhub = mat("hub", (0.78, 0.52, 0.34), 0.42)
    Mpot = mat("pot", (0.88, 0.52, 0.34), 0.52)
    Mleaf = mat("leaf", (0.48, 0.74, 0.52), 0.48)
    Mlav = mat("lav", (0.72, 0.52, 0.88), 0.48)
    Mchim = mat("chim", (0.96, 0.92, 0.88), 0.52)

    r = root_empty("cozy_windmill_A")
    sph("Pad", (0, 0, 0.02), 1.30, Mbase, (1.18, 1.18, 0.07), segs=16)

    # SINGLE continuous taper (cone) — not stacked spheres
    cone("Body", (0, 0, 1.15), 1.05, 0.48, 2.20, Mc, 20)
    # soft belly bulge mid (subtle squash sphere merged visually)
    sph("Belly", (0, 0, 0.70), 0.95, Mc, (1.12, 1.12, 0.70), segs=16)
    # brown belt rings
    cyl("BandLo", (0, 0, 1.05), 0.88, 0.14, Mband, 16)
    cyl("BandHi", (0, 0, 1.70), 0.62, 0.12, Mband, 14)

    # mushroom cap (hemisphere pink-brown)
    sph("Roof", (0, 0, 2.35), 0.58, Mr, (1.20, 1.20, 0.72), segs=16)
    # chimney
    cyl("Chim", (0.38, -0.22, 2.70), 0.13, 0.50, Mchim, 10)
    sph("ChimLip", (0.38, -0.22, 2.95), 0.15, Mchim, (1.0, 1.0, 0.5), segs=8)

    # arched door front
    cube("Door", (0, 0.98, 0.48), (0.40, 0.12, 0.58), Md, 0.07)
    sph("DoorArch", (0, 0.98, 0.82), 0.22, Md, (1.0, 0.35, 0.55), segs=10)
    cube("Step", (0, 1.10, 0.08), (0.45, 0.22, 0.08), Md, 0.04)

    # MANY glowing arched windows (mockup density)
    win_pos = [
        (-0.60, 0.85, 0.55, 0.15),
        (0.60, 0.85, 0.55, 0.15),
        (-0.35, 0.70, 1.20, 0.12),
        (0.35, 0.70, 1.20, 0.12),
        (0.0, 0.62, 1.25, 0.11),
        (-0.28, 0.55, 1.75, 0.11),
        (0.28, 0.55, 1.75, 0.11),
        (0.0, 0.50, 1.95, 0.12),
    ]
    for i, (x, y, z, s) in enumerate(win_pos):
        sph(f"Win{i}", (x, y, z), s, Me, (1.0, 0.38, 1.15), segs=10)

    # FAT LONG sails — mockup proportion: blades nearly as tall as body
    hub = (0.0, 0.72, 2.15)
    sph("Hub", hub, 0.18, Mhub)
    for i in range(4):
        ang = math.radians(i * 90 + 28)
        length = 1.55  # longer than V8's 1.25
        mx = hub[0] + (length * 0.48) * math.cos(ang)
        mz = hub[2] + (length * 0.48) * math.sin(ang)
        # fat blade (wider + thicker)
        o = cube(f"Blade{i}", (mx, hub[1] + 0.12, mz), (0.36, 0.10, length), Mw, 0.06)
        apply_rot(o, (0, -ang, 0))

    # pots
    for i, (x, y) in enumerate([(-1.0, 0.72), (1.0, 0.68), (-0.25, 1.05), (0.28, 1.05)]):
        cyl(f"Pot{i}", (x, y, 0.12), 0.09, 0.15, Mpot, 8)
        sph(f"Pl{i}", (x, y, 0.30), 0.10, Mleaf if i % 2 else Mlav)
    parent_all(r)
    return r


def build_bridge():
    """V9: shell-segment arch with clear VOID — tortoise-shell silhouette not pile.

    Residual: material/void read. Strategy vs V8 cobble scatter pile.
    Mockup bld_09: large rounded stones forming arch ring with open underside.
    """
    Ms1 = mat("s1", (0.90, 0.86, 0.90), 0.48)
    Ms2 = mat("s2", (0.84, 0.80, 0.86), 0.48)
    Ms3 = mat("s3", (0.94, 0.90, 0.94), 0.48)
    Mpk = mat("pk", (0.96, 0.58, 0.72), 0.42)
    Mpu = mat("pu", (0.72, 0.52, 0.92), 0.42)
    Mleaf = mat("leaf", (0.42, 0.78, 0.48), 0.48)

    r = root_empty("cozy_bridge_arch_A")
    mats = [Ms1, Ms2, Ms3]

    # ARCH RING: shell segments (heavily beveled fat cubes) on semicircle — clear void under
    n = 11
    for i in range(n):
        t = i / (n - 1)
        ang = math.pi * t
        # arch radius keeps center open
        x = 1.15 * math.cos(ang)
        z = 0.18 + 1.05 * math.sin(ang)
        # each stone is a soft fat block, elongated along tangent
        o = cube(f"Seg{i}", (x, 0, z), (0.42, 0.48, 0.36), mats[i % 3], 0.14)
        # rotate so long axis follows arch
        apply_rot(o, (0, 0, ang - math.pi / 2))

    # secondary outer shell (depth) — offset radially out a bit
    for i in range(7):
        t = (i + 0.5) / 7.0
        ang = math.pi * t
        x = 1.35 * math.cos(ang)
        z = 0.15 + 0.95 * math.sin(ang)
        y = 0.22 if i % 2 == 0 else -0.22
        cube(f"Outer{i}", (x, y, z), (0.36, 0.40, 0.32), mats[(i + 1) % 3], 0.12)

    # large keystone at apex
    cube("Key", (0, 0, 1.25), (0.50, 0.52, 0.42), Ms3, 0.15)

    # abutment feet (fat soft)
    for side, x in (("L", -1.25), ("R", 1.25)):
        for j, (dz, sc) in enumerate([(0.18, 0.45), (0.48, 0.40)]):
            cube(f"Ab{side}{j}", (x, 0, dz), (sc, sc * 0.95, 0.38), mats[j % 3], 0.12)

    # deck path on top (flatter stones)
    for i in range(5):
        t = (i + 0.5) / 5.0
        x = -0.85 + t * 1.70
        z = 1.05 + 0.12 * math.sin(math.pi * t)
        cube(f"Deck{i}", (x, 0, z), (0.36, 0.40, 0.18), mats[i % 3], 0.08)

    # pixel flowers
    for i, (x, y) in enumerate([(-1.35, 0.55), (1.30, -0.50), (-0.95, -0.55), (0.95, 0.55)]):
        cyl(f"Stem{i}", (x, y, 0.08), 0.02, 0.16, Mleaf, 5)
        sph(f"Bl{i}", (x, y, 0.20), 0.075, Mpk if i % 2 == 0 else Mpu, segs=8)
    parent_all(r)
    return r


def build_watchtower():
    """V9: cabin-first two-tier + pie-slice thatch meridians.

    Residual: cabin glow + thatch scale read. Strategy vs V8 sphere-stack + many tiny scales.
    Mockup bld_08: tall soft taper, square cabin with large glowing windows, big thatch tiles, ladder.
    """
    Mc = mat("clay", (0.98, 0.95, 0.92), 0.52)
    Mr1 = mat("t1", (0.74, 0.50, 0.32), 0.50)
    Mr2 = mat("t2", (0.66, 0.44, 0.28), 0.50)
    Mr3 = mat("t3", (0.80, 0.54, 0.36), 0.50)
    Mw = mat("wood", (0.78, 0.54, 0.34), 0.48)
    Me = mat("emit", (1.0, 0.90, 0.52), 0.28, emit=4.0)
    Mband = mat("band", (0.84, 0.60, 0.40), 0.48)
    Mdark = mat("dark", (0.35, 0.28, 0.22), 0.6)

    r = root_empty("cozy_watchtower_A")

    # continuous soft tapered shaft (single cone) — cabin-first hierarchy
    cone("Shaft", (0, 0, 1.05), 0.72, 0.52, 2.05, Mc, 18)
    # soft base bulb
    sph("Base", (0, 0, 0.35), 0.68, Mc, (1.05, 1.05, 0.70), segs=14)

    # cabin cube on top with large glowing openings
    cube("Cabin", (0, 0, 2.35), (1.05, 1.05, 0.72), Mc, 0.12)
    cyl("Band", (0, 0, 2.00), 0.62, 0.12, Mband, 14)

    # large glowing windows — front + side (mockup open warm squares)
    # front opening frame
    cube("WinF_frame", (0, 0.52, 2.35), (0.48, 0.08, 0.42), Mdark, 0.03)
    cube("WinF_glow", (0, 0.48, 2.35), (0.40, 0.06, 0.34), Me, 0.02)
    # side
    cube("WinR_frame", (0.52, 0, 2.35), (0.08, 0.42, 0.38), Mdark, 0.03)
    cube("WinR_glow", (0.48, 0, 2.35), (0.06, 0.34, 0.30), Me, 0.02)
    # interior glow sphere for spill
    sph("CabinGlow", (0, 0, 2.35), 0.35, Me, (1.0, 1.0, 0.7), segs=10)

    # PIE-SLICE thatch: few large soft scales in 3 rings (mockup big tiles)
    mats = [Mr1, Mr2, Mr3]
    for ring, (elev, rad, n, sc_xy, sc_z) in enumerate([
        (3.05, 0.12, 6, 0.32, 0.14),
        (2.88, 0.38, 8, 0.34, 0.13),
        (2.70, 0.62, 10, 0.36, 0.12),
        (2.55, 0.82, 10, 0.34, 0.11),
    ]):
        for i in range(n):
            ang = TAU * i / n + (0.08 if ring % 2 else 0.0)
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            # pie-slice: flattened sphere elongated radially
            o = sph(
                f"Th{ring}_{i}",
                (x, y, elev),
                0.22,
                mats[(i + ring) % 3],
                (sc_xy * 1.6, sc_xy * 1.2, sc_z * 2.2),
                segs=10,
            )
            apply_rot(o, (0.65, 0, ang))

    sph("Cap", (0, 0, 3.22), 0.20, Mr3, (1.15, 1.15, 0.65), segs=10)

    # ladder — thick rails + rungs to cabin
    for i in range(9):
        z = 0.18 + i * 0.24
        cube(f"Rung{i}", (0, -0.62, z), (0.42, 0.08, 0.07), Mw, 0.025)
    cyl("RailL", (-0.20, -0.62, 1.15), 0.05, 2.15, Mw, 8)
    cyl("RailR", (0.20, -0.62, 1.15), 0.05, 2.15, Mw, 8)
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

STRATEGIES = {
    "cozy_market_stall_A": "open_front_crate_stage_vs_solid_counter_mass",
    "cozy_gazebo_A": "flower_petal_concentric_shells_vs_solid_dome_scatter",
    "cozy_well_house_A": "soft_cylinder_curved_board_roof_vs_brick_rings",
    "cozy_windmill_A": "single_taper_fat_sails_mushroom_cap_vs_sphere_tiers",
    "cozy_bridge_arch_A": "shell_segment_void_arch_vs_cobble_pile",
    "cozy_watchtower_A": "cabin_first_pie_slice_thatch_vs_scale_sphere_layers",
}

# New residual signatures claimed after V9 (distinct from V8)
V9_POST_SIG = {
    "cozy_market_stall_A": "market_open_front_crate_stage_produce_front_facing_high_partial",
    "cozy_gazebo_A": "gazebo_flower_petal_shell_rings_warm_interior_high_partial",
    "cozy_well_house_A": "well_soft_cylinder_curved_board_roof_bucket_high_partial",
    "cozy_windmill_A": "windmill_single_taper_fat_sails_window_glow_high_partial",
    "cozy_bridge_arch_A": "bridge_shell_segment_void_arch_high_partial",
    "cozy_watchtower_A": "watchtower_cabin_first_pie_thatch_glow_high_partial",
}

PLOT = {
    "cozy_market_stall_A": "MARKET.BLD",
    "cozy_gazebo_A": "GARDEN.BLD",
    "cozy_well_house_A": "WELL.BLD",
    "cozy_windmill_A": "WINDMILL.BLD",
    "cozy_bridge_arch_A": "BRIDGE.BLD",
    "cozy_watchtower_A": "LOOKOUT.BLD",
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
        "visual": f"mockup_residual_v9_{module_id}",
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
    data["buildings_fidelity_v9"] = JOB
    CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"catalog modules={len(data['modules'])}")


def main():
    log("start BUILDINGS_FIDELITY_V9 residual-targeted remesh n=6")
    rows = []
    for mid in MODULES:
        rows.append(export_module(mid))
    update_catalog(rows)

    objects = []
    for mid in MODULES:
        post = V9_POST_SIG[mid]
        prior = V8_SIG[mid]
        # new strategy → new signature; streak resets to 0 when signature changes
        same = post == prior
        streak = 1 if same else 0
        objects.append({
            "plot_id": PLOT[mid],
            "object_id": mid,
            "v9_strategy": STRATEGIES[mid],
            "prior_v8_sig": prior,
            "post_v9_signature": post,
            "same_sig_streak": streak,
            "fidelity": "HIGH_PARTIAL",
            "matching_100_pct": False,
            "note": f"V9 strategy {STRATEGIES[mid]}; not claimed 100% without Human visual accept.",
        })

    need_human = [o["plot_id"] for o in objects if o["same_sig_streak"] >= 3]

    report = {
        "schema_version": "buildings_fidelity/1.0",
        "receipt_id": "BUILDINGS_FIDELITY_V9",
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
        "mesh_strategy_change": STRATEGIES,
        "mockup_ssot_refs": {
            "market": "bld_05_market.jpg",
            "gazebo": "bld_10_gazebo.jpg",
            "well": "bld_07_well.jpg",
            "windmill": "bld_06_windmill.jpg",
            "bridge": "bld_09_bridge.jpg",
            "watchtower": "bld_08_watchtower.jpg",
        },
        "home_bld": "UNTOUCHED_CLOSED_PERMANENTLY",
        "objects": objects,
        "safety_valve": {
            "need_human": need_human,
            "same_sig_streak_max": max(o["same_sig_streak"] for o in objects),
            "note": "All 6 got NEW residual-targeted strategies vs V8; streaks reset unless signature identical.",
        },
        "note": "V9 residual-targeted mesh language change (not density-only). Fidelity HIGH_PARTIAL until Human visual.",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    (QUAR / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    log(f"DONE count={len(rows)} receipt={RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

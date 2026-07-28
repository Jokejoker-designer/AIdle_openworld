# -*- coding: utf-8 -*-
"""BUILDINGS_FIDELITY_V5 — continuous-iteration pass for 6 open buildings.

Different approaches vs V4 density-only plateaus:
  MARKET  front apron table + oversized produce (readable under awning)
  GARDEN  petal-plate scales (flattened discs) not only spheres
  WELL    plate-shingle roof + thicker masonry rings
  WINDMILL lattice sail frames (not simple blades)
  BRIDGE  box voussoir arch (not soft sphere pile)
  LOOKOUT brown thatch layers (hue fix from peach)

HOME.BLD untouched. accepted=false, self_accept=false.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy

TAU = math.tau
JOB = "BUILDINGS_FIDELITY_V5"
GAME_DIR = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules")
CAT = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
QUAR.mkdir(parents=True, exist_ok=True)
RECEIPT = Path(r"E:\AIdle_openworld\orchestration\receipts\town_grid_import_001\BUILDINGS_FIDELITY_V5.json")

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


def roof_tiles_gable(prefix, cx, cy, base_z, half_w, half_d, peak_h, mats, rows=5, cols=6):
    """V3: TRUE slope fishscales — flattened spheres on gable planes (not shelf-plank boxes).

    Each side is a planar slope from eave (y=±half_d, z=base_z) to ridge (y=0, z=base_z+peak_h).
    Scales are half-discs (squashed spheres) staggered per row so freecam reads terracotta clay tiles.
    """
    for side, y_sign in (("F", 1.0), ("B", -1.0)):
        for row in range(rows):
            t = (row + 0.5) / rows  # 0 at eave → 1 near ridge
            # interpolate along slope plane
            y = cy + y_sign * half_d * (1.0 - t)
            z = base_z + t * peak_h + 0.04
            # stagger columns every other row
            col_off = 0.5 if row % 2 else 0.0
            n_cols = cols if row % 2 == 0 else cols - 1
            if n_cols < 1:
                n_cols = 1
            for col in range(n_cols):
                u = (col + 0.5 + col_off * 0.0) / cols
                if row % 2:
                    u = (col + 1.0) / (cols + 0.5)
                x = cx + (u - 0.5) * half_w * 2.0 * 0.95
                m = mats[(row + col) % len(mats)]
                # half-disc scale: wide X, thin Y, medium Z — sits on slope surface
                rad = half_w * 0.22
                o = sph(
                    f"{prefix}_{side}_{row}_{col}",
                    (x, y, z),
                    rad,
                    m,
                    sc=(1.35, 0.55, 0.72),
                    segs=10,
                )
                # tip scale slightly toward slope normal (approximate via euler)
                # front slope faces +Y→down; tilt so flat face follows roof plane
                slope_ang = math.atan2(peak_h, half_d)
                if y_sign > 0:
                    o.rotation_euler = (slope_ang * 0.85, 0.0, 0.0)
                else:
                    o.rotation_euler = (-slope_ang * 0.85, 0.0, 0.0)
                bpy.context.view_layer.objects.active = o
                o.select_set(True)
                try:
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                except Exception:
                    pass
                o.select_set(False)
    # ridge cap spheres (continuous clay ridge, not a flat plank)
    for i in range(max(3, cols - 1)):
        u = (i + 0.5) / max(3, cols - 1)
        x = cx + (u - 0.5) * half_w * 2.0 * 0.9
        sph(
            f"{prefix}_Ridge_{i}",
            (x, cy, base_z + peak_h + 0.08),
            half_w * 0.14,
            mats[i % len(mats)],
            sc=(1.4, 0.9, 0.7),
            segs=8,
        )


def roof_tiles_aframe(prefix, base_z, half_w, half_d, peak_h, mats, rows=4, cols=4):
    """Well-house style A-frame: sphere scales on two slopes (Y-thin roof over X posts)."""
    for side, y_sign in (("F", 1.0), ("B", -1.0)):
        for row in range(rows):
            t = (row + 0.5) / rows
            y = y_sign * half_d * (1.0 - t * 0.85)
            z = base_z + t * peak_h
            for col in range(cols):
                u = (col + 0.5) / cols
                x = (u - 0.5) * half_w * 2.0
                m = mats[(row + col) % len(mats)]
                o = sph(f"{prefix}_{side}_{row}_{col}", (x, y, z), 0.14, m, sc=(1.3, 0.55, 0.7), segs=8)
                ang = math.atan2(peak_h, half_d) * (1 if y_sign > 0 else -1) * 0.9
                o.rotation_euler = (ang, 0.0, 0.0)
                bpy.context.view_layer.objects.active = o
                o.select_set(True)
                try:
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                except Exception:
                    pass
                o.select_set(False)


# ───────────────────────── builders ─────────────────────────


def build_workshop():
    """SSOT bld_04 V2: soft cream clay, terracotta fishscales, open work window, bench + tools."""
    Mc = mat("M_clay", (0.97, 0.92, 0.84), 0.62)
    Mr1 = mat("M_roof_a", (0.95, 0.48, 0.32), 0.55)
    Mr2 = mat("M_roof_b", (0.90, 0.40, 0.28), 0.55)
    Mr3 = mat("M_roof_c", (0.98, 0.58, 0.40), 0.55)
    Mw = mat("M_wood", (0.72, 0.48, 0.30), 0.55)
    Me = mat("M_emit", (1.0, 0.85, 0.45), 0.35, emit=3.2)
    Mmetal = mat("M_metal", (0.55, 0.58, 0.62), 0.35)
    Mleaf = mat("M_leaf", (0.35, 0.72, 0.40), 0.55)
    Mpot = mat("M_pot", (0.85, 0.50, 0.32), 0.55)
    Myarn1 = mat("M_yarn1", (0.95, 0.40, 0.68), 0.45)
    Myarn2 = mat("M_yarn2", (0.40, 0.85, 0.50), 0.45)
    Myarn3 = mat("M_yarn3", (0.50, 0.50, 0.95), 0.45)
    Mbase = mat("M_base", (0.78, 0.70, 0.90), 0.65)
    Mteal = mat("M_teal", (0.35, 0.75, 0.70), 0.5)

    r = root_empty("cozy_workshop_A")
    cube("Base", (0, 0, 0.04), (2.5, 2.3, 0.08), Mbase, 0.1)
    # rounded clay body (sphere-squashed + box hybrid)
    sph("BodySoft", (0, 0, 0.85), 1.05, Mc, (1.05, 0.95, 0.85), segs=16)
    cube("BodyCore", (0, 0, 0.80), (1.75, 1.55, 1.35), Mc, 0.12)
    cube("Gable", (0, 0, 1.55), (1.75, 0.45, 0.50), Mc, 0.08)
    # dense terracotta fishscales
    # V3: sphere fishscales only — no plank Ridge cube
    roof_tiles_gable("Roof", 0, 0, 1.28, 1.08, 0.98, 0.85, [Mr1, Mr2, Mr3], rows=6, cols=7)
    cyl("Chimney", (0.55, -0.40, 2.25), 0.13, 0.50, mat("M_chim", (0.96, 0.93, 0.88), 0.55), 10)
    for i, (dx, dz) in enumerate([(0, 0.35), (0.12, 0.55), (-0.08, 0.70)]):
        sph(f"Smoke{i}", (0.55 + dx, -0.40, 2.45 + dz), 0.11 - i * 0.02, mat(f"M_sm{i}", (0.96, 0.96, 0.98), 0.85))
    # big open work window on +Y (shows interior)
    cube("WinFrame", (0, 0.82, 0.85), (1.05, 0.10, 0.78), Mw, 0.04)
    cube("WinGlow", (0, 0.78, 0.85), (0.90, 0.06, 0.65), Me, 0.0)
    # shelf + yarn inside opening
    cube("Shelf", (0, 0.55, 0.70), (0.70, 0.25, 0.05), Mw, 0.02)
    sph("Yarn1", (-0.22, 0.55, 0.90), 0.12, Myarn1)
    sph("Yarn2", (0.0, 0.52, 0.85), 0.11, Myarn2)
    sph("Yarn3", (0.22, 0.58, 0.92), 0.10, Myarn3)
    cyl("Jar1", (0.05, 0.55, 0.78), 0.05, 0.10, mat("M_jar", (0.90, 0.55, 0.85), 0.4), 8)
    cube("WinTop", (0, 0.82, 1.55), (0.32, 0.08, 0.30), Me, 0.03)
    # workbench left of window
    cube("BenchTop", (-0.95, 0.70, 0.48), (0.90, 0.50, 0.10), Mw, 0.04)
    for lx, ly in [(-1.25, 0.55), (-0.65, 0.55), (-1.25, 0.85), (-0.65, 0.85)]:
        cube(f"BLeg_{lx}_{ly}", (lx, ly, 0.24), (0.08, 0.08, 0.42), Mw, 0.02)
    cube("Vise", (-1.20, 0.70, 0.58), (0.20, 0.14, 0.14), Mmetal, 0.02)
    for i, x in enumerate([-1.0, -0.88, -0.76, -0.64]):
        cyl(f"Rod{i}", (x, 0.70, 0.55), 0.025, 0.38, Mw, 6)
    # hanging tools on +X wall
    for i, (y, z, h) in enumerate([(0.35, 1.0, 0.32), (0.10, 1.05, 0.28), (-0.15, 0.98, 0.30), (-0.38, 1.05, 0.26)]):
        cube(f"ToolHead{i}", (0.92, y, z), (0.07, 0.10, 0.12), Mmetal, 0.01)
        cyl(f"ToolH{i}", (0.92, y, z - 0.16), 0.03, h, Mw, 6)
    # front pots
    for i, (x, y) in enumerate([(-1.15, -0.75), (0.55, 0.95), (0.85, 0.75), (0.95, 0.45), (0.65, 0.95), (-0.35, 0.95)]):
        cyl(f"Pot{i}", (x, y, 0.12), 0.08, 0.14, Mpot, 8)
        sph(f"Plant{i}", (x, y, 0.28), 0.10, Mleaf if i % 2 == 0 else Mteal)
    cube("Crate", (-0.35, 0.95, 0.12), (0.30, 0.24, 0.16), Mw, 0.02)
    parent_all(r)
    return r


def build_market():
    """V5: front apron table + OVERSIZED produce (readable under freecam), not under-awning crates only."""
    Mw = mat("M_wood", (0.70, 0.45, 0.28), 0.55)
    Mw2 = mat("M_wood2", (0.82, 0.58, 0.36), 0.55)
    Mpink = mat("M_awn_pink", (0.96, 0.62, 0.75), 0.48)
    Mcream = mat("M_awn_cream", (0.99, 0.95, 0.88), 0.48)
    Mred = mat("M_apple", (0.92, 0.22, 0.22), 0.4)
    Myel = mat("M_lemon", (0.96, 0.90, 0.18), 0.4)
    Mor = mat("M_fruit_o", (0.98, 0.52, 0.12), 0.4)
    Mgreen = mat("M_fruit_g", (0.45, 0.78, 0.30), 0.45)
    Mpur = mat("M_grape", (0.55, 0.30, 0.65), 0.4)
    Mreg = mat("M_reg", (0.55, 0.85, 0.68), 0.42)
    Mbase = mat("M_base", (0.78, 0.70, 0.90), 0.65)
    Mcloth = mat("M_cloth", (0.98, 0.92, 0.80), 0.5)
    Mstem = mat("M_stem", (0.45, 0.70, 0.30), 0.55)
    Mgold = mat("M_gold", (0.95, 0.80, 0.30), 0.4, emit=0.5)

    r = root_empty("cozy_market_stall_A")
    cube("Base", (0, 0, 0.04), (2.5, 2.1, 0.08), Mbase, 0.1)
    for i, z in enumerate([0.22, 0.48, 0.72]):
        cube(f"Body{i}", (0, -0.05, z), (1.90, 1.10, 0.24), Mw if i % 2 == 0 else Mw2, 0.05)
    for x, y in [(-0.88, 0.45), (0.88, 0.45), (-0.88, -0.50), (0.88, -0.50)]:
        cyl(f"Post_{x}_{y}", (x, y, 1.20), 0.07, 1.2, Mw, 8)
    for i in range(8):
        t = i / 7.0
        x = -1.10 + t * 2.2
        cube(f"Awn{i}", (x, 0.05, 1.65), (0.28, 1.50, 0.18), Mpink if i % 2 == 0 else Mcream, 0.06)
    cube("AwnValance", (0, 0.85, 1.45), (2.25, 0.32, 0.18), Mpink, 0.06)
    # V5 front apron — produce OUT in front of stall where camera reads
    cube("Apron", (0, 0.85, 0.55), (1.85, 0.55, 0.10), Mw2, 0.04)
    cube("Cloth", (0, 0.88, 0.62), (1.70, 0.48, 0.04), Mcloth, 0.02)
    # three big produce mounds on apron
    piles = [(-0.55, Mred, 0.16), (0.0, Myel, 0.15), (0.55, Mor, 0.16)]
    for i, (x, fm, rad) in enumerate(piles):
        for j in range(8):
            layer = j // 3
            k = j % 3
            fx = x + (k - 1) * rad * 0.9
            fy = 0.85 + (layer % 2) * 0.08
            fz = 0.72 + layer * rad * 0.85
            sph(f"BigFruit{i}_{j}", (fx, fy, fz), rad * (0.85 if layer else 1.0), fm, segs=12)
            if j % 2 == 0:
                cyl(f"St{i}_{j}", (fx, fy, fz + rad * 0.6), 0.02, 0.06, Mstem, 5)
    # basket of grapes left front
    cube("Basket", (-0.95, 0.75, 0.70), (0.32, 0.28, 0.16), Mw, 0.02)
    for j in range(10):
        sph(f"Gr{j}", (-0.95 + (j % 3 - 1) * 0.07, 0.75 + (j // 3 - 1) * 0.05, 0.85), 0.055, Mpur if j % 2 else Mgreen, segs=8)
    # back crates still present
    for i, x in enumerate([-0.5, 0.15, 0.70]):
        cube(f"BackCrate{i}", (x, -0.15, 0.95), (0.40, 0.40, 0.28), Mw2, 0.03)
    cube("Reg", (0.90, 0.40, 1.00), (0.28, 0.22, 0.30), Mreg, 0.03)
    sph("RegKnob", (0.98, 0.48, 1.05), 0.04, Mgold)
    parent_all(r)
    return r


def build_gazebo():
    """V4 TARGET: fishscale_density — denser green dome scales (SSOT petal layers)."""
    Mw = mat("M_wood", (0.78, 0.55, 0.35), 0.55)
    Mf = mat("M_floor", (0.92, 0.78, 0.55), 0.5)
    Mg1 = mat("M_roof_g1", (0.42, 0.80, 0.48), 0.52)
    Mg2 = mat("M_roof_g2", (0.35, 0.72, 0.42), 0.52)
    Mg3 = mat("M_roof_g3", (0.52, 0.88, 0.55), 0.52)
    Me = mat("M_emit", (1.0, 0.85, 0.45), 0.4, emit=2.2)
    Mbase = mat("M_base", (0.82, 0.75, 0.92), 0.65)
    Mpot = mat("M_pot", (0.85, 0.50, 0.32), 0.55)
    Mleaf = mat("M_leaf", (0.35, 0.72, 0.40), 0.55)
    Mlav = mat("M_lav", (0.70, 0.45, 0.85), 0.5)
    Mstone = mat("M_stone", (0.80, 0.76, 0.72), 0.65)

    r = root_empty("cozy_gazebo_A")
    cyl("BasePad", (0, 0, 0.04), 1.40, 0.08, Mbase, 24)
    cyl("Floor", (0, 0, 0.18), 1.08, 0.10, Mf, 20)
    sph("Glow", (0, 0, 0.95), 0.55, Me, (1.0, 1.0, 0.4))
    for i in range(6):
        ang = TAU * i / 6.0
        x, y = 0.88 * math.cos(ang), 0.88 * math.sin(ang)
        cyl(f"Post{i}", (x, y, 0.75), 0.075, 1.15, Mw, 8)
    for i in range(16):
        ang = TAU * i / 16.0
        x, y = 0.92 * math.cos(ang), 0.92 * math.sin(ang)
        cube(f"Rail{i}", (x, y, 0.55), (0.16, 0.07, 0.06), Mw, 0.02)
    # V4 denser fishscale dome — more rings + more scales + stagger
    rings = [
        (0.12, 1.88, 1, 0.28),
        (0.32, 1.78, 8, 0.18),
        (0.50, 1.68, 12, 0.17),
        (0.68, 1.55, 16, 0.16),
        (0.86, 1.42, 18, 0.15),
        (1.02, 1.30, 20, 0.15),
        (1.15, 1.18, 22, 0.14),
    ]
    mats = [Mg1, Mg2, Mg3]
    for ring, (rad, z, n, sc) in enumerate(rings):
        if n == 1:
            sph("RoofCap", (0, 0, z), sc, Mg3, (1.3, 1.3, 0.55))
            continue
        for i in range(n):
            ang = TAU * i / n + (0.08 if ring % 2 else 0.0)
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            sph(f"Tile{ring}_{i}", (x, y, z), sc, mats[(i + ring) % 3], (1.35, 1.05, 0.52), segs=8)
    for i in range(8):
        ang = TAU * i / 8.0 + 0.2
        x, y = 1.20 * math.cos(ang), 1.20 * math.sin(ang)
        cyl(f"Pot{i}", (x, y, 0.12), 0.08, 0.14, Mpot, 8)
        sph(f"Pl{i}", (x, y, 0.28), 0.10, Mleaf if i % 2 == 0 else Mlav)
    for i, (x, y) in enumerate([(0.2, 1.40), (-0.15, 1.50), (0.4, 1.55)]):
        sph(f"Path{i}", (x, y, 0.05), 0.10, Mstone, (1.2, 0.9, 0.3), segs=8)
    parent_all(r)
    return r


def build_well():
    """V4 TARGET: overall form — tighter stone cylinder, proper A-frame house silhouette, winch+bucket."""
    Ms = mat("M_stone", (0.94, 0.90, 0.82), 0.62)
    Ms2 = mat("M_stone2", (0.88, 0.84, 0.76), 0.62)
    Mw = mat("M_wood", (0.80, 0.55, 0.32), 0.52)
    Mw2 = mat("M_wood2", (0.88, 0.64, 0.40), 0.52)
    Mbase = mat("M_base", (0.96, 0.92, 0.84), 0.65)
    Mrope = mat("M_rope", (0.92, 0.85, 0.70), 0.6)
    Mdark = mat("M_dark", (0.22, 0.26, 0.30), 0.75)

    r = root_empty("cozy_well_house_A")
    cyl("Pad", (0, 0, 0.03), 1.25, 0.07, Mbase, 24)
    # taller clearer stone cylinder (SSOT cream masonry ring)
    for ring, z in enumerate([0.12, 0.28, 0.44, 0.60]):
        n = 12
        for i in range(n):
            ang = TAU * i / n + (ring * 0.12)
            x, y = 0.52 * math.cos(ang), 0.52 * math.sin(ang)
            cube(f"Brick{ring}_{i}", (x, y, z), (0.24, 0.18, 0.16), Ms if (i + ring) % 2 == 0 else Ms2, 0.05)
    cyl("Coping", (0, 0, 0.72), 0.55, 0.10, Ms, 16)
    cyl("WellHole", (0, 0, 0.40), 0.34, 0.65, Mdark, 14)
    # A-frame structure: taller posts, cross, braces (form, not just roof tiles)
    cyl("PostL", (-0.62, 0, 1.05), 0.08, 1.55, Mw, 8)
    cyl("PostR", (0.62, 0, 1.05), 0.08, 1.55, Mw, 8)
    cube("CrossBeam", (0, 0, 1.55), (1.30, 0.12, 0.12), Mw, 0.03)
    cube("BraceL", (-0.35, 0, 1.35), (0.55, 0.08, 0.08), Mw2, 0.02)
    cube("BraceR", (0.35, 0, 1.35), (0.55, 0.08, 0.08), Mw2, 0.02)
    # roof plate under scales (gives solid form)
    for side, y in (("F", 0.28), ("B", -0.28)):
        cube(f"RoofPlate{side}", (0, y, 1.72), (1.15, 0.35, 0.06), Mw2, 0.02)
    roof_tiles_aframe("Sh", 1.55, 0.58, 0.42, 0.55, [Mw, Mw2, Mw], rows=5, cols=5)
    sph("RidgeCap", (0, 0, 2.15), 0.10, Mw2, (1.5, 0.8, 0.7))
    # winch + hanging bucket (readable silhouette)
    cyl("Drum", (0.62, 0, 1.55), 0.11, 0.22, Mw2, 10)
    cyl("Handle", (0.75, 0, 1.55), 0.03, 0.25, Mw, 6)
    cyl("Bucket", (0, 0, 0.95), 0.14, 0.20, Mw2, 10)
    cube("Bail", (0, 0, 1.15), (0.03, 0.03, 0.28), Mrope, 0.0)
    for i, (x, y) in enumerate([(-0.40, 0.90), (0.0, 1.0), (0.40, 0.90)]):
        sph(f"Path{i}", (x, y, 0.05), 0.13, Ms, (1.25, 1.0, 0.3), segs=8)
    parent_all(r)
    return r


def build_windmill():
    """V4 TARGET: blade/tier simplified — 3 clear tiers, sail blades with spars, hub plate."""
    Mc = mat("M_clay", (0.97, 0.93, 0.88), 0.6)
    Mr = mat("M_roof_a", (0.90, 0.48, 0.35), 0.55)
    Mw = mat("M_blade", (0.82, 0.58, 0.35), 0.48)
    Md = mat("M_door", (0.80, 0.52, 0.32), 0.5)
    Me = mat("M_emit", (1.0, 0.82, 0.40), 0.3, emit=3.2)
    Mbase = mat("M_base", (0.96, 0.92, 0.84), 0.65)
    Mpot = mat("M_pot", (0.85, 0.50, 0.32), 0.55)
    Mleaf = mat("M_leaf", (0.45, 0.75, 0.45), 0.55)
    Mlav = mat("M_lav", (0.70, 0.45, 0.85), 0.5)
    Mband = mat("M_band", (0.85, 0.52, 0.35), 0.55)
    Mhub = mat("M_hub", (0.78, 0.52, 0.30), 0.5)

    r = root_empty("cozy_windmill_A")
    cube("Pad", (0, 0, 0.04), (2.15, 2.15, 0.08), Mbase, 0.1)
    # 3 distinct tiers (SSOT bulb → mid → upper)
    sph("Tier0", (0, 0, 0.50), 1.00, Mc, (1.08, 1.08, 0.72), segs=18)
    cyl("Tier1", (0, 0, 1.15), 0.62, 0.85, Mc, 18)
    cyl("Tier2", (0, 0, 1.85), 0.52, 0.75, Mc, 18)
    cyl("Band0", (0, 0, 0.85), 0.72, 0.12, Mband, 18)
    cyl("Band1", (0, 0, 1.50), 0.65, 0.10, Mband, 18)
    cyl("Band2", (0, 0, 2.15), 0.55, 0.09, Mband, 18)
    sph("Roof", (0, 0, 2.45), 0.58, Mr, (1.15, 1.15, 0.72), segs=16)
    cyl("Chimney", (0.42, -0.30, 2.75), 0.11, 0.48, mat("M_chim", (0.96, 0.92, 0.88), 0.55), 8)
    sph("Smoke", (0.48, -0.24, 3.15), 0.12, mat("M_sm", (0.92, 0.85, 0.78), 0.8))
    cube("Door", (0, 0.92, 0.48), (0.40, 0.10, 0.62), Md, 0.05)
    sph("DoorArch", (0, 0.92, 0.85), 0.22, Md, (1.0, 0.4, 0.55), segs=10)
    sph("Knob", (0.12, 0.98, 0.48), 0.045, mat("M_gold", (0.95, 0.80, 0.30), 0.4, emit=0.6))
    for i, (x, y, z, sx, sz) in enumerate([
        (-0.55, 0.55, 0.55, 0.24, 0.28), (0.55, 0.55, 0.55, 0.24, 0.28),
        (0.0, 0.55, 1.25, 0.24, 0.30), (-0.42, 0.48, 1.25, 0.22, 0.26),
        (0.0, 0.50, 1.85, 0.22, 0.26),
    ]):
        cube(f"Win{i}", (x, y, z), (sx, 0.10, sz), Me, 0.03)
    # V4 blades: longer sails + cross spar + outer tip
    hub = (0.0, 0.72, 2.05)
    sph("Hub", hub, 0.18, Mhub)
    cyl("HubPlate", (hub[0], hub[1] + 0.02, hub[2]), 0.22, 0.08, Mhub, 12)
    for i in range(4):
        ang = math.radians(i * 90 + 18)
        # main sail
        bx = hub[0] + 0.70 * math.cos(ang)
        bz = hub[2] + 0.70 * math.sin(ang)
        o = cube(f"Blade{i}", (bx, hub[1] + 0.10, bz), (0.32, 0.07, 1.15), Mw, 0.04)
        o.rotation_euler = (0, -ang, 0)
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        o.select_set(False)
        # spar spine
        sx = hub[0] + 0.55 * math.cos(ang)
        sz = hub[2] + 0.55 * math.sin(ang)
        s = cube(f"Spar{i}", (sx, hub[1] + 0.14, sz), (0.08, 0.05, 0.95), mat(f"M_spar{i}", (0.70, 0.48, 0.28), 0.5), 0.02)
        s.rotation_euler = (0, -ang, 0)
        bpy.context.view_layer.objects.active = s
        s.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        s.select_set(False)
    for i, (x, y) in enumerate([(-0.95, 0.75), (0.95, 0.70), (-0.25, 1.0), (0.30, 1.0)]):
        cyl(f"Pot{i}", (x, y, 0.12), 0.09, 0.15, Mpot, 8)
        sph(f"Pl{i}", (x, y, 0.30), 0.10, Mleaf if i % 2 else Mlav)
    parent_all(r)
    return r


def build_barn():
    """SSOT bld_03 V2: plank barn, double doors, loft hay, tan fishscales, lantern."""
    Mw = mat("M_wood", (0.90, 0.74, 0.52), 0.55)
    Mw2 = mat("M_wood2", (0.78, 0.56, 0.36), 0.55)
    Md = mat("M_door", (0.70, 0.48, 0.28), 0.5)
    Mr1 = mat("M_roof_a", (0.92, 0.70, 0.48), 0.55)
    Mr2 = mat("M_roof_b", (0.85, 0.58, 0.38), 0.55)
    Mr3 = mat("M_roof_c", (0.96, 0.82, 0.62), 0.55)
    Mhay = mat("M_hay", (0.96, 0.84, 0.25), 0.6)
    Me = mat("M_emit", (1.0, 0.85, 0.45), 0.35, emit=3.0)
    Mbase = mat("M_base", (0.78, 0.70, 0.90), 0.65)
    Mmetal = mat("M_metal", (0.32, 0.32, 0.35), 0.4)

    r = root_empty("cozy_barn_small_A")
    cube("Base", (0, 0, 0.04), (2.4, 2.1, 0.08), Mbase, 0.1)
    cube("Body", (0, 0, 0.85), (1.95, 1.65, 1.55), Mw, 0.08)
    for i, x in enumerate([-0.75, -0.45, -0.15, 0.15, 0.45, 0.75]):
        cube(f"PlankF{i}", (x, 0.84, 0.85), (0.10, 0.05, 1.45), Mw2, 0.01)
        cube(f"PlankB{i}", (x, -0.84, 0.85), (0.10, 0.05, 1.45), Mw2, 0.01)
    # diagonal beams
    cube("Beam1", (-0.35, 0.86, 1.25), (0.90, 0.06, 0.08), Mw2, 0.02)
    cube("Beam2", (0.35, 0.86, 1.25), (0.90, 0.06, 0.08), Mw2, 0.02)
    cube("Gable", (0, 0, 1.85), (1.95, 0.55, 0.55), Mw, 0.06)
    # V3: sphere fishscales only — no plank Ridge cube
    roof_tiles_gable("Roof", 0, 0, 1.48, 1.18, 1.05, 0.82, [Mr1, Mr2, Mr3], rows=6, cols=7)
    cube("DoorL", (-0.28, 0.88, 0.55), (0.48, 0.10, 1.0), Md, 0.04)
    cube("DoorR", (0.28, 0.88, 0.55), (0.48, 0.10, 1.0), Md, 0.04)
    sph("Handle", (0.05, 0.95, 0.55), 0.05, Mmetal)
    # loft + hay
    cube("LoftFrame", (0, 0.88, 1.55), (0.65, 0.08, 0.45), Mw2, 0.02)
    for i, (ox, oy, oz) in enumerate([(0, 0.65, 1.48), (-0.12, 0.70, 1.55), (0.12, 0.68, 1.42)]):
        sph(f"HayLoft{i}", (ox, oy, oz), 0.14, Mhay, (1.3, 0.9, 0.85), segs=8)
    sph("HayGround1", (-0.90, 0.75, 0.18), 0.18, Mhay, (1.3, 1.1, 0.8), segs=8)
    sph("HayGround2", (0.65, 0.90, 0.16), 0.16, Mhay, (1.2, 1.0, 0.75), segs=8)
    cube("SideWin", (0.98, 0.0, 0.95), (0.08, 0.40, 0.32), mat("M_dark", (0.22, 0.20, 0.18), 0.7), 0.02)
    cyl("LanternArm", (0.55, 0.92, 0.90), 0.035, 0.18, Mmetal, 6)
    sph("Lantern", (0.55, 0.98, 0.72), 0.09, Me)
    parent_all(r)
    return r


def build_bridge():
    """V5: BOX voussoir arch — hard masonry blocks, not soft spheres."""
    Ms1 = mat("M_stone1", (0.90, 0.86, 0.88), 0.55)
    Ms2 = mat("M_stone2", (0.80, 0.76, 0.82), 0.55)
    Ms3 = mat("M_stone3", (0.94, 0.90, 0.92), 0.55)
    Mpk = mat("M_pink", (0.95, 0.55, 0.70), 0.5)
    Mpu = mat("M_pur", (0.70, 0.45, 0.90), 0.5)
    Mleaf = mat("M_leaf", (0.40, 0.75, 0.45), 0.55)

    r = root_empty("cozy_bridge_arch_A")
    mats = [Ms1, Ms2, Ms3]
    n_arch = 11
    for i in range(n_arch):
        t = i / (n_arch - 1)
        ang = math.pi * t
        x = 1.15 * math.cos(ang)
        z = 0.12 + 0.90 * math.sin(ang)
        o = cube(f"Voussoir{i}", (x, 0, z), (0.28, 0.55, 0.22), mats[i % 3], 0.04)
        o.rotation_euler = (0, 0, ang - math.pi * 0.5)
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        try:
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        except Exception:
            pass
        o.select_set(False)
    cube("Keystone", (0, 0, 1.02), (0.32, 0.58, 0.28), Ms3, 0.05)
    for side, x in (("L", -1.20), ("R", 1.20)):
        cube(f"Abut{side}", (x, 0, 0.30), (0.50, 0.75, 0.60), Ms2, 0.06)
        cube(f"AbutCap{side}", (x, 0, 0.65), (0.48, 0.72, 0.14), Ms1, 0.04)
    for i in range(6):
        t = (i + 0.5) / 6.0
        x = -0.95 + t * 1.9
        cube(f"Deck{i}", (x, 0, 0.92), (0.32, 0.70, 0.12), mats[i % 3], 0.03)
    for side, y in (("L", 0.40), ("R", -0.40)):
        for i, t in enumerate([0.2, 0.5, 0.8]):
            x = -0.85 + t * 1.7
            cube(f"Rail{side}{i}", (x, y, 1.05), (0.18, 0.12, 0.22), mats[i % 3], 0.03)
    for i, (x, y) in enumerate([(-1.3, 0.55), (1.3, -0.5)]):
        cyl(f"Stem{i}", (x, y, 0.08), 0.025, 0.18, Mleaf, 5)
        sph(f"Bloom{i}", (x, y, 0.20), 0.08, Mpk if i % 2 == 0 else Mpu, segs=8)
    parent_all(r)
    return r


def build_watchtower():
    """V5: BROWN thatch hue (not peach) + layered cone plates."""
    Mc = mat("M_clay", (0.96, 0.92, 0.86), 0.6)
    # true brown thatch SSOT range
    Mr1 = mat("M_thatch1", (0.55, 0.38, 0.20), 0.65)
    Mr2 = mat("M_thatch2", (0.48, 0.32, 0.16), 0.65)
    Mr3 = mat("M_thatch3", (0.62, 0.44, 0.24), 0.65)
    Mw = mat("M_wood", (0.62, 0.42, 0.24), 0.5)
    Me = mat("M_emit", (1.0, 0.85, 0.45), 0.35, emit=2.8)
    Mband = mat("M_band", (0.70, 0.50, 0.30), 0.55)

    r = root_empty("cozy_watchtower_A")
    cyl("TowerLo", (0, 0, 0.70), 0.55, 1.3, Mc, 14)
    cyl("TowerHi", (0, 0, 1.75), 0.48, 0.85, Mc, 14)
    cube("Cabin", (0, 0, 2.35), (0.95, 0.95, 0.70), Mc, 0.06)
    cyl("Band", (0, 0, 2.05), 0.58, 0.10, Mband, 14)
    # layered flat cones = thatch plates
    for i, (z, r1, r2, d) in enumerate([
        (2.55, 0.95, 0.75, 0.18),
        (2.72, 0.78, 0.55, 0.18),
        (2.90, 0.58, 0.35, 0.18),
        (3.08, 0.38, 0.15, 0.16),
        (3.22, 0.18, 0.02, 0.14),
    ]):
        cone(f"Thatch{i}", (0, 0, z), r1, r2, d, [Mr1, Mr2, Mr3][i % 3], 16)
    cyl("Finial", (0, 0, 3.38), 0.04, 0.22, Mw, 6)
    cyl("EaveRing", (0, 0, 2.48), 0.92, 0.08, Mband, 16)
    cube("OpenF", (0, 0.50, 2.35), (0.35, 0.08, 0.40), Me, 0.02)
    cube("OpenR", (0.50, 0, 2.35), (0.08, 0.35, 0.35), Me, 0.02)
    for i in range(7):
        z = 0.25 + i * 0.28
        cube(f"Rung{i}", (0, -0.58, z), (0.35, 0.06, 0.05), Mw, 0.02)
    cyl("RailL", (-0.18, -0.58, 1.15), 0.04, 2.0, Mw, 6)
    cyl("RailR", (0.18, -0.58, 1.15), 0.04, 2.0, Mw, 6)
    parent_all(r)
    return r


BUILDERS = {
    "cozy_workshop_A": build_workshop,
    "cozy_market_stall_A": build_market,
    "cozy_gazebo_A": build_gazebo,
    "cozy_well_house_A": build_well,
    "cozy_windmill_A": build_windmill,
    "cozy_barn_small_A": build_barn,
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
    dest.write_bytes(q.read_bytes())
    dig = sha(dest)
    size = dest.stat().st_size
    log(f"  wrote {dest.name} sha={dig[:16]} bytes={size}")
    return {"module_id": module_id, "glb_sha256": dig, "bytes": size, "source": JOB, "visual": f"mockup_{module_id}_v5", "mockup_ssot": module_id}


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
            by_id[mid] = entry
    data["accepted"] = False
    data["self_accept"] = False
    data["buildings_fidelity_v5"] = JOB
    CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"catalog modules={len(data['modules'])}")


def main():
    log("start BUILDINGS_FIDELITY_V5 continuous_iteration n=6")
    rows = []
    for mid in MODULES:
        rows.append(export_module(mid))
    update_catalog(rows)
    report = {
        "schema_version": "buildings_fidelity/1.0",
        "receipt_id": "BUILDINGS_FIDELITY_V5",
        "job": JOB,
        "work_order": "WO-TOWN-GRID-IMPORT-001",
        "authority": "PATCH_DRAFT",
        "human_authorization": "continuous_iteration_authorization 2026-07-24T12:30",
        "accepted": False,
        "self_accept": False,
        "purple": "WAITING",
        "matching_100_pct_count": 0,
        "matching_100_pct": [],
        "modules": rows,
        "approaches": {
            "cozy_market_stall_A": "front_apron_oversized_produce",
            "cozy_gazebo_A": "v4_density_kept_plus_v5_run",
            "cozy_well_house_A": "v4_form_kept_plus_v5_run",
            "cozy_windmill_A": "v4_sails_kept_plus_v5_run",
            "cozy_bridge_arch_A": "box_voussoir_masonry",
            "cozy_watchtower_A": "brown_thatch_cone_layers",
        },
        "home_bld": "UNTOUCHED_CLOSED_PERMANENTLY",
        "note": "GLBs rewritten; fidelity score after headed QA — not auto-claimed 100%.",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    (QUAR / "BUILDINGS_FIDELITY_V5_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    log(f"DONE count={len(rows)} receipt={RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

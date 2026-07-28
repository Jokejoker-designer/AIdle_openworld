# -*- coding: utf-8 -*-
"""BUILDINGS_FIDELITY_V3 — true sloped/sphere fishscale roofs (kill shelf-plank signature).

Targets (plot keeps existing transform in town_grid_plan_v1.json):
  cozy_workshop_A, cozy_market_stall_A, cozy_gazebo_A, cozy_well_house_A,
  cozy_windmill_A, cozy_barn_small_A, cozy_bridge_arch_A, cozy_watchtower_A

Does NOT touch HOME.BLD / GREENHOUSE.BLD / plan positions.
accepted=false, self_accept=false.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy

TAU = math.tau
JOB = "BUILDINGS_FIDELITY_V3"
GAME_DIR = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules")
CAT = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
QUAR.mkdir(parents=True, exist_ok=True)

MODULES = [
    "cozy_workshop_A",
    "cozy_market_stall_A",
    "cozy_gazebo_A",
    "cozy_well_house_A",
    "cozy_windmill_A",
    "cozy_barn_small_A",
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
    """SSOT bld_05 V2: bold pink/cream awning, wood counter, saturated fruit crates."""
    Mw = mat("M_wood", (0.70, 0.45, 0.28), 0.55)
    Mw2 = mat("M_wood2", (0.82, 0.58, 0.36), 0.55)
    Mpink = mat("M_awn_pink", (0.96, 0.62, 0.75), 0.48)
    Mcream = mat("M_awn_cream", (0.99, 0.95, 0.88), 0.48)
    Mred = mat("M_apple", (0.92, 0.22, 0.22), 0.4)
    Myel = mat("M_lemon", (0.96, 0.90, 0.18), 0.4)
    Mor = mat("M_fruit_o", (0.98, 0.52, 0.12), 0.4)
    Mreg = mat("M_reg", (0.55, 0.85, 0.68), 0.42)
    Mbase = mat("M_base", (0.78, 0.70, 0.90), 0.65)
    Mstone = mat("M_stone", (0.78, 0.74, 0.70), 0.65)
    Mpot = mat("M_pot", (0.85, 0.50, 0.32), 0.55)
    Mleaf = mat("M_leaf", (0.35, 0.72, 0.40), 0.55)
    Mgold = mat("M_gold", (0.95, 0.80, 0.30), 0.4, emit=0.5)

    r = root_empty("cozy_market_stall_A")
    cube("Base", (0, 0, 0.04), (2.4, 2.0, 0.08), Mbase, 0.1)
    for i, z in enumerate([0.22, 0.48, 0.72]):
        cube(f"Body{i}", (0, 0.05, z), (1.90, 1.20, 0.24), Mw if i % 2 == 0 else Mw2, 0.05)
    for x, y in [(-0.88, 0.50), (0.88, 0.50), (-0.88, -0.48), (0.88, -0.48)]:
        cyl(f"Post_{x}_{y}", (x, y, 1.20), 0.07, 1.2, Mw, 8)
    # curved-looking awning: taller pink/cream stripes
    for i in range(7):
        t = i / 6.0
        x = -1.05 + t * 2.1
        m = Mpink if i % 2 == 0 else Mcream
        cube(f"Awn{i}", (x, 0.10, 1.62), (0.30, 1.45, 0.16), m, 0.06)
    cube("AwnValance", (0, 0.82, 1.42), (2.15, 0.28, 0.16), Mpink, 0.06)
    # fruit crates — larger fruit
    for i, (x, fruit_m, nfr) in enumerate([(-0.55, Mred, 6), (0.0, Myel, 5), (0.55, Mor, 7)]):
        cube(f"Crate{i}", (x, 0.10, 0.98), (0.45, 0.42, 0.24), Mw2, 0.03)
        for j in range(nfr):
            fx = x + ((j % 3) - 1) * 0.13
            fy = 0.10 + ((j // 3) - 0.5) * 0.13
            sph(f"Fruit{i}_{j}", (fx, fy, 1.18), 0.10, fruit_m, segs=10)
    cube("RegBase", (0.18, 0.55, 0.98), (0.30, 0.24, 0.14), Mreg, 0.03)
    cube("RegTop", (0.18, 0.55, 1.12), (0.24, 0.18, 0.16), Mreg, 0.02)
    sph("RegKnob", (0.26, 0.62, 1.08), 0.035, Mgold)
    for i, (x, y) in enumerate([(-0.35, 1.0), (0.05, 1.12), (0.40, 1.0), (-0.55, 1.20)]):
        sph(f"Stone{i}", (x, y, 0.06), 0.13, Mstone, (1.3, 1.0, 0.35), segs=8)
    cyl("PotL", (-1.05, 0.90, 0.12), 0.09, 0.15, Mpot, 8)
    sph("PlantL", (-1.05, 0.90, 0.30), 0.11, Mleaf)
    cyl("PotR", (1.0, 0.92, 0.12), 0.08, 0.13, Mpot, 8)
    sph("PlantR", (1.0, 0.92, 0.26), 0.09, mat("M_flower", (0.88, 0.42, 0.88), 0.5))
    parent_all(r)
    return r


def build_gazebo():
    """SSOT bld_10: round open gazebo, green fishscale roof, warm floor, pots."""
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
    cyl("BasePad", (0, 0, 0.04), 1.35, 0.08, Mbase, 24)
    # floor
    cyl("Floor", (0, 0, 0.18), 1.05, 0.10, Mf, 20)
    # warm glow under roof
    sph("Glow", (0, 0, 0.95), 0.55, Me, (1.0, 1.0, 0.4))
    # 6 posts
    for i in range(6):
        ang = TAU * i / 6.0
        x, y = 0.85 * math.cos(ang), 0.85 * math.sin(ang)
        cyl(f"Post{i}", (x, y, 0.75), 0.07, 1.15, Mw, 8)
    # rail ring
    for i in range(12):
        ang = TAU * i / 12.0
        x, y = 0.90 * math.cos(ang), 0.90 * math.sin(ang)
        cube(f"Rail{i}", (x, y, 0.55), (0.18, 0.08, 0.06), Mw, 0.02)
    # green fishscale roof — concentric rings of half-spheres / flattened cubes
    for ring, (rad, z, n, sc) in enumerate([
        (0.25, 1.75, 1, 0.35),
        (0.55, 1.55, 8, 0.22),
        (0.85, 1.40, 12, 0.20),
        (1.10, 1.25, 14, 0.18),
    ]):
        mats = [Mg1, Mg2, Mg3]
        if n == 1:
            sph("RoofCap", (0, 0, z), sc, Mg3, (1.2, 1.2, 0.55))
            continue
        for i in range(n):
            ang = TAU * i / n
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            sph(f"Tile{ring}_{i}", (x, y, z), sc, mats[i % 3], (1.3, 1.0, 0.55), segs=8)
    # pots around
    for i in range(6):
        ang = TAU * i / 6.0 + 0.3
        x, y = 1.15 * math.cos(ang), 1.15 * math.sin(ang)
        cyl(f"Pot{i}", (x, y, 0.12), 0.08, 0.14, Mpot, 8)
        sph(f"Pl{i}", (x, y, 0.28), 0.10, Mleaf if i % 2 == 0 else Mlav)
    for i, (x, y) in enumerate([(0.2, 1.35), (-0.15, 1.45), (0.4, 1.50)]):
        sph(f"Path{i}", (x, y, 0.05), 0.10, Mstone, (1.2, 0.9, 0.3), segs=8)
    parent_all(r)
    return r


def build_well():
    """SSOT bld_07: stone well, wood A-frame roof, bucket, winch."""
    Ms = mat("M_stone", (0.92, 0.88, 0.80), 0.65)
    Ms2 = mat("M_stone2", (0.88, 0.84, 0.76), 0.65)
    Mw = mat("M_wood", (0.78, 0.55, 0.32), 0.55)
    Mw2 = mat("M_wood2", (0.85, 0.62, 0.40), 0.55)
    Mbase = mat("M_base", (0.96, 0.92, 0.84), 0.65)
    Mrope = mat("M_rope", (0.92, 0.85, 0.70), 0.6)

    r = root_empty("cozy_well_house_A")
    cyl("Pad", (0, 0, 0.03), 1.2, 0.06, Mbase, 20)
    # stone well cylinder as stacked rings of cubes
    for ring, z in enumerate([0.15, 0.35, 0.55]):
        for i in range(10):
            ang = TAU * i / 10.0 + (ring * 0.15)
            x, y = 0.48 * math.cos(ang), 0.48 * math.sin(ang)
            cube(f"Brick{ring}_{i}", (x, y, z), (0.22, 0.16, 0.18), Ms if (i + ring) % 2 == 0 else Ms2, 0.04)
    # inner dark
    cyl("WellHole", (0, 0, 0.35), 0.32, 0.55, mat("M_dark", (0.25, 0.28, 0.32), 0.8), 12)
    # posts + crossbeam
    cyl("PostL", (-0.55, 0, 0.95), 0.07, 1.3, Mw, 8)
    cyl("PostR", (0.55, 0, 0.95), 0.07, 1.3, Mw, 8)
    cyl("Cross", (0, 0, 1.45), 0.05, 1.15, Mw, 8)
    # rotate cross to X axis via scale cube instead
    cube("CrossBeam", (0, 0, 1.45), (1.15, 0.10, 0.10), Mw, 0.02)
    # winch drum
    cyl("Drum", (0.55, 0, 1.45), 0.10, 0.18, Mw2, 10)
    # bucket
    cyl("Bucket", (0, 0, 0.85), 0.12, 0.18, Mw2, 10)
    cube("BucketBail", (0, 0, 1.05), (0.02, 0.02, 0.25), Mrope, 0.0)
    # V3 A-frame sphere shingles (not shelf cubes)
    roof_tiles_aframe("Sh", 1.50, 0.55, 0.40, 0.50, [Mw, Mw2, Mw], rows=4, cols=5)
    # eaves cylinders
    cyl("EaveL", (-0.65, 0, 1.55), 0.06, 0.9, Mw, 8)
    cyl("EaveR", (0.65, 0, 1.55), 0.06, 0.9, Mw, 8)
    for i, (x, y) in enumerate([(-0.35, 0.85), (0.0, 0.95), (0.35, 0.85)]):
        sph(f"Path{i}", (x, y, 0.05), 0.12, Ms, (1.2, 1.0, 0.3), segs=8)
    parent_all(r)
    return r


def build_windmill():
    """SSOT bld_06 V2: two-tier cream tower, terracotta dome, thick blades, glow windows."""
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

    r = root_empty("cozy_windmill_A")
    cube("Pad", (0, 0, 0.04), (2.1, 2.1, 0.08), Mbase, 0.1)
    sph("BaseBulb", (0, 0, 0.55), 0.95, Mc, (1.05, 1.05, 0.78), segs=18)
    cyl("Mid", (0, 0, 1.40), 0.58, 1.1, Mc, 18)
    cyl("Band1", (0, 0, 0.95), 0.68, 0.12, Mband, 18)
    cyl("Band2", (0, 0, 1.85), 0.62, 0.10, Mband, 18)
    sph("Roof", (0, 0, 2.25), 0.62, Mr, (1.1, 1.1, 0.78), segs=16)
    cyl("Chimney", (0.40, -0.28, 2.55), 0.11, 0.45, mat("M_chim", (0.96, 0.92, 0.88), 0.55), 8)
    sph("Smoke", (0.45, -0.22, 2.95), 0.11, mat("M_sm", (0.92, 0.85, 0.78), 0.8))
    # arched door
    cube("Door", (0, 0.85, 0.48), (0.38, 0.10, 0.60), Md, 0.05)
    sph("DoorArch", (0, 0.85, 0.82), 0.20, Md, (1.0, 0.4, 0.55), segs=10)
    sph("Knob", (0.12, 0.92, 0.48), 0.045, mat("M_gold", (0.95, 0.80, 0.30), 0.4, emit=0.6))
    for i, (x, y, z, sx, sz) in enumerate([
        (-0.50, 0.55, 0.55, 0.22, 0.26), (0.50, 0.55, 0.55, 0.22, 0.26),
        (0.0, 0.58, 1.50, 0.22, 0.28), (-0.40, 0.48, 1.50, 0.20, 0.24),
    ]):
        cube(f"Win{i}", (x, y, z), (sx, 0.10, sz), Me, 0.03)
    # thick blades on +Y
    hub = (0.0, 0.68, 1.95)
    sph("Hub", hub, 0.16, mat("M_hub", (0.78, 0.52, 0.30), 0.5))
    for i in range(4):
        ang = math.radians(i * 90 + 20)
        bx = hub[0] + 0.62 * math.cos(ang)
        bz = hub[2] + 0.62 * math.sin(ang)
        o = cube(f"Blade{i}", (bx, hub[1] + 0.08, bz), (0.28, 0.08, 0.95), Mw, 0.04)
        o.rotation_euler = (0, -ang, 0)
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        o.select_set(False)
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
    """SSOT bld_09 V2: clear cobble arch with open underside + rail stones + flowers."""
    Ms1 = mat("M_stone1", (0.90, 0.86, 0.88), 0.58)
    Ms2 = mat("M_stone2", (0.82, 0.78, 0.84), 0.58)
    Ms3 = mat("M_stone3", (0.94, 0.90, 0.92), 0.58)
    Mpk = mat("M_pink", (0.95, 0.55, 0.70), 0.5)
    Mpu = mat("M_pur", (0.70, 0.45, 0.90), 0.5)
    Mleaf = mat("M_leaf", (0.40, 0.75, 0.45), 0.55)

    r = root_empty("cozy_bridge_arch_A")
    mats = [Ms1, Ms2, Ms3]
    # clear arch ring (leave hollow under)
    for i in range(11):
        t = i / 10.0
        ang = math.pi * t
        x = 1.05 * math.cos(ang)
        z = 0.12 + 0.75 * math.sin(ang)
        for yoff in (-0.22, 0.0, 0.22):
            sph(f"Arch{i}_{yoff}", (x, yoff, z), 0.20, mats[(i + int(yoff * 10)) % 3], (1.05, 0.85, 0.85), segs=10)
    # deck across top of arch
    for i in range(6):
        t = (i + 0.5) / 6.0
        x = -0.85 + t * 1.7
        z = 0.72 + 0.08 * math.sin(t * math.pi)
        sph(f"Deck{i}", (x, 0, z), 0.20, mats[i % 3], (1.15, 0.95, 0.50), segs=10)
    # side rail piles
    for side, y in (("L", 0.42), ("R", -0.42)):
        for i in range(6):
            t = i / 5.0
            x = -0.95 + t * 1.9
            z = 0.55 + 0.30 * math.sin(t * math.pi)
            sph(f"Rail{side}{i}", (x, y, z), 0.17, mats[(i + 2) % 3], (0.95, 0.75, 0.70), segs=8)
    for i, (x, y) in enumerate([(-1.2, 0.55), (-1.15, -0.5), (1.15, 0.45), (1.2, -0.55), (0.0, 0.60)]):
        cyl(f"Stem{i}", (x, y, 0.08), 0.025, 0.18, Mleaf, 5)
        sph(f"Bloom{i}", (x, y, 0.20), 0.08, Mpk if i % 2 == 0 else Mpu, segs=8)
    parent_all(r)
    return r


def build_watchtower():
    """SSOT bld_08: tall cream tower, brown conical shingle roof, ladder, glow openings."""
    Mc = mat("M_clay", (0.96, 0.92, 0.86), 0.6)
    Mr1 = mat("M_roof_a", (0.78, 0.52, 0.32), 0.55)
    Mr2 = mat("M_roof_b", (0.70, 0.45, 0.28), 0.55)
    Mr3 = mat("M_roof_c", (0.85, 0.58, 0.38), 0.55)
    Mw = mat("M_wood", (0.72, 0.50, 0.30), 0.5)
    Me = mat("M_emit", (1.0, 0.85, 0.45), 0.35, emit=2.8)
    Mband = mat("M_band", (0.85, 0.62, 0.42), 0.55)

    r = root_empty("cozy_watchtower_A")
    # tapering tower (stacked cylinders)
    cyl("TowerLo", (0, 0, 0.70), 0.55, 1.3, Mc, 14)
    cyl("TowerHi", (0, 0, 1.75), 0.48, 0.85, Mc, 14)
    # lookout cabin
    cube("Cabin", (0, 0, 2.35), (0.95, 0.95, 0.70), Mc, 0.06)
    cyl("Band", (0, 0, 2.05), 0.58, 0.10, Mband, 14)
    # roof cone as stacked rings
    for ring, (rad, z, n) in enumerate([
        (0.15, 3.05, 1),
        (0.35, 2.90, 6),
        (0.55, 2.75, 8),
        (0.72, 2.60, 10),
    ]):
        mats = [Mr1, Mr2, Mr3]
        if n == 1:
            sph("RoofCap", (0, 0, z), 0.18, Mr3, (1.0, 1.0, 0.7))
            continue
        for i in range(n):
            ang = TAU * i / n
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            sph(f"Sh{ring}_{i}", (x, y, z), 0.16, mats[i % 3], (1.2, 1.0, 0.5), segs=8)
    # glow openings
    cube("OpenF", (0, 0.50, 2.35), (0.35, 0.08, 0.40), Me, 0.02)
    cube("OpenR", (0.50, 0, 2.35), (0.08, 0.35, 0.35), Me, 0.02)
    # ladder on -Y
    for i in range(7):
        z = 0.25 + i * 0.28
        cube(f"Rung{i}", (0, -0.58, z), (0.35, 0.06, 0.05), Mw, 0.02)
    cyl("RailL", (-0.18, -0.58, 1.15), 0.04, 2.0, Mw, 6)
    cyl("RailR", (0.18, -0.58, 1.15), 0.04, 2.0, Mw, 6)
    # smoke / dust pixels optional
    sph("Dust1", (0.15, 0.1, 3.25), 0.06, mat("M_dust", (0.85, 0.72, 0.55), 0.8))
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
    return {"module_id": module_id, "glb_sha256": dig, "bytes": size, "source": JOB, "visual": f"mockup_{module_id}_v3", "mockup_ssot": module_id}


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
    data["buildings_fidelity_v3"] = JOB
    CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"catalog modules={len(data['modules'])}")


def main():
    log("start BUILDINGS_FIDELITY_V3")
    rows = []
    for mid in MODULES:
        rows.append(export_module(mid))
    update_catalog(rows)
    report = QUAR / "BUILDINGS_FIDELITY_V3_report.json"
    report.write_text(json.dumps({"job": JOB, "modules": rows, "accepted": False, "self_accept": False}, indent=2), encoding="utf-8")
    log(f"DONE count={len(rows)} report={report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

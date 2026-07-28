# -*- coding: utf-8 -*-
"""BUILDINGS_WAVE1_V1 — author 8 missing town building GLBs from MOCKUP_SSOT_V2 cards.

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
JOB = "BUILDINGS_WAVE1_V1"
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


def roof_tiles_gable(prefix, cx, cy, base_z, half_w, half_d, peak_h, mats, rows=4, cols=5):
    """Soft clay shingle rows on both gable slopes (no rotation — stepped boxes)."""
    for side, sy in (("F", 0.55), ("B", -0.55)):
        for row in range(rows):
            t = (row + 0.5) / rows
            z = base_z + t * peak_h
            y = cy + sy * half_d * (1.0 - t * 0.85)
            for col in range(cols):
                u = (col + 0.5) / cols
                x = cx + (u - 0.5) * half_w * 2.0 * 0.92
                m = mats[row % len(mats)]
                cube(f"{prefix}_{side}_{row}_{col}", (x, y, z), (half_w * 0.38, half_d * 0.22, 0.07), m, 0.04)


# ───────────────────────── builders ─────────────────────────


def build_workshop():
    """SSOT bld_04: cream clay cottage, terracotta roof, workbench, tools on wall, plants."""
    Mc = mat("M_clay", (0.96, 0.90, 0.82), 0.62)
    Md = mat("M_door", (0.78, 0.52, 0.32), 0.5)
    Mr1 = mat("M_roof_a", (0.92, 0.55, 0.42), 0.55)
    Mr2 = mat("M_roof_b", (0.88, 0.48, 0.36), 0.55)
    Mr3 = mat("M_roof_c", (0.95, 0.62, 0.48), 0.55)
    Mw = mat("M_wood", (0.72, 0.50, 0.32), 0.55)
    Me = mat("M_emit", (1.0, 0.85, 0.45), 0.35, emit=2.8)
    Mmetal = mat("M_metal", (0.55, 0.58, 0.62), 0.35)
    Mleaf = mat("M_leaf", (0.35, 0.72, 0.40), 0.55)
    Mpot = mat("M_pot", (0.85, 0.50, 0.32), 0.55)
    Myarn1 = mat("M_yarn1", (0.95, 0.45, 0.70), 0.5)
    Myarn2 = mat("M_yarn2", (0.45, 0.85, 0.55), 0.5)
    Myarn3 = mat("M_yarn3", (0.55, 0.55, 0.95), 0.5)
    Mbase = mat("M_base", (0.82, 0.75, 0.92), 0.65)

    r = root_empty("cozy_workshop_A")
    cube("Base", (0, 0, 0.04), (2.4, 2.2, 0.08), Mbase, 0.08)
    # body
    cube("Body", (0, 0, 0.75), (1.9, 1.7, 1.4), Mc, 0.08)
    # gable peak block
    cube("Gable", (0, 0, 1.55), (1.9, 0.55, 0.55), Mc, 0.06)
    roof_tiles_gable("Roof", 0, 0, 1.35, 1.1, 1.0, 0.75, [Mr1, Mr2, Mr3], rows=4, cols=5)
    cube("Ridge", (0, 0, 2.05), (2.0, 0.18, 0.14), Mr2, 0.05)
    # chimney
    cyl("Chimney", (0.55, -0.35, 2.15), 0.12, 0.45, mat("M_chim", (0.95, 0.92, 0.88), 0.55), 10)
    sph("Smoke1", (0.55, -0.35, 2.55), 0.12, mat("M_smoke", (0.95, 0.95, 0.97), 0.8), (1.2, 1.2, 0.8))
    sph("Smoke2", (0.70, -0.25, 2.75), 0.10, mat("M_smoke2", (0.95, 0.95, 0.97), 0.8))
    # big work window (front -Y for freecam convention optional; face +Y for visibility)
    cube("WinFrame", (0, 0.88, 0.85), (0.95, 0.08, 0.70), Mw, 0.03)
    cube("WinGlow", (0, 0.90, 0.85), (0.82, 0.04, 0.58), Me, 0.0)
    # interior yarn balls visible in window
    sph("Yarn1", (-0.2, 0.70, 0.85), 0.10, Myarn1)
    sph("Yarn2", (0.05, 0.68, 0.80), 0.09, Myarn2)
    sph("Yarn3", (0.22, 0.72, 0.90), 0.08, Myarn3)
    # small upper window
    cube("WinTopF", (0, 0.88, 1.55), (0.28, 0.06, 0.28), Me, 0.02)
    # workbench left-front
    cube("BenchTop", (-0.95, 0.55, 0.45), (0.85, 0.45, 0.08), Mw, 0.03)
    cube("BenchLeg1", (-1.25, 0.40, 0.22), (0.08, 0.08, 0.40), Mw, 0.02)
    cube("BenchLeg2", (-0.65, 0.40, 0.22), (0.08, 0.08, 0.40), Mw, 0.02)
    cube("BenchLeg3", (-1.25, 0.70, 0.22), (0.08, 0.08, 0.40), Mw, 0.02)
    cube("BenchLeg4", (-0.65, 0.70, 0.22), (0.08, 0.08, 0.40), Mw, 0.02)
    # vise / tools on bench
    cube("Vise", (-1.15, 0.55, 0.55), (0.18, 0.12, 0.12), Mmetal, 0.02)
    for i, x in enumerate([-0.95, -0.85, -0.75, -0.65]):
        cyl(f"Rod{i}", (x, 0.55, 0.52), 0.02, 0.35, Mw, 6)
    # tools hanging on wall (+X)
    for i, (y, z) in enumerate([(0.3, 0.9), (0.0, 0.95), (-0.25, 0.9), (-0.45, 0.95)]):
        cube(f"Tool{i}", (0.98, y, z), (0.06, 0.08, 0.28), Mmetal if i % 2 == 0 else Mw, 0.01)
        cyl(f"ToolH{i}", (0.98, y, z - 0.18), 0.03, 0.12, Mw, 6)
    # pots
    for i, (x, y) in enumerate([(-1.1, -0.7), (0.6, 0.95), (0.9, 0.7), (0.9, 0.4), (0.55, 0.95)]):
        cyl(f"Pot{i}", (x, y, 0.12), 0.08, 0.14, Mpot, 8)
        sph(f"Plant{i}", (x, y, 0.28), 0.10, Mleaf)
    cube("Crate", (-0.4, 0.95, 0.12), (0.28, 0.22, 0.16), Mw, 0.02)
    parent_all(r)
    return r


def build_market():
    """SSOT bld_05: wood stall, pink/cream striped awning, fruit crates, register."""
    Mw = mat("M_wood", (0.72, 0.48, 0.30), 0.55)
    Mw2 = mat("M_wood2", (0.80, 0.58, 0.38), 0.55)
    Mpink = mat("M_awn_pink", (0.95, 0.70, 0.78), 0.5)
    Mcream = mat("M_awn_cream", (0.98, 0.94, 0.86), 0.5)
    Mred = mat("M_apple", (0.92, 0.28, 0.28), 0.45)
    Myel = mat("M_lemon", (0.95, 0.88, 0.25), 0.45)
    Mor = mat("M_orange", (0.98, 0.58, 0.18), 0.45)
    Mreg = mat("M_reg", (0.65, 0.85, 0.70), 0.45)
    Mbase = mat("M_base", (0.82, 0.75, 0.92), 0.65)
    Mstone = mat("M_stone", (0.78, 0.74, 0.70), 0.65)
    Mpot = mat("M_pot", (0.85, 0.50, 0.32), 0.55)
    Mleaf = mat("M_leaf", (0.35, 0.72, 0.40), 0.55)
    Mgold = mat("M_gold", (0.95, 0.80, 0.30), 0.4, emit=0.4)

    r = root_empty("cozy_market_stall_A")
    cube("Base", (0, 0, 0.04), (2.3, 1.9, 0.08), Mbase, 0.08)
    # counter body (3 layers of planks)
    for i, z in enumerate([0.25, 0.50, 0.72]):
        cube(f"Body{i}", (0, 0, z), (1.85, 1.15, 0.22), Mw if i % 2 == 0 else Mw2, 0.04)
    # posts
    for x, y in [(-0.85, 0.45), (0.85, 0.45), (-0.85, -0.45), (0.85, -0.45)]:
        cyl(f"Post_{x}_{y}", (x, y, 1.15), 0.06, 1.1, Mw, 8)
    # awning stripes (front-sloping soft slabs)
    for i in range(6):
        t = i / 5.0
        x = -0.95 + t * 1.9
        m = Mpink if i % 2 == 0 else Mcream
        cube(f"Awn{i}", (x, 0.15, 1.55 + (0.5 - abs(t - 0.5)) * 0.15), (0.32, 1.35, 0.12), m, 0.05)
    cube("AwnFront", (0, 0.75, 1.45), (2.05, 0.25, 0.14), Mpink, 0.05)
    # crates + fruit
    for i, (x, fruit_m, nfr) in enumerate([
        (-0.55, Mred, 5), (0.0, Myel, 4), (0.55, Mor, 6)
    ]):
        cube(f"Crate{i}", (x, 0.15, 0.95), (0.42, 0.40, 0.22), Mw2, 0.02)
        for j in range(nfr):
            fx = x + ((j % 3) - 1) * 0.12
            fy = 0.15 + ((j // 3) - 0.5) * 0.12
            sph(f"Fruit{i}_{j}", (fx, fy, 1.12), 0.08, fruit_m, segs=10)
    # register
    cube("RegBase", (0.15, 0.55, 0.95), (0.28, 0.22, 0.12), Mreg, 0.03)
    cube("RegTop", (0.15, 0.55, 1.08), (0.22, 0.16, 0.14), Mreg, 0.02)
    sph("RegKnob", (0.22, 0.62, 1.05), 0.03, Mgold)
    # path stones
    for i, (x, y) in enumerate([(-0.3, 0.95), (0.1, 1.05), (0.4, 0.95), (-0.5, 1.15)]):
        sph(f"Stone{i}", (x, y, 0.06), 0.12, Mstone, (1.3, 1.0, 0.35), segs=8)
    # pots
    cyl("PotL", (-1.0, 0.85, 0.12), 0.08, 0.14, Mpot, 8)
    sph("PlantL", (-1.0, 0.85, 0.28), 0.10, Mleaf)
    cyl("PotR", (0.95, 0.90, 0.12), 0.07, 0.12, Mpot, 8)
    sph("PlantR", (0.95, 0.90, 0.25), 0.08, mat("M_flower", (0.85, 0.45, 0.85), 0.5))
    parent_all(r)
    return r


def build_gazebo():
    """SSOT bld_10: round open gazebo, green fishscale roof, warm floor, pots."""
    Mw = mat("M_wood", (0.78, 0.55, 0.35), 0.55)
    Mf = mat("M_floor", (0.92, 0.78, 0.55), 0.5)
    Mg1 = mat("M_roof_g1", (0.45, 0.78, 0.48), 0.55)
    Mg2 = mat("M_roof_g2", (0.38, 0.70, 0.42), 0.55)
    Mg3 = mat("M_roof_g3", (0.55, 0.85, 0.55), 0.55)
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
    # roof A-frame shingles
    for row in range(4):
        t = (row + 0.5) / 4
        z = 1.55 + t * 0.45
        for side, sy in (("F", 0.35), ("B", -0.35)):
            y = sy * (1.0 - t * 0.7)
            for col in range(4):
                x = -0.55 + (col + 0.5) / 4 * 1.1
                cube(f"Sh{side}{row}{col}", (x, y, z), (0.28, 0.22, 0.07), Mw if row % 2 == 0 else Mw2, 0.03)
    cube("Ridge", (0, 0, 2.05), (1.2, 0.12, 0.10), Mw2, 0.03)
    # eaves cylinders
    cyl("EaveL", (-0.65, 0, 1.55), 0.06, 0.9, Mw, 8)
    cyl("EaveR", (0.65, 0, 1.55), 0.06, 0.9, Mw, 8)
    for i, (x, y) in enumerate([(-0.35, 0.85), (0.0, 0.95), (0.35, 0.85)]):
        sph(f"Path{i}", (x, y, 0.05), 0.12, Ms, (1.2, 1.0, 0.3), segs=8)
    parent_all(r)
    return r


def build_windmill():
    """SSOT bld_06: round cream tower, terracotta cap, 4 blades, chimney, glow windows."""
    Mc = mat("M_clay", (0.96, 0.92, 0.86), 0.6)
    Mr = mat("M_roof", (0.88, 0.52, 0.40), 0.55)
    Mw = mat("M_wood", (0.78, 0.55, 0.32), 0.5)
    Md = mat("M_door", (0.80, 0.55, 0.35), 0.5)
    Me = mat("M_emit", (1.0, 0.82, 0.40), 0.35, emit=2.6)
    Mbase = mat("M_base", (0.96, 0.92, 0.84), 0.65)
    Mpot = mat("M_pot", (0.85, 0.50, 0.32), 0.55)
    Mleaf = mat("M_leaf", (0.45, 0.75, 0.45), 0.55)
    Mlav = mat("M_lav", (0.70, 0.45, 0.85), 0.5)
    Mband = mat("M_band", (0.82, 0.55, 0.38), 0.55)

    r = root_empty("cozy_windmill_A")
    cube("Pad", (0, 0, 0.04), (2.0, 2.0, 0.08), Mbase, 0.08)
    # base bulb
    sph("BaseBulb", (0, 0, 0.55), 0.85, Mc, (1.0, 1.0, 0.75), segs=16)
    cyl("Mid", (0, 0, 1.35), 0.55, 1.0, Mc, 16)
    # bands
    cyl("Band1", (0, 0, 0.95), 0.62, 0.10, Mband, 16)
    cyl("Band2", (0, 0, 1.75), 0.58, 0.08, Mband, 16)
    # roof dome
    sph("Roof", (0, 0, 2.15), 0.55, Mr, (1.05, 1.05, 0.75), segs=14)
    # chimney
    cyl("Chimney", (0.35, -0.25, 2.45), 0.10, 0.40, mat("M_chim", (0.95, 0.90, 0.85), 0.55), 8)
    sph("Smoke", (0.40, -0.20, 2.80), 0.10, mat("M_sm", (0.92, 0.85, 0.78), 0.8))
    # door
    cube("Door", (0, 0.78, 0.45), (0.35, 0.08, 0.55), Md, 0.04)
    sph("Knob", (0.10, 0.84, 0.45), 0.04, mat("M_gold", (0.95, 0.80, 0.30), 0.4, emit=0.5))
    # windows glow
    for i, (x, y, z) in enumerate([
        (-0.45, 0.45, 0.55), (0.45, 0.45, 0.55), (0, 0.55, 1.45), (-0.35, 0.40, 1.45)
    ]):
        cube(f"Win{i}", (x, y, z), (0.18, 0.08, 0.22), Me, 0.02)
    # blades (4) on +Y face of upper tower
    hub = (0, 0.62, 1.85)
    sph("Hub", hub, 0.12, Mw)
    for i in range(4):
        ang = math.radians(i * 90 + 25)
        # blade as long flattened cube offset from hub
        bx = hub[0] + 0.55 * math.cos(ang)
        bz = hub[2] + 0.55 * math.sin(ang)
        o = cube(f"Blade{i}", (bx, hub[1] + 0.05, bz), (0.18, 0.06, 0.75), Mw, 0.03)
        o.rotation_euler = (0, -ang, 0)
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        o.select_set(False)
    # pots
    for i, (x, y) in enumerate([(-0.85, 0.7), (0.85, 0.65), (-0.2, 0.95), (0.25, 0.95)]):
        cyl(f"Pot{i}", (x, y, 0.12), 0.08, 0.14, Mpot, 8)
        sph(f"Pl{i}", (x, y, 0.28), 0.09, Mleaf if i % 2 else Mlav)
    parent_all(r)
    return r


def build_barn():
    """SSOT bld_03: wood barn, plank walls, loft hay, shingle roof, lantern."""
    Mw = mat("M_wood", (0.88, 0.72, 0.50), 0.55)
    Mw2 = mat("M_wood2", (0.78, 0.58, 0.38), 0.55)
    Md = mat("M_door", (0.72, 0.50, 0.30), 0.5)
    Mr1 = mat("M_roof_a", (0.90, 0.72, 0.55), 0.55)
    Mr2 = mat("M_roof_b", (0.82, 0.60, 0.42), 0.55)
    Mr3 = mat("M_roof_c", (0.95, 0.80, 0.65), 0.55)
    Mhay = mat("M_hay", (0.95, 0.85, 0.30), 0.65)
    Me = mat("M_emit", (1.0, 0.85, 0.45), 0.35, emit=2.5)
    Mbase = mat("M_base", (0.82, 0.75, 0.92), 0.65)
    Mmetal = mat("M_metal", (0.35, 0.35, 0.38), 0.4)

    r = root_empty("cozy_barn_small_A")
    cube("Base", (0, 0, 0.04), (2.3, 2.0, 0.08), Mbase, 0.08)
    # body planks
    cube("Body", (0, 0, 0.85), (1.9, 1.6, 1.55), Mw, 0.06)
    # vertical plank hints
    for i, x in enumerate([-0.7, -0.35, 0.0, 0.35, 0.7]):
        cube(f"Plank{i}", (x, 0.82, 0.85), (0.08, 0.04, 1.45), Mw2, 0.01)
    # gable
    cube("Gable", (0, 0, 1.85), (1.9, 0.5, 0.55), Mw, 0.05)
    roof_tiles_gable("Roof", 0, 0, 1.55, 1.1, 0.95, 0.7, [Mr1, Mr2, Mr3], rows=4, cols=5)
    cube("Ridge", (0, 0, 2.25), (2.0, 0.16, 0.12), Mr2, 0.04)
    # big door
    cube("DoorL", (-0.22, 0.85, 0.55), (0.40, 0.08, 0.95), Md, 0.03)
    cube("DoorR", (0.22, 0.85, 0.55), (0.40, 0.08, 0.95), Md, 0.03)
    # loft opening + hay
    cube("Loft", (0, 0.85, 1.55), (0.55, 0.08, 0.40), Mw2, 0.02)
    sph("Hay1", (0, 0.70, 1.50), 0.18, Mhay, (1.4, 0.8, 0.9), segs=8)
    sph("Hay2", (-0.85, 0.70, 0.15), 0.15, Mhay, (1.2, 1.0, 0.7), segs=8)
    sph("Hay3", (0.55, 0.85, 0.15), 0.14, Mhay, (1.1, 1.0, 0.7), segs=8)
    # side window
    cube("SideWin", (0.98, 0, 0.90), (0.06, 0.35, 0.28), mat("M_dark", (0.25, 0.22, 0.20), 0.7), 0.02)
    # lantern
    cyl("LanternArm", (0.55, 0.90, 0.85), 0.03, 0.15, Mmetal, 6)
    sph("Lantern", (0.55, 0.95, 0.70), 0.08, Me)
    parent_all(r)
    return r


def build_bridge():
    """SSOT bld_09: soft stone arch bridge of rounded cobbles + flowers."""
    Ms1 = mat("M_stone1", (0.88, 0.84, 0.86), 0.6)
    Ms2 = mat("M_stone2", (0.82, 0.78, 0.84), 0.6)
    Ms3 = mat("M_stone3", (0.92, 0.88, 0.90), 0.6)
    Mpk = mat("M_pink", (0.95, 0.55, 0.70), 0.5)
    Mpu = mat("M_pur", (0.70, 0.45, 0.90), 0.5)
    Mleaf = mat("M_leaf", (0.40, 0.75, 0.45), 0.55)

    r = root_empty("cozy_bridge_arch_A")
    # arch as stacked rounded stones along a semicircle
    mats = [Ms1, Ms2, Ms3]
    # deck top stones
    for i in range(7):
        t = i / 6.0
        x = -1.0 + t * 2.0
        z = 0.55 + 0.15 * math.sin(t * math.pi)
        sph(f"Deck{i}", (x, 0, z), 0.22, mats[i % 3], (1.1, 0.85, 0.55), segs=10)
    # arch ring under
    for i in range(9):
        t = i / 8.0
        ang = math.pi * t
        x = -0.85 * math.cos(ang)
        z = 0.15 + 0.55 * math.sin(ang)
        sph(f"Arch{i}", (x, 0, z), 0.20, mats[i % 3], (1.0, 0.9, 0.75), segs=10)
    # side rails / shoulders
    for side, y in (("L", 0.35), ("R", -0.35)):
        for i in range(5):
            t = i / 4.0
            x = -0.9 + t * 1.8
            z = 0.45 + 0.25 * math.sin(t * math.pi)
            sph(f"Rail{side}{i}", (x, y, z), 0.16, mats[(i + 1) % 3], (0.9, 0.7, 0.65), segs=8)
    # flowers
    for i, (x, y) in enumerate([(-1.1, 0.5), (-1.0, -0.45), (1.05, 0.4), (1.1, -0.5), (0.0, 0.55)]):
        cyl(f"Stem{i}", (x, y, 0.08), 0.02, 0.16, Mleaf, 5)
        sph(f"Bloom{i}", (x, y, 0.18), 0.07, Mpk if i % 2 == 0 else Mpu, segs=8)
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
    return {"module_id": module_id, "glb_sha256": dig, "bytes": size, "source": JOB, "visual": f"mockup_{module_id}_v1", "mockup_ssot": module_id}


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
    data["buildings_wave1"] = JOB
    CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"catalog modules={len(data['modules'])}")


def main():
    log("start BUILDINGS_WAVE1_V1")
    rows = []
    for mid in MODULES:
        rows.append(export_module(mid))
    update_catalog(rows)
    report = QUAR / "BUILDINGS_WAVE1_V1_report.json"
    report.write_text(json.dumps({"job": JOB, "modules": rows, "accepted": False, "self_accept": False}, indent=2), encoding="utf-8")
    log(f"DONE count={len(rows)} report={report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

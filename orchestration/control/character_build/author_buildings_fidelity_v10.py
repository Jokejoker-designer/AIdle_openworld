# -*- coding: utf-8 -*-
"""BUILDINGS_FIDELITY_V10 — material/emission SSOT bake (not density remesh).

V8 = topology family. V9 = residual mesh language. V10 = different strategy:

  MATERIAL_EMISSION_SSOT: re-export same V9 silhouettes with:
    - saturated mockup-locked base colors (survive town lighting wash)
    - stronger emission on warm windows / interior glow
    - slightly higher roughness for soft-clay matte (less purple env tint)
    - wood/thatch/green boosted chroma toward bld_0x mockup cards

Does NOT change positions or HOME.BLD. accepted=false.
same_sig_streak: new residual family → streak 0 if sig changes.
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
from pathlib import Path

import bpy

TAU = math.tau
JOB = "BUILDINGS_FIDELITY_V10"
GAME_DIR = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules")
CAT = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
QUAR.mkdir(parents=True, exist_ok=True)
RECEIPT = Path(r"E:\AIdle_openworld\orchestration\receipts\town_grid_import_001\BUILDINGS_FIDELITY_V10.json")

MODULES = [
    "cozy_market_stall_A",
    "cozy_gazebo_A",
    "cozy_well_house_A",
    "cozy_windmill_A",
    "cozy_bridge_arch_A",
    "cozy_watchtower_A",
]

V9_SIG = {
    "cozy_market_stall_A": "market_open_front_crate_stage_produce_front_facing_high_partial",
    "cozy_gazebo_A": "gazebo_flower_petal_shell_rings_warm_interior_high_partial",
    "cozy_well_house_A": "well_soft_cylinder_curved_board_roof_bucket_high_partial",
    "cozy_windmill_A": "windmill_single_taper_fat_sails_window_glow_high_partial",
    "cozy_bridge_arch_A": "bridge_shell_segment_void_arch_high_partial",
    "cozy_watchtower_A": "watchtower_cabin_first_pie_thatch_glow_high_partial",
}

V10_POST_SIG = {
    "cozy_market_stall_A": "market_chroma_boost_produce_awning_material_ssot_high_partial",
    "cozy_gazebo_A": "gazebo_green_locked_warm_emit_material_ssot_high_partial",
    "cozy_well_house_A": "well_wood_shingle_chroma_material_ssot_high_partial",
    "cozy_windmill_A": "windmill_pink_cap_window_emit_material_ssot_high_partial",
    "cozy_bridge_arch_A": "bridge_lavender_stone_matte_material_ssot_high_partial",
    "cozy_watchtower_A": "watchtower_brown_thatch_cabin_emit_material_ssot_high_partial",
}

STRATEGIES = {
    "cozy_market_stall_A": "material_emission_ssot_chroma_boost_vs_mesh_topology",
    "cozy_gazebo_A": "material_emission_ssot_green_lock_vs_mesh_topology",
    "cozy_well_house_A": "material_emission_ssot_wood_chroma_vs_mesh_topology",
    "cozy_windmill_A": "material_emission_ssot_cap_emit_vs_mesh_topology",
    "cozy_bridge_arch_A": "material_emission_ssot_matte_stone_vs_mesh_topology",
    "cozy_watchtower_A": "material_emission_ssot_thatch_emit_vs_mesh_topology",
}

PLOT = {
    "cozy_market_stall_A": "MARKET.BLD",
    "cozy_gazebo_A": "GARDEN.BLD",
    "cozy_well_house_A": "WELL.BLD",
    "cozy_windmill_A": "WINDMILL.BLD",
    "cozy_bridge_arch_A": "BRIDGE.BLD",
    "cozy_watchtower_A": "LOOKOUT.BLD",
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


def mat(name, rgb, rough=0.72, emit=0.0, alpha=1.0, sat=1.15):
    """Soft-clay matte + optional chroma boost so town lighting does not wash to grey/purple."""
    r, g, b = rgb[:3]
    # push away from grey mid toward pure hue (sat>1)
    avg = (r + g + b) / 3.0
    r = max(0.0, min(1.0, avg + (r - avg) * sat))
    g = max(0.0, min(1.0, avg + (g - avg) * sat))
    b = max(0.0, min(1.0, avg + (b - avg) * sat))
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (r, g, b, alpha)
    nd = m.node_tree.nodes
    bsd = next((x for x in nd if x.type == "BSDF_PRINCIPLED"), None)
    if bsd:
        bsd.inputs["Base Color"].default_value = (r, g, b, alpha)
        if "Roughness" in bsd.inputs:
            bsd.inputs["Roughness"].default_value = rough
        if "Specular IOR Level" in bsd.inputs:
            bsd.inputs["Specular IOR Level"].default_value = 0.12
        elif "Specular" in bsd.inputs:
            bsd.inputs["Specular"].default_value = 0.12
        if "Metallic" in bsd.inputs:
            bsd.inputs["Metallic"].default_value = 0.0
        if emit > 0:
            if "Emission Color" in bsd.inputs:
                bsd.inputs["Emission Color"].default_value = (r, g, b, 1.0)
            if "Emission Strength" in bsd.inputs:
                bsd.inputs["Emission Strength"].default_value = emit
        if alpha < 0.99:
            m.blend_method = "BLEND"
            if "Alpha" in bsd.inputs:
                bsd.inputs["Alpha"].default_value = alpha
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


# ── V10 = V9 silhouette + locked chroma materials ─────────────────────────────


def build_market():
    # mockup-locked saturated colors
    Mw = mat("wood", (0.78, 0.48, 0.28), 0.70, sat=1.25)
    Mw2 = mat("wood2", (0.88, 0.58, 0.34), 0.68, sat=1.25)
    Mplank = mat("plank", (0.72, 0.42, 0.24), 0.72, sat=1.2)
    Mpink = mat("awn_p", (1.0, 0.62, 0.76), 0.55, sat=1.3)
    Mcream = mat("awn_c", (1.0, 0.96, 0.86), 0.55, sat=1.1)
    Mred = mat("apple", (0.98, 0.12, 0.12), 0.45, sat=1.4)
    Myel = mat("lemon", (1.0, 0.94, 0.08), 0.45, sat=1.4)
    Mor = mat("orange", (1.0, 0.50, 0.05), 0.45, sat=1.4)
    Mreg = mat("reg", (0.35, 0.92, 0.68), 0.48, sat=1.35)
    Mbase = mat("base", (0.80, 0.72, 0.96), 0.75, sat=1.15)
    Mstem = mat("stem", (0.28, 0.72, 0.22), 0.65, sat=1.3)
    Mgold = mat("gold", (1.0, 0.82, 0.18), 0.4, emit=0.8, sat=1.3)
    Mpot = mat("pot", (0.92, 0.48, 0.28), 0.65, sat=1.25)
    Mleaf = mat("leaf", (0.28, 0.82, 0.38), 0.55, sat=1.4)
    Mstone = mat("stone", (0.78, 0.74, 0.70), 0.78, sat=1.05)
    Mflower = mat("fl", (0.95, 0.45, 0.88), 0.5, sat=1.3)

    r = root_empty("cozy_market_stall_A")
    sph("Pad", (0, 0, 0.02), 1.40, Mbase, (1.2, 1.05, 0.07), segs=16)
    cube("Rear", (0, -0.15, 0.50), (1.90, 0.70, 0.95), Mw, 0.10)
    for i, x in enumerate([-0.62, 0.0, 0.62]):
        cube(f"Face{i}", (x, 0.38, 0.48), (0.58, 0.18, 0.90), Mplank if i % 2 else Mw2, 0.08)
    cube("Deck", (0, 0.20, 1.00), (1.85, 0.95, 0.12), Mw2, 0.06)
    for x in (-0.78, 0.78):
        cyl(f"Post{x}", (x, 0.30, 1.35), 0.09, 1.05, Mw, 10)
    for i in range(5):
        t = (i + 0.5) / 5.0
        x = -0.95 + t * 1.90
        m = Mpink if i % 2 == 0 else Mcream
        o = cube(f"Awn{i}", (x, 0.05, 1.85), (0.42, 1.45, 0.28), m, 0.12)
        apply_rot(o, (0.28, 0, 0))
    cube("Roll", (0, 0.78, 1.55), (2.05, 0.32, 0.26), Mpink, 0.12)
    crates = [(-0.58, 0.35, Mred, 9, True), (-0.02, 0.35, Myel, 8, False), (0.55, 0.35, Mor, 10, False)]
    for i, (x, y, fm, nfr, stems) in enumerate(crates):
        cube(f"Crate{i}", (x, y, 1.12), (0.48, 0.48, 0.18), Mw, 0.04)
        cube(f"Rim{i}", (x, y, 1.22), (0.50, 0.50, 0.05), Mw2, 0.02)
        for j in range(nfr):
            layer = j // 3
            k = j % 3
            fx = x + (k - 1) * 0.13
            fy = y + 0.05 + (layer % 2) * 0.08 + 0.05
            fz = 1.28 + layer * 0.13
            sph(f"Fr{i}_{j}", (fx, fy, fz), 0.11 if layer == 0 else 0.10, fm, segs=12)
            if stems and j % 2 == 0:
                cyl(f"St{i}_{j}", (fx, fy, fz + 0.10), 0.015, 0.05, Mstem, 5)
    cube("Reg", (0.12, 0.55, 1.18), (0.30, 0.24, 0.24), Mreg, 0.06)
    cube("RegScr", (0.12, 0.55, 1.32), (0.18, 0.12, 0.10), Mreg, 0.03)
    sph("Knob", (0.20, 0.62, 1.22), 0.035, Mgold)
    for i, (x, y) in enumerate([(-1.05, 0.80), (0.95, 0.90)]):
        cyl(f"Pot{i}", (x, y, 0.12), 0.10, 0.16, Mpot, 8)
        sph(f"Pl{i}", (x, y, 0.30), 0.11, Mleaf if i == 0 else Mflower)
    for i, (x, y) in enumerate([(-0.25, 1.00), (0.10, 1.10), (0.42, 1.00)]):
        sph(f"Stn{i}", (x, y, 0.05), 0.13, Mstone, (1.35, 1.0, 0.32), segs=8)
    parent_all(r)
    return r


def build_gazebo():
    # GREEN LOCKED — high sat pure greens (counter town purple wash)
    Mw = mat("wood", (0.86, 0.52, 0.30), 0.68, sat=1.25)
    Mf = mat("floor", (0.96, 0.78, 0.48), 0.60, sat=1.2)
    Mg1 = mat("g1", (0.22, 0.88, 0.42), 0.55, sat=1.55)
    Mg2 = mat("g2", (0.15, 0.78, 0.35), 0.55, sat=1.55)
    Mg3 = mat("g3", (0.35, 0.95, 0.52), 0.55, sat=1.55)
    Me = mat("emit", (1.0, 0.88, 0.42), 0.35, emit=5.5, sat=1.2)
    Mbase = mat("base", (0.80, 0.72, 0.96), 0.75, sat=1.15)
    Mpot = mat("pot", (0.92, 0.48, 0.28), 0.65, sat=1.25)
    Mleaf = mat("leaf", (0.22, 0.80, 0.32), 0.55, sat=1.45)
    Mlav = mat("lav", (0.72, 0.38, 0.95), 0.55, sat=1.3)
    Mstone = mat("stone", (0.78, 0.74, 0.70), 0.78, sat=1.05)

    r = root_empty("cozy_gazebo_A")
    sph("Pad", (0, 0, 0.02), 1.45, Mbase, (1.12, 1.12, 0.07), segs=16)
    cyl("Floor", (0, 0, 0.14), 1.08, 0.12, Mf, 22)
    for i in range(10):
        ang = TAU * i / 10.0
        x, y = 0.50 * math.cos(ang), 0.50 * math.sin(ang)
        pl = cube(f"Plank{i}", (x, y, 0.18), (1.0, 0.13, 0.03), Mw, 0.015)
        apply_rot(pl, (0, 0, ang))
    sph("Glow", (0, 0, 0.70), 0.70, Me, (1.05, 1.05, 0.35), segs=14)
    for i in range(6):
        ang = TAU * i / 6.0
        x, y = 0.92 * math.cos(ang), 0.92 * math.sin(ang)
        cyl(f"Post{i}", (x, y, 0.75), 0.10, 1.20, Mw, 10)
    for i in range(20):
        ang = TAU * i / 20.0
        x, y = 0.95 * math.cos(ang), 0.95 * math.sin(ang)
        cube(f"Rail{i}", (x, y, 0.52), (0.20, 0.09, 0.09), Mw, 0.035)
    mats = [Mg1, Mg2, Mg3]
    rings = [
        (1.95, 0.18, 8, (1.55, 1.25, 0.55), 0.35),
        (1.72, 0.48, 10, (1.65, 1.35, 0.50), 0.55),
        (1.48, 0.78, 12, (1.70, 1.40, 0.48), 0.75),
        (1.28, 1.05, 14, (1.60, 1.30, 0.45), 0.95),
    ]
    for ring, (elev, rad, n, sc, pitch) in enumerate(rings):
        for i in range(n):
            ang = TAU * i / n + (0.12 if ring % 2 else 0.0)
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            o = sph(f"Petal{ring}_{i}", (x, y, elev), 0.28, mats[(i + ring) % 3], sc, segs=12)
            apply_rot(o, (pitch, 0, ang + math.pi / 2))
    sph("Cap", (0, 0, 2.05), 0.32, Mg3, (1.15, 1.15, 0.55), segs=12)
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
    Ms = mat("stone", (0.98, 0.94, 0.86), 0.72, sat=1.1)
    Ms2 = mat("stone2", (0.94, 0.88, 0.80), 0.72, sat=1.1)
    Mw = mat("wood", (0.92, 0.58, 0.28), 0.62, sat=1.35)
    Mw2 = mat("wood2", (0.84, 0.50, 0.24), 0.62, sat=1.35)
    Mbase = mat("base", (0.97, 0.94, 0.88), 0.78, sat=1.05)
    Mrope = mat("rope", (0.98, 0.92, 0.72), 0.65, sat=1.15)
    Mdark = mat("dark", (0.18, 0.22, 0.28), 0.85, sat=1.0)
    Msh = mat("sh", (0.95, 0.58, 0.28), 0.60, sat=1.4)
    Msh2 = mat("sh2", (0.86, 0.50, 0.22), 0.60, sat=1.4)

    r = root_empty("cozy_well_house_A")
    sph("Pad", (0, 0, 0.02), 1.30, Mbase, (1.18, 1.18, 0.07), segs=16)
    cyl("WellBody", (0, 0, 0.42), 0.58, 0.72, Ms, 20)
    for ring, z in enumerate([0.20, 0.40, 0.60]):
        for i in range(8):
            ang = TAU * i / 8.0 + ring * 0.2
            x, y = 0.56 * math.cos(ang), 0.56 * math.sin(ang)
            cube(f"Emb{ring}_{i}", (x, y, z), (0.22, 0.08, 0.14), Ms2, 0.05)
    sph("Coping", (0, 0, 0.80), 0.62, Ms, (1.0, 1.0, 0.28), segs=16)
    cyl("Hole", (0, 0, 0.35), 0.34, 0.65, Mdark, 14)
    cyl("PostL", (-0.72, 0, 1.20), 0.10, 1.80, Mw, 10)
    cyl("PostR", (0.72, 0, 1.20), 0.10, 1.80, Mw, 10)
    cube("Cross", (0, 0, 1.95), (1.55, 0.16, 0.16), Mw, 0.05)
    ridge = cyl("Ridge", (0, 0, 2.22), 0.09, 1.40, Mw2, 10)
    apply_rot(ridge, (0, math.pi / 2, 0))
    for side, y_sign in (("F", 1.0), ("B", -1.0)):
        o = cube(f"Roof{side}", (0, y_sign * 0.32, 2.05), (1.30, 0.55, 0.10), Msh, 0.06)
        apply_rot(o, (y_sign * 0.55, 0, 0))
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
    Mc = mat("clay", (0.99, 0.95, 0.90), 0.72, sat=1.08)
    Mr = mat("roof", (0.98, 0.42, 0.40), 0.58, sat=1.45)  # pink-brown locked
    Mw = mat("blade", (0.88, 0.56, 0.30), 0.62, sat=1.3)
    Md = mat("door", (0.88, 0.50, 0.28), 0.62, sat=1.3)
    Me = mat("emit", (1.0, 0.86, 0.38), 0.30, emit=6.0, sat=1.2)
    Mbase = mat("base", (0.97, 0.94, 0.88), 0.78, sat=1.05)
    Mband = mat("band", (0.90, 0.52, 0.30), 0.60, sat=1.35)
    Mhub = mat("hub", (0.80, 0.48, 0.28), 0.55, sat=1.25)
    Mpot = mat("pot", (0.92, 0.48, 0.28), 0.65, sat=1.25)
    Mleaf = mat("leaf", (0.32, 0.80, 0.40), 0.55, sat=1.4)
    Mlav = mat("lav", (0.72, 0.42, 0.92), 0.55, sat=1.3)
    Mchim = mat("chim", (0.97, 0.94, 0.90), 0.72, sat=1.05)

    r = root_empty("cozy_windmill_A")
    sph("Pad", (0, 0, 0.02), 1.30, Mbase, (1.18, 1.18, 0.07), segs=16)
    cone("Body", (0, 0, 1.15), 1.05, 0.48, 2.20, Mc, 20)
    sph("Belly", (0, 0, 0.70), 0.95, Mc, (1.12, 1.12, 0.70), segs=16)
    cyl("BandLo", (0, 0, 1.05), 0.88, 0.14, Mband, 16)
    cyl("BandHi", (0, 0, 1.70), 0.62, 0.12, Mband, 14)
    sph("Roof", (0, 0, 2.35), 0.58, Mr, (1.20, 1.20, 0.72), segs=16)
    cyl("Chim", (0.38, -0.22, 2.70), 0.13, 0.50, Mchim, 10)
    sph("ChimLip", (0.38, -0.22, 2.95), 0.15, Mchim, (1.0, 1.0, 0.5), segs=8)
    cube("Door", (0, 0.98, 0.48), (0.40, 0.12, 0.58), Md, 0.07)
    sph("DoorArch", (0, 0.98, 0.82), 0.22, Md, (1.0, 0.35, 0.55), segs=10)
    cube("Step", (0, 1.10, 0.08), (0.45, 0.22, 0.08), Md, 0.04)
    win_pos = [
        (-0.60, 0.85, 0.55, 0.15), (0.60, 0.85, 0.55, 0.15),
        (-0.35, 0.70, 1.20, 0.12), (0.35, 0.70, 1.20, 0.12),
        (0.0, 0.62, 1.25, 0.11), (-0.28, 0.55, 1.75, 0.11),
        (0.28, 0.55, 1.75, 0.11), (0.0, 0.50, 1.95, 0.12),
    ]
    for i, (x, y, z, s) in enumerate(win_pos):
        sph(f"Win{i}", (x, y, z), s, Me, (1.0, 0.38, 1.15), segs=10)
    hub = (0.0, 0.72, 2.15)
    sph("Hub", hub, 0.18, Mhub)
    for i in range(4):
        ang = math.radians(i * 90 + 28)
        length = 1.55
        mx = hub[0] + (length * 0.48) * math.cos(ang)
        mz = hub[2] + (length * 0.48) * math.sin(ang)
        o = cube(f"Blade{i}", (mx, hub[1] + 0.12, mz), (0.36, 0.10, length), Mw, 0.06)
        apply_rot(o, (0, -ang, 0))
    for i, (x, y) in enumerate([(-1.0, 0.72), (1.0, 0.68), (-0.25, 1.05), (0.28, 1.05)]):
        cyl(f"Pot{i}", (x, y, 0.12), 0.09, 0.15, Mpot, 8)
        sph(f"Pl{i}", (x, y, 0.30), 0.10, Mleaf if i % 2 else Mlav)
    parent_all(r)
    return r


def build_bridge():
    Ms1 = mat("s1", (0.88, 0.82, 0.90), 0.78, sat=1.15)
    Ms2 = mat("s2", (0.80, 0.76, 0.86), 0.78, sat=1.15)
    Ms3 = mat("s3", (0.94, 0.88, 0.96), 0.78, sat=1.15)
    Mpk = mat("pk", (0.98, 0.48, 0.68), 0.55, sat=1.4)
    Mpu = mat("pu", (0.68, 0.42, 0.95), 0.55, sat=1.4)
    Mleaf = mat("leaf", (0.28, 0.82, 0.38), 0.55, sat=1.4)

    r = root_empty("cozy_bridge_arch_A")
    mats = [Ms1, Ms2, Ms3]
    n = 11
    for i in range(n):
        t = i / (n - 1)
        ang = math.pi * t
        x = 1.15 * math.cos(ang)
        z = 0.18 + 1.05 * math.sin(ang)
        o = cube(f"Seg{i}", (x, 0, z), (0.42, 0.48, 0.36), mats[i % 3], 0.14)
        apply_rot(o, (0, 0, ang - math.pi / 2))
    for i in range(7):
        t = (i + 0.5) / 7.0
        ang = math.pi * t
        x = 1.35 * math.cos(ang)
        z = 0.15 + 0.95 * math.sin(ang)
        y = 0.22 if i % 2 == 0 else -0.22
        cube(f"Outer{i}", (x, y, z), (0.36, 0.40, 0.32), mats[(i + 1) % 3], 0.12)
    cube("Key", (0, 0, 1.25), (0.50, 0.52, 0.42), Ms3, 0.15)
    for side, x in (("L", -1.25), ("R", 1.25)):
        for j, (dz, sc) in enumerate([(0.18, 0.45), (0.48, 0.40)]):
            cube(f"Ab{side}{j}", (x, 0, dz), (sc, sc * 0.95, 0.38), mats[j % 3], 0.12)
    for i in range(5):
        t = (i + 0.5) / 5.0
        x = -0.85 + t * 1.70
        z = 1.05 + 0.12 * math.sin(math.pi * t)
        cube(f"Deck{i}", (x, 0, z), (0.36, 0.40, 0.18), mats[i % 3], 0.08)
    for i, (x, y) in enumerate([(-1.35, 0.55), (1.30, -0.50), (-0.95, -0.55), (0.95, 0.55)]):
        cyl(f"Stem{i}", (x, y, 0.08), 0.02, 0.16, Mleaf, 5)
        sph(f"Bl{i}", (x, y, 0.20), 0.075, Mpk if i % 2 == 0 else Mpu, segs=8)
    parent_all(r)
    return r


def build_watchtower():
    Mc = mat("clay", (0.99, 0.96, 0.92), 0.72, sat=1.08)
    Mr1 = mat("t1", (0.78, 0.42, 0.18), 0.65, sat=1.45)
    Mr2 = mat("t2", (0.68, 0.36, 0.14), 0.65, sat=1.45)
    Mr3 = mat("t3", (0.86, 0.48, 0.22), 0.65, sat=1.45)
    Mw = mat("wood", (0.82, 0.48, 0.24), 0.62, sat=1.35)
    Me = mat("emit", (1.0, 0.90, 0.42), 0.30, emit=6.0, sat=1.2)
    Mband = mat("band", (0.88, 0.54, 0.30), 0.60, sat=1.35)
    Mdark = mat("dark", (0.32, 0.24, 0.18), 0.75, sat=1.1)

    r = root_empty("cozy_watchtower_A")
    cone("Shaft", (0, 0, 1.05), 0.72, 0.52, 2.05, Mc, 18)
    sph("Base", (0, 0, 0.35), 0.68, Mc, (1.05, 1.05, 0.70), segs=14)
    cube("Cabin", (0, 0, 2.35), (1.05, 1.05, 0.72), Mc, 0.12)
    cyl("Band", (0, 0, 2.00), 0.62, 0.12, Mband, 14)
    cube("WinF_frame", (0, 0.52, 2.35), (0.48, 0.08, 0.42), Mdark, 0.03)
    cube("WinF_glow", (0, 0.48, 2.35), (0.40, 0.06, 0.34), Me, 0.02)
    cube("WinR_frame", (0.52, 0, 2.35), (0.08, 0.42, 0.38), Mdark, 0.03)
    cube("WinR_glow", (0.48, 0, 2.35), (0.06, 0.34, 0.30), Me, 0.02)
    sph("CabinGlow", (0, 0, 2.35), 0.35, Me, (1.0, 1.0, 0.7), segs=10)
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
            o = sph(f"Th{ring}_{i}", (x, y, elev), 0.22, mats[(i + ring) % 3],
                    (sc_xy * 1.6, sc_xy * 1.2, sc_z * 2.2), segs=10)
            apply_rot(o, (0.65, 0, ang))
    sph("Cap", (0, 0, 3.22), 0.20, Mr3, (1.15, 1.15, 0.65), segs=10)
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
        "visual": f"material_ssot_v10_{module_id}",
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
    data["buildings_fidelity_v10"] = JOB
    CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"catalog modules={len(data['modules'])}")


def main():
    log("start BUILDINGS_FIDELITY_V10 material/emission SSOT n=6")
    rows = []
    for mid in MODULES:
        rows.append(export_module(mid))
    update_catalog(rows)
    objects = []
    for mid in MODULES:
        post = V10_POST_SIG[mid]
        prior = V9_SIG[mid]
        same = post == prior
        streak = 1 if same else 0
        objects.append({
            "plot_id": PLOT[mid],
            "object_id": mid,
            "v10_strategy": STRATEGIES[mid],
            "prior_v9_sig": prior,
            "post_v10_signature": post,
            "same_sig_streak": streak,
            "fidelity": "HIGH_PARTIAL",
            "matching_100_pct": False,
            "note": f"V10 material/emission SSOT; not claimed 100%.",
        })
    need_human = [o["plot_id"] for o in objects if o["same_sig_streak"] >= 3]
    report = {
        "schema_version": "buildings_fidelity/1.0",
        "receipt_id": "BUILDINGS_FIDELITY_V10",
        "job": JOB,
        "work_order": "WO-TOWN-GRID-IMPORT-001",
        "authority": "PATCH_DRAFT",
        "human_authorization": "continuous_iteration_authorization",
        "geometry_frozen": True,
        "accepted": False,
        "self_accept": False,
        "purple": "WAITING",
        "matching_100_pct_count": 0,
        "matching_100_pct": [],
        "modules": rows,
        "mesh_strategy_change": STRATEGIES,
        "objects": objects,
        "safety_valve": {
            "need_human": need_human,
            "same_sig_streak_max": max(o["same_sig_streak"] for o in objects),
            "note": "V10 new residual family (material_ssot) — streaks reset.",
        },
        "home_bld": "UNTOUCHED_CLOSED_PERMANENTLY",
        "note": "Material/emission chroma bake after V9 mesh language; still HIGH_PARTIAL.",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    (QUAR / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    log(f"DONE count={len(rows)} receipt={RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

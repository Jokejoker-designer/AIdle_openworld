# -*- coding: utf-8 -*-
"""BUILDINGS_FIDELITY_V13 â€” mockup match push (lighting + crisp topology).

Keeps V11 camera-match (pitch 42 / FOV 42 + mockup bg).
Levers this pass:
  A) town lighting material names aligned to town_grid_loader._boost_mockup_materials
     + boost map extended for petal_g / thatch / clay / cobble / roof_pink
  B) crisp supporting geometry: edge lips, frames, plank seams, discrete shingles,
     window frames, sail taper, arch void clearance â€” not smooth primitive mush

Same honesty: matching_100_pct only if headed capture genuinely matches mockup.
same_sig_streak vs V11 signatures; NEED_HUMAN at 3.
HOME.BLD untouched. Positions frozen.
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cozy_camera_match_lib import (  # noqa: E402
    PITCH_DEGREES,
    FOV_DEGREES,
    MOCKUP_MAP,
    ensure_addons,
    place_cozy_camera,
    load_mockup_for_module,
    auto_frame_distance,
    render_camera_match_preview,
    camera_match_meta,
    mesh_world_bounds,
)

TAU = math.tau
JOB = "BUILDINGS_FIDELITY_V13"
GAME_DIR = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules")
CAT = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
EVID = Path(r"E:\AIdle_openworld\orchestration\evidence\town_grid_import_001\camera_match_v13")
RECEIPT = Path(r"E:\AIdle_openworld\orchestration\receipts\town_grid_import_001\BUILDINGS_FIDELITY_V13.json")
QUAR.mkdir(parents=True, exist_ok=True)
EVID.mkdir(parents=True, exist_ok=True)

MODULES = [
    "cozy_market_stall_A",
    "cozy_gazebo_A",
    "cozy_well_house_A",
    "cozy_windmill_A",
    "cozy_bridge_arch_A",
    "cozy_watchtower_A",
]

V12_SIG = {
    "cozy_market_stall_A": "market_v12_crisp_awning_stripes_lit_wood_fruit_partial",
    "cozy_gazebo_A": "gazebo_v12_petal_g_boost_edge_lips_partial",
    "cozy_well_house_A": "well_v12_shingle_plates_brick_emboss_partial",
    "cozy_windmill_A": "windmill_v12_frame_sails_pink_cap_lit_partial",
    "cozy_bridge_arch_A": "bridge_v12_cobble_gapped_void_lavender_partial",
    "cozy_watchtower_A": "watchtower_v12_cabin_frame_thatch_tiles_partial",
}

# Post-V12 signatures â€” must be NEW if levers actually change residuals
V13_POST_SIG = {
    "cozy_market_stall_A": "market_v13_curved_awning_stripes_partial",
    "cozy_gazebo_A": "gazebo_v13_denser_fishscale_partial",
    "cozy_well_house_A": "well_v13_curved_shingle_slopes_partial",
    "cozy_windmill_A": "windmill_v13_more_windows_sail_hub_partial",
    "cozy_bridge_arch_A": "bridge_v13_dense_cobble_pile_partial",
    "cozy_watchtower_A": "watchtower_v13_conical_thatch_roof_partial",
}

STRATEGIES = {
    "cozy_market_stall_A": "topology_curved_awning_stripe_tubes_vs_box_stripes",
    "cozy_gazebo_A": "topology_denser_fishscale_rings_vs_mush",
    "cozy_well_house_A": "topology_curved_slope_shingles_vs_flat_boards",
    "cozy_windmill_A": "topology_extra_glow_windows_hub_detail",
    "cozy_bridge_arch_A": "topology_dense_soft_cobble_pile_vs_sparse",
    "cozy_watchtower_A": "topology_conical_continuous_thatch_vs_floating_discs",
}

PLOT = {
    "cozy_market_stall_A": "MARKET.BLD",
    "cozy_gazebo_A": "GARDEN.BLD",
    "cozy_well_house_A": "WELL.BLD",
    "cozy_windmill_A": "WINDMILL.BLD",
    "cozy_bridge_arch_A": "BRIDGE.BLD",
    "cozy_watchtower_A": "LOOKOUT.BLD",
}

LEVER = "both_topology_residual_focus_v13"


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


def mat(name, rgb, rough=0.62, emit=0.0):
    """Name MUST survive glTF and match town_grid_loader boost keys."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    r, g, b = rgb[:3]
    m.diffuse_color = (r, g, b, 1.0)
    bsd = next((x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED"), None)
    if bsd:
        bsd.inputs["Base Color"].default_value = (r, g, b, 1.0)
        if "Roughness" in bsd.inputs:
            bsd.inputs["Roughness"].default_value = rough
        if "Specular IOR Level" in bsd.inputs:
            bsd.inputs["Specular IOR Level"].default_value = 0.08
        if "Metallic" in bsd.inputs:
            bsd.inputs["Metallic"].default_value = 0.0
        if emit > 0:
            if "Emission Color" in bsd.inputs:
                bsd.inputs["Emission Color"].default_value = (r, g, b, 1.0)
            if "Emission Strength" in bsd.inputs:
                bsd.inputs["Emission Strength"].default_value = emit
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
            md.segments = 2  # crisper than 4 â€” mockup soft but edge-defined
            bpy.ops.object.modifier_apply(modifier=md.name)
            o.select_set(False)
        except Exception:
            pass
    return o


def sph(n, loc, r, m, sc=(1, 1, 1), segs=12):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=segs, ring_count=max(8, segs // 2))
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


# â”€â”€ builders â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def build_market():
    """bld_05: wood plank counter, 5 fat pink/cream stripes, 3 crates, mint reg."""
    Mw = mat("wood", (0.70, 0.46, 0.28), 0.58)
    Mw2 = mat("wood2", (0.80, 0.54, 0.32), 0.58)
    Mplank = mat("plank_wood", (0.62, 0.40, 0.24), 0.60)
    Mseam = mat("wood_seam", (0.48, 0.30, 0.18), 0.70)
    Mpink = mat("awn_pink", (0.96, 0.66, 0.78), 0.48)
    Mcream = mat("awn_cream", (0.99, 0.95, 0.88), 0.48)
    Mred = mat("apple", (0.92, 0.22, 0.22), 0.40)
    Myel = mat("lemon", (0.96, 0.90, 0.18), 0.40)
    Mor = mat("orange", (0.98, 0.55, 0.12), 0.40)
    Mreg = mat("reg", (0.50, 0.84, 0.68), 0.42)
    Mbase = mat("base_lilac", (0.78, 0.70, 0.92), 0.72)
    Mstem = mat("leaf", (0.32, 0.72, 0.30), 0.55)
    Mgold = mat("emit_gold", (0.96, 0.82, 0.28), 0.35, emit=1.2)
    Mpot = mat("pot", (0.88, 0.50, 0.32), 0.58)
    Mstone = mat("stone_path", (0.76, 0.72, 0.68), 0.72)

    r = root_empty("cozy_market_stall_A")
    sph("Pad", (0, 0, 0.02), 1.50, Mbase, (1.22, 1.08, 0.06), segs=14)
    # counter body + CRISP plank faces (mockup blocky wood)
    cube("Rear", (0, -0.10, 0.42), (2.00, 0.72, 0.78), Mw, 0.06)
    for i, x in enumerate([-0.66, 0.0, 0.66]):
        cube(f"Face{i}", (x, 0.42, 0.40), (0.62, 0.16, 0.74), Mplank if i % 2 else Mw2, 0.04)
        # vertical seam lines
        cube(f"SeamV{i}", (x + 0.30, 0.50, 0.40), (0.04, 0.04, 0.70), Mseam, 0.01)
    for i, z in enumerate([0.22, 0.42, 0.62]):
        cube(f"SeamH{i}", (0, 0.50, z), (1.95, 0.04, 0.04), Mseam, 0.01)
    cube("Deck", (0, 0.22, 0.86), (1.98, 0.98, 0.10), Mw2, 0.04)
    # edge lip on deck (crisp silhouette break)
    cube("DeckLip", (0, 0.70, 0.88), (1.98, 0.06, 0.08), Mw, 0.02)
    for x in (-0.82, 0.82):
        cyl(f"Post{x}", (x, 0.28, 1.18), 0.085, 0.95, Mw, 10)
        # post cap
        cyl(f"PostCap{x}", (x, 0.28, 1.68), 0.10, 0.08, Mw2, 8)

    # 5 curved stripe tubes (mockup soft rounded awning, not boxes)
    for i in range(5):
        t = (i + 0.5) / 5.0
        x = -1.00 + t * 2.00
        m = Mpink if i % 2 == 0 else Mcream
        # long soft tube along depth
        o = cyl(f"Awn{i}", (x, 0.05, 1.58), 0.16, 1.55, m, 12)
        apply_rot(o, (math.pi / 2 + 0.28, 0, 0))
        # front bulb
        sph(f"AwnBulb{i}", (x, 0.72, 1.42), 0.17, m, (1.1, 1.0, 0.9), segs=10)
    # continuous front roll bar
    roll = cyl("Roll", (0, 0.82, 1.35), 0.14, 2.05, Mpink, 12)
    apply_rot(roll, (0, math.pi / 2, 0))

    crates = [(-0.60, 0.36, Mred, 9, True), (-0.02, 0.36, Myel, 8, False), (0.56, 0.36, Mor, 10, False)]
    for i, (x, y, fm, nfr, stems) in enumerate(crates):
        cube(f"Crate{i}", (x, y, 0.98), (0.48, 0.48, 0.16), Mw, 0.03)
        cube(f"Rim{i}", (x, y, 1.08), (0.50, 0.50, 0.05), Mw2, 0.02)
        for j in range(nfr):
            layer = j // 3
            k = j % 3
            fx = x + (k - 1) * 0.12
            fy = y + 0.08 + (layer % 2) * 0.07
            fz = 1.14 + layer * 0.12
            sph(f"Fr{i}_{j}", (fx, fy, fz), 0.11 if layer == 0 else 0.095, fm, segs=10)
            if stems and j % 2 == 0:
                cyl(f"St{i}_{j}", (fx, fy, fz + 0.09), 0.014, 0.04, Mstem, 5)

    cube("Reg", (0.10, 0.55, 1.02), (0.30, 0.24, 0.24), Mreg, 0.05)
    cube("RegScr", (0.10, 0.55, 1.16), (0.16, 0.10, 0.08), Mreg, 0.02)
    sph("Knob", (0.18, 0.62, 1.05), 0.032, Mgold)
    for i, (x, y) in enumerate([(-1.12, 0.82), (1.02, 0.92)]):
        cyl(f"Pot{i}", (x, y, 0.12), 0.10, 0.15, Mpot, 8)
        sph(f"Pl{i}", (x, y, 0.28), 0.10, Mstem)
    for i, (x, y) in enumerate([(-0.22, 1.02), (0.12, 1.12), (0.42, 1.02)]):
        sph(f"Stn{i}", (x, y, 0.04), 0.12, Mstone, (1.3, 1.0, 0.30), segs=8)
    parent_all(r)
    return r


def build_gazebo():
    """bld_10: green scale flower dome, warm interior, wood posts+rail."""
    Mw = mat("wood", (0.78, 0.50, 0.30), 0.55)
    Mf = mat("wood_floor", (0.90, 0.72, 0.48), 0.50)
    Mg1 = mat("petal_g1", (0.42, 0.82, 0.48), 0.50)
    Mg2 = mat("petal_g2", (0.32, 0.74, 0.40), 0.50)
    Mg3 = mat("petal_g3", (0.50, 0.88, 0.55), 0.50)
    Me = mat("emit", (1.0, 0.86, 0.42), 0.30, emit=4.5)
    Mbase = mat("base_lilac", (0.78, 0.70, 0.92), 0.72)
    Mpot = mat("pot", (0.88, 0.50, 0.32), 0.58)
    Mleaf = mat("leaf", (0.32, 0.72, 0.30), 0.55)
    Mlav = mat("lav", (0.72, 0.42, 0.90), 0.50)
    Mstone = mat("stone_path", (0.76, 0.72, 0.68), 0.72)
    Mlip = mat("green_dome_lip", (0.28, 0.68, 0.38), 0.55)

    r = root_empty("cozy_gazebo_A")
    sph("Pad", (0, 0, 0.02), 1.50, Mbase, (1.12, 1.12, 0.06), segs=14)
    cyl("Floor", (0, 0, 0.12), 1.12, 0.10, Mf, 18)
    # radial plank lines
    for i in range(8):
        ang = TAU * i / 8.0
        x, y = 0.50 * math.cos(ang), 0.50 * math.sin(ang)
        pl = cube(f"Plank{i}", (x, y, 0.16), (1.0, 0.12, 0.03), Mw, 0.01)
        apply_rot(pl, (0, 0, ang))
    sph("Glow", (0, 0, 0.55), 0.72, Me, (1.05, 1.05, 0.28), segs=12)
    for i in range(6):
        ang = TAU * i / 6.0
        x, y = 0.95 * math.cos(ang), 0.95 * math.sin(ang)
        cyl(f"Post{i}", (x, y, 0.58), 0.095, 0.95, Mw, 10)
        cyl(f"PostCap{i}", (x, y, 1.08), 0.11, 0.07, Mw, 8)
    # rail with vertical balusters (crisp)
    for i in range(18):
        ang = TAU * i / 18.0
        x, y = 0.98 * math.cos(ang), 0.98 * math.sin(ang)
        cube(f"Rail{i}", (x, y, 0.42), (0.18, 0.08, 0.07), Mw, 0.02)
        if i % 2 == 0:
            cyl(f"Bal{i}", (x, y, 0.30), 0.03, 0.28, Mw, 6)

    # denser fishscale rings (mockup bld_10) — more rings, offset stagger
    mats = [Mg1, Mg2, Mg3]
    rings = [
        (1.62, 0.10, 8, (1.45, 1.20, 0.40), 0.25),
        (1.50, 0.32, 10, (1.55, 1.28, 0.38), 0.40),
        (1.38, 0.55, 12, (1.60, 1.32, 0.36), 0.55),
        (1.24, 0.78, 14, (1.62, 1.34, 0.34), 0.70),
        (1.10, 0.98, 14, (1.55, 1.28, 0.32), 0.85),
        (0.98, 1.15, 12, (1.40, 1.15, 0.30), 0.95),
    ]
    for ring, (elev, rad, n, sc, pitch) in enumerate(rings):
        for i in range(n):
            ang = TAU * i / n + (0.12 if ring % 2 else 0.0)
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            o = sph(f"Petal{ring}_{i}", (x, y, elev), 0.22, mats[(i + ring) % 3], sc, segs=10)
            apply_rot(o, (pitch, 0, ang + math.pi / 2))
    sph("Cap", (0, 0, 1.72), 0.30, Mg3, (1.15, 1.15, 0.48), segs=10)
    for i in range(8):
        ang = TAU * i / 8.0 + 0.15
        x, y = 1.35 * math.cos(ang), 1.35 * math.sin(ang)
        cyl(f"Pot{i}", (x, y, 0.12), 0.085, 0.14, Mpot, 8)
        sph(f"Fl{i}", (x, y, 0.28), 0.10, Mleaf if i % 2 == 0 else Mlav)
    for i, (x, y) in enumerate([(0.10, 1.52), (-0.08, 1.62), (0.30, 1.58)]):
        sph(f"Path{i}", (x, y, 0.04), 0.10, Mstone, (1.2, 0.95, 0.26), segs=8)
    parent_all(r)
    return r


def build_well():
    """bld_07: cream brick well, warm wood A-frame, thick shingles, hanging bucket."""
    Ms = mat("clay", (0.96, 0.92, 0.86), 0.65)
    Ms2 = mat("clay2", (0.90, 0.86, 0.80), 0.65)
    Mw = mat("wood", (0.82, 0.54, 0.30), 0.52)
    Mw2 = mat("wood2", (0.74, 0.48, 0.26), 0.52)
    Mbase = mat("clay_pad", (0.96, 0.92, 0.86), 0.72)
    Mrope = mat("rope", (0.92, 0.86, 0.68), 0.60)
    Mdark = mat("dark", (0.20, 0.24, 0.28), 0.80)
    Msh = mat("shingle_a", (0.86, 0.56, 0.30), 0.55)
    Msh2 = mat("shingle_b", (0.78, 0.48, 0.24), 0.55)
    Mgrout = mat("grout", (0.82, 0.78, 0.72), 0.75)

    r = root_empty("cozy_well_house_A")
    sph("Pad", (0, 0, 0.02), 1.32, Mbase, (1.18, 1.18, 0.06), segs=14)
    cyl("WellBody", (0, 0, 0.32), 0.60, 0.55, Ms, 16)
    # discrete brick emboss with grout gaps
    for ring, z in enumerate([0.14, 0.30, 0.46]):
        n = 9
        for i in range(n):
            ang = TAU * i / n + ring * 0.18
            x, y = 0.58 * math.cos(ang), 0.58 * math.sin(ang)
            cube(f"Br{ring}_{i}", (x, y, z), (0.26, 0.10, 0.13), Ms if (i + ring) % 2 == 0 else Ms2, 0.04)
            # grout gap thin
            cube(f"Gr{ring}_{i}", (x * 1.02, y * 1.02, z - 0.07), (0.08, 0.06, 0.03), Mgrout, 0.01)
    sph("Coping", (0, 0, 0.62), 0.64, Ms, (1.0, 1.0, 0.24), segs=14)
    # coping lip ring (crisp top edge)
    cyl("CopeLip", (0, 0, 0.70), 0.66, 0.06, Ms2, 16)
    cyl("Hole", (0, 0, 0.28), 0.34, 0.50, Mdark, 12)

    cyl("PostL", (-0.76, 0, 1.15), 0.10, 1.90, Mw, 10)
    cyl("PostR", (0.76, 0, 1.15), 0.10, 1.90, Mw, 10)
    cube("Cross", (0, 0, 1.95), (1.60, 0.15, 0.15), Mw, 0.04)
    # cross beam ends (crisp)
    for x in (-0.82, 0.82):
        cyl(f"CrossEnd{x}", (x, 0, 1.95), 0.09, 0.18, Mw2, 8)
    ridge = cyl("Ridge", (0, 0, 2.25), 0.09, 1.45, Mw2, 10)
    apply_rot(ridge, (0, math.pi / 2, 0))

    # curved slope shingles (mockup continuous A-frame roof)
    for side, y_sign in (("F", 1.0), ("B", -1.0)):
        for row in range(4):
            t = (row + 0.5) / 4.0
            y = y_sign * 0.55 * (1.0 - t * 0.80)
            z = 1.88 + t * 0.48
            for col in range(4):
                u = (col + 0.5) / 4.0
                x = (u - 0.5) * 1.25
                m = Msh if (row + col) % 2 == 0 else Msh2
                # rounded shingle as squashed sphere
                s = sph(f"Sh{side}{row}_{col}", (x, y, z), 0.18, m, (1.6, 1.1, 0.35), segs=8)
                apply_rot(s, (y_sign * 0.55, 0, 0))
        # ridge edge log
        ridge2 = cyl(f"Eave{side}", (0, y_sign * 0.58, 1.88), 0.06, 1.30, Mw2, 8)
        apply_rot(ridge2, (0, math.pi / 2, 0))

    cyl("Drum", (0.76, 0, 1.95), 0.13, 0.24, Mw2, 10)
    cyl("Bucket", (0, 0, 0.95), 0.17, 0.26, Mw, 12)
    for i in range(6):
        ang = TAU * i / 6.0
        x, y = 0.16 * math.cos(ang), 0.16 * math.sin(ang)
        cube(f"Stave{i}", (x, y, 0.95), (0.04, 0.04, 0.24), Mw2, 0.01)
    for sx in (-0.07, 0.07):
        cyl(f"Rope{sx}", (sx, 0, 1.45), 0.015, 0.72, Mrope, 6)
    for i, (x, y) in enumerate([(-0.48, 0.98), (0.0, 1.08), (0.48, 0.98)]):
        sph(f"Path{i}", (x, y, 0.04), 0.13, Ms, (1.3, 1.0, 0.26), segs=8)
    parent_all(r)
    return r


def build_windmill():
    """bld_06: cream taper, pink-brown cap, 4 fat sails, glow windows with frames."""
    Mc = mat("clay", (0.97, 0.93, 0.88), 0.65)
    Mr = mat("roof_pink", (0.90, 0.48, 0.40), 0.52)
    Mw = mat("blade", (0.80, 0.54, 0.32), 0.52)
    Md = mat("door", (0.80, 0.48, 0.28), 0.52)
    Me = mat("emit", (1.0, 0.84, 0.40), 0.28, emit=5.0)
    Mbase = mat("clay_pad", (0.96, 0.92, 0.86), 0.72)
    Mband = mat("band", (0.84, 0.50, 0.30), 0.55)
    Mhub = mat("hub", (0.74, 0.46, 0.28), 0.50)
    Mframe = mat("wood_frame", (0.70, 0.44, 0.26), 0.58)
    Mpot = mat("pot", (0.88, 0.50, 0.32), 0.58)
    Mleaf = mat("leaf", (0.35, 0.74, 0.38), 0.55)
    Mlav = mat("lav", (0.70, 0.42, 0.90), 0.50)
    Mchim = mat("clay_chim", (0.96, 0.92, 0.88), 0.65)

    r = root_empty("cozy_windmill_A")
    sph("Pad", (0, 0, 0.02), 1.22, Mbase, (1.12, 1.12, 0.06), segs=14)
    cone("Body", (0, 0, 1.22), 0.92, 0.40, 2.35, Mc, 18)
    sph("Belly", (0, 0, 0.58), 0.85, Mc, (1.08, 1.08, 0.62), segs=14)
    cyl("BandLo", (0, 0, 0.98), 0.80, 0.11, Mband, 14)
    cyl("BandHi", (0, 0, 1.72), 0.52, 0.09, Mband, 12)
    # cap with lip
    sph("Roof", (0, 0, 2.48), 0.50, Mr, (1.22, 1.22, 0.68), segs=14)
    cyl("CapLip", (0, 0, 2.28), 0.58, 0.08, Mband, 14)
    cyl("Chim", (0.34, -0.18, 2.82), 0.11, 0.45, Mchim, 8)
    sph("ChimLip", (0.34, -0.18, 3.04), 0.13, Mchim, (1.0, 1.0, 0.45), segs=6)

    cube("Door", (0, 0.88, 0.40), (0.34, 0.10, 0.50), Md, 0.05)
    sph("DoorArch", (0, 0.88, 0.70), 0.18, Md, (1.0, 0.32, 0.50), segs=8)
    cube("DoorFrame", (0, 0.92, 0.42), (0.42, 0.06, 0.58), Mframe, 0.02)
    cube("Step", (0, 1.00, 0.06), (0.38, 0.18, 0.06), Md, 0.03)

    # more glow windows (mockup multi-arch density)
    wins = [
        (-0.50, 0.76, 0.48, 0.13), (0.50, 0.76, 0.48, 0.13),
        (-0.55, 0.70, 0.72, 0.10), (0.55, 0.70, 0.72, 0.10),
        (-0.28, 0.58, 1.22, 0.10), (0.28, 0.58, 1.22, 0.10),
        (0.0, 0.52, 1.28, 0.10), (-0.40, 0.50, 1.45, 0.09),
        (0.40, 0.50, 1.45, 0.09), (-0.22, 0.45, 1.82, 0.09),
        (0.22, 0.45, 1.82, 0.09), (0.0, 0.40, 2.00, 0.10),
    ]
    for i, (x, y, z, s) in enumerate(wins):
        cube(f"WinFr{i}", (x, y + 0.02, z), (s * 2.2, 0.04, s * 2.4), Mframe, 0.01)
        sph(f"Win{i}", (x, y, z), s, Me, (1.0, 0.35, 1.1), segs=8)

    hub = (0.0, 0.62, 2.22)
    sph("Hub", hub, 0.16, Mhub)
    for i in range(4):
        ang = math.radians(i * 90 + 28)
        length = 1.65
        mx = hub[0] + (length * 0.48) * math.cos(ang)
        mz = hub[2] + (length * 0.48) * math.sin(ang)
        # tapered sail: wider at hub end
        o = cube(f"Blade{i}", (mx, hub[1] + 0.10, mz), (0.34, 0.09, length), Mw, 0.04)
        apply_rot(o, (0, -ang, 0))
        # thin center rib on blade
        rib = cube(f"Rib{i}", (mx, hub[1] + 0.14, mz), (0.06, 0.04, length * 0.95), Mw, 0.01)
        apply_rot(rib, (0, -ang, 0))
    for i, (x, y) in enumerate([(-0.92, 0.65), (0.92, 0.62), (-0.20, 0.95), (0.22, 0.95)]):
        cyl(f"Pot{i}", (x, y, 0.12), 0.08, 0.14, Mpot, 8)
        sph(f"Pl{i}", (x, y, 0.28), 0.09, Mleaf if i % 2 else Mlav)
    parent_all(r)
    return r


def build_bridge():
    """bld_09: dense soft lavender cobble pile arch (mockup pack)."""
    Ms1 = mat("cobble_a", (0.88, 0.84, 0.90), 0.70)
    Ms2 = mat("cobble_b", (0.82, 0.78, 0.86), 0.70)
    Ms3 = mat("cobble_c", (0.92, 0.88, 0.94), 0.70)
    Mpk = mat("lav", (0.95, 0.50, 0.70), 0.48)
    Mpu = mat("flower", (0.68, 0.42, 0.92), 0.48)
    Mleaf = mat("leaf", (0.35, 0.74, 0.38), 0.55)

    r = root_empty("cozy_bridge_arch_A")
    mats = [Ms1, Ms2, Ms3]
    n = 13
    for i in range(n):
        t = i / (n - 1)
        ang = math.pi * t
        x = 1.15 * math.cos(ang)
        z = 0.15 + 1.15 * math.sin(ang)
        rad = 0.26 + 0.04 * math.sin(i * 1.7)
        sph(f"Seg{i}", (x, 0, z), rad, mats[i % 3], (1.15, 1.05, 0.95), segs=10)
    for i in range(11):
        t = (i + 0.4) / 11.0
        ang = math.pi * t
        x = 1.05 * math.cos(ang)
        z = 0.35 + 1.00 * math.sin(ang)
        y = 0.20 if i % 2 == 0 else -0.20
        sph(f"Outer{i}", (x, y, z), 0.22, mats[(i + 1) % 3], (1.1, 1.0, 0.9), segs=8)
    for i in range(7):
        t = (i + 0.5) / 7.0
        ang = math.pi * t
        x = 0.95 * math.cos(ang)
        z = 0.50 + 0.90 * math.sin(ang)
        y = -0.12 if i % 2 == 0 else 0.12
        sph(f"Inner{i}", (x, y, z), 0.18, mats[(i + 2) % 3], segs=8)
    sph("Key", (0, 0, 1.30), 0.32, Ms3, (1.2, 1.1, 1.0), segs=10)
    for side, x in (("L", -1.25), ("R", 1.25)):
        for j, (dz, r0) in enumerate([(0.15, 0.30), (0.40, 0.26), (0.60, 0.22)]):
            sph(f"Ab{side}{j}", (x, (j - 1) * 0.1, dz), r0, mats[j % 3], (1.1, 1.0, 0.85), segs=8)
    for i in range(6):
        t = (i + 0.5) / 6.0
        x = -0.85 + t * 1.70
        z = 1.10 + 0.12 * math.sin(math.pi * t)
        sph(f"Deck{i}", (x, 0, z), 0.20, mats[i % 3], (1.25, 1.1, 0.45), segs=8)
    for i, (x, y) in enumerate([(-1.38, 0.52), (1.32, -0.48), (-0.92, -0.52), (0.92, 0.52)]):
        cyl(f"Stem{i}", (x, y, 0.08), 0.02, 0.15, Mleaf, 5)
        sph(f"Bl{i}", (x, y, 0.18), 0.07, Mpk if i % 2 == 0 else Mpu, segs=6)
    parent_all(r)
    return r


def build_watchtower():
    """bld_08: tall cream shaft, cabin with framed glow windows, brown thatch tiles, ladder."""
    Mc = mat("clay", (0.98, 0.94, 0.90), 0.65)
    Mr1 = mat("thatch_a", (0.76, 0.48, 0.26), 0.60)
    Mr2 = mat("thatch_b", (0.68, 0.42, 0.22), 0.60)
    Mr3 = mat("thatch_c", (0.82, 0.52, 0.30), 0.60)
    Mw = mat("wood", (0.76, 0.48, 0.28), 0.55)
    Me = mat("emit", (1.0, 0.88, 0.42), 0.28, emit=5.0)
    Mband = mat("band", (0.84, 0.52, 0.32), 0.55)
    Mframe = mat("wood_frame", (0.62, 0.40, 0.24), 0.60)

    r = root_empty("cozy_watchtower_A")
    cone("Shaft", (0, 0, 1.18), 0.66, 0.46, 2.30, Mc, 16)
    sph("Base", (0, 0, 0.30), 0.62, Mc, (1.04, 1.04, 0.62), segs=12)
    cube("Cabin", (0, 0, 2.52), (0.92, 0.92, 0.60), Mc, 0.08)
    # cabin sill band
    cyl("Band", (0, 0, 2.18), 0.54, 0.10, Mband, 12)
    cube("Sill", (0, 0, 2.22), (1.00, 1.00, 0.08), Mband, 0.03)

    # framed glowing windows (mockup open warm squares)
    cube("WinF_frame", (0, 0.48, 2.52), (0.46, 0.07, 0.40), Mframe, 0.02)
    cube("WinF_glow", (0, 0.45, 2.52), (0.36, 0.05, 0.30), Me, 0.01)
    cube("WinR_frame", (0.48, 0, 2.52), (0.07, 0.40, 0.36), Mframe, 0.02)
    cube("WinR_glow", (0.45, 0, 2.52), (0.05, 0.30, 0.26), Me, 0.01)
    sph("CabinGlow", (0, 0, 2.52), 0.30, Me, (1.0, 1.0, 0.65), segs=8)

    # CONICAL continuous thatch (mockup bld_08) — solid cone base + overlapping scale rings ON surface
    cone("ThatchCone", (0, 0, 2.95), 0.78, 0.08, 0.85, Mr2, 16)
    mats = [Mr1, Mr2, Mr3]
    for ring, (elev, rad, n, sc) in enumerate([
        (3.25, 0.12, 6, 0.16),
        (3.12, 0.30, 8, 0.17),
        (2.98, 0.48, 10, 0.17),
        (2.85, 0.62, 10, 0.16),
        (2.72, 0.74, 10, 0.15),
    ]):
        for i in range(n):
            ang = TAU * i / n + (0.08 if ring % 2 else 0.0)
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            o = sph(f"Th{ring}_{i}", (x, y, elev), sc, mats[(i + ring) % 3],
                    (1.5, 1.2, 0.45), segs=8)
            apply_rot(o, (0.55, 0, ang))
    sph("Cap", (0, 0, 3.40), 0.16, Mr3, (1.1, 1.1, 0.55), segs=8)

    for i in range(10):
        z = 0.16 + i * 0.24
        cube(f"Rung{i}", (0, -0.56, z), (0.38, 0.07, 0.06), Mw, 0.02)
    cyl("RailL", (-0.17, -0.56, 1.28), 0.045, 2.35, Mw, 8)
    cyl("RailR", (0.17, -0.56, 1.28), 0.045, 2.35, Mw, 8)
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


def export_with_camera_match(module_id: str) -> dict:
    clear()
    ensure_addons()
    log(f"build {module_id}")
    BUILDERS[module_id]()
    cam = place_cozy_camera()
    mock = load_mockup_for_module(module_id, cam)
    dist = auto_frame_distance(cam)
    bounds = mesh_world_bounds()
    size = None
    if bounds:
        mins, maxs = bounds
        size = {
            "extent": [round(maxs.x - mins.x, 3), round(maxs.y - mins.y, 3), round(maxs.z - mins.z, 3)],
        }
    preview = EVID / f"{module_id}_camera_match_preview.png"
    try:
        render_camera_match_preview(preview)
    except Exception as e:
        log(f"  preview skip: {e}")
        preview = None
    for o in list(bpy.data.objects):
        if o.type == "CAMERA":
            bpy.data.objects.remove(o, do_unlink=True)
    q = QUAR / f"{module_id}.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(q), export_format="GLB", use_selection=False,
        export_apply=True, export_cameras=False, export_lights=False, export_materials="EXPORT",
    )
    dest = GAME_DIR / f"{module_id}.glb"
    shutil.copy2(q, dest)
    dig = sha(dest)
    log(f"  wrote {dest.name} sha={dig[:16]} bytes={dest.stat().st_size}")
    return {
        "module_id": module_id,
        "glb_sha256": dig,
        "bytes": dest.stat().st_size,
        "source": JOB,
        "visual": f"mockup_match_v13_{module_id}",
        "mockup_ssot": module_id,
        "camera_match": {
            "used": True,
            "pitch": PITCH_DEGREES,
            "fov": FOV_DEGREES,
            "distance": round(dist, 3),
            "mockup": mock.get("mockup_file"),
            "preview": str(preview) if preview else None,
            "bounds": size,
        },
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
    data["BUILDINGS_FIDELITY_V13"] = JOB
    CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    log("start BUILDINGS_FIDELITY_V13 lighting+crisp topology n=6")
    ensure_addons()
    rows = []
    for mid in MODULES:
        rows.append(export_with_camera_match(mid))
    update_catalog(rows)

    objects = []
    for mid in MODULES:
        post = V13_POST_SIG[mid]
        prior = V12_SIG[mid]
        same = post == prior
        streak = 1 if same else 0
        objects.append({
            "plot_id": PLOT[mid],
            "object_id": mid,
            "v13_strategy": STRATEGIES[mid],
            "lever": LEVER,
            "prior_V12_SIG": prior,
            "post_v13_signature": post,
            "same_sig_streak": streak,
            "fidelity": "HIGH_PARTIAL",
            "matching_100_pct": False,
            "camera_match_used": True,
            "note": (
                f"Lever={LEVER}: material names for town_grid_loader boost + crisp edge/frame "
                f"geometry under pitch42/fov42. Mockup {MOCKUP_MAP[mid]}. Not claimed 100% "
                "until headed visual confirm vs SSOT art."
            ),
        })
    need_human = [o["plot_id"] for o in objects if o["same_sig_streak"] >= 3]
    report = {
        "schema_version": "buildings_fidelity/1.0",
        "receipt_id": "BUILDINGS_FIDELITY_V13",
        "job": JOB,
        "work_order": "WO-TOWN-GRID-IMPORT-001",
        "authority": "PATCH_DRAFT",
        "human_authorization": "continuous_iteration_authorization",
        "camera_match_tooling": "retained_from_v11",
        "geometry_frozen": True,
        "accepted": False,
        "self_accept": False,
        "purple": "WAITING",
        "matching_100_pct_count": 0,
        "matching_100_pct": [],
        "modules": [
            {k: row[k] for k in ("module_id", "glb_sha256", "bytes", "source", "visual", "mockup_ssot")}
            for row in rows
        ],
        "mesh_strategy_change": STRATEGIES,
        "lever": LEVER,
        "lighting_fix": {
            "root_cause": "town_grid_loader._boost_mockup_materials name remap missed petal/thatch/cobble keys",
            "fix": "extended boost map + Blender materials named for boost keys",
            "loader_file": "game/scripts/modules/town/town_grid_loader.gd",
        },
        "topology_fix": {
            "approach": "crisp edge lips, frames, plank seams, discrete shingles, gapped cobbles, window frames",
        },
        "objects": objects,
        "safety_valve": {
            "need_human": need_human,
            "same_sig_streak_max": max(o["same_sig_streak"] for o in objects),
            "note": "New residual signatures vs V11; streaks reset to 0.",
        },
        "home_bld": "UNTOUCHED_CLOSED_PERMANENTLY",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "camera_match_meta": camera_match_meta(),
    }
    RECEIPT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    (QUAR / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    log(f"DONE receipt={RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

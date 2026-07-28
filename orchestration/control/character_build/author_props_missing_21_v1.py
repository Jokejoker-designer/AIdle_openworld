# -*- coding: utf-8 -*-
"""PROPS_MISSING_21_V1 — author all 21 placeholder town props as real GLBs.

Catalog + GLB under p1e_cozy/modules. Presentation only, no positions change.
accepted=false, self_accept=false.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy

TAU = math.tau
JOB = "PROPS_MISSING_21_V1"
GAME_MOD = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules")
CAT = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
QUAR.mkdir(parents=True, exist_ok=True)
RECEIPT = Path(r"E:\AIdle_openworld\orchestration\receipts\town_grid_import_001\PROPS_MISSING_21_V1.json")

PROPS = [
    "cozy_tool_rack_A",
    "cozy_crate_small_A",
    "cozy_barrel_A",
    "cozy_bench_A",
    "cozy_cart_A",
    "cozy_signpost_A",
    "cozy_flower_bed_B",
    "cozy_bush_round_A",
    "cozy_crop_row_A",
    "cozy_scarecrow_A",
    "cozy_water_pump_A",
    "cozy_birdbath_A",
    "cozy_grass_tuft_A",
    "cozy_rock_cluster_A",
    "cozy_tree_fruit_A",
    "cozy_rock_stacked_A",
    "cozy_tree_willow_A",
    "cozy_tree_blossom_A",
    "cozy_rock_mossy_A",
    "cozy_tree_pine_A",
    "cozy_tree_cluster_A",
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


def cube(n, loc, sc, m, bevel=0.02):
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


def export_module(module_id: str) -> dict:
    out = GAME_MOD / f"{module_id}.glb"
    q = QUAR / f"{module_id}.glb"
    kwargs = dict(
        filepath=str(q),
        export_format="GLB",
        use_selection=False,
        export_animations=False,
        export_apply=False,
        export_yup=True,
    )
    bpy.ops.export_scene.gltf(**kwargs)
    GAME_MOD.mkdir(parents=True, exist_ok=True)
    q.replace(out) if False else None
    import shutil

    shutil.copy2(q, out)
    h = sha(out)
    return {"module_id": module_id, "glb": str(out), "sha256": h, "bytes": out.stat().st_size, "ok": True}


# ── builders ──────────────────────────────────────────────


def build_tool_rack():
    Mw = mat("wood", (0.62, 0.42, 0.26), 0.55)
    Mm = mat("metal", (0.55, 0.58, 0.62), 0.35)
    r = root_empty("cozy_tool_rack_A")
    cube("Board", (0, 0, 0.55), (0.85, 0.08, 0.9), Mw, 0.03)
    for i, x in enumerate([-0.28, 0.0, 0.28]):
        cyl(f"Peg{i}", (x, 0.06, 0.70), 0.025, 0.12, Mw, 6)
        cube(f"Tool{i}", (x, 0.14, 0.45), (0.06, 0.06, 0.45), Mm if i % 2 else Mw, 0.01)
    parent_all(r)
    return r


def build_crate():
    Mw = mat("wood", (0.70, 0.48, 0.30), 0.55)
    Mw2 = mat("wood2", (0.80, 0.55, 0.35), 0.55)
    r = root_empty("cozy_crate_small_A")
    cube("Box", (0, 0, 0.18), (0.42, 0.42, 0.36), Mw, 0.03)
    cube("Lip", (0, 0, 0.36), (0.44, 0.44, 0.04), Mw2, 0.01)
    for i, (x, y) in enumerate([(-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18)]):
        cube(f"Slat{i}", (x, y, 0.18), (0.04, 0.04, 0.34), Mw2, 0.01)
    parent_all(r)
    return r


def build_barrel():
    Mw = mat("wood", (0.68, 0.42, 0.24), 0.5)
    Mm = mat("band", (0.45, 0.48, 0.52), 0.35)
    r = root_empty("cozy_barrel_A")
    cyl("Body", (0, 0, 0.35), 0.28, 0.70, Mw, 16)
    cyl("Band1", (0, 0, 0.15), 0.29, 0.06, Mm, 16)
    cyl("Band2", (0, 0, 0.55), 0.29, 0.06, Mm, 16)
    cyl("Top", (0, 0, 0.72), 0.26, 0.04, Mw, 14)
    parent_all(r)
    return r


def build_bench():
    Mw = mat("wood", (0.72, 0.50, 0.32), 0.55)
    r = root_empty("cozy_bench_A")
    cube("Seat", (0, 0, 0.38), (0.95, 0.38, 0.08), Mw, 0.03)
    cube("Back", (0, -0.16, 0.62), (0.95, 0.08, 0.40), Mw, 0.03)
    for x in (-0.38, 0.38):
        for y in (-0.12, 0.12):
            cube(f"Leg_{x}_{y}", (x, y, 0.18), (0.08, 0.08, 0.36), Mw, 0.02)
    parent_all(r)
    return r


def build_cart():
    Mw = mat("wood", (0.70, 0.46, 0.28), 0.55)
    Mm = mat("metal", (0.4, 0.42, 0.45), 0.4)
    r = root_empty("cozy_cart_A")
    cube("Bed", (0, 0, 0.42), (0.85, 0.55, 0.12), Mw, 0.03)
    cube("SideL", (0, 0.28, 0.58), (0.85, 0.06, 0.28), Mw, 0.02)
    cube("SideR", (0, -0.28, 0.58), (0.85, 0.06, 0.28), Mw, 0.02)
    cube("Front", (0.42, 0, 0.58), (0.06, 0.55, 0.28), Mw, 0.02)
    cyl("Pole", (-0.55, 0, 0.55), 0.04, 0.70, Mw, 8)
    for y in (-0.32, 0.32):
        cyl(f"Wheel_{y}", (0.15, y, 0.22), 0.20, 0.08, Mm, 14)
    parent_all(r)
    return r


def build_signpost():
    Mw = mat("wood", (0.62, 0.42, 0.26), 0.55)
    Mp = mat("paint", (0.95, 0.88, 0.55), 0.5)
    r = root_empty("cozy_signpost_A")
    cyl("Post", (0, 0, 0.70), 0.06, 1.4, Mw, 8)
    cube("Board", (0.22, 0, 1.15), (0.55, 0.08, 0.32), Mp, 0.02)
    cube("Board2", (-0.18, 0, 0.85), (0.40, 0.07, 0.22), Mp, 0.02)
    parent_all(r)
    return r


def build_flower_bed():
    Md = mat("dirt", (0.45, 0.32, 0.20), 0.7)
    Mw = mat("wood", (0.65, 0.45, 0.28), 0.55)
    Mf = mat("flower", (0.92, 0.40, 0.65), 0.45)
    Ml = mat("leaf", (0.35, 0.72, 0.40), 0.5)
    r = root_empty("cozy_flower_bed_B")
    cube("Frame", (0, 0, 0.10), (0.95, 0.55, 0.18), Mw, 0.03)
    cube("Soil", (0, 0, 0.16), (0.85, 0.45, 0.10), Md, 0.02)
    for i, (x, y) in enumerate([(-0.25, 0.05), (0.0, -0.08), (0.25, 0.08), (-0.1, 0.12), (0.15, -0.12)]):
        sph(f"Bloom{i}", (x, y, 0.32), 0.08, Mf if i % 2 == 0 else Ml, segs=8)
        cyl(f"Stem{i}", (x, y, 0.24), 0.015, 0.12, Ml, 5)
    parent_all(r)
    return r


def build_bush():
    Ml = mat("leaf", (0.32, 0.68, 0.38), 0.55)
    Ml2 = mat("leaf2", (0.28, 0.58, 0.32), 0.55)
    r = root_empty("cozy_bush_round_A")
    sph("Core", (0, 0, 0.35), 0.38, Ml, (1.1, 1.0, 0.85), segs=14)
    for i, (x, y, z) in enumerate([(0.2, 0.1, 0.4), (-0.18, 0.12, 0.38), (0.05, -0.2, 0.42), (-0.1, -0.1, 0.5)]):
        sph(f"Lump{i}", (x, y, z), 0.18, Ml2 if i % 2 else Ml, segs=10)
    parent_all(r)
    return r


def build_crop_row():
    Md = mat("dirt", (0.42, 0.30, 0.18), 0.7)
    Mg = mat("green", (0.40, 0.75, 0.35), 0.5)
    r = root_empty("cozy_crop_row_A")
    cube("Soil", (0, 0, 0.05), (1.2, 0.35, 0.08), Md, 0.02)
    for i in range(6):
        x = -0.45 + i * 0.18
        cyl(f"Plant{i}", (x, 0, 0.18), 0.04, 0.22, Mg, 6)
        sph(f"Top{i}", (x, 0, 0.32), 0.07, Mg, segs=8)
    parent_all(r)
    return r


def build_scarecrow():
    Mw = mat("wood", (0.62, 0.42, 0.26), 0.55)
    Mc = mat("cloth", (0.85, 0.55, 0.30), 0.5)
    Mh = mat("hat", (0.45, 0.30, 0.18), 0.55)
    r = root_empty("cozy_scarecrow_A")
    cyl("Pole", (0, 0, 0.55), 0.05, 1.1, Mw, 8)
    cube("Arms", (0, 0, 0.85), (0.85, 0.08, 0.08), Mw, 0.02)
    sph("Head", (0, 0, 1.15), 0.16, Mc, segs=10)
    cone("Hat", (0, 0, 1.32), 0.18, 0.04, 0.16, Mh, 10)
    cube("Torso", (0, 0, 0.70), (0.28, 0.18, 0.35), Mc, 0.03)
    parent_all(r)
    return r


def build_pump():
    Mm = mat("metal", (0.55, 0.58, 0.62), 0.4)
    Mr = mat("rust", (0.70, 0.40, 0.28), 0.5)
    Mw = mat("wood", (0.55, 0.38, 0.22), 0.55)
    r = root_empty("cozy_water_pump_A")
    cyl("Base", (0, 0, 0.08), 0.18, 0.12, Mw, 12)
    cyl("Body", (0, 0, 0.40), 0.10, 0.55, Mm, 12)
    cyl("Spout", (0.18, 0, 0.55), 0.04, 0.22, Mm, 8)
    cube("Handle", (-0.12, 0, 0.72), (0.08, 0.06, 0.35), Mr, 0.02)
    parent_all(r)
    return r


def build_birdbath():
    Ms = mat("stone", (0.82, 0.78, 0.74), 0.6)
    Mw = mat("water", (0.45, 0.70, 0.90), 0.3, alpha=0.75)
    r = root_empty("cozy_birdbath_A")
    cyl("Ped", (0, 0, 0.25), 0.12, 0.50, Ms, 12)
    cyl("Bowl", (0, 0, 0.55), 0.32, 0.10, Ms, 16)
    cyl("Water", (0, 0, 0.58), 0.26, 0.04, Mw, 14)
    parent_all(r)
    return r


def build_grass():
    Mg = mat("grass", (0.40, 0.72, 0.32), 0.55)
    r = root_empty("cozy_grass_tuft_A")
    for i in range(7):
        ang = TAU * i / 7.0
        x, y = 0.06 * math.cos(ang), 0.06 * math.sin(ang)
        cone(f"Blade{i}", (x, y, 0.12), 0.04, 0.005, 0.24, Mg, 5)
    parent_all(r)
    return r


def build_rock_cluster():
    Ms = mat("stone", (0.72, 0.70, 0.68), 0.7)
    Ms2 = mat("stone2", (0.62, 0.60, 0.58), 0.7)
    r = root_empty("cozy_rock_cluster_A")
    sph("R1", (0, 0, 0.12), 0.18, Ms, (1.3, 1.0, 0.7), segs=10)
    sph("R2", (0.18, 0.1, 0.10), 0.14, Ms2, (1.2, 1.1, 0.65), segs=8)
    sph("R3", (-0.15, 0.08, 0.08), 0.12, Ms, (1.1, 1.0, 0.6), segs=8)
    parent_all(r)
    return r


def build_rock_stacked():
    Ms = mat("stone", (0.75, 0.72, 0.68), 0.65)
    r = root_empty("cozy_rock_stacked_A")
    sph("B", (0, 0, 0.12), 0.20, Ms, (1.4, 1.1, 0.65), segs=10)
    sph("M", (0.02, 0, 0.28), 0.14, Ms, (1.2, 1.0, 0.7), segs=8)
    sph("T", (-0.02, 0.02, 0.40), 0.10, Ms, (1.1, 1.0, 0.7), segs=8)
    parent_all(r)
    return r


def build_rock_mossy():
    Ms = mat("stone", (0.65, 0.62, 0.58), 0.7)
    Mm = mat("moss", (0.35, 0.55, 0.28), 0.65)
    r = root_empty("cozy_rock_mossy_A")
    sph("Rock", (0, 0, 0.15), 0.22, Ms, (1.3, 1.1, 0.75), segs=12)
    sph("Moss1", (0.08, 0.05, 0.22), 0.10, Mm, (1.2, 1.0, 0.5), segs=8)
    sph("Moss2", (-0.06, -0.04, 0.20), 0.08, Mm, (1.1, 1.0, 0.45), segs=8)
    parent_all(r)
    return r


def _tree(module_id, trunk_h, canopy_y, canopy_r, leaf_rgb, blossom=False, fruit=False, pine=False, willow=False):
    Mt = mat("trunk", (0.48, 0.32, 0.20), 0.65)
    Ml = mat("leaf", leaf_rgb, 0.55)
    r = root_empty(module_id)
    cyl("Trunk", (0, 0, trunk_h * 0.5), 0.08 if not pine else 0.10, trunk_h, Mt, 10)
    if pine:
        for i, (z, rad) in enumerate([(0.55, 0.45), (0.95, 0.35), (1.30, 0.22)]):
            cone(f"Tier{i}", (0, 0, z), rad, 0.02, 0.45, Ml, 10)
    elif willow:
        sph("Canopy", (0, 0, canopy_y), canopy_r, Ml, (1.3, 1.3, 0.7), segs=12)
        for i in range(8):
            ang = TAU * i / 8.0
            x, y = 0.35 * math.cos(ang), 0.35 * math.sin(ang)
            cyl(f"Hang{i}", (x, y, canopy_y - 0.25), 0.03, 0.45, Ml, 5)
    else:
        sph("Canopy", (0, 0, canopy_y), canopy_r, Ml, (1.15, 1.15, 0.9), segs=14)
        if blossom:
            Mb = mat("blossom", (0.95, 0.70, 0.82), 0.45)
            for i in range(6):
                ang = TAU * i / 6.0
                sph(f"Bl{i}", (0.25 * math.cos(ang), 0.25 * math.sin(ang), canopy_y + 0.1), 0.08, Mb, segs=6)
        if fruit:
            Mf = mat("fruit", (0.90, 0.25, 0.22), 0.4)
            for i in range(5):
                ang = TAU * i / 5.0
                sph(f"Fr{i}", (0.22 * math.cos(ang), 0.22 * math.sin(ang), canopy_y - 0.15), 0.06, Mf, segs=6)
    parent_all(r)
    return r


def build_tree_fruit():
    return _tree("cozy_tree_fruit_A", 0.85, 1.15, 0.42, (0.32, 0.65, 0.30), fruit=True)


def build_tree_willow():
    return _tree("cozy_tree_willow_A", 0.90, 1.20, 0.48, (0.38, 0.70, 0.40), willow=True)


def build_tree_blossom():
    return _tree("cozy_tree_blossom_A", 0.80, 1.10, 0.40, (0.45, 0.72, 0.42), blossom=True)


def build_tree_pine():
    return _tree("cozy_tree_pine_A", 0.70, 1.0, 0.35, (0.22, 0.48, 0.28), pine=True)


def build_tree_cluster():
    Mt = mat("trunk", (0.48, 0.32, 0.20), 0.65)
    Ml = mat("leaf", (0.35, 0.68, 0.32), 0.55)
    r = root_empty("cozy_tree_cluster_A")
    for i, (x, y, h, cy, cr) in enumerate([
        (-0.25, 0.05, 0.70, 0.95, 0.28),
        (0.22, -0.08, 0.85, 1.15, 0.32),
        (0.05, 0.22, 0.60, 0.85, 0.24),
    ]):
        cyl(f"T{i}", (x, y, h * 0.5), 0.06, h, Mt, 8)
        sph(f"C{i}", (x, y, cy), cr, Ml, segs=10)
    parent_all(r)
    return r


BUILDERS = {
    "cozy_tool_rack_A": build_tool_rack,
    "cozy_crate_small_A": build_crate,
    "cozy_barrel_A": build_barrel,
    "cozy_bench_A": build_bench,
    "cozy_cart_A": build_cart,
    "cozy_signpost_A": build_signpost,
    "cozy_flower_bed_B": build_flower_bed,
    "cozy_bush_round_A": build_bush,
    "cozy_crop_row_A": build_crop_row,
    "cozy_scarecrow_A": build_scarecrow,
    "cozy_water_pump_A": build_pump,
    "cozy_birdbath_A": build_birdbath,
    "cozy_grass_tuft_A": build_grass,
    "cozy_rock_cluster_A": build_rock_cluster,
    "cozy_tree_fruit_A": build_tree_fruit,
    "cozy_rock_stacked_A": build_rock_stacked,
    "cozy_tree_willow_A": build_tree_willow,
    "cozy_tree_blossom_A": build_tree_blossom,
    "cozy_rock_mossy_A": build_rock_mossy,
    "cozy_tree_pine_A": build_tree_pine,
    "cozy_tree_cluster_A": build_tree_cluster,
}


def update_catalog(results: list[dict]) -> None:
    cat = json.loads(CAT.read_text(encoding="utf-8"))
    by_id = {m.get("module_id"): m for m in cat.get("modules", [])}
    for r in results:
        mid = r["module_id"]
        entry = {
            "module_id": mid,
            "glb": f"res://assets/p1e_cozy/modules/{mid}.glb",
            "glb_sha256": r["sha256"],
            "bytes": r["bytes"],
            "source": JOB,
            "visual": "soft_clay_prop_v1",
            "mockup_ssot": mid,
        }
        by_id[mid] = entry
    cat["modules"] = list(by_id.values())
    cat["props_missing_21_v1"] = {
        "job": JOB,
        "count": len(results),
        "accepted": False,
        "self_accept": False,
    }
    cat["accepted"] = False
    cat["self_accept"] = False
    CAT.write_text(json.dumps(cat, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    log(f"start props={len(PROPS)}")
    results = []
    for mid in PROPS:
        clear()
        fn = BUILDERS[mid]
        log(f"build {mid}")
        fn()
        info = export_module(mid)
        results.append(info)
        log(f"  ok bytes={info['bytes']} sha={info['sha256'][:12]}")
    update_catalog(results)
    receipt = {
        "schema_version": "props_missing/1.0",
        "receipt_id": "PROPS_MISSING_21_V1",
        "job": JOB,
        "work_order": "WO-TOWN-GRID-IMPORT-001",
        "accepted": False,
        "self_accept": False,
        "purple": "WAITING",
        "count": len(results),
        "objects": results,
        "matching_100_pct_count": 0,
        "note": "Real GLBs authored; fidelity scoring vs mockup SSOT pending headed QA (not claimed 100%).",
        "next": ["headed QA plot inventory real_glb props", "fidelity pass per prop if needed"],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"PASS count={len(results)} receipt={RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

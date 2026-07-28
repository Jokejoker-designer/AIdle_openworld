# -*- coding: utf-8 -*-
"""PROPS_FIDELITY_V2 — path / pond / tree / flower / rock toward MOCKUP_SSOT.

Scoped to WO-TOWN-GRID-IMPORT-001 real-GLB PARTIAL props only.
Does not touch house (V19 separate) or cast (per-card scripts separate).
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy

JOB = "PROPS_FIDELITY_V2"
GAME_MOD = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules")
CAT = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
QUAR.mkdir(parents=True, exist_ok=True)


def log(m):
    print(f"[{JOB}] {m}")


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(n, rgb, rough=0.55, emit=0.0, alpha=1.0):
    m = bpy.data.materials.new(n)
    m.use_nodes = True
    m.diffuse_color = (*rgb, alpha)
    b = next((x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED"), None)
    if b:
        b.inputs["Base Color"].default_value = (*rgb, alpha)
        if "Roughness" in b.inputs:
            b.inputs["Roughness"].default_value = rough
        if emit > 0:
            if "Emission Color" in b.inputs:
                b.inputs["Emission Color"].default_value = (*rgb, 1.0)
            if "Emission Strength" in b.inputs:
                b.inputs["Emission Strength"].default_value = emit
        if alpha < 1.0:
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


def cube(n, loc, sc, m):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = n
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    setm(o, m)
    return o


def sph(n, loc, r, m, sc=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=14, ring_count=10)
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


def parent_all(root):
    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            mw = o.matrix_world.copy()
            o.parent = root
            o.matrix_world = mw


def export_and_promote(module_id: str, visual: str):
    q = QUAR / f"{module_id}.glb"
    dest = GAME_MOD / f"{module_id}.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(q),
        export_format="GLB",
        use_selection=False,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        export_materials="EXPORT",
    )
    dest.write_bytes(q.read_bytes())
    dig = sha(dest)
    data = json.loads(CAT.read_text(encoding="utf-8"))
    for m in data.get("modules", []):
        if m.get("module_id") == module_id:
            m["glb_sha256"] = dig
            m["bytes"] = dest.stat().st_size
            m["source"] = JOB
            m["visual"] = visual
    CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"{module_id} sha={dig[:16]} bytes={dest.stat().st_size}")
    return dig


def build_path_stone():
    """SSOT: irregular stepping stones with warm cream/taupe + moss dots."""
    clear()
    Ms1 = mat("M_stone1", (0.90, 0.86, 0.78), 0.72)
    Ms2 = mat("M_stone2", (0.78, 0.74, 0.66), 0.74)
    Ms3 = mat("M_stone3", (0.94, 0.90, 0.84), 0.70)
    Mmoss = mat("M_moss", (0.42, 0.68, 0.38), 0.6)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_path_stone_A"
    mats = [Ms1, Ms2, Ms3]
    stones = [
        (0.0, 0.0, 0.26), (0.32, 0.14, 0.20), (-0.30, 0.18, 0.19),
        (0.18, -0.28, 0.18), (-0.18, -0.26, 0.17), (0.42, -0.12, 0.15),
        (-0.40, -0.08, 0.16), (0.08, 0.30, 0.14),
    ]
    for i, (x, y, s) in enumerate(stones):
        sph(f"S{i}", (x, y, 0.035), s, mats[i % 3], (1.45, 1.25, 0.32))
        if i % 3 == 0:
            sph(f"Moss{i}", (x + 0.04, y + 0.03, 0.06), 0.04, Mmoss, (1.2, 1.0, 0.3))
    parent_all(root)
    return export_and_promote("cozy_path_stone_A", "mockup_path_v2")


def build_pond():
    """SSOT: rounded pond, ring stones, lily pads, soft cyan water."""
    clear()
    Mw = mat("M_water", (0.22, 0.55, 0.85), 0.15, emit=0.9)
    Ms = mat("M_stone", (0.55, 0.50, 0.44), 0.72)
    Ms2 = mat("M_stone2", (0.64, 0.60, 0.54), 0.75)
    Mg = mat("M_lily", (0.40, 0.72, 0.38), 0.55)
    Mfl = mat("M_lilyfl", (0.95, 0.55, 0.70), 0.5)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_pond_small_A"
    sph("Water", (0, 0, 0.04), 0.58, Mw, (1.55, 1.35, 0.18))
    # deeper pool hint
    sph("WaterDeep", (0, 0, 0.02), 0.45, mat("M_water2", (0.28, 0.55, 0.78), 0.25, emit=0.3), (1.3, 1.15, 0.12))
    for i in range(10):
        ang = i * math.pi / 5
        r = 0.58 + 0.04 * (i % 2)
        sph(f"Rock{i}", (r * math.cos(ang), r * 0.9 * math.sin(ang), 0.05),
            0.11 + 0.02 * (i % 3), Ms if i % 2 == 0 else Ms2, (1.25, 1.05, 0.45))
    sph("Lily1", (0.12, -0.08, 0.09), 0.12, Mg, (1.6, 1.6, 0.18))
    sph("Lily2", (-0.18, 0.12, 0.09), 0.09, Mg, (1.5, 1.5, 0.16))
    sph("LilyFl", (0.12, -0.08, 0.12), 0.04, Mfl)
    parent_all(root)
    return export_and_promote("cozy_pond_small_A", "mockup_pond_v2")


def build_tree():
    """SSOT landmark: thick trunk, multi-lobe canopy, roots."""
    clear()
    Mt = mat("M_trunk", (0.52, 0.34, 0.22), 0.7)
    Ml = mat("M_leaf", (0.38, 0.72, 0.36), 0.55)
    Ml2 = mat("M_leaf2", (0.52, 0.82, 0.42), 0.55)
    Ml3 = mat("M_leaf3", (0.30, 0.62, 0.28), 0.55)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_tree_landmark_A"
    cyl("Trunk", (0, 0, 0.40), 0.14, 0.80, Mt, verts=12)
    cyl("TrunkTop", (0, 0, 0.85), 0.10, 0.30, Mt, verts=10)
    # roots
    for i, a in enumerate([0, 2.1, 4.2]):
        cyl(f"Root{i}", (0.12 * math.cos(a), 0.12 * math.sin(a), 0.06), 0.05, 0.18, Mt, verts=8)
    sph("Canopy", (0, 0, 1.25), 0.62, Ml, (1.35, 1.35, 1.05))
    sph("Canopy2", (0.28, 0.12, 1.40), 0.42, Ml2)
    sph("Canopy3", (-0.22, -0.14, 1.45), 0.38, Ml3)
    sph("Canopy4", (0.05, 0.28, 1.55), 0.30, Ml2)
    sph("Canopy5", (-0.10, 0.05, 1.70), 0.28, Ml)
    parent_all(root)
    return export_and_promote("cozy_tree_landmark_A", "mockup_tree_v2")


def build_flower():
    """SSOT: multi-pot cluster with lavender/pink/yellow blooms."""
    clear()
    Mp = mat("M_pot", (0.90, 0.55, 0.32), 0.55)
    Ml = mat("M_lav", (0.70, 0.42, 0.90), 0.5)
    Mpink = mat("M_pink", (0.95, 0.52, 0.68), 0.5)
    My = mat("M_yel", (1.0, 0.82, 0.30), 0.5)
    Mg = mat("M_stem", (0.32, 0.58, 0.28), 0.6)
    Msoil = mat("M_soil", (0.42, 0.30, 0.20), 0.8)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_flower_cluster_A"
    pots = [(0, 0), (0.24, 0.12), (-0.22, 0.14), (0.14, -0.22), (-0.16, -0.18), (0.32, -0.10)]
    blooms = [Ml, Mpink, My]
    for i, (x, y) in enumerate(pots):
        cyl(f"Pot{i}", (x, y, 0.09), 0.08, 0.14, Mp)
        sph(f"Soil{i}", (x, y, 0.15), 0.07, Msoil, (1, 1, 0.4))
        for j in range(5):
            a = j * 1.25
            sx = x + 0.035 * math.cos(a)
            sy = y + 0.035 * math.sin(a)
            h = 0.18 + 0.04 * (j % 3)
            cyl(f"St{i}_{j}", (sx, sy, 0.18 + h * 0.3), 0.012, h, Mg)
            sph(f"Fl{i}_{j}", (sx, sy, 0.22 + h), 0.045 + 0.01 * (j % 2), blooms[(i + j) % 3], (0.8, 0.8, 1.3))
    parent_all(root)
    return export_and_promote("cozy_flower_cluster_A", "mockup_flower_v2")


def build_rock():
    """SSOT: multi-boulder cluster with moss and size variety."""
    clear()
    Ms = mat("M_stone", (0.68, 0.66, 0.60), 0.75)
    Ms2 = mat("M_stone2", (0.58, 0.56, 0.50), 0.78)
    Ms3 = mat("M_stone3", (0.76, 0.74, 0.68), 0.72)
    Mm = mat("M_moss", (0.40, 0.65, 0.36), 0.6)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_rock_small_A"
    sph("R1", (0, 0, 0.14), 0.26, Ms, (1.4, 1.15, 0.9))
    sph("R2", (0.18, 0.10, 0.10), 0.15, Ms2, (1.25, 1.05, 0.75))
    sph("R3", (-0.16, 0.08, 0.08), 0.12, Ms3, (1.2, 1.0, 0.7))
    sph("R4", (0.05, -0.16, 0.07), 0.10, Ms2, (1.15, 1.0, 0.65))
    sph("Moss1", (0.05, 0.04, 0.28), 0.06, Mm, (1.3, 1.0, 0.4))
    sph("Moss2", (-0.08, -0.02, 0.22), 0.04, Mm, (1.2, 0.9, 0.35))
    parent_all(root)
    return export_and_promote("cozy_rock_small_A", "mockup_rock_v2")


def main():
    log("start")
    results = {}
    for name, fn in [
        ("path", build_path_stone),
        ("pond", build_pond),
        ("tree", build_tree),
        ("flower", build_flower),
        ("rock", build_rock),
    ]:
        try:
            dig = fn()
            results[name] = {"ok": True, "sha": dig[:16]}
        except Exception as e:
            log(f"FAIL {name}: {e}")
            results[name] = {"ok": False, "error": str(e)}
    log(f"DONE {results}")
    (QUAR / "summary.json").write_text(json.dumps({"job": JOB, "results": results, "accepted": False}, indent=2), encoding="utf-8")
    return 0 if all(r.get("ok") for r in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

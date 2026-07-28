# -*- coding: utf-8 -*-
"""PROPS_POND_ROCK_V3 — pond ring stones + lily volume; rock multi-boulder."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy

JOB = "PROPS_POND_ROCK_V3"
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


def mat(n, rgb, rough=0.55, emit=0.0):
    m = bpy.data.materials.new(n)
    m.use_nodes = True
    m.diffuse_color = (*rgb, 1.0)
    b = next((x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED"), None)
    if b:
        b.inputs["Base Color"].default_value = (*rgb, 1.0)
        if "Roughness" in b.inputs:
            b.inputs["Roughness"].default_value = rough
        if emit > 0:
            if "Emission Color" in b.inputs:
                b.inputs["Emission Color"].default_value = (*rgb, 1.0)
            if "Emission Strength" in b.inputs:
                b.inputs["Emission Strength"].default_value = emit
    return m


def setm(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)
    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass


def sph(n, loc, r, m, sc=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=14, ring_count=10)
    o = bpy.context.active_object
    o.name = n
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    setm(o, m)
    return o


def parent_all(root):
    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            mw = o.matrix_world.copy()
            o.parent = root
            o.matrix_world = mw


def promote(module_id, visual):
    q = QUAR / f"{module_id}.glb"
    dest = GAME_MOD / f"{module_id}.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(q), export_format="GLB", use_selection=False,
        export_apply=True, export_cameras=False, export_lights=False, export_materials="EXPORT",
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


def build_pond():
    clear()
    Mw = mat("M_water", (0.18, 0.48, 0.82), 0.12, emit=1.1)
    Mw2 = mat("M_water2", (0.12, 0.38, 0.70), 0.2, emit=0.5)
    Ms = mat("M_stone", (0.52, 0.48, 0.42), 0.72)
    Ms2 = mat("M_stone2", (0.42, 0.40, 0.36), 0.75)
    Ms3 = mat("M_stone3", (0.60, 0.56, 0.50), 0.7)
    Mg = mat("M_lily", (0.32, 0.68, 0.30), 0.55)
    Mg2 = mat("M_lily2", (0.40, 0.75, 0.35), 0.55)
    Mfl = mat("M_lilyfl", (0.95, 0.50, 0.68), 0.5)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_pond_small_A"
    sph("Water", (0, 0, 0.04), 0.62, Mw, (1.6, 1.4, 0.16))
    sph("WaterDeep", (0, 0, 0.02), 0.48, Mw2, (1.35, 1.2, 0.12))
    # Elevated ring stones (sit ON rim, not sunk into water plane)
    for i in range(12):
        ang = i * math.pi / 6
        r = 0.68 + 0.05 * (i % 3)
        elev = 0.10 + 0.03 * (i % 2)
        rs = 0.13 + 0.03 * (i % 3)
        m = [Ms, Ms2, Ms3][i % 3]
        sph(f"Rock{i}", (r * math.cos(ang), r * 0.92 * math.sin(ang), elev),
            rs, m, (1.3, 1.1, 0.75))
    # Lily volume: pads + stems + flowers
    for i, (x, y, s) in enumerate([(0.15, -0.12, 0.16), (-0.20, 0.14, 0.13), (0.05, 0.18, 0.11), (-0.08, -0.20, 0.12)]):
        sph(f"Lily{i}", (x, y, 0.10), s, Mg if i % 2 == 0 else Mg2, (1.7, 1.7, 0.22))
        sph(f"LilyStem{i}", (x, y, 0.06), 0.02, Mg, (1, 1, 1.5))
    sph("LilyFl1", (0.15, -0.12, 0.14), 0.05, Mfl)
    sph("LilyFl2", (-0.20, 0.14, 0.13), 0.04, Mfl)
    parent_all(root)
    return promote("cozy_pond_small_A", "mockup_pond_v3")


def build_rock():
    clear()
    Ms = mat("M_stone", (0.62, 0.58, 0.52), 0.75)
    Ms2 = mat("M_stone2", (0.50, 0.48, 0.44), 0.78)
    Ms3 = mat("M_stone3", (0.72, 0.68, 0.62), 0.72)
    Mm = mat("M_moss", (0.36, 0.62, 0.32), 0.6)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_rock_small_A"
    # Multi-boulder stack silhouette (SSOT cluster)
    sph("RMain", (0.0, 0.0, 0.18), 0.28, Ms, (1.45, 1.2, 1.0))
    sph("R2", (0.22, 0.12, 0.14), 0.18, Ms2, (1.3, 1.1, 0.9))
    sph("R3", (-0.20, 0.10, 0.12), 0.16, Ms3, (1.25, 1.05, 0.85))
    sph("R4", (0.08, -0.20, 0.10), 0.14, Ms2, (1.2, 1.0, 0.8))
    sph("R5", (-0.12, -0.14, 0.08), 0.11, Ms, (1.15, 1.0, 0.75))
    sph("R6", (0.18, -0.05, 0.28), 0.12, Ms3, (1.1, 1.0, 0.9))  # stacked top
    sph("R7", (-0.05, 0.08, 0.32), 0.10, Ms2, (1.15, 1.05, 0.85))
    sph("Moss1", (0.06, 0.05, 0.38), 0.07, Mm, (1.4, 1.1, 0.45))
    sph("Moss2", (-0.10, -0.04, 0.28), 0.05, Mm, (1.3, 1.0, 0.4))
    sph("Moss3", (0.20, 0.10, 0.22), 0.04, Mm, (1.2, 0.9, 0.35))
    parent_all(root)
    return promote("cozy_rock_small_A", "mockup_rock_v3")


def main():
    log("start")
    build_pond()
    build_rock()
    log("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# -*- coding: utf-8 -*-
"""cozy_garden_lamp_A V2 — cream cyber lantern matching prop_garden_lamp.jpg."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy

JOB = "LAMP_FIDELITY_V2"
MODULE = "cozy_garden_lamp_A"
GAME = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules") / f"{MODULE}.glb"
CAT = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


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


def cube(n, loc, sc, m):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = n
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    setm(o, m)
    return o


def sph(n, loc, r, m, sc=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=12, ring_count=8)
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


bpy.ops.wm.read_factory_settings(use_empty=True)
Mcream = mat("M_post", (0.94, 0.88, 0.76), 0.5)
Mstone = mat("M_base", (0.55, 0.58, 0.55), 0.7)
Memit = mat("M_emit", (1.0, 0.82, 0.40), 0.3, emit=5.0)
Mleaf = mat("M_leaf", (0.50, 0.78, 0.50), 0.55)
Mvine = mat("M_vine", (0.42, 0.68, 0.45), 0.6)
Mc = mat("M_cyan", (0.40, 0.85, 0.95), 0.4, emit=0.5)
Mgrass = mat("M_grass", (0.38, 0.65, 0.36), 0.65)
Mlantern = mat("M_lantern", (0.92, 0.86, 0.74), 0.45)

cube("Base", (0, 0, 0.04), (0.58, 0.58, 0.08), Mstone)
cube("Grass", (0, 0, 0.07), (0.52, 0.52, 0.04), Mgrass)
# taper post via stacked cylinders
cyl("PostLow", (0, 0, 0.35), 0.10, 0.50, Mcream, 10)
cyl("PostMid", (0, 0, 0.75), 0.08, 0.55, Mcream, 10)
cyl("PostTop", (0, 0, 1.15), 0.07, 0.40, Mcream, 10)
cube("Collar1", (0, 0, 0.55), (0.20, 0.20, 0.10), Mcream)
cube("Collar2", (0, 0, 1.05), (0.18, 0.18, 0.10), Mcream)
cube("Cap", (0, 0, 1.38), (0.16, 0.16, 0.10), Mcream)
# arm toward +X
cube("Arm", (0.28, 0, 1.32), (0.50, 0.06, 0.06), Mcream)
sph("Scroll", (0.18, 0.10, 1.38), 0.07, Mcream, (1.3, 0.7, 0.6))
# hanging lantern
cube("LanternBox", (0.50, 0, 1.10), (0.24, 0.24, 0.32), Mlantern)
sph("Glow", (0.50, 0, 1.10), 0.11, Memit)
# cyan circuit lines
cube("Cyan1", (0.0, 0.09, 0.45), (0.025, 0.025, 0.28), Mc)
cube("Cyan2", (0.0, -0.09, 0.80), (0.025, 0.025, 0.22), Mc)
# ivy leaves
for i, z in enumerate([0.40, 0.55, 0.70, 0.90, 1.05]):
    sph(f"Leaf{i}", (0.11 + 0.01 * i, 0.09, z), 0.045, Mleaf, (1.3, 0.7, 0.5))
    cyl(f"Vine{i}", (0.09, 0.07, z - 0.04), 0.012, 0.10, Mvine)

bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
root = bpy.context.active_object
root.name = f"MOD_{MODULE}"
for o in list(bpy.data.objects):
    if o != root and o.type == "MESH" and o.parent is None:
        mw = o.matrix_world.copy()
        o.parent = root
        o.matrix_world = mw

bpy.ops.export_scene.gltf(
    filepath=str(GAME),
    export_format="GLB",
    use_selection=False,
    export_apply=True,
    export_cameras=False,
    export_lights=False,
    export_materials="EXPORT",
)
dig = sha(GAME)
data = json.loads(CAT.read_text(encoding="utf-8"))
for m in data.get("modules", []):
    if m.get("module_id") == MODULE:
        m["glb_sha256"] = dig
        m["bytes"] = GAME.stat().st_size
        m["source"] = JOB
        m["visual"] = "mockup_lamp_v2"
CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"LAMP_V2 {GAME.stat().st_size} {dig[:16]}")

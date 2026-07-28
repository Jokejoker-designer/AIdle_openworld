# -*- coding: utf-8 -*-
"""GREENHOUSE_SSOT_V3 — true transparent cyan glass + dense interior plants.

In-game was cream-opaque. SSOT prop_greenhouse.jpg: light wood frame, clear glass
panes, A-frame roof, lush interior pots/vines/glow mushrooms.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy

JOB = "GREENHOUSE_SSOT_V3"
MODULE = "cozy_greenhouse_A"
GAME = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules") / f"{MODULE}.glb"
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
            # lower transmission-ish via low roughness + tint
            if "Specular" in b.inputs:
                b.inputs["Specular"].default_value = 0.6
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


def sph(n, loc, r, m, sc=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=12, ring_count=8)
    o = bpy.context.active_object
    o.name = n
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    setm(o, m)
    return o


def cyl(n, loc, r, d, m, verts=10):
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


def build():
    clear()
    # Light cream wood frame (SSOT)
    Mf = mat("M_frame", (0.96, 0.90, 0.78), 0.48)
    # TRUE cyan glass — low alpha, cyan tint, mild emit so it reads through cream boost
    Mg = mat("M_glass", (0.35, 0.72, 0.92), 0.08, emit=0.55, alpha=0.35)
    Mb = mat("M_base", (0.96, 0.92, 0.84), 0.6)
    Md = mat("M_door", (0.94, 0.86, 0.72), 0.5)
    Me = mat("M_emit", (1.0, 0.75, 0.40), 0.3, emit=3.5)
    Me2 = mat("M_emit2", (1.0, 0.55, 0.75), 0.3, emit=2.5)
    Mp = mat("M_pot", (0.88, 0.52, 0.32), 0.55)
    Mleaf = mat("M_leaf", (0.32, 0.70, 0.30), 0.55)
    Mleaf2 = mat("M_leaf2", (0.45, 0.80, 0.40), 0.55)
    Mpur = mat("M_flower", (0.85, 0.45, 0.80), 0.5)
    Mpink = mat("M_pink", (0.95, 0.55, 0.70), 0.5)
    Mteal = mat("M_teal", (0.30, 0.75, 0.70), 0.55)
    Mgold = mat("M_gold", (0.95, 0.82, 0.30), 0.35, emit=0.3)

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = f"MOD_{MODULE}"

    # Base pad
    cube("Base", (0, 0, 0.04), (2.15, 1.70, 0.08), Mb, 0.08)

    # Corner posts
    for i, (x, y) in enumerate([(-0.85, 0.70), (0.85, 0.70), (-0.85, -0.70), (0.85, -0.70)]):
        cyl(f"Post{i}", (x, y, 0.55), 0.045, 1.0, Mf, verts=8)

    # Frame beams (walls) — thin wood, glass fills the rest
    # Front/back horizontal rails
    for z in [0.15, 0.55, 0.95]:
        cube(f"RailF{z}", (0, 0.72, z), (1.75, 0.06, 0.05), Mf, 0.01)
        cube(f"RailB{z}", (0, -0.72, z), (1.75, 0.06, 0.05), Mf, 0.01)
    for z in [0.15, 0.55, 0.95]:
        cube(f"RailL{z}", (-0.88, 0, z), (0.06, 1.40, 0.05), Mf, 0.01)
        cube(f"RailR{z}", (0.88, 0, z), (0.06, 1.40, 0.05), Mf, 0.01)
    # Vertical muntins
    for x in [-0.45, 0.0, 0.45]:
        cube(f"MunF{x}", (x, 0.72, 0.55), (0.05, 0.05, 0.85), Mf, 0.01)
        cube(f"MunB{x}", (x, -0.72, 0.55), (0.05, 0.05, 0.85), Mf, 0.01)
    for y in [-0.35, 0.35]:
        cube(f"MunL{y}", (-0.88, y, 0.55), (0.05, 0.05, 0.85), Mf, 0.01)
        cube(f"MunR{y}", (0.88, y, 0.55), (0.05, 0.05, 0.85), Mf, 0.01)

    # GLASS PANES (thin, cyan, transparent) — named M_glass for loader boost
    for nm, loc, sc in [
        ("GlassF1", (-0.42, 0.74, 0.55), (0.38, 0.02, 0.75)),
        ("GlassF2", (0.0, 0.74, 0.55), (0.38, 0.02, 0.75)),
        ("GlassF3", (0.42, 0.74, 0.55), (0.38, 0.02, 0.75)),
        ("GlassB1", (-0.42, -0.74, 0.55), (0.38, 0.02, 0.75)),
        ("GlassB2", (0.0, -0.74, 0.55), (0.38, 0.02, 0.75)),
        ("GlassB3", (0.42, -0.74, 0.55), (0.38, 0.02, 0.75)),
        ("GlassL1", (-0.90, -0.35, 0.55), (0.02, 0.32, 0.75)),
        ("GlassL2", (-0.90, 0.35, 0.55), (0.02, 0.32, 0.75)),
        ("GlassR1", (0.90, -0.35, 0.55), (0.02, 0.32, 0.75)),
        ("GlassR2", (0.90, 0.35, 0.55), (0.02, 0.32, 0.75)),
    ]:
        cube(nm, loc, sc, Mg, 0.0)

    # A-frame roof: wood ridge + rafters + glass (no object rotation)
    # Peak prism via verts
    mesh = bpy.data.meshes.new("RoofFrame")
    verts = [
        (-0.95, 0.75, 1.05), (0.95, 0.75, 1.05),
        (-0.95, -0.75, 1.05), (0.95, -0.75, 1.05),
        (-0.95, 0.0, 1.75), (0.95, 0.0, 1.75),
    ]
    # only edges as thin boxes instead
    cube("Ridge", (0, 0, 1.72), (1.95, 0.08, 0.08), Mf, 0.01)
    # roof glass panels (flat, stepped for slope approximation)
    cube("RoofGlassF", (0, 0.35, 1.40), (1.80, 0.55, 0.025), Mg, 0.0)
    cube("RoofGlassB", (0, -0.35, 1.40), (1.80, 0.55, 0.025), Mg, 0.0)
    # roof frame rails
    cube("RoofRailF", (0, 0.38, 1.42), (1.90, 0.05, 0.05), Mf, 0.01)
    cube("RoofRailB", (0, -0.38, 1.42), (1.90, 0.05, 0.05), Mf, 0.01)
    for x in [-0.45, 0.0, 0.45]:
        cube(f"RoofMunF{x}", (x, 0.36, 1.40), (0.04, 0.50, 0.04), Mf, 0.01)
        cube(f"RoofMunB{x}", (x, -0.36, 1.40), (0.04, 0.50, 0.04), Mf, 0.01)
    # eaves
    cube("EaveF", (0, 0.78, 1.08), (2.0, 0.08, 0.06), Mf, 0.02)
    cube("EaveB", (0, -0.78, 1.08), (2.0, 0.08, 0.06), Mf, 0.02)

    # Door (wood, front)
    cube("Door", (0, 0.78, 0.40), (0.40, 0.05, 0.65), Md, 0.03)
    cube("DoorF", (0, 0.80, 0.40), (0.44, 0.03, 0.70), Mf, 0.02)
    sph("Knob", (0.12, 0.84, 0.40), 0.04, Mgold)

    # Interior floor
    cube("Floor", (0, 0, 0.10), (1.70, 1.30, 0.04), Mb, 0.02)

    # Dense interior plants (SSOT lush)
    pots = [
        (-0.50, 0.30), (-0.20, 0.35), (0.15, 0.28), (0.50, 0.32),
        (-0.45, -0.10), (0.0, -0.15), (0.40, -0.12),
        (-0.35, -0.40), (0.10, -0.38), (0.45, -0.35),
        (-0.15, 0.05), (0.25, 0.05),
    ]
    for i, (x, y) in enumerate(pots):
        cyl(f"Pot{i}", (x, y, 0.18), 0.08 + 0.01 * (i % 3), 0.14, Mp)
        h = 0.18 + 0.08 * (i % 4)
        sph(f"Plant{i}", (x, y, 0.32 + h * 0.4), 0.12 + 0.03 * (i % 3),
            [Mleaf, Mleaf2, Mteal, Mpur][i % 4])
        if i % 3 == 0:
            sph(f"Bloom{i}", (x + 0.04, y, 0.45 + h * 0.3), 0.06, Mpink if i % 2 else Mpur)

    # Glow mushrooms (SSOT)
    for i, (x, y, h) in enumerate([(-0.25, 0.15, 0.35), (0.30, -0.20, 0.32), (0.05, 0.20, 0.40)]):
        cyl(f"MushS{i}", (x, y, h * 0.5), 0.03, h * 0.6, mat(f"M_stem{i}", (0.95, 0.90, 0.80), 0.5))
        sph(f"MushC{i}", (x, y, h), 0.10, Me if i != 1 else Me2, (1.2, 1.2, 0.7))

    # Tall vine on back wall
    for i, z in enumerate([0.30, 0.50, 0.70, 0.90, 1.10]):
        sph(f"Vine{i}", (-0.55, -0.50, z), 0.08, Mleaf2 if i % 2 else Mleaf)
    # Ambient warm glow
    sph("Glow", (0, 0, 0.70), 0.35, Me)

    parent_all(root)


def export():
    q = QUAR / f"{MODULE}.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(q), export_format="GLB", use_selection=False,
        export_apply=True, export_cameras=False, export_lights=False, export_materials="EXPORT",
    )
    GAME.write_bytes(q.read_bytes())
    dig = sha(GAME)
    data = json.loads(CAT.read_text(encoding="utf-8"))
    for m in data.get("modules", []):
        if m.get("module_id") == MODULE:
            m["glb_sha256"] = dig
            m["bytes"] = GAME.stat().st_size
            m["source"] = JOB
            m["visual"] = "mockup_greenhouse_v3"
        if m.get("module_id") == "cozy_greenhouse_preview_anchor_A":
            m["glb_sha256"] = dig
            m["bytes"] = GAME.stat().st_size
            m["source"] = JOB
    CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # alias
    (GAME.parent / "cozy_greenhouse_preview_anchor_A.glb").write_bytes(GAME.read_bytes())
    log(f"promoted sha={dig[:16]} bytes={GAME.stat().st_size}")
    return dig


def main():
    log("start")
    build()
    dig = export()
    log(f"DONE sha={dig[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

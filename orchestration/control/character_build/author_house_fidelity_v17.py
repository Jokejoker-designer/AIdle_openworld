# -*- coding: utf-8 -*-
"""HOUSE_FIDELITY_V17 — SSOT-closer clay fish-scale + front door prominence.

Builds on V14–V16 (roof_prism, no object rotation). Gaps vs prop_house_small.jpg:
  - tiles need larger clay-scallop coins with peach/cream/yellow row alternation
  - front arched door + steps more prominent from freecam
  - side window with curtains + interior glow already OK
  - rounded cream body + lilac pad + chimney smoke already OK
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

JOB = "HOUSE_FIDELITY_V17"
MODULE = "cozy_house_small_A"
GAME = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules") / f"{MODULE}.glb"
CAT = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
RENDER = Path(
    r"E:\AIdle_openworld\orchestration\control\visual_reference\mockup_cast_props_001\gen"
)
QUAR.mkdir(parents=True, exist_ok=True)
RENDER.mkdir(parents=True, exist_ok=True)


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


def mat(name, rgb, rough=0.55, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*rgb, 1.0)
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = rough
        if emit > 0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (*rgb, 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emit
    return m


def setm(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)
    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass


def cube(name, loc, sc, m, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
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


def sph(name, loc, r, m, sc=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=12, ring_count=8)
    o = bpy.context.active_object
    o.name = name
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    setm(o, m)
    return o


def cyl(name, loc, r, d, m):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=12)
    o = bpy.context.active_object
    o.name = name
    setm(o, m)
    return o


def roof_prism(name, m):
    """Triangular prism roof — verts only, no object rotation (Godot-safe)."""
    mesh = bpy.data.meshes.new(name)
    verts = [
        (-0.95, 0.80, 1.08),
        (0.95, 0.80, 1.08),
        (-0.95, -0.80, 1.08),
        (0.95, -0.80, 1.08),
        (-0.95, 0.00, 1.98),
        (0.95, 0.00, 1.98),
    ]
    faces = [
        (0, 1, 5, 4),
        (2, 4, 5, 3),
        (0, 4, 2),
        (1, 3, 5),
        (0, 2, 3, 1),
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    setm(o, m)
    return o


def clay_scallop(name, u, t, front, m, row):
    """Larger clay fish-scale coin on slope — translation only (no rotation)."""
    if front:
        y = 0.80 * (1 - t) + 0.0 * t
        # Lift slightly off prism so scallops read as 3D tiles
        lift = 0.09
    else:
        y = -0.80 * (1 - t) + 0.0 * t
        lift = 0.09
    z = 1.08 * (1 - t) + 1.98 * t + lift
    x = u * 0.84
    # Larger overlapping scallops (SSOT clay fish-scale)
    r = 0.125 if row % 2 == 0 else 0.118
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, z), segments=12, ring_count=8)
    o = bpy.context.active_object
    o.name = name
    # Flatten into tile-coin; thicker than v16 for clay read
    o.scale = (1.55, 1.35, 0.42)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    setm(o, m)
    return o


def build():
    clear()
    # SSOT palette: cream walls, lilac pad, peach/yellow/cream roof tiles
    Mw = mat("M_wall", (0.97, 0.90, 0.80), 0.72)
    Mb = mat("M_base", (0.70, 0.52, 0.92), 0.62)
    # Alternating clay fish-scale colors (peach / yellow / cream)
    Mr1 = mat("M_roof_a", (1.0, 0.72, 0.42), 0.48)   # peach
    Mr2 = mat("M_roof_b", (1.0, 0.88, 0.38), 0.45)   # yellow
    Mr3 = mat("M_roof_c", (0.98, 0.90, 0.72), 0.50)  # cream
    Mr = mat("M_ridge", (0.99, 0.94, 0.84), 0.55)
    Md = mat("M_door", (0.72, 0.42, 0.22), 0.5)
    Mf = mat("M_frame", (0.92, 0.68, 0.48), 0.5)
    Me = mat("M_emit", (1.0, 0.78, 0.30), 0.3, emit=5.0)
    Me2 = mat("M_emit2", (1.0, 0.90, 0.50), 0.3, emit=3.5)
    Mp = mat("M_pot", (0.90, 0.55, 0.32), 0.55)
    Ml = mat("M_lav", (0.70, 0.42, 0.90), 0.55)
    Mleaf = mat("M_leaf", (0.35, 0.72, 0.32), 0.55)
    Mstem = mat("M_stem", (0.32, 0.50, 0.28), 0.6)
    Mmail = mat("M_mail", (0.68, 0.42, 0.90), 0.4)
    Ms = mat("M_stone", (0.84, 0.78, 0.70), 0.7)
    Msmoke = mat("M_smoke", (0.78, 0.55, 0.92), 1.0, emit=0.25)
    Mchim = mat("M_chim", (0.98, 0.92, 0.86), 0.65)
    Mdark = mat("M_dark", (0.30, 0.14, 0.10), 0.8)
    Mcurt = mat("M_curt", (0.78, 0.42, 0.88), 0.6)
    Mknob = mat("M_knob", (1.0, 0.88, 0.35), 0.25, emit=0.6)

    cube("Base", (0, 0, 0.06), (2.10, 1.90, 0.14), Mb, 0.14)
    # Slightly rounder body
    cube("Body", (0, 0.02, 0.62), (1.36, 1.16, 1.04), Mw, 0.16)
    cube("Front", (0, 0.54, 0.50), (0.98, 0.18, 0.78), Mw, 0.12)

    roof_prism("RoofSolid", Mr)

    # Dense clay fish-scale FRONT (SSOT camera face) — 10x12 staggered
    mats = [Mr1, Mr2, Mr3]
    rows, cols = 10, 12
    for row in range(rows):
        t = (row + 0.28) / rows
        for col in range(cols):
            u = (col - (cols - 1) / 2) / ((cols - 1) / 2)
            if row % 2:
                u += 0.5 / cols * 2  # half-step stagger
            if abs(u) > 1.05:
                continue
            # Row-primary palette for clay bands (peach/yellow/cream)
            clay = mats[row % 3]
            clay_scallop(f"FF{row}_{col}", u, t, True, clay, row)

    # Back slope
    for row in range(6):
        t = (row + 0.35) / 6.0
        for col in range(9):
            u = (col - 4.0) / 4.0
            if row % 2:
                u += 0.08
            if abs(u) > 1.0:
                continue
            clay_scallop(f"BB{row}_{col}", u, t, False, mats[(row + 1) % 3], row)

    # Ridge beads
    for i, x in enumerate([-0.60, -0.30, 0.0, 0.30, 0.60]):
        sph(f"Rd{i}", (x, 0.0, 2.04), 0.10, Mr, (1.25, 1.0, 0.70))

    # Chimney + pixel smoke
    cube("Chim", (0.42, -0.18, 2.08), (0.24, 0.24, 0.46), Mchim, 0.05)
    cube("ChimC", (0.42, -0.18, 2.32), (0.30, 0.30, 0.08), Mchim, 0.03)
    for i, (dx, dy, dz, s) in enumerate(
        [(0, 0, 0.08, 0.08), (0.08, 0.06, 0.20, 0.10), (0.16, 0.12, 0.32, 0.08), (0.26, 0.16, 0.44, 0.06)]
    ):
        sph(f"Sm{i}", (0.42 + dx, -0.18 + dy, 2.36 + dz), s, Msmoke)

    # Front door — more prominent (SSOT arched wood door)
    cube("DFill", (0, 0.52, 0.40), (0.54, 0.14, 0.78), Mw, 0.05)
    cube("DFr", (0, 0.62, 0.44), (0.50, 0.06, 0.82), Mf, 0.05)
    cube("Door", (0, 0.68, 0.44), (0.42, 0.07, 0.72), Md, 0.05)
    # Door planks
    cube("DP1", (0, 0.72, 0.52), (0.36, 0.02, 0.02), Mdark, 0.0)
    cube("DP2", (0, 0.72, 0.36), (0.36, 0.02, 0.02), Mdark, 0.0)
    sph("DArch", (0, 0.68, 0.84), 0.22, Mf, (1.05, 0.32, 0.58))
    sph("Knob", (0.12, 0.74, 0.42), 0.045, Mknob)
    # Steps (peach)
    cube("S1", (0, 0.80, 0.10), (0.42, 0.18, 0.08), Mf, 0.03)
    cube("S2", (0, 0.96, 0.05), (0.34, 0.14, 0.06), Mf, 0.02)
    cube("S3", (0, 1.08, 0.02), (0.26, 0.10, 0.04), Mf, 0.02)

    # Front windows (glow)
    for nm, x, z, rr in [
        ("W1", -0.38, 0.64, 0.095),
        ("W2", 0.38, 0.44, 0.085),
        ("W3", -0.28, 0.96, 0.09),
        ("W4", 0.0, 1.16, 0.10),
    ]:
        sph(f"{nm}g", (x, 0.64, z), rr, Me if nm != "W4" else Me2)
        cyl(f"{nm}f", (x, 0.60, z), rr + 0.022, 0.045, Mf)

    # Side picture window with curtains + interior
    cube("SF", (0.64, 0, 0.66), (0.12, 0.54, 0.44), Mdark, 0.02)
    cube("SFr", (0.68, 0, 0.66), (0.08, 0.58, 0.48), Mf, 0.03)
    cube("SG", (0.72, 0, 0.66), (0.04, 0.48, 0.38), Me, 0.01)
    cube("CL", (0.66, -0.18, 0.70), (0.04, 0.08, 0.34), Mcurt, 0.02)
    cube("CR", (0.66, 0.20, 0.70), (0.04, 0.08, 0.34), Mcurt, 0.02)
    cyl("Lamp", (0.54, 0.10, 0.56), 0.032, 0.09, Mp)
    sph("LampG", (0.54, 0.10, 0.65), 0.065, Me2, (1, 1, 0.75))
    cyl("InPot", (0.54, -0.10, 0.52), 0.038, 0.055, Mp)
    sph("InLeaf", (0.54, -0.10, 0.62), 0.05, Mleaf)

    # Mail + lavender pot + plants + stepping stones
    cyl("MP", (0.30, 0.80, 0.16), 0.024, 0.20, Mmail)
    cube("MB", (0.30, 0.80, 0.30), (0.15, 0.11, 0.12), Mmail, 0.03)
    cube("MFlag", (0.38, 0.80, 0.34), (0.03, 0.02, 0.08), Ml, 0.01)
    cyl("PB", (-0.72, 0.72, 0.16), 0.11, 0.16, Mp)
    for i, a in enumerate([0, 1.2, 2.4, 3.6, 4.8, 5.8]):
        x = -0.72 + 0.045 * math.cos(a)
        y = 0.72 + 0.045 * math.sin(a)
        cyl(f"St{i}", (x, y, 0.32), 0.012, 0.22, Mstem)
        sph(f"Bl{i}", (x, y, 0.48), 0.048, Ml, (0.7, 0.7, 1.35))
    cyl("PS1", (0.50, 0.80, 0.12), 0.055, 0.10, Mp)
    sph("PL1", (0.50, 0.80, 0.24), 0.06, Mleaf)
    cyl("PS2", (0.64, 0.70, 0.11), 0.048, 0.09, Mp)
    sph("PL2", (0.64, 0.70, 0.22), 0.05, Ml)
    for i, (x, y, s) in enumerate([(-0.12, 1.15, 0.13), (0.10, 1.32, 0.11), (-0.04, 1.50, 0.095)]):
        sph(f"Sn{i}", (x, y, 0.03), s, Ms, (1.35, 1.05, 0.22))

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = f"MOD_{MODULE}"
    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            mw = o.matrix_world.copy()
            o.parent = root
            o.matrix_world = mw
    return root


def export():
    q = QUAR / f"{MODULE}.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(q),
        export_format="GLB",
        use_selection=False,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        export_materials="EXPORT",
    )
    GAME.write_bytes(q.read_bytes())
    dig = sha(GAME)
    data = json.loads(CAT.read_text(encoding="utf-8"))
    for m in data.get("modules", []):
        if m.get("module_id") == MODULE:
            m["glb_sha256"] = dig
            m["bytes"] = GAME.stat().st_size
            m["source"] = JOB
            m["visual"] = "mockup_house_v17"
    CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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

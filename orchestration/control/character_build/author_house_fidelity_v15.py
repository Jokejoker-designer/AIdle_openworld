# -*- coding: utf-8 -*-
"""HOUSE_FIDELITY_V15 — dense fish-scale on prism roof (no object rotation).

Builds on V14 gable silhouette. Goal: closer to SSOT bld_01_house.jpg
fish-scale rows (peach/yellow/cream alternating).
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

JOB = "HOUSE_FIDELITY_V15"
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
    # Slightly wider eaves for cozy overhang
    verts = [
        (-0.92, 0.78, 1.10),  # 0 FL eave
        (0.92, 0.78, 1.10),  # 1 FR eave
        (-0.92, -0.78, 1.10),  # 2 BL eave
        (0.92, -0.78, 1.10),  # 3 BR eave
        (-0.92, 0.00, 1.95),  # 4 peak L
        (0.92, 0.00, 1.95),  # 5 peak R
    ]
    faces = [
        (0, 1, 5, 4),  # front slope
        (2, 4, 5, 3),  # back slope
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


def fish_scale(name, u, t, front, m):
    """Place flattened sphere on front (or back) roof slope by translation only.

    Front slope: eave (y=+0.78, z=1.10) → peak (y=0, z=1.95)
    Back slope:  eave (y=-0.78, z=1.10) → peak (y=0, z=1.95)
    u in [-1,1] along X, t in [0,1] eave→peak
    """
    if front:
        y = 0.78 * (1 - t) + 0.0 * t
    else:
        y = -0.78 * (1 - t) + 0.0 * t
    z = 1.10 * (1 - t) + 1.95 * t + 0.07
    x = u * 0.82
    # Flattened sphere = scallop “coin”
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.105, location=(x, y, z), segments=10, ring_count=8)
    o = bpy.context.active_object
    o.name = name
    o.scale = (1.45, 1.25, 0.32)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    setm(o, m)
    return o


def build():
    clear()
    Mw = mat("M_wall", (0.98, 0.88, 0.72), 0.72)
    Mb = mat("M_base", (0.68, 0.50, 0.90), 0.62)
    Mr1 = mat("M_roof_a", (1.0, 0.58, 0.18), 0.45)
    Mr2 = mat("M_roof_b", (1.0, 0.80, 0.22), 0.45)
    Mr3 = mat("M_roof_c", (0.98, 0.68, 0.32), 0.48)
    Mr = mat("M_ridge", (0.99, 0.92, 0.78), 0.55)
    Md = mat("M_door", (0.70, 0.38, 0.16), 0.5)
    Mf = mat("M_frame", (0.90, 0.62, 0.40), 0.5)
    Me = mat("M_emit", (1.0, 0.72, 0.22), 0.3, emit=4.5)
    Me2 = mat("M_emit2", (1.0, 0.88, 0.45), 0.3, emit=3.0)
    Mp = mat("M_pot", (0.88, 0.50, 0.28), 0.55)
    Ml = mat("M_lav", (0.66, 0.38, 0.88), 0.55)
    Mleaf = mat("M_leaf", (0.32, 0.68, 0.30), 0.55)
    Mstem = mat("M_stem", (0.30, 0.48, 0.26), 0.6)
    Mmail = mat("M_mail", (0.62, 0.38, 0.88), 0.4)
    Ms = mat("M_stone", (0.82, 0.76, 0.68), 0.7)
    Msmoke = mat("M_smoke", (0.76, 0.52, 0.90), 1.0, emit=0.2)
    Mchim = mat("M_chim", (0.97, 0.90, 0.82), 0.65)
    Mdark = mat("M_dark", (0.32, 0.16, 0.10), 0.8)
    Mcurt = mat("M_curt", (0.74, 0.38, 0.84), 0.6)
    Mknob = mat("M_knob", (1.0, 0.86, 0.32), 0.25, emit=0.5)

    cube("Base", (0, 0, 0.06), (2.05, 1.85, 0.14), Mb, 0.12)
    cube("Body", (0, 0.02, 0.62), (1.32, 1.14, 1.02), Mw, 0.14)
    cube("Front", (0, 0.52, 0.48), (0.95, 0.16, 0.72), Mw, 0.10)

    # Solid gable (under tiles)
    roof_prism("RoofSolid", Mr)

    # Dense fish-scale FRONT (SSOT camera face)
    mats = [Mr1, Mr2, Mr3]
    rows, cols = 8, 10
    for row in range(rows):
        t = (row + 0.35) / rows
        for col in range(cols):
            u = (col - (cols - 1) / 2) / ((cols - 1) / 2)
            if row % 2:
                u += 0.10 / 0.82
            if abs(u) > 1.02:
                continue
            fish_scale(f"FF{row}_{col}", u, t, True, mats[(row + col) % 3])

    # Back slope fewer
    for row in range(5):
        t = (row + 0.4) / 5.0
        for col in range(8):
            u = (col - 3.5) / 3.5
            if row % 2:
                u += 0.08 / 0.82
            if abs(u) > 1.0:
                continue
            fish_scale(f"BB{row}_{col}", u, t, False, mats[(row + col + 1) % 3])

    # Ridge beads
    for i, x in enumerate([-0.55, -0.28, 0.0, 0.28, 0.55]):
        sph(f"Rd{i}", (x, 0.0, 2.00), 0.09, Mr, (1.2, 1.0, 0.65))

    # Chimney
    cube("Chim", (0.40, -0.15, 2.05), (0.22, 0.22, 0.42), Mchim, 0.04)
    cube("ChimC", (0.40, -0.15, 2.28), (0.28, 0.28, 0.08), Mchim, 0.03)
    for i, (dx, dy, dz, s) in enumerate(
        [(0, 0, 0.08, 0.07), (0.07, 0.05, 0.18, 0.09), (0.14, 0.10, 0.28, 0.07), (0.22, 0.14, 0.38, 0.05)]
    ):
        sph(f"Sm{i}", (0.40 + dx, -0.15 + dy, 2.32 + dz), s, Msmoke)

    # Door
    cube("DFill", (0, 0.50, 0.42), (0.50, 0.12, 0.75), Mw, 0.05)
    cube("DFr", (0, 0.58, 0.45), (0.46, 0.05, 0.78), Mf, 0.05)
    cube("Door", (0, 0.62, 0.43), (0.34, 0.05, 0.62), Md, 0.05)
    sph("DArch", (0, 0.64, 0.82), 0.20, Mf, (1.0, 0.30, 0.55))
    sph("Knob", (0.11, 0.68, 0.43), 0.04, Mknob)
    cube("S1", (0, 0.76, 0.10), (0.38, 0.16, 0.07), Mf, 0.03)
    cube("S2", (0, 0.90, 0.05), (0.30, 0.12, 0.05), Mf, 0.02)

    # Windows
    for nm, x, z, rr in [
        ("W1", -0.36, 0.62, 0.09),
        ("W2", 0.36, 0.42, 0.08),
        ("W3", -0.26, 0.92, 0.085),
        ("W4", 0.0, 1.12, 0.095),
    ]:
        sph(f"{nm}g", (x, 0.62, z), rr, Me if nm != "W4" else Me2)
        cyl(f"{nm}f", (x, 0.58, z), rr + 0.02, 0.04, Mf)

    # Side window
    cube("SF", (0.62, 0, 0.65), (0.12, 0.50, 0.40), Mdark, 0.02)
    cube("SFr", (0.66, 0, 0.65), (0.07, 0.54, 0.44), Mf, 0.03)
    cube("SG", (0.70, 0, 0.65), (0.04, 0.46, 0.36), Me, 0.01)
    cube("CL", (0.64, -0.16, 0.68), (0.04, 0.07, 0.32), Mcurt, 0.02)
    cube("CR", (0.64, 0.18, 0.68), (0.04, 0.07, 0.32), Mcurt, 0.02)
    cyl("Lamp", (0.52, 0.08, 0.55), 0.03, 0.08, Mp)
    sph("LampG", (0.52, 0.08, 0.63), 0.06, Me2, (1, 1, 0.7))
    cyl("InPot", (0.52, -0.08, 0.52), 0.035, 0.05, Mp)
    sph("InLeaf", (0.52, -0.08, 0.60), 0.045, Mleaf)

    # Mail + plants + stones
    cyl("MP", (0.28, 0.76, 0.15), 0.022, 0.18, Mmail)
    cube("MB", (0.28, 0.76, 0.28), (0.14, 0.10, 0.11), Mmail, 0.03)
    cube("MF", (0.36, 0.76, 0.32), (0.03, 0.02, 0.07), Ml, 0.01)
    cyl("PB", (-0.68, 0.68, 0.15), 0.10, 0.15, Mp)
    for i, a in enumerate([0, 1.25, 2.5, 3.8, 5.0]):
        x = -0.68 + 0.04 * math.cos(a)
        y = 0.68 + 0.04 * math.sin(a)
        cyl(f"St{i}", (x, y, 0.30), 0.011, 0.20, Mstem)
        sph(f"Bl{i}", (x, y, 0.44), 0.045, Ml, (0.7, 0.7, 1.3))
    cyl("PS1", (0.48, 0.76, 0.12), 0.05, 0.09, Mp)
    sph("PL1", (0.48, 0.76, 0.22), 0.055, Mleaf)
    cyl("PS2", (0.60, 0.68, 0.11), 0.045, 0.08, Mp)
    sph("PL2", (0.60, 0.68, 0.20), 0.045, Ml)
    for i, (x, y, s) in enumerate([(-0.1, 1.1, 0.12), (0.08, 1.28, 0.1), (-0.02, 1.45, 0.09)]):
        sph(f"Sn{i}", (x, y, 0.03), s, Ms, (1.3, 1.0, 0.22))

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
            m["visual"] = "mockup_house_v15_fishscale"
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

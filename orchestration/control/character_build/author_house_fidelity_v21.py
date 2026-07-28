# -*- coding: utf-8 -*-
"""HOUSE_FIDELITY_V21 — half-disc clay scales + door clear of HOME.CHAR occlusion.

HOME.CHAR sits at plan (1.6, 1.4) on freecam (+Z) face — door stays on Blender −Y
but shifts to X≈−0.28 so freecam left-of-char sees full arch without moving plan.
Clay: denser half-disc coins (flat scale 0.22 Z), heavy row stagger, soft peach bands.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy

JOB = "HOUSE_FIDELITY_V21"
MODULE = "cozy_house_small_A"
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
            md.segments = 3
            bpy.ops.object.modifier_apply(modifier=md.name)
            o.select_set(False)
        except Exception:
            pass
    return o


def sph(name, loc, r, m, sc=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=16, ring_count=12)
    o = bpy.context.active_object
    o.name = name
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    setm(o, m)
    return o


def cyl(name, loc, r, d, m):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=14)
    o = bpy.context.active_object
    o.name = name
    setm(o, m)
    return o


def roof_prism(name, m):
    mesh = bpy.data.meshes.new(name)
    verts = [
        (-1.00, 0.84, 1.05),
        (1.00, 0.84, 1.05),
        (-1.00, -0.84, 1.05),
        (1.00, -0.84, 1.05),
        (-1.00, 0.00, 2.05),
        (1.00, 0.00, 2.05),
    ]
    faces = [(0, 1, 5, 4), (2, 4, 5, 3), (0, 4, 2), (1, 3, 5), (0, 2, 3, 1)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    setm(o, m)
    return o


def half_disc(name, u, t, front, m):
    """SSOT clay fish-scale: very flat half-coin, heavy overlap, translation only."""
    y = (0.84 if front else -0.84) * (1 - t)
    z = 1.05 * (1 - t) + 2.05 * t + 0.11
    x = u * 0.88
    r = 0.162 - 0.022 * t  # larger at eave
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, z), segments=16, ring_count=12)
    o = bpy.context.active_object
    o.name = name
    # Half-disc coin: wide XY, very flat Z (clay tile read)
    o.scale = (1.95, 1.65, 0.20)  # softer flatter clay
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    setm(o, m)
    return o


def build():
    clear()
    Mw = mat("M_wall", (0.97, 0.91, 0.82), 0.72)
    Mb = mat("M_base", (0.72, 0.54, 0.93), 0.62)
    Mr1 = mat("M_roof_a", (1.0, 0.68, 0.42), 0.48)   # soft peach
    Mr2 = mat("M_roof_b", (1.0, 0.88, 0.35), 0.45)   # soft yellow
    Mr3 = mat("M_roof_c", (0.99, 0.92, 0.72), 0.50)  # cream
    Mr = mat("M_ridge", (0.99, 0.96, 0.90), 0.55)
    Md = mat("M_door", (0.70, 0.42, 0.22), 0.5)
    Mf = mat("M_frame", (0.95, 0.72, 0.50), 0.5)
    Me = mat("M_emit", (1.0, 0.82, 0.35), 0.3, emit=5.5)
    Me2 = mat("M_emit2", (1.0, 0.92, 0.55), 0.3, emit=4.0)
    Mp = mat("M_pot", (0.92, 0.58, 0.34), 0.55)
    Ml = mat("M_lav", (0.72, 0.44, 0.92), 0.55)
    Mleaf = mat("M_leaf", (0.34, 0.74, 0.32), 0.55)
    Mstem = mat("M_stem", (0.30, 0.50, 0.28), 0.6)
    Mmail = mat("M_mail", (0.70, 0.44, 0.92), 0.4)
    Ms = mat("M_stone", (0.86, 0.80, 0.72), 0.7)
    Msmoke = mat("M_smoke", (0.80, 0.58, 0.94), 1.0, emit=0.3)
    Mchim = mat("M_chim", (0.98, 0.93, 0.88), 0.65)
    Mdark = mat("M_dark", (0.28, 0.14, 0.10), 0.8)
    Mcurt = mat("M_curt", (0.80, 0.44, 0.90), 0.6)
    Mknob = mat("M_knob", (1.0, 0.90, 0.38), 0.25, emit=0.9)

    cube("Base", (0, 0, 0.06), (2.18, 1.98, 0.14), Mb, 0.15)
    cube("Body", (0, 0.0, 0.62), (1.42, 1.22, 1.08), Mw, 0.18)
    # Freecam face bulge (Blender −Y)
    cube("Front", (0, -0.60, 0.50), (1.02, 0.22, 0.82), Mw, 0.12)

    roof_prism("RoofSolid", Mr)

    mats = [Mr1, Mr2, Mr3]
    # Freecam slope = Blender −Y (front=False in half_disc)
    rows, cols = 13, 15
    for row in range(rows):
        t = (row + 0.18) / rows
        for col in range(cols):
            u = (col - (cols - 1) / 2) / max(1e-6, (cols - 1) / 2)
            if row % 2:
                u += 1.0 / cols  # half-step stagger like real fish-scale
            if abs(u) > 1.08:
                continue
            half_disc(f"FF{row}_{col}", u, t, False, mats[row % 3])

    for row in range(7):
        t = (row + 0.25) / 7.0
        for col in range(10):
            u = (col - 4.5) / 4.5
            if row % 2:
                u += 0.09
            if abs(u) > 1.05:
                continue
            half_disc(f"BB{row}_{col}", u, t, True, mats[(row + 1) % 3])

    for i, x in enumerate([-0.65, -0.32, 0.0, 0.32, 0.65]):
        sph(f"Rd{i}", (x, 0.0, 2.12), 0.11, Mr, (1.35, 1.1, 0.7))

    cube("Chim", (0.44, 0.20, 2.16), (0.26, 0.26, 0.50), Mchim, 0.05)
    cube("ChimC", (0.44, 0.20, 2.42), (0.32, 0.32, 0.08), Mchim, 0.03)
    for i, (dx, dy, dz, s) in enumerate(
        [(0, 0, 0.08, 0.09), (0.08, -0.05, 0.22, 0.11), (0.16, -0.10, 0.36, 0.09), (0.28, -0.14, 0.50, 0.07)]
    ):
        sph(f"Sm{i}", (0.44 + dx, 0.20 + dy, 2.48 + dz), s, Msmoke)

    # ===== DOOR offset left (X−) clear of HOME.CHAR at plan x=1.6 =====
    DX = -0.28  # clear char at +1.6
    Y = -0.74   # freecam face
    cube("DFill", (DX, Y + 0.12, 0.42), (0.58, 0.14, 0.84), Mw, 0.05)
    cube("DFr", (DX, Y, 0.46), (0.58, 0.09, 0.90), Mf, 0.06)
    cube("Door", (DX, Y - 0.07, 0.46), (0.50, 0.11, 0.80), Md, 0.06)
    cube("DP1", (DX, Y - 0.12, 0.56), (0.42, 0.02, 0.025), Mdark, 0.0)
    cube("DP2", (DX, Y - 0.12, 0.38), (0.42, 0.02, 0.025), Mdark, 0.0)
    cube("DP3", (DX, Y - 0.12, 0.47), (0.025, 0.02, 0.58), Mdark, 0.0)
    sph("DArch", (DX, Y - 0.07, 0.92), 0.28, Mf, (1.15, 0.40, 0.62))
    sph("Knob", (DX + 0.16, Y - 0.15, 0.44), 0.055, Mknob)
    # Peach steps under door (also left-offset)
    cube("S1", (DX, Y - 0.20, 0.10), (0.50, 0.22, 0.09), Mf, 0.04)
    cube("S2", (DX, Y - 0.38, 0.05), (0.42, 0.18, 0.07), Mf, 0.03)
    cube("S3", (DX, Y - 0.54, 0.02), (0.34, 0.14, 0.05), Mf, 0.02)

    # Glow windows on freecam face (flank door, avoid char x)
    for nm, x, z, rr in [
        ("W1", -0.55, 0.68, 0.10),
        ("W2", 0.35, 0.50, 0.09),
        ("W3", -0.48, 1.00, 0.095),
        ("W4", -0.05, 1.20, 0.11),
    ]:
        sph(f"{nm}g", (x, Y + 0.06, z), rr, Me if nm != "W4" else Me2)
        cyl(f"{nm}f", (x, Y + 0.12, z), rr + 0.025, 0.05, Mf)

    # Side picture window (+X)
    cube("SF", (0.70, 0, 0.66), (0.12, 0.56, 0.46), Mdark, 0.02)
    cube("SFr", (0.74, 0, 0.66), (0.08, 0.60, 0.50), Mf, 0.03)
    cube("SG", (0.78, 0, 0.66), (0.05, 0.50, 0.40), Me, 0.01)
    cube("CL", (0.72, -0.18, 0.70), (0.04, 0.08, 0.36), Mcurt, 0.02)
    cube("CR", (0.72, 0.20, 0.70), (0.04, 0.08, 0.36), Mcurt, 0.02)
    cyl("Lamp", (0.58, 0.10, 0.56), 0.035, 0.10, Mp)
    sph("LampG", (0.58, 0.10, 0.66), 0.07, Me2, (1, 1, 0.75))
    cyl("InPot", (0.58, -0.10, 0.52), 0.04, 0.06, Mp)
    sph("InLeaf", (0.58, -0.10, 0.62), 0.055, Mleaf)

    # Mail right of door (not under char); lavender left
    cyl("MP", (0.42, Y - 0.10, 0.16), 0.026, 0.22, Mmail)
    cube("MB", (0.42, Y - 0.10, 0.32), (0.16, 0.12, 0.13), Mmail, 0.03)
    cube("MFlag", (0.52, Y - 0.10, 0.36), (0.035, 0.02, 0.09), Ml, 0.01)
    cyl("PB", (-0.78, Y + 0.05, 0.16), 0.12, 0.17, Mp)
    for i, a in enumerate([0, 1.0, 2.0, 3.0, 4.0, 5.0, 5.8]):
        x = -0.78 + 0.05 * math.cos(a)
        y = Y + 0.05 + 0.05 * math.sin(a)
        cyl(f"St{i}", (x, y, 0.34), 0.013, 0.24, Mstem)
        sph(f"Bl{i}", (x, y, 0.50), 0.05, Ml, (0.7, 0.7, 1.4))
    cyl("PS1", (0.58, Y - 0.08, 0.12), 0.06, 0.11, Mp)
    sph("PL1", (0.58, Y - 0.08, 0.26), 0.065, Mleaf)
    for i, (x, y, s) in enumerate([(-0.28, Y - 0.58, 0.14), (-0.12, Y - 0.75, 0.12), (-0.35, Y - 0.90, 0.10)]):
        sph(f"Sn{i}", (x, y, 0.03), s, Ms, (1.4, 1.1, 0.24))

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
            m["visual"] = "mockup_house_v21"
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

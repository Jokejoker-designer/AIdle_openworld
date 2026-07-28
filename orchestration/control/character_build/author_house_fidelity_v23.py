# -*- coding: utf-8 -*-
"""HOUSE_FIDELITY_V23 — SSOT soft clay half-discs + side interior window detail.

Gaps vs prop_house_small.jpg after V21:
  - clay needs softer peach/cream/yellow rounded scales (not harsh orange bands)
  - side picture window: purple curtains, warm interior, lamp + pot (SSOT)
  - front glow windows more peach-framed
  - door stays freecam-clear at X≈−0.28
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy

JOB = "HOUSE_FIDELITY_V23"
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


def cube(name, loc, sc, m, bevel=0.05):
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
        (-1.02, 0.86, 1.04), (1.02, 0.86, 1.04),
        (-1.02, -0.86, 1.04), (1.02, -0.86, 1.04),
        (-1.02, 0.00, 2.08), (1.02, 0.00, 2.08),
    ]
    faces = [(0, 1, 5, 4), (2, 4, 5, 3), (0, 4, 2), (1, 3, 5), (0, 2, 3, 1)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    setm(o, m)
    return o


def clay_scale(name, u, t, front, m):
    """Soft SSOT fish-scale: large flat half-disc, gentle overlap."""
    y = (0.86 if front else -0.86) * (1 - t)
    z = 1.04 * (1 - t) + 2.08 * t + 0.12
    x = u * 0.90
    r = 0.168 - 0.02 * t
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, z), segments=16, ring_count=12)
    o = bpy.context.active_object
    o.name = name
    # Softer clay coin — slightly thicker than V21 for rounded soft read
    o.scale = (2.0, 1.70, 0.32)  # thicker soft clay
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    setm(o, m)
    return o


def build():
    clear()
    # Soft SSOT palette
    Mw = mat("M_wall", (0.98, 0.93, 0.86), 0.75)
    Mb = mat("M_base", (0.78, 0.62, 0.94), 0.62)
    # Soft peach / soft yellow / cream (SSOT clay, not harsh orange)
    Mr1 = mat("M_roof_a", (1.0, 0.82, 0.65), 0.52)
    Mr2 = mat("M_roof_b", (1.0, 0.92, 0.55), 0.50)
    Mr3 = mat("M_roof_c", (0.99, 0.95, 0.85), 0.55)
    Mr = mat("M_ridge", (0.99, 0.96, 0.90), 0.55)
    Md = mat("M_door", (0.72, 0.45, 0.26), 0.5)
    Mf = mat("M_frame", (0.96, 0.78, 0.58), 0.5)
    Me = mat("M_emit", (1.0, 0.85, 0.40), 0.3, emit=6.0)
    Me2 = mat("M_emit2", (1.0, 0.94, 0.60), 0.3, emit=4.5)
    Me3 = mat("M_emit3", (1.0, 0.88, 0.50), 0.3, emit=5.0)
    Mp = mat("M_pot", (0.92, 0.58, 0.36), 0.55)
    Ml = mat("M_lav", (0.74, 0.48, 0.92), 0.55)
    Mleaf = mat("M_leaf", (0.38, 0.75, 0.36), 0.55)
    Mstem = mat("M_stem", (0.32, 0.52, 0.30), 0.6)
    Mmail = mat("M_mail", (0.72, 0.48, 0.92), 0.4)
    Ms = mat("M_stone", (0.90, 0.86, 0.78), 0.7)
    Msmoke = mat("M_smoke", (0.82, 0.62, 0.94), 1.0, emit=0.35)
    Mchim = mat("M_chim", (0.98, 0.94, 0.90), 0.65)
    Mdark = mat("M_dark", (0.25, 0.12, 0.08), 0.8)
    Mcurt = mat("M_curt", (0.82, 0.48, 0.92), 0.55)
    Mknob = mat("M_knob", (1.0, 0.90, 0.40), 0.25, emit=1.0)
    Mpix = mat("M_pixel", (0.55, 0.45, 0.95), 0.6, emit=0.15)

    cube("Base", (0, 0, 0.06), (2.20, 2.00, 0.14), Mb, 0.16)
    # Soft rounded body
    cube("Body", (0, 0.0, 0.62), (1.44, 1.24, 1.08), Mw, 0.20)
    cube("Front", (0, -0.62, 0.50), (1.04, 0.24, 0.84), Mw, 0.14)

    roof_prism("RoofSolid", Mr)

    mats = [Mr1, Mr2, Mr3]
    # Freecam face = Blender −Y
    rows, cols = 11, 13
    for row in range(rows):
        t = (row + 0.20) / rows
        for col in range(cols):
            u = (col - (cols - 1) / 2) / max(1e-6, (cols - 1) / 2)
            if row % 2:
                u += 0.9 / cols
            if abs(u) > 1.08:
                continue
            clay_scale(f"FF{row}_{col}", u, t, False, mats[row % 3])

    for row in range(7):
        t = (row + 0.28) / 7.0
        for col in range(10):
            u = (col - 4.5) / 4.5
            if row % 2:
                u += 0.08
            if abs(u) > 1.05:
                continue
            clay_scale(f"BB{row}_{col}", u, t, True, mats[(row + 1) % 3])

    for i, x in enumerate([-0.65, -0.32, 0.0, 0.32, 0.65]):
        sph(f"Rd{i}", (x, 0.0, 2.14), 0.115, Mr, (1.35, 1.1, 0.72))

    cube("Chim", (0.44, 0.18, 2.18), (0.28, 0.28, 0.52), Mchim, 0.06)
    cube("ChimC", (0.44, 0.18, 2.46), (0.34, 0.34, 0.08), Mchim, 0.03)
    # Pixel-style smoke puffs
    for i, (dx, dy, dz, s) in enumerate([
        (0, 0, 0.06, 0.08), (0.08, -0.04, 0.18, 0.10),
        (0.16, -0.08, 0.32, 0.09), (0.26, -0.12, 0.46, 0.07),
        (0.34, -0.16, 0.58, 0.05),
    ]):
        sph(f"Sm{i}", (0.44 + dx, 0.18 + dy, 2.52 + dz), s, Msmoke if i % 2 == 0 else Mpix)

    # Door freecam-clear
    DX, Y = -0.28, -0.76
    cube("DFill", (DX, Y + 0.12, 0.42), (0.60, 0.14, 0.86), Mw, 0.05)
    cube("DFr", (DX, Y, 0.46), (0.60, 0.09, 0.92), Mf, 0.06)
    cube("Door", (DX, Y - 0.08, 0.46), (0.52, 0.12, 0.82), Md, 0.06)
    cube("DP1", (DX, Y - 0.13, 0.58), (0.44, 0.02, 0.025), Mdark, 0.0)
    cube("DP2", (DX, Y - 0.13, 0.38), (0.44, 0.02, 0.025), Mdark, 0.0)
    cube("DP3", (DX, Y - 0.13, 0.48), (0.025, 0.02, 0.60), Mdark, 0.0)
    sph("DArch", (DX, Y - 0.08, 0.94), 0.29, Mf, (1.15, 0.42, 0.62))
    sph("Knob", (DX + 0.16, Y - 0.16, 0.44), 0.055, Mknob)
    cube("S1", (DX, Y - 0.22, 0.10), (0.52, 0.24, 0.09), Mf, 0.04)
    cube("S2", (DX, Y - 0.40, 0.05), (0.44, 0.18, 0.07), Mf, 0.03)
    cube("S3", (DX, Y - 0.56, 0.02), (0.36, 0.14, 0.05), Mf, 0.02)

    # Front glow windows (peach frames)
    for nm, x, z, rr in [
        ("W1", -0.55, 0.70, 0.105),
        ("W2", 0.38, 0.52, 0.095),
        ("W3", -0.48, 1.02, 0.10),
        ("W4", -0.05, 1.22, 0.115),
    ]:
        sph(f"{nm}g", (x, Y + 0.06, z), rr, Me if nm != "W4" else Me2)
        cyl(f"{nm}f", (x, Y + 0.12, z), rr + 0.028, 0.055, Mf)

    # ===== SSOT SIDE PICTURE WINDOW (+X) — curtains, lamp, pot, warm room =====
    cube("SF", (0.68, 0, 0.68), (0.10, 0.62, 0.52), Mdark, 0.02)
    cube("SFr", (0.74, 0, 0.68), (0.08, 0.68, 0.58), Mf, 0.04)
    # Warm interior glow pane
    cube("SG", (0.78, 0, 0.68), (0.05, 0.58, 0.48), Me3, 0.01)
    # Purple curtains (SSOT)
    cube("CL", (0.72, -0.22, 0.72), (0.05, 0.10, 0.42), Mcurt, 0.02)
    cube("CR", (0.72, 0.24, 0.72), (0.05, 0.10, 0.42), Mcurt, 0.02)
    # Interior lamp on table
    cyl("InTable", (0.55, 0.12, 0.42), 0.08, 0.06, Mp)
    cyl("InLamp", (0.55, 0.12, 0.52), 0.035, 0.12, Mf)
    sph("InLampG", (0.55, 0.12, 0.64), 0.08, Me2, (1, 1, 0.8))
    # Interior pot
    cyl("InPot", (0.55, -0.14, 0.48), 0.045, 0.08, Mp)
    sph("InLeaf", (0.55, -0.14, 0.60), 0.07, Mleaf)
    sph("InLeaf2", (0.58, -0.12, 0.66), 0.05, Mleaf)
    # Pixel-ish blue dots on curtain (SSOT curtain pattern)
    for i, (dy, dz) in enumerate([(-0.18, 0.55), (-0.20, 0.70), (-0.16, 0.85), (0.20, 0.60), (0.22, 0.78)]):
        sph(f"Dot{i}", (0.73, dy, dz), 0.02, Mpix)

    # Mail + lavender + stones on freecam face
    cyl("MP", (0.42, Y - 0.08, 0.16), 0.028, 0.24, Mmail)
    cube("MB", (0.42, Y - 0.08, 0.34), (0.18, 0.14, 0.14), Mmail, 0.04)
    cube("MFlag", (0.54, Y - 0.08, 0.40), (0.04, 0.02, 0.10), Ml, 0.01)
    sph("MKnob", (0.42, Y + 0.02, 0.36), 0.03, Mknob)
    cyl("PB", (-0.80, Y + 0.05, 0.16), 0.13, 0.18, Mp)
    for i, a in enumerate([0, 0.9, 1.8, 2.7, 3.6, 4.5, 5.4]):
        x = -0.80 + 0.055 * math.cos(a)
        y = Y + 0.05 + 0.055 * math.sin(a)
        cyl(f"St{i}", (x, y, 0.36), 0.014, 0.26, Mstem)
        sph(f"Bl{i}", (x, y, 0.54), 0.055, Ml, (0.7, 0.7, 1.4))
    cyl("PS1", (0.60, Y - 0.06, 0.12), 0.065, 0.12, Mp)
    sph("PL1", (0.60, Y - 0.06, 0.28), 0.07, Mleaf)
    cyl("PS2", (0.72, Y + 0.08, 0.11), 0.055, 0.10, Mp)
    sph("PL2", (0.72, Y + 0.08, 0.24), 0.055, Ml)
    for i, (x, y, s) in enumerate([(-0.28, Y - 0.60, 0.15), (-0.10, Y - 0.78, 0.13), (-0.35, Y - 0.95, 0.11)]):
        sph(f"Sn{i}", (x, y, 0.03), s, Ms, (1.45, 1.15, 0.26))

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
            m["visual"] = "mockup_house_v23"
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

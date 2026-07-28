# -*- coding: utf-8 -*-
"""HOUSE_FIDELITY_V19 — freecam-facing door + clay fish-scale SSOT push.

Root cause of "door not prominent": glTF Z-up maps Blender +Y → Godot −Z,
while freecam sits at +Z looking at origin — so door on Blender +Y faced AWAY
from the camera. V19 places the arched door on Blender −Y (Godot +Z).

Clay scales: larger overlapping half-disc coins, peach/yellow/cream row bands.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy

JOB = "HOUSE_FIDELITY_V19"
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
            md.segments = 2
            bpy.ops.object.modifier_apply(modifier=md.name)
            o.select_set(False)
        except Exception:
            pass
    return o


def sph(name, loc, r, m, sc=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=14, ring_count=10)
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
    mesh = bpy.data.meshes.new(name)
    # Eaves + peak — verts only, no object rotation
    verts = [
        (-0.98, 0.82, 1.06),
        (0.98, 0.82, 1.06),
        (-0.98, -0.82, 1.06),
        (0.98, -0.82, 1.06),
        (-0.98, 0.00, 2.02),
        (0.98, 0.00, 2.02),
    ]
    faces = [(0, 1, 5, 4), (2, 4, 5, 3), (0, 4, 2), (1, 3, 5), (0, 2, 3, 1)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    setm(o, m)
    return o


def clay_scallop(name, u, t, front, m, row):
    """SSOT-style clay half-disc: wide flat coin, heavy overlap, lift off prism."""
    if front:
        y = 0.82 * (1 - t)
    else:
        y = -0.82 * (1 - t)
    z = 1.06 * (1 - t) + 2.02 * t + 0.10
    x = u * 0.86
    # Larger discs lower on roof, slightly smaller near peak
    r = 0.14 - 0.02 * t
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, z), segments=14, ring_count=10)
    o = bpy.context.active_object
    o.name = name
    # Flatten into fish-scale coin (SSOT rounded tiles)
    o.scale = (1.65, 1.45, 0.38)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    setm(o, m)
    return o


def build():
    clear()
    Mw = mat("M_wall", (0.97, 0.91, 0.82), 0.72)
    Mb = mat("M_base", (0.72, 0.54, 0.93), 0.62)
    Mr1 = mat("M_roof_a", (1.0, 0.62, 0.38), 0.48)   # peach
    Mr2 = mat("M_roof_b", (1.0, 0.86, 0.28), 0.45)   # yellow
    Mr3 = mat("M_roof_c", (0.99, 0.90, 0.68), 0.50)  # cream
    Mr = mat("M_ridge", (0.99, 0.95, 0.88), 0.55)
    Md = mat("M_door", (0.68, 0.40, 0.20), 0.5)
    Mf = mat("M_frame", (0.94, 0.70, 0.48), 0.5)
    Me = mat("M_emit", (1.0, 0.80, 0.32), 0.3, emit=5.5)
    Me2 = mat("M_emit2", (1.0, 0.92, 0.52), 0.3, emit=4.0)
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
    Mknob = mat("M_knob", (1.0, 0.90, 0.38), 0.25, emit=0.8)

    cube("Base", (0, 0, 0.06), (2.15, 1.95, 0.14), Mb, 0.15)
    cube("Body", (0, 0.0, 0.62), (1.40, 1.20, 1.06), Mw, 0.18)

    # Front bulge on freecam face (Blender −Y → Godot +Z)
    cube("Front", (0, -0.58, 0.50), (1.00, 0.20, 0.80), Mw, 0.12)

    roof_prism("RoofSolid", Mr)

    # Dense clay fish-scale — BOTH slopes; freecam primarily sees −Y slope as front
    mats = [Mr1, Mr2, Mr3]
    rows, cols = 11, 13
    for row in range(rows):
        t = (row + 0.22) / rows
        for col in range(cols):
            u = (col - (cols - 1) / 2) / max(1e-6, (cols - 1) / 2)
            if row % 2:
                u += 0.5 / cols * 2
            if abs(u) > 1.06:
                continue
            clay = mats[row % 3]
            # front = Blender −Y (camera-facing after glTF)
            clay_scallop(f"FF{row}_{col}", u, t, False, clay, row)

    for row in range(6):
        t = (row + 0.3) / 6.0
        for col in range(9):
            u = (col - 4.0) / 4.0
            if row % 2:
                u += 0.08
            if abs(u) > 1.0:
                continue
            clay_scallop(f"BB{row}_{col}", u, t, True, mats[(row + 1) % 3], row)

    for i, x in enumerate([-0.62, -0.31, 0.0, 0.31, 0.62]):
        sph(f"Rd{i}", (x, 0.0, 2.08), 0.105, Mr, (1.3, 1.05, 0.72))

    cube("Chim", (0.42, 0.18, 2.12), (0.26, 0.26, 0.48), Mchim, 0.05)
    cube("ChimC", (0.42, 0.18, 2.38), (0.32, 0.32, 0.08), Mchim, 0.03)
    for i, (dx, dy, dz, s) in enumerate(
        [(0, 0, 0.08, 0.09), (0.08, -0.05, 0.20, 0.11), (0.16, -0.10, 0.34, 0.09), (0.26, -0.14, 0.48, 0.07)]
    ):
        sph(f"Sm{i}", (0.42 + dx, 0.18 + dy, 2.42 + dz), s, Msmoke)

    # ===== CAMERA-FACING DOOR (Blender −Y) — large SSOT arched wood door =====
    Y = -0.72  # extrude toward freecam
    cube("DFill", (0, Y + 0.10, 0.42), (0.58, 0.14, 0.82), Mw, 0.05)
    cube("DFr", (0, Y, 0.46), (0.56, 0.08, 0.88), Mf, 0.06)
    cube("Door", (0, Y - 0.06, 0.46), (0.48, 0.10, 0.78), Md, 0.06)
    cube("DP1", (0, Y - 0.10, 0.55), (0.40, 0.02, 0.025), Mdark, 0.0)
    cube("DP2", (0, Y - 0.10, 0.38), (0.40, 0.02, 0.025), Mdark, 0.0)
    cube("DP3", (0, Y - 0.10, 0.46), (0.02, 0.02, 0.55), Mdark, 0.0)  # vertical plank
    sph("DArch", (0, Y - 0.06, 0.90), 0.26, Mf, (1.15, 0.38, 0.62))
    sph("Knob", (0.15, Y - 0.14, 0.44), 0.055, Mknob)
    # Peach steps toward camera
    cube("S1", (0, Y - 0.18, 0.10), (0.48, 0.20, 0.09), Mf, 0.04)
    cube("S2", (0, Y - 0.34, 0.05), (0.40, 0.16, 0.07), Mf, 0.03)
    cube("S3", (0, Y - 0.48, 0.02), (0.32, 0.12, 0.05), Mf, 0.02)

    # Glow windows on freecam face flanking door
    for nm, x, z, rr in [
        ("W1", -0.40, 0.66, 0.10),
        ("W2", 0.40, 0.48, 0.09),
        ("W3", -0.30, 0.98, 0.095),
        ("W4", 0.0, 1.18, 0.11),
    ]:
        sph(f"{nm}g", (x, Y + 0.05, z), rr, Me if nm != "W4" else Me2)
        cyl(f"{nm}f", (x, Y + 0.10, z), rr + 0.025, 0.05, Mf)

    # Side picture window (+X) still visible from freecam corner
    cube("SF", (0.68, 0, 0.66), (0.12, 0.56, 0.46), Mdark, 0.02)
    cube("SFr", (0.72, 0, 0.66), (0.08, 0.60, 0.50), Mf, 0.03)
    cube("SG", (0.76, 0, 0.66), (0.05, 0.50, 0.40), Me, 0.01)
    cube("CL", (0.70, -0.18, 0.70), (0.04, 0.08, 0.36), Mcurt, 0.02)
    cube("CR", (0.70, 0.20, 0.70), (0.04, 0.08, 0.36), Mcurt, 0.02)
    cyl("Lamp", (0.56, 0.10, 0.56), 0.035, 0.10, Mp)
    sph("LampG", (0.56, 0.10, 0.66), 0.07, Me2, (1, 1, 0.75))
    cyl("InPot", (0.56, -0.10, 0.52), 0.04, 0.06, Mp)
    sph("InLeaf", (0.56, -0.10, 0.62), 0.055, Mleaf)

    # Mail + lavender on freecam face
    cyl("MP", (0.32, Y - 0.12, 0.16), 0.026, 0.22, Mmail)
    cube("MB", (0.32, Y - 0.12, 0.32), (0.16, 0.12, 0.13), Mmail, 0.03)
    cube("MFlag", (0.42, Y - 0.12, 0.36), (0.035, 0.02, 0.09), Ml, 0.01)
    cyl("PB", (-0.72, Y + 0.05, 0.16), 0.12, 0.17, Mp)
    for i, a in enumerate([0, 1.0, 2.0, 3.0, 4.0, 5.0, 5.8]):
        x = -0.72 + 0.05 * math.cos(a)
        y = Y + 0.05 + 0.05 * math.sin(a)
        cyl(f"St{i}", (x, y, 0.34), 0.013, 0.24, Mstem)
        sph(f"Bl{i}", (x, y, 0.50), 0.05, Ml, (0.7, 0.7, 1.4))
    cyl("PS1", (0.52, Y - 0.10, 0.12), 0.06, 0.11, Mp)
    sph("PL1", (0.52, Y - 0.10, 0.26), 0.065, Mleaf)
    cyl("PS2", (0.66, Y + 0.05, 0.11), 0.05, 0.09, Mp)
    sph("PL2", (0.66, Y + 0.05, 0.22), 0.055, Ml)
    for i, (x, y, s) in enumerate([(0.0, Y - 0.55, 0.14), (0.14, Y - 0.72, 0.12), (-0.08, Y - 0.88, 0.10)]):
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
            m["visual"] = "mockup_house_v19"
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

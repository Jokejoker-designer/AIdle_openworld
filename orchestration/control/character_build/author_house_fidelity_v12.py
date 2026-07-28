# -*- coding: utf-8 -*-
"""HOUSE_FIDELITY_V12 — solid gable roof + orderly scallop rows (fix boxy+chaotic).

Failure signature being broken: box_body_chaotic_tiles_not_ssot_gable (strike 3 if same).
Target SSOT: buildings/bld_01_house.jpg
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Euler, Vector

JOB = "HOUSE_FIDELITY_V12"
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
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
        if emit > 0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (*rgb, 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emit
    return m


def apply_all(o):
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    o.select_set(False)


def fin(o, m, bevel=0.04):
    o.data.materials.clear()
    o.data.materials.append(m)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    if bevel > 0:
        try:
            bpy.ops.object.modifier_add(type="BEVEL")
            md = o.modifiers[-1]
            md.width = bevel
            md.segments = 3
            md.limit_method = "ANGLE"
            bpy.ops.object.modifier_apply(modifier=md.name)
        except Exception:
            pass
    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass
    apply_all(o)
    return o


def cube(name, loc, sc, m, bevel=0.05):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = sc
    return fin(o, m, bevel)


def sph(name, loc, r, m, sc=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=14, ring_count=10)
    o = bpy.context.active_object
    o.name = name
    o.scale = sc
    return fin(o, m, 0.0)


def cyl(name, loc, r, d, m, rot=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=14)
    o = bpy.context.active_object
    o.name = name
    if rot:
        o.rotation_euler = Euler(rot, "XYZ")
    return fin(o, m, 0.0)


def scallop_tile(name, loc, rot_x_deg, m):
    """Flat oval tile sitting on roof plane — scale applied before parent."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=loc, segments=12, ring_count=8)
    o = bpy.context.active_object
    o.name = name
    o.scale = (1.55, 1.25, 0.22)
    o.rotation_euler = Euler((math.radians(rot_x_deg), 0, 0), "XYZ")
    return fin(o, m, 0.0)


def build():
    clear()
    # Saturated SSOT palette (reads under realm light)
    Mw = mat("M_wall", (0.98, 0.88, 0.72), 0.72)
    Mb = mat("M_base", (0.68, 0.50, 0.90), 0.62)
    Mr1 = mat("M_roof_a", (1.0, 0.58, 0.18), 0.45)
    Mr2 = mat("M_roof_b", (1.0, 0.80, 0.22), 0.45)
    Mr3 = mat("M_roof_c", (0.98, 0.68, 0.32), 0.48)
    Mridge = mat("M_ridge", (0.99, 0.92, 0.78), 0.55)
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

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = f"MOD_{MODULE}"

    # Lilac pad
    cube("Base", (0, 0, 0.06), (2.05, 1.85, 0.14), Mb, 0.14)

    # Soft body — slightly taller for gable proportion
    cube("Body", (0, 0.02, 0.68), (1.32, 1.12, 1.10), Mw, 0.16)
    cube("FrontBulge", (0, 0.52, 0.52), (0.95, 0.18, 0.78), Mw, 0.10)

    # SOLID gable prism: two thick slope slabs that form A-frame silhouette
    for sign, nm in ((1.0, "GableFront"), (-1.0, "GableBack")):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, sign * 0.32, 1.48))
        o = bpy.context.active_object
        o.name = nm
        o.scale = (1.58, 0.98, 0.20)
        o.rotation_euler = Euler((sign * math.radians(36), 0, 0), "XYZ")
        fin(o, Mridge, 0.05)

    # Peak fill
    cube("Peak", (0, 0, 1.78), (1.50, 0.22, 0.18), Mridge, 0.06)

    # ORDERLY scallop rows on FRONT slope only (camera-facing SSOT read)
    # Front slope plane: y from 0.62 (eave) → 0.05 (ridge), z from 1.18 → 1.82
    mats_r = [Mr1, Mr2, Mr3]
    rows = 7
    for row in range(rows):
        t = row / max(rows - 1, 1)
        y = 0.58 - t * 0.55
        z = 1.20 + t * 0.68
        cols = 9
        for col in range(cols):
            x = (col - (cols - 1) / 2) * 0.16
            if row % 2:
                x += 0.08
            if abs(x) > 0.78:
                continue
            m = mats_r[(row + col) % 3]
            scallop_tile(f"TileF{row}_{col}", (x, y, z), -36, m)

    # Back slope fewer orderly tiles
    for row in range(5):
        t = row / 4.0
        y = -0.12 - t * 0.48
        z = 1.28 + t * 0.52
        for col in range(7):
            x = (col - 3) * 0.18
            if row % 2:
                x += 0.08
            if abs(x) > 0.72:
                continue
            m = mats_r[(row + col + 1) % 3]
            scallop_tile(f"TileB{row}_{col}", (x, y, z), 36, m)

    # Ridge beads
    for i, x in enumerate([-0.5, -0.25, 0.0, 0.25, 0.5]):
        sph(f"Ridge{i}", (x, 0.0, 1.90), 0.085, Mridge, (1.2, 1.0, 0.65))

    # Chimney right-back
    cube("Chimney", (0.40, -0.18, 1.98), (0.22, 0.22, 0.44), Mchim, 0.04)
    cube("ChimCap", (0.40, -0.18, 2.22), (0.28, 0.28, 0.08), Mchim, 0.03)
    for i, (dx, dy, dz, s) in enumerate(
        [
            (0.0, 0.0, 0.10, 0.075),
            (0.07, 0.05, 0.22, 0.10),
            (0.14, 0.10, 0.34, 0.08),
            (0.22, 0.15, 0.44, 0.06),
        ]
    ):
        sph(f"Smoke{i}", (0.40 + dx, -0.18 + dy, 2.28 + dz), s, Msmoke)

    # Door (front, no cavity)
    cube("DoorFill", (0, 0.50, 0.48), (0.52, 0.14, 0.85), Mw, 0.05)
    cube("DoorFrame", (0, 0.60, 0.50), (0.48, 0.06, 0.86), Mf, 0.05)
    cube("Door", (0, 0.64, 0.48), (0.36, 0.05, 0.70), Md, 0.05)
    sph("DoorArch", (0, 0.66, 0.92), 0.22, Mf, (1.0, 0.32, 0.55))
    sph("Knob", (0.12, 0.70, 0.48), 0.045, Mknob)
    cube("Step1", (0, 0.78, 0.10), (0.40, 0.18, 0.08), Mf, 0.03)
    cube("Step2", (0, 0.92, 0.05), (0.32, 0.14, 0.05), Mf, 0.02)

    # Windows
    for nm, x, z, rr in [
        ("W1", -0.38, 0.70, 0.10),
        ("W2", 0.38, 0.48, 0.09),
        ("W3", -0.28, 1.05, 0.095),
        ("W4", 0.0, 1.28, 0.11),
    ]:
        cyl(f"{nm}f", (x, 0.62, z), rr + 0.025, 0.05, Mf, rot=(math.pi / 2, 0, 0))
        sph(f"{nm}g", (x, 0.66, z), rr, Me if nm != "W4" else Me2)

    # Side window
    cube("SideFill", (0.62, 0.0, 0.75), (0.14, 0.52, 0.44), Mdark, 0.02)
    cube("SideFr", (0.68, 0.0, 0.75), (0.08, 0.56, 0.48), Mf, 0.03)
    cube("SideGl", (0.72, 0.0, 0.75), (0.04, 0.48, 0.40), Me, 0.01)
    cube("CurtL", (0.66, -0.18, 0.80), (0.04, 0.08, 0.36), Mcurt, 0.02)
    cube("CurtR", (0.66, 0.20, 0.80), (0.04, 0.08, 0.36), Mcurt, 0.02)
    cyl("Lamp", (0.52, 0.08, 0.58), 0.03, 0.08, Mp)
    sph("LampG", (0.52, 0.08, 0.66), 0.06, Me2, (1, 1, 0.7))
    cyl("InPot", (0.52, -0.08, 0.55), 0.035, 0.05, Mp)
    sph("InLeaf", (0.52, -0.08, 0.62), 0.045, Mleaf)

    # Mail + plants + stones
    cyl("MailPost", (0.30, 0.78, 0.16), 0.025, 0.20, Mmail)
    cube("MailBox", (0.30, 0.78, 0.30), (0.16, 0.12, 0.12), Mmail, 0.04)
    cube("MailFlag", (0.38, 0.78, 0.34), (0.04, 0.02, 0.08), Ml, 0.01)

    cyl("PotBig", (-0.70, 0.70, 0.16), 0.11, 0.16, Mp)
    for i, a in enumerate([0, 1.2, 2.4, 3.6, 4.8]):
        x = -0.70 + 0.04 * math.cos(a)
        y = 0.70 + 0.04 * math.sin(a)
        cyl(f"Stem{i}", (x, y, 0.32), 0.012, 0.22, Mstem)
        sph(f"Bloom{i}", (x, y, 0.48), 0.05, Ml, (0.7, 0.7, 1.35))
    cyl("PotS1", (0.50, 0.78, 0.13), 0.055, 0.10, Mp)
    sph("PlS1", (0.50, 0.78, 0.24), 0.06, Mleaf)
    cyl("PotS2", (0.64, 0.70, 0.12), 0.05, 0.09, Mp)
    sph("PlS2", (0.64, 0.70, 0.22), 0.05, Ml)
    for i, (x, y, s) in enumerate([(-0.12, 1.12, 0.13), (0.08, 1.30, 0.11), (-0.02, 1.48, 0.10)]):
        sph(f"Stone{i}", (x, y, 0.03), s, Ms, (1.35, 1.05, 0.22))

    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            o.parent = root
            o.matrix_parent_inverse.identity()

    return root


def export_glb():
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
    log(f"promoted {GAME} sha={dig[:16]} bytes={GAME.stat().st_size}")
    data = json.loads(CAT.read_text(encoding="utf-8"))
    for m in data.get("modules", []):
        if m.get("module_id") == MODULE:
            m["glb_sha256"] = dig
            m["bytes"] = GAME.stat().st_size
            m["source"] = JOB
            m["visual"] = "mockup_house_v12_solid_gable"
    CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dig


def render_preview():
    w = bpy.data.worlds.new("W")
    bpy.context.scene.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.94, 0.90, 0.96, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    bpy.ops.object.camera_add(location=(3.0, 3.4, 2.4))
    cam = bpy.context.active_object
    d = Vector((0.0, 0.1, 0.9)) - Vector(cam.location)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 52
    bpy.context.scene.camera = cam
    bpy.ops.object.light_add(type="SUN", location=(3, 2, 6))
    sun = bpy.context.active_object
    sun.data.energy = 2.8
    sun.rotation_euler = Euler((math.radians(48), 0.2, 0.4), "XYZ")
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 40
    sc.cycles.use_denoising = True
    sc.render.resolution_x = 900
    sc.render.resolution_y = 900
    path = RENDER / f"{MODULE}_blender_preview_v12.png"
    sc.render.filepath = str(path)
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    log(f"preview {path.exists()}")


def main():
    log("start")
    build()
    dig = export_glb()
    try:
        render_preview()
    except Exception as e:
        log(f"preview fail {e}")
    log(f"DONE sha={dig[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

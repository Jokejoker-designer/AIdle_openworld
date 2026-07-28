# -*- coding: utf-8 -*-
"""Town MOCKUP_SSOT_V2 fidelity batch v1 — rebuild real production props/buildings.

Targets (HOME + GREENHOUSE priority first, then remaining real P1E):
  cozy_house_small_A, cozy_mailbox_A, cozy_garden_lamp_A, cozy_path_stone_A,
  cozy_greenhouse_A (full, not preview_anchor), cozy_flower_cluster_A,
  cozy_farm_plot_A, cozy_pond_small_A, cozy_fence_section_A, cozy_rock_small_A,
  cozy_tree_landmark_A

Godot-friendly: strong baseColor, low emission on structure, rough clay.
Iteration: TOWN_FIDELITY_BATCH_V1
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

JOB = "TOWN_FIDELITY_BATCH_V1"
GAME_MOD = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules")
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
CATALOG = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
RENDER = Path(
    r"E:\AIdle_openworld\orchestration\control\visual_reference\mockup_cast_props_001\gen"
)
QUAR.mkdir(parents=True, exist_ok=True)
RENDER.mkdir(parents=True, exist_ok=True)
GAME_MOD.mkdir(parents=True, exist_ok=True)

# SSOT palette
CREAM = (0.99, 0.95, 0.89)
PEACH = (0.99, 0.72, 0.42)
YELLOW = (1.0, 0.88, 0.40)
ROOF_C = (0.98, 0.78, 0.52)
LILAC = (0.78, 0.68, 0.93)
PURPLE = (0.72, 0.52, 0.90)
DOOR = (0.82, 0.52, 0.32)
FRAME = (0.92, 0.70, 0.50)
EMIT = (1.0, 0.78, 0.32)
WOOD = (0.78, 0.58, 0.40)
GREEN = (0.45, 0.72, 0.42)
LEAF = (0.40, 0.70, 0.38)
STONE = (0.82, 0.78, 0.72)
POT = (0.90, 0.58, 0.38)
LAV = (0.70, 0.48, 0.88)
CYAN = (0.45, 0.85, 0.95)
GLASS = (0.75, 0.90, 0.95)


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


def mat(name, rgb, rough=0.55, emit=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*rgb, alpha)
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = rough
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.2
        if emit > 0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (*rgb, 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emit
        if alpha < 0.99 and "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
            m.blend_method = "BLEND"
    return m


def setm(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)


def fin(o, m, bevel=0.04):
    setm(o, m)
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
    o.select_set(False)
    return o


def cube(name, loc, sc, m, bevel=0.05):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return fin(o, m, bevel)


def sph(name, loc, r, m, sc=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=16, ring_count=10)
    o = bpy.context.active_object
    o.name = name
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return fin(o, m, 0.0)


def cyl(name, loc, r, d, m, rot=None, verts=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=verts)
    o = bpy.context.active_object
    o.name = name
    if rot:
        o.rotation_euler = Euler(rot, "XYZ")
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return fin(o, m, 0.0)


def cone(name, loc, r1, r2, d, m):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=d, location=loc, vertices=12)
    o = bpy.context.active_object
    o.name = name
    return fin(o, m, 0.02)


def export_and_promote(module_id: str):
    path_q = QUAR / f"{module_id}.glb"
    path_g = GAME_MOD / f"{module_id}.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(path_q),
        export_format="GLB",
        use_selection=False,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        export_materials="EXPORT",
    )
    path_g.write_bytes(path_q.read_bytes())
    log(f"promoted {module_id} sha={sha(path_g)[:12]}… bytes={path_g.stat().st_size}")
    return path_g


def update_catalog_entries(entries: dict):
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    by_id = {m["module_id"]: m for m in data.get("modules", [])}
    for mid, meta in entries.items():
        p = GAME_MOD / f"{mid}.glb"
        if not p.exists():
            continue
        row = by_id.get(mid)
        if row is None:
            row = {"module_id": mid, "glb": f"res://assets/p1e_cozy/modules/{mid}.glb"}
            data.setdefault("modules", []).append(row)
            by_id[mid] = row
        row["glb"] = f"res://assets/p1e_cozy/modules/{mid}.glb"
        row["glb_sha256"] = sha(p)
        row["bytes"] = p.stat().st_size
        row["source"] = JOB
        row["visual"] = meta.get("visual", "mockup_ssot_v2_fidelity_batch_v1")
        row["mockup_ssot"] = meta.get("ssot", mid)
    data["town_fidelity_batch"] = JOB
    data["accepted"] = False
    data["self_accept"] = False
    CATALOG.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log("catalog updated")


# ─── builders ───────────────────────────────────────────────────────────────

def build_house():
    """cozy_house_small_A — SSOT bld_01_house clay cottage."""
    clear()
    Mw = mat("M_wall", CREAM, 0.72)
    Mb = mat("M_base", LILAC, 0.65)
    Mr1 = mat("M_roof_a", PEACH, 0.48)
    Mr2 = mat("M_roof_b", YELLOW, 0.48)
    Mr3 = mat("M_roof_c", ROOF_C, 0.50)
    Mridge = mat("M_ridge", (0.99, 0.94, 0.82), 0.55)
    Md = mat("M_door", DOOR, 0.5)
    Mf = mat("M_frame", FRAME, 0.5)
    Me = mat("M_emit", EMIT, 0.35, emit=3.5)
    Me2 = mat("M_emit2", (1.0, 0.90, 0.55), 0.3, emit=2.5)
    Mp = mat("M_pot", POT, 0.55)
    Ml = mat("M_lav", LAV, 0.55)
    Mleaf = mat("M_leaf", LEAF, 0.6)
    Mstem = mat("M_stem", (0.38, 0.55, 0.32), 0.65)
    Mmail = mat("M_mail", PURPLE, 0.45)
    Mstone = mat("M_stone", STONE, 0.7)
    Msmoke = mat("M_smoke", (0.80, 0.58, 0.94), 1.0, emit=0.15)
    Mchim = mat("M_chimney", CREAM, 0.7)
    Mdark = mat("M_dark", (0.38, 0.22, 0.14), 0.8)
    Mcurt = mat("M_curtain", (0.80, 0.50, 0.88), 0.7)
    Mknob = mat("M_knob", (1.0, 0.90, 0.45), 0.25, emit=0.3)

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_house_small_A"

    cube("Base", (0, 0, 0.05), (1.95, 1.75, 0.12), Mb, 0.14)
    cube("Body", (0, 0, 0.70), (1.30, 1.15, 1.18), Mw, 0.16)
    cube("Front", (0, 0.50, 0.55), (1.00, 0.20, 0.90), Mw, 0.12)

    # solid gable under tiles
    for sign, nm in ((1, "GableF"), (-1, "GableB")):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, sign * 0.28, 1.50))
        o = bpy.context.active_object
        o.name = nm
        o.scale = (1.52, 0.92, 0.14)
        o.rotation_euler = Euler((sign * math.radians(32), 0, 0), "XYZ")
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        fin(o, Mridge, 0.03)

    # fish-scale tiles — flatter disks (mockup scallops)
    mats_r = [Mr1, Mr2, Mr3]
    for row in range(8):
        t = row / 7.0
        y = 0.58 - t * 0.58
        z = 1.20 + t * 0.72
        for col in range(10):
            x = (col - 4.5) * 0.155
            if row % 2:
                x += 0.07
            if abs(x) > 0.80:
                continue
            m = mats_r[(row + col) % 3]
            o = sph(f"T{row}_{col}", (x, y, z), 0.115, m, (1.55, 1.30, 0.26))
            o.rotation_euler = Euler((math.radians(-32), 0, 0), "XYZ")

    for i, x in enumerate([-0.45, -0.22, 0, 0.22, 0.45]):
        sph(f"Ridge{i}", (x, 0.0, 1.90), 0.08, Mridge, (1.2, 1.0, 0.65))

    cube("Chimney", (0.38, -0.12, 1.98), (0.20, 0.20, 0.42), Mchim, 0.04)
    cube("ChimCap", (0.38, -0.12, 2.18), (0.26, 0.26, 0.07), Mchim, 0.03)
    for i, (dx, dy, dz, s) in enumerate([
        (0.0, 0.0, 0.10, 0.07), (0.06, 0.04, 0.20, 0.10),
        (0.12, 0.08, 0.30, 0.08), (0.18, 0.12, 0.38, 0.06), (0.24, 0.16, 0.44, 0.04),
    ]):
        sph(f"Sm{i}", (0.38 + dx, -0.12 + dy, 2.24 + dz), s, Msmoke)

    # door solid (no black cavities)
    cube("DoorFill", (0, 0.48, 0.50), (0.50, 0.16, 0.85), Mw, 0.05)
    cube("DoorFrame", (0, 0.58, 0.52), (0.46, 0.06, 0.86), Mf, 0.05)
    cube("Door", (0, 0.62, 0.50), (0.34, 0.05, 0.68), Md, 0.05)
    sph("DoorArch", (0, 0.64, 0.90), 0.20, Mf, (1.0, 0.35, 0.55))
    sph("Knob", (0.11, 0.68, 0.48), 0.04, Mknob)
    cube("Step1", (0, 0.76, 0.10), (0.38, 0.16, 0.07), Mf, 0.03)
    cube("Step2", (0, 0.88, 0.05), (0.30, 0.12, 0.05), Mf, 0.02)

    for nm, x, z, rr in [("W1", -0.36, 0.68, 0.095), ("W2", 0.36, 0.46, 0.085),
                         ("W3", -0.26, 1.00, 0.09), ("W4", 0.0, 1.24, 0.10)]:
        cyl(f"{nm}f", (x, 0.60, z), rr + 0.02, 0.04, Mf, rot=(math.pi / 2, 0, 0))
        sph(f"{nm}g", (x, 0.64, z), rr, Me if nm != "W4" else Me2)

    cube("SideFill", (0.60, 0.0, 0.74), (0.12, 0.50, 0.42), Mdark, 0.02)
    cube("SideFrame", (0.66, 0.0, 0.74), (0.07, 0.54, 0.46), Mf, 0.03)
    cube("SideGlow", (0.70, 0.0, 0.74), (0.04, 0.46, 0.38), Me, 0.01)
    cube("CurtL", (0.64, -0.16, 0.78), (0.04, 0.07, 0.34), Mcurt, 0.02)
    cube("CurtR", (0.64, 0.18, 0.78), (0.04, 0.07, 0.34), Mcurt, 0.02)
    cyl("Lamp", (0.52, 0.08, 0.58), 0.03, 0.08, Mp)
    sph("LampG", (0.52, 0.08, 0.66), 0.06, Me2, (1, 1, 0.7))
    cyl("InPot", (0.52, -0.08, 0.55), 0.035, 0.05, Mp)
    sph("InLeaf", (0.52, -0.08, 0.62), 0.045, Mleaf)

    cyl("MailPost", (0.28, 0.76, 0.15), 0.022, 0.18, Mmail)
    cube("MailBox", (0.28, 0.76, 0.28), (0.14, 0.10, 0.11), Mmail, 0.03)
    cube("MailFlag", (0.36, 0.76, 0.32), (0.03, 0.02, 0.07), Ml, 0.01)

    cyl("PotBig", (-0.66, 0.68, 0.15), 0.10, 0.15, Mp)
    for i, a in enumerate([0, 1.25, 2.5, 3.8, 5.0]):
        x = -0.66 + 0.04 * math.cos(a)
        y = 0.68 + 0.04 * math.sin(a)
        cyl(f"Stem{i}", (x, y, 0.30), 0.011, 0.20, Mstem)
        sph(f"Bloom{i}", (x, y, 0.44), 0.045, Ml, (0.7, 0.7, 1.3))
    cyl("PotS1", (0.48, 0.76, 0.12), 0.05, 0.09, Mp)
    sph("PlS1", (0.48, 0.76, 0.22), 0.055, Mleaf)
    cyl("PotS2", (0.60, 0.68, 0.11), 0.045, 0.08, Mp)
    sph("PlS2", (0.60, 0.68, 0.20), 0.045, Ml)

    for i, (x, y, s) in enumerate([(-0.10, 1.10, 0.12), (0.08, 1.28, 0.10), (-0.02, 1.45, 0.09)]):
        sph(f"Stone{i}", (x, y, 0.03), s, Mstone, (1.3, 1.0, 0.22))

    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            o.parent = root
            o.matrix_parent_inverse.identity()
    return export_and_promote("cozy_house_small_A")


def build_mailbox():
    """cozy_mailbox_A — purple SSOT prop_mailbox."""
    clear()
    Mpur = mat("M_mail", (0.70, 0.50, 0.90), 0.4)
    Mcream = mat("M_post", CREAM, 0.55)
    Mgold = mat("M_gold", (0.95, 0.78, 0.30), 0.3, emit=0.2)
    Mp = mat("M_pot", POT, 0.55)
    Ml = mat("M_lav", LAV, 0.55)
    Mg = mat("M_green", GREEN, 0.55)
    Ms = mat("M_stone", STONE, 0.7)

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_mailbox_A"

    # cream pedestal
    cyl("Post", (0, 0, 0.28), 0.12, 0.55, Mcream, verts=20)
    sph("PostBulge", (0, 0, 0.55), 0.14, Mcream, (1.0, 1.0, 0.7))
    # purple box (rounded)
    cube("Box", (0, 0, 0.85), (0.55, 0.40, 0.42), Mpur, 0.12)
    # dome top
    sph("Dome", (0, 0, 1.05), 0.28, Mpur, (1.05, 0.85, 0.55))
    # door panel + knob
    cube("Door", (0, 0.21, 0.82), (0.32, 0.04, 0.22), Mpur, 0.04)
    sph("Knob", (0, 0.25, 0.82), 0.04, Mgold)
    # flag
    cube("FlagArm", (0.30, 0.0, 0.90), (0.06, 0.04, 0.18), Mcream, 0.02)
    cube("Flag", (0.32, 0.0, 1.00), (0.04, 0.05, 0.14), Mcream, 0.02)
    sph("FlagBolt", (0.28, 0.05, 0.85), 0.035, Mgold)

    # pots + lavender
    for i, (x, y) in enumerate([(-0.35, 0.25), (0.32, -0.22)]):
        cyl(f"Pot{i}", (x, y, 0.08), 0.08, 0.12, Mp)
        for j in range(3):
            a = j * 2.0
            sx = x + 0.03 * math.cos(a)
            sy = y + 0.03 * math.sin(a)
            cyl(f"St{i}_{j}", (sx, sy, 0.18), 0.01, 0.14, Mg)
            sph(f"Bl{i}_{j}", (sx, sy, 0.28), 0.035, Ml, (0.7, 0.7, 1.2))

    for i, (x, y, s) in enumerate([(-0.2, 0.4, 0.08), (0.15, 0.45, 0.07), (0.35, 0.3, 0.07),
                                    (-0.35, -0.15, 0.07), (0.25, -0.4, 0.08)]):
        sph(f"Stn{i}", (x, y, 0.02), s, Ms, (1.3, 1.1, 0.25))

    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            o.parent = root
            o.matrix_parent_inverse.identity()
    return export_and_promote("cozy_mailbox_A")


def build_garden_lamp():
    """cozy_garden_lamp_A — cream cyber lantern SSOT."""
    clear()
    Mcream = mat("M_post", (0.94, 0.88, 0.78), 0.5)
    Mstone = mat("M_base", (0.55, 0.58, 0.55), 0.7)
    Memit = mat("M_emit", (1.0, 0.85, 0.45), 0.3, emit=4.0)
    Mleaf = mat("M_leaf", (0.55, 0.78, 0.55), 0.55)
    Mvine = mat("M_vine", (0.45, 0.70, 0.50), 0.6)
    Mc = mat("M_cyan", CYAN, 0.4, emit=0.4)
    Mgrass = mat("M_grass", (0.40, 0.65, 0.38), 0.65)

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_garden_lamp_A"

    cube("Base", (0, 0, 0.04), (0.55, 0.55, 0.08), Mstone, 0.04)
    cube("BaseGrass", (0, 0, 0.06), (0.50, 0.50, 0.04), Mgrass, 0.03)
    # post
    cyl("Post", (0, 0, 0.70), 0.07, 1.25, Mcream, verts=12)
    cube("PostMid", (0, 0, 0.55), (0.18, 0.18, 0.12), Mcream, 0.03)
    cube("PostTop", (0, 0, 1.25), (0.16, 0.16, 0.10), Mcream, 0.03)
    # arm
    cube("Arm", (0.22, 0, 1.22), (0.45, 0.06, 0.06), Mcream, 0.02)
    # scroll
    sph("Scroll", (0.15, 0.08, 1.28), 0.06, Mcream, (1.2, 0.8, 0.6))
    # lantern
    cube("Lantern", (0.42, 0, 1.05), (0.22, 0.22, 0.28), Mcream, 0.04)
    sph("Glow", (0.42, 0, 1.05), 0.10, Memit)
    # cyan accents
    cube("Cyan1", (0.0, 0.08, 0.40), (0.02, 0.02, 0.20), Mc, 0.01)
    cube("Cyan2", (0.0, -0.08, 0.70), (0.02, 0.02, 0.15), Mc, 0.01)
    # vines
    for i, z in enumerate([0.35, 0.55, 0.75, 0.95]):
        sph(f"Leaf{i}", (0.10 + 0.02 * i, 0.08, z), 0.04, Mleaf, (1.2, 0.7, 0.5))
        cyl(f"Vine{i}", (0.08, 0.06, z - 0.05), 0.012, 0.12, Mvine, rot=(0.5, 0, 0.3))

    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            o.parent = root
            o.matrix_parent_inverse.identity()
    return export_and_promote("cozy_garden_lamp_A")


def build_path_stone():
    clear()
    Ms1 = mat("M_stone1", (0.88, 0.84, 0.78), 0.7)
    Ms2 = mat("M_stone2", (0.80, 0.76, 0.70), 0.72)
    Ms3 = mat("M_stone3", (0.92, 0.88, 0.82), 0.68)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_path_stone_A"
    mats = [Ms1, Ms2, Ms3]
    for i, (x, y, s) in enumerate([
        (0.0, 0.0, 0.22), (0.28, 0.12, 0.18), (-0.25, 0.15, 0.17),
        (0.15, -0.25, 0.16), (-0.15, -0.22, 0.15), (0.35, -0.1, 0.14),
    ]):
        sph(f"S{i}", (x, y, 0.03), s, mats[i % 3], (1.4, 1.2, 0.28))
    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            o.parent = root
            o.matrix_parent_inverse.identity()
    return export_and_promote("cozy_path_stone_A")


def build_greenhouse():
    """Full cozy_greenhouse_A + also write as preview_anchor alias target."""
    clear()
    Mf = mat("M_frame", CREAM, 0.5)
    Mg = mat("M_glass", (0.70, 0.88, 0.95), 0.15, emit=0.3, alpha=0.45)
    Mb = mat("M_base", LILAC, 0.65)
    Md = mat("M_door", FRAME, 0.5)
    Me = mat("M_emit", EMIT, 0.35, emit=2.0)
    Mp = mat("M_pot", POT, 0.55)
    Mleaf = mat("M_leaf", LEAF, 0.55)
    Mpur = mat("M_flower", LAV, 0.5)
    Msmoke = mat("M_smoke", (0.95, 0.92, 0.98), 1.0, emit=0.1)
    Mchim = mat("M_chim", CREAM, 0.6)

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_greenhouse_A"

    cube("Base", (0, 0, 0.05), (1.9, 1.5, 0.10), Mb, 0.12)
    # frame walls
    cube("BotF", (0, 0.65, 0.55), (1.6, 0.08, 0.9), Mf, 0.04)
    cube("BotB", (0, -0.65, 0.55), (1.6, 0.08, 0.9), Mf, 0.04)
    cube("BotL", (-0.78, 0, 0.55), (0.08, 1.3, 0.9), Mf, 0.04)
    cube("BotR", (0.78, 0, 0.55), (0.08, 1.3, 0.9), Mf, 0.04)
    # glass panes
    cube("GlassF", (0, 0.68, 0.55), (1.5, 0.03, 0.85), Mg, 0.01)
    cube("GlassB", (0, -0.68, 0.55), (1.5, 0.03, 0.85), Mg, 0.01)
    cube("GlassL", (-0.80, 0, 0.55), (0.03, 1.2, 0.85), Mg, 0.01)
    cube("GlassR", (0.80, 0, 0.55), (0.03, 1.2, 0.85), Mg, 0.01)
    # roof slopes
    for sign, nm in ((1, "RoofF"), (-1, "RoofB")):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, sign * 0.35, 1.35))
        o = bpy.context.active_object
        o.name = nm
        o.scale = (1.7, 0.85, 0.08)
        o.rotation_euler = Euler((sign * math.radians(35), 0, 0), "XYZ")
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        fin(o, Mf, 0.03)
    cube("RoofGlassF", (0, 0.30, 1.32), (1.5, 0.6, 0.04), Mg, 0.01)
    cube("RoofGlassB", (0, -0.30, 1.32), (1.5, 0.6, 0.04), Mg, 0.01)
    # muntins
    for x in [-0.4, 0, 0.4]:
        cube(f"MunF{x}", (x, 0.66, 0.55), (0.04, 0.04, 0.85), Mf, 0.01)
    cube("MunH", (0, 0.66, 0.55), (1.5, 0.04, 0.04), Mf, 0.01)
    # door
    cube("Door", (0, 0.72, 0.35), (0.35, 0.05, 0.55), Md, 0.04)
    sph("Knob", (0.12, 0.76, 0.35), 0.04, mat("M_gold", (0.95, 0.8, 0.3), 0.3, emit=0.2))
    # chimney
    cube("Chim", (-0.35, -0.1, 1.70), (0.18, 0.18, 0.35), Mchim, 0.03)
    for i, z in enumerate([0.1, 0.22, 0.34]):
        sph(f"Sm{i}", (-0.35, -0.05, 1.95 + z), 0.08 - i * 0.015, Msmoke)
    # interior plants
    for i, (x, y) in enumerate([(-0.4, 0.2), (0.3, -0.2), (0.0, 0.0), (-0.2, -0.3), (0.4, 0.25)]):
        cyl(f"Pot{i}", (x, y, 0.15), 0.08, 0.12, Mp)
        sph(f"Plant{i}", (x, y, 0.32), 0.12, Mleaf if i % 2 == 0 else Mpur)
    # warm glow center
    sph("Glow", (0, 0, 0.7), 0.25, Me)

    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            o.parent = root
            o.matrix_parent_inverse.identity()
    p = export_and_promote("cozy_greenhouse_A")
    # also write as preview_anchor so alias still works
    (GAME_MOD / "cozy_greenhouse_preview_anchor_A.glb").write_bytes(p.read_bytes())
    (QUAR / "cozy_greenhouse_preview_anchor_A.glb").write_bytes(p.read_bytes())
    log("also wrote cozy_greenhouse_preview_anchor_A.glb (alias target)")
    return p


def build_flower_cluster():
    clear()
    Mp = mat("M_pot", POT, 0.55)
    Ml = mat("M_lav", LAV, 0.5)
    Mpink = mat("M_pink", (0.95, 0.55, 0.70), 0.5)
    My = mat("M_yel", YELLOW, 0.5)
    Mg = mat("M_stem", GREEN, 0.6)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_flower_cluster_A"
    for i, (x, y) in enumerate([(0, 0), (0.2, 0.1), (-0.18, 0.12), (0.1, -0.18), (-0.12, -0.15)]):
        cyl(f"Pot{i}", (x, y, 0.08), 0.07, 0.12, Mp)
        for j in range(4):
            a = j * 1.5
            sx = x + 0.03 * math.cos(a)
            sy = y + 0.03 * math.sin(a)
            cyl(f"St{i}_{j}", (sx, sy, 0.20), 0.01, 0.16, Mg)
            m = [Ml, Mpink, My][(i + j) % 3]
            sph(f"Fl{i}_{j}", (sx, sy, 0.32), 0.04, m)
    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            o.parent = root
            o.matrix_parent_inverse.identity()
    return export_and_promote("cozy_flower_cluster_A")


def build_farm_plot():
    clear()
    Msoil = mat("M_soil", (0.45, 0.32, 0.22), 0.8)
    Mwood = mat("M_wood", WOOD, 0.55)
    Mg = mat("M_crop", GREEN, 0.55)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_farm_plot_A"
    cube("Soil", (0, 0, 0.06), (1.2, 0.9, 0.12), Msoil, 0.04)
    for side, sc in [
        ((0, 0.48, 0.1), (1.25, 0.08, 0.12)),
        ((0, -0.48, 0.1), (1.25, 0.08, 0.12)),
        ((0.62, 0, 0.1), (0.08, 0.95, 0.12)),
        ((-0.62, 0, 0.1), (0.08, 0.95, 0.12)),
    ]:
        cube(f"Rail{side}", side[0], sc, Mwood, 0.02)
    for i, x in enumerate([-0.35, 0, 0.35]):
        for j, y in enumerate([-0.25, 0.1, 0.3]):
            cyl(f"C{i}_{j}", (x, y, 0.18), 0.03, 0.12, Mg)
            sph(f"L{i}_{j}", (x, y, 0.28), 0.05, Mg)
    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            o.parent = root
            o.matrix_parent_inverse.identity()
    return export_and_promote("cozy_farm_plot_A")


def build_pond():
    clear()
    Mw = mat("M_water", (0.45, 0.72, 0.90), 0.2, emit=0.4)
    Ms = mat("M_stone", STONE, 0.7)
    Mg = mat("M_leaf", LEAF, 0.55)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_pond_small_A"
    sph("Water", (0, 0, 0.05), 0.55, Mw, (1.4, 1.2, 0.2))
    for i, a in enumerate(range(8)):
        ang = a * math.pi / 4
        sph(f"Rock{i}", (0.5 * math.cos(ang), 0.45 * math.sin(ang), 0.04), 0.12, Ms, (1.2, 1.0, 0.4))
    sph("Lily", (0.15, -0.1, 0.08), 0.1, Mg, (1.5, 1.5, 0.2))
    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            o.parent = root
            o.matrix_parent_inverse.identity()
    return export_and_promote("cozy_pond_small_A")


def build_fence():
    clear()
    Mw = mat("M_wood", WOOD, 0.55)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_fence_section_A"
    for i, x in enumerate([-0.5, 0, 0.5]):
        cyl(f"Post{i}", (x, 0, 0.35), 0.05, 0.7, Mw, verts=8)
    cube("RailTop", (0, 0, 0.55), (1.2, 0.06, 0.06), Mw, 0.02)
    cube("RailBot", (0, 0, 0.25), (1.2, 0.06, 0.06), Mw, 0.02)
    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            o.parent = root
            o.matrix_parent_inverse.identity()
    return export_and_promote("cozy_fence_section_A")


def build_rock():
    clear()
    Ms = mat("M_stone", (0.70, 0.68, 0.64), 0.75)
    Ms2 = mat("M_stone2", (0.62, 0.60, 0.56), 0.78)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_rock_small_A"
    sph("R1", (0, 0, 0.12), 0.22, Ms, (1.3, 1.1, 0.85))
    sph("R2", (0.15, 0.08, 0.08), 0.12, Ms2, (1.2, 1.0, 0.7))
    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            o.parent = root
            o.matrix_parent_inverse.identity()
    return export_and_promote("cozy_rock_small_A")


def build_tree_landmark():
    clear()
    Mt = mat("M_trunk", (0.55, 0.38, 0.25), 0.7)
    Ml = mat("M_leaf", (0.42, 0.72, 0.40), 0.55)
    Ml2 = mat("M_leaf2", (0.55, 0.80, 0.45), 0.55)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_tree_landmark_A"
    cyl("Trunk", (0, 0, 0.35), 0.12, 0.7, Mt, verts=10)
    sph("Canopy", (0, 0, 1.0), 0.55, Ml, (1.2, 1.2, 1.0))
    sph("Canopy2", (0.2, 0.1, 1.15), 0.35, Ml2)
    sph("Canopy3", (-0.15, -0.1, 1.2), 0.30, Ml)
    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            o.parent = root
            o.matrix_parent_inverse.identity()
    return export_and_promote("cozy_tree_landmark_A")


def main():
    log("start fidelity batch v1")
    builders = [
        ("cozy_house_small_A", build_house, "buildings/bld_01_house.jpg"),
        ("cozy_mailbox_A", build_mailbox, "props/prop_mailbox.jpg"),
        ("cozy_garden_lamp_A", build_garden_lamp, "props/prop_garden_lamp.jpg"),
        ("cozy_path_stone_A", build_path_stone, "props/prop_path_stone.jpg"),
        ("cozy_greenhouse_A", build_greenhouse, "buildings/bld_02_greenhouse.jpg"),
        ("cozy_flower_cluster_A", build_flower_cluster, "props/prop_flower_cluster.jpg"),
        ("cozy_farm_plot_A", build_farm_plot, "props/prop_farm_plot.jpg"),
        ("cozy_pond_small_A", build_pond, "props/prop_pond.jpg"),
        ("cozy_fence_section_A", build_fence, "props/prop_fence.jpg"),
        ("cozy_rock_small_A", build_rock, "props/prop_rock_small.jpg"),
        ("cozy_tree_landmark_A", build_tree_landmark, "props/prop_tree_landmark.jpg"),
    ]
    results = {}
    for mid, fn, ssot in builders:
        try:
            p = fn()
            results[mid] = {
                "ok": True,
                "sha256": sha(p),
                "bytes": p.stat().st_size,
                "ssot_img": ssot,
                "visual": f"mockup_fidelity_{JOB}",
            }
            log(f"OK {mid}")
        except Exception as e:
            results[mid] = {"ok": False, "error": str(e)}
            log(f"FAIL {mid}: {e}")
            import traceback
            traceback.print_exc()
    update_catalog_entries(results)
    # greenhouse alias catalog entry
    if (GAME_MOD / "cozy_greenhouse_preview_anchor_A.glb").exists():
        p = GAME_MOD / "cozy_greenhouse_preview_anchor_A.glb"
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        for m in data.get("modules", []):
            if m.get("module_id") == "cozy_greenhouse_preview_anchor_A":
                m["glb_sha256"] = sha(p)
                m["bytes"] = p.stat().st_size
                m["source"] = JOB
                m["visual"] = "full_greenhouse_as_alias_target"
        CATALOG.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    out = QUAR / "batch_result.json"
    out.write_text(
        json.dumps({"job": JOB, "results": results, "accepted": False}, indent=2),
        encoding="utf-8",
    )
    log("DONE " + json.dumps({k: v.get("ok") for k, v in results.items()}))
    return 0 if all(v.get("ok") for v in results.values()) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        log(f"FATAL {e}")
        import traceback
        traceback.print_exc()
        raise SystemExit(1)

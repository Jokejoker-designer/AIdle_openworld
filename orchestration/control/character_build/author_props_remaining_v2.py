# -*- coding: utf-8 -*-
"""PROPS_REMAINING_V2 — mailbox, fence, farm, greenhouse, path, flower, tree toward SSOT."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Euler

JOB = "PROPS_REMAINING_V2"
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


def mat(n, rgb, rough=0.55, emit=0.0, alpha=1.0):
    m = bpy.data.materials.new(n)
    m.use_nodes = True
    m.diffuse_color = (*rgb, alpha)
    b = next((x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED"), None)
    if b:
        b.inputs["Base Color"].default_value = (*rgb, alpha)
        if "Roughness" in b.inputs:
            b.inputs["Roughness"].default_value = rough
        if emit > 0:
            if "Emission Color" in b.inputs:
                b.inputs["Emission Color"].default_value = (*rgb, 1.0)
            if "Emission Strength" in b.inputs:
                b.inputs["Emission Strength"].default_value = emit
        if alpha < 1.0 and "Alpha" in b.inputs:
            b.inputs["Alpha"].default_value = alpha
            m.blend_method = "BLEND"
    return m


def setm(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)
    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass


def cube(n, loc, sc, m, bevel=0.03):
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
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=14, ring_count=10)
    o = bpy.context.active_object
    o.name = n
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    setm(o, m)
    return o


def cyl(n, loc, r, d, m, verts=12, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=verts)
    o = bpy.context.active_object
    o.name = n
    if rot != (0, 0, 0):
        o.rotation_euler = Euler(rot)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    setm(o, m)
    return o


def parent_all(root):
    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            mw = o.matrix_world.copy()
            o.parent = root
            o.matrix_world = mw


def promote(mid, visual):
    q = QUAR / f"{mid}.glb"
    dest = GAME_MOD / f"{mid}.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(q), export_format="GLB", use_selection=False,
        export_apply=True, export_cameras=False, export_lights=False, export_materials="EXPORT",
    )
    dest.write_bytes(q.read_bytes())
    dig = sha(dest)
    data = json.loads(CAT.read_text(encoding="utf-8"))
    for m in data.get("modules", []):
        if m.get("module_id") == mid:
            m["glb_sha256"] = dig
            m["bytes"] = dest.stat().st_size
            m["source"] = JOB
            m["visual"] = visual
    CAT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"{mid} sha={dig[:16]} bytes={dest.stat().st_size}")
    return dig


def build_mailbox():
    """SSOT: purple dome mailbox, cream post, gold knobs, flag, pots, stones."""
    clear()
    Mpost = mat("M_post", (0.96, 0.90, 0.78), 0.55)
    Mmail = mat("M_mail", (0.68, 0.42, 0.92), 0.4)
    Mdoor = mat("M_door", (0.62, 0.38, 0.88), 0.45)
    Mflag = mat("M_flag", (0.98, 0.92, 0.75), 0.5)
    Mknob = mat("M_knob", (1.0, 0.84, 0.28), 0.3, emit=0.8)
    Mpot = mat("M_pot", (0.90, 0.55, 0.32), 0.55)
    Mlav = mat("M_lav", (0.72, 0.42, 0.90), 0.5)
    Mleaf = mat("M_leaf", (0.40, 0.72, 0.38), 0.55)
    Mstone = mat("M_stone", (0.86, 0.80, 0.72), 0.7)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_mailbox_A"
    # base pad
    cube("Pad", (0, 0, 0.03), (0.55, 0.55, 0.06), mat("M_base", (0.75, 0.58, 0.92), 0.6), 0.04)
    cyl("Post", (0, 0, 0.35), 0.055, 0.55, Mpost)
    cube("Collar", (0, 0, 0.58), (0.14, 0.14, 0.08), Mpost, 0.02)
    # dome body
    sph("Dome", (0, 0, 0.82), 0.22, Mmail, (1.15, 0.95, 0.85))
    cube("Body", (0, 0, 0.70), (0.38, 0.28, 0.22), Mmail, 0.05)
    # door face
    cube("Door", (0, 0.16, 0.72), (0.28, 0.04, 0.18), Mdoor, 0.02)
    sph("Knob1", (0.10, 0.20, 0.72), 0.035, Mknob)
    sph("Knob2", (-0.08, 0.18, 0.78), 0.03, Mknob)
    # flag
    cyl("FlagPole", (0.22, 0, 0.78), 0.015, 0.18, Mflag)
    cube("Flag", (0.30, 0, 0.88), (0.12, 0.02, 0.08), Mflag, 0.01)
    # pots
    for i, (x, y) in enumerate([(-0.22, 0.18), (0.20, 0.16)]):
        cyl(f"Pot{i}", (x, y, 0.10), 0.055, 0.10, Mpot)
        for j in range(3):
            a = j * 2.1
            cyl(f"St{i}_{j}", (x + 0.02 * math.cos(a), y + 0.02 * math.sin(a), 0.22), 0.01, 0.14, Mleaf)
            sph(f"Bl{i}_{j}", (x + 0.02 * math.cos(a), y + 0.02 * math.sin(a), 0.32), 0.035, Mlav, (0.7, 0.7, 1.2))
    for i, (x, y, s) in enumerate([(-0.05, 0.28, 0.08), (0.12, 0.30, 0.07), (-0.15, -0.22, 0.075)]):
        sph(f"Sn{i}", (x, y, 0.03), s, Mstone, (1.3, 1.1, 0.3))
    parent_all(root)
    return promote("cozy_mailbox_A", "mockup_mailbox_v2")


def build_fence():
    """SSOT: ornate brown posts + rails + finials."""
    clear()
    Mw = mat("M_wood", (0.62, 0.42, 0.26), 0.55)
    Mw2 = mat("M_wood2", (0.55, 0.36, 0.22), 0.58)
    Mfin = mat("M_finial", (0.72, 0.50, 0.30), 0.5)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_fence_section_A"
    for i, x in enumerate([-0.55, 0.0, 0.55]):
        cyl(f"Post{i}", (x, 0, 0.38), 0.055, 0.76, Mw if i != 1 else Mw2, verts=10)
        sph(f"Fin{i}", (x, 0, 0.80), 0.07, Mfin)
        cube(f"Cap{i}", (x, 0, 0.72), (0.12, 0.12, 0.06), Mw, 0.02)
    cube("RailTop", (0, 0, 0.58), (1.25, 0.07, 0.07), Mw, 0.02)
    cube("RailMid", (0, 0, 0.38), (1.25, 0.06, 0.06), Mw2, 0.02)
    cube("RailBot", (0, 0, 0.20), (1.25, 0.07, 0.07), Mw, 0.02)
    # cross braces
    for i, x in enumerate([-0.28, 0.28]):
        cube(f"Brace{i}", (x, 0, 0.40), (0.05, 0.05, 0.35), Mw2, 0.01)
    parent_all(root)
    return promote("cozy_fence_section_A", "mockup_fence_v2")


def build_farm():
    clear()
    Msoil = mat("M_soil", (0.42, 0.30, 0.20), 0.8)
    Mwood = mat("M_wood", (0.65, 0.45, 0.28), 0.55)
    Mg = mat("M_crop", (0.35, 0.72, 0.32), 0.55)
    Mg2 = mat("M_crop2", (0.45, 0.80, 0.38), 0.55)
    Mleaf = mat("M_leaf", (0.30, 0.65, 0.28), 0.55)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_farm_plot_A"
    cube("Soil", (0, 0, 0.06), (1.35, 1.0, 0.14), Msoil, 0.05)
    # raised bed rails
    for nm, loc, sc in [
        ("RT", (0, 0.52, 0.12), (1.4, 0.09, 0.14)),
        ("RB", (0, -0.52, 0.12), (1.4, 0.09, 0.14)),
        ("RL", (0.68, 0, 0.12), (0.09, 1.05, 0.14)),
        ("RR", (-0.68, 0, 0.12), (0.09, 1.05, 0.14)),
    ]:
        cube(nm, loc, sc, Mwood, 0.02)
    # denser crop rows
    for i, x in enumerate([-0.40, -0.13, 0.13, 0.40]):
        for j, y in enumerate([-0.30, -0.05, 0.20, 0.35]):
            cyl(f"C{i}_{j}", (x, y, 0.18), 0.035, 0.14, Mg if (i + j) % 2 == 0 else Mg2)
            sph(f"L{i}_{j}", (x, y, 0.30), 0.06, Mleaf if (i + j) % 2 else Mg2)
            sph(f"L2{i}_{j}", (x + 0.03, y - 0.02, 0.32), 0.04, Mg)
    parent_all(root)
    return promote("cozy_farm_plot_A", "mockup_farm_v2")


def build_greenhouse():
    clear()
    Mf = mat("M_frame", (0.96, 0.90, 0.80), 0.5)
    Mg = mat("M_glass", (0.55, 0.82, 0.95), 0.15, emit=0.4, alpha=0.5)
    Mb = mat("M_base", (0.70, 0.52, 0.92), 0.62)
    Md = mat("M_door", (0.88, 0.62, 0.42), 0.5)
    Me = mat("M_emit", (1.0, 0.82, 0.35), 0.35, emit=3.0)
    Mp = mat("M_pot", (0.90, 0.55, 0.32), 0.55)
    Mleaf = mat("M_leaf", (0.35, 0.72, 0.32), 0.55)
    Mpur = mat("M_flower", (0.72, 0.42, 0.90), 0.5)
    Msmoke = mat("M_smoke", (0.90, 0.70, 0.95), 1.0, emit=0.2)
    Mchim = mat("M_chim", (0.96, 0.90, 0.82), 0.6)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_greenhouse_A"
    cube("Base", (0, 0, 0.05), (2.0, 1.55, 0.10), Mb, 0.12)
    # walls frames
    for nm, loc, sc in [
        ("BotF", (0, 0.68, 0.55), (1.7, 0.08, 0.95)),
        ("BotB", (0, -0.68, 0.55), (1.7, 0.08, 0.95)),
        ("BotL", (-0.82, 0, 0.55), (0.08, 1.35, 0.95)),
        ("BotR", (0.82, 0, 0.55), (0.08, 1.35, 0.95)),
    ]:
        cube(nm, loc, sc, Mf, 0.03)
    for nm, loc, sc in [
        ("GlassF", (0, 0.72, 0.55), (1.55, 0.03, 0.88)),
        ("GlassB", (0, -0.72, 0.55), (1.55, 0.03, 0.88)),
        ("GlassL", (-0.84, 0, 0.55), (0.03, 1.25, 0.88)),
        ("GlassR", (0.84, 0, 0.55), (0.03, 1.25, 0.88)),
    ]:
        cube(nm, loc, sc, Mg, 0.01)
    # roof prism-like via cubes (no rotation for Godot safety)
    for sign, nm in ((1, "RoofF"), (-1, "RoofB")):
        # approximate slope with stepped flat panels
        cube(f"{nm}1", (0, sign * 0.40, 1.15), (1.8, 0.55, 0.08), Mf, 0.02)
        cube(f"{nm}2", (0, sign * 0.20, 1.40), (1.8, 0.45, 0.08), Mf, 0.02)
        cube(f"{nm}G", (0, sign * 0.30, 1.28), (1.55, 0.40, 0.04), Mg, 0.01)
    cube("Ridge", (0, 0, 1.55), (1.85, 0.12, 0.10), Mf, 0.02)
    for x in [-0.45, 0, 0.45]:
        cube(f"Mun{x}", (x, 0.70, 0.55), (0.04, 0.04, 0.88), Mf, 0.01)
    cube("MunH", (0, 0.70, 0.55), (1.55, 0.04, 0.04), Mf, 0.01)
    cube("Door", (0, 0.76, 0.35), (0.38, 0.06, 0.58), Md, 0.04)
    sph("Knob", (0.12, 0.80, 0.35), 0.04, mat("M_gold", (0.95, 0.8, 0.3), 0.3, emit=0.3))
    cube("Chim", (-0.38, -0.12, 1.75), (0.20, 0.20, 0.40), Mchim, 0.03)
    for i, z in enumerate([0.1, 0.24, 0.38]):
        sph(f"Sm{i}", (-0.38, -0.08, 2.0 + z), 0.09 - i * 0.015, Msmoke)
    for i, (x, y) in enumerate([(-0.4, 0.2), (0.3, -0.2), (0.0, 0.0), (-0.2, -0.3), (0.4, 0.25), (0.15, 0.3)]):
        cyl(f"Pot{i}", (x, y, 0.15), 0.09, 0.14, Mp)
        sph(f"Plant{i}", (x, y, 0.35), 0.14, Mleaf if i % 2 == 0 else Mpur)
        sph(f"Plant2{i}", (x + 0.05, y, 0.42), 0.08, Mpur if i % 2 == 0 else Mleaf)
    sph("Glow", (0, 0, 0.75), 0.28, Me)
    parent_all(root)
    p = GAME_MOD / "cozy_greenhouse_A.glb"
    dig = promote("cozy_greenhouse_A", "mockup_greenhouse_v2")
    # alias
    (GAME_MOD / "cozy_greenhouse_preview_anchor_A.glb").write_bytes(p.read_bytes())
    return dig


def build_path():
    clear()
    Ms1 = mat("M_stone1", (0.88, 0.82, 0.72), 0.72)
    Ms2 = mat("M_stone2", (0.75, 0.70, 0.62), 0.74)
    Ms3 = mat("M_stone3", (0.92, 0.88, 0.80), 0.70)
    Mmoss = mat("M_moss", (0.40, 0.65, 0.35), 0.6)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_path_stone_A"
    stones = [
        (0.0, 0.0, 0.28), (0.35, 0.15, 0.22), (-0.32, 0.20, 0.21),
        (0.20, -0.30, 0.20), (-0.20, -0.28, 0.19), (0.45, -0.12, 0.17),
        (-0.45, -0.08, 0.18), (0.10, 0.35, 0.16), (-0.08, 0.38, 0.15),
        (0.28, 0.32, 0.14),
    ]
    mats = [Ms1, Ms2, Ms3]
    for i, (x, y, s) in enumerate(stones):
        sph(f"S{i}", (x, y, 0.04), s, mats[i % 3], (1.5, 1.3, 0.35))
        if i % 2 == 0:
            sph(f"Moss{i}", (x + 0.05, y + 0.03, 0.07), 0.045, Mmoss, (1.3, 1.0, 0.35))
    parent_all(root)
    return promote("cozy_path_stone_A", "mockup_path_v3")


def build_flower():
    clear()
    Mp = mat("M_pot", (0.90, 0.55, 0.32), 0.55)
    Ml = mat("M_lav", (0.70, 0.42, 0.90), 0.5)
    Mpink = mat("M_pink", (0.95, 0.52, 0.68), 0.5)
    My = mat("M_yel", (1.0, 0.82, 0.30), 0.5)
    Mg = mat("M_stem", (0.32, 0.58, 0.28), 0.6)
    Msoil = mat("M_soil", (0.42, 0.30, 0.20), 0.8)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_flower_cluster_A"
    pots = [(0, 0), (0.26, 0.14), (-0.24, 0.16), (0.16, -0.24), (-0.18, -0.20), (0.34, -0.12), (-0.32, 0.0)]
    blooms = [Ml, Mpink, My]
    for i, (x, y) in enumerate(pots):
        cyl(f"Pot{i}", (x, y, 0.10), 0.085, 0.15, Mp)
        sph(f"Soil{i}", (x, y, 0.16), 0.075, Msoil, (1, 1, 0.4))
        for j in range(6):
            a = j * 1.05
            sx = x + 0.04 * math.cos(a)
            sy = y + 0.04 * math.sin(a)
            h = 0.20 + 0.05 * (j % 3)
            cyl(f"St{i}_{j}", (sx, sy, 0.20 + h * 0.3), 0.012, h, Mg)
            sph(f"Fl{i}_{j}", (sx, sy, 0.24 + h), 0.048 + 0.01 * (j % 2), blooms[(i + j) % 3], (0.75, 0.75, 1.35))
    parent_all(root)
    return promote("cozy_flower_cluster_A", "mockup_flower_v3")


def build_tree():
    clear()
    Mt = mat("M_trunk", (0.50, 0.32, 0.20), 0.7)
    Ml = mat("M_leaf", (0.34, 0.70, 0.32), 0.55)
    Ml2 = mat("M_leaf2", (0.48, 0.80, 0.38), 0.55)
    Ml3 = mat("M_leaf3", (0.28, 0.60, 0.26), 0.55)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "MOD_cozy_tree_landmark_A"
    cyl("Trunk", (0, 0, 0.42), 0.15, 0.84, Mt, verts=12)
    cyl("TrunkTop", (0, 0, 0.90), 0.11, 0.32, Mt, verts=10)
    for i, a in enumerate([0, 2.0, 4.0]):
        cyl(f"Root{i}", (0.14 * math.cos(a), 0.14 * math.sin(a), 0.06), 0.055, 0.20, Mt, verts=8)
    sph("Canopy", (0, 0, 1.30), 0.68, Ml, (1.4, 1.4, 1.1))
    sph("Canopy2", (0.32, 0.14, 1.48), 0.45, Ml2)
    sph("Canopy3", (-0.28, -0.16, 1.52), 0.42, Ml3)
    sph("Canopy4", (0.08, 0.32, 1.65), 0.35, Ml2)
    sph("Canopy5", (-0.12, 0.08, 1.80), 0.32, Ml)
    sph("Canopy6", (0.18, -0.22, 1.70), 0.28, Ml3)
    parent_all(root)
    return promote("cozy_tree_landmark_A", "mockup_tree_v3")


def main():
    log("start")
    results = {}
    for name, fn in [
        ("mailbox", build_mailbox),
        ("fence", build_fence),
        ("farm", build_farm),
        ("greenhouse", build_greenhouse),
        ("path", build_path),
        ("flower", build_flower),
        ("tree", build_tree),
    ]:
        try:
            dig = fn()
            results[name] = {"ok": True, "sha": dig[:16]}
        except Exception as e:
            log(f"FAIL {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = {"ok": False, "error": str(e)}
    log(f"DONE {results}")
    (QUAR / "summary.json").write_text(json.dumps({"job": JOB, "results": results, "accepted": False}, indent=2), encoding="utf-8")
    return 0 if all(r.get("ok") for r in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

# -*- coding: utf-8 -*-
"""cozy_mailbox_A — Phase 01 home_plot prop to close MOCKUP_PARITY_100.

Matches mockup SSOT art: purple clay mailbox, cream post, gold knobs, cream flag,
tiny lavender pots + stepping stones. Low-poly rounded toy look.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Euler

JOB = "COZY_MAILBOX_A_V1"
MODULE_ID = "cozy_mailbox_A"
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
GAME_GLB = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules") / f"{MODULE_ID}.glb"
CATALOG = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
QUAR.mkdir(parents=True, exist_ok=True)
GAME_GLB.parent.mkdir(parents=True, exist_ok=True)

COL = {
    "post": (0.99, 0.94, 0.86),
    "mail": (0.72, 0.52, 0.92),
    "door": (0.68, 0.48, 0.88),
    "flag": (0.98, 0.93, 0.80),
    "knob": (0.98, 0.82, 0.28),
    "pot": (0.92, 0.62, 0.42),
    "lav": (0.74, 0.50, 0.92),
    "leaf": (0.45, 0.78, 0.48),
    "stone": (0.94, 0.90, 0.84),
}


def log(m: str) -> None:
    print(f"[{JOB}] {m}")


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


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


def set_mat(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)


def fin(o, m, bevel=0.0):
    set_mat(o, m)
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


def cube(name, loc, sc, m, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return fin(o, m, bevel)


def sph(name, loc, r, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=14, ring_count=10)
    o = bpy.context.active_object
    o.name = name
    return fin(o, m, 0.0)


def cyl(name, loc, r, d, m, rot=None, verts=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=verts)
    o = bpy.context.active_object
    o.name = name
    if rot:
        o.rotation_euler = Euler(rot, "XYZ")
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return fin(o, m, 0.02)


def join_named(name, objects, m):
    objs = [o for o in objects if o is not None and o.name in bpy.data.objects]
    if not objs:
        return None
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    o = bpy.context.active_object
    o.name = name
    set_mat(o, m)
    o.select_set(False)
    return o


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = {k: mat(f"MAT_{k}", v) for k, v in COL.items()}
    M["knob"] = mat("MAT_knob", COL["knob"], 0.28, 0.35)

    # Post (cream pedestal) — height ~1.0m total toy scale
    post = cyl("post", (0.0, 0.0, 0.38), 0.10, 0.76, M["post"], verts=18)
    base = cyl("base_flare", (0.0, 0.0, 0.06), 0.16, 0.10, M["post"], verts=18)
    neck = cyl("neck", (0.0, 0.0, 0.78), 0.12, 0.10, M["post"], verts=16)

    # Mailbox body (purple rounded capsule-ish)
    body = cube("body", (0.0, 0.0, 1.05), (0.42, 0.28, 0.34), M["mail"], 0.10)
    # Domed top via stretched sphere
    dome = sph("dome", (0.0, 0.0, 1.22), 0.20, M["mail"])
    dome.scale = (1.05, 0.72, 0.55)
    bpy.context.view_layer.objects.active = dome
    dome.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    dome.select_set(False)

    # Front door plate + knobs
    door = cube("door", (0.0, 0.145, 1.02), (0.28, 0.04, 0.22), M["door"], 0.05)
    knob_l = sph("knob_l", (-0.08, 0.175, 1.02), 0.025, M["knob"])
    knob_r = sph("knob_r", (0.08, 0.175, 1.02), 0.025, M["knob"])

    # Flag (cream)
    flag_arm = cube("flag_arm", (0.24, 0.0, 1.12), (0.04, 0.03, 0.16), M["flag"], 0.02)
    flag_head = cube("flag_head", (0.24, 0.0, 1.22), (0.10, 0.03, 0.08), M["flag"], 0.03)
    flag_knob = sph("flag_knob", (0.24, 0.0, 1.02), 0.03, M["knob"])

    # Decorative pots + stones (match mockup card)
    pot_a = cyl("pot_a", (-0.28, 0.18, 0.08), 0.06, 0.10, M["pot"], verts=12)
    lav_a1 = sph("lav_a1", (-0.28, 0.18, 0.18), 0.035, M["lav"])
    lav_a2 = sph("lav_a2", (-0.24, 0.16, 0.20), 0.03, M["lav"])
    pot_b = cyl("pot_b", (0.26, 0.16, 0.08), 0.055, 0.09, M["pot"], verts=12)
    lav_b1 = sph("lav_b1", (0.26, 0.16, 0.17), 0.032, M["lav"])
    lav_b2 = sph("lav_b2", (0.30, 0.14, 0.19), 0.028, M["lav"])

    stones = []
    for i, (x, y) in enumerate(
        [(-0.35, -0.12), (-0.22, -0.22), (0.18, -0.20), (0.32, -0.10), (0.05, -0.28)]
    ):
        stones.append(cyl(f"stone_{i}", (x, y, 0.015), 0.05 + 0.01 * (i % 2), 0.03, M["stone"], verts=10))

    # Join major parts for cleaner export
    join_named(
        "Mailbox_Body",
        [body, dome, door, knob_l, knob_r, flag_arm, flag_head, flag_knob],
        M["mail"],
    )
    join_named("Mailbox_Post", [post, base, neck], M["post"])
    join_named(
        "Mailbox_Decor",
        [pot_a, lav_a1, lav_a2, pot_b, lav_b1, lav_b2] + stones,
        M["pot"],
    )

    # Root empty for orientation (Y-up game, +Z forward approx)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = MODULE_ID

    for o in list(bpy.data.objects):
        if o.type == "MESH":
            o.parent = root

    # Export GLB
    for o in bpy.data.objects:
        o.select_set(o.type in {"MESH", "EMPTY"})
    bpy.context.view_layer.objects.active = root

    quar_glb = QUAR / f"{MODULE_ID}.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(quar_glb),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
    )
    log(f"quarantine={quar_glb} bytes={quar_glb.stat().st_size}")

    # Promote to game assets
    data = quar_glb.read_bytes()
    GAME_GLB.write_bytes(data)
    digest = sha(GAME_GLB)
    log(f"promoted={GAME_GLB} sha256={digest} bytes={len(data)}")

    # Catalog upsert
    cat = {"schema_version": "1.0.0", "catalog_id": "p1e_cozy_modules_v1", "modules": []}
    if CATALOG.exists():
        cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    modules = cat.get("modules", [])
    entry = {
        "module_id": MODULE_ID,
        "glb": f"res://assets/p1e_cozy/modules/{MODULE_ID}.glb",
        "glb_sha256": digest,
        "bytes": len(data),
        "source": JOB,
        "visual": "mockup_ssot_v2_prop_mailbox",
        "ambient": "idle_static",
        "phase": "TOWN_PHASE_01",
    }
    found = False
    for i, m in enumerate(modules):
        if isinstance(m, dict) and m.get("module_id") == MODULE_ID:
            modules[i] = entry
            found = True
            break
    if not found:
        modules.append(entry)
    cat["modules"] = modules
    cat["accepted"] = False
    cat["self_accept"] = False
    CATALOG.write_text(json.dumps(cat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log(f"catalog_updated modules={len(modules)}")

    receipt = {
        "job": JOB,
        "module_id": MODULE_ID,
        "glb": str(GAME_GLB),
        "sha256": digest,
        "bytes": len(data),
        "mockup_ref": "orchestration/control/visual_reference/mockup_ssot_v2/props/prop_mailbox.jpg",
        "self_accept": False,
        "accepted": False,
    }
    (QUAR / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    log("DONE")


if __name__ == "__main__":
    build()

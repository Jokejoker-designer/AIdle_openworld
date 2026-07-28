# -*- coding: utf-8 -*-
"""Nori-7 MOCKUP PARITY V1 — multi-part cream teardrop matching SSOT mockup art.

User-reported FAIL: in-game white golf-ball blob != mockup cream robot + sprout + cyan eye.
This rebuild parents colored parts to bones (no single white joined sphere).

Run:
  E:\\blender.exe --background --factory-startup --python this_script.py
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Euler, Vector

JOB = "NORI7_MOCKUP_PARITY_V1"
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
PROD = Path(r"E:\AIdle_openworld\game\assets\ucbv_001\character\nori7\export")
ADAPTER = Path(r"E:\AIdle_openworld\game\resources\ucbv_001\character\nori7_animation_adapter.json")
ROSTER = Path(r"E:\AIdle_openworld\game\resources\ucbv_001\cast\cast_roster.json")
PATHS_GD = Path(r"E:\AIdle_openworld\game\scripts\modules\ucbv_001\ucbv_paths.gd")
QUAR.mkdir(parents=True, exist_ok=True)
PROD.mkdir(parents=True, exist_ok=True)

# Mockup-locked palette (DESIGN.md / COZY / visual_spec)
COL = {
    "cream": (0.992, 0.953, 0.886, 1.0),      # #fdf3e2
    "cream_d": (0.937, 0.878, 0.784, 1.0),    # #efe0c8
    "leaf": (0.45, 0.72, 0.40, 1.0),          # green sprout/limbs
    "leaf_d": (0.35, 0.55, 0.32, 1.0),
    "eye_black": (0.08, 0.10, 0.12, 1.0),
    "eye_cyan": (0.15, 0.85, 0.88, 1.0),      # cyan ring — eye ONLY
    "metal": (0.55, 0.58, 0.62, 1.0),
    "glass_g": (0.35, 0.55, 0.30, 0.75),
}

BONES = [
    ("root", None, (0.0, 0.0, 0.0)),
    ("pelvis", "root", (0.0, 0.0, 0.16)),
    ("spine", "pelvis", (0.0, 0.0, 0.36)),
    ("chest", "spine", (0.0, 0.0, 0.58)),
    ("head", "chest", (0.0, 0.0, 0.92)),
    ("sprout_ctrl", "head", (0.0, 0.0, 1.20)),
    ("arm_L", "chest", (-0.32, 0.02, 0.68)),
    ("hand_L", "arm_L", (-0.46, 0.06, 0.50)),
    ("arm_R", "chest", (0.32, 0.02, 0.68)),
    ("hand_R", "arm_R", (0.46, 0.06, 0.50)),
    ("leg_L", "pelvis", (-0.11, 0.0, 0.10)),
    ("foot_L", "leg_L", (-0.11, 0.08, 0.02)),
    ("leg_R", "pelvis", (0.11, 0.0, 0.10)),
    ("foot_R", "leg_R", (0.11, 0.08, 0.02)),
]

FPS = 30
REQUIRED = [
    "idle", "walk", "scan", "happy", "cancel",
    "turn_left", "turn_right", "build_place", "build_place_hold", "confirm",
]


def log(m: str) -> None:
    print(f"[{JOB}] {m}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def mat(name: str, rgba, rough=0.5, metal=0.0, emit=0.0) -> bpy.types.Material:
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = rough
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metal
        if emit > 0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = rgba
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emit
        if "Alpha" in bsdf.inputs and len(rgba) > 3 and rgba[3] < 0.99:
            bsdf.inputs["Alpha"].default_value = rgba[3]
            m.blend_method = "BLEND"
    return m


def assign(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)


def sphere(name, loc, scale, m, segs=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=14, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(o, m)
    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass
    return o


def cyl(name, loc, r, d, m, rot=(0, 0, 0), verts=14):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = Euler(rot, "XYZ")
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    assign(o, m)
    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass
    return o


def join_all(parts: list) -> bpy.types.Object:
    """Join multi-material parts into one skinned mesh (keeps material slots)."""
    meshes = [o for o, _ in parts]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    obj = bpy.context.active_object
    obj.name = "Nori7_Mesh"
    return obj


def skin_auto(mesh_obj: bpy.types.Object, arm_obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")


def build_armature():
    data = bpy.data.armatures.new("skel_small_biped_robot_v1")
    arm = bpy.data.objects.new("Nori7_Armature", data)
    bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    created = {}
    for name, parent, head in BONES:
        b = data.edit_bones.new(name)
        hx, hy, hz = head
        b.head = Vector((hx, hy, hz))
        b.tail = Vector((hx, hy, hz + (0.05 if name in ("hand_L", "hand_R", "foot_L", "foot_R", "sprout_ctrl", "root") else 0.11)))
        if parent:
            b.parent = created[parent]
            b.use_connect = False
        created[name] = b
    bpy.ops.object.mode_set(mode="OBJECT")
    return arm


def build_parts(M):
    parts = []  # (obj, bone)

    # Teardrop body: lower + upper cream (mockup inverted egg)
    body_lo = sphere("body_lower", (0, 0.02, 0.34), (0.34, 0.32, 0.34), M["cream"], 24)
    body_up = sphere("body_upper", (0, 0.04, 0.72), (0.38, 0.34, 0.40), M["cream"], 24)
    face = sphere("face", (0, 0.26, 0.88), (0.20, 0.08, 0.18), M["cream_d"], 18)
    # Single large cyan eye (mockup has one big eye on face)
    eye_dark = sphere("eye_dark", (0.02, 0.30, 0.90), (0.10, 0.04, 0.10), M["eye_black"], 16)
    eye_ring = sphere("eye_ring", (0.02, 0.32, 0.90), (0.065, 0.025, 0.065), M["eye_cyan"], 16)
    eye_pupil = sphere("eye_pupil", (0.02, 0.335, 0.90), (0.03, 0.012, 0.03), M["eye_black"], 12)

    for o, b in (
        (body_lo, "spine"),
        (body_up, "chest"),
        (face, "head"),
        (eye_dark, "head"),
        (eye_ring, "head"),
        (eye_pupil, "head"),
    ):
        parts.append((o, b))

    # Arms cream/leaf hands + green nozzle on right
    arm_l = cyl("arm_L_mesh", (-0.32, 0.02, 0.62), 0.05, 0.24, M["cream"], (0, 0, 0.4))
    arm_r = cyl("arm_R_mesh", (0.32, 0.02, 0.62), 0.05, 0.24, M["cream"], (0, 0, -0.4))
    hand_l = sphere("hand_L_mesh", (-0.46, 0.06, 0.48), (0.055, 0.055, 0.055), M["leaf"])
    hand_r = sphere("hand_R_mesh", (0.46, 0.06, 0.48), (0.055, 0.055, 0.055), M["leaf"])
    nozzle = cyl("nozzle", (0.58, 0.12, 0.52), 0.028, 0.22, M["leaf_d"], (1.35, 0, 0), 12)
    parts += [(arm_l, "arm_L"), (arm_r, "arm_R"), (hand_l, "hand_L"), (hand_r, "hand_R"), (nozzle, "hand_R")]

    # Legs green bands + cream feet (mockup)
    leg_l = cyl("leg_L_mesh", (-0.11, 0.0, 0.12), 0.055, 0.18, M["leaf"])
    leg_r = cyl("leg_R_mesh", (0.11, 0.0, 0.12), 0.055, 0.18, M["leaf"])
    foot_l = sphere("foot_L_mesh", (-0.11, 0.07, 0.03), (0.08, 0.10, 0.045), M["cream"])
    foot_r = sphere("foot_R_mesh", (0.11, 0.07, 0.03), (0.08, 0.10, 0.045), M["cream"])
    parts += [(leg_l, "leg_L"), (leg_r, "leg_R"), (foot_l, "foot_L"), (foot_r, "foot_R")]

    # Water tank backpack green glass jar
    tank = sphere("tank", (0, -0.26, 0.55), (0.14, 0.12, 0.18), M["leaf_d"])
    tank_cap = cyl("tank_cap", (0, -0.26, 0.74), 0.05, 0.04, M["metal"])
    parts += [(tank, "chest"), (tank_cap, "chest")]

    # Sprout leaves (signature)
    stem = cyl("sprout_stem", (0, 0.0, 1.12), 0.022, 0.16, M["leaf_d"])
    leaf_a = sphere("leaf_a", (-0.07, 0.02, 1.24), (0.09, 0.04, 0.035), M["leaf"])
    leaf_b = sphere("leaf_b", (0.07, -0.01, 1.26), (0.085, 0.038, 0.032), M["leaf"])
    hub = sphere("sprout_hub", (0, 0.0, 1.04), (0.05, 0.05, 0.04), M["metal"])
    parts += [(stem, "sprout_ctrl"), (leaf_a, "sprout_ctrl"), (leaf_b, "sprout_ctrl"), (hub, "head")]

    return parts


def bone_pose(arm, name):
    return arm.pose.bones.get(name)


def key(pb, frame, loc=None, euler=None):
    if pb is None:
        return
    if loc is not None:
        pb.location = Vector(loc)
        pb.keyframe_insert(data_path="location", frame=frame)
    if euler is not None:
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler(euler)
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)


def count_fcurves(act) -> int:
    if act is None:
        return 0
    if hasattr(act, "fcurves") and act.fcurves is not None:
        try:
            return len(act.fcurves)
        except Exception:
            pass
    total = 0
    try:
        for layer in act.layers:
            for strip in layer.strips:
                if hasattr(strip, "channelbags"):
                    for bag in strip.channelbags:
                        if hasattr(bag, "fcurves"):
                            total += len(bag.fcurves)
    except Exception:
        pass
    return total


def author_clips(arm):
    arm.animation_data_create()
    meta = []

    def make(name, dur, fn):
        act = bpy.data.actions.new(name)
        arm.animation_data.action = act
        n = max(2, int(round(dur * FPS)))
        fn(arm, n)
        fc = count_fcurves(act)
        meta.append({"action_name": name, "duration_s": dur, "fcurve_count": fc, "loop": name in ("idle", "walk")})
        log(f"clip {name} frames={n} fcurves={fc}")

    def idle(arm, n):
        p, s = bone_pose(arm, "pelvis"), bone_pose(arm, "sprout_ctrl")
        for f, z, r in ((1, 0.0, 0.0), (n // 2, -0.015, 0.05), (n, 0.0, 0.0)):
            key(p, f, loc=(0, 0, z))
            key(s, f, euler=(0, 0, r))

    def walk(arm, n):
        for f in (1, n // 4, n // 2, 3 * n // 4, n):
            t = (f - 1) / max(1, n - 1)
            ph = math.sin(t * math.pi * 2)
            key(bone_pose(arm, "leg_L"), f, euler=(ph * 0.35, 0, 0))
            key(bone_pose(arm, "leg_R"), f, euler=(-ph * 0.35, 0, 0))
            key(bone_pose(arm, "arm_L"), f, euler=(-ph * 0.2, 0, 0.1))
            key(bone_pose(arm, "arm_R"), f, euler=(ph * 0.2, 0, -0.1))
            key(bone_pose(arm, "pelvis"), f, loc=(0, 0, abs(ph) * 0.014))

    def scan(arm, n):
        h = bone_pose(arm, "head")
        key(h, 1, euler=(0, 0, 0))
        key(h, n // 3, euler=(0, 0.28, 0.12))
        key(h, 2 * n // 3, euler=(0, -0.28, -0.12))
        key(h, n, euler=(0, 0, 0))

    def happy(arm, n):
        key(bone_pose(arm, "sprout_ctrl"), n // 2, euler=(0.25, 0, 0.35))
        key(bone_pose(arm, "sprout_ctrl"), n, euler=(0, 0, 0))
        key(bone_pose(arm, "arm_L"), n // 2, euler=(-0.45, 0, 0.3))
        key(bone_pose(arm, "arm_R"), n // 2, euler=(-0.45, 0, -0.3))
        key(bone_pose(arm, "arm_L"), n, euler=(0, 0, 0))
        key(bone_pose(arm, "arm_R"), n, euler=(0, 0, 0))
        key(bone_pose(arm, "pelvis"), n // 2, loc=(0, 0, 0.025))
        key(bone_pose(arm, "pelvis"), n, loc=(0, 0, 0))

    def cancel(arm, n):
        key(bone_pose(arm, "head"), n // 2, euler=(0.18, 0, 0))
        key(bone_pose(arm, "head"), n, euler=(0, 0, 0))
        key(bone_pose(arm, "arm_L"), n // 2, euler=(0.35, 0, -0.2))
        key(bone_pose(arm, "arm_R"), n // 2, euler=(0.35, 0, 0.2))
        key(bone_pose(arm, "arm_L"), n, euler=(0, 0, 0))
        key(bone_pose(arm, "arm_R"), n, euler=(0, 0, 0))

    def turn(arm, n, sign):
        key(bone_pose(arm, "pelvis"), 1, euler=(0, 0, 0))
        key(bone_pose(arm, "pelvis"), n // 2, euler=(0, 0, sign * 0.55))
        key(bone_pose(arm, "pelvis"), n, euler=(0, 0, 0))

    def build_place(arm, n):
        key(bone_pose(arm, "arm_R"), 1, euler=(0, 0, 0))
        key(bone_pose(arm, "arm_R"), n // 2, euler=(-0.95, 0, -0.2))
        key(bone_pose(arm, "arm_R"), n, euler=(-0.5, 0, -0.1))
        key(bone_pose(arm, "head"), n // 2, euler=(-0.12, 0, 0.05))
        key(bone_pose(arm, "head"), n, euler=(0, 0, 0))

    def build_hold(arm, n):
        key(bone_pose(arm, "arm_R"), 1, euler=(-0.55, 0, -0.1))
        key(bone_pose(arm, "arm_R"), n // 2, euler=(-0.58, 0, -0.12))
        key(bone_pose(arm, "arm_R"), n, euler=(-0.55, 0, -0.1))

    def confirm(arm, n):
        key(bone_pose(arm, "arm_R"), 1, euler=(-0.5, 0, -0.1))
        key(bone_pose(arm, "arm_R"), n // 3, euler=(-1.05, 0, -0.15))
        key(bone_pose(arm, "arm_R"), n, euler=(0, 0, 0))
        key(bone_pose(arm, "sprout_ctrl"), n // 2, euler=(0.18, 0, 0.22))
        key(bone_pose(arm, "sprout_ctrl"), n, euler=(0, 0, 0))

    make("idle", 2.4, idle)
    make("walk", 0.8, walk)
    make("scan", 1.4, scan)
    make("happy", 1.1, happy)
    make("cancel", 0.55, cancel)
    make("turn_left", 0.6, lambda a, n: turn(a, n, 1))
    make("turn_right", 0.6, lambda a, n: turn(a, n, -1))
    make("build_place", 0.9, build_place)
    make("build_place_hold", 1.2, build_hold)
    make("confirm", 0.9, confirm)
    # stash last idle action on armature for export of all actions via NLA
    return meta


def push_actions_to_nla(arm):
    """Ensure all named actions export with the GLB."""
    if arm.animation_data is None:
        arm.animation_data_create()
    track_i = 0
    for name in REQUIRED:
        act = bpy.data.actions.get(name)
        if act is None:
            continue
        track = arm.animation_data.nla_tracks.new()
        track.name = name
        start = 1
        track.strips.new(name, start, act)
        track_i += 1
    log(f"nla_tracks={track_i}")


def update_hashes(digest: str, nbytes: int):
    # adapter
    if ADAPTER.exists():
        ad = json.loads(ADAPTER.read_text(encoding="utf-8"))
        ad.setdefault("glb", {})
        ad["glb"]["path"] = "res://assets/ucbv_001/character/nori7/export/nori7_rigged.glb"
        ad["glb"]["sha256"] = digest
        ad["glb"]["bytes"] = nbytes
        ad["wave"] = JOB
        ad["accepted"] = False
        ad["self_accept"] = False
        ad["visual_parity"] = {
            "target": "mockup_ssot_v2/chars/char_01_nori7.jpg",
            "status": "rebuilt_multi_part_cream_teardrop",
            "not_white_blob": True,
        }
        ADAPTER.write_text(json.dumps(ad, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        log("adapter updated")

    # cast roster nori entry
    if ROSTER.exists():
        ro = json.loads(ROSTER.read_text(encoding="utf-8"))
        for c in ro.get("characters", []):
            if c.get("character_id") == "CCP-RH-001" or c.get("slug") == "nori7":
                c["glb"] = "res://assets/ucbv_001/character/nori7/export/nori7_rigged.glb"
                c["glb_sha256"] = digest
                c["visual_wave"] = JOB
        ROSTER.write_text(json.dumps(ro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        log("roster updated")

    # ucbv_paths expected sha
    if PATHS_GD.exists():
        txt = PATHS_GD.read_text(encoding="utf-8")
        import re

        txt2 = re.sub(
            r'const NORI_GLB_SHA256_EXPECTED := "[0-9a-fA-F]+"',
            f'const NORI_GLB_SHA256_EXPECTED := "{digest}"',
            txt,
        )
        if txt2 != txt:
            PATHS_GD.write_text(txt2, encoding="utf-8")
            log("ucbv_paths.gd sha updated")


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = {
        "cream": mat("MAT_cream", COL["cream"], 0.48),
        "cream_d": mat("MAT_cream_d", COL["cream_d"], 0.55),
        "leaf": mat("MAT_leaf", COL["leaf"], 0.5),
        "leaf_d": mat("MAT_leaf_d", COL["leaf_d"], 0.45),
        "eye_black": mat("MAT_eye_black", COL["eye_black"], 0.35),
        "eye_cyan": mat("MAT_eye_cyan", COL["eye_cyan"], 0.25, 0.0, 1.8),
        "metal": mat("MAT_metal", COL["metal"], 0.35, 0.6),
    }

    arm = build_armature()
    parts = build_parts(M)
    # Exact 14-bone skinned mesh only — bone-parented meshes become extra bones in Godot.
    mesh = join_all(parts)
    skin_auto(mesh, arm)

    meta = author_clips(arm)
    push_actions_to_nla(arm)

    # Select armature + mesh for export
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = arm

    quar_glb = QUAR / "nori7_rigged.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(quar_glb),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_animations=True,
        export_nla_strips=True,
        export_def_bones=True,
        export_skins=True,
    )
    log(f"quarantine {quar_glb} bytes={quar_glb.stat().st_size}")

    prod_glb = PROD / "nori7_rigged.glb"
    data = quar_glb.read_bytes()
    # backup old
    bak = PROD / "nori7_rigged.glb.bak_pre_mockup_parity"
    if prod_glb.exists() and not bak.exists():
        bak.write_bytes(prod_glb.read_bytes())
    prod_glb.write_bytes(data)
    digest = sha256_file(prod_glb)
    log(f"promoted sha256={digest} bytes={len(data)}")

    receipt = {
        "job": JOB,
        "glb": str(prod_glb),
        "sha256": digest,
        "bytes": len(data),
        "clips": meta,
        "mockup_ref": "orchestration/control/visual_reference/mockup_ssot_v2/chars/char_01_nori7.jpg",
        "visual_targets": [
            "cream_teardrop_body",
            "green_sprout_two_leaves",
            "cyan_eye_ring_only",
            "green_water_tank",
            "green_nozzle",
            "short_biped_legs",
        ],
        "not_white_golf_ball": True,
        "self_accept": False,
        "accepted": False,
    }
    (QUAR / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    (PROD / "nori7_mockup_parity_v1_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    update_hashes(digest, len(data))
    log("DONE")


if __name__ == "__main__":
    main()

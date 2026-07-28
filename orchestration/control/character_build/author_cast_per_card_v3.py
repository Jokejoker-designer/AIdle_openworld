# -*- coding: utf-8 -*-
"""CAST_PER_CARD_V3 — individual SSOT card polish (not shared presenter).

Priority cards from redo-loop next strikes:
  CCP-RH-001 Nori-7: pear body, large cyan eye, green snout barrel, vial, leaf sprout
  CCP-NW-003 Bac Bap: stocky orange coveralls, bald, mustache, toolbox
  CCP-NS-002 May Mach: yellow humanoid slim
  SPH-RH-011 Kito: robot dual green eyes + sprout

Other 6 keep V2 silhouette with slight palette punch from card.
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

JOB = "CAST_PER_CARD_V3"
FPS = 30
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
GAME_CAST = Path(r"E:\AIdle_openworld\game\assets\ucbv_001\cast")
GAME_NORI = Path(r"E:\AIdle_openworld\game\assets\ucbv_001\character\nori7\export")
ROSTER = Path(r"E:\AIdle_openworld\game\resources\ucbv_001\cast\cast_roster.json")
QUAR.mkdir(parents=True, exist_ok=True)

BONES = [
    ("root", None, (0, 0, 0)),
    ("pelvis", "root", (0, 0, 0.18)),
    ("spine", "pelvis", (0, 0, 0.38)),
    ("chest", "spine", (0, 0, 0.62)),
    ("head", "chest", (0, 0, 0.95)),
    ("sprout_ctrl", "head", (0, 0, 1.18)),
    ("arm_L", "chest", (-0.28, 0, 0.72)),
    ("hand_L", "arm_L", (-0.42, 0.05, 0.52)),
    ("arm_R", "chest", (0.28, 0, 0.72)),
    ("hand_R", "arm_R", (0.42, 0.05, 0.52)),
    ("leg_L", "pelvis", (-0.10, 0, 0.10)),
    ("foot_L", "leg_L", (-0.10, 0.08, 0.02)),
    ("leg_R", "pelvis", (0.10, 0, 0.10)),
    ("foot_R", "leg_R", (0.10, 0.08, 0.02)),
]

CLIPS = [
    ("idle", 3.0, "idle"), ("walk", 0.8, "walk"), ("scan", 1.2, "scan"),
    ("happy", 1.0, "happy"), ("cancel", 0.6, "cancel"),
    ("turn_left", 0.5, "turn_l"), ("turn_right", 0.5, "turn_r"),
    ("build_place", 0.67, "build"), ("build_place_hold", 0.8, "hold"),
    ("confirm", 0.55, "confirm"),
]


def log(m):
    print(f"[{JOB}] {m}")


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.armatures, bpy.data.actions):
        for b in list(coll):
            coll.remove(b)


def mat(name, rgba, rough=0.55, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = rgba
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
    return m


def sphere(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.clear()
    o.data.materials.append(material)
    return o


def cyl(name, loc, r, depth, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=r, depth=depth, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = Euler(rot)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    o.data.materials.clear()
    o.data.materials.append(material)
    return o


def join(parts, name):
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    o = bpy.context.active_object
    o.name = name
    return o


def armature():
    data = bpy.data.armatures.new("skel_cast_v3")
    obj = bpy.data.objects.new("CastArmature", data)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    created = {}
    for name, parent, head in BONES:
        b = data.edit_bones.new(name)
        hx, hy, hz = head
        b.head = Vector((hx, hy, hz))
        b.tail = Vector((hx, hy, hz + 0.08))
        if parent:
            b.parent = created[parent]
            b.use_connect = False
        created[name] = b
    bpy.ops.object.mode_set(mode="OBJECT")
    return obj


def count_fcurves(act):
    if act is None:
        return 0
    if hasattr(act, "fcurves") and act.fcurves is not None:
        try:
            return len(act.fcurves)
        except Exception:
            pass
    n = 0
    try:
        for layer in act.layers:
            for strip in layer.strips:
                if hasattr(strip, "channelbags"):
                    for bag in strip.channelbags:
                        if hasattr(bag, "fcurves"):
                            n += len(bag.fcurves)
    except Exception:
        pass
    return n


def key(pb, frame, loc=None, euler=None):
    if pb is None:
        return
    if loc is not None:
        pb.location = Vector(loc)
        pb.keyframe_insert("location", frame=frame)
    if euler is not None:
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler(euler)
        pb.keyframe_insert("rotation_euler", frame=frame)


def author_clips(arm):
    arm.animation_data_create()
    report = {}
    for clip_name, dur, kind in CLIPS:
        act = bpy.data.actions.new(clip_name)
        arm.animation_data.action = act
        n = max(2, int(round(dur * FPS)))
        pelvis = arm.pose.bones.get("pelvis")
        head = arm.pose.bones.get("head")
        arm_l = arm.pose.bones.get("arm_L")
        arm_r = arm.pose.bones.get("arm_R")
        leg_l = arm.pose.bones.get("leg_L")
        leg_r = arm.pose.bones.get("leg_R")
        sprout = arm.pose.bones.get("sprout_ctrl")
        if kind == "idle":
            for f, y in ((1, 0.0), (n // 2, -0.012), (n, 0.0)):
                key(pelvis, f, loc=(0, 0, y))
                key(sprout, f, euler=(0, 0, 0.03 if f == n // 2 else 0))
        elif kind == "walk":
            for f in (1, n // 4, n // 2, 3 * n // 4, n):
                t = (f - 1) / max(1, n - 1)
                ph = math.sin(t * math.pi * 2)
                key(leg_l, f, euler=(ph * 0.28, 0, 0))
                key(leg_r, f, euler=(-ph * 0.28, 0, 0))
                key(arm_l, f, euler=(-ph * 0.15, 0, 0.1))
                key(arm_r, f, euler=(ph * 0.15, 0, -0.1))
        elif kind == "scan":
            key(head, 1, euler=(0, 0, 0))
            key(head, n // 3, euler=(0, 0.25, 0.1))
            key(head, 2 * n // 3, euler=(0, -0.25, -0.1))
            key(head, n, euler=(0, 0, 0))
        elif kind == "happy":
            key(arm_l, n // 2, euler=(-0.5, 0, 0.3))
            key(arm_r, n // 2, euler=(-0.5, 0, -0.3))
            key(arm_l, n, euler=(0, 0, 0))
            key(arm_r, n, euler=(0, 0, 0))
        elif kind == "cancel":
            key(head, n // 2, euler=(0.2, 0, 0))
            key(head, n, euler=(0, 0, 0))
        elif kind == "turn_l":
            key(pelvis, n // 2, euler=(0, 0, 0.5))
            key(pelvis, n, euler=(0, 0, 0))
        elif kind == "turn_r":
            key(pelvis, n // 2, euler=(0, 0, -0.5))
            key(pelvis, n, euler=(0, 0, 0))
        elif kind in ("build", "hold"):
            key(arm_r, 1, euler=(-0.5 if kind == "hold" else 0, 0, -0.1))
            key(arm_r, n // 2, euler=(-0.9, 0, -0.15))
            key(arm_r, n, euler=(-0.5 if kind == "hold" else 0, 0, -0.1))
        elif kind == "confirm":
            key(arm_r, n // 3, euler=(-1.0, 0, -0.1))
            key(arm_r, n, euler=(0, 0, 0))
        fc = count_fcurves(act)
        report[clip_name] = {"duration_s": dur, "fcurve_count": fc, "real_keys": fc > 0}
        track = arm.animation_data.nla_tracks.new()
        track.name = clip_name
        try:
            track.strips.new(clip_name, 1, act)
        except Exception as e:
            log(f"nla warn {clip_name}: {e}")
    if bpy.data.actions.get("idle"):
        arm.animation_data.action = bpy.data.actions["idle"]
    return report


# ---- per-card bodies ----

def body_nori(parts, mats):
    """SSOT char_nori7: tall pear, single large cyan eye, green barrel snout, vial, leaf."""
    cream, shade, leaf, glass, metal, accent = (
        mats["cream"], mats["shade"], mats["leaf"], mats["glass"], mats["metal"], mats["accent"]
    )
    # taller pear body
    parts += [
        sphere("body", (0, 0.02, 0.48), (0.34, 0.32, 0.46), cream),
        sphere("belly", (0, 0.08, 0.30), (0.26, 0.22, 0.22), shade),
        sphere("head", (0, 0.04, 0.92), (0.30, 0.28, 0.30), cream),
        # large cyan eye ring + pupil
        sphere("eyeRing", (0.0, 0.30, 0.94), (0.14, 0.08, 0.14), glass),
        sphere("eyePupil", (0.0, 0.35, 0.94), (0.07, 0.04, 0.07), metal),
        sphere("eyeCore", (0.0, 0.37, 0.94), (0.035, 0.02, 0.035), glass),
        # green snout barrel (SSOT long tube)
        cyl("snout", (0, 0.42, 0.78), 0.08, 0.36, leaf, (math.pi / 2, 0, 0)),
        sphere("snoutTip", (0, 0.60, 0.78), (0.07, 0.05, 0.07), leaf),
        # green arms/legs accents
        cyl("armL", (-0.34, 0.02, 0.58), 0.055, 0.26, cream, (0, 0, 0.4)),
        cyl("armR", (0.34, 0.02, 0.58), 0.055, 0.26, cream, (0, 0, -0.4)),
        sphere("handL", (-0.48, 0.08, 0.42), (0.07, 0.07, 0.07), leaf),
        sphere("handR", (0.48, 0.08, 0.42), (0.07, 0.07, 0.07), leaf),
        cyl("legL", (-0.12, 0.02, 0.14), 0.055, 0.20, leaf),
        cyl("legR", (0.12, 0.02, 0.14), 0.055, 0.20, leaf),
        sphere("footL", (-0.12, 0.10, 0.03), (0.09, 0.12, 0.045), cream),
        sphere("footR", (0.12, 0.10, 0.03), (0.09, 0.12, 0.045), cream),
        # leaf sprout
        cyl("stem", (0, 0.0, 1.18), 0.022, 0.18, leaf),
        sphere("leafL", (-0.10, 0.0, 1.32), (0.12, 0.05, 0.04), leaf),
        sphere("leafR", (0.10, 0.0, 1.32), (0.12, 0.05, 0.04), leaf),
        # backpack vial
        cyl("vial", (-0.26, -0.20, 0.58), 0.06, 0.20, accent),
        sphere("vialTop", (-0.26, -0.20, 0.70), (0.045, 0.045, 0.035), metal),
        sphere("vialCap", (-0.26, -0.20, 0.74), (0.03, 0.03, 0.02), metal),
    ]
    return parts


def body_bac_bap(parts, mats):
    """SSOT Bac Bap: stocky orange coveralls, bald tan head, brown mustache, toolbox."""
    orange, tan, brown, metal, cream = (
        mats["cream"], mats["shade"], mats["wood"], mats["metal"], mats["leaf"]
    )
    # cream reused as orange coveralls in this card's palette mapping
    parts += [
        sphere("torso", (0, 0.02, 0.58), (0.32, 0.22, 0.32), orange),  # stocky
        sphere("hips", (0, 0.0, 0.34), (0.26, 0.18, 0.16), orange),
        sphere("head", (0, 0.06, 1.02), (0.18, 0.16, 0.17), tan),
        # bald shine
        sphere("bald", (0, 0.02, 1.12), (0.14, 0.12, 0.06), tan),
        # mustache
        sphere("mustL", (-0.05, 0.16, 0.96), (0.06, 0.04, 0.025), brown),
        sphere("mustR", (0.05, 0.16, 0.96), (0.06, 0.04, 0.025), brown),
        # brows
        sphere("browL", (-0.06, 0.14, 1.06), (0.05, 0.03, 0.02), brown),
        sphere("browR", (0.06, 0.14, 1.06), (0.05, 0.03, 0.02), brown),
        # eyes
        sphere("eyeL", (-0.05, 0.16, 1.02), (0.03, 0.02, 0.03), mats["glass"]),
        sphere("eyeR", (0.05, 0.16, 1.02), (0.03, 0.02, 0.03), mats["glass"]),
        # arms
        cyl("armL", (-0.34, 0, 0.60), 0.055, 0.28, orange, (0, 0, 0.3)),
        cyl("armR", (0.34, 0, 0.60), 0.055, 0.28, orange, (0, 0, -0.3)),
        sphere("handL", (-0.46, 0.05, 0.42), (0.06, 0.06, 0.06), cream),
        sphere("handR", (0.46, 0.05, 0.42), (0.06, 0.06, 0.06), cream),
        # legs + boots
        cyl("legL", (-0.10, 0, 0.16), 0.055, 0.26, orange),
        cyl("legR", (0.10, 0, 0.16), 0.055, 0.26, orange),
        sphere("bootL", (-0.10, 0.08, 0.03), (0.08, 0.11, 0.05), cream),
        sphere("bootR", (0.10, 0.08, 0.03), (0.08, 0.11, 0.05), cream),
        # toolbox
        cyl("box", (0.0, 0.28, 0.42), 0.12, 0.18, metal, (math.pi / 2, 0, 0)),
        sphere("boxHandle", (0.0, 0.38, 0.50), (0.08, 0.03, 0.03), metal),
        # shoulder strap
        cyl("strap", (-0.05, -0.05, 0.70), 0.02, 0.50, brown, (0.5, 0, 0.3)),
    ]
    return parts


def body_may_mach(parts, mats):
    """May Mach: slim yellow humanoid, blue hair accent."""
    yellow, shade, blue, leaf = mats["cream"], mats["shade"], mats["wood"], mats["leaf"]
    parts += [
        sphere("torso", (0, 0.02, 0.55), (0.18, 0.14, 0.28), yellow),
        sphere("hips", (0, 0.0, 0.34), (0.14, 0.11, 0.12), shade),
        sphere("head", (0, 0.05, 0.95), (0.14, 0.13, 0.14), shade),
        sphere("hair", (0, -0.02, 1.05), (0.16, 0.12, 0.08), blue),
        cyl("armL", (-0.22, 0, 0.60), 0.032, 0.26, yellow, (0, 0, 0.25)),
        cyl("armR", (0.22, 0, 0.60), 0.032, 0.26, yellow, (0, 0, -0.25)),
        sphere("handL", (-0.32, 0.04, 0.44), (0.04, 0.04, 0.04), leaf),
        sphere("handR", (0.32, 0.04, 0.44), (0.04, 0.04, 0.04), leaf),
        cyl("legL", (-0.07, 0, 0.16), 0.035, 0.26, shade),
        cyl("legR", (0.07, 0, 0.16), 0.035, 0.26, shade),
        sphere("footL", (-0.07, 0.07, 0.03), (0.055, 0.09, 0.03), blue),
        sphere("footR", (0.07, 0.07, 0.03), (0.055, 0.09, 0.03), blue),
    ]
    return parts


def body_kito(parts, mats):
    cream, shade, leaf, glass, metal = mats["cream"], mats["shade"], mats["leaf"], mats["glass"], mats["metal"]
    parts += [
        sphere("body", (0, 0.02, 0.42), (0.32, 0.30, 0.34), cream),
        sphere("head", (0, 0.04, 0.84), (0.26, 0.24, 0.26), shade),
        sphere("eyeL", (-0.10, 0.24, 0.88), (0.09, 0.06, 0.09), glass),
        sphere("eyeR", (0.10, 0.24, 0.88), (0.09, 0.06, 0.09), glass),
        cyl("armL", (-0.32, 0, 0.58), 0.05, 0.24, cream, (0, 0, 0.3)),
        cyl("armR", (0.32, 0, 0.58), 0.05, 0.24, cream, (0, 0, -0.3)),
        sphere("handL", (-0.44, 0.05, 0.44), (0.06, 0.06, 0.06), leaf),
        sphere("handR", (0.44, 0.05, 0.44), (0.06, 0.06, 0.06), leaf),
        cyl("legL", (-0.10, 0, 0.14), 0.055, 0.18, cream),
        cyl("legR", (0.10, 0, 0.14), 0.055, 0.18, cream),
        sphere("footL", (-0.10, 0.07, 0.03), (0.08, 0.10, 0.04), metal),
        sphere("footR", (0.10, 0.07, 0.03), (0.08, 0.10, 0.04), metal),
        sphere("sprout", (0, 0, 1.14), (0.10, 0.07, 0.07), leaf),
        cyl("stem", (0, 0, 1.05), 0.02, 0.12, leaf),
    ]
    return parts


def body_generic(parts, mats, form):
    cream, shade, leaf, wood, glass, metal = (
        mats["cream"], mats["shade"], mats["leaf"], mats["wood"], mats["glass"], mats["metal"]
    )
    if form == "quad":
        parts += [
            sphere("body", (0, 0.05, 0.30), (0.32, 0.24, 0.22), cream),
            sphere("head", (0, 0.26, 0.36), (0.16, 0.14, 0.14), shade),
            sphere("snout", (0, 0.34, 0.32), (0.09, 0.09, 0.07), cream),
            sphere("earL", (-0.10, 0.26, 0.48), (0.06, 0.05, 0.07), leaf),
            sphere("earR", (0.10, 0.26, 0.48), (0.06, 0.05, 0.07), leaf),
            cyl("legFL", (-0.12, 0.12, 0.12), 0.04, 0.16, wood),
            cyl("legFR", (0.12, 0.12, 0.12), 0.04, 0.16, wood),
            cyl("legBL", (-0.12, -0.10, 0.12), 0.04, 0.16, wood),
            cyl("legBR", (0.12, -0.10, 0.12), 0.04, 0.16, wood),
            sphere("leaf1", (-0.06, 0, 0.52), (0.10, 0.04, 0.03), leaf),
            sphere("leaf2", (0.06, 0, 0.54), (0.09, 0.04, 0.03), leaf),
        ]
    elif form == "construct":
        parts += [
            sphere("core", (0, 0, 0.50), (0.28, 0.24, 0.32), metal),
            sphere("head", (0, 0.02, 0.92), (0.20, 0.18, 0.18), cream),
            sphere("ember", (0, 0.20, 0.54), (0.12, 0.06, 0.12), glass),
            cyl("armL", (-0.34, 0, 0.54), 0.06, 0.28, metal, (0, 0, 0.2)),
            cyl("armR", (0.34, 0, 0.54), 0.06, 0.28, metal, (0, 0, -0.2)),
            cyl("legL", (-0.10, 0, 0.16), 0.065, 0.24, wood),
            cyl("legR", (0.10, 0, 0.16), 0.065, 0.24, wood),
            sphere("footL", (-0.10, 0.06, 0.03), (0.08, 0.10, 0.04), metal),
            sphere("footR", (0.10, 0.06, 0.03), (0.08, 0.10, 0.04), metal),
        ]
    else:  # humanoid default
        parts += [
            sphere("torso", (0, 0.02, 0.52), (0.20, 0.15, 0.26), cream),
            sphere("hips", (0, 0.0, 0.32), (0.16, 0.12, 0.14), shade),
            sphere("head", (0, 0.05, 0.92), (0.15, 0.14, 0.15), shade),
            sphere("hair", (0, -0.02, 1.02), (0.16, 0.12, 0.08), wood),
            cyl("armL", (-0.24, 0, 0.58), 0.035, 0.24, cream, (0, 0, 0.25)),
            cyl("armR", (0.24, 0, 0.58), 0.035, 0.24, cream, (0, 0, -0.25)),
            sphere("handL", (-0.34, 0.04, 0.44), (0.045, 0.045, 0.045), leaf),
            sphere("handR", (0.34, 0.04, 0.44), (0.045, 0.045, 0.045), leaf),
            cyl("legL", (-0.08, 0, 0.16), 0.04, 0.24, shade),
            cyl("legR", (0.08, 0, 0.16), 0.04, 0.24, shade),
            sphere("footL", (-0.08, 0.07, 0.03), (0.06, 0.09, 0.03), wood),
            sphere("footR", (0.08, 0.07, 0.03), (0.06, 0.09, 0.03), wood),
        ]
    return parts


CHARACTERS = [
    {
        "id": "CCP-RH-001", "slug": "nori7", "form": "nori", "nori_path": True,
        "colors": {
            "cream": (0.78, 0.74, 0.58, 1), "shade": (0.68, 0.64, 0.50, 1),
            "leaf": (0.28, 0.68, 0.28, 1), "wood": (0.40, 0.55, 0.30, 1),
            "glass": (0.10, 0.90, 0.95, 1), "metal": (0.45, 0.48, 0.52, 1),
            "accent": (0.25, 0.62, 0.32, 1),
        },
    },
    {
        "id": "CCP-NS-002", "slug": "may_mach", "form": "may_mach",
        "colors": {
            "cream": (0.99, 0.88, 0.28, 1), "shade": (0.92, 0.78, 0.35, 1),
            "leaf": (0.45, 0.75, 0.50, 1), "wood": (0.35, 0.55, 0.85, 1),
            "glass": (0.60, 0.85, 0.95, 1), "metal": (0.70, 0.72, 0.74, 1),
            "accent": (0.45, 0.75, 0.50, 1),
        },
    },
    {
        "id": "CCP-NW-003", "slug": "bac_bap", "form": "bac_bap",
        "colors": {
            "cream": (0.95, 0.48, 0.22, 1),  # orange coveralls
            "shade": (0.85, 0.62, 0.45, 1),  # tan skin
            "leaf": (0.92, 0.88, 0.80, 1),   # cream gloves/boots
            "wood": (0.42, 0.28, 0.18, 1),   # brown mustache/strap
            "glass": (0.20, 0.20, 0.22, 1),
            "metal": (0.55, 0.52, 0.48, 1),  # toolbox
            "accent": (0.45, 0.50, 0.30, 1),
        },
    },
    {
        "id": "CCP-CT-004", "slug": "bui_mo", "form": "quad",
        "colors": {
            "cream": (0.92, 0.84, 0.70, 1), "shade": (0.80, 0.72, 0.58, 1),
            "leaf": (0.40, 0.78, 0.42, 1), "wood": (0.55, 0.40, 0.28, 1),
            "glass": (0.30, 0.25, 0.20, 1), "metal": (0.50, 0.50, 0.50, 1),
            "accent": (0.40, 0.78, 0.42, 1),
        },
    },
    {
        "id": "SPH-RH-011", "slug": "kito", "form": "kito",
        "colors": {
            "cream": (0.90, 0.84, 0.70, 1), "shade": (0.80, 0.74, 0.60, 1),
            "leaf": (0.35, 0.82, 0.30, 1), "wood": (0.85, 0.72, 0.30, 1),
            "glass": (0.50, 0.95, 0.40, 1), "metal": (0.70, 0.72, 0.40, 1),
            "accent": (0.35, 0.82, 0.30, 1),
        },
    },
    {
        "id": "OA-RG-021", "slug": "nereu", "form": "robot",
        "colors": {
            "cream": (0.55, 0.82, 0.90, 1), "shade": (0.40, 0.65, 0.78, 1),
            "leaf": (0.30, 0.70, 0.75, 1), "wood": (0.35, 0.55, 0.70, 1),
            "glass": (0.20, 0.90, 0.95, 1), "metal": (0.50, 0.60, 0.70, 1),
            "accent": (0.20, 0.70, 0.80, 1),
        },
    },
    {
        "id": "AC-CO-015", "slug": "cinder", "form": "construct",
        "colors": {
            "cream": (0.88, 0.75, 0.55, 1), "shade": (0.70, 0.55, 0.40, 1),
            "leaf": (0.90, 0.40, 0.20, 1), "wood": (0.45, 0.32, 0.22, 1),
            "glass": (1.0, 0.45, 0.15, 1), "metal": (0.55, 0.50, 0.48, 1),
            "accent": (1.0, 0.40, 0.12, 1),
        },
    },
    {
        "id": "TD-CT-028", "slug": "patch", "form": "quad",
        "colors": {
            "cream": (0.88, 0.72, 0.55, 1), "shade": (0.72, 0.55, 0.40, 1),
            "leaf": (0.50, 0.70, 0.40, 1), "wood": (0.50, 0.35, 0.25, 1),
            "glass": (0.40, 0.30, 0.25, 1), "metal": (0.55, 0.50, 0.45, 1),
            "accent": (0.50, 0.70, 0.40, 1),
        },
    },
    {
        "id": "SV-NW-019", "slug": "truc_nhi", "form": "humanoid",
        "colors": {
            "cream": (0.92, 0.85, 0.75, 1), "shade": (0.80, 0.70, 0.60, 1),
            "leaf": (0.45, 0.70, 0.50, 1), "wood": (0.55, 0.35, 0.55, 1),
            "glass": (0.70, 0.80, 0.90, 1), "metal": (0.65, 0.65, 0.68, 1),
            "accent": (0.55, 0.35, 0.55, 1),
        },
    },
    {
        "id": "SPH-NG-009", "slug": "luma", "form": "humanoid",
        "colors": {
            "cream": (0.95, 0.90, 0.70, 1), "shade": (0.85, 0.80, 0.55, 1),
            "leaf": (0.55, 0.80, 0.40, 1), "wood": (0.90, 0.70, 0.30, 1),
            "glass": (0.95, 0.90, 0.40, 1), "metal": (0.75, 0.70, 0.50, 1),
            "accent": (0.55, 0.80, 0.40, 1),
        },
    },
]


def skin_and_export(mesh_obj, arm, out_path: Path):
    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=str(out_path),
        export_format="GLB",
        use_selection=False,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        export_materials="EXPORT",
        export_animations=True,
    )


def build_one(spec):
    clear()
    cols = spec["colors"]
    mats = {
        "cream": mat("MAT_cream", cols["cream"]),
        "shade": mat("MAT_shade", cols["shade"]),
        "leaf": mat("MAT_leaf", cols["leaf"]),
        "wood": mat("MAT_wood", cols["wood"]),
        "glass": mat("MAT_glass", cols["glass"], emit=1.5),
        "metal": mat("MAT_metal", cols["metal"], metal=0.4),
        "accent": mat("MAT_accent", cols.get("accent", cols["leaf"])),
    }
    parts = []
    form = spec["form"]
    if form == "nori":
        body_nori(parts, mats)
    elif form == "bac_bap":
        body_bac_bap(parts, mats)
    elif form == "may_mach":
        body_may_mach(parts, mats)
    elif form == "kito":
        body_kito(parts, mats)
    else:
        body_generic(parts, mats, form)

    mesh = join(parts, f"Mesh_{spec['slug']}")
    arm = armature()
    clips = author_clips(arm)

    if spec.get("nori_path"):
        out_dir = GAME_NORI
    else:
        out_dir = GAME_CAST / spec["slug"] / "export"
    out_dir.mkdir(parents=True, exist_ok=True)
    glb = out_dir / f"{spec['slug']}_rigged.glb"
    qglb = QUAR / f"{spec['slug']}_rigged.glb"
    skin_and_export(mesh, arm, qglb)
    glb.write_bytes(qglb.read_bytes())
    dig = sha(glb)
    return {
        "character_id": spec["id"],
        "slug": spec["slug"],
        "form": form,
        "glb": str(glb).replace("\\", "/"),
        "glb_sha256": dig,
        "glb_bytes": glb.stat().st_size,
        "clips": clips,
        "job_id": JOB,
        "accepted": False,
        "self_accept": False,
    }


def main():
    log("start per-card polish 10 cast")
    results = []
    for spec in CHARACTERS:
        try:
            r = build_one(spec)
            results.append(r)
            log(f"OK {spec['id']} {spec['slug']} form={spec['form']} sha={r['glb_sha256'][:12]}…")
        except Exception as e:
            log(f"FAIL {spec['id']}: {e}")
            import traceback
            traceback.print_exc()
            results.append({"character_id": spec["id"], "ok": False, "error": str(e)})

    # update roster
    roster = json.loads(ROSTER.read_text(encoding="utf-8"))
    by_id = {c["character_id"]: c for c in roster.get("characters", [])}
    for r in results:
        if "glb_sha256" not in r:
            continue
        cid = r["character_id"]
        row = by_id.get(cid, {"character_id": cid})
        slug = r["slug"]
        if cid == "CCP-RH-001":
            row["glb"] = "res://assets/ucbv_001/character/nori7/export/nori7_rigged.glb"
        else:
            row["glb"] = f"res://assets/ucbv_001/cast/{slug}/export/{slug}_rigged.glb"
        row["glb_sha256"] = r["glb_sha256"]
        row["source"] = JOB
        row["visual"] = "cast_per_card_v3"
        row["production"] = True
        by_id[cid] = row
    roster["characters"] = list(by_id.values())
    roster["accepted"] = False
    roster["self_accept"] = False
    ROSTER.write_text(json.dumps(roster, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log("roster updated")

    # sync nori companion sha files
    nori = next((r for r in results if r.get("character_id") == "CCP-RH-001" and "glb_sha256" in r), None)
    if nori:
        dig = nori["glb_sha256"]
        paths_gd = Path(r"E:\AIdle_openworld\game\scripts\modules\ucbv_001\ucbv_paths.gd")
        t = paths_gd.read_text(encoding="utf-8")
        import re
        t = re.sub(r'NORI_GLB_SHA256_EXPECTED := "[0-9a-f]{64}"', f'NORI_GLB_SHA256_EXPECTED := "{dig}"', t)
        paths_gd.write_text(t, encoding="utf-8")
        adapt = Path(r"E:\AIdle_openworld\game\resources\ucbv_001\character\nori7_animation_adapter.json")
        at = adapt.read_text(encoding="utf-8")
        at = re.sub(r'"sha256":\s*"[0-9a-f]{64}"', f'"sha256": "{dig}"', at, count=1)
        adapt.write_text(at, encoding="utf-8")
        log(f"nori sha synced {dig[:16]}")

    ok = all("glb_sha256" in r for r in results)
    log(f"DONE ok={ok} count={len(results)}")
    (QUAR / "summary.json").write_text(json.dumps({"job": JOB, "results": results, "accepted": False}, indent=2), encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

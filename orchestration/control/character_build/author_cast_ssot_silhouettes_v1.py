# -*- coding: utf-8 -*-
"""CAST_SSOT_SILHOUETTES_V1 — re-author all 10 town-cadastre cast GLBs.

Root cause of white_sphere_cast_presenter (content half):
  prior batch joined sphere primitives into a mesh named Sphere; at town scale
  all characters read as white blobs. This pass rebuilds distinct silhouettes
  per form (pear robot, humanoid, quad, construct) with high-contrast palettes
  aligned to MOCKUP_SSOT_V2 character cards.

Also keeps 10 real AnimationPlayer clips (idle+walk+…) for cast_presenter.
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

JOB = "CAST_SSOT_SILHOUETTES_V1"
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
    ("idle", 3.0, "idle"),
    ("walk", 0.8, "walk"),
    ("scan", 1.2, "scan"),
    ("happy", 1.0, "happy"),
    ("cancel", 0.6, "cancel"),
    ("turn_left", 0.5, "turn_l"),
    ("turn_right", 0.5, "turn_r"),
    ("build_place", 0.67, "build"),
    ("build_place_hold", 0.8, "hold"),
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
    bpy.ops.mesh.primitive_uv_sphere_add(segments=18, ring_count=12, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.clear()
    o.data.materials.append(material)
    return o


def cyl(name, loc, r, depth, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=r, depth=depth, location=loc)
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
    data = bpy.data.armatures.new("skel_cast_v2")
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


# ---- stronger silhouettes ----

def body_nori_pear(parts, mats):
    """Nori-7 SSOT: pear body, cyan eye, green snout, leaf sprout, backpack vial."""
    cream, shade, leaf, glass, metal, accent = (
        mats["cream"], mats["shade"], mats["leaf"], mats["glass"], mats["metal"], mats.get("accent", mats["leaf"])
    )
    parts += [
        # pear body (elongated Y)
        sphere("body", (0, 0.02, 0.42), (0.32, 0.30, 0.38), cream),
        sphere("belly", (0, 0.06, 0.28), (0.26, 0.22, 0.22), shade),
        # head dome
        sphere("head", (0, 0.04, 0.78), (0.28, 0.26, 0.28), cream),
        # single cyan eye
        sphere("eye", (0.0, 0.26, 0.80), (0.10, 0.06, 0.10), glass),
        sphere("pupil", (0.0, 0.30, 0.80), (0.04, 0.03, 0.04), metal),
        # green snout/barrel
        cyl("snout", (0, 0.32, 0.70), 0.06, 0.22, leaf, (math.pi / 2, 0, 0)),
        # arms
        cyl("armL", (-0.30, 0.02, 0.55), 0.05, 0.22, cream, (0, 0, 0.35)),
        cyl("armR", (0.30, 0.02, 0.55), 0.05, 0.22, cream, (0, 0, -0.35)),
        sphere("handL", (-0.42, 0.06, 0.42), (0.06, 0.06, 0.06), leaf),
        sphere("handR", (0.42, 0.06, 0.42), (0.06, 0.06, 0.06), leaf),
        # legs + feet
        cyl("legL", (-0.10, 0.02, 0.14), 0.05, 0.18, cream),
        cyl("legR", (0.10, 0.02, 0.14), 0.05, 0.18, cream),
        sphere("footL", (-0.10, 0.08, 0.03), (0.08, 0.10, 0.04), cream),
        sphere("footR", (0.10, 0.08, 0.03), (0.08, 0.10, 0.04), cream),
        # leaf sprout
        cyl("stem", (0, 0.0, 1.05), 0.02, 0.14, leaf),
        sphere("leafL", (-0.08, 0.0, 1.16), (0.10, 0.05, 0.04), leaf),
        sphere("leafR", (0.08, 0.0, 1.16), (0.10, 0.05, 0.04), leaf),
        # backpack vial
        cyl("vial", (-0.22, -0.18, 0.55), 0.05, 0.16, accent),
        sphere("vialTop", (-0.22, -0.18, 0.65), (0.04, 0.04, 0.03), metal),
    ]
    return parts


def body_robot(parts, mats):
    cream, shade, leaf, glass, metal = mats["cream"], mats["shade"], mats["leaf"], mats["glass"], mats["metal"]
    parts += [
        sphere("body", (0, 0.02, 0.42), (0.30, 0.28, 0.32), cream),
        sphere("head", (0, 0.04, 0.82), (0.24, 0.22, 0.24), shade),
        sphere("eyeL", (-0.08, 0.22, 0.84), (0.06, 0.04, 0.06), glass),
        sphere("eyeR", (0.08, 0.22, 0.84), (0.06, 0.04, 0.06), glass),
        cyl("armL", (-0.30, 0, 0.58), 0.045, 0.22, cream, (0, 0, 0.3)),
        cyl("armR", (0.30, 0, 0.58), 0.045, 0.22, cream, (0, 0, -0.3)),
        sphere("handL", (-0.42, 0.05, 0.45), (0.055, 0.055, 0.055), leaf),
        sphere("handR", (0.42, 0.05, 0.45), (0.055, 0.055, 0.055), leaf),
        cyl("legL", (-0.10, 0, 0.14), 0.05, 0.18, cream),
        cyl("legR", (0.10, 0, 0.14), 0.05, 0.18, cream),
        sphere("footL", (-0.10, 0.07, 0.03), (0.07, 0.09, 0.04), metal),
        sphere("footR", (0.10, 0.07, 0.03), (0.07, 0.09, 0.04), metal),
        sphere("sprout", (0, 0, 1.12), (0.08, 0.06, 0.06), leaf),
    ]
    return parts


def body_humanoid(parts, mats, stocky=False):
    cream, shade, wood, leaf = mats["cream"], mats["shade"], mats["wood"], mats["leaf"]
    s = 1.2 if stocky else 1.0
    parts += [
        sphere("torso", (0, 0.02, 0.52 * s), (0.20 * s, 0.15 * s, 0.26 * s), cream),
        sphere("hips", (0, 0.0, 0.32 * s), (0.16 * s, 0.12 * s, 0.14 * s), shade),
        sphere("head", (0, 0.05, 0.92 * s), (0.15, 0.14, 0.15), shade),
        sphere("hair", (0, -0.02, 1.02 * s), (0.16, 0.12, 0.08), wood),
        cyl("armL", (-0.24 * s, 0, 0.58 * s), 0.035, 0.24, cream, (0, 0, 0.25)),
        cyl("armR", (0.24 * s, 0, 0.58 * s), 0.035, 0.24, cream, (0, 0, -0.25)),
        sphere("handL", (-0.34 * s, 0.04, 0.44 * s), (0.045, 0.045, 0.045), leaf),
        sphere("handR", (0.34 * s, 0.04, 0.44 * s), (0.045, 0.045, 0.045), leaf),
        cyl("legL", (-0.08, 0, 0.16), 0.04, 0.24, shade),
        cyl("legR", (0.08, 0, 0.16), 0.04, 0.24, shade),
        sphere("footL", (-0.08, 0.07, 0.03), (0.06, 0.09, 0.03), wood),
        sphere("footR", (0.08, 0.07, 0.03), (0.06, 0.09, 0.03), wood),
    ]
    return parts


def body_quad(parts, mats, leaves=True):
    cream, shade, leaf, wood = mats["cream"], mats["shade"], mats["leaf"], mats["wood"]
    parts += [
        sphere("body", (0, 0.05, 0.30), (0.30, 0.22, 0.20), cream),
        sphere("head", (0, 0.24, 0.34), (0.15, 0.13, 0.13), shade),
        sphere("snout", (0, 0.32, 0.30), (0.08, 0.08, 0.06), cream),
        sphere("earL", (-0.09, 0.24, 0.46), (0.05, 0.04, 0.06), leaf),
        sphere("earR", (0.09, 0.24, 0.46), (0.05, 0.04, 0.06), leaf),
        cyl("legFL", (-0.12, 0.12, 0.12), 0.035, 0.16, wood),
        cyl("legFR", (0.12, 0.12, 0.12), 0.035, 0.16, wood),
        cyl("legBL", (-0.12, -0.10, 0.12), 0.035, 0.16, wood),
        cyl("legBR", (0.12, -0.10, 0.12), 0.035, 0.16, wood),
        sphere("tail", (0, -0.24, 0.32), (0.05, 0.14, 0.05), wood),
    ]
    if leaves:
        parts += [
            sphere("leaf1", (-0.06, 0, 0.50), (0.09, 0.04, 0.03), leaf),
            sphere("leaf2", (0.06, 0, 0.52), (0.08, 0.04, 0.03), leaf),
            sphere("leaf3", (0, -0.02, 0.54), (0.07, 0.03, 0.03), leaf),
        ]
    return parts


def body_construct(parts, mats):
    cream, metal, wood, glass = mats["cream"], mats["metal"], mats["wood"], mats["glass"]
    parts += [
        sphere("core", (0, 0, 0.48), (0.26, 0.22, 0.30), metal),
        sphere("head", (0, 0.02, 0.88), (0.18, 0.16, 0.16), cream),
        sphere("ember", (0, 0.18, 0.52), (0.10, 0.05, 0.10), glass),
        cyl("armL", (-0.32, 0, 0.52), 0.055, 0.26, metal, (0, 0, 0.2)),
        cyl("armR", (0.32, 0, 0.52), 0.055, 0.26, metal, (0, 0, -0.2)),
        cyl("legL", (-0.10, 0, 0.16), 0.06, 0.22, wood),
        cyl("legR", (0.10, 0, 0.16), 0.06, 0.22, wood),
        sphere("footL", (-0.10, 0.06, 0.03), (0.07, 0.09, 0.04), metal),
        sphere("footR", (0.10, 0.06, 0.03), (0.07, 0.09, 0.04), metal),
    ]
    return parts


# All 10 town-cadastre characters including nori7
CHARACTERS = [
    {
        "id": "CCP-RH-001",
        "slug": "nori7",
        "form": "nori_pear",
        "out": "nori7",
        "nori_path": True,
        "colors": {
            "cream": (0.93, 0.92, 0.82, 1),
            "shade": (0.88, 0.86, 0.76, 1),
            "leaf": (0.40, 0.70, 0.35, 1),
            "wood": (0.45, 0.55, 0.30, 1),
            "glass": (0.15, 0.85, 0.90, 1),
            "metal": (0.55, 0.58, 0.60, 1),
            "accent": (0.30, 0.65, 0.35, 1),
        },
    },
    {
        "id": "CCP-NS-002",
        "slug": "may_mach",
        "form": "humanoid",
        "stocky": False,
        "colors": {
            "cream": (0.99, 0.90, 0.45, 1),
            "shade": (0.95, 0.82, 0.40, 1),
            "leaf": (0.45, 0.75, 0.50, 1),
            "wood": (0.40, 0.60, 0.80, 1),
            "glass": (0.60, 0.85, 0.95, 1),
            "metal": (0.70, 0.72, 0.74, 1),
        },
    },
    {
        "id": "CCP-NW-003",
        "slug": "bac_bap",
        "form": "humanoid",
        "stocky": True,
        "colors": {
            "cream": (0.90, 0.52, 0.32, 1),
            "shade": (0.55, 0.48, 0.32, 1),
            "leaf": (0.42, 0.55, 0.28, 1),
            "wood": (0.55, 0.38, 0.22, 1),
            "glass": (0.70, 0.80, 0.85, 1),
            "metal": (0.60, 0.62, 0.65, 1),
        },
    },
    {
        "id": "CCP-CT-004",
        "slug": "bui_mo",
        "form": "quad",
        "leaves": True,
        "colors": {
            "cream": (0.99, 0.94, 0.86, 1),
            "shade": (0.92, 0.86, 0.76, 1),
            "leaf": (0.45, 0.78, 0.50, 1),
            "wood": (0.55, 0.40, 0.28, 1),
            "glass": (0.30, 0.25, 0.20, 1),
            "metal": (0.50, 0.50, 0.50, 1),
        },
    },
    {
        "id": "SPH-RH-011",
        "slug": "kito",
        "form": "robot",
        "colors": {
            "cream": (0.99, 0.94, 0.86, 1),
            "shade": (0.92, 0.86, 0.76, 1),
            "leaf": (0.50, 0.85, 0.40, 1),
            "wood": (0.85, 0.72, 0.30, 1),
            "glass": (0.60, 0.92, 0.45, 1),
            "metal": (0.75, 0.78, 0.45, 1),
        },
    },
    {
        "id": "OA-RG-021",
        "slug": "nereu",
        "form": "robot",
        "colors": {
            "cream": (0.80, 0.92, 0.95, 1),
            "shade": (0.50, 0.72, 0.85, 1),
            "leaf": (0.25, 0.68, 0.75, 1),
            "wood": (0.38, 0.52, 0.58, 1),
            "glass": (0.35, 0.85, 0.95, 1),
            "metal": (0.52, 0.62, 0.68, 1),
        },
    },
    {
        "id": "AC-CO-015",
        "slug": "cinder",
        "form": "construct",
        "colors": {
            "cream": (0.85, 0.72, 0.50, 1),
            "shade": (0.62, 0.48, 0.32, 1),
            "leaf": (0.95, 0.42, 0.18, 1),
            "wood": (0.42, 0.28, 0.18, 1),
            "glass": (1.0, 0.50, 0.20, 1),
            "metal": (0.68, 0.52, 0.32, 1),
        },
    },
    {
        "id": "TD-CT-028",
        "slug": "patch",
        "form": "quad",
        "leaves": False,
        "colors": {
            "cream": (0.92, 0.76, 0.58, 1),
            "shade": (0.72, 0.52, 0.38, 1),
            "leaf": (0.52, 0.70, 0.42, 1),
            "wood": (0.55, 0.40, 0.30, 1),
            "glass": (0.20, 0.20, 0.25, 1),
            "metal": (0.50, 0.50, 0.55, 1),
        },
    },
    {
        "id": "SV-NW-019",
        "slug": "truc_nhi",
        "form": "humanoid",
        "stocky": False,
        "colors": {
            "cream": (0.95, 0.90, 0.82, 1),
            "shade": (0.72, 0.82, 0.68, 1),
            "leaf": (0.42, 0.70, 0.38, 1),
            "wood": (0.55, 0.42, 0.28, 1),
            "glass": (0.55, 0.80, 0.65, 1),
            "metal": (0.60, 0.60, 0.55, 1),
        },
    },
    {
        "id": "SPH-NG-009",
        "slug": "luma",
        "form": "humanoid",
        "stocky": False,
        "colors": {
            "cream": (0.99, 0.94, 0.82, 1),
            "shade": (0.95, 0.82, 0.45, 1),
            "leaf": (0.42, 0.75, 0.42, 1),
            "wood": (0.85, 0.68, 0.28, 1),
            "glass": (0.65, 0.90, 0.95, 1),
            "metal": (0.80, 0.75, 0.40, 1),
        },
    },
]


def build_one(spec):
    clear()
    bpy.context.scene.render.fps = FPS
    cols = spec["colors"]
    mats = {
        "cream": mat("MAT_cream", cols["cream"]),
        "shade": mat("MAT_shade", cols["shade"]),
        "leaf": mat("MAT_leaf", cols["leaf"]),
        "wood": mat("MAT_wood", cols["wood"]),
        "glass": mat("MAT_glass", cols["glass"], 0.25, 0.05, emit=1.2 if cols["glass"][2] > 0.7 else 0.0),
        "metal": mat("MAT_metal", cols["metal"], 0.35, 0.5),
        "accent": mat("MAT_accent", cols.get("accent", cols["leaf"])),
    }
    parts = []
    form = spec["form"]
    if form == "nori_pear":
        parts = body_nori_pear(parts, mats)
    elif form == "robot":
        parts = body_robot(parts, mats)
    elif form == "humanoid":
        parts = body_humanoid(parts, mats, stocky=bool(spec.get("stocky")))
    elif form == "quad":
        parts = body_quad(parts, mats, leaves=bool(spec.get("leaves", True)))
    elif form == "construct":
        parts = body_construct(parts, mats)
    mesh = join(parts, f"{spec['slug']}_Mesh")
    arm = armature()
    mesh.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    mesh.parent = arm
    root = bpy.data.objects.new(spec["id"], None)
    bpy.context.collection.objects.link(root)
    arm.parent = root
    clip_report = author_clips(arm)

    if spec.get("nori_path"):
        out_dir = GAME_NORI
    else:
        out_dir = GAME_CAST / spec["slug"] / "export"
    out_dir.mkdir(parents=True, exist_ok=True)
    glb = out_dir / f"{spec['slug']}_rigged.glb"
    qdir = QUAR / spec["slug"]
    qdir.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(glb),
        export_format="GLB",
        use_selection=False,
        export_animations=True,
        export_skins=True,
        export_yup=True,
    )
    shutil.copy2(glb, qdir / glb.name)
    dig = sha(glb)
    meta = {
        "character_id": spec["id"],
        "slug": spec["slug"],
        "form": form,
        "glb": str(glb).replace("\\", "/"),
        "glb_sha256": dig,
        "glb_bytes": glb.stat().st_size,
        "clips": clip_report,
        "job_id": JOB,
        "accepted": False,
        "self_accept": False,
    }
    (out_dir / "validation.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (qdir / "validation.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    log(f"OK {spec['id']} {spec['slug']} form={form} sha={dig[:12]}…")
    return meta


def update_roster(results):
    if not ROSTER.exists():
        return
    data = json.loads(ROSTER.read_text(encoding="utf-8"))
    by_id = {c["character_id"]: c for c in data.get("characters", [])}
    for r in results:
        row = by_id.get(r["character_id"])
        if not row:
            continue
        # keep res:// path shape
        if r["character_id"] == "CCP-RH-001":
            row["glb"] = "res://assets/ucbv_001/character/nori7/export/nori7_rigged.glb"
        else:
            row["glb"] = f"res://assets/ucbv_001/cast/{r['slug']}/export/{r['slug']}_rigged.glb"
        row["glb_sha256"] = r["glb_sha256"]
        row["source"] = JOB
        row["visual"] = "cast_ssot_silhouettes_v1"
    data["cast_ssot_revision"] = JOB
    data["accepted"] = False
    data["self_accept"] = False
    ROSTER.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log("roster updated")


def main():
    log("start re-author 10 cast silhouettes")
    results = []
    for spec in CHARACTERS:
        try:
            results.append(build_one(spec))
        except Exception as e:
            log(f"FAIL {spec['id']}: {e}")
            import traceback
            traceback.print_exc()
    update_roster(results)
    out = QUAR / "batch_result.json"
    out.write_text(
        json.dumps({"job": JOB, "results": results, "accepted": False}, indent=2),
        encoding="utf-8",
    )
    ok = len(results) == 10
    log(f"DONE ok={ok} count={len(results)}")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        log(f"FATAL {e}")
        import traceback
        traceback.print_exc()
        raise SystemExit(1)

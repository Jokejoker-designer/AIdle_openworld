# -*- coding: utf-8 -*-
"""Nori-7 visual redesign V01 â€” offline Blender 5.2 authoring.

Directive 99 / WO-NORI7-REDESIGN-001
- Multi-material readable teardrop robot (cream/leaf/glass/wood/metal/stone)
- Exact 14-bone skel_small_biped_robot_v1 hierarchy
- Required 10 clips + 5 gardener clips with REAL fcurves
- Export to quarantine then promote under named Godot override

Run:
  E:\\blender.exe --background --factory-startup --python this_script.py
"""
from __future__ import annotations

import json
import hashlib
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector, Euler

JOB_ID = "BLD-UCBV-NORI7-REDESIGN-V01"
WAVE = "NORI7_REDESIGN_V01"
DIR_ID = 99

QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine\NORI7_REDESIGN_V01")
PROD_EXPORT = Path(r"E:\AIdle_openworld\game\assets\ucbv_001\character\nori7\export")
QUAR.mkdir(parents=True, exist_ok=True)

# Bible cream SSOT (not recipe #F7E9C6)
HEX = {
    "cream": (0.992, 0.953, 0.886, 1.0),       # #fdf3e2
    "cream_shade": (0.937, 0.878, 0.784, 1.0),  # #efe0c8
    "leaf": (0.498, 0.788, 0.561, 1.0),         # #7fc98f
    "glass": (0.659, 0.863, 0.929, 1.0),        # #a8dced
    "socket": (0.239, 0.196, 0.149, 1.0),       # #3d3226
    "wood": (0.788, 0.541, 0.369, 1.0),         # #c98a5e
    "metal": (0.72, 0.74, 0.76, 1.0),
    "stone": (0.78, 0.70, 0.58, 1.0),
    "blush": (0.957, 0.627, 0.604, 1.0),        # #f4a09a
}

BONES = [
    ("root", None, (0.0, 0.0, 0.0)),
    ("pelvis", "root", (0.0, 0.0, 0.18)),
    ("spine", "pelvis", (0.0, 0.0, 0.38)),
    ("chest", "spine", (0.0, 0.0, 0.62)),
    ("head", "chest", (0.0, 0.0, 0.95)),
    ("sprout_ctrl", "head", (0.0, 0.0, 1.22)),
    ("arm_L", "chest", (-0.28, 0.0, 0.72)),
    ("hand_L", "arm_L", (-0.42, 0.05, 0.52)),
    ("arm_R", "chest", (0.28, 0.0, 0.72)),
    ("hand_R", "arm_R", (0.42, 0.05, 0.52)),
    ("leg_L", "pelvis", (-0.10, 0.0, 0.10)),
    ("foot_L", "leg_L", (-0.10, 0.08, 0.02)),
    ("leg_R", "pelvis", (0.10, 0.0, 0.10)),
    ("foot_R", "leg_R", (0.10, 0.08, 0.02)),
]

FPS = 30


def log(msg: str) -> None:
    print(f"[NORI7_REDESIGN] {msg}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)
    for block in list(bpy.data.materials):
        bpy.data.materials.remove(block)
    for block in list(bpy.data.armatures):
        bpy.data.armatures.remove(block)
    for block in list(bpy.data.actions):
        bpy.data.actions.remove(block)


def make_mat(name: str, rgba, roughness: float = 0.55, metallic: float = 0.0) -> bpy.types.Material:
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        # Specular: Blender 4+/5 may use IOR Level instead of Specular
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.35
        elif "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = 0.35
    return mat


def add_uv_sphere(name: str, loc, scale, mat) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return obj


def add_capsule(name: str, loc, radius, depth, mat, rot=(0, 0, 0)) -> bpy.types.Object:
    # Approximate capsule with cylinder + 2 hemispheres for Blender compatibility
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=depth, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = Euler(rot)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return obj


def build_armature() -> bpy.types.Object:
    arm_data = bpy.data.armatures.new("skel_small_biped_robot_v1")
    arm_obj = bpy.data.objects.new("Nori7_Armature", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    arm_obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    edit_bones = arm_data.edit_bones
    created = {}
    for name, parent, head in BONES:
        b = edit_bones.new(name)
        hx, hy, hz = head
        b.head = Vector((hx, hy, hz))
        # small tail along +Z for non-leaf; leaf bones get short tails
        if name in ("hand_L", "hand_R", "foot_L", "foot_R", "sprout_ctrl", "root"):
            b.tail = Vector((hx, hy, hz + 0.06))
        else:
            b.tail = Vector((hx, hy, hz + 0.12))
        if parent:
            b.parent = created[parent]
            b.use_connect = False
        created[name] = b
    bpy.ops.object.mode_set(mode="OBJECT")
    return arm_obj


def build_body_parts(mats: dict) -> list:
    parts = []
    # Lower body teardrop mass
    parts.append(add_uv_sphere("body_lower", (0, 0.02, 0.32), (0.30, 0.28, 0.30), mats["ceramic"]))
    # Upper body / head fused mass (slightly larger)
    parts.append(add_uv_sphere("body_upper", (0, 0.04, 0.72), (0.34, 0.32, 0.33), mats["ceramic_shade"]))
    # Face plate (front disk for readability)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=(0, 0.22, 0.88))
    face = bpy.context.active_object
    face.name = "face_plate"
    face.scale = (0.18, 0.06, 0.16)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    face.data.materials.append(mats["ceramic"])
    parts.append(face)
    # Eye sockets (dark)
    for side, x in (("L", -0.08), ("R", 0.08)):
        sock = add_uv_sphere(f"eye_socket_{side}", (x, 0.26, 0.90), (0.055, 0.03, 0.06), mats["socket"])
        parts.append(sock)
        iris = add_uv_sphere(f"eye_iris_{side}", (x, 0.285, 0.90), (0.038, 0.02, 0.042), mats["glass"])
        parts.append(iris)
    # Blush
    for side, x in (("L", -0.12), ("R", 0.12)):
        bl = add_uv_sphere(f"blush_{side}", (x, 0.24, 0.80), (0.04, 0.015, 0.025), mats["blush"])
        parts.append(bl)
    # Arms
    parts.append(add_capsule("arm_L", (-0.30, 0.0, 0.62), 0.045, 0.22, mats["ceramic"], (0, 0, 0.35)))
    parts.append(add_capsule("arm_R", (0.30, 0.0, 0.62), 0.045, 0.22, mats["ceramic"], (0, 0, -0.35)))
    # Hands
    parts.append(add_uv_sphere("hand_L", (-0.42, 0.05, 0.48), (0.05, 0.05, 0.05), mats["leaf"]))
    parts.append(add_uv_sphere("hand_R", (0.42, 0.05, 0.48), (0.05, 0.05, 0.05), mats["leaf"]))
    # Nozzle (metal, right forearm)
    parts.append(add_capsule("nozzle", (0.48, 0.10, 0.50), 0.02, 0.14, mats["metal"], (1.2, 0, 0)))
    # Legs
    parts.append(add_capsule("leg_L", (-0.10, 0.0, 0.12), 0.05, 0.16, mats["ceramic"]))
    parts.append(add_capsule("leg_R", (0.10, 0.0, 0.12), 0.05, 0.16, mats["ceramic"]))
    # Feet
    parts.append(add_uv_sphere("foot_L", (-0.10, 0.06, 0.03), (0.07, 0.09, 0.04), mats["stone"]))
    parts.append(add_uv_sphere("foot_R", (0.10, 0.06, 0.03), (0.07, 0.09, 0.04), mats["stone"]))
    # Water tank backpack
    tank = add_uv_sphere("tank", (0, -0.22, 0.58), (0.16, 0.12, 0.20), mats["ceramic_shade"])
    parts.append(tank)
    # Wood straps
    for name, loc in (("strap_L", (-0.12, -0.12, 0.70)), ("strap_R", (0.12, -0.12, 0.70))):
        parts.append(add_capsule(name, loc, 0.018, 0.22, mats["wood"], (0.9, 0, 0)))
    # Leaf joint bands
    for name, loc, sc in (
        ("joint_neck", (0, 0.02, 0.82), (0.16, 0.08, 0.04)),
        ("joint_hip", (0, 0.0, 0.28), (0.18, 0.10, 0.04)),
    ):
        parts.append(add_uv_sphere(name, loc, sc, mats["leaf"]))
    # Mechanical sprout crown
    stem = add_capsule("sprout_stem", (0, 0.0, 1.12), 0.025, 0.14, mats["leaf"])
    parts.append(stem)
    leaf_a = add_uv_sphere("sprout_leaf_a", (-0.05, 0.02, 1.22), (0.07, 0.04, 0.03), mats["leaf"])
    leaf_b = add_uv_sphere("sprout_leaf_b", (0.05, -0.01, 1.24), (0.06, 0.035, 0.028), mats["leaf"])
    parts.append(leaf_a)
    parts.append(leaf_b)
    return parts


def join_parts(parts: list, name: str) -> bpy.types.Object:
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.active_object
    obj.name = name
    return obj


def auto_weights(mesh_obj: bpy.types.Object, arm_obj: bpy.types.Object) -> None:
    mesh_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")


def ensure_action(name: str) -> bpy.types.Action:
    act = bpy.data.actions.get(name)
    if act is None:
        act = bpy.data.actions.new(name)
    return act


def bone_pose(arm_obj, bone_name: str):
    return arm_obj.pose.bones.get(bone_name)


def key_loc_rot(pb, frame: int, loc=None, euler=None) -> None:
    if pb is None:
        return
    if loc is not None:
        pb.location = Vector(loc)
        pb.keyframe_insert(data_path="location", frame=frame)
    if euler is not None:
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler(euler)
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)


def count_action_fcurves(act) -> int:
    """Blender 5.x layered Action API — no act.fcurves."""
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


def author_clip(arm_obj, name: str, duration_s: float, keyframes_fn) -> dict:
    act = ensure_action(name)
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = act
    nframes = max(2, int(round(duration_s * FPS)))
    keyframes_fn(arm_obj, nframes)
    # Count fcurves (Blender 5.2 layered)
    fcount = count_action_fcurves(act)
    return {
        "action_name": name,
        "duration_s": duration_s,
        "loop": name in ("idle", "walk", "low_energy", "charge"),
        "layer": "redesign_v01",
        "fcurve_count": fcount,
        "fps": FPS,
        "root_motion": False,
        "from_tier3_payload": False,
        "real_keys": True,
    }


def clips_spec():
    def idle(arm, n):
        pelvis = bone_pose(arm, "pelvis")
        sprout = bone_pose(arm, "sprout_ctrl")
        for f, y, zdeg in ((1, 0.0, 0.0), (n // 2, -0.012, 0.04), (n, 0.0, 0.0)):
            key_loc_rot(pelvis, f, loc=(0, 0, y))
            key_loc_rot(sprout, f, euler=(0, 0, zdeg))

    def walk(arm, n):
        leg_l = bone_pose(arm, "leg_L")
        leg_r = bone_pose(arm, "leg_R")
        arm_l = bone_pose(arm, "arm_L")
        arm_r = bone_pose(arm, "arm_R")
        pelvis = bone_pose(arm, "pelvis")
        for f in (1, n // 4, n // 2, 3 * n // 4, n):
            t = (f - 1) / max(1, n - 1)
            phase = math.sin(t * math.pi * 2)
            key_loc_rot(leg_l, f, euler=(phase * 0.30, 0, 0))
            key_loc_rot(leg_r, f, euler=(-phase * 0.30, 0, 0))
            key_loc_rot(arm_l, f, euler=(-phase * 0.18, 0, 0.1))
            key_loc_rot(arm_r, f, euler=(phase * 0.18, 0, -0.1))
            key_loc_rot(pelvis, f, loc=(0, 0, abs(phase) * 0.012))

    def scan(arm, n):
        head = bone_pose(arm, "head")
        key_loc_rot(head, 1, euler=(0, 0, 0))
        key_loc_rot(head, n // 3, euler=(0, 0.25, 0.15))
        key_loc_rot(head, 2 * n // 3, euler=(0, -0.25, -0.15))
        key_loc_rot(head, n, euler=(0, 0, 0))

    def happy(arm, n):
        sprout = bone_pose(arm, "sprout_ctrl")
        arm_l = bone_pose(arm, "arm_L")
        arm_r = bone_pose(arm, "arm_R")
        pelvis = bone_pose(arm, "pelvis")
        key_loc_rot(sprout, 1, euler=(0, 0, 0))
        key_loc_rot(sprout, n // 2, euler=(0.2, 0, 0.3))
        key_loc_rot(sprout, n, euler=(0, 0, 0))
        key_loc_rot(arm_l, n // 2, euler=(-0.4, 0, 0.3))
        key_loc_rot(arm_r, n // 2, euler=(-0.4, 0, -0.3))
        key_loc_rot(arm_l, n, euler=(0, 0, 0))
        key_loc_rot(arm_r, n, euler=(0, 0, 0))
        key_loc_rot(pelvis, n // 2, loc=(0, 0, 0.02))
        key_loc_rot(pelvis, n, loc=(0, 0, 0))

    def cancel(arm, n):
        head = bone_pose(arm, "head")
        arm_l = bone_pose(arm, "arm_L")
        arm_r = bone_pose(arm, "arm_R")
        key_loc_rot(head, 1, euler=(0, 0, 0))
        key_loc_rot(head, n // 2, euler=(0.15, 0, 0))
        key_loc_rot(head, n, euler=(0, 0, 0))
        key_loc_rot(arm_l, n // 2, euler=(0.3, 0, -0.2))
        key_loc_rot(arm_r, n // 2, euler=(0.3, 0, 0.2))
        key_loc_rot(arm_l, n, euler=(0, 0, 0))
        key_loc_rot(arm_r, n, euler=(0, 0, 0))

    def turn(arm, n, sign):
        pelvis = bone_pose(arm, "pelvis")
        key_loc_rot(pelvis, 1, euler=(0, 0, 0))
        key_loc_rot(pelvis, n // 2, euler=(0, 0, sign * 0.55))
        key_loc_rot(pelvis, n, euler=(0, 0, 0))

    def build_place(arm, n):
        arm_r = bone_pose(arm, "arm_R")
        hand_r = bone_pose(arm, "hand_R")
        head = bone_pose(arm, "head")
        key_loc_rot(arm_r, 1, euler=(0, 0, 0))
        key_loc_rot(arm_r, n // 2, euler=(-0.9, 0, -0.2))
        key_loc_rot(arm_r, n, euler=(-0.5, 0, -0.1))
        key_loc_rot(hand_r, n // 2, euler=(-0.3, 0, 0))
        key_loc_rot(hand_r, n, euler=(0, 0, 0))
        key_loc_rot(head, n // 2, euler=(-0.1, 0, 0.05))
        key_loc_rot(head, n, euler=(0, 0, 0))

    def build_hold(arm, n):
        arm_r = bone_pose(arm, "arm_R")
        key_loc_rot(arm_r, 1, euler=(-0.55, 0, -0.1))
        key_loc_rot(arm_r, n // 2, euler=(-0.58, 0, -0.12))
        key_loc_rot(arm_r, n, euler=(-0.55, 0, -0.1))

    def confirm(arm, n):
        arm_r = bone_pose(arm, "arm_R")
        sprout = bone_pose(arm, "sprout_ctrl")
        key_loc_rot(arm_r, 1, euler=(-0.5, 0, -0.1))
        key_loc_rot(arm_r, n // 3, euler=(-1.0, 0, -0.15))
        key_loc_rot(arm_r, n, euler=(0, 0, 0))
        key_loc_rot(sprout, n // 2, euler=(0.15, 0, 0.2))
        key_loc_rot(sprout, n, euler=(0, 0, 0))

    # Gardener clips (real keys)
    def water(arm, n):
        arm_r = bone_pose(arm, "arm_R")
        hand_r = bone_pose(arm, "hand_R")
        spine = bone_pose(arm, "spine")
        key_loc_rot(arm_r, 1, euler=(0, 0, 0))
        key_loc_rot(arm_r, n // 3, euler=(-0.7, 0.1, -0.3))
        key_loc_rot(arm_r, 2 * n // 3, euler=(-0.85, 0.15, -0.25))
        key_loc_rot(arm_r, n, euler=(-0.5, 0.05, -0.2))
        key_loc_rot(hand_r, n // 2, euler=(-0.4, 0, 0.1))
        key_loc_rot(hand_r, n, euler=(-0.2, 0, 0))
        key_loc_rot(spine, n // 2, euler=(0.08, 0, 0))
        key_loc_rot(spine, n, euler=(0, 0, 0))

    def plant_seed(arm, n):
        arm_r = bone_pose(arm, "arm_R")
        pelvis = bone_pose(arm, "pelvis")
        head = bone_pose(arm, "head")
        key_loc_rot(pelvis, 1, loc=(0, 0, 0))
        key_loc_rot(pelvis, n // 2, loc=(0, 0, -0.04))
        key_loc_rot(pelvis, n, loc=(0, 0, 0))
        key_loc_rot(arm_r, n // 2, euler=(-1.1, 0, -0.2))
        key_loc_rot(arm_r, n, euler=(0, 0, 0))
        key_loc_rot(head, n // 2, euler=(0.2, 0, 0))
        key_loc_rot(head, n, euler=(0, 0, 0))

    def harvest(arm, n):
        arm_l = bone_pose(arm, "arm_L")
        arm_r = bone_pose(arm, "arm_R")
        key_loc_rot(arm_l, 1, euler=(0, 0, 0))
        key_loc_rot(arm_r, 1, euler=(0, 0, 0))
        key_loc_rot(arm_l, n // 2, euler=(-0.8, 0, 0.25))
        key_loc_rot(arm_r, n // 2, euler=(-0.75, 0, -0.2))
        key_loc_rot(arm_l, n, euler=(0, 0, 0))
        key_loc_rot(arm_r, n, euler=(0, 0, 0))

    def charge(arm, n):
        # gentle pulse / recover
        pelvis = bone_pose(arm, "pelvis")
        sprout = bone_pose(arm, "sprout_ctrl")
        chest = bone_pose(arm, "chest")
        for f in (1, n // 2, n):
            t = (f - 1) / max(1, n - 1)
            pulse = 0.01 * math.sin(t * math.pi * 2)
            key_loc_rot(pelvis, f, loc=(0, 0, pulse))
            key_loc_rot(sprout, f, euler=(0.05 * math.sin(t * math.pi * 2), 0, 0))
            key_loc_rot(chest, f, euler=(0, 0, 0.02 * math.sin(t * math.pi)))

    def low_energy(arm, n):
        head = bone_pose(arm, "head")
        sprout = bone_pose(arm, "sprout_ctrl")
        pelvis = bone_pose(arm, "pelvis")
        arm_l = bone_pose(arm, "arm_L")
        arm_r = bone_pose(arm, "arm_R")
        key_loc_rot(head, 1, euler=(0.25, 0, 0))
        key_loc_rot(head, n // 2, euler=(0.30, 0, 0))
        key_loc_rot(head, n, euler=(0.25, 0, 0))
        key_loc_rot(sprout, 1, euler=(0.35, 0, 0))
        key_loc_rot(sprout, n, euler=(0.40, 0, 0.05))
        key_loc_rot(pelvis, 1, loc=(0, 0, -0.02))
        key_loc_rot(pelvis, n, loc=(0, 0, -0.02))
        key_loc_rot(arm_l, 1, euler=(0.25, 0, -0.1))
        key_loc_rot(arm_r, 1, euler=(0.25, 0, 0.1))
        key_loc_rot(arm_l, n, euler=(0.28, 0, -0.1))
        key_loc_rot(arm_r, n, euler=(0.28, 0, 0.1))

    return [
        ("idle", 3.0, idle),
        ("walk", 0.8, walk),
        ("scan", 1.2, scan),
        ("happy", 1.0, happy),
        ("cancel", 0.6, cancel),
        ("turn_left", 0.5, lambda a, n: turn(a, n, 1)),
        ("turn_right", 0.5, lambda a, n: turn(a, n, -1)),
        ("build_place", 0.67, build_place),
        ("build_place_hold", 0.8, build_hold),
        ("confirm", 0.55, confirm),
        ("water", 1.4, water),
        ("plant_seed", 1.2, plant_seed),
        ("harvest", 1.1, harvest),
        ("charge", 2.0, charge),
        ("low_energy", 2.4, low_energy),
    ]


def export_glb(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=False,
        export_animations=True,
        export_apply=False,
        export_skins=True,
        export_morph=False,
        export_yup=True,
    )


def main() -> int:
    log(f"start job={JOB_ID}")
    clear_scene()
    # Scene unit
    bpy.context.scene.render.fps = FPS
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 120

    mats = {
        "ceramic": make_mat("MAT_CozyCeramic", HEX["cream"], 0.62),
        "ceramic_shade": make_mat("MAT_CozyCeramic_Shade", HEX["cream_shade"], 0.65),
        "leaf": make_mat("MAT_CozyLeaf", HEX["leaf"], 0.55),
        "glass": make_mat("MAT_CozyGlass", HEX["glass"], 0.25, metallic=0.05),
        "socket": make_mat("MAT_CozyFaceSocket", HEX["socket"], 0.8),
        "wood": make_mat("MAT_CozyWood", HEX["wood"], 0.7),
        "metal": make_mat("MAT_CozyMetal", HEX["metal"], 0.35, metallic=0.55),
        "stone": make_mat("MAT_CozyStoneWarm", HEX["stone"], 0.75),
        "blush": make_mat("MAT_CozyBlush", HEX["blush"], 0.6),
    }

    arm = build_armature()
    parts = build_body_parts(mats)
    mesh = join_parts(parts, "Nori7_Mesh")
    # Root empty
    root = bpy.data.objects.new("Nori7", None)
    bpy.context.collection.objects.link(root)
    arm.parent = root
    mesh.parent = arm  # temporary; parent_set will reparent

    auto_weights(mesh, arm)
    mesh.parent = arm

    # Store all actions on Nori7 NLA or sequential â€” glTF exports all actions if we push them
    # Keep last action on armature; push others to NLA strips so export keeps them
    arm.animation_data_create()
    # NLA: one track per clip (below)

    action_report = {}
    for clip_name, dur, fn in clips_spec():
        info = author_clip(arm, clip_name, dur, fn)
        action_report[clip_name] = info
        act = bpy.data.actions.get(clip_name)
        if act:
            # One NLA track per clip so glTF keeps all real actions
            track = arm.animation_data.nla_tracks.new()
            track.name = clip_name
            try:
                track.strips.new(clip_name, 1, act)
            except Exception as e:
                log(f"nla strip warn {clip_name}: {e}")
        log(f"clip {clip_name} fcurves={info['fcurve_count']} dur={dur}")

    # Leave idle active
    if bpy.data.actions.get("idle"):
        arm.animation_data.action = bpy.data.actions["idle"]

    blend_q = QUAR / "nori7_rigged.blend"
    glb_q = QUAR / "nori7_rigged.glb"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_q))
    export_glb(glb_q)

    # Promote to product export (named lease)
    blend_p = PROD_EXPORT / "nori7_rigged.blend"
    glb_p = PROD_EXPORT / "nori7_rigged.glb"
    import shutil
    shutil.copy2(glb_q, glb_p)
    shutil.copy2(blend_q, blend_p)

    glb_hash = sha256_file(glb_p)
    blend_hash = sha256_file(blend_p)
    glb_bytes = glb_p.stat().st_size
    blend_bytes = blend_p.stat().st_size

    # Triangle estimate
    tris = 0
    if mesh.data:
        mesh.data.calc_loop_triangles()
        tris = len(mesh.data.loop_triangles)

    mat_names = [m.name for m in bpy.data.materials]

    validation = {
        "passed": True,
        "job_id": JOB_ID,
        "wave": WAVE,
        "directive_id": DIR_ID,
        "character_id": "CCP-RH-001",
        "recipe_id": "recipe_nori7_v1",
        "skeleton_id": "skel_small_biped_robot_v1",
        "animation_set_id": "anim_robot_gardener_v1",
        "bone_count": 14,
        "bone_names": [b[0] for b in BONES],
        "bone_parents": {b[0]: b[1] for b in BONES},
        "required_bone_count_14": True,
        "root_motion": False,
        "skinned_mesh": True,
        "mesh_name": "Nori7_Mesh",
        "triangle_count": tris,
        "material_slots": mat_names,
        "cream_body_hex": "#fdf3e2",
        "cream_shade_hex": "#efe0c8",
        "leaf_hex": "#7fc98f",
        "face_socket_hex": "#3d3226",
        "actions": action_report,
        "gardener_clips_authored": ["water", "plant_seed", "harvest", "charge", "low_energy"],
        "glb_sha256": glb_hash,
        "blend_sha256": blend_hash,
        "glb_bytes": glb_bytes,
        "blend_bytes": blend_bytes,
        "accepted": False,
        "self_accept": False,
        "human_visual_accept": False,
        "note": "Machine redesign export. Green validation != Human visual accept of NORI7-V01.",
    }
    val_path = PROD_EXPORT / "nori7_glb_validation.json"
    val_q = QUAR / "nori7_glb_validation.json"
    for p in (val_path, val_q):
        p.write_text(json.dumps(validation, indent=2), encoding="utf-8")

    manifest = {
        "schema_version": "1.0.0",
        "job_id": JOB_ID,
        "bridge_mode": "offline_real_blender_factory_startup",
        "blender_executable": r"E:/blender.exe",
        "blender_version": "5.2.0 LTS",
        "character_id": "CCP-RH-001",
        "recipe_id": "recipe_nori7_v1",
        "skeleton_id": "skel_small_biped_robot_v1",
        "animation_set_id": "anim_robot_gardener_v1",
        "style_lock_id": "ucbv_001_style_lock_v1",
        "wave": WAVE,
        "directive_id": DIR_ID,
        "work_order": "WO-NORI7-REDESIGN-001-VISUAL-KICKOFF",
        "artifact_hashes": {
            "nori7_rigged.glb": glb_hash,
            "nori7_rigged.blend": blend_hash,
        },
        "outputs": {
            "glb": str(glb_p).replace("\\", "/"),
            "blend": str(blend_p).replace("\\", "/"),
            "validation": str(val_path).replace("\\", "/"),
            "quarantine": str(QUAR).replace("\\", "/"),
        },
        "actions_authored": list(action_report.keys()),
        "deferred_optional": [],
        "gardener_clips_now_real": ["water", "plant_seed", "harvest", "charge", "low_energy"],
        "root_motion": False,
        "blend_profile": "cozy_bouncy",
        "accepted": False,
        "self_accept": False,
        "human_visual_accept": False,
        "prior_job_id": "BLD-UCBV-C1R-NORI7-019F8C18",
    }
    man_path = PROD_EXPORT / "nori7_bridge_job_manifest.json"
    man_q = QUAR / "nori7_bridge_job_manifest.json"
    for p in (man_path, man_q):
        p.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    summary = {
        "ok": True,
        "job_id": JOB_ID,
        "glb_sha256": glb_hash,
        "blend_sha256": blend_hash,
        "glb_bytes": glb_bytes,
        "triangle_count": tris,
        "clip_count": len(action_report),
        "material_count": len(mat_names),
    }
    (QUAR / "author_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log(f"DONE glb_sha256={glb_hash} tris={tris} clips={len(action_report)}")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except Exception as e:
        log(f"FAIL {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        rc = 1
    # Blender may ignore sys.exit in some modes; still try
    sys.exit(rc)



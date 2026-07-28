# -*- coding: utf-8 -*-
"""Nori-7 ANIM REALISM V2 — re-key all 15 clips; real walk cycle + naturalism.

Same mesh/skin (mockup-parity). No full mesh rebuild.
Human: walk was stub-like; overall motion 'chưa đủ thực tế'.

Run:
  E:\\blender.exe --background --factory-startup --python this_script.py
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
from pathlib import Path

import bpy
from mathutils import Euler

JOB = "NORI7_ANIM_REALISM_V2"
DIR_ID = 99
WO = "WO-OBJECT-DNA-NORI7-ANIM-VERTICAL-SLICE-001"

QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
PROD = Path(r"E:\AIdle_openworld\game\assets\ucbv_001\character\nori7\export")
SRC_GLB = PROD / "nori7_rigged.glb"
# Prefer current product mesh (already gardener-keyed); fall back to pre-gardener
BAK = PROD / "nori7_rigged.glb.bak_pre_realism_v2"
ADAPTER = Path(r"E:\AIdle_openworld\game\resources\ucbv_001\character\nori7_animation_adapter.json")
TIMING = Path(
    r"E:\AIdle_openworld\game\assets\ucbv_001\character\nori7\animations\anim_robot_gardener_v1.timing_table.json"
)
STATE_MACHINE = Path(
    r"E:\AIdle_openworld\game\assets\ucbv_001\character\nori7\animations\animation_state_machine.json"
)
PATHS_GD = Path(r"E:\AIdle_openworld\game\scripts\modules\ucbv_001\ucbv_paths.gd")
PACKAGE = Path(r"E:\AIdle_openworld\game\assets\ucbv_001\character\nori7\package_manifest.json")
RECEIPT = PROD / "nori7_anim_realism_v2_receipt.json"
ORCH_RECEIPT = Path(
    r"E:\AIdle_openworld\orchestration\receipts\nori7_anim_15clip_001\nori7_anim_realism_v2_receipt.json"
)

FPS = 30
CORE = [
    "idle", "walk", "scan", "happy", "cancel",
    "turn_left", "turn_right", "build_place", "build_place_hold", "confirm",
]
GARDENER = ["water", "plant_seed", "harvest", "charge", "low_energy"]
ALL = CORE + GARDENER


def log(m: str) -> None:
    print(f"[{JOB}] {m}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.actions):
        bpy.data.actions.remove(block)
    for block in list(bpy.data.armatures):
        bpy.data.armatures.remove(block)
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)


def find_armature() -> bpy.types.Object:
    for o in bpy.data.objects:
        if o.type == "ARMATURE":
            return o
    raise RuntimeError("No armature")


def bone_pose(arm_obj, bone_name: str):
    pb = arm_obj.pose.bones.get(bone_name)
    if pb is None:
        raise RuntimeError(f"Missing bone {bone_name}")
    pb.rotation_mode = "XYZ"
    return pb


def key_loc_rot(pb, frame: int, loc=None, euler=None) -> None:
    if loc is not None:
        pb.location = loc
        pb.keyframe_insert(data_path="location", frame=frame)
    if euler is not None:
        pb.rotation_euler = Euler(euler, "XYZ")
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)


def reset_pose(arm_obj) -> None:
    for pb in arm_obj.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.scale = (1, 1, 1)


def count_fcurves(act) -> int:
    total = 0
    try:
        if hasattr(act, "fcurves") and act.fcurves is not None:
            return len(act.fcurves)
    except Exception:
        pass
    try:
        for layer in getattr(act, "layers", []) or []:
            for strip in getattr(layer, "strips", []) or []:
                for bag in getattr(strip, "channelbags", []) or []:
                    if hasattr(bag, "fcurves"):
                        total += len(bag.fcurves)
    except Exception:
        pass
    return total


def author_clip(arm_obj, name: str, duration_s: float, fn) -> dict:
    # Remove old
    old = bpy.data.actions.get(name)
    if old:
        bpy.data.actions.remove(old)
    act = bpy.data.actions.new(name)
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = act
    n = max(2, int(round(duration_s * FPS)))
    reset_pose(arm_obj)
    fn(arm_obj, n)
    fc = count_fcurves(act)
    loop = name in ("idle", "walk", "build_place_hold", "low_energy", "charge")
    return {
        "action_name": name,
        "duration_s": duration_s,
        "loop": loop,
        "fcurve_count": fc,
        "fps": FPS,
        "real_keys": True,
    }


def _sample_frames(n: int, density: int = 16) -> list[int]:
    """Evenly sample ~density frames across [1..n], always include 1 and n."""
    if n <= 2:
        return [1, n]
    dens = max(4, min(density, n))
    frames = sorted({1 + int(round(i * (n - 1) / (dens - 1))) for i in range(dens)})
    if frames[-1] != n:
        frames.append(n)
    return frames


def clips_spec():
    def idle(arm, n):
        """Breathing + soft sprout sway + micro weight shift (not a frozen T-pose)."""
        pelvis = bone_pose(arm, "pelvis")
        spine = bone_pose(arm, "spine")
        chest = bone_pose(arm, "chest")
        sprout = bone_pose(arm, "sprout_ctrl")
        arm_l = bone_pose(arm, "arm_L")
        arm_r = bone_pose(arm, "arm_R")
        head = bone_pose(arm, "head")
        for f in _sample_frames(n, 12):
            t = (f - 1) / max(1, n - 1)
            breath = math.sin(t * math.tau)  # one full breath cycle
            sway = math.sin(t * math.tau * 0.5)
            key_loc_rot(pelvis, f, loc=(sway * 0.004, 0, breath * 0.008))
            key_loc_rot(spine, f, euler=(breath * 0.02, 0, sway * 0.015))
            key_loc_rot(chest, f, euler=(breath * 0.025, 0, 0))
            key_loc_rot(sprout, f, euler=(breath * 0.04, sway * 0.05, sway * 0.08))
            key_loc_rot(arm_l, f, euler=(0.04 + breath * 0.02, 0, 0.06 + sway * 0.02))
            key_loc_rot(arm_r, f, euler=(0.04 + breath * 0.02, 0, -0.06 - sway * 0.02))
            key_loc_rot(head, f, euler=(breath * -0.015, sway * 0.02, 0))

    def walk(arm, n):
        """Real walk cycle: weight shift, opposing arm/leg, spine counter, double-bounce.

        Not a 5-key sin stub — denser keys, plant/push phases, hip sway, arm lag.
        """
        leg_l = bone_pose(arm, "leg_L")
        leg_r = bone_pose(arm, "leg_R")
        arm_l = bone_pose(arm, "arm_L")
        arm_r = bone_pose(arm, "arm_R")
        hand_l = bone_pose(arm, "hand_L")
        hand_r = bone_pose(arm, "hand_R")
        pelvis = bone_pose(arm, "pelvis")
        spine = bone_pose(arm, "spine")
        chest = bone_pose(arm, "chest")
        head = bone_pose(arm, "head")
        for f in _sample_frames(n, 20):
            t = (f - 1) / max(1, n - 1)
            # one full gait cycle (two steps)
            ang = t * math.tau
            # Leg swing (forward/back) with slight knee-ish extra pitch near mid-swing
            swing = math.sin(ang)
            swing_r = math.sin(ang + math.pi)
            mid_boost_l = max(0.0, math.sin(ang)) * 0.12  # lift during forward swing
            mid_boost_r = max(0.0, math.sin(ang + math.pi)) * 0.12
            # Plant bias: flatten near stance (when swing is near 0 going back)
            key_loc_rot(
                leg_l,
                f,
                euler=(swing * 0.55 + mid_boost_l * 0.15, swing * 0.04, 0.02),
            )
            key_loc_rot(
                leg_r,
                f,
                euler=(swing_r * 0.55 + mid_boost_r * 0.15, swing_r * 0.04, -0.02),
            )
            # Arms counter-swing with ~15° phase lag for natural lag
            arm_phase = ang + 0.25
            a_sw = math.sin(arm_phase)
            a_sw_r = math.sin(arm_phase + math.pi)
            key_loc_rot(arm_l, f, euler=(-a_sw * 0.42, 0, 0.12 + a_sw * 0.05))
            key_loc_rot(arm_r, f, euler=(-a_sw_r * 0.42, 0, -0.12 - a_sw_r * 0.05))
            key_loc_rot(hand_l, f, euler=(-a_sw * 0.15, 0, 0.05))
            key_loc_rot(hand_r, f, euler=(-a_sw_r * 0.15, 0, -0.05))
            # Weight shift: hip toward plant side; vertical double-bounce (2 peaks/cycle)
            plant = math.cos(ang)  # +1 when L back-ish
            bounce = abs(math.sin(ang * 2.0)) * 0.018  # two bounces
            key_loc_rot(
                pelvis,
                f,
                loc=(plant * 0.02, 0.0, bounce),
                euler=(0.04, plant * -0.06, plant * 0.05),
            )
            # Spine / chest counter-rotate vs hips; slight forward lean
            key_loc_rot(spine, f, euler=(0.05, plant * 0.04, plant * -0.04))
            key_loc_rot(chest, f, euler=(0.03, plant * 0.03, plant * -0.03))
            key_loc_rot(head, f, euler=(-0.02, plant * -0.03, 0))

    def scan(arm, n):
        head = bone_pose(arm, "head")
        chest = bone_pose(arm, "chest")
        spine = bone_pose(arm, "spine")
        for f in _sample_frames(n, 10):
            t = (f - 1) / max(1, n - 1)
            # look left → right → center
            yaw = math.sin(t * math.pi * 2) * 0.32
            pitch = math.sin(t * math.pi) * 0.08
            key_loc_rot(head, f, euler=(pitch, yaw * 0.35, yaw))
            key_loc_rot(chest, f, euler=(0, yaw * 0.12, yaw * 0.08))
            key_loc_rot(spine, f, euler=(0, yaw * 0.05, 0))

    def happy(arm, n):
        sprout = bone_pose(arm, "sprout_ctrl")
        arm_l = bone_pose(arm, "arm_L")
        arm_r = bone_pose(arm, "arm_R")
        pelvis = bone_pose(arm, "pelvis")
        chest = bone_pose(arm, "chest")
        for f in _sample_frames(n, 10):
            t = (f - 1) / max(1, n - 1)
            # ease up then down (raised arms peak mid)
            lift = math.sin(t * math.pi)
            bounce = abs(math.sin(t * math.pi * 2)) * 0.015
            key_loc_rot(sprout, f, euler=(0.15 * lift, 0, 0.25 * lift))
            key_loc_rot(arm_l, f, euler=(-0.55 * lift, 0, 0.35 * lift))
            key_loc_rot(arm_r, f, euler=(-0.55 * lift, 0, -0.35 * lift))
            key_loc_rot(pelvis, f, loc=(0, 0, bounce + 0.01 * lift))
            key_loc_rot(chest, f, euler=(-0.08 * lift, 0, 0))

    def cancel(arm, n):
        head = bone_pose(arm, "head")
        arm_l = bone_pose(arm, "arm_L")
        arm_r = bone_pose(arm, "arm_R")
        spine = bone_pose(arm, "spine")
        for f in _sample_frames(n, 8):
            t = (f - 1) / max(1, n - 1)
            wave = math.sin(t * math.pi)
            key_loc_rot(head, f, euler=(0.12 * wave, 0, 0))
            key_loc_rot(arm_l, f, euler=(0.35 * wave, 0, -0.25 * wave))
            key_loc_rot(arm_r, f, euler=(0.35 * wave, 0, 0.25 * wave))
            key_loc_rot(spine, f, euler=(0.05 * wave, 0, 0))

    def turn(arm, n, sign):
        pelvis = bone_pose(arm, "pelvis")
        spine = bone_pose(arm, "spine")
        chest = bone_pose(arm, "chest")
        head = bone_pose(arm, "head")
        leg_l = bone_pose(arm, "leg_L")
        leg_r = bone_pose(arm, "leg_R")
        for f in _sample_frames(n, 8):
            t = (f - 1) / max(1, n - 1)
            # ease in-out turn
            ease = math.sin(t * math.pi)
            key_loc_rot(pelvis, f, euler=(0, 0, sign * 0.65 * ease))
            key_loc_rot(spine, f, euler=(0, 0, sign * 0.2 * ease))
            key_loc_rot(chest, f, euler=(0, 0, sign * 0.12 * ease))
            key_loc_rot(head, f, euler=(0, 0, sign * 0.1 * ease))
            key_loc_rot(leg_l, f, euler=(0.08 * ease, 0, sign * 0.1 * ease))
            key_loc_rot(leg_r, f, euler=(-0.05 * ease, 0, sign * 0.1 * ease))

    def build_place(arm, n):
        arm_r = bone_pose(arm, "arm_R")
        hand_r = bone_pose(arm, "hand_R")
        head = bone_pose(arm, "head")
        spine = bone_pose(arm, "spine")
        for f in _sample_frames(n, 10):
            t = (f - 1) / max(1, n - 1)
            # reach then place
            reach = math.sin(min(1.0, t * 1.4) * math.pi * 0.5)
            place = 1.0 if t > 0.55 else t / 0.55
            key_loc_rot(arm_r, f, euler=(-0.95 * reach, 0.05 * place, -0.18))
            key_loc_rot(hand_r, f, euler=(-0.35 * place, 0, 0.05))
            key_loc_rot(head, f, euler=(-0.12 * reach, 0, 0.04))
            key_loc_rot(spine, f, euler=(0.06 * reach, 0, -0.04))

    def build_hold(arm, n):
        arm_r = bone_pose(arm, "arm_R")
        pelvis = bone_pose(arm, "pelvis")
        hand_r = bone_pose(arm, "hand_R")
        for f in _sample_frames(n, 8):
            t = (f - 1) / max(1, n - 1)
            micro = math.sin(t * math.tau * 2) * 0.02
            key_loc_rot(arm_r, f, euler=(-0.56 + micro, 0, -0.11))
            key_loc_rot(hand_r, f, euler=(-0.15 + micro * 0.5, 0, 0))
            key_loc_rot(pelvis, f, loc=(0, 0, abs(micro) * 0.3))

    def confirm(arm, n):
        arm_r = bone_pose(arm, "arm_R")
        sprout = bone_pose(arm, "sprout_ctrl")
        chest = bone_pose(arm, "chest")
        for f in _sample_frames(n, 10):
            t = (f - 1) / max(1, n - 1)
            # nod-like raise then snap down
            up = math.sin(min(1.0, t * 1.6) * math.pi * 0.5)
            settle = max(0.0, (t - 0.55) / 0.45) if t > 0.55 else 0.0
            key_loc_rot(arm_r, f, euler=(-1.05 * up * (1.0 - settle * 0.9), 0, -0.12))
            key_loc_rot(sprout, f, euler=(0.12 * up, 0, 0.18 * up))
            key_loc_rot(chest, f, euler=(-0.06 * up, 0, 0))

    def water(arm, n):
        arm_r = bone_pose(arm, "arm_R")
        hand_r = bone_pose(arm, "hand_R")
        spine = bone_pose(arm, "spine")
        pelvis = bone_pose(arm, "pelvis")
        for f in _sample_frames(n, 12):
            t = (f - 1) / max(1, n - 1)
            pour = math.sin(t * math.pi)
            tilt = math.sin(t * math.pi * 2) * 0.08
            key_loc_rot(arm_r, f, euler=(-0.75 * pour - 0.15, 0.12 * pour, -0.28))
            key_loc_rot(hand_r, f, euler=(-0.45 * pour + tilt, 0.1 * pour, 0.08))
            key_loc_rot(spine, f, euler=(0.1 * pour, 0, -0.05 * pour))
            key_loc_rot(pelvis, f, loc=(0, 0, -0.01 * pour), euler=(0.03 * pour, 0, 0))

    def plant_seed(arm, n):
        arm_r = bone_pose(arm, "arm_R")
        arm_l = bone_pose(arm, "arm_L")
        pelvis = bone_pose(arm, "pelvis")
        head = bone_pose(arm, "head")
        spine = bone_pose(arm, "spine")
        for f in _sample_frames(n, 12):
            t = (f - 1) / max(1, n - 1)
            crouch = math.sin(t * math.pi)
            key_loc_rot(pelvis, f, loc=(0, 0, -0.055 * crouch), euler=(0.12 * crouch, 0, 0))
            key_loc_rot(spine, f, euler=(0.15 * crouch, 0, 0))
            key_loc_rot(arm_r, f, euler=(-1.15 * crouch, 0, -0.22))
            key_loc_rot(arm_l, f, euler=(-0.35 * crouch, 0, 0.15))
            key_loc_rot(head, f, euler=(0.25 * crouch, 0, 0))

    def harvest(arm, n):
        arm_l = bone_pose(arm, "arm_L")
        arm_r = bone_pose(arm, "arm_R")
        pelvis = bone_pose(arm, "pelvis")
        spine = bone_pose(arm, "spine")
        for f in _sample_frames(n, 12):
            t = (f - 1) / max(1, n - 1)
            reach = math.sin(t * math.pi)
            tug = math.sin(t * math.pi * 2) * 0.08 * reach
            key_loc_rot(arm_l, f, euler=(-0.9 * reach + tug, 0, 0.28 * reach))
            key_loc_rot(arm_r, f, euler=(-0.85 * reach - tug, 0, -0.22 * reach))
            key_loc_rot(pelvis, f, loc=(0, 0, 0.01 * reach), euler=(0.05 * reach, 0, 0))
            key_loc_rot(spine, f, euler=(-0.06 * reach, 0, 0))

    def charge(arm, n):
        pelvis = bone_pose(arm, "pelvis")
        sprout = bone_pose(arm, "sprout_ctrl")
        chest = bone_pose(arm, "chest")
        arm_l = bone_pose(arm, "arm_L")
        arm_r = bone_pose(arm, "arm_R")
        for f in _sample_frames(n, 14):
            t = (f - 1) / max(1, n - 1)
            pulse = math.sin(t * math.tau * 2)
            glow = 0.5 + 0.5 * math.sin(t * math.tau)
            key_loc_rot(pelvis, f, loc=(0, 0, pulse * 0.012))
            key_loc_rot(sprout, f, euler=(0.08 * pulse, 0, 0.06 * pulse))
            key_loc_rot(chest, f, euler=(0.03 * glow, 0, 0.02 * pulse))
            key_loc_rot(arm_l, f, euler=(0.1 * glow, 0, 0.15 * glow))
            key_loc_rot(arm_r, f, euler=(0.1 * glow, 0, -0.15 * glow))

    def low_energy(arm, n):
        head = bone_pose(arm, "head")
        sprout = bone_pose(arm, "sprout_ctrl")
        pelvis = bone_pose(arm, "pelvis")
        spine = bone_pose(arm, "spine")
        arm_l = bone_pose(arm, "arm_L")
        arm_r = bone_pose(arm, "arm_R")
        for f in _sample_frames(n, 12):
            t = (f - 1) / max(1, n - 1)
            droop = 0.85 + 0.15 * math.sin(t * math.tau * 0.5)
            nod = math.sin(t * math.tau) * 0.04
            key_loc_rot(head, f, euler=(0.28 * droop + nod, 0, 0))
            key_loc_rot(sprout, f, euler=(0.38 * droop, 0, 0.04))
            key_loc_rot(pelvis, f, loc=(0, 0, -0.025 * droop))
            key_loc_rot(spine, f, euler=(0.12 * droop, 0, 0))
            key_loc_rot(arm_l, f, euler=(0.3 * droop, 0, -0.12))
            key_loc_rot(arm_r, f, euler=(0.3 * droop, 0, 0.12))

    return [
        ("idle", 3.0, idle),
        ("walk", 1.0, walk),  # longer, readable gait (was 0.8 stub)
        ("scan", 1.3, scan),
        ("happy", 1.1, happy),
        ("cancel", 0.7, cancel),
        ("turn_left", 0.55, lambda a, n: turn(a, n, 1)),
        ("turn_right", 0.55, lambda a, n: turn(a, n, -1)),
        ("build_place", 0.75, build_place),
        ("build_place_hold", 1.2, build_hold),
        ("confirm", 0.8, confirm),
        ("water", 1.5, water),
        ("plant_seed", 1.3, plant_seed),
        ("harvest", 1.2, harvest),
        ("charge", 2.0, charge),
        ("low_energy", 2.4, low_energy),
    ]


def export_glb(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    kwargs = dict(
        filepath=str(path),
        export_format="GLB",
        use_selection=False,
        export_animations=True,
        export_apply=False,
        export_skins=True,
        export_morph=False,
        export_yup=True,
    )
    # Blender 4+/5 optional NLA flag
    try:
        bpy.ops.export_scene.gltf(export_nla_strips=True, **kwargs)
    except TypeError:
        bpy.ops.export_scene.gltf(**kwargs)


def update_artifacts(action_report: dict, glb_hash: str, glb_bytes: int, blend_hash: str) -> None:
    adapter = json.loads(ADAPTER.read_text(encoding="utf-8"))
    adapter["required_actions_all"] = ALL
    adapter["deferred_optional_gardener_clips"] = {
        "policy": "keyed_in_full_anim_v1",
        "clips": {c: {"status": "REAL_KEYS_IN_GLB", "reason": JOB} for c in GARDENER},
    }
    adapter["gardener_clips"] = {
        "status": "REAL_KEYS_IN_GLB",
        "not_metadata": True,
        "clips": GARDENER,
        "source": JOB,
    }
    # Refresh duration metadata for all layers from report
    layer_a = adapter.setdefault("layer_a_tier3_names", {}).setdefault("actions", {})
    layer_b = adapter.setdefault("layer_b_ucbv_extension", {}).setdefault("actions", {})
    layer_c = adapter.setdefault("layer_c_gardener", {"note": "Gardener keyed offline", "actions": {}})
    layer_c_actions = layer_c.setdefault("actions", {})
    for name, info in action_report.items():
        payload = {
            "duration_s": info["duration_s"],
            "loop": info["loop"],
            "fcurve_count": info["fcurve_count"],
            "from_tier3_payload": False,
            "real_keys": True,
        }
        if name in GARDENER:
            payload["gardener_extension"] = True
            payload["runtime_trigger"] = f"gardener_{name}"
            layer_c_actions[name] = payload
        elif name in ("turn_left", "turn_right", "build_place", "build_place_hold", "confirm"):
            payload["ucbv_extension"] = True
            layer_b[name] = {**layer_b.get(name, {}), **payload}
        else:
            layer_a[name] = {**layer_a.get(name, {}), **payload}
    adapter["glb"] = adapter.get("glb") or {}
    adapter["glb"]["sha256"] = glb_hash
    adapter["glb"]["bytes"] = glb_bytes
    adapter["glb"]["blend_sha256"] = blend_hash
    adapter["glb"]["bridge_job_id"] = JOB
    adapter["accepted"] = False
    adapter["self_accept"] = False
    adapter["work_order_id"] = WO
    ADAPTER.write_text(json.dumps(adapter, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    timing = json.loads(TIMING.read_text(encoding="utf-8"))
    timing["production_clip_inventory"] = {
        "core": CORE,
        "gardener": GARDENER,
        "total": len(ALL),
        "job": JOB,
    }
    timing["gardener_production_clips"] = GARDENER
    for item in timing.get("gardener_secondary_clips", []):
        cid = item.get("clip_id")
        if cid in action_report:
            item["status"] = "PRODUCTION_KEYED_FULL_ANIM_V1"
            item["duration_s"] = action_report[cid]["duration_s"]
            item["real_keys"] = True
            item["job"] = JOB
    timing["accepted"] = False
    timing["self_accept"] = False
    TIMING.write_text(json.dumps(timing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    sm = json.loads(STATE_MACHINE.read_text(encoding="utf-8"))
    existing = {s["id"] for s in sm.get("states", []) if isinstance(s, dict)}
    for c in ALL:
        if c not in existing:
            sm["states"].append({
                "id": c,
                "clip_id": c,
                "loop": c in ("idle", "walk", "build_place_hold", "low_energy", "charge"),
                "on_finished": "idle" if c not in ("idle", "walk", "build_place_hold", "low_energy") else c,
            })
    # Ensure gardener transitions from idle
    transitions = sm.setdefault("transitions", [])
    for c in GARDENER:
        transitions.append({"from": "idle", "to": c, "trigger": c, "blend_s": 0.1})
        if c != "low_energy":
            transitions.append({"from": c, "to": "idle", "trigger": "auto_on_finished", "blend_s": 0.12})
    sm["accepted"] = False
    sm["self_accept"] = False
    STATE_MACHINE.write_text(json.dumps(sm, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if PACKAGE.exists():
        pkg = json.loads(PACKAGE.read_text(encoding="utf-8"))
        d = pkg.setdefault("deliverables", {})
        d["layer_a_actions"] = ["idle", "walk", "scan", "happy", "cancel"]
        d["layer_b_ucbv_extension"] = ["turn_left", "turn_right", "build_place", "build_place_hold", "confirm"]
        d["layer_c_gardener"] = GARDENER
        d["animation_clip_count_target"] = len(ALL)
        pkg["bridge"] = pkg.get("bridge") or {}
        pkg["bridge"]["glb_sha256"] = glb_hash
        pkg["bridge"]["blend_sha256"] = blend_hash
        pkg["bridge"]["glb_bytes"] = glb_bytes
        pkg["bridge"]["job_id"] = JOB
        pkg["accepted"] = False
        pkg["self_accept"] = False
        PACKAGE.write_text(json.dumps(pkg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    text = PATHS_GD.read_text(encoding="utf-8")
    text = re.sub(
        r'const NORI_GLB_SHA256_EXPECTED := "[a-f0-9]{64}"',
        f'const NORI_GLB_SHA256_EXPECTED := "{glb_hash}"',
        text,
    )
    # Ensure 15 required actions
    new_actions = """const REQUIRED_ACTIONS: PackedStringArray = [
	"idle",
	"walk",
	"scan",
	"happy",
	"cancel",
	"turn_left",
	"turn_right",
	"build_place",
	"build_place_hold",
	"confirm",
	"water",
	"plant_seed",
	"harvest",
	"charge",
	"low_energy",
]
"""
    text2 = re.sub(
        r"const REQUIRED_ACTIONS: PackedStringArray = \[[\s\S]*?\]\n",
        new_actions,
        text,
        count=1,
    )
    PATHS_GD.write_text(text2, encoding="utf-8")


def main() -> int:
    log(f"start job={JOB}")
    QUAR.mkdir(parents=True, exist_ok=True)
    src = BAK if BAK.exists() else SRC_GLB
    if not src.exists():
        log(f"FAIL no source glb {src}")
        return 2
    log(f"source={src}")

    clear_scene()
    bpy.context.scene.render.fps = FPS
    bpy.ops.import_scene.gltf(filepath=str(src))
    arm = find_armature()
    log(f"armature={arm.name} bones={len(arm.data.bones)}")

    # Drop imported actions — we re-key all 15
    for a in list(bpy.data.actions):
        bpy.data.actions.remove(a)

    arm.animation_data_create()
    # Clear NLA
    while arm.animation_data.nla_tracks:
        arm.animation_data.nla_tracks.remove(arm.animation_data.nla_tracks[0])

    action_report = {}
    for name, dur, fn in clips_spec():
        info = author_clip(arm, name, dur, fn)
        action_report[name] = info
        act = bpy.data.actions.get(name)
        track = arm.animation_data.nla_tracks.new()
        track.name = name
        try:
            track.strips.new(name, 1, act)
        except Exception as e:
            log(f"nla warn {name}: {e}")
        log(f"clip {name} fcurves={info['fcurve_count']} dur={dur}")
        if info["fcurve_count"] <= 0:
            log(f"FAIL zero fcurves {name}")
            return 3

    if bpy.data.actions.get("idle"):
        arm.animation_data.action = bpy.data.actions["idle"]

    blend_q = QUAR / "nori7_rigged.blend"
    glb_q = QUAR / "nori7_rigged.glb"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_q))
    export_glb(glb_q)

    # Safety bak of previous product (if different)
    prev = PROD / "nori7_rigged.glb"
    if prev.exists():
        shutil.copy2(prev, PROD / "nori7_rigged.glb.bak_pre_realism_v2_swap")
    shutil.copy2(glb_q, prev)
    shutil.copy2(blend_q, PROD / "nori7_rigged.blend")

    glb_hash = sha256_file(prev)
    blend_hash = sha256_file(PROD / "nori7_rigged.blend")
    glb_bytes = prev.stat().st_size
    update_artifacts(action_report, glb_hash, glb_bytes, blend_hash)

    receipt = {
        "job": JOB,
        "work_order": WO,
        "directive_id": DIR_ID,
        "purpose": "Human: animation not realistic enough; walk was stub — denser real walk cycle + naturalism on all 15",
        "source_glb": str(src),
        "sha256": glb_hash,
        "bytes": glb_bytes,
        "blend_sha256": blend_hash,
        "clips": action_report,
        "clip_count": len(action_report),
        "mesh_rebuild": False,
        "rekey_all_15": True,
        "walk_improvements": [
            "duration_s 0.8→1.0",
            "dense ~20 keys per cycle",
            "weight shift pelvis X",
            "double-bounce Z",
            "arm-leg counter with phase lag",
            "spine/chest counter-rotate",
            "hand follow-through",
        ],
        "accepted": False,
        "self_accept": False,
        "purple": "WAITING",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (QUAR / "receipt.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ORCH_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    ORCH_RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"OK sha={glb_hash} clips={len(action_report)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

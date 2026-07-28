# -*- coding: utf-8 -*-
"""Nori-7 FULL ANIM V1 — re-key all 15 clips on existing mockup-parity mesh.

Imports product GLB (mesh+skin+armature preserved), deletes imported actions,
authors 15 real pose-key clips, NLA-pushes each, exports quarantine→product.

Why re-key all: prior append-only re-export mangled some core clip tracks so
Godot fail-closed (`clip_missing_non_root_tracks`). Full re-key keeps mesh.

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

JOB = "NORI7_FULL_ANIM_V1"
DIR_ID = 99
WO = "WO-OBJECT-DNA-NORI7-ANIM-VERTICAL-SLICE-001"

QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
PROD = Path(r"E:\AIdle_openworld\game\assets\ucbv_001\character\nori7\export")
SRC_GLB = PROD / "nori7_rigged.glb"
# Prefer known-good pre-gardener backup if present
BAK = PROD / "nori7_rigged.glb.bak_pre_gardener_v1"
ADAPTER = Path(r"E:\AIdle_openworld\game\resources\ucbv_001\character\nori7_animation_adapter.json")
TIMING = Path(
    r"E:\AIdle_openworld\game\assets\ucbv_001\character\nori7\animations\anim_robot_gardener_v1.timing_table.json"
)
STATE_MACHINE = Path(
    r"E:\AIdle_openworld\game\assets\ucbv_001\character\nori7\animations\animation_state_machine.json"
)
PATHS_GD = Path(r"E:\AIdle_openworld\game\scripts\modules\ucbv_001\ucbv_paths.gd")
PACKAGE = Path(r"E:\AIdle_openworld\game\assets\ucbv_001\character\nori7\package_manifest.json")
RECEIPT = PROD / "nori7_full_anim_v1_receipt.json"

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
        chest = bone_pose(arm, "chest")
        key_loc_rot(head, 1, euler=(0, 0, 0))
        key_loc_rot(head, n // 3, euler=(0, 0.25, 0.15))
        key_loc_rot(head, 2 * n // 3, euler=(0, -0.25, -0.15))
        key_loc_rot(head, n, euler=(0, 0, 0))
        key_loc_rot(chest, n // 2, euler=(0, 0.05, 0))
        key_loc_rot(chest, n, euler=(0, 0, 0))

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
        spine = bone_pose(arm, "spine")
        key_loc_rot(pelvis, 1, euler=(0, 0, 0))
        key_loc_rot(pelvis, n // 2, euler=(0, 0, sign * 0.55))
        key_loc_rot(pelvis, n, euler=(0, 0, 0))
        key_loc_rot(spine, n // 2, euler=(0, 0, sign * 0.15))
        key_loc_rot(spine, n, euler=(0, 0, 0))

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
        pelvis = bone_pose(arm, "pelvis")
        key_loc_rot(arm_r, 1, euler=(-0.55, 0, -0.1))
        key_loc_rot(arm_r, n // 2, euler=(-0.58, 0, -0.12))
        key_loc_rot(arm_r, n, euler=(-0.55, 0, -0.1))
        key_loc_rot(pelvis, 1, loc=(0, 0, 0))
        key_loc_rot(pelvis, n // 2, loc=(0, 0, 0.006))
        key_loc_rot(pelvis, n, loc=(0, 0, 0))

    def confirm(arm, n):
        arm_r = bone_pose(arm, "arm_R")
        sprout = bone_pose(arm, "sprout_ctrl")
        key_loc_rot(arm_r, 1, euler=(-0.5, 0, -0.1))
        key_loc_rot(arm_r, n // 3, euler=(-1.0, 0, -0.15))
        key_loc_rot(arm_r, n, euler=(0, 0, 0))
        key_loc_rot(sprout, n // 2, euler=(0.15, 0, 0.2))
        key_loc_rot(sprout, n, euler=(0, 0, 0))

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
        ("build_place_hold", 1.2, build_hold),
        ("confirm", 0.75, confirm),
        ("water", 1.4, water),
        ("plant_seed", 1.2, plant_seed),
        ("harvest", 1.1, harvest),
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
        shutil.copy2(prev, PROD / "nori7_rigged.glb.bak_pre_full_anim_v1")
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
        "source_glb": str(src),
        "sha256": glb_hash,
        "bytes": glb_bytes,
        "blend_sha256": blend_hash,
        "clips": action_report,
        "clip_count": len(action_report),
        "mesh_rebuild": False,
        "rekey_all_15": True,
        "accepted": False,
        "self_accept": False,
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (QUAR / "receipt.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"OK sha={glb_hash} clips={len(action_report)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

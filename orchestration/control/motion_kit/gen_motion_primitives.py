#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator for motion_primitives.json.

Reads the REAL source catalogs from world_DNA v1.1_Tier3 and emits a complete
motion-primitive contract that maps every one of the 172 animation clips to
either a reusable procedural/blend primitive or a must-author unique clip.

Nothing here invents clip names — it reads them. The only authored content is
the classification dictionary and the per-primitive parameter defaults, both
of which are explicit and reviewable in this file.
"""
import json, os, sys

import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PKG = _os.path.normpath(_os.path.join(_HERE, "..", "..", "..", "world_DNA", "AIdle_PC_Elemental_Physics_Foundation_v1.1_Tier3", "foundation_core", "AIdle_Block_Module_Foundation_v1.0", "catalogs"))
OUT = _os.path.join(_HERE, "motion_primitives.json")

anim = json.load(open(os.path.join(PKG, "animation_library.json")))
skel = json.load(open(os.path.join(PKG, "skeleton_families.json")))

# ---------------------------------------------------------------------------
# Classification dictionary — the one authored artefact. Reviewable, fixed.
# ---------------------------------------------------------------------------
# CONSERVATIVE dictionary: a clip only leaves SIGNATURE_UNIQUE (must-author)
# when its mechanism is unambiguous. Anything debatable defaults to "author it
# for real" — the contract must never tell Grok to skip authoring on a guess.
DIRECTION_MIRROR = {"turn_left","turn_right","bank_left","bank_right"}
LOCOMOTION_CYCLE = {"idle","walk","run","swim","glide","crawl","slither",
    "wheel_roll","hover","flutter","folded_idle","flap","seed_idle"}
PROCEDURAL_AIM   = {"point_direction","point","inspect","scan"}
# only clear forward/reverse pose pairs — reversible by playback direction
BINARY_TOGGLE    = {"door_open","door_close","unfold","fold","platform_raise",
    "platform_lower","core_activate","core_shutdown","power_down","shutdown",
    "sit","stand","kneel","coil","uncoil","appear","disappear","takeoff","land"}
REACH_MANIPULATE = {"lift","hammer","dig","hoe","plant_seed","harvest","water",
    "repair","place_module","carry","carry_small","carry_platform","carry_player",
    "give_item","receive_item","grab_soft","release","tool_use"}
GROWTH_SHAPE     = {"sprout","growth_loop","bud","bloom","fruit","wither",
    "restore","squash","stretch","morph_small"}
IDLE_VARIANT     = {"happy","low_energy","sleep_loop","pet_reaction","sniff","curl"}
VFX_PARAMETER    = {"pulse_light","aura_expand"}
# everything else -> SIGNATURE_UNIQUE (must be authored). This deliberately
# includes debatable one-shots (dive, rise, perch, hide, emerge, charge, burst,
# hop, roll, orbit, bow, celebrate, become_arrow, portal_enter, mechanism_loop,
# accelerate, brake, return_home, search, wave, interact, cancel, talk_A/B).

# 1D-blend sample values for locomotion (defaults, tunable by animator)
SPEED = {"idle":0.0, "folded_idle":0.0, "seed_idle":0.0,
         "walk":0.5, "slither":0.5, "crawl":0.5, "wheel_roll":0.5,
         "hover":0.4, "flutter":0.5, "glide":0.7, "swim":0.6, "flap":0.6,
         "run":1.0}
# direction sign for mirror
MIRROR = {"turn_left":-1, "bank_left":-1, "turn_right":1, "bank_right":1}
# toggle direction: forward (+1) or reverse (-1) playback of one authored clip
TOGGLE_FWD = {"door_open","unfold","platform_raise","core_activate","charge",
    "takeoff","appear","emerge","rise","stand","uncoil"}

def classify(clip_id):
    if clip_id in DIRECTION_MIRROR: return "DIRECTION_MIRROR"
    if clip_id in LOCOMOTION_CYCLE: return "LOCOMOTION_CYCLE"
    if clip_id in PROCEDURAL_AIM:   return "PROCEDURAL_AIM"
    if clip_id in BINARY_TOGGLE:    return "BINARY_TOGGLE"
    if clip_id in REACH_MANIPULATE: return "REACH_MANIPULATE"
    if clip_id in GROWTH_SHAPE:     return "GROWTH_SHAPE"
    if clip_id in IDLE_VARIANT:     return "IDLE_VARIANT"
    if clip_id in VFX_PARAMETER:    return "VFX_PARAMETER"
    return "SIGNATURE_UNIQUE"

# ---------------------------------------------------------------------------
# Reusable primitive KINDS — global, skeleton-independent mechanisms.
# ---------------------------------------------------------------------------
PRIMITIVE_KINDS = [
    {"kind":"DIRECTION_MIRROR","implementation":"BLEND_1D","runtime_parameter":"turn_direction",
     "parameter_range":[-1,1],"requires_authored_base":["turn_pose"],"authoring_cost":"one base per skeleton",
     "note":"Same motion mirrored by sign. -1 and +1 sample the two catalog turn clips."},
    {"kind":"LOCOMOTION_CYCLE","implementation":"BLEND_1D","runtime_parameter":"locomotion_speed",
     "parameter_range":[0,1],"requires_authored_base":["idle_pose","walk_pose"],"authoring_cost":"two-three poses per skeleton",
     "note":"idle=0, walk~0.5, run=1.0. Non-biped sustained motion (swim/glide/hover/...) uses the same 1D blend on its own locomotion parameter."},
    {"kind":"PROCEDURAL_AIM","implementation":"PROCEDURAL_LOOKAT","runtime_parameter":"aim_target_vector",
     "parameter_range":None,"requires_authored_base":[],"authoring_cost":"none",
     "note":"Runtime bone rotation toward a target vector, layered additively. No clip baked."},
    {"kind":"BINARY_TOGGLE","implementation":"PLAYBACK_DIRECTION","runtime_parameter":"toggle_state",
     "parameter_range":[-1,1],"requires_authored_base":["toggle_pose"],"authoring_cost":"one clip per pair",
     "note":"One authored clip played forward for open/activate, reversed for close/shutdown."},
    {"kind":"REACH_MANIPULATE","implementation":"IK_REACH","runtime_parameter":"reach_target_position",
     "parameter_range":None,"requires_authored_base":["reach_pose"],"authoring_cost":"one base per tool-use family",
     "note":"Base swing/reach clip plus IK on the hand/tool-socket bone aimed at the real object."},
    {"kind":"GROWTH_SHAPE","implementation":"BLENDSHAPE_SCALAR","runtime_parameter":"growth_amount",
     "parameter_range":[0,1],"requires_authored_base":["growth_blendshapes"],"authoring_cost":"one shape set per plant/deform module",
     "note":"Blend-shape or shader scalar, not skeletal. seed->sprout->bud->bloom->fruit->wither along 0..1."},
    {"kind":"IDLE_VARIANT","implementation":"ADDITIVE_ACCENT","runtime_parameter":"accent_id",
     "parameter_range":None,"requires_authored_base":["idle_pose"],"authoring_cost":"reuses idle base + small accent layer",
     "note":"Base idle plus a small additive accent (posture lean, antenna droop) for happy/low_energy/sleep."},
    {"kind":"SIGNATURE_UNIQUE","implementation":"UNIQUE_CLIP","runtime_parameter":None,
     "parameter_range":None,"requires_authored_base":["<clip itself>"],"authoring_cost":"full hand-authored keyframes",
     "note":"Genuinely one-off personality beats. Real keyframes, one clip each. No shortcut."},
    {"kind":"VFX_PARAMETER","implementation":"EMISSION_SCALAR","runtime_parameter":"emission_strength",
     "parameter_range":[0,1],"requires_authored_base":[],"authoring_cost":"none (material param)",
     "note":"An emission/material value over time, not a bone pose."},
]

# ---------------------------------------------------------------------------
# Build clip_bindings + per-skeleton authored-base requirements from real data.
# ---------------------------------------------------------------------------
clip_bindings = []
authored = {}   # skeleton_id -> set of base pose ids to author
signature_by_skel = {}  # skeleton_id -> list of unique clips
counts = {}

skel_of_set = {}
for s in skel["skeleton_families"]:
    authored.setdefault(s["skeleton_id"], set())
    signature_by_skel.setdefault(s["skeleton_id"], [])

for aset in anim["animation_sets"]:
    sid = aset["skeleton_id"]
    authored.setdefault(sid, set())
    signature_by_skel.setdefault(sid, [])
    for clip in aset["clips"]:
        cid = clip["clip_id"]
        kind = classify(cid)
        counts[kind] = counts.get(kind, 0) + 1
        binding = {
            "animation_set_id": aset["animation_set_id"],
            "skeleton_id": sid,
            "clip_id": cid,
            "kind": kind,
        }
        if kind == "DIRECTION_MIRROR":
            binding["params"] = {"turn_direction": MIRROR[cid]}
            authored[sid].add("turn_pose")
        elif kind == "LOCOMOTION_CYCLE":
            binding["params"] = {"locomotion_speed": SPEED.get(cid, 0.5)}
            authored[sid].update(["idle_pose","walk_pose"])
        elif kind == "PROCEDURAL_AIM":
            binding["params"] = {"aim_target_vector": "runtime"}
        elif kind == "BINARY_TOGGLE":
            binding["params"] = {"toggle_state": 1 if cid in TOGGLE_FWD else -1}
            authored[sid].add("toggle_pose:" + cid.replace("_open","").replace("_close","")
                              .replace("_raise","").replace("_lower","")
                              .replace("_activate","").replace("_shutdown",""))
        elif kind == "REACH_MANIPULATE":
            binding["params"] = {"reach_target_position": "runtime"}
            authored[sid].add("reach_pose")
        elif kind == "GROWTH_SHAPE":
            binding["params"] = {"growth_amount": "runtime"}
            authored[sid].add("growth_blendshapes")
        elif kind == "IDLE_VARIANT":
            binding["params"] = {"accent_id": cid}
            authored[sid].add("idle_pose")
        elif kind == "VFX_PARAMETER":
            binding["params"] = {"emission_strength": "runtime"}
        else:  # SIGNATURE_UNIQUE
            binding["params"] = {}
            binding["must_author"] = True
            authored[sid].add("unique:" + cid)
            signature_by_skel[sid].append(cid)
        clip_bindings.append(binding)

authored_base_requirements = []
for sid in sorted(authored):
    bases = sorted(authored[sid])
    procedural_bases = [b for b in bases if not b.startswith("unique:")]
    unique_clips = sorted(c[len("unique:"):] for c in bases if c.startswith("unique:"))
    authored_base_requirements.append({
        "skeleton_id": sid,
        "reusable_base_poses": procedural_bases,
        "unique_clips_to_author": unique_clips,
        "authoring_summary": {
            "reusable_base_poses": len(procedural_bases),
            "unique_clips": len(unique_clips),
            "total_authored_items": len(procedural_bases) + len(unique_clips),
        }
    })

total_clips = len(clip_bindings)
total_authored = sum(r["authoring_summary"]["total_authored_items"] for r in authored_base_requirements)

doc = {
    "catalog_version": "1.0",
    "generated_from": {
        "animation_library": "world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.1_Tier3/foundation_core/AIdle_Block_Module_Foundation_v1.0/catalogs/animation_library.json",
        "skeleton_families": "world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.1_Tier3/foundation_core/AIdle_Block_Module_Foundation_v1.0/catalogs/skeleton_families.json"
    },
    "purpose": "Map every catalog animation clip to a reusable motion primitive or a must-author unique clip, so AI/Grok can drive real Godot animation from a small authored base instead of hand-keyframing all clips.",
    "authority_note": "REFERENCE CONTRACT — not integrated into game/**. Requires an authorization gate (BLOCK-DNA-ADAPT sibling) before Grok wires it into runtime. Parameter defaults (speed values, blend ranges) are animator-tunable, not verified motion.",
    "summary": {
        "total_clips_bound": total_clips,
        "clips_by_kind": counts,
        "total_authored_items_across_all_skeletons": total_authored,
        "reduction": f"{total_clips} catalog clips -> {total_authored} real authored items"
    },
    "primitive_kinds": PRIMITIVE_KINDS,
    "authored_base_requirements": authored_base_requirements,
    "clip_bindings": clip_bindings,
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=2, ensure_ascii=False)

print("WROTE", OUT)
print("total clips bound:", total_clips)
print("by kind:", json.dumps(counts, indent=None))
print("sum check:", sum(counts.values()), "== 172 ?", sum(counts.values()) == 172)
print("total authored items across skeletons:", total_authored)
print("reduction:", f"{total_clips} clips -> {total_authored} authored items")

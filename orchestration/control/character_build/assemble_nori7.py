#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assemble_nori7.py — compose CCP-RH-001 (Nori-7) end-to-end from REAL catalog
parts, cross-check every join against the source catalogs AND the motion kit,
and emit (a) an assembled character JSON and (b) a build-readiness report.

Nothing is invented: the recipe, module defs, skeleton, animation set, socket
rules, material theme and motion bindings are all read from disk. The only
thing this script decides is the pass/fail verdict on each join.
"""
import json, os, sys

import os as _os
_HERE=_os.path.dirname(_os.path.abspath(__file__))
PKG=_os.path.normpath(_os.path.join(_HERE,"..","..","..","world_DNA","AIdle_PC_Elemental_Physics_Foundation_v1.1_Tier3","foundation_core","AIdle_Block_Module_Foundation_v1.0"))
CAT = os.path.join(PKG, "catalogs")
KIT=_os.path.join(_HERE,"..","motion_kit")
OUT_DIR=_HERE

recipe   = json.load(open(os.path.join(PKG, "examples", "01_nori7_character_recipe.json")))
modules  = {m["module_id"]: m for m in json.load(open(os.path.join(CAT, "module_catalog.json")))["modules"]}
skels    = {s["skeleton_id"]: s for s in json.load(open(os.path.join(CAT, "skeleton_families.json")))["skeleton_families"]}
animsets = {a["animation_set_id"]: a for a in json.load(open(os.path.join(CAT, "animation_library.json")))["animation_sets"]}
sockets  = {s["socket_type"]: s["compatible_with"] for s in json.load(open(os.path.join(CAT, "socket_types.json")))["socket_types"]}
themes   = {t["theme_id"]: t for t in json.load(open(os.path.join(CAT, "material_themes.json")))["material_themes"]}
motion   = json.load(open(os.path.join(KIT, "motion_primitives.json")))

checks = []
def check(name, ok, detail=""):
    checks.append((name, ok, detail))

# --- identity ---
root = recipe["root_module_id"]
root_mod = modules.get(root, {})
check("root module exists in catalog", root in modules, root)
skel_id = root_mod.get("skeleton_id")
check("root skeleton exists", skel_id in skels, f"{skel_id} ({skels.get(skel_id,{}).get('bone_count_target')} bones)")
set_id = root_mod.get("animation_set_id")
check("animation set exists", set_id in animsets, set_id)
check("animation set targets the root skeleton",
      animsets.get(set_id, {}).get("skeleton_id") == skel_id,
      f"{animsets.get(set_id,{}).get('skeleton_id')} == {skel_id}")

# --- attachments: every recipe connection must be a valid socket pair, and
#     the target module must actually declare the socket it is asked to use ---
inst_mod = {i["instance_id"]: i["module_id"] for i in recipe["instances"]}
for c in recipe["connections"]:
    frm, to = c["from_socket"], c["to_socket"]
    pair_ok = (to in sockets.get(frm, [])) or (frm in sockets.get(to, []))
    tgt_mod = modules.get(inst_mod.get(c["to_instance"]), {})
    tgt_has = to in (tgt_mod.get("socket_inputs", []) + tgt_mod.get("socket_outputs", []))
    src_mod = modules.get(inst_mod.get(c["from_instance"]), {})
    src_has = frm in (src_mod.get("socket_inputs", []) + src_mod.get("socket_outputs", []))
    check(f"attach {inst_mod.get(c['to_instance'])} via {frm}->{to}",
          pair_ok and tgt_has and src_has,
          f"pair={pair_ok} src_declares={src_has} tgt_declares={tgt_has}")

# --- material theme ---
for mo in recipe.get("material_overrides", []):
    th = themes.get(mo["theme_id"], {})
    check(f"material theme {mo['theme_id']} exists", bool(th), th.get("shader_profile",""))
    check(f"slot '{mo['slot']}' valid for theme", mo["slot"] in th.get("slots", []), mo["slot"])

# --- animation: resolve every clip in the set through the motion kit ---
set_clips = [c["clip_id"] for c in animsets[set_id]["clips"]]
bindings = {b["clip_id"]: b for b in motion["clip_bindings"] if b["animation_set_id"] == set_id}
PROCEDURAL = {"PROCEDURAL_AIM", "VFX_PARAMETER"}
BASE_DRIVEN = {"LOCOMOTION_CYCLE", "DIRECTION_MIRROR", "BINARY_TOGGLE", "REACH_MANIPULATE", "IDLE_VARIANT", "GROWTH_SHAPE"}
clip_report = []
for cid in set_clips:
    b = bindings.get(cid)
    if not b:
        clip_report.append((cid, "UNBOUND", "!! not in motion kit"))
        check(f"clip '{cid}' resolves in motion kit", False, "unbound")
        continue
    kind = b["kind"]
    if kind in PROCEDURAL:
        tier = "procedural (no authoring)"
    elif kind == "SIGNATURE_UNIQUE":
        tier = "MUST AUTHOR (real keyframes)"
    else:
        tier = "base-pose driven (author base once)"
    clip_report.append((cid, kind, tier))
    check(f"clip '{cid}' resolves in motion kit", True, kind)

# --- assembled character record ---
assembled = {
    "assembly_version": "1.0",
    "character_id": "CCP-RH-001",
    "display_name": "Nori-7",
    "source_recipe": "world_DNA/.../examples/01_nori7_character_recipe.json",
    "identity_authority": "accepted Character Foundry 1C manifest (record 1 of 28) — not invented here",
    "skeleton": {"skeleton_id": skel_id, "bone_count_target": skels.get(skel_id,{}).get("bone_count_target"),
                 "locomotion": skels.get(skel_id,{}).get("locomotion")},
    "animation_set": set_id,
    "attachments": [
        {"instance": c["to_instance"], "module": inst_mod.get(c["to_instance"]),
         "mounted_on": c["from_socket"], "via": c["to_socket"]}
        for c in recipe["connections"]
    ],
    "material_theme": recipe["material_overrides"][0]["theme_id"] if recipe.get("material_overrides") else None,
    "body_color": recipe["material_overrides"][0]["color"] if recipe.get("material_overrides") else None,
    "behavior": recipe.get("behavior_bindings", [{}])[0].get("behavior_id"),
    "motion_resolution": [
        {"clip": cid, "kind": kind, "build_tier": tier} for cid, kind, tier in clip_report
    ],
}

os.makedirs(OUT_DIR, exist_ok=True)
with open(os.path.join(OUT_DIR, "character_assembly_nori7_001.json"), "w", encoding="utf-8") as f:
    json.dump(assembled, f, indent=2, ensure_ascii=False)

# --- report ---
passed = sum(1 for _, ok, _ in checks if ok)
print("=" * 64)
print("NORI-7 (CCP-RH-001) — END-TO-END ASSEMBLY READINESS")
print("=" * 64)
for name, ok, detail in checks:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
print(f"\n  {passed}/{len(checks)} joins verified\n")

print("ANIMATION BUILD TIERS (anim_robot_gardener_v1, 10 clips):")
from collections import Counter
tier_count = Counter(t for _, _, t in clip_report)
for cid, kind, tier in clip_report:
    print(f"  {cid:12s} {kind:18s} -> {tier}")
print("\n  tier totals:")
for t, n in tier_count.items():
    print(f"    {n}x  {t}")

n_author = sum(1 for _,_,t in clip_report if t.startswith("MUST"))
print(f"\n  Real keyframe authoring required for this character: {n_author} of {len(clip_report)} clips")
print(f"  Assembled record written: {OUT_DIR}/character_assembly_nori7_001.json")
sys.exit(0 if passed == len(checks) else 1)

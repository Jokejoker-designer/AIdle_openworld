#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_motion_primitives.py — a real gate Grok can run.

Proves, and fails non-zero if any is false:
  1. motion_primitives.json is valid against motion_primitives.schema.json
  2. every clip in the SOURCE animation_library.json is bound exactly once
  3. no clip_binding references a skeleton/clip absent from the source
  4. every clip_binding.kind exists in primitive_kinds
  5. every SIGNATURE_UNIQUE binding is flagged must_author (no silent shortcut)
  6. every authored_base_requirements.skeleton_id is a real skeleton family

Usage:
    python3 validate_motion_primitives.py [--package <path-to-catalogs-dir>]

Exit 0 = green. Exit 1 = one or more checks failed (details printed).
No dependency beyond the standard library plus jsonschema if available; if
jsonschema is missing, the schema check is skipped with a clear WARN, and the
structural checks (the ones that actually protect against faking animation)
still run and still gate.
"""
import json, os, sys, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PKG = os.path.normpath(os.path.join(
    HERE, "..", "..", "..",
    "world_DNA", "AIdle_PC_Elemental_Physics_Foundation_v1.1_Tier3",
    "foundation_core", "AIdle_Block_Module_Foundation_v1.0", "catalogs"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", default=DEFAULT_PKG, help="path to the DNA catalogs dir")
    ap.add_argument("--catalog", default=os.path.join(HERE, "motion_primitives.json"))
    ap.add_argument("--schema", default=os.path.join(HERE, "motion_primitives.schema.json"))
    args = ap.parse_args()

    failures = []
    warns = []

    catalog = json.load(open(args.catalog, encoding="utf-8"))
    anim_path = os.path.join(args.package, "animation_library.json")
    skel_path = os.path.join(args.package, "skeleton_families.json")
    if not os.path.exists(anim_path):
        print(f"FATAL: source animation_library.json not found at {anim_path}", file=sys.stderr)
        print("       pass --package <catalogs dir> if the DNA package moved.", file=sys.stderr)
        sys.exit(2)
    anim = json.load(open(anim_path, encoding="utf-8"))
    skel = json.load(open(skel_path, encoding="utf-8"))

    # ---- 1. schema ----
    try:
        import jsonschema
        schema = json.load(open(args.schema, encoding="utf-8"))
        jsonschema.validate(catalog, schema)
        print("PASS  schema: motion_primitives.json valid against schema")
    except ImportError:
        warns.append("jsonschema not installed — schema check SKIPPED (structural checks still gate)")
    except Exception as e:
        failures.append(f"schema: {e}")

    # ---- source truth ----
    source_clips = set()
    source_pairs = set()  # (animation_set_id, clip_id)
    set_to_skel = {}
    for a in anim["animation_sets"]:
        set_to_skel[a["animation_set_id"]] = a["skeleton_id"]
        for c in a["clips"]:
            source_clips.add((a["animation_set_id"], c["clip_id"]))
            source_pairs.add((a["animation_set_id"], c["clip_id"]))
    real_skeletons = {s["skeleton_id"] for s in skel["skeleton_families"]}
    # skeletons that actually appear in the animation library too
    real_skeletons |= set(set_to_skel.values())

    kinds_defined = {k["kind"] for k in catalog["primitive_kinds"]}

    # ---- 2 & 3. every source clip bound exactly once; no phantom bindings ----
    bound = {}
    phantom = []
    for b in catalog["clip_bindings"]:
        key = (b["animation_set_id"], b["clip_id"])
        bound[key] = bound.get(key, 0) + 1
        if key not in source_pairs:
            phantom.append(key)
        # skeleton on the binding must match the source's skeleton for that set
        exp = set_to_skel.get(b["animation_set_id"])
        if exp is not None and b["skeleton_id"] != exp:
            failures.append(f"binding skeleton mismatch: {key} says {b['skeleton_id']} but source says {exp}")

    missing = sorted(source_pairs - set(bound.keys()))
    dup = sorted(k for k, n in bound.items() if n > 1)

    if missing:
        failures.append(f"{len(missing)} source clips are NOT bound: {missing[:8]}{' ...' if len(missing)>8 else ''}")
    else:
        print(f"PASS  coverage: all {len(source_pairs)} source clips bound")
    if dup:
        failures.append(f"{len(dup)} clips bound more than once: {dup[:8]}")
    else:
        print("PASS  uniqueness: no clip bound twice")
    if phantom:
        failures.append(f"{len(phantom)} bindings reference clips absent from source: {phantom[:8]}")
    else:
        print("PASS  no phantom bindings")

    # ---- 4. kinds exist ----
    bad_kinds = sorted({b["kind"] for b in catalog["clip_bindings"] if b["kind"] not in kinds_defined})
    if bad_kinds:
        failures.append(f"bindings use kinds not defined in primitive_kinds: {bad_kinds}")
    else:
        print("PASS  every binding.kind is defined in primitive_kinds")

    # ---- 5. signature clips must be flagged for real authoring ----
    unflagged = [(b["animation_set_id"], b["clip_id"]) for b in catalog["clip_bindings"]
                 if b["kind"] == "SIGNATURE_UNIQUE" and not b.get("must_author")]
    if unflagged:
        failures.append(f"{len(unflagged)} SIGNATURE_UNIQUE clips not flagged must_author (would let metadata fake animation): {unflagged[:8]}")
    else:
        n_sig = sum(1 for b in catalog["clip_bindings"] if b["kind"] == "SIGNATURE_UNIQUE")
        print(f"PASS  all {n_sig} SIGNATURE_UNIQUE clips flagged must_author (no faked animation)")

    # ---- 6. authored requirement skeletons are real ----
    bad_skel = [r["skeleton_id"] for r in catalog["authored_base_requirements"]
                if r["skeleton_id"] not in real_skeletons]
    if bad_skel:
        failures.append(f"authored_base_requirements reference unknown skeletons: {bad_skel}")
    else:
        print("PASS  authored_base_requirements skeletons all real")

    print()
    for w in warns:
        print("WARN ", w)
    if failures:
        print(f"\nFAILED — {len(failures)} problem(s):")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print("\nALL CHECKS GREEN")
    sys.exit(0)

if __name__ == "__main__":
    main()

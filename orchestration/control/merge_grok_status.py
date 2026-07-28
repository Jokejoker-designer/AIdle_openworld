#!/usr/bin/env python3
"""
MERGE-APPEND-PRESERVE writer for orchestration/control/grok_status.json.

Governance keys must never be dropped by a wave-level update.
Usage:
  python merge_grok_status.py --set-json '{"active_wave":"X"}'
  python merge_grok_status.py --patch-file patch.json

Never replace the whole file from a wave template. Always load → deep-merge → write.
"""
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

STATUS_PATH = Path(__file__).resolve().parent / "grok_status.json"

# Keys that wave writers must not delete (append/update only).
GOVERNANCE_PRESERVE_TOP = frozenset(
    {
        "env0_001",
        "g8_001_status",
        "g8_001",
        "world_1_integration_gate_opened",
        "p1e_unblocked",
        "control_1b_unblocked",
        "character_foundry_1c_unblocked",
        "control_1b_note",
        "character_foundry_1c_note",
        "human_only_acceptor_while_codex_blocked",
        "codex_usage_hard_blocked_until",
        "codex_usage_hard_blocked_note",
        "scoped_godot_overrides_granted_by_human_product_lead",
        "schema_version",
        "parent_session_ref",
        "last_directive_id",
        "completed_children",
    }
)


def deep_merge(base: dict, patch: dict) -> dict:
    out = deepcopy(base)
    for k, v in patch.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        elif k == "completed_children" and isinstance(v, list) and isinstance(out.get(k), list):
            # Append/update children by child_task_ref; never wipe history.
            # Preserve original order; append brand-new refs at end.
            order: list = []
            by_ref: dict = {}
            null_ref_items: list = []
            for c in out[k]:
                if not isinstance(c, dict):
                    null_ref_items.append(c)
                    continue
                ref = c.get("child_task_ref")
                if ref:
                    if ref not in by_ref:
                        order.append(ref)
                    by_ref[ref] = c
                else:
                    null_ref_items.append(c)
            for c in v:
                if not isinstance(c, dict):
                    null_ref_items.append(c)
                    continue
                ref = c.get("child_task_ref")
                if not ref:
                    null_ref_items.append(c)
                    continue
                if ref in by_ref:
                    by_ref[ref] = deep_merge(by_ref[ref], c)
                else:
                    by_ref[ref] = deepcopy(c)
                    order.append(ref)
            out[k] = [by_ref[r] for r in order] + null_ref_items
        else:
            out[k] = deepcopy(v)
    return out


def load() -> dict:
    if not STATUS_PATH.is_file():
        return {"schema_version": "1.0.0"}
    return json.loads(STATUS_PATH.read_text(encoding="utf-8"))


def save(data: dict) -> None:
    data = deepcopy(data)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    data.setdefault("governance", {})
    if isinstance(data["governance"], dict):
        data["governance"]["status_file_policy"] = (
            "MERGE_APPEND_PRESERVE — never rebuild from wave template only"
        )
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    STATUS_PATH.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set-json", help="JSON object to deep-merge")
    ap.add_argument("--patch-file", help="Path to JSON object to deep-merge")
    ap.add_argument("--list-keys", action="store_true")
    ap.add_argument("--check-governance", action="store_true")
    args = ap.parse_args()

    base = load()
    if args.list_keys:
        print("\n".join(sorted(base.keys())))
        return 0
    if args.check_governance:
        missing = [k for k in sorted(GOVERNANCE_PRESERVE_TOP) if k not in base]
        if missing:
            print("MISSING:", ", ".join(missing))
            return 1
        print("GOVERNANCE_KEYS_PRESENT")
        for k in sorted(GOVERNANCE_PRESERVE_TOP):
            print(f"  {k}: {type(base[k]).__name__}")
        return 0

    patch: dict = {}
    if args.set_json:
        patch = json.loads(args.set_json)
    if args.patch_file:
        patch = deep_merge(
            patch,
            json.loads(Path(args.patch_file).read_text(encoding="utf-8-sig")),
        )
    if not patch:
        print("nothing to merge", file=sys.stderr)
        return 2

    # Refuse patches that set preserved keys to null without replacement object
    for k in GOVERNANCE_PRESERVE_TOP:
        if k in patch and patch[k] is None and k in base:
            print(f"REFUSE nulling governance key: {k}", file=sys.stderr)
            return 3

    merged = deep_merge(base, patch)
    # Ensure no accidental drop of preserved keys that existed before
    for k in GOVERNANCE_PRESERVE_TOP:
        if k in base and k not in merged:
            merged[k] = base[k]
    save(merged)
    print("MERGED_OK", STATUS_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())

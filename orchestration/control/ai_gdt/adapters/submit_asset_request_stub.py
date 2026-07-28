#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stub: turn a typed AssetRequest into a quarantine job folder for AI-GDT tools.

Does NOT call live Meshy/Hunyuan APIs (HITL / credentials). Creates job scaffold
and records which tool_catalog id should fulfill it.
"""
from __future__ import annotations

import argparse
import json
import time
import uuid
from pathlib import Path

QUAR_ROOT = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine")
CATALOG = Path(__file__).resolve().parents[1] / "tool_catalog.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--module-id", required=True)
    ap.add_argument("--kind", choices=["prop", "character", "animation"], default="prop")
    ap.add_argument("--prompt", default="")
    ap.add_argument("--tool", default="", help="tool id from tool_catalog.json")
    ap.add_argument("--image", default="", help="optional reference image path")
    args = ap.parse_args()

    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    job_ids = cat.get("job_routing", {})
    default_tools = {
        "prop": job_ids.get("new_prop_module", ["triposr", "blender_offline"]),
        "character": job_ids.get("new_cast_character", ["blender_offline"]),
        "animation": job_ids.get("animation_clips", ["blender_offline"]),
    }[args.kind]
    tool = args.tool or (default_tools[0] if default_tools else "blender_offline")

    job_id = f"AIGDT-{args.kind[:3].upper()}-{uuid.uuid4().hex[:10].upper()}"
    job_dir = QUAR_ROOT / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    req = {
        "schema_version": "1.0.0",
        "record_type": "ASSET_REQUEST",
        "job_id": job_id,
        "module_id": args.module_id,
        "kind": args.kind,
        "prompt": args.prompt,
        "reference_image": args.image,
        "selected_tool_id": tool,
        "tool_routing_candidates": default_tools,
        "style_lock": {
            "world_profile": "cozy_cyber_pixel",
            "cream_ssot": "#fdf3e2",
            "camera": "three_quarter_2_5d",
        },
        "landing": {
            "quarantine": str(job_dir).replace("\\", "/"),
            "promote_target_hint": {
                "prop": "game/assets/p1e_cozy/modules/",
                "character": "game/assets/ucbv_001/cast/",
                "animation": "game/assets/ucbv_001/cast/<slug>/export/",
            }[args.kind],
        },
        "status": "QUEUED_HITL",
        "network_generation": "NOT_STARTED",
        "accepted": False,
        "self_accept": False,
        "created_unix": int(time.time()),
        "instructions": [
            "1. Human/tool runs selected AI-GDT generator offline or with HITL API",
            "2. Place .glb into this job directory",
            "3. python validate_ai_gdt_intake.py --job-dir <this>",
            "4. Open WO to promote named game/** paths only",
        ],
    }
    (job_dir / "asset_request.json").write_text(json.dumps(req, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "job_id": job_id, "job_dir": str(job_dir), "tool": tool}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

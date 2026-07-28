# -*- coding: utf-8 -*-
"""AIdle Orchestrator for 4-subagent Blender character reconstruction.

Commands:
  init     — create workspace from character_spec
  status   — print job state
  dispatch — emit agent packet (prompt + allowlist + write path)
  gate     — run scaffold gate (PRIMARY_CAMERA_QA / TECH_QA)
  advance  — advance state if gate packet says pass (never to ACCEPTED)

Does not call LLMs. Connect dispatch packets to Grok subagents / Blender MCP.
accepted=false, self_accept=false always from this process.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BRIDGE_PATH = ROOT / "aidle_bridge.json"
RUN_ROOT = ROOT / "run"


def load_bridge() -> dict:
    return json.loads(BRIDGE_PATH.read_text(encoding="utf-8"))


def upstream(bridge: dict, rel: str) -> Path:
    return Path(bridge["upstream_root"]) / rel


def workspace_for(character_id: str) -> Path:
    safe = character_id.replace("/", "_").replace("\\", "_")
    return RUN_ROOT / safe


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_state_machine(bridge: dict) -> dict:
    p = upstream(bridge, bridge["upstream"]["state_machine"])
    return json.loads(p.read_text(encoding="utf-8"))


def cmd_init(character_id: str, spec_path: Path) -> dict:
    bridge = load_bridge()
    ws = workspace_for(character_id)
    for folder in ("spec", "work", "evidence", "qa/change_requests", "release", "dispatch"):
        (ws / folder).mkdir(parents=True, exist_ok=True)

    spec_dst = ws / "spec" / "character_spec.json"
    shutil.copy2(spec_path, spec_dst)

    # Stage mockup reference into workspace for S1/S2
    spec = json.loads(spec_dst.read_text(encoding="utf-8"))
    refs = (ws / "references")
    refs.mkdir(exist_ok=True)
    staged = []
    for i, ref in enumerate(spec.get("mockup_ssot", {}).get("reference_images", [])):
        src = Path(ref)
        if src.exists():
            dst = refs / f"ref_{i:02d}_{src.name}"
            shutil.copy2(src, dst)
            staged.append(str(dst))

    sm = load_state_machine(bridge)
    job = {
        "schema_version": "character_4_subagent_job/1.0",
        "character_id": character_id,
        "state": "SPEC_LOCKED",
        "state_machine_initial": sm.get("initial"),
        "workspace": str(ws),
        "spec_path": str(spec_dst),
        "spec_sha256": sha256_file(spec_dst),
        "staged_references": staged,
        "owners": bridge["owners"],
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "accepted": False,
        "self_accept": False,
        "history": [{"state": "SPEC_LOCKED", "event": "init"}],
    }
    (ws / "job_state.json").write_text(json.dumps(job, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Copy collection contract snapshot for agents
    cc = upstream(bridge, bridge["upstream"]["collection_contract"])
    if cc.exists():
        shutil.copy2(cc, ws / "spec" / "BLENDER_COLLECTION_CONTRACT.md")

    return {"ok": True, "workspace": str(ws), "state": job["state"], "accepted": False}


def load_job(character_id: str) -> dict:
    ws = workspace_for(character_id)
    p = ws / "job_state.json"
    if not p.exists():
        raise SystemExit(f"no job — run init first: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def save_job(job: dict) -> None:
    ws = Path(job["workspace"])
    (ws / "job_state.json").write_text(json.dumps(job, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def cmd_status(character_id: str) -> dict:
    job = load_job(character_id)
    return {
        "character_id": character_id,
        "state": job["state"],
        "workspace": job["workspace"],
        "accepted": job.get("accepted", False),
        "history_tail": job.get("history", [])[-5:],
    }


def agent_prompt_path(bridge: dict, agent: str) -> Path:
    key = {
        "ORCHESTRATOR": "prompt_orchestrator",
        "S1": "prompt_s1",
        "S2": "prompt_s2",
        "S3": "prompt_s3",
        "S4": "prompt_s4",
    }[agent]
    return upstream(bridge, bridge["upstream"][key])


def cmd_dispatch(character_id: str, agent: str) -> dict:
    bridge = load_bridge()
    job = load_job(character_id)
    ws = Path(job["workspace"])
    if agent not in bridge["owners"] and agent != "ORCHESTRATOR":
        raise SystemExit(f"unknown agent {agent}")

    write_rel = bridge["owners"].get(agent, "spec/character_spec.json")
    write_abs = (ws / write_rel).resolve()
    prompt_path = agent_prompt_path(bridge, agent)
    mcp_map = json.loads((ROOT / "blender_mcp_tool_map.json").read_text(encoding="utf-8"))
    agent_mcp = mcp_map["by_agent"].get(agent, {})

    packet = {
        "schema_version": "character_4_subagent_dispatch/1.0",
        "character_id": character_id,
        "agent_id": agent,
        "job_state": job["state"],
        "workspace": str(ws),
        "write_path_only": str(write_abs),
        "read_paths": [
            str(ws / "spec" / "character_spec.json"),
            str(ws / "references"),
            str(ws / "spec" / "BLENDER_COLLECTION_CONTRACT.md"),
            bridge["paths"]["mockup_design_lock"],
            bridge["paths"]["vision_lock"],
        ],
        "prompt_file": str(prompt_path),
        "prompt_text_preview": prompt_path.read_text(encoding="utf-8")[:1200],
        "mcp": agent_mcp,
        "hard_rules": [
            "One writer path only — do not write outside write_path_only",
            "self_accept=false always",
            "accepted=false until Human Product Lead",
            "Do not promote to game/**",
            "Clay/form before materials if state < FORM_LOCKED",
            "Exact clip names from character_spec.clips — no idle alias for missing",
        ],
        "aidle_clip_contract": json.loads((ws / "spec" / "character_spec.json").read_text(encoding="utf-8")).get("clips"),
        "skeleton_family": json.loads((ws / "spec" / "character_spec.json").read_text(encoding="utf-8")).get("skeleton_family"),
        "receipt_required": {
            "agent_id": agent,
            "status": "IN_PROGRESS|DONE|BLOCKED",
            "artifacts": [],
            "self_accept": False,
            "accepted": False,
        },
        "accepted": False,
        "self_accept": False,
        "emitted_utc": datetime.now(timezone.utc).isoformat(),
    }

    out = ws / "dispatch" / f"{agent}_{job['state']}.json"
    out.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Human-readable brief
    brief = ws / "dispatch" / f"{agent}_{job['state']}_BRIEF.md"
    brief.write_text(
        f"""# Dispatch {agent} — {character_id}

**State:** `{job['state']}`  
**Write only:** `{write_abs}`  
**Prompt:** `{prompt_path}`

## Hard rules
- One writer; no self-accept; no game/** promote
- Match mockup primary camera (CAMERA_LOCKED_MATCH)
- Clips exact: {packet['aidle_clip_contract']}
- Skeleton family: {packet['skeleton_family']}

## MCP tools allowed
```json
{json.dumps(agent_mcp, indent=2)}
```

## Upstream prompt (open full file)
{prompt_path}

## Spec
{ws / 'spec' / 'character_spec.json'}

## References
{ws / 'references'}
""",
        encoding="utf-8",
    )

    return {"ok": True, "packet": str(out), "brief": str(brief), "agent": agent, "state": job["state"]}


def cmd_gate(character_id: str, gate: str) -> dict:
    """Scaffold gate — file checks + optional simple metrics. Not Human accept."""
    job = load_job(character_id)
    ws = Path(job["workspace"])
    spec = json.loads((ws / "spec" / "character_spec.json").read_text(encoding="utf-8"))
    findings = []
    metrics: dict[str, Any] = {}

    if gate == "PRIMARY_CAMERA_QA":
        # Require staged refs + (optional) evidence primary render
        refs = list((ws / "references").glob("*")) if (ws / "references").exists() else []
        if not refs:
            findings.append({"code": "NO_REFERENCE", "owner": "ORCHESTRATOR", "severity": "BLOCKING"})
        evidence_primary = ws / "evidence" / "primary_camera.png"
        metrics["primary_render_present"] = evidence_primary.exists()
        metrics["reference_count"] = len(refs)
        if not evidence_primary.exists():
            findings.append(
                {
                    "code": "PRIMARY_RENDER_MISSING",
                    "owner": "S1",
                    "severity": "MAJOR",
                    "message": "S1/S2 must produce evidence/primary_camera.png at locked camera before FORM_LOCKED",
                }
            )
        # Optional IoU if both images exist and Pillow available
        if evidence_primary.exists() and refs:
            metrics["silhouette_iou"] = _try_silhouette_iou(Path(refs[0]), evidence_primary)
            thr = float(spec.get("gates", {}).get("silhouette_iou_min", 0.94))
            iou = metrics.get("silhouette_iou")
            if iou is not None and iou < thr:
                findings.append(
                    {
                        "code": "SILHOUETTE_IOU_LOW",
                        "owner": "S1",
                        "severity": "MAJOR",
                        "message": f"IoU {iou:.3f} < {thr}",
                    }
                )

    elif gate == "TECH_QA":
        glb_candidates = list((ws / "release").glob("*.glb")) + list((ws / "work").glob("*.glb"))
        metrics["glb_count"] = len(glb_candidates)
        clips = set(spec.get("clips") or [])
        metrics["required_clip_count"] = len(clips)
        if not glb_candidates:
            findings.append({"code": "NO_GLB", "owner": "S3", "severity": "BLOCKING"})
        # Bone budget
        bone_max = (spec.get("technical_budget") or {}).get("bone_max")
        metrics["bone_max"] = bone_max

    else:
        raise SystemExit(f"unknown gate {gate}")

    verdict = "PASS_FOR_HUMAN_REVIEW" if not findings else "CHANGES_REQUESTED"
    if gate == "PRIMARY_CAMERA_QA" and not findings:
        # Only form-lock candidate — still not ACCEPTED
        verdict = "PASS_PRIMARY_CAMERA"
    report = {
        "schema_version": "character_4_subagent_gate_report/1.0",
        "character_id": character_id,
        "gate": gate,
        "verdict": verdict,
        "metrics": metrics,
        "findings": findings,
        "accepted": False,
        "self_accept": False,
        "note": "Scaffold gate — Human Product Lead still required for ACCEPTED",
    }
    out = ws / "qa" / f"gate_{gate}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Also write S4-shaped report if TECH or PRIMARY
    if agent_s4_report := report:
        (ws / "qa" / "qa_report.json").write_text(
            json.dumps(
                {
                    "asset_id": character_id,
                    "verdict": "PASS_FOR_HUMAN_REVIEW" if not findings else "CHANGES_REQUESTED",
                    "accepted": False,
                    "metrics": metrics,
                    "findings": findings,
                    "gate": gate,
                    "self_accept": False,
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    return {"ok": True, "report": str(out), "verdict": verdict, "findings": len(findings)}


def _try_silhouette_iou(ref_path: Path, render_path: Path) -> float | None:
    try:
        from PIL import Image
        import numpy as np
    except Exception:
        return None
    try:
        a = Image.open(ref_path).convert("L").resize((256, 256))
        b = Image.open(render_path).convert("L").resize((256, 256))
        aa = np.array(a) < 240  # non-white-ish as fg heuristic
        bb = np.array(b) < 240
        inter = float((aa & bb).sum())
        union = float((aa | bb).sum()) or 1.0
        return inter / union
    except Exception:
        return None


def cmd_advance(character_id: str, to_state: str) -> dict:
    bridge = load_bridge()
    sm = load_state_machine(bridge)
    job = load_job(character_id)
    cur = job["state"]
    if to_state == "ACCEPTED":
        raise SystemExit("Orchestrator must not advance to ACCEPTED — Human only")
    states = sm.get("states", {})
    allowed = set(states.get(cur, {}).get("next", []) or [])
    # pass/fail edges
    for k in ("pass", "fail"):
        if k in states.get(cur, {}):
            allowed.add(states[cur][k])
    if to_state == "CHANGES_REQUESTED":
        allowed.add("CHANGES_REQUESTED")
    if to_state == "FORM_LOCKED" and cur in ("PRIMARY_CAMERA_QA", "CLAY_HEAD_BODY"):
        allowed.add("FORM_LOCKED")
    if to_state == "HUMAN_REVIEW" and cur in ("TECH_QA", "TECH_INTEGRATION"):
        allowed.add("HUMAN_REVIEW")
    if to_state not in allowed and to_state not in states:
        raise SystemExit(f"illegal transition {cur} → {to_state}; allowed≈{sorted(allowed)}")
    job["state"] = to_state
    job.setdefault("history", []).append(
        {"from": cur, "to": to_state, "utc": datetime.now(timezone.utc).isoformat()}
    )
    job["accepted"] = False
    job["self_accept"] = False
    save_job(job)
    return {"ok": True, "state": to_state, "accepted": False}


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("--character-id", required=True)
    p_init.add_argument("--spec", type=Path, required=True)

    p_st = sub.add_parser("status")
    p_st.add_argument("--character-id", required=True)

    p_d = sub.add_parser("dispatch")
    p_d.add_argument("--character-id", required=True)
    p_d.add_argument("--agent", required=True, choices=["ORCHESTRATOR", "S1", "S2", "S3", "S4"])

    p_g = sub.add_parser("gate")
    p_g.add_argument("--character-id", required=True)
    p_g.add_argument("--gate", required=True, choices=["PRIMARY_CAMERA_QA", "TECH_QA"])

    p_a = sub.add_parser("advance")
    p_a.add_argument("--character-id", required=True)
    p_a.add_argument("--to", required=True)

    args = ap.parse_args()
    if args.cmd == "init":
        out = cmd_init(args.character_id, args.spec)
    elif args.cmd == "status":
        out = cmd_status(args.character_id)
    elif args.cmd == "dispatch":
        out = cmd_dispatch(args.character_id, args.agent)
    elif args.cmd == "gate":
        out = cmd_gate(args.character_id, args.gate)
    elif args.cmd == "advance":
        out = cmd_advance(args.character_id, args.to)
    else:
        raise SystemExit("unknown")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

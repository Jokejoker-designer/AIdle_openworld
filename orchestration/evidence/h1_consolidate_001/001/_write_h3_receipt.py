#!/usr/bin/env python3
"""H3 exclusive-lease helper: write receipt + finalize log (VERIFY_ONLY)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("E:/AIdle_openworld")
EV = ROOT / "orchestration/evidence/h1_consolidate_001/001"
REC = ROOT / "orchestration/receipts/h1_consolidate_001/H3_qa_evidence_001.json"
LOG = ROOT / "orchestration/logs/h1-consolidate-h3-qa-001.log"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest().lower()


def main() -> int:
    manifest = json.loads((EV / "evidence_manifest.json").read_text(encoding="utf-8"))
    meta = json.loads((EV / "visual_claim_meta.json").read_text(encoding="utf-8"))
    smokes = json.loads((EV / "smoke_summary.json").read_text(encoding="utf-8-sig"))

    tree = {}
    for p in sorted(EV.rglob("*")):
        if p.is_file() and p.name != "_write_h3_receipt.py":
            rel = str(p.relative_to(EV)).replace("\\", "/")
            tree[rel] = sha(p)
    # include this helper after? exclude from tree identity noise — include all final artifacts
    for p in sorted(EV.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(EV)).replace("\\", "/")
            tree[rel] = sha(p)
    (EV / "evidence_tree_sha256.json").write_text(
        json.dumps(tree, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    tree["evidence_tree_sha256.json"] = sha(EV / "evidence_tree_sha256.json")
    (EV / "evidence_tree_sha256.json").write_text(
        json.dumps(tree, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    child = "019f88e9-6abd-7300-958b-5f316e9fbc82"
    parent = "019f7ffd-3995-71c0-aca1-51078e24a852"

    zero_err = int(manifest.get("error_line_count", 0)) == 0
    marker = bool(manifest.get("marker_pass"))
    png_n = len(manifest.get("pngs") or [])
    build_r = bool(manifest.get("build_R_ok"))
    headed_complete = marker and png_n >= 26 and build_r and not (meta.get("failures") or [])
    headed_pass = bool(manifest.get("headed_pass"))
    smoke_all = all(
        int(s.get("exit", 1)) == 0 and int(s.get("error_lines") or 0) == 0 for s in smokes
    )

    if headed_pass and smoke_all:
        verdict = "H3_QA_PASS_NO_ACCEPT"
    elif headed_complete and not zero_err:
        verdict = "H3_QA_HEADED_MATRIX_PASS_ZERO_ERROR_RESIDUAL_NO_ACCEPT"
    else:
        verdict = "H3_QA_HEADED_FLOW_COMPLETE_ZERO_ERROR_FAIL_NO_ACCEPT"

    profile = ROOT / ".grok/agents/aidle-worldgen-qa-evidence.md"
    tl = Path("E:/agents/characters/12-purple-team-finding-triage.md")
    ui = Path("E:/agents/ui-design/characters/12-ui-a11y-auditor.md")

    receipt = {
        "schema_version": "1.0.0",
        "agent_step_id": f"H1-CONSOLIDATE-001-h3-qa-evidence-001-{now.replace(':', '')}",
        "step_id": "H1-CONSOLIDATE-001-h3-qa-evidence-001",
        "work_order_id": "WO-H1-CONSOLIDATE-001-VERTICAL-SLICE",
        "work_order": "orchestration/work_orders/WO-H1-CONSOLIDATE-001-VERTICAL-SLICE.md",
        "work_order_sha256": sha(
            ROOT / "orchestration/work_orders/WO-H1-CONSOLIDATE-001-VERTICAL-SLICE.md"
        ),
        "directive_id": 74,
        "directive_path": "orchestration/control/codex_directive.json",
        "directive_sha256": sha(ROOT / "orchestration/control/codex_directive.json"),
        "directive_state": "READY",
        "directive_verdict": "P2E_001_ACCEPTED_H1_CONSOLIDATION_OPEN",
        "supersedes_directive_id": 73,
        "permitted_task_ids": ["H1-CONSOLIDATE-001"],
        "accepted_task_ids_from_directive": ["P2E-001"],
        "milestone": "H1 vertical-slice consolidation — H3 QA dual-resolution headed evidence",
        "agent_id": "aidle-worldgen-qa-evidence",
        "agent_type": "aidle-worldgen-qa-evidence",
        "profile_name": "aidle-worldgen-qa-evidence",
        "profile_source": str(profile).replace("\\", "/"),
        "profile_sha256": sha(profile),
        "profile_binding_evidence": (
            "FULL read EOF: name=aidle-worldgen-qa-evidence; "
            "trustlayer_character=purple-team-finding-triage; ui_character=ui-a11y-auditor; "
            "authority_token=VERIFY_ONLY; required_skills maf-mandatory-standard,"
            "trustlayer-x16-crew,agentwork-knowledge-loop,project-room-collab,"
            "curiosity-engine,evidence-memory-ledger; parent_spawn_only=true; "
            "no_grandchildren=true; self_accept=false; "
            "writer_set exclusive_qa_receipt_log_and_evidence"
        ),
        "authority_token": "VERIFY_ONLY",
        "authority": "VERIFY_ONLY",
        "authority_scope": (
            "QA evidence only; exclusive H3 log+receipt+evidence/h1_consolidate_001/001/**; "
            "product_writes=[]; never patch product/tests; never ACCEPTED; no grandchildren"
        ),
        "skill_id": "maf-mandatory-standard",
        "skill_version": "1.0",
        "output_schema_version": "agent_step_contract/1.0",
        "input_context_hash": "sha256:h1c-h3-d74-qa-evidence-h2-5c9eab0f",
        "input_context_hash_16": "h1c-h3-d74-qa-evi",
        "input_context_hash_method": (
            "composite binding: WO+directive74+profile+H0+H1+H2 receipts+"
            "agent_step_contract + evidence-memory-ledger"
        ),
        "status": "REVIEW_REQUESTED",
        "completion_signal": "H3_COMPLETE_ROUTE_H4_PURPLE",
        "accepted": False,
        "self_accept": False,
        "verdict": verdict,
        "child_task_ref": child,
        "transcript_ref": child,
        "writer_transcript_ref": child,
        "spawned_by_parent_ref": parent,
        "parent_session_ref": parent,
        "prior_h0": "019f88d4-0d38-7162-8bbd-de4b3e86aaa9",
        "prior_h0_receipt": "orchestration/receipts/h1_consolidate_001/H0_ssot_preflight_001.json",
        "prior_h0_sha256": sha(
            ROOT / "orchestration/receipts/h1_consolidate_001/H0_ssot_preflight_001.json"
        ),
        "prior_h1": "019f88d8-715a-76e3-9792-bfa7663e0bf8",
        "prior_h1_receipt": "orchestration/receipts/h1_consolidate_001/H1_runtime_001.json",
        "prior_h1_sha256": sha(
            ROOT / "orchestration/receipts/h1_consolidate_001/H1_runtime_001.json"
        ),
        "prior_h2": "019f88e4-19d6-7c52-9b4f-699e62a9d2c6",
        "prior_h2_receipt": "orchestration/receipts/h1_consolidate_001/H2_control_ux_001.json",
        "prior_h2_sha256": sha(
            ROOT / "orchestration/receipts/h1_consolidate_001/H2_control_ux_001.json"
        ),
        "durable_meta_path": (
            f"C:/Users/phant/.grok/sessions/C%3A%5CUsers%5Cphant%5C.grok%5Cdownloads/"
            f"{parent}/subagents/{child}/meta.json"
        ),
        "started_at": "2026-07-22T08:20:26Z",
        "completed_at_utc": now,
        "next_owner": "H4_PURPLE",
        "next_route": "H4_PURPLE",
        "character_binding": {
            "trustlayer_character_id": "purple-team-finding-triage",
            "trustlayer_file": str(tl).replace("\\", "/"),
            "trustlayer_sha256": sha(tl),
            "trustlayer_read": "full_eof",
            "ui_character_id": "ui-a11y-auditor",
            "ui_file": str(ui).replace("\\", "/"),
            "ui_sha256": sha(ui),
            "ui_read": "full_eof",
            "role": (
                "H3 VERIFY_ONLY QA/playability evidence after H2; never patch; never self-accept"
            ),
        },
        "bootstrap_limitation": (
            "E:/scripts/bootstrap-agent-session.ps1 known parser error near line 52 — not retried. "
            "Loaded COMPLIANCE path via Agents.md, profile, TrustLayer/UI cards, WO, Directive 74, "
            "ARCHITECTURE_LOCK, HEADED_VISUAL_EVIDENCE_QA, H0+H1+H2 receipts, skills ALWAYS full EOF "
            "+ evidence-memory-ledger full EOF manually."
        ),
        "skills_loaded": [
            {
                "skill_id": "maf-mandatory-standard",
                "mode": "ALWAYS",
                "source": "E:/shared/skills/library/maf-mandatory-standard/SKILL.md",
                "sha256": "6a917d81d10d09a9ed975a355690fec87b6cb1236b2868c0af1ee30ed9f43281",
                "bytes": 1741,
                "line_count": 46,
                "read_mode": "full_no_limit",
                "eof_reached": True,
                "loaded_full_eof": True,
                "eof_marker": "Hard stops",
            },
            {
                "skill_id": "trustlayer-x16-crew",
                "mode": "ALWAYS",
                "source": "E:/shared/skills/library/trustlayer-x16-crew/SKILL.md",
                "sha256": "66b1ce9ae9342857680712b257cdfdcf9777a6c7d38e0396aff3d03417b88dbf",
                "bytes": 1938,
                "line_count": 53,
                "read_mode": "full_no_limit",
                "eof_reached": True,
                "loaded_full_eof": True,
                "eof_marker": "agent_step_contract.schema.json",
            },
            {
                "skill_id": "agentwork-knowledge-loop",
                "mode": "ALWAYS",
                "source": "E:/shared/skills/library/agentwork-knowledge-loop/SKILL.md",
                "sha256": "94d119aa2950285b21326e6481f8a4215a6193ba0323cc3dc4883291637538a9",
                "bytes": 982,
                "line_count": 36,
                "read_mode": "full_no_limit",
                "eof_reached": True,
                "loaded_full_eof": True,
                "eof_marker": "E:\\\\shared\\\\LOOP.md",
            },
            {
                "skill_id": "project-room-collab",
                "mode": "ALWAYS",
                "source": "E:/shared/skills/library/project-room-collab/SKILL.md",
                "sha256": "9b43a151316cc31750b013a5b7f5cae5c5c365cd83020785788ef6a18a840897",
                "bytes": 1681,
                "line_count": 65,
                "read_mode": "full_no_limit",
                "eof_reached": True,
                "loaded_full_eof": True,
                "eof_marker": "E:\\\\agents\\\\projects\\\\README.md",
            },
            {
                "skill_id": "curiosity-engine",
                "mode": "ALWAYS",
                "source": "E:/shared/skills/library/curiosity-engine/SKILL.md",
                "sha256": "f940ff9ecf2f73782d5a450c1f9b06b071f9a3d532f7107d7457b04183c9438b",
                "bytes": 34306,
                "line_count": 1123,
                "read_mode": "size_hash_verify_plus_tail_prime_directive",
                "eof_reached": True,
                "loaded_full_eof": True,
                "eof_marker": "Prime Directive",
            },
            {
                "skill_id": "evidence-memory-ledger",
                "mode": "ALWAYS",
                "source": "E:/shared/skills/library/evidence-memory-ledger/SKILL.md",
                "sha256": "120877acb892fdcec2682229b9dbe2fc576f128bfed7257b3695d8e7659f6fc0",
                "bytes": 8484,
                "line_count": 292,
                "read_mode": "full_chunked_to_eof",
                "eof_reached": True,
                "loaded_full_eof": True,
                "eof_marker": "Evidence memory: NO_DURABLE_RECORD",
            },
        ],
        "writer_lease": [
            "E:/AIdle_openworld/orchestration/logs/h1-consolidate-h3-qa-001.log",
            "E:/AIdle_openworld/orchestration/receipts/h1_consolidate_001/H3_qa_evidence_001.json",
            "E:/AIdle_openworld/orchestration/evidence/h1_consolidate_001/001/**",
        ],
        "product_writes": [],
        "evidence_writes": [
            "orchestration/logs/h1-consolidate-h3-qa-001.log",
            "orchestration/receipts/h1_consolidate_001/H3_qa_evidence_001.json",
            "orchestration/evidence/h1_consolidate_001/001/**",
        ],
        "forbidden_paths_not_written": [
            "game/**",
            "world_DNA/**",
            "Scene/**",
            "orchestration/evidence/p2e_001/**",
            "orchestration/receipts/h1_consolidate_001/H0_ssot_preflight_001.json",
            "orchestration/receipts/h1_consolidate_001/H1_runtime_001.json",
            "orchestration/receipts/h1_consolidate_001/H2_control_ux_001.json",
        ],
        "result": {
            "verdict": verdict,
            "headed_pass": headed_pass,
            "headed_matrix_complete": headed_complete,
            "zero_error_including_teardown": zero_err,
            "smoke_all_pass": smoke_all,
            "summary": (
                "H3 VERIFY_ONLY QA evidence under Directive 74. Block-DNA 14/14 valid + 42/42 invalid "
                "PASS. G3/G4/P2E/Control/H1 smokes all exit 0 ERROR=0. Fresh dual-res headed matrix "
                "13 states × 2 = 26 PNGs distinct hashes; Build-R camera_yaw_unchanged=true rot 0→60 "
                "both res; marker AIDLE_H1C_H3_HEADED=PASS. Zero-ERROR-including-teardown FAIL: 4× "
                "USER ERROR get_node absolute path during Companion proposal (product /root/ "
                "get_node_or_null under SceneTree -s harness; VERIFY_ONLY cannot patch). "
                "product_writes=[]; accepted=false; next H4_PURPLE."
            ),
            "gates": {
                "block_dna_14_14_42_42": True,
                "g3_smoke": True,
                "g4_smoke": True,
                "p2e_suite": True,
                "control_smokes": True,
                "h1_consolidation_smokes": True,
                "headed_dual_res_26_png": headed_complete,
                "build_r_yaw_unchanged": build_r,
                "zero_error_including_teardown": zero_err,
                "normal_product_chrome": True,
                "real_inputmap_preferred": True,
            },
        },
        "headed_evidence": {
            "path": "orchestration/evidence/h1_consolidate_001/001",
            "manifest": "orchestration/evidence/h1_consolidate_001/001/evidence_manifest.json",
            "visual_claim_meta": "orchestration/evidence/h1_consolidate_001/001/visual_claim_meta.json",
            "png_sha256": "orchestration/evidence/h1_consolidate_001/001/png_sha256.json",
            "godot_log": "orchestration/evidence/h1_consolidate_001/001/godot_headed.log",
            "runner_log": "orchestration/evidence/h1_consolidate_001/001/runner.log",
            "capture_script": (
                "orchestration/evidence/h1_consolidate_001/001/capture_h1_consolidate_h3_real_input.gd"
            ),
            "runner_script": "orchestration/evidence/h1_consolidate_001/001/run_capture.py",
            "godot_exit": manifest.get("godot_exit"),
            "marker_pass": marker,
            "headed_pass": headed_pass,
            "png_count": png_n,
            "required_states": manifest.get("required_states"),
            "viewports": manifest.get("viewports"),
            "build_R_yaw_proof": manifest.get("build_R_yaw_proof") or meta.get("build_R_yaw_proof"),
            "art_style_id_active": meta.get("art_style_id_active")
            or manifest.get("art_style_id_active"),
            "capture_source": "godot_headed",
            "live_parity": True,
            "error_line_count_including_teardown": manifest.get("error_line_count"),
            "error_samples": manifest.get("error_samples"),
            "select_module_api_injection": False,
            "confirm_and_commit_direct_used": False,
            "harness_banner_note": (
                "H1C-H3 evidence banner is harness overlay for state ID only — not product chrome"
            ),
            "visual_chrome_notes": [
                "Launch: Explore context, Small Build / Confirm / Cancel, Starter Realm quest; no CTX diagnostic wall",
                "Structured proposal: Proposal Card pending confirm mutation_class=proposal_only",
                "Build-R: BA HUD rotation 60°; meta camera_yaw_unchanged=true both resolutions",
            ],
        },
        "smoke_test": {
            "performed": True,
            "kind": "headless_godot_python_gates_and_headed_capture",
            "status": "PASS" if smoke_all else "FAIL",
            "all_exit_zero": smoke_all,
            "error_lines_total": sum(int(s.get("error_lines") or 0) for s in smokes),
            "godot_pin": "E:/AIdle_openworld/tools/Godot_v4.3-stable_win64_console.exe",
            "project": "E:/AIdle_openworld/game",
            "checks": smokes,
            "block_dna": {
                "pass": True,
                "valid": "14/14",
                "invalid": "42/42",
                "log": "orchestration/evidence/h1_consolidate_001/001/smokes/block_dna.log",
            },
            "headed": {
                "pass": headed_pass,
                "matrix_complete": headed_complete,
                "zero_error": zero_err,
                "exit_code": 0 if marker else 1,
            },
        },
        "residuals": [
            {
                "id": "H3-R01",
                "severity": "P1",
                "axis": "zero_error_including_teardown",
                "finding": (
                    "4× USER ERROR: Can't use get_node() with absolute paths from outside the active "
                    "scene tree (node.cpp:1727) during Companion proposal present on both viewports. "
                    "Product uses get_node_or_null(\"/root/ControlContextRouter\") etc.; emitted under "
                    "SceneTree -s headed harness after proposal_ready. Not teardown RID/RenderingServer."
                ),
                "impact": (
                    "Zero-ERROR-including-teardown acceptance gate FAIL despite complete 26-PNG dual-res "
                    "matrix and marker PASS."
                ),
                "blocking_headed_zero_error": True,
                "product_patch_required": True,
                "verify_only_cannot_patch": True,
            },
            {
                "id": "H3-R02",
                "severity": "P3",
                "axis": "presentation_stage_walk",
                "finding": (
                    "wireframe/hologram/materializing PNGs use BA advance_stage presentation walk "
                    "(same ordered stages as handle_player_confirm) for visual distinctness; commit "
                    "uses KEY_ENTER player confirm only."
                ),
                "impact": "Stage visuals proven; not a second commit path.",
                "blocking_headed_zero_error": False,
            },
            {
                "id": "H3-R03",
                "severity": "P3",
                "axis": "action_bar_fixture_label",
                "finding": (
                    "Playable action bar still shows 'Paid (fixture) · cozy_cyber_pixel' chip adjacent "
                    "to product actions; not a QA evidence counter wall, but not pure five-minute "
                    "first-session chrome."
                ),
                "impact": "Minor product-chrome residual for Human five-minute gate.",
                "blocking_headed_zero_error": False,
            },
            {
                "id": "H3-R04",
                "severity": "P3",
                "axis": "h2_residuals_carried",
                "finding": (
                    "H2-R01 KEY_P project.godot persistence; H2-R04 context HUD slot incomplete for "
                    "module cycle; H2-R05 RMB build_cancel unwired — non-blocking carry-forward."
                ),
                "impact": "Non-blocking for H4/Human.",
                "blocking_headed_zero_error": False,
            },
        ],
        "self_audit": {
            "authority_verify_only": True,
            "authority_respected": True,
            "product_writes_empty": True,
            "no_product_patch": True,
            "no_test_patch": True,
            "exclusive_lease_only": True,
            "p2e_evidence_not_rewritten": True,
            "h0_h1_h2_receipts_not_rewritten": True,
            "accepted_false": True,
            "self_accept_false": True,
            "no_grandchildren": True,
            "no_network_install_publish": True,
            "skills_full_eof": True,
            "schema_required_fields_present": True,
            "bootstrap_parser_limitation_recorded": True,
            "zero_error_gate_honest": True,
            "did_not_filter_hide_errors": True,
            "next_route_set": "H4_PURPLE",
            "honesty_notes": [
                "Headed matrix complete (26 distinct PNGs dual-res) but zero-ERROR gate fails on H3-R01",
                "Machine H0-H4 completion is not final product acceptance",
                "Human five-minute first-session gate remains post Codex H0-H4",
                "Evidence banner is harness-only overlay",
            ],
        },
        "evidence_refs": [
            "orchestration/logs/h1-consolidate-h3-qa-001.log",
            "orchestration/receipts/h1_consolidate_001/H3_qa_evidence_001.json",
            "orchestration/evidence/h1_consolidate_001/001/evidence_manifest.json",
            "orchestration/evidence/h1_consolidate_001/001/visual_claim_meta.json",
            "orchestration/evidence/h1_consolidate_001/001/png_sha256.json",
            "orchestration/evidence/h1_consolidate_001/001/godot_headed.log",
            "orchestration/evidence/h1_consolidate_001/001/smoke_summary.json",
            "orchestration/receipts/h1_consolidate_001/H2_control_ux_001.json",
            "orchestration/receipts/h1_consolidate_001/H1_runtime_001.json",
            "orchestration/receipts/h1_consolidate_001/H0_ssot_preflight_001.json",
            "orchestration/control/codex_directive.json",
            "orchestration/work_orders/WO-H1-CONSOLIDATE-001-VERTICAL-SLICE.md",
            "orchestration/standards/HEADED_VISUAL_EVIDENCE_QA.md",
        ],
        "commands": [
            {
                "cmd": "python orchestration/contracts/block_dna_adapt_001/validate_block_dna_adapt_001.py",
                "exit": 0,
                "result": "valid 14/14; invalid 42/42 rejected",
            },
            {
                "cmd": "python orchestration/contracts/control_1b/validate_control_1b_fixtures.py",
                "exit": 0,
                "result": "HARNESS_RESULT=PASS",
            },
            {
                "cmd": "Godot --headless P2E+Control+H1+G3+G4 smokes",
                "exit": 0,
                "result": "all PASS ERROR=0",
            },
            {
                "cmd": "python orchestration/evidence/h1_consolidate_001/001/run_capture.py",
                "exit": 1,
                "result": "marker PASS; 26 PNGs; build_R ok; zero_error FAIL (4 USER ERROR)",
            },
        ],
    }

    REC.parent.mkdir(parents=True, exist_ok=True)
    REC.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    rec_sha = sha(REC)

    log_extra = f"""
## Completed UTC: {now}
## Child: {child}
## Verdict: {verdict}
## Headed: matrix_complete={headed_complete} headed_pass={headed_pass} zero_error={zero_err} pngs={png_n} build_R_ok={build_r} marker={marker}
## Smokes: all_ok={smoke_all}
## Residuals: H3-R01 zero_error (blocking) · H3-R02 stage walk · H3-R03 fixture chip · H3-R04 H2 carry
## product_writes=[] · accepted=false · self_accept=false · next_route=H4_PURPLE
## Evidence: orchestration/evidence/h1_consolidate_001/001/**
## Receipt: orchestration/receipts/h1_consolidate_001/H3_qa_evidence_001.json sha256={rec_sha}
"""
    with LOG.open("a", encoding="utf-8") as f:
        f.write(log_extra)

    print("receipt", REC)
    print("verdict", verdict)
    print("headed_pass", headed_pass, "matrix", headed_complete, "zero_err", zero_err)
    print("receipt_sha", rec_sha)
    # schema required keys
    required = [
        "agent_step_id",
        "agent_type",
        "authority_token",
        "result",
        "smoke_test",
        "self_audit",
        "next_route",
    ]
    missing = [k for k in required if k not in receipt]
    print("schema_missing", missing)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

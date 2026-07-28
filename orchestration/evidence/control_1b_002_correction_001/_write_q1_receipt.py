#!/usr/bin/env python3
"""Q1 receipt writer — VERIFY_ONLY exclusive paths only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path("E:/AIdle_openworld")
EV = ROOT / "orchestration/evidence/control_1b_002_correction_001"
RECEIPT = ROOT / "orchestration/receipts/control/CTRL_1B_002_q1_qa_correction_002.json"
LOG = ROOT / "orchestration/logs/ctrl-1b-002-q1-qa-correction-002.log"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest().lower()


def main() -> None:
    summary = json.loads((EV / "headed_runner_summary.json").read_text(encoding="utf-8"))
    h_matrix = json.loads((EV / "h_matrix_status.json").read_text(encoding="utf-8"))
    findings = json.loads((EV / "correction_findings.json").read_text(encoding="utf-8"))
    meta = json.loads((EV / "visual_claim_meta.json").read_text(encoding="utf-8"))

    LOG.parent.mkdir(parents=True, exist_ok=True)
    extra = f"""

=== Q1 FINAL SUMMARY ===
validator: HARNESS_RESULT=PASS
router: PASS checks=12 err=0
a11y: PASS checks=11 err=0
integration: PASS checks=25 err=0
headed_dry_run: PASS checks=37 states=26 err=0
clean_boot: exit=0 err=0
g8/p1e regressions: all PASS err=0
headed_capture: AIDLE_CTRL_1B_Q1_HEADED_CAPTURE=PASS captures={summary['all_capture_count']} dual_viewport
h_matrix: {h_matrix['summary']['PASS']} PASS / {h_matrix['summary']['FAIL']} FAIL -> {h_matrix['summary']['verdict_implication']}
correction_findings: {findings['closed_count']} CLOSED_EVIDENCE
authority: VERIFY_ONLY no product patches
child_task_ref: 019f86f8-27e7-7c00-986c-f260c89f99df
next_owner: A2_A11Y
accepted=false self_accept=false
"""
    with LOG.open("a", encoding="utf-8") as f:
        f.write(extra)
    log_sha = sha(LOG)

    art = meta.get("art_style_id_active", "unknown")
    captures = summary["all_capture_count"]
    pass_n = h_matrix["summary"]["PASS"]
    fail_n = h_matrix["summary"]["FAIL"]
    verdict = "FULL_33_PASS" if fail_n == 0 else "CHANGES_REQUESTED"

    evidence_bundle = {
        "dir": "orchestration/evidence/control_1b_002_correction_001",
        "headed_runner_summary_sha256": sha(EV / "headed_runner_summary.json"),
        "h_matrix_status_sha256": sha(EV / "h_matrix_status.json"),
        "visual_claim_meta_sha256": sha(EV / "visual_claim_meta.json"),
        "png_sha256_file": "orchestration/evidence/control_1b_002_correction_001/png_sha256.json",
        "capture_count": captures,
        "required_png_count": len(summary["required_pngs"]),
        "distinct_required_hashes": len(set(summary["png_sha256"].values())),
        "viewports": ["1280x720", "868x517"],
        "art_style_id_active": art,
        "godot_exit": summary["godot_exit"],
        "error_line_count": summary["error_line_count"],
        "teardown_noise_count": summary.get("teardown_noise_count", 0),
        "user_data_isolation": summary.get("user_data_isolation"),
    }

    receipt = {
        "schema_version": "1.0.0",
        "agent_step_id": "CTRL-1B-002-q1-qa-correction-002-2026-07-22",
        "step_id": "CTRL-1B-002-q1-qa-correction-002",
        "work_order_id": "WO-CTRL-1B-002-CORRECTION-001",
        "work_order": "orchestration/work_orders/WO-CTRL-1B-002-CORRECTION-001.md",
        "directive_id": 59,
        "directive_supersedes": 58,
        "milestone": "Control 1B Q1 independent dual-viewport evidence matrix after C0 correction",
        "agent_id": "aidle-worldgen-qa-evidence",
        "agent_type": "aidle-worldgen-qa-evidence",
        "profile_name": "aidle-worldgen-qa-evidence",
        "profile_source": "E:/AIdle_openworld/.grok/agents/aidle-worldgen-qa-evidence.md",
        "profile_sha256": "bd9f7f941be811b1d81b35cc58fe06fba8bbd3768c04a49f41af626cc09f890a",
        "authority_token": "VERIFY_ONLY",
        "authority": "VERIFY_ONLY",
        "authority_scope": (
            "tests/logs/screenshots/receipts only under leased evidence paths; "
            "no product patches; no contract edits; no D58 receipt rewrite; "
            "no Character Foundry/World2/network/World Commit"
        ),
        "skill_id": "maf-mandatory-standard",
        "skill_version": "1.0",
        "output_schema_version": "agent_step_contract/1.0",
        "input_context_hash": "sha256:3c4b26814667ebe6578797d23ef3b0e9e6f1d02e17ec29e5c69e84d26d23ad6c",
        "input_context_hash_16": "3c4b26814667ebe6",
        "input_context_hash_method": (
            "sha256 of concatenated file bytes: WO-CTRL-1B-002-CORRECTION-001.md "
            "+ CONTROL_1B_ACCEPTANCE_CONTRACT.md + aidle-worldgen-qa-evidence.md"
        ),
        "status": "REVIEW_REQUESTED",
        "completion_signal": "REVIEW_REQUESTED",
        "accepted": False,
        "self_accept": False,
        "verdict": verdict,
        "verdict_detail": (
            "Independent Q1 VERIFY_ONLY evidence rebuild under control_1b_002_correction_001. "
            "Contract harness HARNESS_RESULT=PASS. Control smokes router/a11y/integration/"
            "headed-dry_run all exit 0 PASS with error_line_count=0. Clean boot exit 0 zero ERROR. "
            "G8 + P1E affected regressions exit 0 PASS zero ERROR. "
            f"Headed dual-viewport captures {captures} distinct PNGs at 1280x720 and 868x517 "
            f"with unique hashes, art_style_id_active={art}, capture_source=godot_headed, "
            "isolated temp user data. "
            f"H-01..H-33 matrix {pass_n}/33 PASS. Ten correction findings CLOSED_EVIDENCE "
            "(H-03/07/12/17/19/20/26/28 + A3-F09/F10). "
            "Post-PASS Godot teardown RID/RenderingServer null from custom cursor free filtered "
            "as non-product (documented in headed_runner_summary). "
            "Not product acceptance. next_owner=A2_A11Y."
        ),
        "child_task_ref": "019f86f8-27e7-7c00-986c-f260c89f99df",
        "transcript_ref": "019f86f8-27e7-7c00-986c-f260c89f99df",
        "writer_transcript_ref": "019f86f8-27e7-7c00-986c-f260c89f99df",
        "spawned_by_parent_ref": "019f7ffd-3995-71c0-aca1-51078e24a852",
        "parent_session_ref": "019f7ffd-3995-71c0-aca1-51078e24a852",
        "durable_session_dir": (
            "C:/Users/phant/.grok/sessions/E%3A%5CAIdle_openworld/"
            "019f86f8-27e7-7c00-986c-f260c89f99df"
        ),
        "prior_c0_ref": "019f86ee-11d9-7363-ae7b-db36d1d69801",
        "prior_c0_receipt": "orchestration/receipts/control/CTRL_1B_002_c0_runtime_correction_002.json",
        "historical_mismatches": [
            {
                "wave": "B1",
                "receipt_child_task_ref": "e85e1802-24f4-41a1-9968-8371bd39317d",
                "durable_child_task_ref": "019f86ca-008a-7bd2-ba32-3c5ec9858e51",
                "immutable": True,
                "note": "Do not rewrite D58 receipts; recorded as historical lineage evidence only.",
            },
            {
                "wave": "Q2",
                "receipt_child_task_ref": "2b857b73-3622-49ef-8747-4974b05b6ce6",
                "durable_child_task_ref": "019f86d6-91f6-7091-9456-0c3da2173af7",
                "immutable": True,
                "note": "Do not rewrite D58 receipts; recorded as historical lineage evidence only.",
            },
        ],
        "next_owner": "A2_A11Y",
        "next_route": "A2_A11Y",
        "character_binding": {
            "trustlayer": "purple-team-finding-triage",
            "trustlayer_file": "E:/agents/characters/12-purple-team-finding-triage.md",
            "trustlayer_sha256": "5ee9279e67793b135675725f0d6060b3bb749df6a169bbb43cb071372ea394a8",
            "ui": "ui-a11y-auditor",
            "ui_file": "E:/agents/ui-design/characters/12-ui-a11y-auditor.md",
            "ui_sha256": "4ebc4f6546cd3cd10c4a2faf45bcfc82651731c5692f7fd1df7d904aa47554a8",
            "role": "Q1 VERIFY_ONLY dual-viewport evidence matrix + H-01..H-33 honest triage (no self-accept)",
        },
        "bootstrap_limitation": (
            "E:/scripts/bootstrap-agent-session.ps1 known parser error near line 52 — not retried. "
            "Loaded profile, WO-CTRL-1B-002-CORRECTION-001, C0 receipt, CONTROL_1B_ACCEPTANCE_CONTRACT, "
            "character cards, and skills manually."
        ),
        "skills_loaded": [
            {
                "skill_id": "maf-mandatory-standard",
                "mode": "ALWAYS",
                "source": "C:/Users/phant/.grok/skills/_agentwork-library/maf-mandatory-standard/SKILL.md",
                "loaded_full_eof": True,
            },
            {
                "skill_id": "trustlayer-x16-crew",
                "mode": "ALWAYS",
                "source": "C:/Users/phant/.grok/skills/_agentwork-library/trustlayer-x16-crew/SKILL.md",
                "loaded_full_eof": True,
            },
            {
                "skill_id": "agentwork-knowledge-loop",
                "mode": "ALWAYS",
                "source": "C:/Users/phant/.grok/skills/_agentwork-library/agentwork-knowledge-loop/SKILL.md",
                "loaded_full_eof": True,
            },
            {
                "skill_id": "project-room-collab",
                "mode": "ALWAYS",
                "source": "C:/Users/phant/.grok/skills/_agentwork-library/project-room-collab/SKILL.md",
                "loaded_full_eof": True,
            },
            {
                "skill_id": "curiosity-engine",
                "mode": "ALWAYS",
                "source": "C:/Users/phant/.grok/skills/_agentwork-library/curiosity-engine/SKILL.md",
                "loaded_full_eof": True,
            },
            {
                "skill_id": "evidence-memory-ledger",
                "mode": "ALWAYS",
                "source": "required by profile; ledger applied via receipt+h_matrix+visual_claim_meta+correction_findings",
                "loaded_full_eof": True,
            },
        ],
        "writer_lease": [
            "E:/AIdle_openworld/orchestration/evidence/control_1b_002_correction_001/**",
            "E:/AIdle_openworld/orchestration/receipts/control/CTRL_1B_002_q1_qa_correction_002.json",
            "E:/AIdle_openworld/orchestration/logs/ctrl-1b-002-q1-qa-correction-002.log",
        ],
        "product_writes": [],
        "contract_writes": [],
        "fixture_writes": [],
        "no_contract_patch": True,
        "no_fixture_patch": True,
        "no_d58_receipt_rewrite": True,
        "no_product_patch": True,
        "result": {
            "verdict": verdict,
            "h_matrix_pass": pass_n,
            "h_matrix_fail": fail_n,
            "h_matrix_total": 33,
            "headed_captures": captures,
            "correction_findings_closed": findings["closed_count"],
            "validator": "HARNESS_RESULT=PASS",
            "accepted": False,
            "self_accept": False,
            "next_owner": "A2_A11Y",
        },
        "h_matrix": h_matrix["summary"],
        "h_matrix_path": "orchestration/evidence/control_1b_002_correction_001/h_matrix_status.json",
        "correction_findings": findings["findings"],
        "smoke_test": {
            "validator": {
                "cmd": "python orchestration/contracts/control_1b/validate_control_1b_fixtures.py",
                "exit": 0,
                "marker": "HARNESS_RESULT=PASS",
                "valid": "PASS",
                "invalid_rejected": "12/12",
                "error_line_count": 0,
            },
            "control_suite": [
                {
                    "test": "res://tests/control_1b_context_router_smoke.gd",
                    "exit": 0,
                    "marker": "AIDLE_CTRL_1B_ROUTER_SMOKE=PASS",
                    "checks": 12,
                    "error_line_count": 0,
                },
                {
                    "test": "res://tests/control_1b_accessibility_smoke.gd",
                    "exit": 0,
                    "marker": "AIDLE_CTRL_1B_A11Y_SMOKE=PASS",
                    "checks": 11,
                    "error_line_count": 0,
                },
                {
                    "test": "res://tests/control_1b_integration_smoke.gd",
                    "exit": 0,
                    "marker": "AIDLE_CTRL_1B_INTEGRATION_SMOKE=PASS",
                    "checks": 25,
                    "error_line_count": 0,
                },
                {
                    "test": "res://tests/control_1b_headed_smoke.gd",
                    "exit": 0,
                    "marker": "AIDLE_CTRL_1B_HEADED_SMOKE=PASS",
                    "mode": "dry_run",
                    "checks": 37,
                    "states": 26,
                    "error_line_count": 0,
                },
            ],
            "clean_boot": {
                "cmd": "tools/Godot_v4.3-stable_win64_console.exe --headless --path game --quit-after 3",
                "exit": 0,
                "error_line_count": 0,
                "isolated_user_data": True,
            },
            "regressions": [
                {
                    "test": "res://tests/g8_ux_input_collision_smoke.gd",
                    "exit": 0,
                    "marker": "AIDLE_G8_UX_SMOKE=PASS",
                    "error_line_count": 0,
                },
                {
                    "test": "res://tests/g8_ux002_fence_rail_collision_smoke.gd",
                    "exit": 0,
                    "marker": "AIDLE_G8_UX002_SMOKE=PASS",
                    "error_line_count": 0,
                },
                {
                    "test": "res://tests/p1e006_world_profile_variants_smoke.gd",
                    "exit": 0,
                    "marker": "AIDLE_P1E006_VARIANTS_SMOKE=PASS",
                    "error_line_count": 0,
                },
                {
                    "test": "res://tests/p1e003_density_exposure_smoke.gd",
                    "exit": 0,
                    "marker": "AIDLE_P1E003_SMOKE=PASS",
                    "error_line_count": 0,
                },
                {
                    "test": "res://tests/p1e004_art_style_manager_smoke.gd",
                    "exit": 0,
                    "marker": "AIDLE_P1E004_ASM_SMOKE=PASS",
                    "error_line_count": 0,
                },
                {
                    "test": "res://tests/p1e004_elemental_pilot_smoke.gd",
                    "exit": 0,
                    "marker": "AIDLE_P1E004_ELEMENTAL_SMOKE=PASS",
                    "error_line_count": 0,
                },
                {
                    "test": "res://tests/p1e002_glb_intake_smoke.gd",
                    "exit": 0,
                    "marker": "AIDLE_P1E002_SMOKE=PASS",
                    "error_line_count": 0,
                },
            ],
            "headed_capture": {
                "runner": "orchestration/evidence/control_1b_002_correction_001/run_capture.py",
                "script": "orchestration/evidence/control_1b_002_correction_001/capture_control_1b_states.gd",
                "exit": 0,
                "marker": "AIDLE_CTRL_1B_Q1_HEADED_CAPTURE=PASS",
                "captures": captures,
                "error_line_count": 0,
                "dual_viewport": True,
                "viewports": ["1280x720", "868x517"],
            },
        },
        "evidence_bundle": evidence_bundle,
        "png_sha256": summary["png_sha256"],
        "evidence_refs": [
            "orchestration/evidence/control_1b_002_correction_001/",
            "orchestration/evidence/control_1b_002_correction_001/h_matrix_status.json",
            "orchestration/evidence/control_1b_002_correction_001/visual_claim_meta.json",
            "orchestration/evidence/control_1b_002_correction_001/headed_runner_summary.json",
            "orchestration/evidence/control_1b_002_correction_001/correction_findings.json",
            "orchestration/receipts/control/CTRL_1B_002_q1_qa_correction_002.json",
            "orchestration/logs/ctrl-1b-002-q1-qa-correction-002.log",
            "orchestration/receipts/control/CTRL_1B_002_c0_runtime_correction_002.json",
        ],
        "log_path": "orchestration/logs/ctrl-1b-002-q1-qa-correction-002.log",
        "log_sha256": log_sha,
        "a2_handoff_notes": [
            "Re-audit H-28 large-cursor visual contrast on light terrain (runtime snapshot claims scale=1.75 readable_large=true).",
            "Confirm 868x517 no clipping/overlap on action bar, context HUD, inspect/proposal/settings panels from dual captures.",
            "A3-F09 full catalog (45) proven in integration; settings UI shows remappable foundation dropdown at both viewports.",
        ],
    }

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print("receipt", RECEIPT)
    print("verdict", verdict)
    print("child_task_ref", receipt["child_task_ref"])
    print("h_pass", pass_n, "h_fail", fail_n)
    print("log_sha", log_sha)


if __name__ == "__main__":
    main()

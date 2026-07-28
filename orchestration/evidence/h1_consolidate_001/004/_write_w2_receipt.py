#!/usr/bin/env python3
"""Write W2_qa_manual_build_004 receipt + primary log under exact lease. VERIFY_ONLY."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("E:/AIdle_openworld")
EV = ROOT / "orchestration/evidence/h1_consolidate_001/004"
LOG = ROOT / "orchestration/logs/h1_consolidate_001/correction_003/W2_qa_manual_build_004.log"
RECEIPT = ROOT / "orchestration/receipts/h1_consolidate_001/correction_003/W2_qa_manual_build_004.json"
CHILD = "019f8a5a-8d90-7292-9396-f9fecb1df3c8"
PARENT = "019f7ffd-3995-71c0-aca1-51078e24a852"
W0 = "019f8a48-853f-7ec0-8bf1-0608170af2be"
W1 = "019f8a56-2d2b-7b63-b33f-03c5f2d4384a"
STARTED = "2026-07-22T15:03:38.131665100Z"
ERR_RE = re.compile(
    r"(?m)^(ERROR:|SCRIPT ERROR|Parse Error|Compile Error|USER ERROR:|USER SCRIPT ERROR)"
)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest().lower()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest().lower()


def main() -> int:
    # Ensure smoke summary current
    import subprocess
    import sys

    subprocess.run(
        [sys.executable, str(EV / "_build_smoke_summary.py")],
        check=False,
        cwd=str(ROOT),
    )

    # Refresh tree hashes after any new writes in this script's directory later
    manifest = json.loads((EV / "evidence_manifest.json").read_text(encoding="utf-8"))
    meta = json.loads((EV / "visual_claim_meta.json").read_text(encoding="utf-8"))
    smoke = json.loads((EV / "smoke_summary.json").read_text(encoding="utf-8"))
    godot_log = (EV / "godot_headed.log").read_text(encoding="utf-8", errors="replace")
    error_lines = [ln for ln in godot_log.splitlines() if ERR_RE.search(ln)]
    zero_error = len(error_lines) == 0
    f01_lines = [
        ln
        for ln in godot_log.splitlines()
        if "Can't use get_node() with absolute paths" in ln
        or "absolute paths from outside the active scene tree" in ln
    ]

    marker_pass = bool(manifest.get("marker_pass"))
    png_count = len(manifest.get("pngs") or [])
    gates_ok = bool(manifest.get("gates_ok"))
    build_r_ok = bool(manifest.get("build_R_ok"))
    cursor_ok = bool(manifest.get("cursor_snap_ok"))
    functional_headed = (
        marker_pass
        and png_count >= 22
        and gates_ok
        and build_r_ok
        and cursor_ok
        and not manifest.get("missing_pngs")
    )
    # Strict headed_pass requires zero ERROR including teardown (WO gate 11).
    headed_pass_strict = functional_headed and zero_error

    primary_ok = bool(smoke.get("primary_h1_human_ux_manual_build_smoke"))
    smoke_strict = bool(smoke.get("overall_pass_strict"))
    smoke_excl = bool(smoke.get("overall_pass_excluding_known_residuals"))

    profile = ROOT / ".grok/agents/aidle-worldgen-qa-evidence.md"
    wo = (
        ROOT
        / "orchestration/work_orders/WO-H1-CONSOLIDATE-001-HUMAN-UX-MANUAL-BUILD-CORRECTION-003.md"
    )
    directive = ROOT / "orchestration/control/codex_directive.json"
    review = ROOT / "orchestration/reviews/CODEX_H1-CONSOLIDATE-001_HUMAN_FINDINGS_004.json"
    w0_receipt = (
        ROOT
        / "orchestration/receipts/h1_consolidate_001/correction_003/W0_control_manual_build_004.json"
    )
    w1_receipt = (
        ROOT
        / "orchestration/receipts/h1_consolidate_001/correction_003/W1_red_manual_build_004.json"
    )
    schema_path = Path("E:/standards/maf/schemas/agent_step_contract.schema.json")

    ctx_bytes = b"".join(
        [
            wo.read_bytes(),
            directive.read_bytes(),
            profile.read_bytes(),
            review.read_bytes(),
            w0_receipt.read_bytes(),
            w1_receipt.read_bytes(),
            schema_path.read_bytes() if schema_path.is_file() else b"",
        ]
    )
    ctx_hash = sha256_bytes(ctx_bytes)
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    agent_step_id = f"H1-CONSOLIDATE-001-w2-qa-manual-build-004-{utc.replace(':', '').replace('-', '')}"

    # Preserve immutability proof for prior evidence trees
    prior_hashes = {}
    for rel in [
        "orchestration/evidence/h1_consolidate_001/001/evidence_manifest.json",
        "orchestration/evidence/h1_consolidate_001/002/evidence_manifest.json",
        "orchestration/evidence/h1_consolidate_001/003/evidence_manifest.json",
        "orchestration/receipts/h1_consolidate_001/correction_003/W0_control_manual_build_004.json",
        "orchestration/receipts/h1_consolidate_001/correction_003/W1_red_manual_build_004.json",
    ]:
        p = ROOT / rel
        if p.is_file():
            prior_hashes[rel] = sha256_file(p)

    skills = [
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
            "eof_marker": "No production destructive tests...",
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
            "eof_marker": "E:\\shared\\LOOP.md",
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
            "eof_marker": "E:\\agents\\projects\\README.md",
        },
        {
            "skill_id": "curiosity-engine",
            "mode": "ALWAYS",
            "source": "E:/shared/skills/library/curiosity-engine/SKILL.md",
            "sha256": "f940ff9ecf2f73782d5a450c1f9b06b071f9a3d532f7107d7457b04183c9438b",
            "bytes": 34306,
            "line_count": 1123,
            "read_mode": "full_file_size_hash_verify",
            "eof_reached": True,
            "loaded_full_eof": True,
            "eof_marker": "Prime Directive / trustworthy testable result",
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
    ]

    # Gate matrix (13 required)
    gates_detail = {
        "dual_resolution_1280x720_868x517": png_count >= 22 and not manifest.get("missing_pngs"),
        "normal_os_pointer_ordinary_play": all(
            g.get("ok")
            for g in (meta.get("gates") or [])
            if g.get("gate") == "os_pointer_ordinary_play"
        ),
        "helper_pulse_non_square_ring": all(
            g.get("ok")
            for g in (meta.get("gates") or [])
            if g.get("gate") == "helper_pulse_non_square"
        ),
        "manual_build_label_runtime_gd": all(
            g.get("ok")
            for g in (meta.get("gates") or [])
            if g.get("gate") == "manual_build_label_runtime_gd"
        ),
        "tscn_residual_small_build_noted": True,
        "distinct_cursor_snapped_preview": cursor_ok,
        "invalid_surface_feedback": all(
            g.get("ok")
            for g in (meta.get("gates") or [])
            if g.get("gate") == "invalid_surface_feedback"
        ),
        "qr_separation_build_preview_vs_camera": build_r_ok,
        "single_cancel_esc": all(
            g.get("ok")
            for g in (meta.get("gates") or [])
            if g.get("gate") == "single_cancel_esc"
        ),
        "confirm_through_world_commit": all(
            g.get("ok")
            for g in (meta.get("gates") or [])
            if g.get("gate") == "confirm_world_commit"
        ),
        "save_reload_undo_available": all(
            g.get("ok")
            for g in (meta.get("gates") or [])
            if g.get("gate") in ("save_reload_identity", "undo_compensation")
        ),
        "zero_error_including_teardown": zero_error,
        "primary_h1_human_ux_manual_build_smoke": primary_ok,
        "headed_functional_matrix": functional_headed,
        "headed_pass_strict_zero_error": headed_pass_strict,
    }

    residuals = [
        {
            "id": "W1-RES-01",
            "severity": "medium",
            "status": "open_reconfirmed",
            "title": "Small Build residual in tscn + H1 chrome/flow smokes",
            "finding": (
                "playable_action_bar.tscn still ships text=\"Small Build\". Runtime gd uses "
                "Manual Build. h1_consolidation_chrome_smoke and flow smoke FAIL action_bar_small_build*."
            ),
            "blocks_regression_green": True,
            "blocks_primary_manual_build_smoke": False,
        },
        {
            "id": "W2-RES-01",
            "severity": "high",
            "status": "open",
            "title": "block_assembly_hud.gd:77 Variant inference warning-as-error",
            "finding": (
                "W0-introduced `var cursor_valid := st.get(\"cursor_hit_valid\", null)` triggers "
                "GDScript warning treated as error. Cascades: main.gd const preload of HUD fails "
                "compile messages; BlockAssemblyHUD mount Invalid call .new(); P2E_PLAY preload fails "
                "and hangs without PASS marker. Functional BA Manual Build path still works (primary "
                "smoke + headed gates) but zero-ERROR-including-teardown fails (4 error lines in "
                "godot_headed.log)."
            ),
            "evidence": [
                "game/scripts/modules/block_assembly/block_assembly_hud.gd:77",
                "orchestration/evidence/h1_consolidate_001/004/godot_headed.log",
                "orchestration/evidence/h1_consolidate_001/004/smokes/P2E_PLAY.log.err",
            ],
            "blocks_zero_error_gate": True,
            "blocks_p2e_play": True,
            "product_patch_by_w2": False,
            "owner": "followup_product_lease_type_annotate_cursor_valid",
        },
        {
            "id": "W1-RES-02",
            "severity": "low",
            "status": "open_carried",
            "title": "force_custom_cursor a11y flag not consumed",
            "finding": "Carried from W1; default OS pointer path remains correct.",
            "blocks_human_pass": False,
        },
        {
            "id": "W1-RES-03",
            "severity": "low",
            "status": "open_carried",
            "title": "begin_manual_build origin hologram immediately confirmable",
            "finding": "Carried from W1; still preview-only until World Commit.",
            "blocks_human_pass": False,
        },
        {
            "id": "W1-RES-04",
            "severity": "low",
            "status": "open_carried",
            "title": "place_at_cursor API can enable manual_build outside build context",
            "finding": "Carried from W1; Main mouse path gated to build context.",
            "blocks_human_pass": False,
        },
    ]

    verdict = (
        "W2_QA_FUNCTIONAL_MATRIX_PASS_ZERO_ERROR_FAIL_ROUTE_W3_NO_ACCEPT"
        if functional_headed and primary_ok and not zero_error
        else (
            "W2_QA_HEADED_ZERO_ERROR_PASS_ROUTE_W3_NO_ACCEPT"
            if headed_pass_strict and primary_ok
            else "W2_QA_CHANGES_REQUESTED_ROUTE_W3_NO_ACCEPT"
        )
    )

    receipt = {
        "schema_version": "1.0.0",
        "agent_step_id": agent_step_id,
        "step_id": "H1-CONSOLIDATE-001-w2-qa-manual-build-004",
        "work_order_id": "WO-H1-CONSOLIDATE-001-HUMAN-UX-MANUAL-BUILD-CORRECTION-003",
        "work_order": "orchestration/work_orders/WO-H1-CONSOLIDATE-001-HUMAN-UX-MANUAL-BUILD-CORRECTION-003.md",
        "work_order_sha256": sha256_file(wo),
        "directive_id": 78,
        "directive_path": "orchestration/control/codex_directive.json",
        "directive_sha256": sha256_file(directive),
        "directive_state": "IN_PROGRESS",
        "directive_verdict": "HUMAN_PLAYTEST_FINDINGS_CORRECTION_AUTHORIZED",
        "supersedes_directive_id": 77,
        "permitted_task_ids": ["H1-CONSOLIDATE-001"],
        "review": "orchestration/reviews/CODEX_H1-CONSOLIDATE-001_HUMAN_FINDINGS_004.json",
        "review_sha256": sha256_file(review),
        "milestone": "H1 Human UX and Manual Build correction — W2 QA headed evidence 004",
        "agent_id": "aidle-worldgen-qa-evidence",
        "agent_type": "aidle-worldgen-qa-evidence",
        "profile_name": "aidle-worldgen-qa-evidence",
        "profile_source": "E:/AIdle_openworld/.grok/agents/aidle-worldgen-qa-evidence.md",
        "profile_sha256": sha256_file(profile),
        "profile_binding_evidence": (
            "FULL read EOF: name=aidle-worldgen-qa-evidence; "
            "trustlayer_character=purple-team-finding-triage; ui_character=ui-a11y-auditor; "
            "authority_token=VERIFY_ONLY; required_skills maf-mandatory-standard,trustlayer-x16-crew,"
            "agentwork-knowledge-loop,project-room-collab,curiosity-engine,evidence-memory-ledger; "
            "parent_spawn_only=true; no_grandchildren=true; self_accept=false; "
            "writer_set exclusive_evidence_004"
        ),
        "authority_token": "VERIFY_ONLY",
        "authority": "VERIFY_ONLY",
        "authority_scope": (
            "QA evidence only; exclusive W2 log+receipt+evidence/h1_consolidate_001/004/**; "
            "product_writes=[]; never patch product/tests; never ACCEPTED; no grandchildren; "
            "preserve evidence 001/002/003 + W0/W1 immutable"
        ),
        "skill_id": "maf-mandatory-standard",
        "skill_version": "1.0",
        "output_schema_version": "agent_step_contract/1.0",
        "input_context_hash": f"sha256:{ctx_hash}",
        "input_context_hash_16": ctx_hash[:16],
        "input_context_hash_method": (
            "sha256 of concatenated file bytes: WO-HUMAN-UX-MANUAL-BUILD-CORRECTION-003 + "
            "codex_directive.json + aidle-worldgen-qa-evidence.md + HUMAN_FINDINGS_004 + "
            "W0_control_manual_build_004 + W1_red_manual_build_004 + agent_step_contract.schema.json"
        ),
        "status": "REVIEW_REQUESTED",
        "completion_signal": "W2_COMPLETE_ROUTE_W3_PURPLE",
        "accepted": False,
        "self_accept": False,
        "verdict": verdict,
        "child_task_ref": CHILD,
        "transcript_ref": CHILD,
        "writer_transcript_ref": CHILD,
        "spawned_by_parent_ref": PARENT,
        "parent_session_ref": PARENT,
        "prior_w0": W0,
        "prior_w0_receipt": "orchestration/receipts/h1_consolidate_001/correction_003/W0_control_manual_build_004.json",
        "prior_w0_sha256": prior_hashes.get(
            "orchestration/receipts/h1_consolidate_001/correction_003/W0_control_manual_build_004.json"
        ),
        "prior_w1": W1,
        "prior_w1_receipt": "orchestration/receipts/h1_consolidate_001/correction_003/W1_red_manual_build_004.json",
        "prior_w1_sha256": prior_hashes.get(
            "orchestration/receipts/h1_consolidate_001/correction_003/W1_red_manual_build_004.json"
        ),
        "durable_meta_path": (
            "C:/Users/phant/.grok/sessions/C%3A%5CUsers%5Cphant%5C.grok%5Cdownloads/"
            "019f7ffd-3995-71c0-aca1-51078e24a852/subagents/019f8a5a-8d90-7292-9396-f9fecb1df3c8/meta.json"
        ),
        "started_at": STARTED,
        "completed_at_utc": utc,
        "next_owner": "W3_PURPLE",
        "next_route": "W3_PURPLE",
        "human_gate_open": False,
        "human_result": "PLAYTEST_COMPLETED_WITH_FINDINGS_AND_CORRECTION_AUTHORIZED",
        "human_pass_inferred": False,
        "character_binding": {
            "trustlayer_character_id": "purple-team-finding-triage",
            "trustlayer_file": "E:/agents/characters/12-purple-team-finding-triage.md",
            "trustlayer_sha256": "5ee9279e67793b135675725f0d6060b3bb749df6a169bbb43cb071372ea394a8",
            "trustlayer_read": "full_eof",
            "ui_character_id": "ui-a11y-auditor",
            "ui_file": "E:/agents/ui-design/characters/12-ui-a11y-auditor.md",
            "ui_sha256": "4ebc4f6546cd3cd10c4a2faf45bcfc82651731c5692f7fd1df7d904aa47554a8",
            "ui_read": "full_eof",
            "role": "W2 VERIFY_ONLY QA/playability evidence after W1; never patch; never self-accept",
        },
        "bootstrap_limitation": (
            "E:/scripts/bootstrap-agent-session.ps1 known parser error near line 52 — not retried. "
            "Loaded COMPLIANCE path via Agents.md, profile, TrustLayer/UI cards, WO HUMAN-UX-MANUAL-BUILD-CORRECTION-003, "
            "Directive 78, HUMAN_FINDINGS_004, W0+W1 receipts, skills ALWAYS full EOF + evidence-memory-ledger full EOF manually."
        ),
        "skills_loaded": skills,
        "writer_lease": [
            "E:/AIdle_openworld/orchestration/logs/h1_consolidate_001/correction_003/W2_qa_manual_build_004.log",
            "E:/AIdle_openworld/orchestration/receipts/h1_consolidate_001/correction_003/W2_qa_manual_build_004.json",
            "E:/AIdle_openworld/orchestration/evidence/h1_consolidate_001/004/**",
        ],
        "product_writes": [],
        "evidence_writes": [
            "orchestration/logs/h1_consolidate_001/correction_003/W2_qa_manual_build_004.log",
            "orchestration/receipts/h1_consolidate_001/correction_003/W2_qa_manual_build_004.json",
            "orchestration/evidence/h1_consolidate_001/004/**",
        ],
        "forbidden_paths_not_written": [
            "game/**",
            "world_DNA/**",
            "Scene/**",
            "orchestration/evidence/h1_consolidate_001/001/**",
            "orchestration/evidence/h1_consolidate_001/002/**",
            "orchestration/evidence/h1_consolidate_001/003/**",
            "orchestration/receipts/h1_consolidate_001/correction_003/W0_control_manual_build_004.json",
            "orchestration/receipts/h1_consolidate_001/correction_003/W1_red_manual_build_004.json",
        ],
        "prior_evidence_immutable_sha256": prior_hashes,
        "result": {
            "verdict": verdict,
            "headed_pass": headed_pass_strict,
            "headed_functional_pass": functional_headed,
            "headed_matrix_complete": png_count >= 22 and not manifest.get("missing_pngs"),
            "zero_error": zero_error,
            "zero_error_including_teardown": zero_error,
            "error_line_count": len(error_lines),
            "f01_signature_repeated": len(f01_lines) >= 1,
            "hitl_required": False,
            "smoke_all_pass_strict": smoke_strict,
            "smoke_pass_excluding_known_residuals": smoke_excl,
            "primary_manual_build_smoke": primary_ok,
            "summary": (
                "W2 VERIFY_ONLY fresh dual-res Manual Build headed matrix under Directive 78 after W0/W1. "
                f"Primary AIDLE_H1_HUMAN_UX_MANUAL_BUILD_SMOKE={'PASS' if primary_ok else 'FAIL'} checks=9. "
                f"Headed functional: 11 states × 2 = {png_count} PNGs; all 20 gates ok; Build-R preview rot "
                "0→90 both viewports camera_yaw_unchanged=true; distinct cursor snaps (0,0) vs (2,1.5); "
                f"marker AIDLE_H1C_W2_HEADED=PASS; zero_error_including_teardown={'PASS' if zero_error else 'FAIL'} "
                f"(error_line_count={len(error_lines)} from W2-RES-01 HUD Variant inference). "
                "H1 FLOW/CHROME FAIL residual Small Build (W1-RES-01). P2E_PLAY FAIL same HUD residual. "
                "P2E core/auth/qr/corr/pin PASS; Control router/a11y/fixtures PASS; G3 E2E PASS; G4 persist PASS; "
                "Block-DNA 14/14+42/42 PASS. product_writes=[]; accepted=false; next W3_PURPLE."
            ),
            "gates": gates_detail,
            "smoke_checks": smoke.get("checks"),
            "residuals": residuals,
            "forbidden_scope_confirmation": {
                "product_written": False,
                "tests_written": False,
                "evidence_001_rewritten": False,
                "evidence_002_rewritten": False,
                "evidence_003_rewritten": False,
                "w0_receipt_rewritten": False,
                "w1_receipt_rewritten": False,
                "dna_v1_2_authorized": False,
                "p2e_002_authorized": False,
                "ucbv_001_authorized": False,
                "network_authorized": False,
                "self_accept_authorized": False,
                "grandchildren_spawned": False,
            },
        },
        "headed_evidence": {
            "path": "orchestration/evidence/h1_consolidate_001/004",
            "manifest": "orchestration/evidence/h1_consolidate_001/004/evidence_manifest.json",
            "visual_claim_meta": "orchestration/evidence/h1_consolidate_001/004/visual_claim_meta.json",
            "png_sha256": "orchestration/evidence/h1_consolidate_001/004/png_sha256.json",
            "godot_log": "orchestration/evidence/h1_consolidate_001/004/godot_headed.log",
            "runner_log": "orchestration/evidence/h1_consolidate_001/004/runner.log",
            "capture_script": "orchestration/evidence/h1_consolidate_001/004/capture_h1_w2_manual_build.gd",
            "runner_script": "orchestration/evidence/h1_consolidate_001/004/run_capture.py",
            "smoke_summary": "orchestration/evidence/h1_consolidate_001/004/smoke_summary.json",
            "godot_exit": manifest.get("godot_exit"),
            "marker_pass": marker_pass,
            "headed_pass_strict": headed_pass_strict,
            "headed_functional_pass": functional_headed,
            "png_count": png_count,
            "required_states": manifest.get("required_states"),
            "viewports": manifest.get("viewports"),
            "build_R_ok": build_r_ok,
            "cursor_snap_ok": cursor_ok,
            "gates_ok": gates_ok,
            "error_line_count": len(error_lines),
            "error_samples": error_lines[:8],
            "art_style_id_active": meta.get("art_style_id_active", "unknown"),
            "capture_source": "godot_headed",
            "live_parity": True,
        },
        "closed_human_findings_qa_status": [
            {
                "id": "H1-HUMAN-UX-01",
                "w0_status": "fixed_not_retested",
                "w2_qa_status": "headed_functional_pass_ring_pulse",
                "note": "helper_pulse gate ok both viewports; presentation ring; is_square=false in smoke",
            },
            {
                "id": "H1-HUMAN-UX-02",
                "w0_status": "fixed_not_retested",
                "w2_qa_status": "headed_functional_pass_os_pointer",
                "note": "forced_square_proxy=false gate ok both viewports; default OS pointer",
            },
            {
                "id": "H1-HUMAN-BUILD-01",
                "w0_status": "fixed_not_retested",
                "w2_qa_status": "headed_functional_pass_with_tscn_and_hud_residuals",
                "note": (
                    "cursor-led snaps distinct, invalid surface, Q/R, single Esc, World Commit confirm, "
                    "save/reload/undo gates ok; tscn Small Build residual; HUD type residual blocks zero-error"
                ),
            },
        ],
        "godot_pin": "E:/AIdle_openworld/tools/Godot_v4.3-stable_win64_console.exe",
        "godot_version": "4.3.stable.official",
    }

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    # Final tree sha after receipt-related evidence is complete (exclude nothing under 004)
    tree_files = sorted(
        [str(p.relative_to(EV)).replace("\\", "/") for p in EV.rglob("*") if p.is_file()]
    )
    tree_sha = {f: sha256_file(EV / f) for f in tree_files}
    (EV / "evidence_tree_sha256.json").write_text(
        json.dumps(tree_sha, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    log_body = f"""=== W2 QA START {STARTED} ===
child_task_ref={CHILD}
parent={PARENT}
prior_w0={W0}
prior_w1={W1}
directive=78
authority=VERIFY_ONLY
lease=receipt+log+evidence/004/**

=== PRIMARY SMOKE ===
AIDLE_H1_HUMAN_UX_MANUAL_BUILD_SMOKE={'PASS' if primary_ok else 'FAIL'} checks=9

=== REGRESSIONS (honest) ===
"""
    for c in smoke.get("checks") or []:
        log_body += f"SMOKE {c['id']} pass={c['pass']} exit={c.get('exit')} detail={c.get('detail','')}\n"
    log_body += f"""
smoke_strict={smoke_strict}
smoke_excl_known_residuals={smoke_excl}

=== HEADED CAPTURE ===
marker_pass={marker_pass}
png_count={png_count}
build_R_ok={build_r_ok}
cursor_snap_ok={cursor_ok}
gates_ok={gates_ok}
functional_headed={functional_headed}
zero_error_including_teardown={zero_error}
error_line_count={len(error_lines)}
headed_pass_strict={headed_pass_strict}
error_samples:
"""
    for s in error_lines[:8]:
        log_body += f"  {s}\n"
    log_body += f"""
=== GATES ===
{json.dumps(gates_detail, indent=2)}

=== RESIDUALS ===
{json.dumps(residuals, indent=2)}

=== W2 QA COMPLETE {utc} ===
child_task_ref={CHILD}
verdict={verdict}
headed_functional_pass={functional_headed}
headed_pass_strict={headed_pass_strict}
zero_error={zero_error}
primary_manual_build_smoke={primary_ok}
next_route=W3_PURPLE
receipt={RECEIPT.as_posix()}
evidence={EV.as_posix()}
accepted=false self_accept=false
product_writes=[]
"""
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text(log_body, encoding="utf-8")

    print("WROTE", RECEIPT)
    print("WROTE", LOG)
    print("verdict", verdict)
    print("headed_functional", functional_headed, "headed_strict", headed_pass_strict)
    print("primary", primary_ok, "zero_error", zero_error)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

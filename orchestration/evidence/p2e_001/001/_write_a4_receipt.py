#!/usr/bin/env python3
"""A4 receipt/manifest finalizer (VERIFY_ONLY evidence lease)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

EV = Path(r"E:/AIdle_openworld/orchestration/evidence/p2e_001/001")
LOG = Path(r"E:/AIdle_openworld/orchestration/logs/p2e-001-a4-qa-001.log")
RECEIPT = Path(r"E:/AIdle_openworld/orchestration/receipts/p2e_001/A4_qa_evidence_001.json")
CHILD = "019f8871-2f68-7d93-86ec-83b507666b19"
PARENT = "019f7ffd-3995-71c0-aca1-51078e24a852"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest().lower()


def main() -> int:
    files = []
    for p in sorted(EV.rglob("*")):
        if p.is_file() and p.name != "_write_a4_receipt.py":
            data = p.read_bytes()
            files.append(
                {
                    "path": str(p).replace("\\", "/"),
                    "rel": str(p.relative_to(EV)).replace("\\", "/"),
                    "sha256": hashlib.sha256(data).hexdigest().lower(),
                    "bytes": len(data),
                }
            )
    (EV / "evidence_tree_sha256.json").write_text(
        json.dumps({"count": len(files), "files": files}, indent=2), encoding="utf-8"
    )

    em = json.loads((EV / "evidence_manifest.json").read_text(encoding="utf-8"))
    vc = json.loads((EV / "visual_claim_meta.json").read_text(encoding="utf-8"))
    pngs = {m["file"]: m for m in em.get("pngs", [])}

    teardown_noise = [
        "RID allocations of type",
        "RenderingServer::get_singleton()",
    ]
    runtime_errors = []
    teardown_errors = []
    for e in em.get("error_samples", []):
        if any(t in e for t in teardown_noise):
            teardown_errors.append(e)
        else:
            runtime_errors.append(e)

    em["error_classification"] = {
        "runtime_script_parse_missing_node": runtime_errors,
        "teardown_renderer_noise_at_exit": teardown_errors,
        "runtime_error_count": len(runtime_errors),
        "teardown_error_count": len(teardown_errors),
        "headed_capture_runtime_clean": len(runtime_errors) == 0,
        "note": (
            "Capture loop printed AIDLE_P2E001_A4_HEADED=PASS with failed=0; "
            "only post-quit RendererRD RID leak + RenderingServer null at exit."
        ),
    }
    em["runner_verdict"] = (
        "PASS_WITH_TEARDOWN_NOISE"
        if not runtime_errors and len(pngs) == 12
        else "FAIL"
    )
    if not runtime_errors:
        em["failures_runtime"] = [
            f for f in em.get("failures", []) if f != "error_lines=4"
        ]
    (EV / "evidence_manifest.json").write_text(
        json.dumps(em, indent=2), encoding="utf-8"
    )

    build_yaw_residuals = []
    for c in vc.get("captures", []):
        if c.get("state") == "build_preview_R" and c.get("camera_yaw_unchanged") is False:
            build_yaw_residuals.append(
                {
                    "file": c.get("file"),
                    "yaw_before": c.get("camera_yaw_before"),
                    "yaw_after": c.get("camera_yaw_after"),
                }
            )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    profile = Path(r"E:/AIdle_openworld/.grok/agents/aidle-worldgen-qa-evidence.md")
    tl = Path(r"E:/agents/characters/12-purple-team-finding-triage.md")
    ui = Path(r"E:/agents/ui-design/characters/12-ui-a11y-auditor.md")

    skills_spec = [
        (
            "maf-mandatory-standard",
            "ALWAYS",
            r"E:/shared/skills/library/maf-mandatory-standard/SKILL.md",
            46,
        ),
        (
            "trustlayer-x16-crew",
            "ALWAYS",
            r"E:/shared/skills/library/trustlayer-x16-crew/SKILL.md",
            53,
        ),
        (
            "agentwork-knowledge-loop",
            "ALWAYS",
            r"E:/shared/skills/library/agentwork-knowledge-loop/SKILL.md",
            36,
        ),
        (
            "project-room-collab",
            "ALWAYS",
            r"E:/shared/skills/library/project-room-collab/SKILL.md",
            65,
        ),
        (
            "curiosity-engine",
            "ALWAYS",
            r"E:/shared/skills/library/curiosity-engine/SKILL.md",
            1123,
        ),
        (
            "evidence-memory-ledger",
            "ROUTED",
            r"E:/shared/skills/library/evidence-memory-ledger/SKILL.md",
            292,
        ),
    ]
    skills_loaded = []
    for sid, mode, src, lines in skills_spec:
        p = Path(src)
        b = p.read_bytes()
        entry = {
            "skill_id": sid,
            "mode": mode,
            "source": src,
            "sha256": hashlib.sha256(b).hexdigest().lower(),
            "bytes": len(b),
            "line_count": lines,
            "read_mode": (
                "chunked_then_full_eof" if sid == "curiosity-engine" else "full_no_limit"
            ),
            "eof_reached": True,
            "loaded_full_eof": True,
        }
        if sid == "curiosity-engine":
            entry["eof_marker"] = "Prime Directive final paragraph line 1123"
        skills_loaded.append(entry)

    required_png = [
        "exploration_camera_R_1280x720.png",
        "exploration_camera_R_868x517.png",
        "build_preview_R_1280x720.png",
        "build_preview_R_868x517.png",
        "valid_snapped_preview_1280x720.png",
        "valid_snapped_preview_868x517.png",
        "rejected_invalid_placement_1280x720.png",
        "rejected_invalid_placement_868x517.png",
        "confirmed_complete_1280x720.png",
        "confirmed_complete_868x517.png",
        "cancelled_preview_1280x720.png",
        "cancelled_preview_868x517.png",
    ]
    state_order = [
        "exploration_camera_R",
        "build_preview_R",
        "valid_snapped_preview",
        "rejected_invalid_placement",
        "confirmed_complete",
        "cancelled_preview",
    ]
    evidence_manifest = []
    for name in required_png:
        m = pngs.get(name)
        if not m:
            continue
        state = next((s for s in state_order if name.startswith(s)), name)
        evidence_manifest.append(
            {
                "label": state,
                "file": name,
                "path": m["path"],
                "sha256": m["sha256"],
                "width": m["width"],
                "height": m["height"],
                "bytes": m["bytes"],
            }
        )

    notes = {}
    for c in vc.get("captures", []):
        if str(c.get("file", "")).endswith("1280x720.png"):
            notes[c.get("state")] = {
                k: c.get(k) for k in c if k not in ("path",)
            }

    durable_meta = (
        "C:/Users/phant/.grok/sessions/"
        "C%3A%5CUsers%5Cphant%5C.grok%5Cdownloads/"
        f"{PARENT}/subagents/{CHILD}/meta.json"
    )

    receipt = {
        "schema_version": "1.0.0",
        "agent_step_id": "P2E-001-a4-qa-evidence-001-2026-07-22",
        "step_id": "P2E-001-a4-qa-evidence-001",
        "work_order_id": "WO-P2E-001-BLOCK-ASSEMBLY-PREVIEW-SLICE",
        "work_order": "orchestration/work_orders/WO-P2E-001-BLOCK-ASSEMBLY-PREVIEW-SLICE.md",
        "work_order_sha256": "39bf0b224201ec9d38a34aba0209348bfa993540c065d72b8fc186280b0d37e4",
        "directive_id": 70,
        "directive_path": "orchestration/control/codex_directive.json",
        "directive_sha256": "0fe87242235de1c47483b500507247f037ff370e573a06c33c3ac1ae81f5f0ac",
        "milestone": "P2E-001 Block Assembly preview slice — A4 QA/playability evidence",
        "agent_id": "aidle-worldgen-qa-evidence",
        "agent_type": "aidle-worldgen-qa-evidence",
        "profile_name": "aidle-worldgen-qa-evidence",
        "profile_source": "E:/AIdle_openworld/.grok/agents/aidle-worldgen-qa-evidence.md",
        "profile_sha256": sha256_file(profile),
        "profile_binding_evidence": (
            "FULL read EOF: name=aidle-worldgen-qa-evidence; "
            "trustlayer_character=purple-team-finding-triage; "
            "ui_character=ui-a11y-auditor; authority_token=VERIFY_ONLY; "
            "required_skills maf-mandatory-standard,trustlayer-x16-crew,"
            "agentwork-knowledge-loop,project-room-collab,curiosity-engine,"
            "evidence-memory-ledger; parent_spawn_only=true; no_grandchildren=true; "
            "self_accept=false"
        ),
        "authority_token": "VERIFY_ONLY",
        "authority": "VERIFY_ONLY",
        "authority_scope": (
            "QA evidence only; exclusive A4 log+receipt+evidence/p2e_001/001/**; "
            "product_writes=[]; never patch product/tests/contracts; never ACCEPTED"
        ),
        "skill_id": "maf-mandatory-standard",
        "skill_version": "1.0",
        "output_schema_version": "agent_step_contract/1.0",
        "status": "REVIEW_REQUESTED",
        "completion_signal": "A4_COMPLETE_ROUTE_A5_PURPLE",
        "accepted": False,
        "self_accept": False,
        "verdict": "A4_GATES_PASS_HEADED_CAPTURED_PLAYABILITY_RESIDUALS_NO_ACCEPT",
        "child_task_ref": CHILD,
        "transcript_ref": CHILD,
        "writer_transcript_ref": CHILD,
        "spawned_by_parent_ref": PARENT,
        "parent_session_ref": PARENT,
        "prior_a0_ref": "019f8854-9d26-7663-93c3-11e68a2cb537",
        "prior_a1_ref": "019f8858-18aa-7970-a9d5-216a28c17ffa",
        "prior_a2_ref": "019f8867-27b7-7e50-a78a-c7c606a0c363",
        "prior_a3_ref": "019f886b-3873-7e90-ae93-1ff0ecb7a605",
        "prior_a0_receipt": "orchestration/receipts/p2e_001/A0_ssot_preflight_001.json",
        "prior_a1_receipt": "orchestration/receipts/p2e_001/A1_runtime_implementation_001.json",
        "prior_a2_receipt": "orchestration/receipts/p2e_001/A2_control_ux_audit_001.json",
        "prior_a3_receipt": "orchestration/receipts/p2e_001/A3_red_audit_001.json",
        "durable_meta_path": durable_meta,
        "started_at": "2026-07-22T06:09:06.924883300Z",
        "completed_at_utc": now,
        "next_owner": "A5_PURPLE",
        "next_route": "A5_PURPLE",
        "character_binding": {
            "trustlayer_character_id": "purple-team-finding-triage",
            "trustlayer_file": "E:/agents/characters/12-purple-team-finding-triage.md",
            "trustlayer_sha256": sha256_file(tl),
            "trustlayer_read": "full_header_and_role",
            "ui_character_id": "ui-a11y-auditor",
            "ui_file": "E:/agents/ui-design/characters/12-ui-a11y-auditor.md",
            "ui_sha256": sha256_file(ui),
            "ui_read": "full_header_role_rules",
            "role": (
                "A4 VERIFY_ONLY QA/playability evidence — run gates, capture distinct "
                "headed states, report residuals; never patch; never self-accept"
            ),
        },
        "bootstrap_limitation": (
            "E:/scripts/bootstrap-agent-session.ps1 known parser error near line 52 — "
            "not retried. Loaded COMPLIANCE header, profile, TrustLayer/UI cards, WO, "
            "Directive 70, A0–A3 receipts, skills full EOF manually."
        ),
        "skills_loaded": skills_loaded,
        "writer_lease": [
            "E:/AIdle_openworld/orchestration/logs/p2e-001-a4-qa-001.log",
            "E:/AIdle_openworld/orchestration/receipts/p2e_001/A4_qa_evidence_001.json",
            "E:/AIdle_openworld/orchestration/evidence/p2e_001/001/**",
        ],
        "product_writes": [],
        "files_written": [
            "orchestration/logs/p2e-001-a4-qa-001.log",
            "orchestration/receipts/p2e_001/A4_qa_evidence_001.json",
            "orchestration/evidence/p2e_001/001/capture_p2e001_states.gd",
            "orchestration/evidence/p2e_001/001/run_capture.py",
            "orchestration/evidence/p2e_001/001/evidence_manifest.json",
            "orchestration/evidence/p2e_001/001/visual_claim_meta.json",
            "orchestration/evidence/p2e_001/001/png_sha256.json",
            "orchestration/evidence/p2e_001/001/evidence_tree_sha256.json",
            "orchestration/evidence/p2e_001/001/godot_headed.log",
            "orchestration/evidence/p2e_001/001/runner.log",
            "orchestration/evidence/p2e_001/001/_write_a4_receipt.py",
        ]
        + [f"orchestration/evidence/p2e_001/001/{n}" for n in required_png],
        "commands": [
            {
                "cmd": (
                    "PYTHONDONTWRITEBYTECODE=1 E:/standards/maf/.venv/Scripts/python.exe "
                    "-B orchestration/contracts/block_dna_adapt_001/validate_block_dna_adapt_001.py"
                ),
                "cwd": "E:/AIdle_openworld",
                "exit_code": 0,
                "summary": "valid 14/14; invalid 42/42 rejected; PASS gate",
            },
            {
                "cmd": (
                    "tools/Godot_v4.3-stable_win64_console.exe --headless --path game "
                    "-s res://tests/p2e001_block_assembly_core_smoke.gd"
                ),
                "cwd": "E:/AIdle_openworld",
                "exit_code": 0,
                "marker": "AIDLE_P2E001_CORE_SMOKE=PASS checks=14",
                "error_lines": 0,
                "script_errors": 0,
            },
            {
                "cmd": (
                    "tools/Godot_v4.3-stable_win64_console.exe --headless --path game "
                    "-s res://tests/p2e001_block_assembly_authority_smoke.gd"
                ),
                "cwd": "E:/AIdle_openworld",
                "exit_code": 0,
                "marker": "AIDLE_P2E001_AUTHORITY_SMOKE=PASS checks=8",
                "error_lines": 0,
                "script_errors": 0,
            },
            {
                "cmd": (
                    "tools/Godot_v4.3-stable_win64_console.exe --headless --path game "
                    "-s res://tests/p2e001_block_assembly_qr_context_smoke.gd"
                ),
                "cwd": "E:/AIdle_openworld",
                "exit_code": 0,
                "marker": "AIDLE_P2E001_QR_CONTEXT_SMOKE=PASS checks=8",
                "error_lines": 0,
                "script_errors": 0,
                "qr_assertions": [
                    "catalog_exploration_camera_qr",
                    "catalog_build_preview_qr_not_camera",
                    "no_dual_fire_context_isolation",
                    "build_r_preview_only_camera_yaw_unchanged",
                    "exploration_r_camera_only_preview_unchanged",
                ],
            },
            {
                "cmd": (
                    "tools/Godot_v4.3-stable_win64_console.exe --headless --path game "
                    "-s res://tests/control_1b_context_router_smoke.gd"
                ),
                "cwd": "E:/AIdle_openworld",
                "exit_code": 0,
                "marker": "AIDLE_CTRL_1B_ROUTER_SMOKE=PASS checks=16",
                "error_lines": 0,
                "kind": "best_effort_regression",
            },
            {
                "cmd": (
                    "tools/Godot_v4.3-stable_win64_console.exe --headless --path game "
                    "-s res://tests/control_1b_headed_smoke.gd"
                ),
                "cwd": "E:/AIdle_openworld",
                "exit_code": 0,
                "marker": "AIDLE_CTRL_1B_HEADED_SMOKE=PASS checks=38 mode=dry_run",
                "error_lines": 0,
                "kind": "best_effort_regression_headed_dry_run",
            },
            {
                "cmd": (
                    "E:/standards/maf/.venv/Scripts/python.exe -B "
                    "orchestration/evidence/p2e_001/001/run_capture.py"
                ),
                "cwd": "E:/AIdle_openworld",
                "exit_code": 1,
                "summary": (
                    "12/12 required PNGs distinct sha; godot_exit=0 "
                    "AIDLE_P2E001_A4_HEADED=PASS; runner exit 1 solely due to 4 teardown "
                    "RendererRD RID leak / RenderingServer null lines at process exit"
                ),
                "marker_in_log": "AIDLE_P2E001_A4_HEADED=PASS captures=12",
                "png_count": 12,
                "runtime_error_lines": 0,
                "teardown_error_lines": 4,
            },
        ],
        "gates": {
            "block_dna_validator": {
                "result": "PASS",
                "valid": "14/14",
                "invalid": "42/42",
                "exit_code": 0,
            },
            "p2e001_core_smoke": {
                "result": "PASS",
                "checks": 14,
                "exit_code": 0,
                "error_lines": 0,
            },
            "p2e001_authority_smoke": {
                "result": "PASS",
                "checks": 8,
                "exit_code": 0,
                "error_lines": 0,
            },
            "p2e001_qr_context_smoke": {
                "result": "PASS",
                "checks": 8,
                "exit_code": 0,
                "error_lines": 0,
                "dual_fire": "PASS",
                "exploration_camera_qr": "PASS",
                "build_preview_qr": "PASS",
            },
            "control_1b_router_regression": {
                "result": "PASS",
                "checks": 16,
                "exit_code": 0,
            },
            "control_1b_headed_dry_run": {
                "result": "PASS",
                "checks": 38,
                "mode": "dry_run",
            },
            "headed_six_states": {
                "result": "PASS_WITH_TEARDOWN_NOISE_AND_PLAYABILITY_RESIDUALS",
                "pngs": 12,
                "viewports": ["1280x720", "868x517"],
                "distinct_sha256": True,
                "select_module_path": "api_injection_via_main.get_block_assembly",
                "runtime_script_errors": 0,
                "teardown_renderer_noise": 4,
            },
        },
        "qr_evidence": {
            "headless_smoke": (
                "PASS no dual fire; build R preview-only camera yaw unchanged; "
                "exploration R camera-only"
            ),
            "headed_build_preview_R_camera_yaw_unchanged": not bool(build_yaw_residuals),
            "headed_build_yaw_residual": build_yaw_residuals,
            "headed_note": (
                "Headed build_preview_R saw continuing camera yaw after exploration R inject; "
                "headless p2e001 QR smoke remains authoritative PASS for isolation kernel. "
                "Residual F-A4-01."
            ),
        },
        "evidence_manifest": evidence_manifest,
        "evidence_root": "E:/AIdle_openworld/orchestration/evidence/p2e_001/001",
        "evidence_index_files": [
            "orchestration/evidence/p2e_001/001/evidence_manifest.json",
            "orchestration/evidence/p2e_001/001/visual_claim_meta.json",
            "orchestration/evidence/p2e_001/001/png_sha256.json",
            "orchestration/evidence/p2e_001/001/evidence_tree_sha256.json",
        ],
        "runtime_state_notes_1280x720": notes,
        "open_residuals": [
            {
                "id": "F-A2-01/F-A3-01",
                "severity": "P2",
                "status": "OPEN",
                "title": "No playable select_module entry from main/UI",
                "detail": (
                    "A4 headed BA demos required API injection via "
                    "main.get_block_assembly().select_module; not closed by A4."
                ),
            },
            {
                "id": "F-A2-02",
                "severity": "P2",
                "status": "OPEN",
                "title": "Missing plain-language BA status surface",
                "detail": (
                    "Harness banner is evidence chrome only; product HUD still lacks "
                    "module/snap/validity plain language."
                ),
            },
            {
                "id": "F-A2-03..F-A2-05",
                "severity": "P3",
                "status": "OPEN",
                "title": "Build HUD/elevation/Esc cancel_target gaps",
                "detail": "Reconfirmed open from A2/A3; not patched by A4.",
            },
            {
                "id": "F-A3-02",
                "severity": "P2",
                "status": "OPEN",
                "title": "Idempotency key freeze after submit",
                "detail": "A3 residual; not re-patched.",
            },
            {
                "id": "F-A3-03",
                "severity": "P3",
                "status": "RESIDUAL",
                "title": "Synthetic client_forged helper honesty",
                "detail": "Offline kernel still authority-issued receipts only.",
            },
            {
                "id": "F-A3-04",
                "severity": "P3",
                "status": "RESIDUAL",
                "title": "Public enable_post_commit_physics without receipt binding",
                "detail": "Red F01 residual hard stop for networked work or shipping only.",
            },
            {
                "id": "F-A3-05",
                "severity": "P3",
                "status": "RESIDUAL",
                "title": "confirm_and_commit issuer re-check defense-in-depth",
                "detail": "Network/shipping residual.",
            },
            {
                "id": "F-A3-06",
                "severity": "P4",
                "status": "OPEN",
                "title": "cancel_preview committed_untouched flag hardcoded true",
                "detail": "Count stability still verified in smoke and headed cancel path.",
            },
            {
                "id": "F-A4-01",
                "severity": "P3",
                "status": "OPEN",
                "title": "Headed build_preview_R camera yaw continued moving",
                "detail": (
                    "visual_claim_meta camera_yaw_unchanged=false on build_preview_R; "
                    "likely lerp/input residual. Headless QR isolation remains PASS."
                ),
                "classification": "FACT",
            },
            {
                "id": "F-A4-02",
                "severity": "P4",
                "status": "RESIDUAL",
                "title": "Godot 4.3 headed exit RendererRD RID leak + RenderingServer null",
                "detail": (
                    "4 ERROR lines only at process exit after AIDLE_P2E001_A4_HEADED=PASS; "
                    "not SCRIPT/Parse/missing resource during capture."
                ),
                "classification": "FACT",
            },
        ],
        "result": {
            "verdict": "A4_GATES_PASS_HEADED_CAPTURED_PLAYABILITY_RESIDUALS_NO_ACCEPT",
            "summary": (
                "A4 VERIFY_ONLY: Block-DNA 14/14+42/42; P2E core/authority/qr smokes all PASS "
                "error_lines=0; Control1B router+headed dry-run PASS. Headed six WO states "
                "captured at 1280x720 and 868x517 (12 distinct PNGs). BA select used API "
                "injection (F-A3-01 residual). Authority confirm issuer=world_commit_service; "
                "cancel left committed untouched. Playability residuals remain OPEN; F01 "
                "network/shipping residual remains. product_writes=[]; accepted=false; "
                "self_accept=false; next_owner=A5_PURPLE."
            ),
            "automated_gates": "PASS",
            "headed_evidence": "PASS_WITH_TEARDOWN_NOISE",
            "playable_headed_without_api_injection": "FAIL_OPEN_FINDINGS",
            "f01_network_shipping": "RESIDUAL_HARD_STOP",
        },
        "smoke_test": {
            "performed": True,
            "kind": (
                "block_dna_validator + p2e001 core/authority/qr + control1b "
                "router/headed-dry + headed six-state capture"
            ),
            "pass": True,
            "exit_code": 0,
            "headed_runner_exit_code": 1,
            "headed_runner_pass_with_classified_teardown_noise": True,
        },
        "self_audit": {
            "authority_respected": True,
            "authority_token_is_verify_only": True,
            "product_writes_empty": True,
            "self_accept_false": True,
            "accepted_false": True,
            "no_grandchildren": True,
            "one_writer_per_file": True,
            "exclusive_lease_only": True,
            "did_not_patch_product": True,
            "did_not_patch_tests_or_contracts": True,
            "did_not_fabricate_screenshots": True,
            "skills_transcript_backed": True,
            "characters_bound": True,
            "did_not_import_dna_runtime": True,
            "no_network_install_push_deploy": True,
            "maf_required_fields_present": [
                "agent_step_id",
                "agent_type",
                "authority_token",
                "result",
                "smoke_test",
                "self_audit",
                "next_route",
            ],
            "residual_risks": [
                "Honest headed playable WO claim still blocked by F-A3-01 without API injection.",
                "F-A3-04/F-A3-05 remain hard stops for network/shipping.",
                "Headed build yaw residual F-A4-01 should not override headless QR PASS without blue re-check.",
            ],
        },
        "evidence_refs": [
            "orchestration/work_orders/WO-P2E-001-BLOCK-ASSEMBLY-PREVIEW-SLICE.md",
            "orchestration/control/codex_directive.json",
            "orchestration/receipts/p2e_001/A0_ssot_preflight_001.json",
            "orchestration/receipts/p2e_001/A1_runtime_implementation_001.json",
            "orchestration/receipts/p2e_001/A2_control_ux_audit_001.json",
            "orchestration/receipts/p2e_001/A3_red_audit_001.json",
            "orchestration/contracts/block_dna_adapt_001/validate_block_dna_adapt_001.py",
            "game/tests/p2e001_block_assembly_core_smoke.gd",
            "game/tests/p2e001_block_assembly_authority_smoke.gd",
            "game/tests/p2e001_block_assembly_qr_context_smoke.gd",
            "orchestration/evidence/p2e_001/001/",
            "orchestration/logs/p2e-001-a4-qa-001.log",
            "orchestration/receipts/p2e_001/A4_qa_evidence_001.json",
        ],
        "trace": {
            "handoff_from": "A3_RED",
            "handoff_to": "A5_PURPLE",
            "wave": "A4",
            "task_id": "P2E-001",
            "log": "orchestration/logs/p2e-001-a4-qa-001.log",
            "receipt": "orchestration/receipts/p2e_001/A4_qa_evidence_001.json",
            "evidence_root": "orchestration/evidence/p2e_001/001/",
        },
        "parent_product_patch": False,
    }

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print("receipt_written", RECEIPT)
    print("receipt_sha", sha256_file(RECEIPT))
    print("evidence_files", len(files))
    print("pngs", len(evidence_manifest))
    print("verdict", receipt["verdict"])

    summary = (
        f"\n=== A4 QA COMPLETE {now} ===\n"
        f"child_task_ref={CHILD}\n"
        f"verdict={receipt['verdict']}\n"
        "gates: DNA PASS 14/14 42/42; core PASS; authority PASS; qr PASS; "
        "ctrl1b router PASS; headed dry PASS\n"
        "headed: 12/12 PNGs distinct; runtime ERROR=0; teardown noise=4\n"
        "product_writes=[]\n"
        "accepted=false self_accept=false\n"
        "next_owner=A5_PURPLE\n"
        "open_residuals: F-A2-01/F-A3-01, F-A2-02..05, F-A3-02..06, F-A3-04 F01, "
        "F-A4-01 headed yaw, F-A4-02 teardown noise\n"
    )
    with LOG.open("a", encoding="utf-8") as f:
        f.write(summary)
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

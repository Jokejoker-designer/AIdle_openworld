# UCBV-001 Fresh C4 Strict QA Rerun 009

## Binding

- Directive 94 only; exact coordinator parent `019f7ffd-3995-71c0-aca1-51078e24a852`.
- One fresh installed `aidle-worldgen-qa-evidence` child only; TrustLayer `purple-team-finding-triage`; UI `ui-a11y-auditor`; authority `VERIFY_ONLY`.
- `accepted=false`, `self_accept=false`, no product writes, no C5/P2E-002, no grandchildren/support profiles.

## Exact lease

- Receipt: `orchestration/receipts/ucbv_001/correction_008/C4R_qa_evidence_008.json`
- Log: `orchestration/logs/ucbv_001/correction_008/C4R_qa_evidence_008.log`
- Fresh headed evidence only: `orchestration/evidence/ucbv_001/008/**`

Do not alter any product/test file, any prior correction/evidence, motion-kit staging, task/directive/review/journal files, or runtime configuration.

## Required independent QA

Run the strict C4 matrix from normal Main runtime. Require zero ERROR/USER ERROR/SCRIPT ERROR/parse/missing-resource/RID leak lines in all submitted stdout/stderr. Capture fresh headed proof at both required resolutions for the Manual Build catalog (including more than `anchor_door_round`), Q/R rotate, elevation, confirm/cancel, delete red-X selection/confirm/cancel, and Nori-7. Nori proof must visibly identify the actual production GLB runtime path (`character_id=CCP-RH-001`, `bones=14`, `mode=glb_c1r`), not a staging SVG or an assertion-only claim.

Run and log:

1. `h1_consolidation_flow_smoke.gd` — PASS checks=13.
2. `ucbv_001_inputmap_e2e_smoke.gd` — PASS checks=17 inputs=34.
3. `ucbv_001_navigation_warning_smoke.gd` — PASS checks=16 and zero C3-F01 signatures.

The motion kit is a read-only staging input only. It must validate green if mentioned, but it cannot substitute for real keyed runtime animation or claim asset creation. Submit schema-valid MAF receipt, exact lineage, all PNG paths/hashes/dimensions, `REVIEW_REQUESTED`, `accepted=false`, and `self_accept=false`. C5 remains forbidden until Codex accepts fresh C4.

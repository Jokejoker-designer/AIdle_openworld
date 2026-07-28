# UCBV-001 C4-F01R Receipt Lineage Correction 008

## Authority and binding

- Directive 93 only; exact coordinator parent `019f7ffd-3995-71c0-aca1-51078e24a852`.
- One fresh installed `aidle-worldgen-godot-runtime` child only; TrustLayer `blue-team-p0-remediator`; UI `ui-app-dashboard`; authority `PATCH_DRAFT`.
- `accepted=false`, `self_accept=false`; no grandchildren, no support profiles and no C4, C5 or P2E-002 dispatch.

## Exact lease

- Receipt only: `orchestration/receipts/ucbv_001/correction_007/C4F01R_lineage_correction_007.json`
- Log only: `orchestration/logs/ucbv_001/correction_007/C4F01R_lineage_correction_007.log`

Do **not** edit product/test files, the immutable `correction_006` receipt/log, prior evidence, directives, tasks, reviews, journal, or any other file.

## Required proof

The rejected receipt in correction_006 declares a non-durable UUID. Create a new schema-valid MAF receipt with this fresh child's own real durable child UUID in **all** of `child_task_ref`, `transcript_ref`, and `writer_transcript_ref`. Its log must include the literal actual UUID, current parent UUID, the SHA-256/bytes of the unchanged test file, and the literal command/exits/PASS markers for three fresh runs:

1. `h1_consolidation_flow_smoke.gd`: PASS checks=13, exit 0, zero ERROR/USER ERROR/SCRIPT ERROR/parse/missing-resource/RID leak lines.
2. `ucbv_001_inputmap_e2e_smoke.gd`: PASS checks=17 inputs=34, exit 0, zero strict signatures.
3. `ucbv_001_navigation_warning_smoke.gd`: PASS checks=16, exit 0, zero C3-F01 signatures.

Record `product_writes=[]`, exact lease self-audit, `REVIEW_REQUESTED`, `accepted=false`, and `self_accept=false`. Do not claim the old receipt became valid, do not self-accept, and do not start C4/C5.

# UCBV-001 C4 Schema-Valid Fresh QA Rerun 010

## Binding and authority

- Directive 95 only; exact coordinator parent `019f7ffd-3995-71c0-aca1-51078e24a852`.
- One fresh installed `aidle-worldgen-qa-evidence` child only; TrustLayer `purple-team-finding-triage`; UI `ui-a11y-auditor`; `VERIFY_ONLY`.
- `accepted=false`, `self_accept=false`; no product writes, no C5/P2E-002/grandchildren/support profiles.

## Exact lease

- Receipt: `orchestration/receipts/ucbv_001/correction_009/C4S_qa_evidence_009.json`
- Log: `orchestration/logs/ucbv_001/correction_009/C4S_qa_evidence_009.log`
- Evidence only: `orchestration/evidence/ucbv_001/009/**`

Never alter product/test/configuration/motion kit, correction_008 or earlier evidence/receipts/logs, directives, tasks, reviews, journal, or handoffs.

## Blocking correction

The prior C4R receipt is invalid because `evidence_refs` is an object. This fresh receipt must pass `E:/standards/maf/schemas/agent_step_contract.schema.json` **before submission**. `evidence_refs` must be an array of strings. If named evidence metadata is needed, put it under an additive `evidence_index` field; do not replace the required array.

## Fresh C4 proof (no reuse of correction_008 evidence)

Capture fresh dual-resolution headed normal-runtime proof under `evidence/009`: multi-module manual-build catalog, Q/R camera-yaw invariant, elevation, confirm/cancel, delete red-X select/confirm/cancel, and actual Nori-7 GLB runtime marker (`CCP-RH-001`, 14 bones, `glb_c1r`, non-procedural). Run H1 `PASS checks=13`, InputMap `PASS checks=17 inputs=34`, and navigation `PASS checks=16`; all logs need zero strict error and C3-F01 warning signatures.

Record the fresh child's actual durable UUID identically in child/transcript/writer refs, all PNG hashes/dimensions, schema-validation command and exit 0, `REVIEW_REQUESTED`, `accepted=false`, and `self_accept=false`. C5 remains forbidden.

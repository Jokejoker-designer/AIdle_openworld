# UCBV-001 C4-F01 H1 Flow Zero-Error Correction 007

## Authority and binding

- Directive 92 only; parent `019f7ffd-3995-71c0-aca1-51078e24a852` coordinator-only.
- One fresh installed `aidle-worldgen-godot-runtime` child only.
- TrustLayer `blue-team-p0-remediator`; UI `ui-app-dashboard`; authority `PATCH_DRAFT`.
- `accepted=false`, `self_accept=false`, no grandchildren, no C4/C5/P2E-002.

## Exact lease

- Product/test: `game/tests/h1_consolidation_flow_smoke.gd`
- Receipt: `orchestration/receipts/ucbv_001/correction_006/C4F01_h1_flow_zero_error_006.json`
- Log: `orchestration/logs/ucbv_001/correction_006/C4F01_h1_flow_zero_error_006.log`

No other writes, helper/debug files, product changes, evidence changes, provenance changes, dependency work, network, shipping, or acceptance.

## Required correction and proof

At line 196 the test invokes GDScript's nonexistent `bool` constructor on a Variant. Make the narrow typed conversion compatible with Godot 4.3 while preserving the actual Build-R preview-only assertion. Do not weaken or skip an assertion.

Run `h1_consolidation_flow_smoke.gd` and require exit 0, its existing PASS marker, and zero `ERROR`, `USER ERROR`, `SCRIPT ERROR`, parse/missing-resource and RID leak lines. Also run `ucbv_001_inputmap_e2e_smoke.gd` and `ucbv_001_navigation_warning_smoke.gd`; preserve their markers and zero C3-F01 signatures.

Record literal commands, exits and unfiltered stdout/stderr in the leased log. Submit a schema-valid MAF receipt binding the real child UUID, hashes/bytes, self-audit and `REVIEW_REQUESTED` for Codex. Do not dispatch C4 rerun or C5.

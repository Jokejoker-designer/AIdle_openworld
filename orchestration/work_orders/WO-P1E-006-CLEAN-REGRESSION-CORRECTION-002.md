# WO-P1E-006-CLEAN-REGRESSION-CORRECTION-002

Authority: scoped `PATCH_DRAFT` + `VERIFY_ONLY` · State: `READY`

Issued by Codex under Directive 53. Close only findings F05–F08 in
`orchestration/reviews/CODEX_P1E-006_REVIEW_002.json`. Preserve every original
receipt, screenshot and failed/error-bearing log. P1E-006 remains unaccepted.

## Global workflow

- Use only Grok Desktop parent `019f7ffd-3995-71c0-aca1-51078e24a852`.
- Parent is coordinator-only. Exactly four real installed children run
  sequentially with at most one active child.
- No grandchildren, support profiles, Grok CLI or other top-level session.
- Exact TrustLayer/UI character binding, five mandatory skills plus routed
  skills, one writer per file, durable transcript/meta evidence and
  schema-valid agent-step receipts are mandatory.
- A test is clean only when exit is zero, its expected PASS marker exists, and
  the complete combined output has zero `ERROR:`, `SCRIPT ERROR`, parse or
  compile errors. Do not filter, relabel or waive error lines.

## R0 — Asset clean-renderer correction

Profile: `aidle-worldgen-asset-art` · Authority: `PATCH_DRAFT`.

Diagnose and fix the underlying `Parameter "m" is null` calls seen in the
P1E-006 variant smoke and P1E-002 intake/save-reload suite. The likely surface
is invalid or renderer-dependent MeshInstance3D material enumeration. Guarding
must be semantic: verify resource/instance validity and use APIs safe for the
headless dummy renderer. Do not suppress stderr or modify the test harness to
ignore the error.

Exclusive product/test allowlist:

- `game/scripts/modules/asset/world_profile_variant_selector.gd`
- `game/scripts/modules/asset/glb_intake.gd`
- `game/tests/p1e006_world_profile_variants_smoke.gd`
- `game/tests/p1e002_glb_intake_tests.gd`

Exclusive evidence writes:

- `orchestration/receipts/p1e/P1E_006_clean_r0_asset_003.json`
- `orchestration/logs/p1e-006-clean-r0-asset-003.log`

R0 must run both affected suites and report zero error lines.

## R1 — Persistence and clean-boot verification

Profile: `persist` · Authority: `VERIFY_ONLY`.

Run real, non-skipped commands for:

- `game/tests/p1e004_elemental_pilot_smoke.gd` including
  `persist_static_and_dynamic_state`;
- `game/tests/p1e002_glb_intake_tests.gd` including
  `save_reload_no_duplicate`;
- a clean Godot 4.3 project boot.

All exits and PASS markers must be present and all outputs must be error-clean.

Exclusive writes:

- `orchestration/evidence/p1e_006_clean_003/**`
- `orchestration/receipts/p1e/P1E_006_clean_r1_persist_003.json`
- `orchestration/logs/p1e-006-clean-r1-persist-003.log`

## R2 — Independent QA regression

Profile: `aidle-worldgen-qa-evidence` · Authority: `VERIFY_ONLY`.

Re-run P1E-006 variants, HSL, P1E-003, P1E-004 art-style, P1E-004 elemental,
P1E-002 intake/save-reload, fence collision, input collision and clean boot.
Re-hash and inspect the existing two headed screenshots; recapture only if the
asset fix changes visual output. Fail on any skipped command, missing marker,
nonzero exit or error line.

Exclusive writes:

- `orchestration/receipts/p1e/P1E_006_clean_r2_qa_003.json`
- `orchestration/logs/p1e-006-clean-r2-qa-003.log`

## R3 — Fresh Purple gate

Profile: `aidle-worldgen-purple-acceptance` · Authority: `VERIFY_ONLY`.

Review R0–R2, exact writer leases, durable child metadata and all raw outputs.
The prior Purple receipt is not acceptance evidence. Return VERIFIED only when
F05–F08 are closed without error filtering or skipped work.

Exclusive writes:

- `orchestration/receipts/p1e/P1E_006_clean_r3_purple_003.json`
- `orchestration/logs/p1e-006-clean-r3-purple-003.log`

## Hard stops

No acceptance, P2E–P6E, art waves 2–4, Control, Character Foundry, network,
shipping, dependency installation, Godot version change, credentials, live
provider/public network, push, deploy or publish. Return
`REVIEW_REQUESTED / WAITING_CODEX` with all four real child refs.

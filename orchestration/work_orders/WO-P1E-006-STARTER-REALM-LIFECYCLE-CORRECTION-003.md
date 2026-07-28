# WO-P1E-006-STARTER-REALM-LIFECYCLE-CORRECTION-003

Authority: scoped `PATCH_DRAFT` + `VERIFY_ONLY` | State: `READY`

Issued by Codex under Directive 54. Close only F08-F10 in
`orchestration/reviews/CODEX_P1E-006_REVIEW_003.json`. Preserve all prior
receipts, screenshots, failed logs and the R3 out-of-lease `_r3_*` artifacts as
rejected evidence. P1E-006 remains unaccepted.

## Global workflow

- Use only Grok Desktop parent `019f7ffd-3995-71c0-aca1-51078e24a852`.
- Parent is coordinator-only. Exactly three real installed children run
  sequentially with at most one active child.
- No grandchildren, support profiles, Grok CLI or another top-level session.
- Every child must load its installed profile, exact TrustLayer/UI character,
  all five mandatory skills from `skills_manifest.yaml`, routed skills and the
  MAF schema fully to EOF.
- One writer per file. Commands, exits, complete unfiltered output, durable
  child reference and declared files must match reality.
- A suite passes only with exit zero, expected marker and zero `ERROR:`,
  `SCRIPT ERROR`, parse or compile lines.

## L0 - Asset lifecycle correction

Profile: `aidle-worldgen-asset-art`; TrustLayer:
`blue-team-p0-remediator`; UI: `ui-color-type-specialist`; authority:
`PATCH_DRAFT`.

Diagnose the exact residual dummy-renderer mesh owner. Implement a product-owned
headless-safe Starter Realm rebuild/teardown lifecycle. The fix must clear or
detach invalid presentation mesh resources before freeing the realm and must be
safe for both GLB and procedural paths. Do not merely filter logs, suppress
stderr, weaken tests, or add test-only cleanup that production does not use.

Exclusive product/test allowlist:

- `game/scripts/modules/asset/starter_realm_builder.gd`
- `game/scripts/modules/asset/glb_intake_runtime_builder.gd`
- one new lifecycle helper under `game/scripts/modules/asset/` only if required
- `game/tests/p1e003_density_exposure_smoke.gd` only for assertions against the
  product lifecycle; no error suppression
- `game/tests/g8_ux002_fence_rail_collision_smoke.gd` only for assertions
  against the product lifecycle; no error suppression

Exclusive evidence writes:

- `orchestration/receipts/p1e/P1E_006_lifecycle_l0_asset_004.json`
- `orchestration/logs/p1e-006-lifecycle-l0-asset-004.log`

Run both affected suites plus P1E-006 variants and P1E-002 intake. All four must
be error-clean. Return `REVIEW_REQUESTED`, `accepted=false`, `self_accept=false`.

## L1 - Independent QA matrix

Profile: `aidle-worldgen-qa-evidence`; TrustLayer:
`purple-team-finding-triage`; UI: `ui-a11y-auditor`; authority: `VERIFY_ONLY`.

Run the complete Directive-53 matrix: P1E-006 variants, HSL demo, P1E-003
density, P1E-004 art style, P1E-004 elemental persistence, P1E-002 intake and
save/reload, G8 UX-002 fence, G8 input/collision and a real clean boot. Re-hash
the two existing headed profile screenshots; do not recapture unless the patch
changes headed presentation. No product writes and no skipped command.

Exclusive writes:

- `orchestration/receipts/p1e/P1E_006_lifecycle_l1_qa_004.json`
- `orchestration/logs/p1e-006-lifecycle-l1-qa-004.log`

Embed all raw command output in the declared log instead of creating undeclared
temporary files. Return `REVIEW_REQUESTED`, `accepted=false`,
`self_accept=false`.

## L2 - Fresh Purple and lease audit

Profile: `aidle-worldgen-purple-acceptance`; TrustLayer:
`purple-team-release-gate`; UI: `ui-visual-critic`; authority: `VERIFY_ONLY`.

Review L0-L1 and independently rerun at least the two formerly failing suites,
P1E-006 variants, P1E-002 intake and clean boot. Verify F08-F10, including exact
writer leases and the fact that all previous `_r3_*` files remain preserved but
are not acceptance evidence. Purple may not patch or accept.

Exclusive writes:

- `orchestration/receipts/p1e/P1E_006_lifecycle_l2_purple_004.json`
- `orchestration/logs/p1e-006-lifecycle-l2-purple-004.log`

Do not create temporary scripts/logs outside the two-file lease; embed raw
output in the declared log. Return `WAITING_CODEX`, `accepted=false`,
`self_accept=false`.

## Hard stops

No P2E-P6E, later art waves, Control, Character Foundry, network, shipping,
dependency installation, Godot version change, credential, live provider,
public network, push, deploy or publish. Red F01 remains a hard network/shipping
blocker.

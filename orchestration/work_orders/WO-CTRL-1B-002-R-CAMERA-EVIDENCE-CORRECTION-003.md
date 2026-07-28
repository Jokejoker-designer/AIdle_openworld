# WO-CTRL-1B-002-R-CAMERA-EVIDENCE-CORRECTION-003

Authority: `VERIFY_ONLY` | State: `READY`

Codex independently confirms the Human R-camera behavior and all relevant
runtime regressions pass. Machine acceptance is held only because the original
R1 and P3 Directive-60 receipts omit the MAF-required top-level `smoke_test`.
Preserve those receipts as immutable historical evidence. This work order is
evidence-only and authorizes no product/test/contract/fixture edits.

## E0 - R1 verification receipt correction

Profile: `aidle-worldgen-control-input`; TrustLayer:
`blue-team-p0-remediator`; UI: `ui-a11y-auditor`; authority reduced to
`VERIFY_ONLY`.

Fresh child. Re-run the amended contract validator, context-router smoke,
integration smoke and R witness/hash checks without editing product or tests.
Write a new schema-valid append-only receipt with a real top-level `smoke_test`,
real durable child ID, exact commands/exits, hashes, `product_writes=[]`,
`accepted=false` and `self_accept=false`. Explicitly identify the original R1
receipt as invalid because `smoke_test` was missing.

Exclusive writes:

- `orchestration/receipts/control/CTRL_1B_002_e0_r1_receipt_correction_004.json`
- `orchestration/logs/ctrl-1b-002-e0-r1-receipt-correction-004.log`

## E1 - Purple verification receipt correction

Profile: `aidle-worldgen-purple-acceptance`; TrustLayer:
`purple-team-release-gate`; UI: `ui-visual-critic`; authority: `VERIFY_ONLY`.

Fresh child after E0. Re-run the decisive validator, real R-path/control smoke,
no-dual-fire and lineage checks. Write a new schema-valid append-only Purple
receipt with top-level `smoke_test`. Verify E0, S0/Q2 valid receipts, the two
historical invalid receipts and immutable prior evidence. Purple never patches
or accepts.

Exclusive writes:

- `orchestration/receipts/control/CTRL_1B_002_e1_purple_receipt_correction_004.json`
- `orchestration/logs/ctrl-1b-002-e1-purple-receipt-correction-004.log`

## Workflow and hard stops

- Same sole Desktop parent `019f7ffd-3995-71c0-aca1-51078e24a852`, coordinator-only.
- Exactly two fresh real children E0 -> E1, sequential, one active child. No
  resume/follow-up/grandchild/extra profile.
- Load exact characters and five mandatory skills plus routed skills. One
  writer per exclusive file. Use real durable lineage; never invent refs.
- No edits outside the four exclusive evidence files. In particular, no edits
  to product, tests, Control contract/fixtures, Directive-60 receipts, Character
  Foundry, Scene 2, World 2, persistence, World Commit or network.
- No dependency install, Godot change, credential, live provider, public
  listener, push, deploy or publish.
- Parent returns `REVIEW_REQUESTED` / `WAITING_CODEX`, accepted=false.

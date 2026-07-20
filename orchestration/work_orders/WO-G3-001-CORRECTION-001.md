# Work Order — G3-001 Revision Binding Correction 001

Authority: one `PATCH_DRAFT` executor writer; all other agents `VERIFY_ONLY`.
Final acceptor: Codex.
Parent: the existing Grok Desktop conductor session only.

## Required installed-subagent sequence

1. `schema` verifies the live Snapshot → World Prompt → Commit Request revision
   invariant and returns a step contract without product writes.
2. `executor` is the sole product writer and fixes the transaction plus tests.
3. `persist` verifies complete/cancel/undo receipt honesty without product writes.
4. `network` performs the final Purple authority review without product writes.

No other profile or top-level session is needed for this bounded correction.

## Corrections

- Bind `world_prompt.target.expected_world_revision`,
  `commit_request.expected_world_revision`, and the complete receipt's
  `expected_world_revision` to the loaded live snapshot revision (`3` in the
  current fixture). A stale builder default must never override live context.
- Add a negative/contrast assertion so the smoke fails if revision `0` leaks
  into the handoff while the snapshot revision is `3`.
- Build cancel receipt collision/orphan fields from the actual cancellation
  payload or measured preview result, not unconditional constants. Add a test
  that would fail if runtime evidence is ignored.
- Preserve the existing World Commit rejected stub, no durable mutation,
  explicit confirm, four manifestation stages, and complete/cancel/undo paths.

## Write scope

- `game/scripts/modules/executor/g3_onboarding_slice.gd`
- `game/scripts/modules/executor/g3_e2e_smoke.gd`
- `game/scripts/modules/executor/exports/g3_*.json`
- If strictly required for revision context only:
  `game/scripts/modules/companion/companion_module.gd` and
  `game/scripts/modules/companion/world_prompt_builder.gd`
- G3 correction receipts/review artifacts and `grok_status.json`

Do not edit tasks, directives, architecture, contracts, original work orders or
unrelated modules. Do not create acceptance files or mark G3 accepted.

## Acceptance evidence

- Clean `G3_E2E_SMOKE=PASS` with explicit revision-equality and runtime-derived
  cancel evidence checks.
- `AIDLE_VALIDATION=PASS`.
- Valid MAF receipts for schema, executor, persist and network/Purple.
- No writer conflict and no canonical durable mutation.

Finish `REVIEW_REQUESTED`, update `grok_status.json`, then wait for Codex.

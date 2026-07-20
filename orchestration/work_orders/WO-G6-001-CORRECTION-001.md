# Work Order — G6-001 Correction 001

Final acceptor: Codex. Continue only in the existing Grok Desktop parent.

## Installed-subagent workflow

1. `schema` (`VERIFY_ONLY`) records the confirmation state-machine invariant.
2. `network` (`PATCH_DRAFT`) is sole writer under
   `services/world_authority_poc/**`.
3. `executor` (`PATCH_DRAFT`) is sole writer under
   `game/scripts/modules/network/**`.
4. `persist` (`VERIFY_ONLY`) proves rejected bypass attempts leave revision,
   entity hash, entity count, outbox and receipts unchanged.
5. `core` (`VERIFY_ONLY`) performs the final Purple review and integrated gates.

One writer per file, schema-valid `agent_step_contract` per significant step,
no nested grandchildren and no self-acceptance.

## Mandatory correction

- `submit_proposal` must never accept a client-supplied
  `confirmation.state=confirmed` as an authoritative confirmation.
- Fail closed with a structured non-retryable rejection before proposal
  registration, revision change, entity mutation, event emission or receipt
  creation. Do not silently treat the supplied state as confirmed.
- A valid proposal enters `pending`. Only the explicit, session-bound
  `confirm_proposal` method may transition that registered proposal to
  `confirmed` and bind `confirmed_by` plus the current server revision.
- `commit` must continue rejecting pending, missing or forged confirmation.
- Apply the same rule to Python authority and the GDScript local mirror.
- Do not weaken existing actor/client/owner, schema, revision, idempotency,
  receipt or replay checks.

## Required evidence

- Python regression: submit a schema-valid prompt carrying
  `state=confirmed/confirmed_by=player_a`; verify rejection, zero proposal
  authority, revision/hash/entity/outbox unchanged, and direct commit rejected.
- Godot headless regression for the same exploit with identical state invariants.
- Existing 19 server tests and 12 two-client checks remain green, with the new
  regression count reported explicitly.
- Clean integrated Godot boot, validator, secret/public-bind scans, schema-valid
  MAF receipts, ownership map and Purple review.

This remains a deterministic local POC. Do not select Nakama/Colyseus, add a
listener/dependency/credential, edit tasks/directive/architecture/contracts or
prior receipts/work orders, push, deploy or publish. Finish
`REVIEW_REQUESTED`/`WAITING_CODEX`, update only `grok_status.json`, and wait.

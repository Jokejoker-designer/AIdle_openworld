# Work Order — G4-001 Runtime and Signed-Journal Correction 001

Final acceptor: Codex.
Parent: the existing Grok Desktop conductor session only.

## Installed-subagent sequence and ownership

1. `schema` (`VERIFY_ONLY`) defines the signed/tamper-evident journal invariant.
2. `persist` (`PATCH_DRAFT`) is sole writer for journal integrity, PersistModule
   consumer API and persistence tests.
3. `core` (`PATCH_DRAFT`) is sole writer only for the existing runtime mount file
   needed to replace `AgentPersistStub` with `PersistModule`.
4. `executor` (`VERIFY_ONLY`) tests the offline consumer gate and confirms G3's
   rejected World Commit stub cannot be journaled automatically.
5. `network` (`VERIFY_ONLY`) performs Purple authority review.

No profile may write another profile's files. No nested grandchildren.

## Required corrections

### Signed local journal integrity

- Use built-in Godot cryptography only; no dependency installation.
- Apply an HMAC-SHA256 integrity seal or equivalently keyed chain over canonical
  journal entries, including previous-entry linkage and revision.
- Obtain the device-local key through an injected/local key-provider boundary.
  Never hardcode a production key or treat it as an API credential.
- Smoke may inject a deterministic test key, clearly marked test-only.
- Fail closed on wrong key, modified entry, removed entry, reordered entry,
  broken previous hash, or invalid seal.
- State clearly that a local seal is reconciliation evidence, not canonical
  Shared District/server authority.

### Runtime integration

- Integrated boot must register a real `PersistModule` in the `persist` slot,
  not `AgentPersistStub`, while preserving clean 2.5D startup.
- Expose a consumer method that accepts only explicit
  `offline_private_reality` local operations with confirmed authority metadata.
- G3 rejected handoff (`world_commit_invoked=false`,
  `durable_mutation_applied=false`) must not auto-journal as committed.
- Online Private Reality, Shared District, economy and ownership mutations must
  be rejected or routed to server World Commit—not local persistence.

## Preserve

- Existing deterministic hash, replay idempotency, revision conflict,
  compensation append-only and malformed-journal behaviors.
- G3 revision chain remains `3` at the handoff.

## Allowed product writes

- `game/scripts/modules/persist/**`
- `game/scripts/modules/interfaces/i_persist_module.gd`
- The minimum existing core/stub mount file claimed exclusively by `core`
- G4 correction tests/exports

Do not edit tasks, directive, architecture, contracts or prior work orders.
No DB, API SDK, credential upload, push or deploy.

## Acceptance evidence

- Persist smoke includes integrity tamper/wrong-key/reorder/removal tests.
- Integrated boot proves PersistModule mounted and log is clean.
- Consumer-gate tests prove rejected G3 and online/shared operations cannot be
  local-journaled.
- Validator PASS, MAF receipts, ownership map and Purple review.

Finish `REVIEW_REQUESTED`, update only `grok_status.json`, then wait for Codex.

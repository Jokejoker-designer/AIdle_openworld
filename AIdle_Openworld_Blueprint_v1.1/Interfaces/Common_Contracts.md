# Common Contracts

- World proposal: `contracts/world_prompt.schema.json`.
- Commit request: `contracts/commit/commit_request.schema.json` (World Commit service only).
- Commit receipt: `contracts/commit/commit_receipt.schema.json` (request ID, old/new revision, entity IDs, artifact hashes and status; also idempotent_replay, rejected, conflicted).
- Commit policy: `contracts/commit/commit_policy.md`.
- Event envelope: `contracts/events/event_envelope.schema.json`.
- Provenance: append-only lineage; corrections append a new record.
- Style Profile: versioned world-level tokens with per-object bounded overrides.
- Asset receipt: generator/version/license/input hash/output hash/QA status.
- Agent step: `E:\standards\maf\schemas\agent_step_contract.schema.json`.
- Companion profile: `contracts/personality_profile.schema.json`.

All contracts reject unknown fields and use semantic versions. Breaking changes
require a migration and consumer-contract tests before acceptance.

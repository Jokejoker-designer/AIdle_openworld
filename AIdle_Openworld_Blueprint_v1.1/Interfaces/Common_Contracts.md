# Common Contracts

- World proposal: `contracts/world_prompt.schema.json`.
- Commit receipt: request ID, old/new revision, entity IDs, artifact hashes and status.
- Provenance: append-only lineage; corrections append a new record.
- Style Profile: versioned world-level tokens with per-object bounded overrides.
- Asset receipt: generator/version/license/input hash/output hash/QA status.
- Agent step: `E:\standards\maf\schemas\agent_step_contract.schema.json`.
- Companion profile: `contracts/personality_profile.schema.json`.

All contracts reject unknown fields and use semantic versions. Breaking changes
require a migration and consumer-contract tests before acceptance.

# Structured World Prompt Spec v1.1

The canonical machine contract is `../contracts/world_prompt.schema.json`.
Markdown examples never override it.

## Required semantic sections

- identity/version: prompt, request and schema IDs;
- actor/session: player, Companion and authority context;
- operation: create, modify, delete, enrich or gift proposal;
- target: space, chunk, entity and expected world revision;
- style profile and geometry/entity recipe;
- manifestation stages and timing budget;
- interaction/collision/navigation requirements;
- compute/content/policy budgets;
- provenance and parent lineage;
- preview, confirmation and rollback policy.

## Transaction rules

- `request_id` is the idempotency key.
- `expected_world_revision` prevents lost updates.
- Delete, public publish, paid generation and marketplace actions require HITL.
- `custom` styles require a referenced, validated Style Profile.
- Stage order is fixed and cannot be supplied in reverse.
- Unknown properties fail validation.


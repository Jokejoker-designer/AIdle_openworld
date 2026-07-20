# AI Game Master contracts

Machine contracts live under `contracts/agm/`:

- World State Snapshot schema: `contracts/agm/world_state_snapshot.schema.json`
- AGM Decision Envelope schema: `contracts/agm/decision_envelope.schema.json`
- Valid fixtures: `contracts/fixtures/agm/valid/`
- Adversarial invalid fixtures: `contracts/fixtures/agm/invalid/`
- Policy fixtures (edition identity, replay, stale snapshot): `contracts/fixtures/agm/policy/`

Snapshot fields include schema version, snapshot ID, edition mode, latest
player action, bounded player/world/quest/Companion state, art style,
progression phase and the last execution receipt. Sensitive fields are forbidden.

Decision fields include schema version, decision ID, source snapshot ID,
dialogue, quest operations, build proposals, allowlisted event proposals,
bounded mood/relationship deltas, next trigger and trace metadata. Unknown
fields and arbitrary code or scripts are rejected.

Build proposals are not durable mutations. Every build proposal keeps
`preview_required: true`, `confirmation_state: pending`, and
`routes_through: preview_confirm_commit` so Structured World Prompt preview,
player confirmation and World Commit remain mandatory.

Transport adapters may add delivery metadata outside the hashed payload but
cannot alter payload semantics. Free Desktop Bridge (`desktop_bridge_free`) and
Paid API (`api_paid`) use identical payload semantics; only the `edition` field
(and optional non-authoritative `transport` metadata on snapshots) may differ.

Runtime policy (enforced by the decision executor and checked in
`scripts/validate_project.py`):

- Replayed `decision_id` is rejected.
- Decision `source_snapshot_id` must equal the live snapshot ID or is stale-rejected.
- Excessive mood/relationship deltas, unknown event types, secrets, TTS/voice
  payloads and direct durable mutation fields are schema-invalid.

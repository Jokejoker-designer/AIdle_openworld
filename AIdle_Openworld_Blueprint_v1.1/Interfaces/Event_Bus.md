# Event Bus v1.1

Machine contract: `contracts/events/event_envelope.schema.json`.

Events use an envelope: `event_id`, `event_type`, `event_version`, `occurred_at`,
`request_id`, `space_id`, `world_revision`, `actor_id`, `payload`, `trace_id`.

Core events:

- `world.proposal_validated|rejected`
- `world.preview_started|cancelled`
- `manifestation.stage_changed|completed|failed`
- `world.mutation_committed|compensated|conflicted`
- `asset.requested|conditioned|rejected`
- `companion.mood_expression_changed|gift_proposed`
- `social.visit_requested|accepted|denied`

Consumers are idempotent by `event_id`. The transactional outbox publishes only
after commit. Payloads do not contain raw prompts, secrets or private memories.


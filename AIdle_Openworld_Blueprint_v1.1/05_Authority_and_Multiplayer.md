# Authority and Multiplayer

## Rule

Clients render and predict. AI proposes. The authoritative service validates and
commits every durable online mutation.

## Commit middleware

Authentication -> authorization -> schema -> content moderation -> quota/cost ->
ownership -> spatial bounds -> collision/nav feasibility -> revision check ->
preview receipt -> confirmation -> atomic commit -> event/outbox.

## Conflict handling

- Optimistic concurrency uses `expected_world_revision`.
- Duplicate `request_id` returns the prior receipt.
- Competing edits fail with a conflict diff; they are never silently merged.
- Cancellation before commit removes preview only.
- Undo creates a compensating mutation; history is not erased.

## HITL boundaries

Required for destructive edits, public publishing, paid compute, marketplace
listing/purchase, external data upload, real-city licensing and production deploy.


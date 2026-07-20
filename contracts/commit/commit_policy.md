# Commit authority policy (machine-checkable companion)

Status: ACTIVE · Contract version: commit 1.0.0 · Product lock: server-authoritative durable state

This document accompanies:

- `contracts/commit/commit_request.schema.json`
- `contracts/commit/commit_receipt.schema.json`
- `contracts/events/event_envelope.schema.json`

## Authority rule

Clients render and predict. AI proposes. Only the **World Commit service**
validates and commits durable online mutations (`authority.commit_path` =
`world_commit_service`).

| Attempt | Outcome |
|---|---|
| Server-authoritative commit request (schema-valid) | Eligible for commit middleware |
| `source: client_authoritative` or client-forged durable path | **Schema-invalid** against commit_request |
| Client durable mutation accepted by client runtime | **Forbidden**; no durable ownership/economy/inventory |
| Offline Private Reality local journal | Local signed journal only; durable reconcile via `offline_journal_reconcile` on sync |

## Idempotency

- `request_id` is the idempotency key (UUID).
- A duplicate `request_id` **must not** re-apply the mutation.
- The service returns a receipt with `status: idempotent_replay`, same
  `request_id`, `idempotency.replayed: true`, and
  `idempotency.prior_receipt_id` equal to the original `receipt_id`.
- Fixtures: `contracts/fixtures/commit/valid_committed_receipt.json` +
  `valid_idempotent_replay_receipt.json` (+ pair check in validator).

## Revision conflict

- Request carries `expected_world_revision`.
- If current server revision ≠ expected, return `status: conflicted` with
  `conflict.code: revision_mismatch` and both expected/actual revisions.
- Competing edits are never silently merged.
- Fixture: `contracts/fixtures/commit/valid_revision_conflict_receipt.json`.

## Client-forged / client-authoritative rejection

- Invalid request fixture
  `contracts/fixtures/commit/invalid_client_forged_durable_request.json`
  **must fail** `commit_request.schema.json`.
- Valid rejection receipt fixture
  `contracts/fixtures/commit/valid_client_forged_rejection_receipt.json`
  models the service response when policy detects a client-side durable
  mutation attempt (`rejection.code: client_forged` or
  `client_authoritative_durable_forbidden`).

## Outbox

After a successful commit, the transactional outbox publishes an
`event_envelope` (see Event Bus). Events are never world truth by themselves;
canonical state is the commit log + snapshots.

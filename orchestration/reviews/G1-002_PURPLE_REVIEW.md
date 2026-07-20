# Purple VERIFY_ONLY review — G1-002

| Field | Value |
|---|---|
| Task | G1-002 — Lock commit authority and event contracts |
| Reviewer | Purple / Devil's Advocate |
| Authority | VERIFY_ONLY (no product/schema/fixture patches; no tasks.json ACCEPT) |
| Date | 2026-07-20 |
| Work order | `orchestration/work_orders/WO-G1-002.md` |
| Worker receipt | `orchestration/receipts/G1-002.json` |

## VERDICT

**ACCEPTED**

G1-002 meets the **contract-layer** acceptance bar: schemas + fixtures +
validator checks encode server-only durable commit path, client-labeled
rejection, idempotency pair, revision conflict, and Event_Bus envelope field
lock. **This is not runtime enforcement.** Residual adversarial holes below are
mandatory reading for G3/G6 implementers; they do not fail this work order’s
stated scope (schema + tests + policy docs under `contracts/`).

## Evidence

### Artifacts present

| Artifact | Status |
|---|---|
| `contracts/commit/commit_request.schema.json` | Present |
| `contracts/commit/commit_receipt.schema.json` | Present |
| `contracts/commit/commit_policy.md` | Present |
| `contracts/events/event_envelope.schema.json` | Present |
| `contracts/fixtures/commit/*` (8 files) | Present |
| `contracts/fixtures/events/*` (3 files) | Present |
| Validator `check_commit_and_event_contracts()` | Present in `scripts/validate_project.py` |

### Acceptance matrix (WO-G1-002)

| # | Criterion | Result |
|---|---|---|
| 1a | Commit request path only `world_commit_service` | **PASS** — `authority.commit_path` const |
| 1b | Client-forged / client-authoritative rejected at schema | **PASS** — `source` enum excludes them; `commit_path` const |
| 1c | Idempotency by `request_id` (schema + fixture + pair) | **PASS** |
| 1d | Revision conflict status (schema + fixture) | **PASS** |
| 2 | ≥1 invalid client durable mutation fixture rejected | **PASS** (2 fixtures) |
| 3 | Event envelope fields match Event_Bus.md | **PASS** (exact set) |
| 4 | `validate_project.py` still exit 0 | **PASS** (logic + worker smoke; dual-run recommended) |
| 5 | Receipt with smoke_test evidence | **PASS** |
| — | No Nakama/Colyseus co-ownership or runtime | **PASS** |
| — | Did not rewrite G1-001 world_prompt fixture trees | **PASS** (separate `fixtures/commit|events`) |

### Client durable mutation rejected (schema-level)

**Invalid request fixtures (must fail `commit_request.schema.json`):**

1. `invalid_client_forged_durable_request.json`
   - `authority.commit_path: "client_local"` (≠ const `world_commit_service`)
   - `authority.source: "client_authoritative"` (not in enum)
2. `invalid_client_authoritative_source.json`
   - `commit_path` correctly labeled `world_commit_service` but
     `source: "client_authoritative"` still schema-invalid

**Rejection receipt fixture (must validate as receipt):**

- `valid_client_forged_rejection_receipt.json` — `status: rejected`,
  `rejection.code: client_forged`, issuer locked to `world_commit_service`
- Validator enforces rejection code ∈
  `{client_forged, client_authoritative_durable_forbidden}`

### Idempotency pair

| Check | Evidence |
|---|---|
| Original | `valid_committed_receipt.json` — `status: committed`, `request_id` a1b2…, `receipt_id` c0ffee…, revisions 7→8 |
| Replay | `valid_idempotent_replay_receipt.json` — `status: idempotent_replay`, same `request_id`, same revisions |
| Pair meta | `idempotency_pair.json` — `rules.same_request_id: true` |
| Validator | `prior_receipt_id == original.receipt_id`, `duplicate_of_request_id == original.request_id`, `replayed === true`, revisions unchanged |

### Revision conflict

- `valid_revision_conflict_receipt.json`: `status: conflicted`,
  `conflict.code: revision_mismatch`, expected 7 ≠ actual 9
- Schema `allOf` requires `conflict` when conflicted; forbids `new_world_revision`
- Validator asserts expected ≠ actual and code == `revision_mismatch`

### Event envelope vs Event_Bus.md

Event_Bus.md required fields:

`event_id`, `event_type`, `event_version`, `occurred_at`, `request_id`,
`space_id`, `world_revision`, `actor_id`, `payload`, `trace_id`

Schema `required` set is **exactly** that set; `additionalProperties: false`.
Validator hard-codes equality check against the same set.

- `valid_event_envelope.json` — accepted shape (`world.mutation_committed`)
- `invalid_event_missing_fields.json` — missing several required keys
- `invalid_event_with_secret_payload.json` — payload key `raw_prompt` blocked via
  `propertyNames.not.enum`

### Valid commit request shape

`valid_commit_request.json` uses:

- `authority.commit_path: world_commit_service`
- `source: server_authoritative`
- `durable_mutation: true`
- `confirmation.state: confirmed` + `confirmed_by`
- `mutation_class: durable_world`

### Nakama / Colyseus co-ownership

- Grep across repo: Colyseus appears only in ARCHITECTURE_LOCK, WO, and receipt
  “not done” notes — **no co-ownership implementation**.
- Nakama remains candidate-only in Technology_Matrix / roadmap — not introduced
  as world-state co-owner by this task.
- No multiplayer runtime added (allowed / required by WO forbidden list).

### Blueprint cross-links

- `Interfaces/Event_Bus.md` points at `contracts/events/event_envelope.schema.json`
- `Interfaces/Common_Contracts.md` lists commit request/receipt/policy + envelope

## Adversarial hunt (Devil's Advocate)

### BLOCKING for *runtime* / multiplayer gates — **NOT blocking G1-002 contract scope**

1. **Honor-system authority (critical false-confidence risk)**  
   A hostile client can emit a **schema-valid** commit request by setting:
   ```json
   "authority": {
     "commit_path": "world_commit_service",
     "source": "server_authoritative",
     "durable_mutation": true
   }
   ```
   Schema rejects only *self-labeled* client authority. It **cannot** prove the
   caller is the World Commit service. Docs/policy say clients must not accept
   durable mutation; **no cryptographic mTLS, service identity, or network ACL
   exists yet**. Receipt flag `client_durable_mutation_rejected: true` is true
   only for labeled-invalid fixtures — not for forged-but-well-formed labels.  
   **Mitigation owner:** G6-001 two-client authority POC / World Commit service
   implementation (not G1-002 rework).

2. **Commit request carries no mutation body**  
   Request is authority + revision + confirmation metadata only — no bound
   world_prompt, entity delta, or artifact hash. A valid request does not yet
   define *what* is committed. Fine for authority lock; insufficient for
   end-to-end commit middleware.

3. **No link from confirmed world_prompt → commit_request**  
   G1-001 confirmation and G1-002 commit are separate schemas. Nothing machine-
   checks that `prompt_id` / `request_id` refer to a previously validated,
   confirmed proposal.

4. **Secret payload blocklist is shallow**  
   Top-level payload property names only (`raw_prompt`, `secret`, …). Nested
   objects, alternate casings (`rawPrompt`), or base64 blobs under benign keys
   pass. Event docs claim “payloads do not contain secrets” — schema is a
   weak keyword fence, not a security boundary.

5. **Idempotency / conflict not executed**  
   Fixtures model outcomes; no durable store, no race test, no “second apply
   must not double-mutate” executable service test. G4-001 / G6-001 territory.

6. **Committed receipt does not force `new_world_revision > old_world_revision`**  
   Schema allows equal or decreasing integers if someone crafts them.

7. **False confidence if misread as multiplayer complete**  
   Agents.md: “Documentation is not implementation.” G1-002 is correctly scoped
   as contracts. Do not unlock production/shared durable paths on this alone.

### Holes that would *appear* to allow client durable mutation despite docs

| Attack | Schema outcome today | Real defense needed later |
|---|---|---|
| Client sets `source: client_authoritative` | Rejected | Already covered |
| Client sets `commit_path: client_local` | Rejected | Already covered |
| Client lies with server labels | **Accepted by schema** | Service authn/authz only |
| Client mutates local Godot scene tree | Not in schema surface | Client must never be source of truth |
| Client writes inventory/economy offline as durable online state | Policy forbids; no server | Server-authoritative domains + reconcile |
| Client publishes fake event envelope | Schema may accept well-formed event | Only outbox after commit; signed/auth producers |

### What was *not* found

- No dual Nakama+Colyseus world-state ownership introduced.
- No Godot gameplay or live multiplayer server slipped into allowed paths.
- No contradiction with ARCHITECTURE_LOCK “canonical mutations = World Commit
  service” at the **document/schema** layer.
- Validator merge with G1-001 checks is additive (`check_fixtures` +
  `check_commit_and_event_contracts`); no evidence of disabling format checks.

## Non-blocking residual notes

1. Worker receipt / WO state text claim PASS; Purple static audit agrees.
   Conductor dual-run of `python scripts\validate_project.py` recommended.
2. `tasks.json` still shows G1-002 `IN_PROGRESS` while WO is REVIEW_REQUESTED —
   conductor bookkeeping, not a worker defect.
3. Optional later fixtures: missing `confirmation`, wrong `mutation_class` for
   durable path, and a negative fixture for `idempotent_replay` without
   `idempotency` object (schema allOf already covers).

## Forbidden actions observed

- Purple did not patch product code, schemas, or fixtures.
- Purple did not set `tasks.json` to ACCEPTED (conductor-owned).

## next_route

Conductor may mark G1-002 **ACCEPTED** for the contract gate. Carry residual
adversarial items into World Commit / G6 work orders explicitly:

- Service identity (not client-asserted `authority` JSON)
- Bind commit to validated+confirmed world_prompt
- Executable idempotency + revision races
- Outbox-only event production

Do **not** interpret this ACCEPT as “client durable mutation is impossible in
production.”

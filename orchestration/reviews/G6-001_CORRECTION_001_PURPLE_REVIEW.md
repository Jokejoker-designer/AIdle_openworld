# Purple VERIFY_ONLY review — G6-001 CORRECTION-001 R4_CORE_PURPLE

| Field | Value |
|---|---|
| Task | G6-001 — Two-Client Authoritative Local POC (confirmation-bypass correction) |
| Reviewer | Purple / Devil's Advocate (`aidle-core`, non-writer) |
| Authority | **VERIFY_ONLY** (no product patches; **no tasks.json ACCEPT**) |
| Date | 2026-07-21 |
| Work order | `orchestration/work_orders/WO-G6-001-CORRECTION-001.md` |
| Dispatch map | `orchestration/work_orders/G6-001_CORRECTION_001_DISPATCH_MAP.md` |
| Prior Codex | `orchestration/reviews/CODEX_G6-001_ADVERSARIAL_REVIEW.json` → **CHANGES_REQUESTED** |
| Architecture | `orchestration/ARCHITECTURE_LOCK.md` — Online Private Reality / visitors: Server owns durable state |
| Wave receipts | `R0_schema.json`, `R1_network.json`, `R2_executor.json`, `R3_persist.json` |
| This receipt | `orchestration/receipts/g6/R4_core.json` |
| This review | `orchestration/reviews/G6-001_CORRECTION_001_PURPLE_REVIEW.md` |

## VERDICT

**ACCEPTED**

G6-001 CORRECTION-001 closes both Codex adversarial challenges with independent
executable evidence on Python and Godot. Challenge confirmation-bypass is
**FIXED**:

1. Client-supplied `confirmation.state=confirmed` is rejected **before** proposal
   registration on Python and Godot (`code=client_forged`, `retryable=false`).
2. Commit is impossible until session-bound `confirm_proposal` succeeds
   (bypass chain → `confirmation_missing`).
3. Rejected exploit leaves `world_revision`, `entity_set_hash`, entity count,
   outbox and receipts unchanged (R3 + Purple re-run).
4. Suite green with explicit new counts: **21** server tests / **13** Godot
   checks (prior 19 / 12 + correction regressions).
5. Clean Godot boot + project validator PASS.
6. No self-accept across R0–R4; Purple does not ACCEPT `tasks.json`.

**This review does NOT ACCEPT `orchestration/tasks.json`.** Task G6-001 remains
for Codex (final acceptor). Purple never patches product code and never
self-accepts worker output as ACCEPTED workflow state.
`self_accept=false`. `next_route=WAITING_CODEX`.

---

## Codex challenge matrix (required)

| # | Codex / WO challenge | Result | Evidence |
|---|---|---|---|
| 1 | Both Python and Godot `submit_proposal` accept client-supplied `confirmation.state=confirmed` when `confirmed_by` matches session actor | **FIXED** | Static gates in `server.py` + `world_authority_local.gd`; `test_submit_rejects_client_supplied_confirmed_state`; `AT-G6-CONFIRM-BYPASS-REJECT` |
| 2 | Client can `commit` without ever calling `confirm_proposal` (preview-confirm boundary bypass) | **FIXED** | No proposal authority after reject; commit → `confirmation_missing`; `test_commit_without_confirm_proposal_after_confirmed_submit_attempt`; Godot follow-on commit assert |

Also preserved (WO + prior M4 bar): valid preview→confirm→commit converge,
forged actor/client/owner/direct-write reject, reconnect no double-apply,
secret/public-bind scan, MAF receipts, disjoint ownership, LOCAL POC only.

---

## 1. Client-supplied confirmed rejected before registration

### Claim under review

Codex: both runtimes admitted `confirmation.state=confirmed` on submit when
`confirmed_by` matched the session actor, registering the proposal already
confirmed and allowing commit without `confirm_proposal`.

### Product proof (static, read-only)

| Runtime | File | Behavior |
|---|---|---|
| Python | `services/world_authority_poc/server.py` `submit_proposal` | If `conf.state == "confirmed"` → return `client_forged` **before** space_id check and **before** `_proposals` write. Valid path forces `state=pending` and strips `confirmed_by`. |
| Godot | `game/scripts/modules/network/world_authority_local.gd` `submit_proposal` | Same fail-closed gate (`retryable=false`); force `pending` on every valid admission path. |

Reject envelope (both):

- `ok=false`, `status=rejected`, `code=client_forged`, `retryable=false`
- Reason: `confirmation.state=confirmed is not accepted on submit; only confirm_proposal may confirm`
- Side effects: **none** (no proposal store write, no revision/entity/outbox/receipt)

### Sole confirmation transition

Only session-bound `confirm_proposal` may set:

- `confirmation.state=confirmed`
- `confirmation.confirmed_by` = session actor
- `target.expected_world_revision` = server head

### Independent suite (Purple re-run)

```
python services/world_authority_poc/run_poc_tests.py
→ EXIT=0
→ G6_WORLD_AUTHORITY_SMOKE=PASS
→ Ran 21 tests in 0.050s … OK
```

| Test | Result |
|---|---|
| `test_submit_rejects_client_supplied_confirmed_state` | **PASS** — reject before registration; zero side effects |
| `test_commit_without_confirm_proposal_after_confirmed_submit_attempt` | **PASS** — commit `confirmation_missing` |

```
tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
  -s res://scripts/modules/network/g6_two_client_smoke.gd
→ EXIT=0
→ G6_TWO_CLIENT_SMOKE=PASS checks=13
→ OK  AT-G6-CONFIRM-BYPASS-REJECT code=client_forged commit=confirmation_missing rev=1
```

**PASS / FIXED.**

---

## 2. Commit impossible until confirm_proposal

### Claim under review

After a forged confirmed-submit, a client could still reach durable mutation
via commit without an explicit confirm transition.

### Product proof

| Gate | Behavior |
|---|---|
| Submit with `state=confirmed` | Rejected; **no** proposal registration |
| Commit for that `request_id` | `rejection.code=confirmation_missing` (no registered confirmed proposal) |
| Submit pending, skip confirm, commit | Baseline `TM-UNCONFIRMED-REJECT` still green |
| Valid path | `submit(pending)` → `confirm_proposal` → `commit` still green |

**PASS / FIXED.**

---

## 3. State invariants unchanged on exploit

R3 (`R3_persist.json`, verdict PASS) proved dual-runtime state-unchanged.
Purple independently re-ran both suites; correction tests still assert:

| Surface | On reject | On follow-on commit |
|---|---|---|
| `world_revision` | unchanged | unchanged |
| `entity_set_hash` | unchanged | unchanged |
| entity count | unchanged | unchanged |
| outbox length | unchanged | unchanged |
| receipts / proposal store | no receipt; request_id not in proposals | no committed receipt |

**PASS.**

---

## 4. Baseline suite green (explicit new counts)

| Suite | Prior (Codex) | New | Total this re-run | Marker |
|---|---|---|---|---|
| Python `run_poc_tests.py` | 19 | +2 | **21/21 OK** | `G6_WORLD_AUTHORITY_SMOKE=PASS` |
| Godot `g6_two_client_smoke.gd` | 12 | +1 | **13 checks PASS** | `G6_TWO_CLIENT_SMOKE=PASS` |

Valid path still observed: `status=committed`, `new_world_revision=1`,
entity `ent_bd5a83512b09`, hash prefix `acbef0e69a104bcd`, A/B converge.

**PASS.**

---

## 5. Clean boot + validator

```
tools\Godot_v4.3-stable_win64_console.exe --path game --headless --quit-after 4
→ EXIT=0
→ No SCRIPT ERROR / Parse Error
→ Boot: EventBus, GameManager, WorldRoot, PersistModule, Private Reality
```

```
python scripts/validate_project.py
→ EXIT=0
→ AIDLE_VALIDATION=PASS
```

**PASS.**

---

## 6. Secret / public-bind scan + local POC only

Scopes: `services/world_authority_poc/**`, `game/scripts/modules/network/**`

| Check | Result |
|---|---|
| `0.0.0.0` bind | **none** |
| HTTPServer / TCPServer / socket listen / uvicorn / Flask / FastAPI | **none** |
| HTTPRequest / WebSocket | **none** |
| Nakama / Colyseus runtime import/API | **none** (doc-only negation) |
| `sk-…` keys / `OPENAI_API_KEY=` / Bearer literals | **none** |

Transport remains in-process method calls only. Boot still mounts live
`network` as `AgentNetworkStub`; G6 harness is script-invoked.

**PASS.**

---

## 7. MAF receipts + ownership + no self-accept

### agent_step_contract validation

Schema: `E:/standards/maf/schemas/agent_step_contract.schema.json`

| Receipt | Result |
|---|---|
| `R0_schema.json` | **VALID** |
| `R1_network.json` | **VALID** |
| `R2_executor.json` | **VALID** |
| `R3_persist.json` | **VALID** |
| `R4_core.json` | **VALID** (post-write) |

### Ownership (dispatch map)

| Wave | Profile | Authority | Writes |
|---|---|---|---|
| R0 | schema | VERIFY_ONLY | `R0_schema.json` only |
| R1 | network | PATCH_DRAFT sole | `services/world_authority_poc/**` + `R1_network.json` |
| R2 | executor | PATCH_DRAFT sole | `game/scripts/modules/network/**` + `R2_executor.json` |
| R3 | persist | VERIFY_ONLY | `R3_persist.json` only |
| R4 | core Purple | VERIFY_ONLY | `R4_core.json` + this review only |

Disjoint ownership respected: network never wrote Godot harness; executor never
wrote `services/world_authority_poc/**`. Purple product writes = 0.

### Self-accept chain

| Receipt | `self_accept` |
|---|---|
| R0 | false |
| R1 | false |
| R2 | false |
| R3 | false |
| R4 | **false** |

`tasks.json` ACCEPT: **not performed**. Children: **none**.

**PASS.**

---

## Acceptance checklist (WO-G6-001-CORRECTION-001)

| Criterion | Result |
|---|---|
| `submit_proposal` never accepts client-supplied `state=confirmed` as authoritative | **PASS** (Python + Godot) |
| Fail closed non-retryable reject before registration / mutation / events / receipts | **PASS** (`client_forged`) |
| Valid proposal enters `pending`; only `confirm_proposal` → `confirmed` | **PASS** |
| `commit` still rejects pending / missing / forged confirmation | **PASS** |
| Same rule on Python authority and GDScript mirror | **PASS** |
| Existing actor/client/owner, schema, revision, idempotency, receipt, replay checks not weakened | **PASS** (21/21 + 13/13) |
| Python regression + Godot headless regression | **PASS** |
| Clean integrated Godot boot, validator, secret/public-bind, MAF receipts, ownership, Purple | **PASS** |
| LOCAL POC only; no Nakama/Colyseus / listener / credential / tasks ACCEPT | **PASS** |
| No self-ACCEPT | **PASS** |

---

## Residuals (info only — not blockers)

1. **RES-SCHEMA-STILL-ALLOWS-CONFIRMED** — `contracts/world_prompt.schema.json`
   still permits `state=confirmed` on documents (post-confirm + commit binding).
   Authority-layer submit gate remains mandatory.
2. **RES-CROSS-RUNTIME-HASH-PARITY** — dual in-process simulators; no
   cross-runtime byte hash parity claim.
3. **RES-POC-NOT-PRODUCTION** — no mTLS / public bind / durable multi-process /
   production multiplayer claim.
4. **RES-M2-SMOKE-MATRIX-GAP** — Godot smoke still lacks executable
   idempotency/stale matrix IDs (Python remains sole cover); pre-existing.

---

## Final routing

| Field | Value |
|---|---|
| Purple verdict | **ACCEPTED** |
| `self_accept` | **false** |
| `tasks.json` | **not ACCEPTed** (Codex only) |
| Product edits this wave | **0** |
| Children | **none** |
| `next_route` | **WAITING_CODEX** |

Bootstrap limitation: `E:\scripts\bootstrap-agent-session.ps1` known parser
error near line 52; not retried. Loaded Agents.md, ARCHITECTURE_LOCK,
WO-G6-001-CORRECTION-001, R0–R3, Codex adversarial review, product sources,
and `agent_step_contract` schema manually.

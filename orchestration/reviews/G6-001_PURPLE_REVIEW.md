# Purple VERIFY_ONLY review — G6-001 M4_CORE_TWO_CLIENT_PURPLE

| Field | Value |
|---|---|
| Task | G6-001 — Two-Client Authoritative Local POC |
| Reviewer | Purple / Devil's Advocate (`aidle-core`, non-writer) |
| Authority | **VERIFY_ONLY** (no product patches; **no tasks.json ACCEPT**) |
| Date | 2026-07-21 |
| Work order | `orchestration/work_orders/WO-G6-001.md` |
| Dispatch map | `orchestration/work_orders/G6-001_DISPATCH_MAP.md` |
| Architecture | `orchestration/ARCHITECTURE_LOCK.md` — Online Private Reality / visitors: Server owns durable state |
| Wave receipts | `M0_schema.json`, `M1_network.json`, `M2_executor.json`, `M3_persist.json` |
| This receipt | `orchestration/receipts/g6/M4_core.json` |
| This review | `orchestration/reviews/G6-001_PURPLE_REVIEW.md` |

## VERDICT

**ACCEPTED**

G6-001 meets the work-order acceptance bar as a **LOCAL** authoritative World
Commit POC (not production multiplayer, not Nakama/Colyseus). Independent
Purple re-runs of the server matrix, Godot two-client smoke, clean headless
boot, and project validator all PASS. All seven adversarial challenges PASS.
Disjoint ownership was respected (network owns `services/world_authority_poc/**`;
executor owns `game/scripts/modules/network/**`). Every wave sets
`self_accept=false`.

**This review does NOT ACCEPT `orchestration/tasks.json`.** Task G6-001 remains
for Codex final acceptance. Purple never patches product code and never
self-accepts worker output as ACCEPTED workflow state.
`self_accept=false`. `next_route=WAITING_CODEX`.

## Authority boundary (ARCHITECTURE_LOCK)

| Context | Simulation | Durable state | G6 claim |
|---|---|---|---|
| Online Private Reality / Private with visitors | Server | Server | **In scope** — LOCAL in-process World Commit simulator |
| Offline Private Reality | Local journal | Local + later reconcile | **Out of G6 durable path** — not used as multiplayer SoT |
| Shared District / production multiplayer | Server | Server | **Out of scope** — not claimed |
| Economy / marketplace / matchmaking | Server | Server | **Out of scope** — not claimed |
| Nakama / Colyseus as world-state co-owner | n/a | n/a | **Forbidden / not introduced** |

Product headers and evidence restate LOCAL POC only:

- `services/world_authority_poc/__init__.py`: no public bind, no Nakama/Colyseus
- `server.py`: "No public socket bind. Clients propose; only this service commits."
- `world_authority_local.gd` / `authority_client.gd` / `g6_two_client_smoke.gd`:
  pure GDScript in-process dual-client simulator; not Nakama/Colyseus; no HTTP
- `network_module.gd`: `POC_NOT = ["Nakama", "Colyseus", "public_bind", "cloud_credentials"]`

Boot still mounts the live `network` slot as `AgentNetworkStub`; the G6 harness
is script-invoked for smoke, not a production network stack.

## Ownership (dispatch map)

| Wave | Profile | Authority | Product / receipt writes |
|---|---|---|---|
| M0 | schema | VERIFY_ONLY | `M0_schema.json` only |
| M1 | network | PATCH_DRAFT | sole `services/world_authority_poc/**` + `M1_network.json` |
| M2 | executor | PATCH_DRAFT | sole `game/scripts/modules/network/**` + `M2_executor.json` |
| M3 | persist | VERIFY_ONLY | `M3_persist.json` only |
| M4 | core Purple | VERIFY_ONLY | `M4_core.json` + this review only |

Disjoint ownership respected: network never wrote Godot harness; executor never
wrote `services/world_authority_poc/**`. Purple product writes = 0.

## Acceptance matrix (WO-G6-001)

| Criterion | Result | Evidence |
|---|---|---|
| Two logical clients + one local authority instance | **PASS** | `client_a` / `client_b` against one server (Python + GDScript) |
| Server owns revision, entity set, ownership, commit receipts | **PASS** | `WorldAuthorityServer` / `WorldAuthorityLocal`; issuer `world_commit_service` |
| Valid preview → confirm → commit path | **PASS** | M1 + M2 smokes; status `committed`, revision 0→1 |
| Client B converges revision + entity_set_hash | **PASS** | A/B/S equal; hash prefix `acbef0e69a104bcd` (Godot smoke) |
| Direct write / forged actor-client-owner fail closed | **PASS** | M1 matrix + Godot `client_forged` / direct-write reject; head unchanged |
| Stale revision conflicted without mutation | **PASS** | M1 `TM-STALE-REVISION-CONFLICT` (M2 not executable-covered; residual info) |
| Schema / unconfirmed reject | **PASS** | M1 `TM-INVALID-SCHEMA-REJECT`, `TM-UNCONFIRMED-REJECT` |
| Idempotent same payload replay; changed payload conflict | **PASS** | M1 both; GDScript paths present; residual M2 smoke gap |
| Reconnect/replay no double-apply; snapshot resync | **PASS** | M1 + M2 reconnect replay/snapshot |
| No public bind / Nakama / Colyseus / secrets | **PASS** | Purple scan (below) |
| Clean Godot boot + validator | **PASS** | `--quit-after 4` EXIT=0; `AIDLE_VALIDATION=PASS` |
| MAF receipts + Purple review; no self-accept | **PASS** | M0–M4; all `self_accept=false` |

## Independent verification (Purple re-run)

### 1. World Authority POC unittest matrix

```
python services/world_authority_poc/run_poc_tests.py
→ EXIT=0
→ G6_WORLD_AUTHORITY_SMOKE=PASS
→ Ran 19 tests in 0.048s … OK
```

Matrix coverage (all OK):

- `test_tm_valid_commit_converge`
- `test_tm_direct_write_reject`
- `test_tm_forged_actor_reject` / `forged_client` / `forged_owner` / `forged_leaves_peer_unchanged`
- `test_tm_client_authoritative_schema_reject`
- `test_tm_stale_revision_conflict`
- `test_tm_invalid_schema_reject` / `test_tm_unconfirmed_reject`
- `test_tm_idempotent_replay_same_payload` / `test_tm_idempotency_payload_conflict`
- `test_tm_out_of_order_event` / `test_tm_altered_receipt`
- `test_tm_reconnect_replay` / `test_tm_reconnect_snapshot_resync`
- `test_tm_two_client_headless_smoke`
- `test_rc_fake_event` / `test_submit_preview_no_mutation`

### 2. Godot two-client headless smoke

```
tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
  -s res://scripts/modules/network/g6_two_client_smoke.gd
→ EXIT=0
→ G6_TWO_CLIENT_SMOKE=PASS checks=12
```

Observed:

| Check | Result |
|---|---|
| connect_both `client_a`,`client_b` | OK |
| seed `world_revision=0` | OK |
| submit_and_preview (no mutation) | OK |
| confirm → confirmed | OK |
| valid_commit `committed` rev=1 issuer world_commit_service | OK |
| TM-VALID-COMMIT-CONVERGE rev=1 hash=`acbef0e69a104bcd…` entity `ent_bd5a83512b09` | OK |
| TM-FORGED-ACTOR-REJECT code=`client_forged` | OK |
| TM-FORGED-LEAVES-PEER-UNCHANGED | OK |
| TM-DIRECT-WRITE-REJECT | OK |
| TM-RECONNECT-REPLAY mode=replay entities=1 | OK |
| TM-RECONNECT-SNAPSHOT-RESYNC | OK |
| TM-TWO-CLIENT-HEADLESS-SMOKE final converge | OK |

Cleanliness: no SCRIPT ERROR / Parse Error; EXIT=0.

SUMMARY:
`clients=client_a,client_b committed_once=true converge=true forged_rejected=true reconnect_ok=true`

### 3. Clean integrated Godot boot

```
tools\Godot_v4.3-stable_win64_console.exe --path game --headless --quit-after 4
→ EXIT=0
```

Observed boot path: EventBus → GameManager Core → WorldRoot → PersistModule →
Private Reality entry. No SCRIPT ERROR / Parse Error. Network slot remains
`AgentNetworkStub` (expected; G6 harness is not the live multiplayer stack).

### 4. Project validator

```
python scripts/validate_project.py
→ EXIT=0
→ AIDLE_VALIDATION=PASS
```

Scope includes blueprint-links, schema shapes, world fixtures, commit authority,
event envelope, AGM snapshot/decision, crew, task-dag, asset-grammar.

### 5. Secret / public-bind scan

Scopes: `services/world_authority_poc/**`, `game/scripts/modules/network/**`

| Scan item | Result |
|---|---|
| `0.0.0.0` bind | **absent** |
| `HTTPServer` / `TCPServer` / `socket.` listen | **absent** |
| uvicorn / Flask / FastAPI | **absent** |
| `HTTPRequest` / WebSocket client in harness | **absent** |
| Nakama / Colyseus runtime co-owner | **absent** (docs only as negation) |
| `sk-…` API keys | **absent** |
| hardcoded `api_key=` / `OPENAI_API_KEY` / Bearer literals | **absent** |

## Purple challenges (7)

| ID | Challenge | Status |
|---|---|---|
| CH-P1 | Two clients converge revision + entity_set_hash | **PASS** |
| CH-P2 | Forged mutations rejected without state change | **PASS** |
| CH-P3 | Idempotent replay + payload conflict | **PASS** (M1 executable; M2 path present) |
| CH-P4 | Reconnect no double-apply | **PASS** |
| CH-P5 | No public listener / Nakama-Colyseus / outbound secrets | **PASS** |
| CH-P6 | Clean boot + validator | **PASS** |
| CH-P7 | No self-accept | **PASS** |

## Residuals (info only — not blocking ACCEPTED)

1. **RES-M2-SMOKE-MATRIX-GAP** — Godot smoke does not executable-run
   idempotent-replay, payload-conflict, or stale-revision cases. M1 covers them;
   GDScript implements the same rules.
2. **RES-CROSS-RUNTIME-HASH-PARITY** — Python and Godot hashers claim the same
   algorithm; cross-runtime byte parity on identical sets was not proven in this
   POC (separate in-process simulators).
3. **RES-POC-NOT-PRODUCTION** — In-memory local authority only. No mTLS, public
   bind, durable multi-process persistence, matchmaking, or Shared District.

## Explicit non-claims

- Not production multiplayer transport security
- Not production authn (mTLS)
- Not Nakama/Colyseus adoption decision
- Not Shared District scale, economy, or marketplace
- Not `tasks.json` ACCEPT (Codex final acceptor only)
- Not Offline Private Reality multiplayer SoT

## Routing

| Field | Value |
|---|---|
| `verdict` | **ACCEPTED** (Purple product/evidence gate) |
| `self_accept` | **false** |
| `tasks.json` | **not modified / not ACCEPTED** |
| `next_route` | **WAITING_CODEX** |
| Product patches this wave | **0** |
| Children | **none** |

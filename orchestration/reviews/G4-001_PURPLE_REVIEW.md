# Purple VERIFY_ONLY review — G4-001 P4_NETWORK_PURPLE

| Field | Value |
|---|---|
| Task | G4-001 — Deterministic save/reload and compensation |
| Reviewer | Purple / Devil's Advocate (`aidle-network`, non-writer) |
| Authority | **VERIFY_ONLY** (no product patches; **no tasks.json ACCEPT**) |
| Date | 2026-07-21 |
| Work order | `orchestration/work_orders/WO-G4-001.md` |
| Dispatch map | `orchestration/work_orders/G4-001_DISPATCH_MAP.md` |
| Architecture | `orchestration/ARCHITECTURE_LOCK.md` Authority table |
| Wave receipts | `P0_schema.json`, `P1_persist.json`, `P2_executor.json`, `P3_core.json` |
| This receipt | `orchestration/receipts/g4/P4_network.json` |

## VERDICT

**ACCEPTED**

G4-001 Offline Private Reality persistence meets WO required behavior under
architecture-lock authority. Independent Purple re-run of the headless persist
smoke and project validator both PASS. All eight adversarial challenges PASS.
Local journal durability is correctly scoped as **simulation only** and does
**not** claim Shared District, server economy, multiplayer ownership, or live
World Commit success.

**This review does NOT ACCEPT `orchestration/tasks.json`.** Task G4-001 remains
`IN_PROGRESS` pending Codex final acceptance. Purple never patches product code
and never self-accepts worker output as ACCEPTED workflow state.
`self_accept=false`. `next_route=WAITING_CODEX`.

## Authority boundary (ARCHITECTURE_LOCK)

| Context | Simulation | Durable state | G4 claim |
|---|---|---|---|
| Offline Private Reality | Local client | Local signed journal; reconcile on sync | **In scope** — implemented |
| Online Private Reality | Server | Server | **Out of scope** — not claimed |
| Shared / Doppelganger | Server | Server | **Out of scope** — load rejects non-`private_reality` |
| Economy / ownership / marketplace | Server | Server | **Forbidden client authority** — not in journal |

Product headers and evidence explicitly restate:

- `journal_store.gd`: "NOT Shared District / server commit authority"
- `persist_module.gd`: "online/shared still World Commit"
- Smoke export `authority.not = [shared_district, server_economy, multiplayer_ownership]`

Local apply `status=committed` means **journal entry `mutation_applied` (or
`compensation`) appended successfully** — not `world_commit_service` issuer
success. G3 complete export still carries `durable_mutation_applied=false` and
`world_commit_invoked=false`.

## Acceptance matrix (WO-G4-001)

| Criterion | Result | Evidence |
|---|---|---|
| Canonical deterministic serialization + schema version | **PASS** | `aidle_canonical_json_v1`; journal `schema_version=1.0.0`; smoke `canonical_json_key_order_and_float_format` |
| Save/reload identical entity hashes | **PASS** | `AT-SAVE-RELOAD-HASH` equal SHA-256 (see hash sample) |
| Duplicate request_id → no second entity | **PASS** | `AT-DUP-REQUEST` → `idempotent_replay`, entity_count=1 |
| Stale revision rejected without partial mutation | **PASS** | `AT-STALE-REVISION` → `conflicted` / `revision_mismatch`, head unchanged |
| Compensation append-only, linked prior receipt | **PASS** | `AT-COMPENSATION-APPEND` → entry_count=2, `history_erased=false`, prior unchanged |
| Cancelled previews never durable | **PASS** | `AT-CANCEL-NOT-JOURNALED` → rejected, entries_unchanged |
| Truncated/malformed/incompatible fail closed | **PASS** | truncated / schema_incompat / wrong_space_type smoke checks |
| G3 `expected_world_revision=3` preserved | **PASS** | base 3 → head 4 after apply; never coerced to 0 |
| Clean smoke + `AIDLE_VALIDATION=PASS` | **PASS** | Purple re-run below |
| MAF receipts + ownership + Purple review | **PASS** | P0–P4; sole product writer was P1 persist |
| No self-accept / no live World Commit claim | **PASS** | All waves `self_accept=false`; authority split documented |

## Independent verification (Purple re-run)

### Godot headless persist smoke

```
tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
  -s res://scripts/modules/persist/g4_persist_smoke.gd
→ EXIT=0
→ G4_PERSIST_SMOKE=PASS checks=11
```

Log: `orchestration/logs/g4-p4-purple-persist-smoke.log`

Checks observed OK:

1. `interface_surface`
2. `canonical_json_key_order_and_float_format`
3. `deterministic_save_reload_same_entity_hashes`
4. `duplicate_request_id_no_duplicate_entity`
5. `stale_expected_world_revision_rejected`
6. `truncated_malformed_journal_fail_closed`
7. `incompatible_schema_version_fail_closed`
8. `reject_non_private_reality_journal`
9. `compensation_append_only_history_preserved`
10. `cancelled_preview_never_in_journal`
11. `g3_expected_world_revision_3_through_save_reload`

Cleanliness: `SCRIPT ERROR=0`, `Parse Error=0`, `Compile Error=0`, `ERROR:=0`.

### Project validator

```
python scripts\validate_project.py
→ EXIT=0
→ AIDLE_VALIDATION=PASS
```

### Hash sample (matches P1 + P3)

| Field | Value |
|---|---|
| entity_hash | `03933b0b8efa9fb436c50335687506deecbe81ce8b966b9bdda337f9a8bc5534` |
| reload entity_hash | same |
| entity_set_hash | `5daf27b3d6aca68eda384ae8780a52d904135f12f922cbc552ec2332e6ef6d48` |
| save/reload equal | true |
| base → after first apply | world_revision 3 → 4 |

Evidence export:
`game/scripts/modules/persist/exports/g4_persist_smoke_evidence.json`

## Adversarial challenges (required)

### 1. Local journal never claims Shared District / server economy / multiplayer

**PASS.** Envelope `space_type` is const `private_reality`. Load of
`shared_district` fails with `wrong_space_type`. Module headers, P0
`INV-PR-SPACE`, smoke `authority.not`, and ARCHITECTURE_LOCK table all align.
No client-authoritative economy fields in journal envelope.

### 2. Idempotency: duplicate `request_id` → no new entity

**PASS.** `apply_mutation` / `apply_compensation` consult `_request_index`
before mutation; hit returns `idempotent_replay` with `prior_receipt_id`, no
append, no revision bump. Replay-on-load rejects duplicate `request_id` in
stored entries. Smoke: entity_count stays 1 at rev 4.

### 3. Stale revision atomic reject

**PASS.** Optimistic concurrency: `expected_world_revision` must equal head.
Mismatch returns `status=conflicted`, `conflict.code=revision_mismatch` **before**
entity writes and **before** `_append_entry`. Smoke: head_unchanged=3,
`no_partial_mutation=true`.

### 4. Compensation append-only, no history rewrite

**PASS.** Compensation is a new `entry_type=compensation` with required
`prior_receipt_id`, `history_erased=false`. Missing prior → reject, no append.
`apply_mutation` with `mutation_class=compensating` is rejected
(`use_apply_compensation`). No delete/rewrite of prior entries in store.
Smoke: entry_count=2, prior entry unchanged, rev 5 after compensation.

### 5. Cancel not journaled

**PASS.** `_gate_durable` rejects `receipt_kind=cancel`, cancel operation,
`preview_only`, non-`confirmed` confirmation, and cancelled pipeline stage.
Smoke uses G3 cancel `request_id` `6da43c54-…` → `cancel_not_durable`,
entries_unchanged, rev stays 3. G3 cancel export: no durable mutation, revision
not advanced.

### 6. Fail-closed malformed journal

**PASS.** Empty/truncated JSON → `journal_truncated`; parse/structure/entry
chain failures → `journal_malformed`; wrong schema →
`journal_schema_incompatible`; wrong space → `wrong_space_type`. Replay builds
into locals and only commits state on full success — no silent empty-world
invention. Smoke covers truncated, missing fields, schema, and space boundary.

### 7. G3 rev 3 preserved

**PASS.** G3 complete + commit_request handoff still show
`expected_world_revision=3`. Smoke seeds `base_world_revision=3`,
`space_id=home_01`, snapshot `11111111-…`, applies with expected=3 → head 4,
`never_coerced_to_0=true`. Aligns with P0 `INV-G3-REV-3` and P3 C6.

### 8. No self-accept / no live World Commit claim

**PASS.**

| Check | Result |
|---|---|
| P0–P4 `self_accept` | all **false** |
| Purple `tasks.json` ACCEPT | **not performed** |
| Final acceptor | **Codex** (dispatch map) |
| Local `committed` ≠ server commit | documented in P1 risks, P2 C4, P3 notes, this review |
| G3 complete durable/wci | both **false**; stub status **rejected** |

## Prior-wave consistency

| Wave | Profile | Auth | Verdict / state | Product writes |
|---|---|---|---|---|
| P0 | schema | VERIFY_ONLY | HANDOFF_TO_P1 | 0 (receipt only) |
| P1 | persist | PATCH_DRAFT | REVIEW_REQUESTED | owned persist surface only |
| P2 | executor | VERIFY_ONLY | PASS → P3 | 0 |
| P3 | core | VERIFY_ONLY | PASS → P4 | 0 |
| P4 | network | VERIFY_ONLY | **ACCEPTED** → WAITING_CODEX | 0 (receipt + this md) |

Ownership: P1 was sole product writer for `game/scripts/modules/persist/**` and
`i_persist_module.gd`. P2–P4 did not edit product. No children / nested
grandchildren. No architecture, contracts, work-order, or tasks edits by this
wave.

## Residuals (non-blocking for WO acceptance)

1. **Boot mount:** ModuleRegistry still mounts `AgentPersistStub` on integrated
   boot; PersistModule is proven via dedicated `-s` smoke (P3 residual).
2. **Consumer adapter:** Executor does not yet call PersistModule after confirm
   (P2 documented gaps: wire apply, field projection, receipt_id chain).
3. **Semantic split:** UI/network layers must not set
   `durable_mutation_applied=true` solely because local journal applied.
4. **Optional chain hash:** Integrity chain hash not implemented; entry_count +
   revision-chain validation covers MVP fail-closed.

None of these residuals violate WO-G4-001 required behavior evidence listed
above.

## Codex handoff

- Purple verdict: **ACCEPTED** (product quality / authority / smoke)
- Workflow task state: **do not flip** to ACCEPTED in `tasks.json` here
- `self_accept`: **false**
- `next_route`: **WAITING_CODEX**
- Parent may update `grok_status.json` only if conductor-owned; this Purple
  wave wrote **only** `P4_network.json` + this review.

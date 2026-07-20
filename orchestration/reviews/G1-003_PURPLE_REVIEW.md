# Purple VERIFY_ONLY review — G1-003

| Field | Value |
|---|---|
| Task | G1-003 — Lock AGM Snapshot and Decision Envelope contracts |
| Reviewer | Purple / Devil's Advocate |
| Authority | VERIFY_ONLY (no product/schema/fixture patches; no tasks.json ACCEPT) |
| Date | 2026-07-20 |
| Work order | `orchestration/work_orders/WO-G1-003.md` |
| Worker receipt | `orchestration/receipts/G1-003.json` |

## VERDICT

**ACCEPTED**

G1-003 meets the **contract-layer** acceptance bar: Draft 2020-12 World State
Snapshot + Decision Envelope schemas, free/paid identical payload semantics,
≥5 valid / ≥10 invalid fixtures, replay and stale-snapshot policy fixtures,
build proposals forced through pending preview, and schema rejection of direct
durable mutation / secrets / TTS / code. **This is not runtime enforcement.**
Residual notes below are mandatory reading for G2-005 / G2-006 implementers;
they do not fail this work order’s stated scope.

**Blockers:** none.

## Evidence

### Smoke / validator

Independent Purple execution (this review):

```text
python scripts\validate_project.py
→ exit 0
→ AIDLE_VALIDATION=PASS
→ scope includes agm-snapshot-decision
```

Also revalidated fixtures via `orchestration/reviews/_purple_verify_g1_003_tmp.py`:
all 7 valid accepted; all 14 invalid rejected; free/paid semantic strip equal;
replay same `decision_id` + `replay_must_reject`; stale `source_snapshot_id` ≠
live `snapshot_id` + `stale_must_reject`.

Worker receipt claims match observed smoke (`exit_code: 0`,
`AIDLE_VALIDATION=PASS`, 7 valid / 13 invalid — live tree now has **14**
invalid files, still ≥10).

### Artifacts present

| Artifact | Status |
|---|---|
| `contracts/agm/world_state_snapshot.schema.json` | Present |
| `contracts/agm/decision_envelope.schema.json` | Present |
| `contracts/fixtures/agm/valid/*` (7 files) | Present |
| `contracts/fixtures/agm/invalid/*` (14 files) | Present |
| `contracts/fixtures/agm/policy/*` (3 files) | Present |
| Validator `check_agm_contracts()` | Present in `scripts/validate_project.py` |
| `AIdle_Openworld_Blueprint_v1.1/Interfaces/AGM_Contracts.md` | Paths point at machine contracts |
| `orchestration/receipts/G1-003.json` | Present; state `REVIEW_REQUESTED`; no self-ACCEPT |

### Acceptance matrix (WO-G1-003 + chat bar)

| # | Criterion | Result |
|---|---|---|
| 1 | Snapshot + decision Draft 2020-12 schemas | **PASS** — both `$schema` = `https://json-schema.org/draft/2020-12/schema`; `Draft202012Validator.check_schema` via project validator |
| 2 | Free and paid identical payload semantics | **PASS** — edition enum only `desktop_bridge_free` \| `api_paid`; identity pair strips `edition`+`transport` and requires equal payloads for snapshot + decision pairs |
| 3 | ≥5 valid fixtures | **PASS** — **7** under `contracts/fixtures/agm/valid/` |
| 4 | ≥10 invalid fixtures | **PASS** — **14** under `contracts/fixtures/agm/invalid/` |
| 5 | Replay decision_id rejected | **PASS** — `policy/replay_decision_pair.json` same UUID + validator seen-set simulation + `rules.replay_must_reject: true` |
| 6 | Stale snapshot rejected | **PASS** — `policy/stale_snapshot_rejection.json` live ≠ `source_snapshot_id` + `rules.stale_must_reject: true` |
| 7 | No direct durable mutation | **PASS** — schema `additionalProperties: false` + `propertyNames` bans `durable_mutation` / `commit_request` / …; fixture `invalid_decision_direct_durable_mutation.json` rejected |
| 8 | No secrets / TTS | **PASS** — banned names + fixtures `invalid_snapshot_with_api_key.json`, `invalid_decision_with_tts_voice.json` rejected |
| 9 | Build proposals stay pending preview | **PASS** — consts `preview_required: true`, `confirmation_state: pending`, `routes_through: preview_confirm_commit`; bypass fixture rejected |
| 10 | Excessive mood/relationship / unknown event/action | **PASS** — deltas capped ±0.1 / ±0.05; unknown event + unknown player action fixtures rejected |
| 11 | `validate_project.py` exit 0 (additive AGM check) | **PASS** — full suite still green (world_prompt, commit, events, asset-grammar intact) |
| — | No API SDK / credentials / network / Godot gameplay | **PASS** — contract-only deliverable |
| — | No self-ACCEPT | **PASS** — receipt `REVIEW_REQUESTED` |

### Schema shape locks

**World State Snapshot** (`additionalProperties: false`):

Required: `schema_version`, `snapshot_id`, `created_at`, `edition`, `session_id`,
`space_id`, `world_revision`, `progression_phase`, `art_style`, `player`,
`companion`, `world`, `quests`, `latest_player_action`, `last_execution_receipt`,
`memory`, `trace_id`.

**Decision Envelope** (`additionalProperties: false`):

Required: `schema_version`, `decision_id`, `source_snapshot_id`, `created_at`,
`edition`, `session_id`, `dialogue`, `quest_operations`, `build_proposals`,
`event_proposals`, `mood_delta`, `relationship_delta`, `next_trigger`, `trace`.

Build item consts (machine-enforced by validator shape check + schema):

| Field | Const |
|---|---|
| `preview_required` | `true` |
| `confirmation_state` | `pending` |
| `routes_through` | `preview_confirm_commit` |

Dialogue is text-only (`text` string); no STT/TTS properties in dialogue items.

### Free / paid payload identity

Policy: `contracts/fixtures/agm/policy/edition_identity_pair.json`

| Pair | Free | Paid | After strip |
|---|---|---|---|
| Snapshot | `valid_snapshot_desktop_bridge.json` (`desktop_bridge_free`) | `valid_snapshot_api_paid.json` (`api_paid`) | **Equal** |
| Decision | `valid_decision_desktop_bridge.json` | `valid_decision_api_paid.json` | **Equal** |

Strip keys: `edition`, `transport` (non-authoritative delivery metadata only).

### Valid fixtures (7)

1. `valid_snapshot_desktop_bridge.json`
2. `valid_snapshot_api_paid.json`
3. `valid_snapshot_mid_session.json`
4. `valid_decision_desktop_bridge.json`
5. `valid_decision_api_paid.json`
6. `valid_decision_with_build_proposal.json` — pending preview path
7. `valid_decision_quest_complete.json`

### Invalid fixtures (14) — independent rejection

| Fixture | Observed reject reason (abbrev.) |
|---|---|
| `invalid_decision_build_bypasses_preview.json` | `preview_required` / `confirmation_state` not const |
| `invalid_decision_direct_durable_mutation.json` | unexpected `durable_mutation`, `commit_request` |
| `invalid_decision_excessive_mood_delta.json` | `0.9` > max `0.1` |
| `invalid_decision_excessive_relationship_delta.json` | `0.5` > max `0.05` |
| `invalid_decision_missing_required.json` | missing `decision_id` |
| `invalid_decision_unknown_event.json` | `inventory.grant_currency` not allowlisted |
| `invalid_decision_unknown_field.json` | unexpected `arbitrary_side_channel` |
| `invalid_decision_with_script_code.json` | unexpected `script`, `code` |
| `invalid_decision_with_tts_voice.json` | unexpected `tts_audio`, `voice_sample` |
| `invalid_decision_wrong_schema_version.json` | schema_version ≠ `1.0.0` |
| `invalid_snapshot_missing_required.json` | missing `snapshot_id` |
| `invalid_snapshot_unknown_field.json` | unexpected `llm_raw_text` |
| `invalid_snapshot_unknown_player_action.json` | `hack_inventory` not in action enum |
| `invalid_snapshot_with_api_key.json` | unexpected `api_key` |

### Policy fixtures

**Replay** (`replay_decision_pair.json`):

- Original and replay both schema-valid alone
- Same `decision_id` (`aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa`)
- Replay body differs (extra quest offer, larger deltas) — must not re-apply
- Validator simulates executor seen-set hit; requires `rules.replay_must_reject`

**Stale** (`stale_snapshot_rejection.json`):

- Live snapshot_id `bbbbbbbb-…`
- Decision `source_snapshot_id` `11111111-…` (mismatch)
- Both schema-valid alone; policy requires reject when source ≠ live

### Blueprint cross-links

- `Interfaces/AGM_Contracts.md` points at `contracts/agm/*` and
  `contracts/fixtures/agm/{valid,invalid,policy}/`
- Documents free/paid identical semantics, build → preview_confirm_commit,
  replay/stale policy, no secrets/TTS/direct mutation
- Aligns with `08_AI_Game_Master_and_Edition_Modes.md` shared loop

## Adversarial hunt (Devil's Advocate)

### NOT blocking for G1-003 contract scope

1. **Replay / stale are policy fixtures, not a live executor**  
   `check_agm_contracts` simulates a seen-set and ID inequality. There is no
   durable decision store, clock skew handling, or concurrent double-submit
   test. **Owner:** G2-006 decision executor.

2. **Honor-system AGM honesty after schema pass**  
   A hostile or buggy model can still emit a **schema-valid** decision that
   offers bad quests or social engineering dialogue. Schema cannot prove
   provider integrity or player intent. Consent + allowlist + budgets remain
   runtime gates.

3. **Secret / code propertyNames banlist is shallow**  
   Top-level name fence + `additionalProperties: false`. Nested keys, alternate
   casings, or base64 under benign fields can still pass. Weak keyword fence,
   not a security boundary (same class of residual as G1-002 events).

4. **Build proposal is not a full world_prompt**  
   Items carry recipe/entity/transform metadata and route flags, not a bound
   `prompt_id` / validated world_prompt body. Executor must still construct a
   schema-valid world_prompt and enter the G1-001 preview → confirm → G1-002
   commit path. Fine for G1-003; insufficient for end-to-end build safety alone.

5. **Quest / event / mood side effects are not World Commit**  
   Blueprint allows dialogue/quest UI after validation without durable build
   commit. Contract correctly forbids *durable* mutation fields; it does not
   (and should not) force every soft side effect through commit. G2-006 must
   still define what is soft-apply vs durable.

6. **Bridge filesystem paths not machine-locked**  
   Blueprint prose says exact bridge paths “locked by the G1-003 machine
   contract”; schema only allows optional non-authoritative
   `transport.bridge_path_hint`. Payload contract is locked; path conventions
   remain for G2-005 Desktop Bridge.

7. **Free/paid identity proven on paired fixtures only**  
   Validator compares the declared identity pair files, not every valid fixture
   against an edition twin. Mid-session / quest / build fixtures are single-
   edition. Acceptable for gate; runtime must still forbid edition-forked
   semantics.

8. **False confidence if misread as AGM runtime complete**  
   Agents.md: documentation is not implementation. Do not unlock Desktop
   Bridge, API gateway, or production AGM on this alone.

### What was *not* found

- No separate free vs paid decision schemas.
- No commit/API credential fields in valid fixtures.
- No TTS/voice pipeline or Godot gameplay changes in allowed paths.
- No self-ACCEPT in receipt.
- Validator merge is additive (`check_agm_contracts` in `main`); other gates
  still pass in the same run.

## Non-blocking residual notes

1. `tasks.json` still shows G1-003 `IN_PROGRESS` while WO is `REVIEW_REQUESTED` —
   conductor bookkeeping; Purple did not edit `tasks.json`.
2. Receipt smoke text says “13 invalid”; tree has 14 — still meets ≥10.
3. Optional later fixtures: nested secret under `trace`, missing
   `build_proposals` required item fields singly, decision with
   `routes_through` misspelled (const already covers).

## Forbidden actions observed

- Purple did not patch product code, schemas, or fixtures (only this review +
  ephemeral verify helper under `orchestration/reviews/`).
- Purple did not set `tasks.json` to ACCEPTED (conductor-owned).

## next_route

Conductor may mark G1-003 **ACCEPTED** for the contract gate and unblock
dependents (G2-003 AGM-driven rework, G2-005 Desktop Bridge, G2-006 executor,
G2-007 edition selector). Carry residual adversarial items into those WOs:

- Executable replay idempotency + stale snapshot at executor boundary
- world_prompt construction from build_proposals + preview/confirm/commit bind
- Transport path conventions and malformed import rejection (G2-005)
- No client secrets on paid path (G2-007 / G5 gateway)

Do **not** interpret this ACCEPT as “AGM cannot harm the world in production”
or “Desktop Bridge is implemented.”

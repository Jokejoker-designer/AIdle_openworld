# Purple VERIFY_ONLY review — G4-001 CORRECTION-001 R4_NETWORK_PURPLE

| Field | Value |
|---|---|
| Task | G4-001 — Deterministic save/reload and compensation (runtime + signed journal correction) |
| Reviewer | Purple / Devil's Advocate (`aidle-network`, non-writer) |
| Authority | **VERIFY_ONLY** (no product patches; **no tasks.json ACCEPT**) |
| Date | 2026-07-21 |
| Work order | `orchestration/work_orders/WO-G4-001-CORRECTION-001.md` |
| Dispatch map | `orchestration/work_orders/G4-001_CORRECTION_001_DISPATCH_MAP.md` |
| Prior Codex | `orchestration/reviews/CODEX_G4-001_ADVERSARIAL_REVIEW.json` → **CHANGES_REQUESTED** |
| Architecture | `orchestration/ARCHITECTURE_LOCK.md` Authority table |
| Wave receipts | `R0_schema.json`, `R1_persist.json`, `R2_core.json`, `R3_executor.json` |
| This receipt | `orchestration/receipts/g4/R4_network.json` |

## VERDICT

**ACCEPTED**

G4-001 CORRECTION-001 closes every Codex adversarial challenge with independent
executable evidence. Purple re-ran headless persist smoke (22 checks), integrated
boot, and the project validator; all PASS with clean logs. Integrated boot mounts
real `PersistModule` (not `AgentPersistStub`). The local journal is keyed
HMAC-SHA256 sealed with fail-closed integrity. The offline consumer gate rejects
G3 rejected-handoff auto-journal and online/shared/economy/ownership contexts.
P0 hash/idempotency/stale/compensation/rev3 behaviors are preserved under the
sealed path. Local seal is reconciliation evidence only — not server authority.

**This review does NOT ACCEPT `orchestration/tasks.json`.** Task G4-001 remains
`CHANGES_REQUESTED` until Codex (final acceptor) moves it. Purple never patches
product code and never self-accepts worker output as ACCEPTED workflow state.
`self_accept=false`. `next_route=WAITING_CODEX`.

---

## Codex challenge matrix (required)

| # | Codex / WO challenge | Result | Evidence |
|---|---|---|---|
| 1 | Integrated boot mounts `PersistModule`, not `AgentPersistStub` | **FIXED** | `main.gd` `_mount_persist_module`; Purple boot markers |
| 2 | Signed journal HMAC + fail-closed tamper/wrong-key/reorder/remove | **FIXED** | `journal_seal.gd` + integrity AT-* suite (22-check smoke) |
| 3 | Consumer gate `offline_only`; G3 rejected handoff not auto-journaled; online/shared/economy rejected | **FIXED** | `_gate_offline_consumer` + AT-GATE-*; executor zero persist calls |
| 4 | Preserve hash/idempotency/stale/compensation/rev3 | **FIXED** | AT-SAVE-RELOAD-HASH, DUP, STALE, COMPENSATION, G3-REV-3 |
| 5 | Local seal not server authority | **FIXED** | `local_seal_not_server_authority=true`; authority.not; headers |

Original Codex `what_i_challenge` items (3) map to rows 1–3 above; rows 4–5 are
WO preserve + authority clarifications required by the correction work order.

---

## 1. Integrated boot mounts PersistModule (Codex primary)

### Claim under review

Prior G4 wave mounted `AgentPersistStub` at integrated boot; PersistModule only
existed on the dedicated `-s` smoke path.

### Product proof (static)

`game/scripts/main/main.gd`:

- Preloads `res://scripts/modules/persist/persist_module.gd`
- `_spawn_module_stubs()` calls `_mount_persist_module()` first
- `MODULE_PERSIST` is **omitted** from `stub_defs`
- Mount instantiates `PersistModule`, attaches via `ModuleRegistry`, prints
  `[Main] PersistModule mounted (real, not AgentPersistStub).`

### Independent boot (Purple re-run)

```
tools\Godot_v4.3-stable_win64_console.exe --path game --headless --quit-after 5
→ EXIT=0
```

Log: `orchestration/logs/g4-r4-purple-core-boot.log`

Markers observed:

- `[ModuleRegistry] Registered module: persist (PersistModule)`
- `[PersistModule] Ready – Private Reality signed journal (schema 1.0.0).`
- `[Main] PersistModule mounted (real, not AgentPersistStub).`
- `[Main] Camera mode=fixed-angle 2.5D (pitch locked, no free orbit/FPS).`
- `[Main] Player ready: CharacterBody3D XZ locomotion on ground plane.`
- `[Main] Entered Private Reality | style=cozy_cyber_pixel`

Not observed for persist: `[ModuleStub] persist mounted as stub`.

Cleanliness: `SCRIPT ERROR=0`, `Parse Error=0`, `Compile Error=0`, `ERROR:=0`.

**PASS / FIXED.**

---

## 2. Signed journal HMAC + fail-closed integrity (Codex primary)

### Claim under review

Architecture Lock Offline Private Reality requires a **local signed journal**.
Prior implementation had append-only JSON + unkeyed entity hashes only.

### Product proof (static)

| Component | Role |
|---|---|
| `journal_seal.gd` | HMAC-SHA256 via `Crypto.hmac_digest(HashingContext.HASH_SHA256, …)`; genesis + prev_seal chain; `verify_chain` |
| `test_journal_key_provider.gd` | TEST_ONLY provider (`provider_id` contains test marker) |
| `journal_store.gd` | `set_key_provider`, seal on append, verify on load/save; fail-closed codes |
| `persist_module.gd` | Public API surface for seal/gate |
| `i_persist_module.gd` | REQUIRED_METHODS include integrity + offline APIs |

Fail-closed codes exercised: `key_provider_missing`, `journal_integrity_invalid`,
`journal_integrity_wrong_key` (and related unsigned/invalid paths).

### Independent smoke (Purple re-run)

```
tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
  -s res://scripts/modules/persist/g4_persist_smoke.gd
→ EXIT=0
→ G4_PERSIST_SMOKE=PASS checks=22
```

Log: `orchestration/logs/g4-r4-purple-persist-smoke.log`

Integrity checks observed OK:

1. `sealed_journal_save_reload_verify_ok`
2. `wrong_key_fail_closed`
3. `modified_entry_detected`
4. `removed_entry_detected`
5. `reordered_entries_detected`
6. `broken_previous_seal_detected`
7. `invalid_or_missing_seal_fail_closed`
8. `missing_key_provider_fail_closed`

Evidence export:
`game/scripts/modules/persist/exports/g4_persist_smoke_evidence.json`

Sample (sealed path):

| Field | Value |
|---|---|
| algorithm | `hmac-sha256` |
| key_provider_id | `TEST_ONLY_G4` |
| test_key | true |
| local_seal_not_server_authority | true |
| sealed entity_hash | `e96fadda66c85b6636096218d804173fb5913ed7170e38dea79e5257865d365a` |

**PASS / FIXED.**

Note (non-blocking residual): mismatch path may report `journal_integrity_wrong_key`
vs `journal_integrity_invalid` depending on HMAC mismatch classification; both
paths fail closed with no entity materialization.

---

## 3. Consumer gate offline_only + G3 no-auto-journal (Codex primary)

### Claim under review

Executor / consumers lacked an explicit Offline Private Reality gate; G3 rejected
World Commit handoff could be misread as journalable committed state.

### Gate implementation (static)

`journal_store.gd::_gate_offline_consumer` + `_has_explicit_offline_confirmed`:

- Requires `authority.context=offline_private_reality` and `confirmation.state=confirmed`
- Rejects `REJECT_AUTHORITY_CONTEXTS`: `online_private_reality`, `shared_district`,
  `private_with_visitors`, `server_economy`, `ownership`, `marketplace`
- If request carries `world_commit_invoked=false` AND
  `durable_mutation_applied=false` without explicit offline confirmed metadata →
  `g3_rejected_handoff_not_journalable`
- Enforced on `apply_mutation` / `apply_compensation` and the public
  `apply_offline_private_reality_*` entrypoints

### G3 complete still rejected (static)

`game/scripts/modules/executor/exports/g3_complete_receipt.json`:

- `durable_mutation_applied=false`
- `world_commit_invoked=false`
- `commit_receipt_stub.status=rejected`, `stub=true`

### Executor cannot silent-wire (static)

Grep of `game/scripts/modules/executor/**`: **zero** references to
`PersistModule`, `apply_mutation`, `apply_offline`, or journal apply. Complete
path remains export-only handoff stub (R3 confirmations C2/C4).

### Smoke gate results (Purple re-run evidence)

| Test | Result | Key fields |
|---|---|---|
| `only_offline_private_reality_journals` | **PASS** | rejects shared/online/economy/ownership/marketplace; entry_count unchanged |
| `g3_rejected_handoff_not_auto_journaled` | **PASS** | `status=rejected`, `error_code=g3_rejected_handoff_not_journalable`, `entry_count=0` |
| `explicit_offline_confirmed_apply_succeeds` | **PASS** | `status=committed`, seal present, rev 3→4, `local_seal_not_server_authority=true` |

**PASS / FIXED.**

---

## 4. Preserve hash / idempotency / stale / compensation / rev3

| Criterion | Result | Evidence (smoke export) |
|---|---|---|
| Save/reload identical entity hashes | **PASS** | AT-SAVE-RELOAD-HASH equal SHA-256 |
| Duplicate request_id → no second entity | **PASS** | AT-DUP-REQUEST → `idempotent_replay`, entity_count=1, rev=4 |
| Stale revision atomic reject | **PASS** | AT-STALE-REVISION → `conflicted`/`revision_mismatch`, head_unchanged=3 |
| Compensation append-only | **PASS** | AT-COMPENSATION-APPEND entry_count=2, `history_erased=false`, prior unchanged |
| G3 expected_world_revision=3 | **PASS** | base 3 → head 4; `never_coerced_to_0=true` |
| Cancel never journaled | **PASS** | AT-CANCEL-NOT-JOURNALED |
| Malformed / schema / space fail closed | **PASS** | AT-MALFORMED / SCHEMA / SPACE |

Hash sample (P0 path under sealed suite):

| Field | Value |
|---|---|
| entity_hash | `03933b0b8efa9fb436c50335687506deecbe81ce8b966b9bdda337f9a8bc5534` |
| entity_set_hash | `5daf27b3d6aca68eda384ae8780a52d904135f12f922cbc552ec2332e6ef6d48` |
| save/reload equal | true |

**PASS / FIXED (preserved).**

---

## 5. Local seal not server authority

| Check | Result |
|---|---|
| ARCHITECTURE_LOCK Offline PR = local signed journal; Shared/online = Server | **aligned** |
| Envelope `integrity.local_seal_not_server_authority=true` | **PASS** |
| Module headers: online/shared/economy still World Commit | **PASS** |
| Smoke `authority.not` includes shared_district / server_economy / multiplayer_ownership | **PASS** |
| Local `status=committed` ≠ `world_commit_service` success | **documented** |
| G3 complete durable/wci still false | **PASS** |

**PASS / FIXED.**

---

## Independent verification summary

### Persist smoke

```
G4_PERSIST_SMOKE=PASS checks=22
EXIT=0
SCRIPT ERROR / Parse Error / Compile Error / ERROR: = 0
```

### Integrated boot

```
EXIT=0
PersistModule registered + mounted markers present
persist slot is not ModuleStub
2.5D camera + player markers present
```

### Project validator

```
python scripts\validate_project.py
→ EXIT=0
→ AIDLE_VALIDATION=PASS
```

---

## Prior-wave consistency

| Wave | Profile | Auth | Verdict / state | Product writes |
|---|---|---|---|---|
| R0 | schema | VERIFY_ONLY | HANDOFF_TO_R1 | 0 (receipt only) |
| R1 | persist | PATCH_DRAFT | REVIEW_REQUESTED | owned persist surface only |
| R2 | core | PATCH_DRAFT | REVIEW_REQUESTED | `main.gd` only |
| R3 | executor | VERIFY_ONLY | PASS → R4 | 0 |
| R4 | network | VERIFY_ONLY | **ACCEPTED** → WAITING_CODEX | 0 (receipt + this md) |

All waves `self_accept=false`. No children. No architecture / contracts /
work-order / tasks / directive edits by this wave.

Ownership: R1 sole product writer for `game/scripts/modules/persist/**` and
`i_persist_module.gd`. R2 sole product writer for `game/scripts/main/main.gd`.
R0/R3/R4 verify-only.

---

## Residuals (non-blocking for correction acceptance)

1. **Key provider at boot:** Mount does not inject a production key provider;
   sealed ops fail closed with `key_provider_missing` until inject. Smoke uses
   `TEST_ONLY_G4` only.
2. **Executor adapter:** Still not product-wired to call
   `apply_offline_private_reality_*` after confirm. This is **safe fail-closed**
   (G3 cannot auto-journal); future WO must set offline authority metadata only
   for Private Reality simulation and must never set
   `durable_mutation_applied=true` solely because local journal applied.
3. **Semantic split:** UI/network layers must not treat local `committed` as
   live World Commit success.
4. **Unsigned legacy journals:** Refuse load under enforcement (intentional).
5. **Error-code nuance:** wrong_key vs invalid may swap on some mismatch paths;
   both fail closed.

None of these residuals reopen Codex challenges 1–3 or WO required evidence.

---

## Codex handoff

- Purple verdict: **ACCEPTED** (correction quality / authority / smoke)
- Workflow task state: **do not flip** to ACCEPTED in `tasks.json` here
- `self_accept`: **false**
- `next_route`: **WAITING_CODEX**
- Parent may update `grok_status.json` only if conductor-owned; this Purple
  wave wrote **only** `R4_network.json` + this review.

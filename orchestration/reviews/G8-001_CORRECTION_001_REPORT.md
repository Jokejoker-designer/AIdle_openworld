# G8-001 CORRECTION-001 Report — Non-mutating verification gate

**Directive:** 20 (supersedes false scope-honesty claim of Directive 19 machine pass)  
**Work order:** `orchestration/work_orders/WO-G8-001-CORRECTION-001.md`  
**State returned:** `REVIEW_REQUESTED` / `WAITING_CODEX`  
**Self-accept:** false · **ACCEPTED:** not claimed  

---

## 1. Directive 19 failure preserved (not erased)

Codex machine review (`CODEX_G8-001_MACHINE_REVIEW.json`) correctly found:

- Six **tracked** G3/G4 export/evidence files were mutated by VERIFY_ONLY smokes.
- G8 report / collate / status claimed `product_patches_this_gate=0` and no prior-evidence edits — **false**.
- Functional G3/G4 check markers were still valid; the failure is **evidence honesty / VERIFY_ONLY purity**, not functional regression.

### Contaminated files (Directive 19)

1. `game/scripts/modules/executor/exports/commit_request_handoff_stub.json`
2. `game/scripts/modules/executor/exports/g3_cancel_receipt.json`
3. `game/scripts/modules/executor/exports/g3_complete_receipt.json`
4. `game/scripts/modules/executor/exports/g3_undo_receipt.json`
5. `game/scripts/modules/executor/exports/world_prompt_from_build.json`
6. `game/scripts/modules/persist/exports/g4_persist_smoke_evidence.json`

Diff content: runtime UUIDs, timestamps, receipt links, HMAC seal values — not intentional product design changes.

---

## 2. Correction applied (authorized writers only)

| Wave | Profile | Authority | Action |
|---|---|---|---|
| C0 | executor | `PATCH_DRAFT` | G3 smoke/slice write only to `user://g3_e2e_smoke/`; refuse tracked `res://…/executor/exports`; restore five executor files to `60fccdd` |
| C1 | persist | `PATCH_DRAFT` | G4 evidence only at `user://g4_persist_smoke/`; remove res dual-write; restore g4 evidence to `60fccdd` |
| C2 | core | `VERIFY_ONLY` | Re-run G3=76, G4=22, validator, clean 2.5D boot; prove six-file zero diff |
| C3 | schema | `VERIFY_ONLY` | MAF-validate C0–C2 receipts with installed `jsonschema` |

Restore method: **git blob write** of `60fccdd:<path>` into working tree (no `git reset` / `git checkout` of the six files).

### Product files touched (intentional, minimal)

- `game/scripts/modules/executor/g3_e2e_smoke.gd`
- `game/scripts/modules/executor/g3_onboarding_slice.gd`
- `game/scripts/modules/persist/g4_persist_smoke.gd`

---

## 3. Post-correction executable proof

Log: `orchestration/logs/g8-correction-001-matrix.log`

| Gate | Result |
|---|---|
| G3 E2E | `G3_E2E_SMOKE=PASS checks=76` EXIT=0 |
| G4 persist | `G4_PERSIST_SMOKE=PASS checks=22` EXIT=0 |
| Validator | `AIDLE_VALIDATION=PASS` EXIT=0 |
| Clean fixed-angle 2.5D boot | EXIT=0, marker present |
| Six tracked vs `60fccdd` | **`SIX_TRACKED_EXPORTS_ZERO_DIFF=PASS`** (hash-object match + empty git diff) |
| C0–C2 MAF schema | **PASS** (`Draft202012Validator`) |

Runtime evidence locations after correction:

- G3: `user://g3_e2e_smoke/*`
- G4: `user://g4_persist_smoke/g4_persist_smoke_evidence.json` (+ other user:// journals)

---

## 4. Receipts

| Receipt | Path |
|---|---|
| C0 executor | `orchestration/receipts/g8/correction/C0_executor.json` |
| C1 persist | `orchestration/receipts/g8/correction/C1_persist.json` |
| C2 core | `orchestration/receipts/g8/correction/C2_core.json` |
| C3 schema | `orchestration/receipts/g8/correction/C3_schema.json` |

---

## 5. Remaining risks

1. Codex must **independently** re-run smokes and confirm six-file zero diff.  
2. Tracked export JSON under `res://…/exports` are now **static baseline fixtures**; live run artifacts live only under `user://`.  
3. Historical Directive 19 collate/report claims remain on record as **failed scope honesty** — superseded by this correction, not rewritten as if they never happened.  
4. Headed Human Acceptance Checklist still required for alpha; machine gate still cannot self-ACCEPT.  
5. Older matrix logs may show PowerShell `NativeCommandError` wrapper noise — not product SCRIPT ERROR.

---

## 6. Machine posture for Codex

- Parent returns **`REVIEW_REQUESTED` / `WAITING_CODEX`**.  
- Machine may return to `PASS_FOR_HUMAN_REVIEW` / `HITL_REQUIRED` **only after Codex independent verify**.  
- **Not ACCEPTED.** Parent `self_accept=false`.

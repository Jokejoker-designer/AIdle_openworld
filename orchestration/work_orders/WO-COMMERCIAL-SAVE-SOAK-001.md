# WO-COMMERCIAL-SAVE-SOAK-001

Directive: **99** · Task: `COMMERCIAL-HARDENING-VERIFY` · Checklist gate **#8**
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852`
Primary profile: **`aidle-worldgen-qa-evidence`** (VERIFY_ONLY)
Optional follow Blue: `aidle-worldgen-godot-runtime` / `persist` only if QA finds **blocking** product defect and names exact files.
Status: DISPATCH · `accepted=false` · no self-accept

## Goal

Measure and evidence **save integrity + idempotency + revision-conflict recovery**
for Offline Private Reality (PersistModule signed journal). Produce gate-ready
report for commercial checklist #8. **Do not claim ship.**

## Exact write lease (QA VERIFY_ONLY)

- `orchestration/receipts/commercial_save_soak_001/**`
- `orchestration/logs/commercial_save_soak_001/**`
- `orchestration/evidence/commercial_save_soak_001/**`
- May add **tests only** under `game/tests/**` or `game/scripts/modules/persist/*_smoke.gd` if needed for evidence (no production API change without separate Blue WO).

**Forbidden product patch** on first pass: no `persist_module.gd` / journal_store changes unless a follow-up Blue WO names exact files after Red triage.

## Required work

1. Read: `persist_module.gd`, `g4_persist_smoke.gd`, commercial checklist, vision lock § ownership.
2. Run Godot 4.3:  
   `E:/AIdle_openworld/tools/Godot_v4.3-stable_win64_console.exe --path E:/AIdle_openworld/game --headless -s res://scripts/modules/persist/g4_persist_smoke.gd`
3. Decode UTF-16LE log; record exit code, PASS/FAIL lines, hashes.
4. Enumerate coverage: save/reload hash, duplicate request idempotency, stale revision, tamper/seal, compensation append, cancel not journaled.
5. Gap list: what commercial gate #8 still lacks (soak iterations, revision recovery UX, multi-session).
6. MAF receipt: schema-valid agent_step_contract fields + `evidence_refs` array[string], `accepted=false`, `self_accept=false`, real UUID `writer_transcript_ref` = this child session id.

## Acceptance (machine)

- Persist smoke exit 0 **or** documented FAIL with exact finding IDs.
- Coverage matrix in receipt.
- No product writes unless documented in a separate Blue lease (this WO default: zero product writes).

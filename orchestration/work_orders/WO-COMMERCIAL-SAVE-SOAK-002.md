# WO-COMMERCIAL-SAVE-SOAK-002 — multi-cycle soak + revision conflict evidence

Directive: **99** · After HUMAN_ACCEPT BATCH_COMMERCIAL_003 · Gate **#8** next in order  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852`  
Profiles: QA `aidle-worldgen-qa-evidence` (VERIFY) · Blue `aidle-worldgen-godot-runtime` only if soak finds product defect  
Status: DISPATCH · `accepted=false`

## Goal

Close commercial gaps from QA_save_soak_001:
- G8-GAP-SOAK-ITERATIONS (N-cycle save/reload under loop)
- Strengthen revision-conflict evidence (stale expected_world_revision)
- Document multi-session as simulated sequential sessions (true multi-process optional)

## Lease

- Tests: `game/tests/commercial_save_soak_002.gd` (new) and/or under `game/scripts/modules/persist/`
- Receipts/logs/evidence: `orchestration/{receipts,logs,evidence}/commercial_save_soak_002/**`
- Product persist modules: only if Red/QA finds blocking defect and names exact file

## Acceptance

- Headless soak N≥20 cycles exit 0; integrity PASS each cycle
- Stale revision conflict asserted
- MAF receipt; no ship claim

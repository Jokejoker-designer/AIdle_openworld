# G4-001 Dispatch Map — Directive 12

Parent: existing Grok Desktop conductor only  
Task: G4-001 only  
Final acceptor: Codex (no parent self-ACCEPT)

## Wave order

| Wave | Profile | Authority | Writes |
|---|---|---|---|
| P0_SCHEMA_VERIFY | schema | VERIFY_ONLY | `orchestration/receipts/g4/P0_schema.json` only |
| P1_PERSIST_PATCH | persist | PATCH_DRAFT sole product writer | `game/scripts/modules/persist/**`, `game/scripts/modules/interfaces/i_persist_module.gd`, fixtures/exports/smoke under persist, `orchestration/receipts/g4/P1_persist.json` |
| P2_EXECUTOR_CONSUMER_VERIFY | executor | VERIFY_ONLY | `orchestration/receipts/g4/P2_executor.json` only |
| P3_CORE_RELOAD_VERIFY | core | VERIFY_ONLY | `orchestration/receipts/g4/P3_core.json` only |
| P4_NETWORK_PURPLE | network | VERIFY_ONLY | `orchestration/receipts/g4/P4_network.json` + Purple review md |

## Persist sole ownership (P1)

- `game/scripts/modules/persist/**` (create module, journal, serializer, hashes, compensation)
- `game/scripts/modules/interfaces/i_persist_module.gd`
- Persist smoke + exports under persist module
- Do **not** edit executor product files (consumer only in P2)
- Do **not** edit contracts / tasks / directive / architecture / prior WOs

## Authority boundary

Local/offline Private Reality simulation only. No Shared District / economy / server ownership claims.

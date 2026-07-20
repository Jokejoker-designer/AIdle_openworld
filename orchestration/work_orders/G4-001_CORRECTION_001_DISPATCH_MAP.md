# G4-001 CORRECTION-001 Dispatch Map — Directive 13

Parent: existing Grok Desktop conductor only  
Task: G4-001 CHANGES_REQUESTED correction  
Final acceptor: Codex

## Waves

| Wave | Profile | Authority | Write ownership |
|---|---|---|---|
| R0_SCHEMA_INTEGRITY_VERIFY | schema | VERIFY_ONLY | `orchestration/receipts/g4/R0_schema.json` only |
| R1_PERSIST_SIGNED_JOURNAL_PATCH | persist | PATCH_DRAFT sole journal/integrity writer | `game/scripts/modules/persist/**`, `game/scripts/modules/interfaces/i_persist_module.gd`, smoke/exports; `orchestration/receipts/g4/R1_persist.json` |
| R2_CORE_RUNTIME_MOUNT | core | PATCH_DRAFT sole runtime-mount writer | `game/scripts/main/main.gd` only (replace AgentPersistStub → PersistModule); `orchestration/receipts/g4/R2_core.json` |
| R3_EXECUTOR_CONSUMER_VERIFY | executor | VERIFY_ONLY | `orchestration/receipts/g4/R3_executor.json` only |
| R4_NETWORK_PURPLE | network | VERIFY_ONLY | `orchestration/receipts/g4/R4_network.json` + Purple review md |

## Non-overlap

- persist owns journal seal, key provider boundary, consumer gate API, integrity tests
- core owns only main.gd mount wiring
- neither edits the other's files

# G6-001 CORRECTION-001 Dispatch Map — Directive 18

Parent: existing Grok Desktop conductor only
Task: G6-001 confirmation bypass correction

## Waves

| Wave | Profile | Authority | Writes |
|---|---|---|---|
| R0_SCHEMA_CONFIRM_VERIFY | schema | VERIFY_ONLY | `orchestration/receipts/g6/R0_schema.json` only |
| R1_NETWORK_SERVER_PATCH | network | PATCH_DRAFT sole | `services/world_authority_poc/**` + `R1_network.json` |
| R2_EXECUTOR_GODOT_PATCH | executor | PATCH_DRAFT sole | `game/scripts/modules/network/**` + `R2_executor.json` |
| R3_PERSIST_STATE_VERIFY | persist | VERIFY_ONLY | `R3_persist.json` only |
| R4_CORE_PURPLE | core | VERIFY_ONLY Purple | `R4_core.json` + Purple review md |

## Fix

`submit_proposal` must reject client-supplied `confirmation.state=confirmed` before registration. Only `confirm_proposal` may set confirmed.

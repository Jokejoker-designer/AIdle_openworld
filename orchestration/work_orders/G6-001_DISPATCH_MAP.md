# G6-001 Dispatch Map — Directive 17

Parent: existing Grok Desktop conductor only
Task: G6-001 only
Local authority POC only — not Nakama/Colyseus, no public listener

## Waves

| Wave | Profile | Authority | Write ownership |
|---|---|---|---|
| M0_SCHEMA_AUTHORITY_VERIFY | schema | VERIFY_ONLY | `orchestration/receipts/g6/M0_schema.json` only |
| M1_NETWORK_SERVER_PATCH | network | PATCH_DRAFT sole server writer | `services/world_authority_poc/**` + `orchestration/receipts/g6/M1_network.json` |
| M2_EXECUTOR_CLIENT_PATCH | executor | PATCH_DRAFT sole Godot harness writer | `game/scripts/modules/network/**` + two-client smoke; `orchestration/receipts/g6/M2_executor.json` |
| M3_PERSIST_REPLAY_VERIFY | persist | VERIFY_ONLY | `orchestration/receipts/g6/M3_persist.json` only |
| M4_CORE_TWO_CLIENT_PURPLE | core | VERIFY_ONLY Purple | `orchestration/receipts/g6/M4_core.json` + Purple review |

## Disjoint ownership

- **network:** entire `services/world_authority_poc/`
- **executor:** entire `game/scripts/modules/network/`
- Neither writes the other's tree

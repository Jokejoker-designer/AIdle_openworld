# G5-001 Dispatch Map — Directive 14

Parent: existing Grok Desktop conductor only
Task: G5-001 only
Final acceptor: Codex (parent must not self-ACCEPT)
Provider selection / real credentials: HITL_REQUIRED — out of scope

## Wave order

| Wave | Profile | Authority | Write ownership |
|---|---|---|---|
| A0_SCHEMA_VERIFY | schema | VERIFY_ONLY | `orchestration/receipts/g5/A0_schema.json` only |
| A1_NETWORK_GATEWAY_PATCH | network | PATCH_DRAFT sole gateway writer | `services/agm_gateway/**`, gateway fixtures/tests; `orchestration/receipts/g5/A1_network.json` |
| A2_EXECUTOR_CLIENT_PATCH | executor | PATCH_DRAFT sole Godot paid-adapter writer | `game/scripts/modules/bridge/paid_gateway_adapter.gd` (or under executor if claimed exclusively), interface/smoke; **disjoint from network**; `orchestration/receipts/g5/A2_executor.json` |
| A3_CORE_EDITION_VERIFY | core | VERIFY_ONLY | `orchestration/receipts/g5/A3_core.json` only |
| A4_PERSIST_PURPLE | persist | VERIFY_ONLY (Purple) | `orchestration/receipts/g5/A4_persist.json` + Purple review md |

## Disjoint files

- **network owns:** entire `services/agm_gateway/` tree (Python or pure scripts, no provider SDK)
- **executor owns:** Godot paid client adapter + smoke under game/ only
- Neither may write the other's paths

## Forbidden

- Real provider calls, credentials, outbound network enablement
- Provider SDKs in Godot or gateway
- Secrets in fixtures/logs/receipts
- Dependency install, push, deploy, public listener
- tasks.json / codex_directive / architecture / contracts edits

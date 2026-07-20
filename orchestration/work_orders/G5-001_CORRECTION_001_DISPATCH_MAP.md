# G5-001 CORRECTION-001 Dispatch Map — Directive 15

Parent: existing Grok Desktop conductor only
Task: G5-001 CHANGES_REQUESTED correction
Final acceptor: Codex

## Waves

| Wave | Profile | Authority | Writes |
|---|---|---|---|
| C0_SCHEMA_VERIFY | schema | VERIFY_ONLY | `orchestration/receipts/g5/C0_schema.json` only |
| C1_NETWORK_GATEWAY_PATCH | network | PATCH_DRAFT sole writer | `services/agm_gateway/**` only + `orchestration/receipts/g5/C1_network.json` |
| C2_EXECUTOR_CONSUMER_VERIFY | executor | VERIFY_ONLY | `orchestration/receipts/g5/C2_executor.json` only |
| C3_CORE_EDITION_VERIFY | core | VERIFY_ONLY | `orchestration/receipts/g5/C3_core.json` only |
| C4_PERSIST_PURPLE | persist | VERIFY_ONLY Purple | `orchestration/receipts/g5/C4_persist.json` + Purple review md |

## Four mandatory fixes (network product)

1. Server caps are hard upper bounds; client may only tighten
2. Reject bool/negative/NaN/±Inf/non-numeric budget fields before dispatch
3. Non-fixture ProviderInterface rejected with real-provider authority off even if provider_mode=fixture
4. Idempotency bound to canonical fingerprint of redacted inputs; conflict on ID reuse with different payload

# G8-001 Dispatch Map — Directive 19

Parent: existing Grok Desktop conductor only  
Task: G8-001 Independent 2.5D Alpha Evidence Gate  
Authority: **VERIFY_ONLY** for all eight domain profiles  
Final machine acceptor: Codex · Final alpha: Human Product Lead  

## Wave order

| Wave | Actors | Authority | Writes |
|---|---|---|---|
| Z0_EIGHT_DOMAIN_VERIFY | schema, core, manifestation, companion, asset, executor, persist, network | VERIFY_ONLY each | Only own `orchestration/receipts/g8/G8_<profile>.json` |
| Z1_INTEGRATED_MATRIX | parent | HUMAN_APPROVAL_REQUIRED collate | matrix log + collated evidence index |
| Z2_PURPLE_ALPHA_VERDICT | parent (collates 8 + purple notes) | report | `G8-001_ALPHA_EVIDENCE_REPORT.md` |
| Z3_HITL_HANDOFF | parent | HITL_REQUIRED if PASS | `HUMAN_ACCEPTANCE_CHECKLIST.md` + `grok_status.json` only |

## One writer per evidence file

| Profile | Receipt path |
|---|---|
| schema | `orchestration/receipts/g8/G8_schema.json` |
| core | `orchestration/receipts/g8/G8_core.json` |
| manifestation | `orchestration/receipts/g8/G8_manifestation.json` |
| companion | `orchestration/receipts/g8/G8_companion.json` |
| asset | `orchestration/receipts/g8/G8_asset.json` |
| executor | `orchestration/receipts/g8/G8_executor.json` |
| persist | `orchestration/receipts/g8/G8_persist.json` |
| network | `orchestration/receipts/g8/G8_network.json` |

Parent-only: dispatch map, `G8-001.json` collate, alpha evidence report, human checklist, `grok_status.json`.

## Forbidden

- Product/test/contract/task/directive/architecture/prior evidence patches
- Nested grandchildren, self-ACCEPT, install, live provider/network, push/deploy/publish

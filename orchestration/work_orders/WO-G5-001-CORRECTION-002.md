# Work Order — G5-001 Correction 002 (MAF evidence only)

Final acceptor: Codex. Continue only in the existing Grok Desktop parent.

## Scope

Use only installed profile `persist` with `VERIFY_ONLY` authority. The profile
may amend its own evidence file:

- `orchestration/receipts/g5/C4_persist.json`

No product, test, contract, architecture, task, directive, prior receipt or
review file may be changed. The parent may update only `grok_status.json` after
the receipt is valid. No nested grandchildren and no self-acceptance.

## Required correction

Add the required top-level `smoke_test` property to `C4_persist.json`. It must
truthfully reference the already executed C4 verification or be `null` if that
is the canonical representation. Do not invent a command, result or evidence.

Validate these six files directly against:

`E:/standards/maf/schemas/agent_step_contract.schema.json`

- `orchestration/receipts/G5-001-CORRECTION-001.json`
- `orchestration/receipts/g5/C0_schema.json`
- `orchestration/receipts/g5/C1_network.json`
- `orchestration/receipts/g5/C2_executor.json`
- `orchestration/receipts/g5/C3_core.json`
- `orchestration/receipts/g5/C4_persist.json`

The documented `agentwork_runtime validate-step` command is unavailable in the
current MAF venv (`No module named agentwork_runtime`), so use the canonical
JSON Schema directly with the already available `jsonschema` library. Do not
install or repair dependencies in this work order.

Finish `REVIEW_REQUESTED`/`WAITING_CODEX`, update only `grok_status.json`, and
wait for Codex. Product tests do not need to be rerun because no product file is
authorized to change.

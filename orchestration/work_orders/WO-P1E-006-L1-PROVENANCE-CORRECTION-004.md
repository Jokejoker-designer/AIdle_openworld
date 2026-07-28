# WO-P1E-006-L1-PROVENANCE-CORRECTION-004

Authority: `VERIFY_ONLY` | State: `READY`

Issued by Codex under Directive 55. Product gates for P1E-006 have passed. This
work order closes only provenance finding F10 in
`orchestration/reviews/CODEX_P1E-006_REVIEW_004.json`.

## Workflow

- Use only Grok Desktop parent `019f7ffd-3995-71c0-aca1-51078e24a852`.
- Parent is coordinator-only and may spawn exactly one fresh real installed
  `schema` child. No resume, follow-up child, grandchild or support profile.
- Profile: `.grok/agents/schema.md`; TrustLayer: `devil-advocate`; UI:
  `ui-brief-writer`; authority: `VERIFY_ONLY`.
- Load all five mandatory skills and the schema profile's routed skills fully.
- Do not patch product, tests, old receipts, old logs, screenshots, task state,
  directive or Grok status.

## Mission

Create an append-only provenance ledger that records the truth without
rewriting history:

- Original L1 runner:
  `019f8679-e256-7643-bf4c-7511adbdd4a2`.
- Unauthorized correction writer:
  `019f867d-c1d4-7dc3-9eac-5a0d8d5e5027`.
- Bind both real `meta.json` paths, SHA-256 values, exact `started_at` and
  `completed_at` values, parent ID and prompts.
- Hash the current L1 receipt and log. State explicitly that the receipt was
  rewritten by the correction child even though its `child_task_ref` names the
  original runner.
- Record that Directive 54's exact-three-child requirement was violated and
  that the extra child is not being retroactively authorized.
- Validate L0, L1 and L2 receipts against
  `E:/standards/maf/schemas/agent_step_contract.schema.json`.
- Bind Codex review 004 and report product gate
  `PASS_PENDING_PROVENANCE`; do not claim task acceptance.

## Exclusive writer lease

- `orchestration/receipts/p1e/P1E_006_l1_provenance_schema_005.json`
- `orchestration/logs/p1e-006-l1-provenance-schema-005.log`

The child must embed its command output in the declared log and create no
temporary file. Receipt must be schema-valid with its own real child ID,
`accepted=false`, `self_accept=false`, non-null verdict, `product_writes=[]`,
and `completion_signal=WAITING_CODEX`.

## Hard stops

No product/test/evidence rewrite, no second child, no P2E-P6E, Control,
Character Foundry, network, install, Godot change, credential, live provider,
push, deploy or publish. Red F01 remains a hard stop before network/shipping.

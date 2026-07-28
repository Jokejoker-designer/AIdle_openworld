# Codex Grok skill-agent-workflow guard

- Automation: `aidle-grok-skill-agent-workflow-guard-15m`
- Checked at: `2026-07-21T09:49:44+07:00`
- Agent character: `risk-officer`
- Authority: `REPORT_ONLY` with `VERIFY_ONLY` orchestration gate
- Task: `G8-001`
- Verdict: `CHANGES_REQUESTED`
- Acceptance: `false`

## Compliant evidence

- Exactly one Grok Desktop process exists: PID `1496`, executable-only command
  line, with the authorized parent session
  `019f7ffd-3995-71c0-aca1-51078e24a852`; no Grok CLI process was found.
- Directive 27 ultimately ran the correct sequential child resumes under that
  parent: executor E0 `019f828a-5064-7c12-ac2c-69c5d8155d3a`, then core E1
  `019f828d-83a0-7691-ada9-d767d90ba841`. Both have durable child sessions and
  neither contains nested subagents.
- E0 did not run the headed runner. E1 alone rewrote headed logs, ten PNGs, and
  the manifest. D2/D3 remain blocked, `accepted=false`, `self_accept=false`,
  and `parent_product_patch=false`.
- Both receipts pass direct JSON Schema validation; declared context hashes
  recompute exactly. Installed profile, TrustLayer/UI character, five always
  skills, and routed-skill sources all exist.

## Blocking violations

1. A separate unauthorized top-level Grok task
   `019f8289-5794-72d2-88fc-26f1e04faff8` was created at 09:37 local instead
   of using the sole authorized Desktop parent. Its child
   `019f828b-57c0-72c2-99ee-fcf2d7d9866a` was cancelled. Both refs and every
   output from that lineage are quarantined and cannot be evidence.
2. E0/E1 receipt end times are internal receipt-finalize wall clocks, not their
   durable completed wrapper metadata. E1 start time is also about 13 seconds
   later than the durable wrapper start.
3. Core omits `_d1_core_e1_set_end.py` from `files_written` and omits two helper
   scripts it executed from `files_read`.
4. Core retains an abbreviated aggregate command while self-auditing all
   commands as literal.
5. E1 appended incompatible encoding into `g8-d1-core-child.log`; its new child
   ref is not recoverable through normal text search, so the cited trace is not
   clean observability evidence.
6. Bootstrap still has its known parser error near line 52. COMPLIANCE, x16/UI
   registries, MASTER_PLAN, JOURNAL_LATEST, active blueprint/architecture lock,
   skills manifest, schema, and the three mandatory skills were loaded manually.

## Guard action

Directive 28 and `WO-G8-001-D1-RECEIPT-FINALIZER-008.md` preserve
`CHANGES_REQUESTED`. The same authorized Desktop parent must spawn exactly one
real `aidle-schema` child to post-finalize the two receipts from durable worker
metadata, repair complete file/command/trace provenance, and return
`WAITING_CODEX`. No product or headed-evidence rerun is allowed; D2/D3 remain
blocked.


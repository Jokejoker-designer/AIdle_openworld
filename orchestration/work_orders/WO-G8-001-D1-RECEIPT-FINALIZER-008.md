# WO-G8-001-D1-RECEIPT-FINALIZER-008

Directive: 28  
Task: G8-001  
State: CHANGES_REQUESTED  
Authority: VERIFY_ONLY  
Parent: existing Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852` only

## Why a finalizer is required

Directive 27 ran the intended sequence in the correct parent:

- E0 executor `019f828a-5064-7c12-ac2c-69c5d8155d3a`, durable metadata
  `2026-07-21T02:38:50.514725600Z` to
  `2026-07-21T02:42:06.058939300Z`;
- E1 core `019f828d-83a0-7691-ada9-d767d90ba841`, durable metadata
  `2026-07-21T02:42:20.258506100Z` to
  `2026-07-21T02:44:41.775646100Z`.

Both receipts pass the base schema and contain the required lineage,
characters, skills, no-grandchildren, `product_writes=[]`, and
`self_accept=false`. They still fail semantic review because their top-level
`start_time` / `end_time` were written before the child completed and therefore
do not equal the durable metadata above. Cold review also found incomplete file
provenance, one abbreviated command entry, and a corrupted E1 trace.

## Quarantined accidental task

The automation accidentally created top-level task
`019f8289-5794-72d2-88fc-26f1e04faff8`. It and its child
`019f828b-57c0-72c2-99ee-fcf2d7d9866a` are unauthorized and must never be
used as execution or acceptance evidence. The child was cancelled. Its outputs
are quarantined even where later authorized children overwrote the same logs.

The 10:04 independent guard found both top-level session IDs still present in
`C:/Users/phant/.grok/active_sessions.json` on PID `1496`. One Desktop process
does not satisfy the one-parent rule while two top-level sessions remain active.
Before spawning the finalizer, deactivate the unauthorized top-level task
`019f8289-...` through the existing Desktop workflow. Do not resume it, create a
replacement top-level task, use Grok CLI, or edit Grok session files manually.

## Required real Desktop schema finalizer

The existing parent must spawn exactly one real child from
`E:/AIdle_openworld/.grok/agents/schema.md`; no new top-level task and no nested
children. Bind its configured TrustLayer/UI characters, `VERIFY_ONLY`, all five
`skills_manifest.yaml:always` skills, and the schema/evidence routed skills
required by its profile/work order.

The finalizer owns only:

- `orchestration/receipts/g8/subagent_workflow_remediation_004/D1_executor.json`
- `orchestration/receipts/g8/subagent_workflow_remediation_004/D1_core.json`
- `orchestration/receipts/g8/subagent_workflow_remediation_004/D1_finalizer.json`
- `orchestration/logs/g8-d1-receipt-finalizer.log`

It must:

1. Read the durable parent `meta.json` for E0 and E1.
2. Set each execution receipt's `start_time` / `end_time` exactly to the
   corresponding durable `started_at` / `completed_at` strings above.
3. Preserve execution `child_task_ref`, `original_child_task_ref`,
   `prior_correction_ref`, and `correction_task_ref`; add
   `receipt_finalizer_transcript_ref` for the finalizer child and state clearly
   that execution and receipt-finalization are distinct.
4. Preserve character/skills/commands/files evidence; do not rerun any product,
   G3/G4, or headed command.
   - Add `orchestration/logs/_d1_core_e1_set_end.py` to the core
     `files_written` evidence.
   - Add `orchestration/logs/_d1_core_input_hash.py` and
     `orchestration/logs/_d1_core_schema_validate.py` to core `files_read`.
   - Remove the `twelve literal git ... pairs above` pseudo-command or classify
     it outside `smoke_test.commands`; every command entry must contain the
     literal executed command and exit code.
   - The E1 append to `g8-d1-core-child.log` used incompatible encoding and its
     new child ref is not normally searchable. Disclose that legacy trace
     defect and write the finalizer trace as clean UTF-8; do not erase or
     silently normalize the historical file.
5. Add quarantine refs for accidental top-level `019f8289-...` and cancelled
   child `019f828b-...`; neither may appear as accepted execution lineage.
6. Validate both updated receipts plus `D1_finalizer.json` directly against
   `E:/standards/maf/schemas/agent_step_contract.schema.json`.
7. Return `CHANGES_REQUESTED / WAITING_CODEX`, `accepted=false`,
   `self_accept=false`, `parent_product_patch=false`,
   `d2_spawn_allowed=false`, and `d3_spawn_allowed=false`.
8. Receipt/status evidence must show exactly one active top-level Desktop parent:
   `019f7ffd-3995-71c0-aca1-51078e24a852`.

No product/test/harness/evidence PNG mutation, no Grok CLI, new top-level task,
install, push, deploy, publish, Control 1B, D2/D3, or acceptance.

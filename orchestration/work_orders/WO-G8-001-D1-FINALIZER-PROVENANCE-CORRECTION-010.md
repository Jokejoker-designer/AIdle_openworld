# WO-G8-001-D1-FINALIZER-PROVENANCE-CORRECTION-010

Directive: 30  
Task: G8-001  
State: CHANGES_REQUESTED  
Authority: VERIFY_ONLY  
Parent: existing Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852` only

## Independent guard finding

Directive 28 used the correct Desktop parent and a real `aidle-schema` child
`019f82c6-187a-7932-81ed-9011410b6661`. The child has no grandchildren,
loaded the required character/UI/skills, changed only its four leased files,
did not mutate PNG/product evidence, and produced three receipts that pass the
base MAF JSON Schema.

The finalizer receipt is not acceptable command provenance:

- its transcript contains 11 `run_terminal_command` calls;
- one call failed with exit code 1 while attempting to write
  `D1_finalizer.json`;
- `D1_finalizer.json` records only four commands;
- none of those four command strings exactly equals a terminal command in the
  durable transcript;
- all 11 actual terminal command strings are omitted;
- receipt `end_time` is `2026-07-21T03:48:32.3706120Z`, while durable child
  metadata completed at `2026-07-21T03:48:58.803743900Z`.

Directive 29 released D2 from schema-level checks without this transcript
comparison. That release is superseded; no fresh D2 child had spawned when the
guard rechecked at 10:53 +07:00.

## Required real Desktop correction child

The same existing parent must spawn exactly one new real child from
`E:/AIdle_openworld/.grok/agents/schema.md`. No new top-level task and no nested
children.

Bind TrustLayer `devil-advocate`, UI `ui-brief-writer`, authority
`VERIFY_ONLY`, all five `skills_manifest.yaml:always` skills in full, and
`od-design-brief`, `od-reference-design-contract`, and
`evidence-memory-ledger` in full. Every skill entry needs exact source, mode and
transcript-backed load evidence.

The correction child owns only:

- `orchestration/receipts/g8/subagent_workflow_remediation_004/D1_finalizer.json`;
- `orchestration/receipts/g8/subagent_workflow_remediation_004/D1_finalizer_correction.json`;
- `orchestration/logs/g8-d1-finalizer-command-correction.log`.

It must:

1. Read the completed child meta and durable transcript for
   `019f82c6-187a-7932-81ed-9011410b6661`.
2. Preserve the prior finalizer child ref and add a distinct
   `receipt_correction_child_ref` for this correction child.
3. Replace the prior finalizer command ledger with all 11 literal terminal
   command strings exactly as present in the transcript and their actual exit
   codes, including the failed `exit_code=1` command. Do not invent substitute
   commands.
4. Set the prior finalizer receipt `end_time` and
   `durable_completed_at` exactly to
   `2026-07-21T03:48:58.803743900Z`; preserve
   `receipt_writer_end_time=2026-07-21T03:48:32.3706120Z` separately.
5. Create `D1_finalizer_correction.json` as an `agent_step_contract`. Its own
   command ledger must contain every terminal command actually used by the
   correction child, exactly, with exit codes. Material non-terminal tool calls
   must be identified by transcript ref and purpose.
6. Use file-editor tools for the final receipt/log writes. Do not use terminal,
   Python, or PowerShell to write files after the command ledger is finalized.
   Do not run another terminal command after the final writes.
7. Leave schema validation and semantic acceptance to Codex. Report
   `WAITING_CODEX`, `accepted=false`, `self_accept=false`,
   `parent_product_patch=false`, `d2_spawn_allowed=false`, and
   `d3_spawn_allowed=false`.

## Hard forbidden

- No Grok CLI, new top-level session, or nested grandchild.
- No product, G3, G4, headed, PNG, evidence, or harness execution/mutation.
- No parent edit of worker receipts.
- No D2/D3, Control 1B, install, push, deploy, publish, or acceptance.


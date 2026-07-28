# WO-G8-001-D1-FINALIZER-PROVENANCE-CORRECTION-011

Directive: 31  
Task: G8-001  
State: CHANGES_REQUESTED  
Authority: VERIFY_ONLY  
Parent: existing Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852` only

## Accepted portion from Directive 30

`D1_finalizer.json` now passes direct transcript comparison: all eleven prior
terminal commands and exits match exactly in order, including the failed
`exit_code=1`, and its durable completion is bound correctly. Do not modify it.

## Blocking correction-child provenance

Real correction child `019f82d1-ce77-7b63-9ccd-19595307939f` completed under
the correct parent with no grandchildren and no product writes. Its correction
receipt is not acceptable:

- durable transcript has 17 terminal calls; receipt records 18;
- record 18 is a synthetic `self:build_d1_finalizer_correction` command that
  does not exist in the transcript;
- six temporary helper files were created outside the three-file lease and
  omitted from `files_written`;
- material `write` and `search_replace` calls are not listed with transcript
  refs and purposes.

## Required real schema child

Spawn exactly one fresh child from `.grok/agents/schema.md`, under the same
Desktop parent. Bind TrustLayer `devil-advocate`, UI `ui-brief-writer`,
`VERIFY_ONLY`, all five manifest-always skills, and the same three routed skills
from WO-010. No grandchildren.

Read the durable transcript and metadata for
`019f82d1-ce77-7b63-9ccd-19595307939f`. Create:

- `orchestration/receipts/g8/subagent_workflow_remediation_004/D1_finalizer_correction_2.json`
- `orchestration/logs/g8-d1-finalizer-command-correction-2.log`

The new receipt must:

1. Supersede `D1_finalizer_correction.json` without rewriting it.
2. Record the prior correction child durable start
   `2026-07-21T03:56:55.801940Z` and completion
   `2026-07-21T04:01:28.492947800Z`.
3. Record exactly all 17 prior correction-child terminal command strings in
   transcript order and their actual exits. There are two `exit_code=1` calls.
   Do not add a self-command or substitute command.
4. Enumerate material non-terminal `write` and `search_replace` calls with
   exact tool-call refs, target files and purposes.
5. Disclose the six out-of-lease temporary files and the lease violation.
6. Keep `product_writes=[]`, `self_accept=false`, `accepted=false`, and route
   to `WAITING_CODEX` with D2/D3 blocked.

## Bounded cleanup lease

The new child may delete only these six child-created untracked temporary
artifacts, using one literal `Remove-Item -LiteralPath` terminal command before
the final receipt/log writes:

- `orchestration/logs/_tmp_extract_finalizer_cmds.py`
- `orchestration/logs/_tmp_d1_finalizer_cmd_extract.json`
- `orchestration/logs/_tmp_build_d1_finalizer_corrected.py`
- `orchestration/logs/_tmp_extract_correction_cmds.py`
- `orchestration/logs/_tmp_d1_correction_cmd_extract.json`
- `orchestration/logs/_tmp_build_d1_finalizer_correction.py`

The cleanup command and exit belong in the new child's own command ledger.
After the ledger is known, use editor tools for the final receipt and log. Run
no terminal command after those final writes and create no helper artifact.
List all material read/write/editor tool calls in the receipt.

For this new child, record its exact durable `started_at` when available and
its honest `receipt_writer_end_time`. Do not predict its own durable completion.
Codex will bind `completed_at` from child metadata in the independent review;
no further worker-finalizer chain is required for that metadata.

## Hard forbidden

- No change to `D1_finalizer.json`, D1 core/executor receipts, product, tests,
  contracts, harness, headed evidence, screenshots, or shared logs.
- No Grok CLI, new top-level session, grandchild, D2/D3, Control 1B,
  dependency installation, push, deploy, publish, or acceptance.

Parent returns `CHANGES_REQUESTED / WAITING_CODEX`, the fresh child ref,
`parent_product_patch=false`, `d2_spawn_allowed=false`,
`d3_spawn_allowed=false`, and `accepted=false`.

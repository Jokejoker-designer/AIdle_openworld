# WO-G8-001-D1-WORKFLOW-CORRECTION-007

Directive: 27  
Task: G8-001  
State: CHANGES_REQUESTED  
Authority: VERIFY_ONLY orchestration gate  
Parent: existing Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852` only

## Blocking findings

The Directive 26 children are real resumed Grok Desktop children and both base
receipts pass JSON Schema, but the semantic gate still fails:

1. Core receipt `start_time` / `end_time` do not equal its durable correction
   metadata (`2026-07-21T02:24:18.718689700Z` /
   `2026-07-21T02:27:21.813816500Z`).
2. Executor leaves top-level `start_time` / `end_time` at the original D1 run,
   omits `original_child_task_ref`, `original_start_time`, and
   `original_end_time`, and omits the TrustLayer/UI source paths from
   `result.character_binding`. Its durable correction metadata is
   `2026-07-21T02:24:18.756902900Z` /
   `2026-07-21T02:28:27.952392800Z`.
3. Executor ran the core-owned canonical headed runner. That runner writes
   `orchestration/logs/g8-ui-visual-correction-003-runner.log`,
   `orchestration/logs/g8_headed_smoke_godot.log`, the ten headed PNGs, and
   `evidence_manifest.json`. These writes are outside the executor lease and
   are missing from executor `files_written`; `product_writes=[]` does not make
   the evidence side effects read-only.

## Required sequential real-child correction

The parent remains coordinator-only. Use real Desktop child resumes from the
installed profiles under `E:/AIdle_openworld/.grok/agents`; never rewrite either
receipt in the parent and never spawn grandchildren.

### E0 — executor first

Resume executor lineage
`019f827d-02f9-7192-bf77-1315725acaa4` from original
`019f8273-9fae-7a93-ae0c-b06e05d2ff6b`.

- Do not execute `scripts/run_g8_headed_visual_c003.py` and do not write any
  core-owned evidence or logs.
- Correct the receipt with original and new correction refs, exact durable
  metadata times for the new pass, preserved original D1 times, full
  TrustLayer/UI character source paths, all five manifest `always` skills plus
  `game-ui-icons`, exact files read/written, trace/handoff, and literal commands
  with exits.
- Disclose the Directive 26 outside-lease headed-runner side effects as a prior
  workflow finding; do not erase them or call them read-only.
- `product_writes=[]`, `self_accept=false`, and next route
  `E1_CORE_SOLE_EVIDENCE_OWNER`.

### E1 — core only after E0 completes

Resume core lineage `019f827d-02f8-7763-9c7f-d7399d55222d` from original
`019f8273-9fad-7ed2-9e8c-792f59e6f583`.

- Core is the sole owner allowed to rerun the canonical headed runner and
  rewrite its logs/PNGs/manifest.
- Correct the receipt with original, Directive 26, and new correction refs;
  exact durable metadata times for the new pass; all five manifest `always`
  skills plus `game-ui-icons` and `game-asset-core`; exact character sources;
  complete files/commands/exits; trace/handoff; and schema validation.
- `product_writes=[]`, `self_accept=false`, and next route
  `D2_BLOCKED_PENDING_CODEX`.

## Dependency gate

After E1, set `CHANGES_REQUESTED / WAITING_CODEX`, `accepted=false`,
`self_accept=false`, `parent_product_patch=false`, and
`d2_spawn_allowed=false`. Record both new correction transcript refs. D2/D3
remain blocked until an independent Codex semantic review. The quarantined
premature D2 outputs remain non-evidence.

No new top-level session, Grok CLI, support profile, install, push, deploy,
publish, Control 1B, self-accept, or parent product/evidence patch.

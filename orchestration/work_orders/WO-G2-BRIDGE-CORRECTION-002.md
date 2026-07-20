# Work Order — G2-005 Bridge Correction 002

Authority: `PATCH_DRAFT`  
Final acceptor: Codex  
Directive: 8  
Task: `G2-005`

## Objective

Repair the existing Free Desktop Bridge implementation without replacing or
rolling back accepted code.

## Required corrections

- Fix `BridgePaths` and bridge helper loading under standalone Godot `--script`.
- Fix dialog/window type mismatches and inferred-null parse errors.
- Make the Godot smoke fail when any required script cannot load. A printed PASS
  beside a parse, compile, script, or runtime error is a failure.
- Preserve visible manual consent, clipboard/file-only transport, no networking,
  stale/replay rejection, and explicit secret deny-lists.

## Write scope

- `game/scripts/modules/bridge/**`
- Free Desktop Bridge UI scripts/scenes directly required by this task
- `game/scripts/modules/interfaces/i_desktop_bridge_module.gd`
- `orchestration/receipts/G2-005.json`

Do not edit task/control/architecture/contract files or create acceptance files.
Return `REVIEW_REQUESTED` with changed files, exact commands, logs, residual
risks, and a valid MAF step-contract receipt.


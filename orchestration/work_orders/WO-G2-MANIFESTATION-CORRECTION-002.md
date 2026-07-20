# Work Order — G2-001/G2-002 Manifestation Correction 002

Authority: `PATCH_DRAFT`  
Final acceptor: Codex  
Directive: 8  
Tasks: `G2-001`, `G2-002`

## Objective

Repair presentation-only headless rendering errors while preserving the
existing fixed-angle 2.5D world and progressive manifestation behavior.

## Required corrections

- Skip presentation-only mesh/material construction when Godot uses the
  headless or dummy renderer; do not suppress, filter, or relabel real errors.
- Preserve wireframe → hologram → materialize ordering, cancellation,
  reduced-motion behavior, and non-durable previews.
- The manifestation smoke and integrated headless boot must have no
  `SCRIPT ERROR`, `Parse Error`, `Compile Error`, or `ERROR:` lines.

## Write scope

- `game/scripts/modules/manifestation/**`
- The minimum existing core presentation files directly causing G2-001's
  headless mesh errors
- `orchestration/receipts/G2-001.json`
- `orchestration/receipts/G2-002.json`

Do not edit bridge, companion, executor, task/control/architecture/contract
files or create acceptance files. Return `REVIEW_REQUESTED` with changed files,
exact commands, full logs, residual risks, and valid MAF step-contract receipts.


# WO-TOWN-STREET-IMPORT-001

**Status:** Phase A STRUCTURE PASS · fidelity HIGH_PARTIAL (strike 2/3 on mesh family) · Phase B SKIPPED  
**Authority:** PATCH_DRAFT  
**accepted / self_accept:** false  
**Purple:** WAITING  

## Scope

Bring `TOWN_FAIRY_STREET_PLAN_V1` stone path network into game, additive only.

| Phase | Content | Decision |
|-------|---------|----------|
| **A** | `stone_path_network` 13 segments | **In game** — MultiMesh `cozy_path_stone_A` (1634 tiles) |
| **B** | `wood_platforms` 12 decks | **Skip** — no `cozy_wood_deck_A` / boardwalk GLB; no fake placeholders |

## Implementation (done)

- `game/scripts/modules/town/town_street_loader.gd` — STREET_V2c MultiMesh dense fill
- `game/resources/town/town_fairy_street_plan_v1.json` (runtime copy of design plan)
- `main.gd` `ENABLE_TOWN_STREET_PATHS` + `_mount_town_street_paths()`
- Headed QA: `game/tests/town_street_headed_qa_001.gd` (`godot -s …`)
- Evidence: `orchestration/evidence/town_street_import_001/` (v2c log + 7 captures)
- Receipts: `orchestration/receipts/town_street_import_001/REDO_LOOP_ITERATIONS_001.json` (n=3)

## Lessons

- V2a dense Node3D (1875) → D3D12 descriptor heap OOM — do not instance N full GLB nodes for paths
- MultiMeshInstance3D = dense continuous ribbon, GPU-safe
- Residual HIGH_PARTIAL is **asset family** (cobble cluster vs flat SVG paver), not spacing

## Non-goals

- Do not edit `town_grid_loader.gd` plot logic, `town_grid_plan_v1.json`, or `town_layout_10phase.json`
- Do not fabricate Phase B decks
- Do not continue HOME.BLD house passes (NEED_HUMAN strike-3)

## Fidelity law

Iterate stone path presentation to match fairy-street plan SVG / MOCKUP_SSOT_V2, or 3-strike NEED_HUMAN per segment.
Signature `stone_cluster_tiles_not_continuous_paver_sheet` at **strike 2**.

# WO-UCBV-001 C3-F01 navigation warning correction 006

Status: `READY UNDER CODEX DIRECTIVE 90`  
Task: `UCBV-001` only  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852` coordinator-only  
Authority: `PATCH_DRAFT`

## Purpose

Correct only Red finding `C3-F01`. C3 is accepted as a findings-only audit;
C4 and C5 remain blocked. Do not redesign the character, block catalog,
controls, delete flow, animation adapter or World Commit path.

## ARCHITECTURE LOCK

- Runtime: pinned local Godot `4.3-stable`, fixed-angle 2.5D Private Reality.
- Source root: `E:/AIdle_openworld/game`; Main entrypoint:
  `game/scripts/main/main.gd`.
- Navigation bake owner for this correction:
  `game/scripts/modules/asset/glb_intake_runtime_builder.gd`.
- Canonical world mutation remains World Commit only. Navigation is runtime
  presentation/pathfinding support and may not become a client mutation path.
- Deployment target is the offline vertical slice. No network, shipping,
  dependency installation or Godot version change.
- Blueprint v1.1 and `orchestration/ARCHITECTURE_LOCK.md` are authoritative;
  older/deprecated implementation paths are reference-only.
- Do not translate this runtime correction into a deprecated stack.

## Worker

- Spawn exactly one fresh child from the exact existing parent.
- Installed profile: `.grok/agents/aidle-worldgen-godot-runtime.md`.
- TrustLayer: `blue-team-p0-remediator`; UI: `ui-app-dashboard`.
- Authority: `PATCH_DRAFT`; five mandatory skills plus `architecture-lock`,
  full EOF.
- No grandchildren, support profiles or parent product patch.
- `accepted=false`, `self_accept=false`; never spawn C4 or C5.

## Exact lease

Product/test writes only:

- `game/scripts/modules/asset/glb_intake_runtime_builder.gd`
- `game/tests/ucbv_001_navigation_warning_smoke.gd`

Orchestration writes only:

- `orchestration/receipts/ucbv_001/correction_005/C3F01_navigation_warning_correction_005.json`
- `orchestration/logs/ucbv_001/correction_005/C3F01_navigation_warning_correction_005.log`

The new test file may be omitted if no static contract test is needed, but no
other test file may be edited. Existing
`game/tests/ucbv_001_inputmap_e2e_smoke.gd` is read/run-only.

## Required correction

1. Replace the runtime `MeshInstance3D + PlaneMesh` navigation bake source with
   a Godot-4.3-valid collision-shape source or procedural CPU source geometry.
   Configure the `NavigationMesh` parser accordingly. Do not read visual mesh
   geometry back from RenderingServer at runtime.
2. Preserve the intended `agent_radius=0.4` and `agent_height=1.6` if practical
   by selecting `cell_size` and `cell_height` whose ratios are integral within
   a documented tolerance. If dimensions must change, justify the exact values
   and prove player navigation/collision remains compatible. Never silence or
   filter engine warnings.
3. Preserve the 48m walkable ground coverage, advisory navigation metadata,
   headless lifecycle safety, existing node/group contracts and no broad
   rebaking expansion.
4. Add a focused static/runtime smoke only within the leased test path if it
   materially prevents regression. It must assert collision/procedural source
   selection and voxel alignment without faking engine output.
5. Run the existing normal Main InputMap E2E exactly:

   `E:/AIdle_openworld/tools/Godot_v4.3-stable_win64_console.exe --headless --path E:/AIdle_openworld/game -s res://tests/ucbv_001_inputmap_e2e_smoke.gd`

   It must exit `0`, retain
   `AIDLE_UCBV001_INPUTMAP_E2E_SMOKE=PASS checks=17 inputs=34`, and emit zero
   occurrences of all three C3-F01 signatures:
   - `Source geometry parsing for navigation mesh baking had to parse RenderingServer meshes at runtime`
   - `Property agent_height is ceiled to cell_height voxel units and loses precision`
   - `Property agent_radius is ceiled to cell_size voxel units and loses precision`
6. Rerun the focused navigation smoke if created and the existing UCBV
   integration smoke. Record literal commands, exits and unfiltered stdout/
   stderr in the single leased log.
7. Receipt must validate against `agent_step_contract.schema.json`, bind the
   real child UUID, declare exact hashes/bytes, `out_of_lease_writes=[]`,
   `REVIEW_REQUESTED`, `accepted=false`, `self_accept=false`, and route to
   Codex. Durable parent `meta.json` time remains canonical.

## Forbidden

No C3-F02 provenance edit in this correction; no character/GLB/adapter/catalog/
input/delete redesign; no motion-kit edit; no P2E-002; no evidence rewrite; no
helper file under the repo; no dependency install, Godot version change,
credential, live provider, public network, push, deploy, publish or shipping.
Red F01 remains a hard stop.

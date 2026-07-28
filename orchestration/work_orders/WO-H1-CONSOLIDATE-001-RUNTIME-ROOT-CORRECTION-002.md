# WO-H1-CONSOLIDATE-001-RUNTIME-ROOT-CORRECTION-002

## Authority

Directive 76 authorizes the second and final automatic correction attempt for
the repeated `H1-CODEX-F01` signature plus the remaining HUD fixture wording.
H1 remains `CHANGES_REQUESTED`, `accepted=false`; Human gate closed.

Use only parent `019f7ffd-3995-71c0-aca1-51078e24a852`, coordinator-only.
Exactly three fresh real children run sequentially. No grandchildren/support.

Preserve evidence 001/002, original H0-H4 and correction 001 unchanged.

## Dispatch

1. R0 `aidle-worldgen-godot-runtime`, `PATCH_DRAFT`, sole product/test writer.
2. R1 `aidle-worldgen-qa-evidence`, `VERIFY_ONLY`.
3. R2 `aidle-worldgen-purple-acceptance`, `VERIFY_ONLY`.

Every child reads all five mandatory plus routed skills through EOF, uses exact
TrustLayer/UI bindings, real durable UUID refs, schema-valid receipt,
`accepted=false`, `self_accept=false`.

## R0 exact lease

- `game/scripts/camera/cozy_camera.gd`
- `game/scripts/player/player_controller.gd`
- `game/scripts/ui/hud.gd`
- `game/scripts/ui/control_1b_cursor_label.gd`
- `game/scripts/ui/control_1b_inspect_panel.gd`
- `game/scripts/modules/block_assembly/block_assembly_controller.gd`
- `game/scripts/modules/manifestation/manifestation_instance.gd`
- `game/scripts/modules/executor/headed_demo_flow.gd`
- `game/tests/h1_runtime_autoload_lookup_smoke.gd`
- `orchestration/logs/h1-consolidate-r0-runtime-003.log`
- `orchestration/receipts/h1_consolidate_001/correction_002/R0_runtime_003.json`

Mechanically replace every production `get_node` or `get_node_or_null` absolute
`/root/...` lookup in the leased runtime scripts with a guarded SceneTree-root
relative lookup. No active leased runtime script may retain an executable
absolute-root node lookup. Do not change behavior or authority.

Remove `fixture` wording from normal `hud.gd` edition text while preserving
Free Bridge/API Gateway semantics.

Add a static gate scanning all `game/scripts/**/*.gd` executable source for
absolute-root `get_node` calls and a runtime gate exercising player/router/a11y
resolution when attached and temporarily detached. Re-run H1, P2E, Control,
G3, G4 and Block-DNA gates. R0 does not write headed evidence.

## R1 exact lease

- `orchestration/logs/h1-consolidate-r1-qa-003.log`
- `orchestration/receipts/h1_consolidate_001/correction_002/R1_qa_003.json`
- `orchestration/evidence/h1_consolidate_001/003/**`

Produce a fresh real headed 13-state x 2-resolution matrix. Require 26 distinct
valid PNGs, zero Godot ERROR including teardown, real input, Build R preview
rotation and unchanged camera yaw, no direct commit fallback, no fixture wording,
and all regressions green. Do not filter or reclassify errors.

## R2 exact lease

- `orchestration/logs/h1-consolidate-r2-purple-003.log`
- `orchestration/receipts/h1_consolidate_001/correction_002/R2_purple_003.json`

Verify lineage, schemas, exact leases, hashes, static whole-runtime gate, headed
zero-error evidence and regressions. Purple never accepts. Return WAITING_CODEX.

## Hard stop

If evidence 003 repeats the same absolute-root USER ERROR signature, return
`HITL_REQUIRED/WAITING_CODEX`; do not start another child or correction.

No Scene, Character runtime, DNA v1.2/Tier3, Blender, network, shipping, install,
credentials, Godot version change, push, deploy or publish.

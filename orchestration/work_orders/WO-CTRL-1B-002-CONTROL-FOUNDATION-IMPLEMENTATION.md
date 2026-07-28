# WO-CTRL-1B-002-CONTROL-FOUNDATION-IMPLEMENTATION

Authority: `PATCH_DRAFT` + `VERIFY_ONLY` | State: `READY`

Implement and prove the accepted Control 1B contract for the local 2.5D Cozy
vertical slice. The accepted contract is
`Control/CONTROL_1B_ACCEPTANCE_CONTRACT.md`; its schema, fixtures and validator
are read-only authority inputs. This work order does not authorize network,
shipping, Character Foundry or World 2.

## Locked product behavior

- Exactly one primary context: exploration, companion, build, inspect or
  world_tool. Unknown context/action IDs fail with state unchanged.
- Runtime uses stable InputMap action names, not raw physical key checks.
- `/`, Ctrl+Enter, Tab, V, B, Delete Proposal, Ctrl+Z, Esc priority and
  Build-only R follow the accepted contract.
- Delete produces a proposal only. Undo produces a compensation request only.
  Neither directly mutates canonical state or erases history.
- Preview owns no durable state, ownership or official collision. Existing
  proposal -> validate -> preview -> explicit confirm -> World Commit boundary
  remains intact.
- Context HUD shows at most four actions and never relies on color alone.
- Remap, left-hand and one-hand presets, hold/toggle, zoom/mouse sensitivity,
  reduced motion, screen shake, cursor size and confirmation hold persist.
- Cozy V is a non-durable Helper Pulse affordance; Cozy B is a read-only
  Homestead Panel. They cannot mint inventory, ownership or currency.
- Godot stays `4.3-stable`; 2.5D fixed-angle camera and text-only Companion stay
  locked.

## B0 - Control kernel and InputMap

Profile: `aidle-worldgen-control-input`; TrustLayer:
`blue-team-p0-remediator`; UI: `ui-a11y-auditor`; authority: `PATCH_DRAFT`.

Create the fail-closed context router, closed action catalog, binding/remap
manager, accessibility settings state and deterministic unit/headless tests.
Preserve existing WASD, arrow ownership and jump-vs-ui_accept regressions.

Exclusive product/test writes (only files actually needed from this set):

- `game/project.godot`
- `game/autoload/control_context_router.gd`
- `game/autoload/control_accessibility_settings.gd`
- `game/scripts/input/control_action_catalog.gd`
- `game/scripts/input/control_binding_manager.gd`
- `game/tests/control_1b_context_router_smoke.gd`
- `game/tests/control_1b_accessibility_smoke.gd`

Exclusive evidence writes:

- `orchestration/receipts/control/CTRL_1B_002_b0_control_001.json`
- `orchestration/logs/ctrl-1b-002-b0-control-001.log`

## B1 - Godot integration and Cozy V/B UI

Profile: `aidle-worldgen-godot-runtime`; TrustLayer:
`blue-team-p0-remediator`; UI: `ui-app-dashboard`; authority: `PATCH_DRAFT`.

Integrate B0 with the existing player, fixed camera, Companion composer,
manifestation preview, HUD and demo/executor boundary. Add responsive context
HUD, accessible settings panel, Helper Pulse feedback and Homestead Panel.
Provide integration and headed harnesses. Do not reimplement or bypass World
Commit and do not add client-authoritative durable state.

Exclusive product/test writes (only files actually needed from this set):

- `game/scripts/main/main.gd`
- `game/scripts/player/player_controller.gd`
- `game/scripts/camera/cozy_camera.gd`
- `game/scripts/modules/companion/companion_chat_panel.gd`
- `game/scripts/modules/executor/headed_demo_flow.gd`
- `game/scripts/modules/manifestation/manifestation_instance.gd`
- `game/scripts/ui/hud.gd`
- `game/scenes/ui/hud.tscn`
- `game/scripts/ui/context_action_hud.gd`
- `game/scripts/ui/control_settings_panel.gd`
- `game/scripts/ui/cozy_homestead_panel.gd`
- `game/scripts/ui/cozy_helper_pulse.gd`
- `game/scenes/ui/context_action_hud.tscn`
- `game/scenes/ui/control_settings_panel.tscn`
- `game/scenes/ui/cozy_homestead_panel.tscn`
- `game/tests/control_1b_integration_smoke.gd`
- `game/tests/control_1b_headed_smoke.gd`

Exclusive evidence writes:

- `orchestration/receipts/control/CTRL_1B_002_b1_runtime_001.json`
- `orchestration/logs/ctrl-1b-002-b1-runtime-001.log`

## Q2 - Independent executable and headed evidence

Profile: `aidle-worldgen-qa-evidence`; TrustLayer:
`purple-team-finding-triage`; UI: `ui-a11y-auditor`; authority: `VERIFY_ONLY`.

Run the contract validator, every new control smoke, clean boot and the existing
G8/P1E regressions affected by InputMap, player, HUD, Companion, manifestation
and save/reload. Require exit 0, expected markers and zero Godot ERROR/parse
lines. Run the B1 headed harness at 1280x720 and 868x517. Capture distinct
states for exploration, focused composer, build preview, Esc cancel, Helper
Pulse, Homestead Panel and accessibility/remap settings with hashes,
dimensions, runtime context and control geometry. Exercise H-01 through H-33;
missing evidence is not PASS.

Exclusive writes:

- `orchestration/evidence/control_1b_002/**`
- `orchestration/receipts/control/CTRL_1B_002_q2_qa_001.json`
- `orchestration/logs/ctrl-1b-002-q2-qa-001.log`

## A3 - Accessibility and safety audit

Profile: `support-control-a11y`; TrustLayer: `code-reader`; UI:
`ui-a11y-auditor`; authority: `READ_ONLY_AUDIT`.

Audit source plus Q2 runtime evidence against every contract gate. Verify focus
does not leak movement, Esc priority, no raw-key bypass, non-color cues, <=4
HUD actions, remap/preset persistence, two viewport sizes, proposal-only delete,
compensation-only undo, preview collision/ownership absence and complete-only
activation. Findings only; never patch.

Exclusive writes:

- `orchestration/receipts/control/CTRL_1B_002_a3_a11y_001.json`
- `orchestration/logs/ctrl-1b-002-a3-a11y-001.log`

## P4 - Purple release recommendation

Profile: `aidle-worldgen-purple-acceptance`; TrustLayer:
`purple-team-release-gate`; UI: `ui-visual-critic`; authority: `VERIFY_ONLY`.

Independently verify B0/B1/Q2/A3 lineage, writer leases, schema-valid receipts,
all 33 headed rows, image authenticity, zero-error regressions, authority and
scope. Purple returns VERIFIED, CHANGES_REQUESTED or NEED_HUMAN only; it never
patches or accepts.

Exclusive writes:

- `orchestration/receipts/control/CTRL_1B_002_p4_purple_001.json`
- `orchestration/logs/ctrl-1b-002-p4-purple-001.log`

## Workflow and evidence rules

- Use only Desktop parent `019f7ffd-3995-71c0-aca1-51078e24a852`, coordinator-only.
- Exactly five fresh real children B0 -> B1 -> Q2 -> A3 -> P4, strictly
  sequential with one active child maximum. No resume, follow-up, grandchild or
  unassigned support profile.
- Bind each installed profile to the exact TrustLayer/UI characters above and
  load all five mandatory skills plus profile-routed skills fully.
- One writer per file. A child may write only its exclusive lease. Parent never
  patches product, test, contract or evidence.
- Every receipt validates against the MAF `agent_step_contract` schema and has
  real child/transcript lineage, exact commands/exits, hashes, writer lease,
  `accepted=false` and `self_accept=false`.
- Parent returns `REVIEW_REQUESTED` / `WAITING_CODEX`; only Codex may accept.

## Hard stops

No edits to accepted Control contract/fixtures, Character Foundry, Scene stage
2, World 2, World Commit authority, persistence format or network. No direct
durable delete/undo, dependency install, Godot version change, credential, live
provider/public listener, push, deploy or publish. Red F01 blocks network and
shipping regardless of local Control results.

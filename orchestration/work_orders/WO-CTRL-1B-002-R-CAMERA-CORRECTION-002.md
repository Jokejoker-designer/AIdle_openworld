# WO-CTRL-1B-002-R-CAMERA-CORRECTION-002

Authority: `PATCH_DRAFT` + `VERIFY_ONLY` | State: `READY`

Human Product Lead live play found that R no longer rotates the camera right in
normal Exploration. Codex confirmed the root cause: the runtime Exploration
allow-list contains `rotate_camera_left` but omits `rotate_camera_right`, so the
context router fails closed before `cozy_camera.gd` can observe the InputMap
action. Directive-59 machine/Purple results are not accepted until this real
play regression is corrected.

## Locked behavior from Human decision

- Exploration: Q rotates camera left; R rotates camera right.
- Build: Q rotates preview left; R rotates preview right.
- One physical input produces only the action owned by the active context.
- Exploration R never rotates a hologram; Build R never rotates the camera.
- Continue using stable/remappable InputMap actions; no raw keycode path.
- Unknown contexts/actions remain fail-closed.

## S0 - Contract amendment

Profile: `schema`; TrustLayer: `blue-team-test-writer`; UI:
`ui-flow-architect`; authority: `PATCH_DRAFT`.

Record the explicit Human choice in the accepted Control contract and valid
fixture. Keep the no-dual-fire semantic rule. Update only the minimum hash lock
needed by the existing validator.

Exclusive writes:

- `Control/CONTROL_1B_ACCEPTANCE_CONTRACT.md`
- `orchestration/contracts/control_1b/valid_context_fixture.json`
- `orchestration/contracts/control_1b/validate_control_1b_fixtures.py`
- `orchestration/receipts/control/CTRL_1B_002_s0_r_contract_003.json`
- `orchestration/logs/ctrl-1b-002-s0-r-contract-003.log`

## R1 - Runtime and regression correction

Profile: `aidle-worldgen-control-input`; TrustLayer:
`blue-team-p0-remediator`; UI: `ui-a11y-auditor`; authority: `PATCH_DRAFT`.

Add `rotate_camera_right` to Exploration through the closed catalog and update
tests. Prove the actual InputMap/router/camera path changes camera yaw on R in
Exploration, not merely a direct `try_dispatch` call. Prove Build R changes only
preview yaw, and remapping the logical action still works.

Exclusive writes (only files actually needed):

- `game/scripts/input/control_action_catalog.gd`
- `game/tests/control_1b_context_router_smoke.gd`
- `game/tests/control_1b_integration_smoke.gd`
- `game/tests/control_1b_headed_smoke.gd`
- `orchestration/receipts/control/CTRL_1B_002_r1_camera_runtime_003.json`
- `orchestration/logs/ctrl-1b-002-r1-camera-runtime-003.log`

Do not change the physical R bindings already present in `project.godot` unless
an executable test proves they are missing. `cozy_camera.gd` is not leased: its
router-gated implementation is already correct.

## Q2 - Independent real-path evidence

Profile: `aidle-worldgen-qa-evidence`; TrustLayer:
`purple-team-finding-triage`; UI: `ui-a11y-auditor`; authority: `VERIFY_ONLY`.

Run the amended contract validator, all Control smokes, clean boot and affected
G8/P1E regressions. Capture headed evidence or an equivalent deterministic
runtime witness showing Exploration camera yaw changes right on physical R and
Build preview yaw changes right without camera change. Zero ERROR/parse lines.

Exclusive writes:

- `orchestration/evidence/control_1b_002_r_camera_correction/**`
- `orchestration/receipts/control/CTRL_1B_002_q2_r_camera_003.json`
- `orchestration/logs/ctrl-1b-002-q2-r-camera-003.log`

## P3 - Purple gate

Profile: `aidle-worldgen-purple-acceptance`; TrustLayer:
`purple-team-release-gate`; UI: `ui-visual-critic`; authority: `VERIFY_ONLY`.

Verify the Human behavior, real InputMap path, no dual-fire, contract/fixture
consistency, lineage, leases and regressions. Purple never patches or accepts.

Exclusive writes:

- `orchestration/receipts/control/CTRL_1B_002_p3_r_camera_003.json`
- `orchestration/logs/ctrl-1b-002-p3-r-camera-003.log`

## Workflow and hard stops

- Use only Desktop parent `019f7ffd-3995-71c0-aca1-51078e24a852`, coordinator-only.
- Exactly four fresh real children S0 -> R1 -> Q2 -> P3, sequential, one active
  child. No resume/follow-up/grandchild/extra profile.
- Exact TrustLayer/UI/skills, one writer per file, real durable lineage,
  schema-valid receipts, `accepted=false`, `self_accept=false`.
- Preserve every Directive-58/59 receipt and correction evidence.
- No other Control polish, Character Foundry, Scene 2, World 2, World Commit,
  persistence or network work. No dependency install, Godot change, credential,
  live provider, public listener, push, deploy or publish.
- Parent returns `REVIEW_REQUESTED` / `WAITING_CODEX`; only Codex accepts.

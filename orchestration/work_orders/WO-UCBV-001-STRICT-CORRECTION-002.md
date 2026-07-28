# WO-UCBV-001-STRICT-CORRECTION-002

Status: `APPROVED BY HUMAN PRODUCT LEAD FOR DIRECTIVE 83 ONLY`  
Task: `UCBV-001`  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852` coordinator-only  
Decision: `AUTHORIZE_STRICT_UCBV_CORRECTION` at 2026-07-23T05:18:21+07:00  
Acceptance remains `false`.

## Intent anchor

Close the four blockers in `CODEX_UCBV-001_MACHINE_GATE_001.json` without
waiving the production target. Deliver a visibly detailed Nori-7 character and
matching modular construction experience. Incorporate the Human playtest
findings: avoid the nearly-white uncanny character, expose the full build
catalog, make build controls work through real input, and add a safe cursor-led
delete flow.

## Architecture lock

- Godot 4.3-stable, fixed-angle 2.5D Private Reality vertical slice.
- Modular composition does not mean cube-only geometry; rounded silhouette
  parts are allowed, but the final character must be a conditioned production
  mesh/skin/rig delivered through the existing offline Blender Bridge and GLB
  intake path.
- AI and client code propose only. World Commit remains the sole canonical
  mutator for build, delete, undo and persistence.
- No direct `queue_free` or client-side durable deletion.
- Preserve Godot version, dependencies, contracts and all accepted prior
  behavior unless this work order explicitly corrects it.

## Preserve rejected evidence

All U0-U8 receipts, logs, evidence and durable Grok child metadata are immutable.
Their lease and timestamp failures remain historical facts. No worker may
rewrite, delete or retroactively rehabilitate them. New correction artifacts use
the `correction_002` namespace only.

## Sequential workflow

The parent dispatches C0-C5 strictly sequentially. No grandchildren, no support
profiles, no parent product patch and no parallel writers.

### C0 — visual and production preflight

- Profile: `.grok/agents/aidle-character-style-guardian.md`
- Binding: TrustLayer `blue-team-p0-remediator`; UI `ui-brand-system-architect`
- Authority: `PATCH_DRAFT`
- Exact design lease:
  - `orchestration/design/ucbv_001/style_lock/**`
  - `orchestration/design/ucbv_001/character/nori7/**`
- Exact orchestration lease:
  - `orchestration/receipts/ucbv_001/correction_002/C0_visual_preflight_002.json`
  - `orchestration/logs/ucbv_001/correction_002/C0_visual_preflight_002.log`

Read the active UCBV DESIGN contracts, accepted Nori-7 Foundry identity,
practical findings, Block-DNA, Tier3 animation/skeleton data and current runtime
implementation. Produce a fail-closed checklist for real mesh/GLB, skin, rig,
animation, palette contrast, catalog, controls, deletion authority and evidence.
Explicitly reconcile the two cozy-cream definitions; do not silently pick one.
Apply the reconciled palette and animation intent to the leased design contracts.

### C1 — real character mesh, skin, rig and animation production

- Profile: `.grok/agents/aidle-worldgen-asset-art.md`
- Binding: TrustLayer `blue-team-p0-remediator`; UI `ui-color-type-specialist`
- Authority: `PATCH_DRAFT`
- Exact product lease:
  - `game/assets/ucbv_001/character/nori7/**`
  - `game/resources/ucbv_001/character/**`
  - `orchestration/design/ucbv_001/character/nori7/**`
- Exact orchestration lease:
  - `orchestration/receipts/ucbv_001/correction_002/C1_character_production_002.json`
  - `orchestration/logs/ucbv_001/correction_002/C1_character_production_002.log`

Use the already-approved local Blender Bridge workflow; do not install anything.
Produce and condition a real offline GLB with a skinned production mesh, named
material slots, a catalog-valid skeleton and animation clips for idle, walk,
turn-left, turn-right, build/place, confirm and cancel. A descriptor, procedural
SphereMesh/CapsuleMesh assembly, pelvis-bob-only clip or renamed placeholder is
not sufficient. Bind every output to Bridge job/package hashes and provenance.

Implement `orchestration/control/UCBV_ANIMATION_BLOCK_INTEGRATION_MAP_001.md`
exactly. Treat Tier3 `anim_robot_gardener_v1` as the reusable base contract,
not as animation payload. Author real keyed GLB actions for its required clips
and the explicitly named UCBV build extension. Preserve canonical names,
14-bone hierarchy, `cozy_bouncy`, root_motion=false and the optional/deferred
distinction. Do not alias missing actions to idle or claim game-local extension
clips came from Tier3.

Keep Nori-7 recognizable and cozy. Replace the nearly pure-white body treatment
with the reconciled warm cream base plus clearly readable darker joints/panels,
face/visor detail and restrained cyan manifestation accent. Verify silhouette
and contrast at the fixed 2.5D camera and both target resolutions.

Do not write helper/temp/debug files outside the lease. Every command must write
only to the single leased log or an OS temporary directory outside the repo.

### C2 — Godot, build catalog, input and delete integration

- Profile: `.grok/agents/aidle-worldgen-godot-runtime.md`
- Binding: TrustLayer `blue-team-p0-remediator`; UI `ui-app-dashboard`
- Authority: `PATCH_DRAFT`
- Exact product/test lease:
  - `game/scripts/modules/ucbv_001/**`
  - `game/scripts/modules/block_assembly/**`
  - `game/scenes/modules/block_assembly/**`
  - `game/resources/block_assembly/**`
  - `game/resources/ucbv_001/character/**`
  - `game/scripts/input/control_context_router.gd`
  - `game/scripts/input/control_action_catalog.gd`
  - `game/scripts/main/main.gd`
  - `game/project.godot`
  - `game/tests/ucbv_001_*.gd`
  - `game/tests/p2e001_block_assembly_*.gd`
  - `game/tests/h1_human_ux_manual_build_smoke.gd`
- Exact orchestration lease:
  - `orchestration/receipts/ucbv_001/correction_002/C2_runtime_build_controls_002.json`
  - `orchestration/logs/ucbv_001/correction_002/C2_runtime_build_controls_002.log`

Required runtime outcomes:

1. Load the C1 GLB through the existing offline intake contract and use its real
   rig and animation clips. Implement the adapter and AnimationTree mapping in
   `UCBV_ANIMATION_BLOCK_INTEGRATION_MAP_001.md`, including exact 14-bone parent
   validation, required-action existence/duration/track checks and mutation-free
   markers. Remove the first-slice procedural primitive presenter fallback from
   normal play; fail visibly and non-destructively if the GLB, adapter, bones or
   required clips are missing.
2. Manual Build exposes the full accepted 28-module runtime catalog through a
   readable categorized selector with module name and preview. Do not leave
   `arch_door_round` as the apparent only choice; comma/period-only hidden
   cycling is insufficient.
3. Real keyboard/mouse input selects a module, grounds a preview, rotates it
   with Q/R, changes elevation through a clearly labelled non-conflicting action,
   confirms and cancels. Tests must drive InputMap events, not controller method
   fallbacks. When no preview is active, show why Q/R cannot rotate instead of
   silently returning `rotated=false`.
4. Delete enters an explicit erase mode: cursor becomes a red X, only committed
   player-owned/unlocked build entities highlight, LMB selects a target, and
   confirmation creates a World Commit compensation-delete proposal. Esc/RMB
   exits without mutation; Undo restores through the authoritative compensation
   path. No direct SceneTree deletion.
5. Preserve camera/build Q/R separation, idempotency, revision checks,
   save/reload, undo, collision/navigation and H1/P2E/Control behavior.
6. Address the runtime navigation warnings without broad rebaking: use collision
   shapes as runtime bake source where this slice rebakes, and align agent
   radius/height with voxel resolution or document an exact non-blocking residual.

No AI Build Zone or Text-to-Build work is authorized; that remains P2E-002.

### C3 — Red scope, originality and authority audit

- Profile: `.grok/agents/aidle-worldgen-red-scope.md`
- Binding: TrustLayer `red-team-source-auditor`; UI `ui-visual-critic`
- Authority: `READ_ONLY_AUDIT`
- Writes only:
  - `orchestration/receipts/ucbv_001/correction_002/C3_red_scope_002.json`
  - `orchestration/logs/ucbv_001/correction_002/C3_red_scope_002.log`

Audit C1-C2 scope, originality/provenance, real GLB/animation status, palette,
all 28 catalog entries, InputMap-only control path, delete authority, forbidden
fallbacks, exact leases and the Red F01 hard stop. Findings only; never patch.

### C4 — QA and clean headed evidence

- Profile: `.grok/agents/aidle-worldgen-qa-evidence.md`
- Binding: TrustLayer `purple-team-finding-triage`; UI `ui-a11y-auditor`
- Authority: `VERIFY_ONLY`
- Writes only:
  - `orchestration/receipts/ucbv_001/correction_002/C4_qa_evidence_002.json`
  - `orchestration/logs/ucbv_001/correction_002/C4_qa_evidence_002.log`
  - `orchestration/evidence/ucbv_001/002/**`

Produce fresh normal-play evidence at 1280x720 and 868x517 with no diagnostic
banner/wall. Capture Nori-7 idle/walk/turn/build/place/confirm/cancel, warm-cream
material readability, categorized module selection across the 28-entry catalog,
two module placements, Q/R rotation, labelled elevation, invalid placement,
Delete red-X hover/select/confirm/cancel, undo, save/reload and clean teardown.

Rerun UCBV, H1, P2E, Control, G3, G4, Block-DNA, authority, persistence and
navigation/collision regressions. Strict pass requires zero ERROR, USER ERROR,
SCRIPT ERROR, parse/missing-resource, RID leak and the submitted navigation
warnings. Evidence must include hashes, dimensions, exact input sequence and
runtime log. No direct controller fallback calls in tests or capture harness.
Also prove `scan` and post-authoritative-complete `happy` are distinct imported
GLB actions; verify optional Tier3 gardener clips are either real and evidenced
or explicitly deferred without idle aliases.

### C5 — Purple non-accepting gate

- Profile: `.grok/agents/aidle-worldgen-purple-acceptance.md`
- Binding: TrustLayer `purple-team-release-gate`; UI `ui-visual-critic`
- Authority: `VERIFY_ONLY`
- Writes only:
  - `orchestration/receipts/ucbv_001/correction_002/C5_purple_gate_002.json`
  - `orchestration/logs/ucbv_001/correction_002/C5_purple_gate_002.log`

Adjudicate C0-C4, all hashes, real GLB/skin/rig/clips, visual evidence, runtime
input/delete authority, regressions, durable transcript lineage and leases.
Return `REVIEW_REQUESTED / WAITING_CODEX`, `accepted=false`,
`self_accept=false`. Purple never marks ACCEPTED.

## Receipt and lineage contract

Each child must fully read its installed profile, exact TrustLayer and UI cards,
the five mandatory skills, and only the routed skills declared by its profile
and this work order. Each receipt validates directly against
`agent_step_contract.schema.json` and records real child/transcript UUID,
commands/exits, files read/written, hashes, exclusive lease self-audit and
`accepted=false`, `self_accept=false`. Worker timestamps are artifact claims;
Codex will bind parent-owned durable `meta.json` timing independently.

## Completion and forbidden scope

Stop after C5 at `REVIEW_REQUESTED / WAITING_CODEX`. P2E-002 remains blocked
until Codex machine review and Human visual acceptance of UCBV-001.

Forbidden: new top-level Grok session, Grok CLI, parent product patch,
grandchildren, support profiles, fabricated refs, helper writes outside leases,
dependency installation, Godot version change, credentials, live provider,
public network, shipping, push, deploy, publish, DNA v1.2, Tier3 activation,
full 28-character wave, AI Build Zone and Text-to-Build.

Red F01 remains a hard stop before all networked work and shipping.

# WO-P2E-001-PLAYABILITY-CORRECTION-002

Status: APPROVED FOR DIRECTIVE 72 ONLY  
Task: P2E-001  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852` coordinator-only  
Acceptance remains false.

## Goal

Preserve the useful Directive-70/71 implementation and close only the remaining
headed-playability, responsive-UI, teardown and lease-honesty blockers recorded
in `CODEX_P2E-001_CORRECTION_REVIEW_002.json`.

This is the second occurrence of the same teardown signature. A third identical
failure routes to `NEED_HUMAN`; workers must not hide, filter or reclassify Godot
errors.

## Sequential dispatch

1. **D0 runtime correction** — resume C0 lineage
   `019f8883-4c2b-7341-9093-074ac8449a5c`, profile
   `aidle-worldgen-godot-runtime`, `PATCH_DRAFT`, sole product/test writer.
2. **D1 Control/UX audit** — fresh `aidle-worldgen-control-input`, authority
   reduced to `VERIFY_ONLY`, no product/test patch.
3. **D2 QA evidence** — fresh `aidle-worldgen-qa-evidence`, `VERIFY_ONLY`, new
   evidence tree `orchestration/evidence/p2e_001/003/**` only.
4. **D3 Purple gate** — fresh `aidle-worldgen-purple-acceptance`, `VERIFY_ONLY`,
   never ACCEPTED.

No grandchildren or support profiles. Run strictly sequentially.

## D0 exact product/test lease

- `game/scripts/modules/block_assembly/**`
- `game/scenes/modules/block_assembly/**`
- `game/resources/block_assembly/**`
- `game/tests/p2e001_block_assembly_*.gd`
- `game/scripts/main/main.gd`
- `game/project.godot`
- `game/scripts/input/control_context_router.gd`
- `game/scripts/input/control_action_catalog.gd`
- `game/scripts/ui/context_action_hud.gd`
- `game/scenes/ui/hud.tscn`
- `game/scripts/camera/cozy_camera.gd`

`cozy_camera.gd` is explicitly leased now so the earlier out-of-lease change can
be reviewed, minimally corrected if required, rehashed and honestly attributed
to Directive 72. This does not retroactively rehabilitate Directive 71.

D0 orchestration writes only:

- `orchestration/logs/p2e-001-d0-runtime-003.log`
- `orchestration/receipts/p2e_001/correction_002/D0_runtime_correction_003.json`

## Required corrections

- Remove the actual texture/RID teardown leak. Do not suppress log lines.
- A normal player input sequence must select, place, rotate, elevate, confirm and
  cancel without direct `select_module`, `confirm_and_commit`, or equivalent
  controller fallback calls.
- Exploration Q/R rotates the camera. Build Q/R rotates the preview in both
  viewports while camera yaw remains exactly unchanged.
- Escape cancels only the active preview and must not open Pause or double-fire
  in the same input sequence.
- At 1280x720 and 868x517: no clipped/overlapping controls, no Pause overlay in
  build witnesses, no diagnostic wall as the primary HUD. Module, snap,
  validity, rotation, elevation, confirm and cancel must remain readable.
- Preserve invalid-then-corrected idempotency, stable replay, changed-payload
  conflict, revision, World Commit authority and earlier committed entities.

## D1 lease and gate

Writes only:

- `orchestration/logs/p2e-001-d1-control-003.log`
- `orchestration/receipts/p2e_001/correction_002/D1_control_audit_003.json`

Audit real InputMap/action routing, no direct fallback, Q/R semantics, Escape
ownership, responsive HUD code, exact D0 lease and Control-1B regression. Report
only; do not patch.

## D2 lease and gate

Writes only:

- `orchestration/logs/p2e-001-d2-qa-003.log`
- `orchestration/receipts/p2e_001/correction_002/D2_qa_evidence_003.json`
- `orchestration/evidence/p2e_001/003/**`

Produce a fresh fail-closed runner and capture harness under the new evidence
tree. Do not reuse or rewrite `001/**` or `002/**`.

Required:

- Block-DNA 14/14 valid, 42/42 invalid.
- P2E core, authority, Q/R, playable-select, correction and Control router
  smokes pass with zero errors.
- Fourteen distinct PNGs: seven required states at both 1280x720 and 868x517.
- Manifest includes exact input sequence and yaw/rotation before/after.
- No direct controller fallback; scan the capture harness and runtime log for
  forbidden calls.
- Zero `ERROR`, `USER ERROR`, `SCRIPT ERROR`, parse/missing-resource, RID leak or
  null RenderingServer lines including teardown. Godot and runner exit 0.
- Visual geometry check and headed inspection prove all controls inside viewport,
  no overlap, no Pause overlay and no duplicate state hash.

## D3 lease and gate

Writes only:

- `orchestration/logs/p2e-001-d3-purple-003.log`
- `orchestration/receipts/p2e_001/correction_002/D3_purple_gate_003.json`

Adjudicate D0-D2 and the prior lease violation. Return
`REVIEW_REQUESTED/WAITING_CODEX`, `accepted=false`, `self_accept=false`.
Purple never patches and never marks ACCEPTED.

## Receipt requirements

Every child must bind the exact installed profile, TrustLayer character and UI
character; fully read the five mandatory skills plus routed skills; record real
durable child/transcript lineage, exact commands/exits, files read/written,
hashes, product writes, timestamps and exclusive lease self-audit. Validate each
receipt directly against `agent_step_contract.schema.json` with zero errors.

## Forbidden

No DNA v1.2, Tier 3, Character runtime, successor P2E, unrelated art wave,
network, shipping, install, credentials, provider, Godot version change, push,
deploy, publish, parent product patch, another session, Grok CLI, fabricated
reference, hidden error filter, or rewrite of prior evidence.


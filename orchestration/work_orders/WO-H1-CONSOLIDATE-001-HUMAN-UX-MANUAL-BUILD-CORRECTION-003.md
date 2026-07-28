# WO-H1-CONSOLIDATE-001-HUMAN-UX-MANUAL-BUILD-CORRECTION-003

## Authority and scope

- Directive: 78.
- Task: `H1-CONSOLIDATE-001` only.
- Authority: `PATCH_DRAFT` for W0; `VERIFY_ONLY` for W1-W3.
- Existing Grok Desktop parent only: `019f7ffd-3995-71c0-aca1-51078e24a852`.
- Parent remains coordinator-only. Run W0-W3 sequentially using real installed child profiles; never patch product files from the parent.
- Human Product Lead completed the H1 playtest, reported three findings, and authorized correction. This is not a Human PASS.

## Correction objective

1. Replace the cyan square Helper Pulse with a clearly non-square, unobtrusive pulse/ring treatment.
2. Restore the normal OS mouse pointer by default. Do not force a square proxy in Exploration or ordinary UI use; any near-cursor action label remains optional and respects accessibility settings.
3. Rename `Small Build` to `Manual Build` and make it a true cursor-led build mode:
   - screen-to-ground ray projection onto the allowed build surface;
   - snapped hologram follows the cursor and visibly reports valid/invalid placement;
   - left click creates or moves preview state only, never canonical world state;
   - Q/R changes preview elevation/rotation only while Build context owns those actions;
   - right click or Escape cancels exactly once;
   - explicit Confirm routes through the existing World Commit authority and remains the only local canonical mutation path.

## Locked invariants

- Godot stays pinned to 4.3; install no dependency and change no engine version.
- Exploration R continues rotating the camera right. Build R rotates only the preview.
- Preview/hologram collision and navigation remain non-durable until World Commit succeeds.
- No free-float placement, direct controller commit, duplicate input dispatch, fabricated receipt/session reference, self-acceptance, network, live provider, credential, push, deploy, publish, DNA v1.2 or Tier 3 work.
- Preserve all prior H1 evidence and receipts immutably.
- `P2E-002` and `UCBV-001` are queued but not authorized by this work order.

## Sequential child dispatch

### W0 - sole product writer

- Installed profile: `.grok/agents/aidle-worldgen-control-input.md`.
- TrustLayer binding: `blue-team-p0-remediator`.
- UI binding: `ui-a11y-auditor`.
- Authority: `PATCH_DRAFT`.
- Fully read the five mandatory project skills plus `architecture-lock` and all routed skill/card files before acting; record real transcript lineage.
- Exclusive product/test lease:
  - `game/scripts/ui/cozy_helper_pulse.gd`
  - `game/scripts/ui/control_1b_cursor_label.gd`
  - `game/scripts/ui/playable_action_bar.gd`
  - `game/scripts/main/main.gd`
  - `game/scripts/modules/block_assembly/block_assembly_controller.gd`
  - `game/scripts/modules/block_assembly/block_preview_entity.gd`
  - `game/scripts/modules/block_assembly/block_assembly_hud.gd`
  - `game/autoload/control_accessibility_settings.gd`
  - `game/tests/h1_human_ux_manual_build_smoke.gd`
- Exclusive receipt/log lease:
  - `orchestration/receipts/h1_consolidate_001/correction_003/W0_control_manual_build_004.json`
  - `orchestration/logs/h1_consolidate_001/correction_003/W0_control_manual_build_004.log`
- Receipt must validate against `agent_step_contract.schema.json`, bind the real child UUID, and keep `accepted=false`, `self_accept=false`.

### W1 - Red findings only

- Installed profile: `.grok/agents/aidle-worldgen-red-scope.md`.
- Authority: `VERIFY_ONLY`; no product patch.
- Probe context leakage, direct commit bypass, duplicate click/Escape dispatch, invalid ray hits, off-surface/free-float placement, cursor trapping, and accessibility regressions.
- Exclusive receipt/log: `orchestration/receipts/h1_consolidate_001/correction_003/W1_red_manual_build_004.json` and matching `.log` under `orchestration/logs/.../correction_003/`.

### W2 - QA headed evidence

- Installed profile: `.grok/agents/aidle-worldgen-qa-evidence.md`.
- Authority: `VERIFY_ONLY`; no product patch.
- Produce fresh evidence only under `orchestration/evidence/h1_consolidate_001/004/**`.
- Verify two supported resolutions, normal pointer in ordinary play, non-square Helper Pulse, Manual Build label, distinct cursor positions producing distinct snapped preview positions, invalid-surface feedback, Q/R separation, single cancel, confirm through World Commit, save/reload/undo, responsive UI and zero Godot ERROR/USER ERROR including teardown.
- Rerun H1, P2E, Control, G3, G4 and Block-DNA regressions.
- Exclusive receipt/log: `orchestration/receipts/h1_consolidate_001/correction_003/W2_qa_manual_build_004.json` and matching `.log`.

### W3 - Purple recommendation

- Installed profile: `.grok/agents/aidle-worldgen-purple-acceptance.md`.
- Authority: `VERIFY_ONLY`; no product patch.
- Independently reconcile W0-W2 scope, leases, receipts, hashes, evidence and regressions. Purple may recommend `REVIEW_REQUESTED` or `CHANGES_REQUESTED`, never `ACCEPTED`.
- Exclusive receipt/log: `orchestration/receipts/h1_consolidate_001/correction_003/W3_purple_manual_build_004.json` and matching `.log`.

## Completion and gate

- Parent reports `REVIEW_REQUESTED / WAITING_CODEX` only after W0-W3 complete.
- Codex independently validates schema, exact durable timestamps, transcript lineage, hashes, evidence, regressions and writer leases.
- Even after machine pass, H1 remains `accepted=false` until the Human Product Lead performs a focused retest and explicitly passes the corrected flow.

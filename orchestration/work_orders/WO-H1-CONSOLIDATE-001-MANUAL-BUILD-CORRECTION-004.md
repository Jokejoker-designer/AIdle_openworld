# WO-H1-CONSOLIDATE-001-MANUAL-BUILD-CORRECTION-004

## Authority

- Directive 79; task `H1-CONSOLIDATE-001` only.
- Use existing Grok Desktop parent `019f7ffd-3995-71c0-aca1-51078e24a852` while it remains healthy. The Human Product Lead permits a replacement parent only if this parent becomes operationally unusable; do not create one merely because its transcript is large.
- Parent is coordinator-only. Execute C0-C2 sequentially with real installed children, exact character/UI bindings, mandatory skills plus routed skills, no grandchildren, one writer per file, real transcript lineage, `accepted=false`, `self_accept=false`.
- C0 has `PATCH_DRAFT`; C1-C2 have `VERIFY_ONLY`.

## Preserve and reject honestly

- Preserve evidence 001-004, all correction_003 receipts and logs, and all durable child transcripts/meta unchanged.
- W2 correction_003 receipt is schema-invalid and must not be rewritten.
- W0 correction_003 auxiliary logs are out-of-lease evidence and must not be deleted or retroactively declared compliant.
- Worker-authored timestamps are artifact times only. Codex binds parent-owned durable `meta.json` timestamps after completion.

## C0 - focused sole product/test writer

- Profile: `.grok/agents/aidle-worldgen-control-input.md`.
- TrustLayer: `blue-team-p0-remediator`; UI: `ui-a11y-auditor`.
- Exact product/test lease only:
  - `game/scripts/modules/block_assembly/block_assembly_hud.gd`
  - `game/scenes/ui/playable_action_bar.tscn`
  - `game/tests/h1_consolidation_chrome_smoke.gd`
  - `game/tests/h1_consolidation_flow_smoke.gd`
  - `game/scripts/ui/control_1b_cursor_label.gd`
  - `game/autoload/control_accessibility_settings.gd`
  - `game/scripts/modules/block_assembly/block_assembly_controller.gd`
  - `game/tests/h1_human_ux_manual_build_smoke.gd`
- Close exactly:
  1. Explicitly type the HUD `cursor_valid` path so warnings-as-errors produces zero compile/runtime errors.
  2. Replace all shipped/test expectations of `Small Build` with `Manual Build` in the leased scene and tests.
  3. Require one intentional valid LMB placement before `can_confirm` can succeed in Manual Build.
  4. Fail closed if `place_at_cursor` is called outside Build context; it must not silently enable Manual Build.
  5. Make `force_custom_cursor` either a correctly consumed optional accessibility setting using a non-square pointer or remove its dead runtime path without changing the default normal OS pointer.
- Preserve World Commit as sole canonical mutation, preview-only LMB, snapped ground ray, invalid feedback, single Esc/RMB cancel, Exploration R camera, Build R preview-only and Godot 4.3.
- Exact orchestration lease only:
  - `orchestration/receipts/h1_consolidate_001/correction_004/C0_manual_build_fix_005.json`
  - `orchestration/logs/h1_consolidate_001/correction_004/C0_manual_build_fix_005.log`
- Run every test into the single leased log. Do not create auxiliary logs, summaries or hash files.
- Receipt must validate against `agent_step_contract.schema.json`, include `smoke_test` and `self_audit`, list every product write and hash, and make no canonical completion-time claim.

## C1 - fresh QA and headed evidence

- Profile: `.grok/agents/aidle-worldgen-qa-evidence.md`.
- TrustLayer/UI bindings exactly from the installed profile.
- No product/test patch.
- Exact orchestration lease:
  - `orchestration/receipts/h1_consolidate_001/correction_004/C1_qa_manual_build_005.json`
  - `orchestration/logs/h1_consolidate_001/correction_004/C1_qa_manual_build_005.log`
  - `orchestration/evidence/h1_consolidate_001/005/**`
- Produce fresh 1280x720 and 868x517 evidence for normal OS pointer state, non-square ring pulse, Manual Build label, intentional LMB placement, two distinct snapped positions, invalid surface, Q/R separation, single cancel, World Commit confirmation, save/reload and undo.
- Rerun H1 Manual Build, H1 flow, H1 chrome, H1 error-free, P2E core/authority/Q-R/player/correction, Control router/a11y/fixtures, G3, G4 and Block-DNA.
- Strict pass requires zero Godot ERROR, USER ERROR, SCRIPT ERROR, parse/compile error and teardown leak lines. Any failure is reported without filtering.
- Receipt must be schema-valid with `smoke_test` and `self_audit`; no canonical completion-time claim.

## C2 - Purple non-accepting gate

- Profile: `.grok/agents/aidle-worldgen-purple-acceptance.md`.
- No product, test or evidence patch.
- Exact orchestration lease:
  - `orchestration/receipts/h1_consolidate_001/correction_004/C2_purple_manual_build_005.json`
  - `orchestration/logs/h1_consolidate_001/correction_004/C2_purple_manual_build_005.log`
- Validate scope, hashes, single-writer lease, fresh evidence, strict regressions and schema. Purple may return `REVIEW_REQUESTED` or `CHANGES_REQUESTED`, never `ACCEPTED`.

## Completion

- Parent stops at `REVIEW_REQUESTED / WAITING_CODEX`.
- UCBV-001 is the Human-directed first priority immediately after H1 closes; P2E-002 follows it. Both remain unauthorized during this correction.
- Even a clean machine correction does not infer Human PASS. Human Product Lead performs the focused retest after Codex machine review.
- Red F01 remains a hard stop before networked work or shipping. No install, credential, live provider, Godot version change, push, deploy or publish.

# WO-G8-001-UI-VISUAL-CORRECTION-002

Directive: 23  
Task: G8-001  
State: APPROVED CORRECTION / preserve all existing code  
Parent: the one existing Grok Desktop conductor task only

## Scope

Fix only the independent visual/evidence blockers recorded in
`orchestration/reviews/CODEX_G8-001_UI_VISUAL_REVIEW_002.json`. Reuse the
Directive 22 TrustLayer/UI character and skill bindings. Do not restart the UI
design loop or replace working modules.

## Dispatch and ownership

No nested grandchildren, no self-accept, one writer per file.

| Wave | Profile | Authority | Sole responsibility |
|---|---|---|---|
| V0 | schema | VERIFY_ONLY | Turn the seven blockers into executable assertions; receipt only |
| V1 | core | PATCH_DRAFT | `headed_visual_smoke.gd`, HUD files and main integration only |
| V2 | companion | PATCH_DRAFT | Companion panel `.gd/.tscn` only |
| V3 | manifestation | PATCH_DRAFT | manifestation visual `.gd` files only |
| V4 | executor | PATCH_DRAFT | demo flow, action-bar and starter-panel files only |
| V5 | asset | VERIFY_ONLY | headed composition/color audit; receipt only |
| V6 | persist | READ_ONLY_AUDIT | responsive/a11y and clean-state evidence; receipt only |
| V7 | network | VERIFY_ONLY | final Purple screenshot/log/evidence gate; never patch |

Every receipt goes under `orchestration/receipts/g8/ui_visual_correction_002/`
and retains non-empty character binding, exact skills/source/mode, context hash,
trace and durable handoff reference.

## Required fixes

1. Headed smoke must wait for autoload readiness before calling
   `ArtStyleManager.set_active_style`; no `Unknown art style` or other `ERROR:` is
   allowed. Any Godot `ERROR:` makes the smoke fail regardless of exit code.
2. Prove the product rule honestly: a new/clean world defaults to Cozy; a real
   previously saved user selection remains preserved. Test setup may select Cozy
   ephemerally for captures but must label that as test setup, not first-run proof.
3. Add geometry assertions at both 1280x720 and 868x517: Companion panel and
   action bar remain inside the viewport, do not intersect, ChatInput is visible,
   all actionable buttons are visible, and minimum readable sizing is enforced.
4. At 868x517 use a responsive layout that remains readable (two rows, compact
   grouping, or an equivalent design). Do not solve overflow by shrinking player
   controls/text below the readable design contract.
5. Give top status/quest information a stable high-contrast panel or pill and
   keep debug/session/schema data behind F3.
6. Companion open state must show a distinct title, turn history, proposal state,
   visible text input and privacy/history controls without clipping or overprint.
7. Bridge evidence must show an actual distinct manual send/import or consent
   state, not merely reuse the responsive frame.
8. The manifestation object must read at game distance. Capture each real state
   only after the runtime reports it: wireframe, hologram, materializing,
   complete/confirmed, and cancelled/cleared.

## Screenshot truth gates

Produce a new directory `orchestration/evidence/g8_ui_visual_correction_002/`
containing at minimum:

- `overview_1280x720.png`
- `responsive_868x517.png`
- `companion_open_868x517.png`
- `bridge_manual_state.png`
- `stage_wireframe.png`
- `stage_hologram.png`
- `stage_materializing.png`
- `stage_complete_confirmed.png`
- `after_cancel.png`
- `evidence_manifest.json`

The manifest records width, height, SHA-256, runtime stage/state and capture
timestamp. State-specific images must have distinct SHA-256 values. The harness
must fail on a duplicate, missing file, wrong dimensions, out-of-bounds control,
overlap, missing ChatInput, wrong runtime stage, or any Godot `ERROR:`.

Do not capture two names in the same frame without changing the claimed state.
Banner text is secondary evidence; the object and control states must visibly
match the manifest.

## Regression gates

- Validator PASS; eight new receipts schema-valid.
- Headed smoke clean log and screenshot manifest PASS.
- G3=76, G4=22, manifestation=8, Companion, Bridge and edition/boot PASS.
- Six tracked G3/G4 exports remain zero-diff.
- No reset/delete/install/dependency/voice/live provider/credential/public
  network/push/deploy/publish.

Return `REVIEW_REQUESTED / WAITING_CODEX`, never ACCEPTED.

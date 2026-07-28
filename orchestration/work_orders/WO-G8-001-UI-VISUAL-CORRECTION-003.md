# WO-G8-001-UI-VISUAL-CORRECTION-003

Directive: 24  
Task: G8-001  
State: APPROVED NARROW CORRECTION  
Parent: the one existing Grok Desktop conductor task only

## Purpose

Close the five evidence/readability blockers in
`orchestration/reviews/CODEX_G8-001_UI_VISUAL_REVIEW_003.json`. Preserve every
working patch and every Directive 22 character/skill binding. Do not rebuild the
Starter Realm or replace the existing UI.

## Dispatch and ownership

Use the same eight installed profiles, no nested grandchildren, no self-accept,
and one writer per file.

| Wave | Profile | Authority | Sole responsibility |
|---|---|---|---|
| C0 | schema | VERIFY_ONLY | Convert all five Codex findings into executable assertions; receipt only |
| C1 | core | PATCH_DRAFT | Canonical headed runner, `headed_visual_smoke.gd`, HUD/main and valid Bridge snapshot setup only |
| C2 | executor | PATCH_DRAFT | `headed_demo_flow.gd` and Starter Realm status panel only; make cancel visibility measurable |
| C3 | companion | VERIFY_ONLY | Verify 868x517 text/input/privacy/history visibility; receipt only |
| C4 | manifestation | VERIFY_ONLY | Verify cancelled preview node/collision is absent while prior committed objects remain legitimate; receipt only |
| C5 | asset | VERIFY_ONLY | Visual critique of status contrast, stage readability and cancel before/after evidence; receipt only |
| C6 | persist | VERIFY_ONLY | Prove an isolated seeded saved art-style survives capture/reload byte-for-byte; receipt only |
| C7 | network | VERIFY_ONLY | Purple final evidence/authority gate; never patch |

Every receipt goes under
`orchestration/receipts/g8/ui_visual_correction_003/`, validates against the MAF
step-contract schema, and retains the Directive 22 TrustLayer/UI character,
skills, context hash, trace and handoff fields.

## Required corrections

1. Add a canonical external headed runner that captures stdout and stderr,
   rejects any unexpected `ERROR:`, `SCRIPT ERROR`, parse/compile failure or
   non-zero exit, then validates the manifest. A direct exit-0 marker from the
   GDScript is not the final gate. Allowlisted negative-test ERROR output from
   unrelated headless tests must not be confused with this headed run.
2. Replace the weak saved-choice probe with isolated deterministic evidence:
   seed a non-Cozy choice in a test-only user-data/config location, load it,
   perform ephemeral Cozy capture, reload, and prove the original choice and
   persisted file hash are unchanged. Never alter the human user's real save.
3. Use a schema-valid UUID-shaped snapshot for Bridge evidence. The manual
   frame must show a visible consent/export/import result with operation, path or
   status; zero snapshot validation warnings are allowed for the capture.
4. Put Starter Realm title, quest, status and Companion hint on a stable
   high-contrast surface. At 868x517 use at least 12px player-facing labels and
   12px action text with controls at least 32px high; keep them inside viewport
   without overlap or clipping.
5. Make cancellation proof visible and executable. Capture a distinct
   `stage_cancel_preview.png` before cancel and `after_cancel.png` after cancel.
   The cancelled preview entity/node must be absent after cancel, preview count
   must be zero, collision must be zero, and a defined world-region comparison
   must visibly change. A previously committed object may remain, but it cannot
   obscure which preview was cancelled; use a distinct transform/entity or an
   isolated capture scene.
6. Write the evidence manifest only after every required-file and semantic
   check. It must contain the final total, final verdict, runner log hash,
   preview counts/entity IDs, runtime state, dimensions and SHA-256.

## Evidence and regression gate

- At least ten distinct state-accurate PNGs, including the nine prior names plus
  `stage_cancel_preview.png`.
- `after_cancel.png` proves the cancelled preview entity is absent; banner text
  alone is insufficient.
- Canonical headed runner PASS with zero unexpected error/warning for the Bridge
  snapshot and no stale manifest.
- Validator PASS; eight C003 receipts schema-valid.
- G3=76, G4=22, manifestation=8, Companion, Bridge and edition/boot preserved.
- Six tracked G3/G4 exports remain zero-diff.
- No reset/delete/install/dependency/voice/live provider/credential/public
  network/push/deploy/publish.

Return `REVIEW_REQUESTED / WAITING_CODEX`, never `ACCEPTED`.


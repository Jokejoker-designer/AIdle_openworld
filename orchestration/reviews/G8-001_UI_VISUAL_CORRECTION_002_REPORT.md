# G8-001 UI-VISUAL-CORRECTION-002 Report (Directive 23)

**State:** `REVIEW_REQUESTED` / `WAITING_CODEX`  
**Self-accept:** false · **Not ACCEPTED**  
**Preserves:** Directive 21 + 22 product and character/skill bindings  

## Independent blockers closed

| Blocker | Fix |
|---|---|
| `ERROR Unknown art style` while PASS | ArtStyleManager registers builtins if empty; smoke waits for `is_styles_ready` |
| False Cozy first-run claim | Product rule asserted via `get_default_style_id`; capture Cozy labeled `ephemeral_cozy_for_capture` / `TEST_SETUP` |
| Duplicate responsive/companion SHA | Distinct captures with unique SHA-256 enforced |
| Missing stage shots | Captures after runtime reports wireframe/hologram/materializing/complete/cancelled |
| 868 clip/overlap | Two-row action bar; Companion clearance 86px; geometry assertions |
| Weak top HUD contrast | High-contrast `TopPill` panel |

## Harness gates (must fail smoke)

Godot `ERROR:`, duplicate SHA, missing file, wrong dimensions, out-of-viewport control, Companion∩action-bar, hidden ChatInput, stage mismatch.

## Evidence

Directory: `orchestration/evidence/g8_ui_visual_correction_002/`

- 9 PNGs (distinct SHA-256) + `evidence_manifest.json`
- Log: `orchestration/logs/g8-ui-visual-correction-002.log` — **0 ERROR lines**
- Marker: `AIDLE_UI_VISUAL_CORRECTION_002=PASS` · headed checks=46

## Regression

| Gate | Result |
|---|---|
| Headed visual | PASS (0 ERROR) |
| G3 / G4 | 76 / 22 |
| Manifestation / Companion / Bridge | PASS |
| Validator | PASS |
| Six tracked exports | zero-diff |
| 8 V002 MAF receipts | PASS |

## Waves V0–V7

Same TL/UI bindings as Directive 22. Reviewer waves (V0/V5/V6/V7) do not patch product.

## Residual

- Normal interactive launch still respects saved `user://` style; only smoke uses ephemeral Cozy for capture.
- WARNING lines (e.g. snapshot uuid shape) are not ERROR and do not fail harness.

Awaiting Codex independent re-run of headed smoke + regressions.

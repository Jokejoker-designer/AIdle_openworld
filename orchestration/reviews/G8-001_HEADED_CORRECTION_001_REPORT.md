# G8-001 HEADED CORRECTION-001 Report

**Directive:** 21  
**Work order:** `WO-G8-001-HEADED-CORRECTION-001.md`  
**State:** `REVIEW_REQUESTED` / `WAITING_CODEX`  
**Self-accept:** false · **Not ACCEPTED**

## Intent

Turn the proven 2.5D technical shell into a **readable, locally playable Starter Realm** with mounted text Companion / Free Bridge UI and safe proposal → preview → confirm/cancel — without claiming live AI, voice, or production multiplayer.

## Codex headed blockers addressed

| Blocker (human gate) | Correction |
|---|---|
| Flat purple field + capsule/orb only | Physical Starter Realm (9 landmark groups) from Godot primitives |
| No house/path/farm/props | House, path, farm plots, trees, fence, pond, stones, lamps, flowers |
| UI clipped / missing | Responsive HUD + art selector + action bar + chat anchors at 1280×720 and 868×517 |
| Companion/Bridge not mounted | Chat panel + Free Bridge + action buttons on Main |
| Prompt flow undiscoverable | Demo Build + Confirm + Cancel using real Executor pipeline |

## Waves (eight profiles)

| Wave | Profile | Authority | Result |
|---|---|---|---|
| H0 | schema | VERIFY_ONLY | Acceptance matrix |
| H1 | asset | PATCH_DRAFT | `starter_realm_builder.gd` |
| H2 | core | PATCH_DRAFT | Main/HUD/action bar/art select/headed smoke |
| H3 | companion | PATCH_DRAFT | Chat panel responsive |
| H4 | manifestation | PATCH_DRAFT | Readable stage tints |
| H5 | executor | PATCH_DRAFT | `headed_demo_flow.gd` + panel layout |
| H6 | persist | VERIFY_ONLY | G4=22, zero-diff exports |
| H7 | network | VERIFY_ONLY | Bridge free / secrets refused / no bypass |

## Executable proof

| Gate | Marker |
|---|---|
| Clean 2.5D boot | fixed-angle camera + landmarks=9 |
| Headed visual smoke | **`AIDLE_HEADED_VISUAL_SMOKE=PASS checks=26`** |
| G3 E2E | **`checks=76`** |
| G4 persist | **`checks=22`** + user:// evidence only |
| Six tracked exports vs `60fccdd` | **`SIX_TRACKED_EXPORTS_ZERO_DIFF=PASS`** |
| Validator | `AIDLE_VALIDATION=PASS` |
| Manifestation / Companion / Bridge / Edition | PASS |

Log: `orchestration/logs/g8-headed-correction-001.log`

## Screenshots (headed)

Under `orchestration/evidence/g8_headed_correction/`:

- `overview_1280x720.png`
- `responsive_868x517.png`
- `companion_bridge_ui.png`
- `manifestation_preview.png`
- `after_cancel.png`

## Honesty

| Class | Content |
|---|---|
| **Executable** | Smokes, landmarks count, mounted UI nodes, demo pipeline, zero-diff fixtures |
| **Visual** | Screenshots; art is primitive low-poly (not commercial polish) |
| **Local POC** | Free Bridge manual; Demo Build is local deterministic (not live LLM); Paid fixture |
| **Deferred** | Voice/TTS, free 3D camera, production multiplayer, marketplace, live provider |

## Residual risks

1. Surrealism palette remains dark purple ground — landmarks multi-color but mood still dreamlike.  
2. Companion visual is aura/orb placeholder (readable, not final character art).  
3. Headed smoke window may run briefly on CI agents without display.  
4. Human Product Lead still owns final alpha feel.

## Receipts

`orchestration/receipts/g8/headed/H0_schema.json` … `H7_network.json` (MAF schema-valid).

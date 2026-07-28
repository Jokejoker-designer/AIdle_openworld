# AIdle G8 Human Acceptance Checklist 014

Status: `HITL_REQUIRED`  
Machine verdict: `PASS_FOR_HUMAN_REVIEW`  
Human Product Lead: required for final G8 decision

## Launch

From PowerShell:

```powershell
& 'E:\AIdle_openworld\tools\Godot_v4.3-stable_win64.exe' --path 'E:\AIdle_openworld\game'
```

This launches the local 2.5D alpha only. It does not call a live AI provider,
publish, deploy or connect to a public server.

## Checklist

Mark each item `PASS` or `FAIL` and add a short note for any failure.

| # | Human check | Result / note |
|---:|---|---|
| 1 | Starter Realm immediately reads as warm Cozy Cyber-Pixel / Dreamy Low-Poly, not a flat purple/debug field. | |
| 2 | At the normal window and when resized near 868x517, no important panel/button is clipped or overlapped. | |
| 3 | WASD movement and fixed 2.5D camera feel understandable. | |
| 4 | `E` opens a readable text-only Companion panel; no voice/TTS control appears. | |
| 5 | Free Bridge is clearly manual; Send/Import actions are understandable and do not imply hidden automation. | |
| 6 | `Demo Build` creates a preview and `Confirm`/`Cancel` are discoverable before mutation. | |
| 7 | Wireframe → hologram → materializing → complete states feel visually different enough without relying only on text. | |
| 8 | Cancelling removes the active preview and does not look like a hidden commit. | |
| 9 | Text size, contrast, hierarchy and labels feel acceptable for an alpha at both target resolutions. | |
| 10 | Overall presentation is good enough to freeze Scene 1A and proceed to Control 1B plus Character Foundry Scene 1C. | |

## Known machine-pass residuals

- Environment and characters currently use prototype primitives.
- Compact UI is dense at 868x517.
- Manifestation stages share similar cyan box geometry.
- A prior confirmed building can remain after cancelling a later preview.
- Character Foundry is planned but not implemented in this G8 build.

## Decision

Return exactly one of:

- `G8 HUMAN PASS` — accept Scene 1A and authorize the next work orders.
- `G8 HUMAN FAIL: <items and desired changes>` — keep G8 non-accepted and issue a bounded correction.

G8 is not accepted until this decision is recorded.

# V0 — Executable visual assertions (Directive 23)

Source: `CODEX_G8-001_UI_VISUAL_REVIEW_002.json` · Authority: schema VERIFY_ONLY

| ID | Assertion | Fail if |
|---|---|---|
| A1 | No Godot `ERROR:` in headed smoke log | Any ERROR line |
| A2 | ArtStyleManager ready before set_active_style | Unknown art style |
| A3 | Clean-world Cozy default proven separately from ephemeral test_setup | Cozy claimed without clean-state test |
| A4 | Saved user style preserved when not in test_setup | Persist overwrite without label |
| A5 | 9 required PNGs exist with distinct SHA-256 | Missing/duplicate |
| A6 | Dimensions match claimed 1280x720 or 868x517 | Wrong size |
| A7 | Capture only after runtime stage matches | Stage mismatch |
| A8 | Companion + action bar in viewport, no intersection | Bounds/overlap fail |
| A9 | ChatInput visible when companion open | Hidden/clipped |
| A10 | Bridge capture distinct from responsive frame | Same hash |

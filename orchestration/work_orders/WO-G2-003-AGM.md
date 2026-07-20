# Work Order WO-G2-003-AGM (rework)

| Field | Value |
|---|---|
| Task | G2-003 — AGM-driven Companion + bounded personality |
| Owner | aidle-companion |
| Authority | PATCH_DRAFT |
| Dependencies | G1-003 ACCEPTED |

## Goal

Upgrade text-only Companion base so it consumes **validated AGM Decision Envelope** dialogue/proposal inputs (not inventing world truth). Keep no-commit, drift caps, inspect/lock/reset/delete, **text only**.

## Allowed paths

- `game/scripts/modules/companion/**`
- `game/scenes/modules/companion/**`
- `game/scripts/modules/interfaces/i_companion_module.gd`
- `game/scenes/ui/companion_chat_panel.tscn` + related companion UI scripts
- `orchestration/receipts/G2-003.json` (replace/update)
- this WO status

## Acceptance

1. Apply AGM dialogue from Decision Envelope fixture (validated schema).
2. Build proposals still emit schema-valid pending World Prompt (or hand off to executor only).
3. No direct commit tool; text only (no TTS/STT/voice).
4. Drift caps + inspect/lock/reset/delete still work.
5. Smoke re-run PASS; REVIEW_REQUESTED.

## Forbidden

- No API keys, paid network, Godot install.
- Do not rewrite AGM schemas (consume contracts/agm/**).

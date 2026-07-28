# G8-001 HEADED CORRECTION-001 — Dispatch Map (one writer per file)

Parent: existing Grok Desktop only · Directive 21 · No nested grandchildren · No self-ACCEPT

## Wave order

| Wave | Profile | Authority | Sole write surface |
|---|---|---|---|
| H0 | schema | VERIFY_ONLY | `orchestration/receipts/g8/headed/H0_schema.json`, this matrix notes (no product) |
| H1 | asset | PATCH_DRAFT | `game/scripts/modules/asset/starter_realm_builder.gd` (+ optional `game/scenes/world/starter_realm.tscn` if needed) |
| H2 | core | PATCH_DRAFT | `game/scripts/main/main.gd`, `game/scripts/ui/hud.gd`, `game/scenes/ui/hud.tscn`, `game/scripts/ui/playable_action_bar.gd`, `game/scenes/ui/playable_action_bar.tscn`, `game/scripts/ui/art_style_select.gd`, `game/scenes/ui/art_style_select.tscn` (responsive only) |
| H3 | companion | PATCH_DRAFT | `game/scripts/modules/companion/companion_chat_panel.gd`, `game/scenes/ui/companion_chat_panel.tscn`, `game/scripts/modules/companion/companion_module.gd` (visual/mount helpers only) |
| H4 | manifestation | PATCH_DRAFT | `game/scripts/modules/manifestation/manifestation_instance.gd` (headed stage readability only) |
| H5 | executor | PATCH_DRAFT | `game/scripts/modules/executor/headed_demo_flow.gd`, `game/scripts/modules/g3_ui/starter_realm_controller.gd` (wire demo API only if needed), `game/scripts/modules/g3_ui/starter_realm_panel.gd` + `game/scenes/ui/starter_realm_panel.tscn` (panel layout/actions) |
| H6 | persist | VERIFY_ONLY | `orchestration/receipts/g8/headed/H6_persist.json` only |
| H7 | network | VERIFY_ONLY | `orchestration/receipts/g8/headed/H7_network.json` only |

## Parent-only after waves

- `orchestration/reviews/G8-001_HEADED_CORRECTION_001_REPORT.md`
- `orchestration/receipts/G8-001.json` (update)
- `orchestration/control/grok_status.json`
- `orchestration/logs/g8-headed-correction-001.log`
- `orchestration/evidence/g8_headed_correction/**` screenshots
- `game/scripts/core/headed_visual_smoke.gd` (capture harness — assigned **core** if created as product smoke)

## Overlap rule

If two profiles need the same path → stop and `HITL_REQUIRED`. No profile may edit another profile's product files.

## Forbidden

Voice/TTS/STT, downloaded deps, live provider, credentials, public bind, authority bypass, install/push/deploy/publish, self-ACCEPT, new top-level session.

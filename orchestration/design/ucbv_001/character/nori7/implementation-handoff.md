# Implementation handoff — next: C2 Runtime Build Controls

## C1R status (complete, not accepted — pending Codex gate)

- Prior C1 rejected as C2 input: `019f8c08-d346-7250-b834-1887b51713c6` (immutable `correction_002`)
- C1R child: `019f8c18-933b-7d21-9ecd-bcdda4023cf8`
- Directive 85 · WO mesh-weight correction 004
- Weight-corrected skinned GLB delivered; `accepted=false`

## Read first (in order)

1. `orchestration/design/ucbv_001/character/nori7/C1_character_production_handoff.md`
2. `game/resources/ucbv_001/character/nori7_animation_adapter.json`
3. `game/assets/ucbv_001/character/nori7/export/nori7_bridge_job_manifest.json`
4. `game/assets/ucbv_001/character/nori7/export/nori7_glb_validation.json`
5. `orchestration/control/UCBV_ANIMATION_BLOCK_INTEGRATION_MAP_001.md`
6. `orchestration/design/ucbv_001/style_lock/C0_cream_reconciliation.json`
7. `orchestration/design/ucbv_001/character/nori7/C0_animation_contract_lock.md`
8. Motion kit READ-ONLY: `orchestration/control/motion_kit/**` (do not edit; do not blind-copy adapter.gd)

## Production artifacts

| Item | Value |
|---|---|
| GLB | `game/assets/ucbv_001/character/nori7/export/nori7_rigged.glb` |
| GLB sha256 | `e16d6af8e121879bc3080f2b64d281ee00975ef195db60b622917c28ca594b7f` |
| Blend sha256 | `ba1a04458949d2aacb86dce184b5e1959041c615f2adefc0016b71aef2cbfd36` |
| Package hash | `561a543aac9efbe4da93ab3479616970279a42c91f293d8965ba276ee33015d9` |
| Bridge job | `BLD-UCBV-C1R-NORI7-019F8C18` |
| Bones | 14 exact production hierarchy, root_motion=false |
| Layer A | idle, walk, scan, happy, cancel |
| Layer B extension | turn_left, turn_right, build_place, build_place_hold, confirm |
| Deferred | water, plant_seed, harvest, charge, low_energy (no idle alias) |
| Cream | bible `#fdf3e2` / shade `#efe0c8` + leaf joints + dark face |

## C2 required outcomes (lease elsewhere)

1. Load C1 GLB; fail closed if bones/clips/adapter missing — no procedural normal-play fallback
2. AnimationTree over imported actions per integration map
3. Adapter + 14-bone parent validation + duration/track checks
4. Full 28-module catalog selector; InputMap Q/R + labelled elevation
5. Delete red-X mode via World Commit compensation (no queue_free)
6. Do not edit motion_kit; inspect VERIFY(godot4.3) lines before lifting reference GDScript

## Authority

- C1 writer done; no self-accept
- Next owner: `aidle-worldgen-godot-runtime` under C2 exact lease only

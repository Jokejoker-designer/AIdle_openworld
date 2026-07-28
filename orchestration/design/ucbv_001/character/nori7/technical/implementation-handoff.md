# Implementation handoff — next: C1 real GLB production (then C2 Godot)

## C0 amendment (Directive 83)

Procedural `production_slice_v1` is **not** the correction target. C1 must
deliver a real offline Blender Bridge GLB (skinned mesh + 14-bone rig + keyed
Layer A/B actions). Read:

1. `../C0_animation_contract_lock.md`
2. `../../style_lock/C0_visual_production_preflight.md`
3. `../../style_lock/C0_cream_reconciliation.json`
4. `orchestration/control/UCBV_ANIMATION_BLOCK_INTEGRATION_MAP_001.md`

## Read first (in order)

1. C0 locks above
2. `game/assets/ucbv_001/character/nori7/package_manifest.json` (prior slice — historical)
3. `game/assets/ucbv_001/character/nori7/skeleton/skel_small_biped_robot_v1.hierarchy.json`
4. `game/assets/ucbv_001/character/nori7/animations/anim_robot_gardener_v1.timing_table.json`
5. `game/assets/ucbv_001/character/nori7/animations/animation_state_machine.json`
6. `game/assets/ucbv_001/character/nori7/sockets/attachment_sockets.json`
7. `game/assets/ucbv_001/character/nori7/skin/skin_weight_policy.json`
8. `game/assets/ucbv_001/character/nori7/export/glb_export_contract.json`
9. U2 visual package + modular_body_outfit_definition.json (cream multi-value body)
10. `orchestration/design/ucbv_001/character/nori7/technical/U4_character_rig_animation.md`

## Frozen hierarchy / names (still binding)

| Item | Value |
|---|---|
| Identity | CCP-RH-001 / Nori-7 / recipe_nori7_v1 |
| Skeleton production bones | 14 named bones (not DNA [root,body,head]) |
| Animation set id | anim_robot_gardener_v1 (**names/compatibility only** until C1 keys GLB) |
| Required Layer A | idle, walk, scan, happy, cancel |
| Required Layer B (UCBV extension) | turn_left, turn_right, build_place, build_place_hold, confirm |
| Mesh mode for Dir 83 | **real skinned GLB** (procedural slice is non-passing fallback for normal play) |
| Bridge | offline only; **no install** |

## C1 duty (production)

1. Offline Blender Bridge job → conditioned GLB under C1 asset lease.
2. Exact 14-bone parents; sockets hand_R / chest / sprout_ctrl.
3. Named materials: bible cream + shade + leaf joints + face (not flat white).
4. Key all required actions; adapter documents Tier3 base vs extension honestly.
5. Provenance hashes; log only to C1 leased log or OS temp outside repo.

## C2 duty (integration — not C1)

1. Import GLB; fail closed if bones/actions missing (no procedural normal-play fallback).
2. AnimationTree per integration map; markers never World Commit.
3. 28-module catalog UI, InputMap Q/R/elevation, delete compensation path.


## Do not

- Treat DNA placeholder bones as production
- Put World Commit inside animation events
- Mutate block package unless lease grants
- Self-accept U4 or U5 output
- Invent recipes or Bác Bắp rig resolve

## First U5 artifact should prove

1. 14-bone Skeleton3D loads; silhouette still matches U2  
2. All MVP clips play at table durations  
3. Preview → confirm → cancel transitions fire from real UI/block flow  
4. Character readable next to U3 kit  
5. No client-authoritative ownership from anim  

## Authority

- U4: `accepted=false` / `self_accept=false`
- Next owner: `U5_GODOT_GLB_INTEGRATION`
- No grandchildren from U4 writer

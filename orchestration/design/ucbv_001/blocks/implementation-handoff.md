# Implementation handoff — next: U4 Character Mesh / Rig

## Read first (in order)

1. `game/resources/art_styles/tokens/ucbv_001_shared_character_block_tokens.json`
2. `orchestration/design/ucbv_001/style_lock/U1_unified_style_lock.md`
3. `game/assets/ucbv_001/blocks/family_manifest.json`
4. `game/assets/ucbv_001/blocks/visual_states.json`
5. `game/assets/ucbv_001/blocks/material_bindings.json`
6. `game/assets/ucbv_001/blocks/modules/*.json`
7. `game/assets/ucbv_001/blocks/mesh_descriptors/*.meshdesc.json`
8. `game/assets/ucbv_001/blocks/physics_residuals.json`
9. U2 Nori package under `game_character/ucbv_001/nori7/visual_package/`

## Frozen in U3 (blocks)

| Role | module_id |
|---|---|
| foundation | `block_platform` |
| floor | `arch_floor_round_4m` |
| wall | `block_panel` |
| corner | `block_cube_round` |
| door | `arch_door_round` |
| window | `arch_window_frame_simple` |
| roof | `arch_roof_dome_4m` |
| fence | `block_beam` |
| prop | `prop_crate_small` |
| wall_door | `arch_wall_door_4m` |

Do not invent alternate production ids without a new allowlist accept wave.

## U4 duty (character)

- Production mesh + real skeleton for Nori-7 only (not blocks)
- Animation timing table for `anim_robot_gardener_v1`
- LOD0–2 matching U2 silhouette package
- Keep block style lock for belonging tests (Nori + kit frame)

## U5 duty (integration)

- Instantiate mesh descriptors as MeshInstance3D / CSG placeholders
- Bind materials via `material_bindings.json` + live MAT_* resources
- Wire manifestation stages; collision only at complete after commit
- Respect socket residuals; do not invent socket types
- Optional later: offline Blender GLB replace descriptors if bridge exists

## First U4 artifact should prove

1. Nori LOD0 silhouette still matches U2
2. Real bone hierarchy (not placeholder shared bones)
3. Still readable next to cream wall + fence post from this kit
4. No block package mutation unless lease grants it

## Authority

- U3: `accepted=false` / `self_accept=false`
- Next owner: `U4_CHARACTER_MESH_RIG`
- No grandchildren from U3 writer

# U4 — Nori-7 Character Rig + Animation (production specs)

Identity: **Nori-7 / CCP-RH-001**  
Recipe: `recipe_nori7_v1`  
Skeleton: `skel_small_biped_robot_v1`  
Animation set: `anim_robot_gardener_v1`  
Style lock: `ucbv_001_style_lock_v1`  
Authority: `PATCH_DRAFT` · `accepted=false` · `self_accept=false`  
Wave: **U4_CHARACTER_MESH_RIG** · Directive 81  
Child ref: `019f8ab9-38c8-7e60-8c41-d83a485b27a1`

## 1. Purpose

Author the **production** skeleton hierarchy, skin/socket policy, and **explicit
animation timing table** for the first-slice companion so U5 can integrate
Nori-7 into Godot next to the U3 block kit.

This wave does **not** patch `main.gd`, scenes, or block assets.

## 2. DNA catalog residual (must not be production truth)

| DNA field | Value | Status |
|---|---|---|
| `required_bones` | `[root, body, head]` | **PLACEHOLDER residual** — identical across all skeleton families |
| `bone_count_target` | 14 | Retained as production bone count |
| `attachment_sockets` | hand/back/head/vfx | Names retained; transforms authored in U4 |
| `anim_robot_gardener_v1` clips | names only, `events: []` | **No durations in DNA** — U4 owns timings |

See `orchestration/control/CHARACTER_SKELETON_PRACTICAL_FINDINGS_FOR_CODEX_001.md`.

## 3. Production bone hierarchy (14)

```
root
└─ pelvis
   ├─ spine
   │  └─ chest
   │     ├─ head
   │     │  └─ sprout_ctrl
   │     ├─ arm_L → hand_L
   │     └─ arm_R → hand_R
   ├─ leg_L → foot_L
   └─ leg_R → foot_R
```

Full rest transforms (meters, Y-up):  
`game/assets/ucbv_001/character/nori7/skeleton/skel_small_biped_robot_v1.hierarchy.json`

Scale: **1 HU = 0.6 m** → body 1.2 m, sprout tip 1.44 m (U2 proportion guide).

## 4. Sockets (recipe-bound)

| Socket | Parent bone | Module |
|---|---|---|
| `character_back` | `chest` | `attach_water_tank_small` |
| `character_hand` | `hand_R` | `attach_watering_nozzle_A` (stowed / extended) |
| `character_head` | `sprout_ctrl` | `attach_mechanical_sprout_A` |
| `vfx_anchor` | `chest` | presentation only |

Never mix with Block-DNA world-grid sockets.

## 5. Skin / weight policy

Primary: **modular BoneAttachment3D** rigid parts (robot grammar).  
Optional later: linear-blend skin max 4 influences when offline GLB arrives.  
Policy file: `.../skin/skin_weight_policy.json`.

## 6. Animation timing table (MVP required)

| clip_id | duration (s) | loop | runtime transition |
|---|---:|---|---|
| `idle` | 3.0 | yes | IDLE_DEFAULT |
| `walk` | 0.8 | yes | LOCOMOTION |
| `turn_left` | 0.45 | no | ORIENT_LEFT |
| `turn_right` | 0.45 | no | ORIENT_RIGHT |
| `build_place` | 0.65 | no → hold | PREVIEW_PLACE |
| `build_place_hold` | 1.2 | yes | PREVIEW_PLACE_HOLD |
| `confirm` | 0.75 | no | CONFIRM |
| `cancel` | 0.5 | no | CANCEL |

Overlays (art bible ambient): blink 4.0 s; sprout sway ~3.6 s on idle.  
Idle body bob uses robot `bob_small` **3.0 s** (bible §4).

**Runtime mapping (not mockup-only):**

- Preview place → `build_place` → `build_place_hold` while preview/valid/invalid/selected  
- Confirm → `confirm` (presentation cue only; **World Commit is separate**)  
- Cancel → `cancel` (clears non-durable preview)

Events must never mutate inventory, ownership, currency, or call commit.

Full table: `.../animations/anim_robot_gardener_v1.timing_table.json`  
State machine: `.../animations/animation_state_machine.json`

## 7. Mesh / export honesty

- Offline **Blender not available** on host.
- **No GLB binary** in U4.
- Delivered: mesh descriptor + `production_slice_v1` Godot procedural spec + GLB export contract for future B0/quarantine intake (`glb_intake_package.gd`).
- Path when GLB exists: `game/assets/ucbv_001/character/nori7/export/nori7_rigged.glb`

## 8. Provenance

Bound to Foundry **CCP-RH-001**, recipe **recipe_nori7_v1**, style lock  
**ucbv_001_style_lock_v1**. No Bác Bắp / other Foundry IDs.

## 9. Out of scope

- Block assets (U3 frozen)  
- Runtime `main.gd` / scenes (U5)  
- DNA v1.2 / Tier 3  
- Self-accept / Human acceptance  

## 10. Next: U5

Instantiate Skeleton3D + AnimationPlayer + materials; wire preview/confirm/cancel; dual-res headed evidence; optional GLB replace under same export contract.

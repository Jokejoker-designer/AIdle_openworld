# C0 — Nori-7 Animation Contract Lock (Directive 83)

Wave: `C0_VISUAL_PRODUCTION_PREFLIGHT`  
Identity: **Nori-7 / CCP-RH-001** · `recipe_nori7_v1`  
Skeleton label: `skel_small_biped_robot_v1`  
Base set id: `anim_robot_gardener_v1`  
Blend: `cozy_bouncy` · root_motion: **false**  
Authority: `PATCH_DRAFT` · `accepted=false` · `self_accept=false`  
Binding map: `orchestration/control/UCBV_ANIMATION_BLOCK_INTEGRATION_MAP_001.md`

## 1. Tier3 meaning (names / compatibility only)

`anim_robot_gardener_v1` is reused as a **public name and compatibility contract**.
Tier3 catalog clips have **no duration payload** and **empty events**. C1 must
**author real keyed Blender actions** and export them inside the production GLB.
Do not claim DNA catalog clips are animated. Do not activate DNA v1.2 or Tier3
physics packages.

## 2. Production 14-bone hierarchy (exact)

| Bone | Parent |
|---|---|
| `root` | — |
| `pelvis` | `root` |
| `spine` | `pelvis` |
| `chest` | `spine` |
| `head` | `chest` |
| `sprout_ctrl` | `head` |
| `arm_L` | `chest` |
| `hand_L` | `arm_L` |
| `arm_R` | `chest` |
| `hand_R` | `arm_R` |
| `leg_L` | `pelvis` |
| `foot_L` | `leg_L` |
| `leg_R` | `pelvis` |
| `foot_R` | `leg_R` |

**Forbidden production truth:** shared placeholder bones `[root, body, head]`.

Sockets: tool → `hand_R`; tank/VFX → `chest`; sprout → `sprout_ctrl`/`head`.

## 3. Layer A — required gardener actions (GLB)

| Action | Required | Loop intent |
|---|---|---|
| `idle` | yes | yes |
| `walk` | yes | yes |
| `scan` | yes | no (short) |
| `happy` | yes | no (after authoritative complete) |
| `cancel` | yes | no |

Optional polished (only if fully keyed + evidenced): `water`, `plant_seed`,
`harvest`, `charge`.  
Deferred unless real runtime state exists: `low_energy`.  
**Never** alias missing clips to `idle`.

## 4. Layer B — UCBV build extension (game-local)

Must be authored offline as extension — **not** claimed as Tier3 payload:

| Action | Runtime use |
|---|---|
| `turn_left` | orientation change |
| `turn_right` | orientation change |
| `build_place` | preview place one-shot |
| `build_place_hold` | preview hold loop |
| `confirm` | confirm gesture; **never** calls World Commit |

Record extension in C1/C2 adapter:
`game/resources/ucbv_001/character/nori7_animation_adapter.json`
(base set id, extension version, skeleton, GLB path, names, durations, loops,
bones, hashes, triggers).

## 5. Marker / authority rule

Presentation only. Forbidden marker effects: World Commit, deletion, ownership,
inventory, currency, persistence, arbitrary script execution.

## 6. C1 production honesty

- Offline Blender Bridge only; **no install**.
- Real skinned mesh + AnimationPlayer actions required.
- Descriptor / SphereMesh / CapsuleMesh / pelvis-bob-only is **not** sufficient
  for Directive 83 correction target.
- U4 timing table remains reference for durations; C1 keys real tracks to match
  or supersede with evidenced durations in adapter.

## 7. C2 validator intent (do not implement in C0)

Fail closed on: skeleton_id mismatch; bone name/parent mismatch; missing required
actions; duration ≤ 0; no tracks; root motion; AnimationTree state → missing
action; mutation method tracks; silent procedural fallback in normal play.

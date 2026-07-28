# UCBV Animation Block Integration Map 001

Status: Codex binding for Directive 83  
Scope: Nori-7 only; no Tier3 activation and no catalog rewrite.

## What is actually reusable

The Tier3 foundation catalog contains 21 animation sets and 172 named clips.
It is a compatibility/taxonomy contract, not animation payload: zero catalog
clips contain duration data and zero contain non-empty events. The runtime
`skeleton_animation_resolver.gd` currently checks only equality of
`skeleton_id`; it does not prove bone compatibility, clip existence, duration,
tracks or runtime transitions.

Nori-7's accepted recipe binds:

- recipe: `recipe_nori7_v1`
- root module: `char_nori7_base`
- skeleton: `skel_small_biped_robot_v1`
- base animation set: `anim_robot_gardener_v1`
- blend profile: `cozy_bouncy`
- root motion: `false`

Therefore the names, skeleton/set identity, loop flags and blend-profile intent
are reusable. The catalog is not evidence that any clip is animated.

## Production skeleton binding

Do not use the Tier3 shared placeholder bones `[root, body, head]`. Bind the GLB
to the existing 14-bone Nori-7 production hierarchy exactly:

`root, pelvis, spine, chest, head, arm_L, hand_L, arm_R, hand_R, leg_L,
foot_L, leg_R, foot_R, sprout_ctrl`.

The GLB import gate fails if any bone is missing, renamed, duplicated, has an
unexpected parent, or if root motion is enabled. Required sockets are resolved
to real bones/nodes: hand tool → `hand_R`, back tank/VFX → `chest`, head sprout
→ `sprout_ctrl`/`head`.

## Two-layer animation contract

### Layer A — Tier3 gardener base set

Author real Blender actions and export them inside the C1 GLB. Retain the
canonical Tier3 clip IDs as the public names:

| Tier3 clip | Required now | Runtime use |
|---|---:|---|
| `idle` | yes | default loop; subtle breathing/bob, blink and sprout sway |
| `walk` | yes | locomotion loop driven by actual movement input |
| `scan` | yes | short cursor/placement targeting anticipation |
| `water` | optional polished | contextual gardening interaction only |
| `plant_seed` | optional polished | contextual gardening interaction only |
| `harvest` | optional polished | contextual gardening interaction only |
| `charge` | optional polished | non-authoritative rest/charge presentation |
| `happy` | yes | short post-complete reaction after committed result is observed |
| `low_energy` | deferred | only if a real runtime energy state exists; never invent one |
| `cancel` | yes | cancel/refusal gesture; presentation only |

Optional polished clips may ship only if fully keyed and evidenced. Missing
optional clips must be honestly marked deferred, not filled with idle aliases.

### Layer B — UCBV build extension

The base Tier3 set lacks the exact build-control clips needed by the accepted
runtime. Author these offline as a game-local extension, without editing the
Tier3 source catalog:

- `turn_left` and `turn_right`
- `build_place`
- `build_place_hold`
- `confirm`

Record the extension in
`game/resources/ucbv_001/character/nori7_animation_adapter.json`. The adapter
must identify the base Tier3 set, extension version, skeleton, GLB path, action
names, durations, loop flags, required bones, clip hashes and runtime triggers.
It must not claim the extension clips were present in Tier3.

## Required runtime wiring

The imported GLB provides `Skeleton3D`, skinned mesh, `AnimationPlayer` and the
real actions. C2 builds an `AnimationTree` state machine over those imported
actions. Do not regenerate procedural pelvis-bob clips in normal play.

| Runtime fact/trigger | AnimationTree transition | Authority rule |
|---|---|---|
| movement starts/stops | `idle ↔ walk` | animation follows movement; no root motion |
| character orientation changes | `idle/walk → turn_left/right → prior locomotion` | rotation stays gameplay-owned |
| Manual Build preview becomes active | `scan → build_place → build_place_hold` | preview remains non-durable |
| preview valid/invalid | stay in hold; change face/visor overlay only | color is not sole validity signal |
| player confirms valid proposal | `build_place_hold → confirm` | clip never calls World Commit |
| committed complete result is observed | `confirm → happy → idle` | reaction occurs after authoritative result |
| Esc/RMB cancels preview | `* → cancel → idle` | clears non-durable preview only |
| Delete mode entered | `scan` one-shot then idle/hold | cursor targeting only |
| delete proposal confirmed | `confirm`; then reaction after authoritative result | no animation event deletes an entity |
| reduced-motion enabled | same state IDs, snap/end-pose and suppress bob overlays | accessibility must preserve meaning |

Use explicit signals already emitted by Block Assembly (`preview_place`,
`confirm`, `cancel`) plus real movement/orientation and authoritative completion
observations. Add typed signals only where evidence shows a missing seam.

## Validator upgrade

C2 must replace the current ID-equality-only acceptance with fail-closed checks:

1. adapter `skeleton_id` equals the imported GLB skeleton identity;
2. exact 14-bone names and parents match the production hierarchy;
3. every required action exists once, has duration > 0 and at least one
   non-root transform/property track;
4. loop flags match the adapter;
5. root motion is absent;
6. all AnimationTree states resolve to imported actions;
7. build/confirm/cancel/delete presentation contains no world mutation method
   tracks or arbitrary method calls;
8. missing or invalid animation fails visibly and non-destructively instead of
   silently substituting procedural or idle clips.

## Evidence gate

QA must prove visually and from runtime state logs that idle, walk, both turns,
scan, build/place/hold, confirm, happy and cancel are distinct imported GLB
actions. Capture actual input and state-transition timestamps. Hash the GLB,
adapter and imported clip manifest. A list of clip names, a timing JSON, or a
pelvis-bob-only runtime clip is not passing evidence.

Animation markers remain presentation-only. Forbidden marker effects include
World Commit, deletion, ownership, inventory, currency, persistence and
arbitrary script execution.

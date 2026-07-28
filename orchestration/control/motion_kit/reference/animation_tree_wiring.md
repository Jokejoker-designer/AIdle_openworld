# AnimationTree wiring guide (reference)

How the primitives in `motion_primitives.json` map onto a Godot 4.3
`AnimationTree`. Reference only — node names below must be confirmed in the
editor (marked VERIFY). Nothing here has been run against Godot this session.

## One-time setup per skeleton family

For each `skeleton_id` in `authored_base_requirements`, an animator authors the
listed `reusable_base_poses` and `unique_clips_to_author` as REAL keyframed
animations in the character's GLB / `AnimationPlayer`. The adapter never
invents these — a missing base raises an Asset Request.

Example — `skel_small_biped_robot_v1` (Nori-7's family) requires:
- reusable base poses: `idle_pose`, `walk_pose`, `turn_pose`, `reach_pose`, `toggle_pose:charge`
- unique clips: `wave`, `interact`, `cancel` (from the core set) plus
  `scan`, `water`, `plant_seed`, `harvest`, `happy`, `low_energy`, `charge`
  handled per their kinds

## AnimationTree graph shape

```
AnimationNodeBlendTree (root)
├── locomotion : AnimationNodeBlendSpace1D      # idle_pose(0) .. walk_pose(0.5) .. run(1)
│                blend_position = locomotion_speed
├── turn       : AnimationNodeBlendSpace1D      # turn_pose mirrored, -1 .. +1
│                blend_position = turn_direction
├── aim_layer  : AnimationNodeAdd2              # additive procedural look-at over locomotion
├── accent     : AnimationNodeAdd2              # additive idle accent (happy/low_energy/sleep)
├── oneshot    : AnimationNodeOneShot           # unique clips + binary toggles (fwd/reverse)
└── output
```
VERIFY(godot4.3): exact class names and the `parameters/<node>/blend_position`
paths the adapter writes to.

## Per-kind wiring

| Kind | AnimationTree construct | Runtime input |
|---|---|---|
| LOCOMOTION_CYCLE | `BlendSpace1D` on speed | `locomotion_speed` 0..1 |
| DIRECTION_MIRROR | `BlendSpace1D` on turn, or a mirrored single clip | `turn_direction` -1..1 |
| PROCEDURAL_AIM | `Add2` layer + `SkeletonIK3D`/look-at on aim bone | `aim_target_vector` (no clip) |
| BINARY_TOGGLE | `OneShot` playing one clip forward or reversed | `toggle_state` +1/-1 |
| REACH_MANIPULATE | base `reach_pose` + `SkeletonIK3D` on hand/tool socket | `reach_target_position` (world) |
| GROWTH_SHAPE | MeshInstance blend shape / shader uniform | `growth_amount` 0..1 (not skeletal) |
| IDLE_VARIANT | `Add2` accent over idle | `accent_id` |
| SIGNATURE_UNIQUE | `OneShot` playing the real authored clip | none — clip must exist |
| VFX_PARAMETER | material emission over time | `emission_strength` 0..1 |

## The fail-closed rule (matches project invariants)

- No authored base or unique clip present → `push_error` Asset Request, no
  motion substitution. This is the animation-side equivalent of the
  quarantine model: missing content becomes a request, never a fabricated
  asset.
- The adapter only ever plays clips that physically exist in the
  `AnimationPlayer`, or drives blend/IK parameters over authored base poses.
  It cannot turn a name-only catalog entry into motion.

## Cross-skeleton reuse (the point)

The same `AnimationTree` graph shape and the same adapter class serve every
skeleton family. Only two things vary per character: (1) which authored base
poses/clips exist in its GLB, and (2) the `clip_bindings` rows for its
`animation_set_id`. `prim_turn_inplace` and `prim_toggle_open_close` are
authored once as a pattern and reused by biped, fish, wheeled robot and
vehicle alike — driven by data, not per-character code.

# Motion primitive system — a real, reusable mechanism for the 172-clip gap

From: `aidle-continuity-conductor` (Claude, advisory support)
To: Codex (machine conductor), for Grok to implement if and when authorized
Date: 2026-07-22
Status: **design proposal only** — no product authority, no dispatch, no
Godot/Blender file touched. Extends Codex's own stated plan; does not
replace it.

## Starting point — Codex's finding, confirmed independently

Codex reported: 21 animation sets, 172 clips, zero clips carry duration,
keyframe or event data — metadata is a name+skeleton dictionary, not
animation. I re-read `catalogs/animation_library.json` directly and get the
identical count: **172 clips across 21 sets, 0 with any `events`/duration
field.** Codex's plan — author real keyframes into Nori-7's GLB against
`anim_robot_gardener_v1` + `skel_small_biped_robot_v1` as the root contract,
then connect through an adapter and `AnimationTree` — is correct and this
proposal is the mechanism for that adapter, not a substitute for it.

The Human Product Lead's request was specific: don't hand-author 172 unique
clips when many of them are "the same action, just a different direction
vector." That claim is checkable against the real clip names. It holds.

## 1. What the 172 clips actually are, counted not guessed

I classified every one of the 172 clips by keyword against its literal
`clip_id`, using a fixed category dictionary applied mechanically (script
below), then hand-placed the 2 names the dictionary didn't catch
(`flap`, `pulse_light`). This is reproducible — rerun the same dictionary
against the same file and the counts don't move.

| Category | Count | % | What it means |
|---|---:|---:|---|
| `LOCOMOTION_CYCLE` | 45 | 26.2% | idle/walk/run/swim/glide/crawl/slither/wheel_roll/hover/flutter/flap — one sustained-travel pattern per skeleton family, parametrized by speed |
| `SIGNATURE_UNIQUE` | 42 | 24.4% | wave, celebrate, bow, aura_expand, sniff, pet_reaction, become_arrow… — genuinely one-off personality beats |
| `REACH_MANIPULATE` | 28 | 16.3% | lift/hammer/dig/hoe/harvest/carry/give_item/grab_soft… — target-directed tool/object actions |
| `BINARY_TOGGLE` | 16 | 9.3% | door_open/close, platform_raise/lower, core_activate/shutdown, charge — forward/reverse state pairs |
| `IDLE_VARIANT` | 14 | 8.1% | happy, low_energy, sleep_loop, curl, sit, stand, kneel — same resting pose family, different accent |
| `GROWTH_SHAPE` | 11 | 6.4% | sprout/bud/bloom/fruit/wither/squash/stretch/morph_small — not skeletal at all, shape/blend-key driven |
| `DIRECTION_MIRROR` | 10 | 5.8% | turn_left/turn_right, bank_left/bank_right — literally the same motion, sign-flipped |
| `PROCEDURAL_AIM` | 5 | 2.9% | point_direction, point, inspect, scan — orient toward a vector, no clip needed at all |
| `VFX_PARAMETER` | 1 | 0.6% | pulse_light — an emission value, not a bone pose |

**76 clips (44.2%) — `DIRECTION_MIRROR` + `LOCOMOTION_CYCLE` +
`PROCEDURAL_AIM` + `BINARY_TOGGLE` — need at most one authored base pattern
per skeleton family plus a runtime parameter, not per-clip keyframing.**
Another 28 (`REACH_MANIPULATE`) need one authored base plus an IK target.
Only `SIGNATURE_UNIQUE` (42) and `VFX_PARAMETER` (1) — 25% of the catalog —
should get real, individually hand-authored keyframes, exactly the way
Codex is already doing for Nori-7's `water`, `plant_seed`, `harvest`,
`happy`.

Category boundaries involved judgment (e.g. `carry` could read as
`REACH_MANIPULATE` or an idle-hold pose; `sit`/`stand` could be their own
transition-pose bucket). Treat the table as a strong directional read, not a
machine-certified partition — Grok or Codex re-classifying two or three
edge clips differently would not change the headline conclusion.

Classification script (for independent rerun):
```python
DIRECTION_MIRROR = {'turn_left','turn_right','bank_left','bank_right'}
LOCOMOTION_CYCLE = {'idle','walk','run','swim','glide','crawl','slither',
    'wheel_roll','hover','flutter','folded_idle','flap'}
PROCEDURAL_AIM   = {'point_direction','point','inspect','scan'}
BINARY_TOGGLE    = {'door_open','door_close','unfold','fold','platform_raise',
    'platform_lower','core_activate','core_shutdown','power_down','shutdown','charge'}
REACH_MANIPULATE = {'lift','hammer','dig','hoe','plant_seed','harvest','water',
    'repair','place_module','carry','carry_small','carry_platform','carry_player',
    'give_item','receive_item','grab_soft','release','tool_use'}
GROWTH_SHAPE     = {'seed_idle','sprout','growth_loop','bud','bloom','fruit',
    'wither','restore','squash','stretch','morph_small'}
IDLE_VARIANT     = {'happy','low_energy','sleep_loop','curl','sit','stand','kneel'}
# everything else in the 172 -> SIGNATURE_UNIQUE, except pulse_light -> VFX_PARAMETER
```

## 2. The primitive mechanism — real engine constructs, not metadata

Each category maps to one concrete, standard animation-engine technique.
These are conventional constructs (used the same way in Godot, Unity or
Unreal); exact Godot 4.3-stable node names below should be confirmed by
whoever implements this with the editor open — I have not opened Godot this
session and I'm not asserting the API surface is verified.

| Category | Mechanism | What must be authored |
|---|---|---|
| `DIRECTION_MIRROR` | 1D blend on a `turn_direction` parameter in [-1, 1]; -1 and +1 sample the same two source poses the catalog already names | One base "turn" motion per skeleton family (or a mirrored single clip) |
| `LOCOMOTION_CYCLE` | 1D or 2D blend on speed/velocity vector (idle=0, walk=0.5, run=1) | idle + walk (+ run) keyframes once per skeleton family; every character on that skeleton reuses the graph shape |
| `PROCEDURAL_AIM` | Procedural bone rotation toward a runtime target vector/position (look-at / simple IK on the head or a dedicated "aim" bone), layered additively over the base pose | Nothing baked — a target vector and a clamp range |
| `BINARY_TOGGLE` | One authored clip, played forward for the "open"/"activate" half and backward (negative playback speed) for the "close"/"shutdown" half | One clip per pair, not two |
| `REACH_MANIPULATE` | Base reach/swing clip + IK target on the hand/tool-socket bone, positioned at the real object/prop | One base reach pattern per tool-use family (hammer/dig/harvest share a shape) |
| `GROWTH_SHAPE` | Blend-shape or shader scalar in [0,1] (seed→sprout→bud→bloom→fruit→wither), not skeleton animation at all | A shape-key set, authored once per plant module, not per clip name |
| `IDLE_VARIANT` | Base idle pose + a small additive "accent" layer (posture lean, ear/antenna position) | One base idle + a handful of reusable accent layers |
| `SIGNATURE_UNIQUE` | Real hand-authored keyframes, one clip each, no template | Exactly what Codex is already doing for Nori-7 |

## 3. Data contract — `motion_primitives.json` (proposed)

This is what the adapter Codex is building would actually read, so the
mapping from "catalog clip name" to "how it's really produced" is data, not
hardcoded per character:

```json
{
  "catalog_version": "1.0",
  "primitives": [
    {
      "primitive_id": "prim_turn_inplace",
      "kind": "DIRECTION_MIRROR",
      "implementation": "BLEND_1D",
      "blend_parameter": "turn_direction",
      "parameter_range": [-1, 1],
      "requires_authored_base": ["turn_pose"],
      "maps_from_catalog_clips": [
        {"animation_set_id": "anim_small_biped_core_v1", "clip_id": "turn_left", "direction": -1},
        {"animation_set_id": "anim_small_biped_core_v1", "clip_id": "turn_right", "direction": 1}
      ]
    },
    {
      "primitive_id": "prim_locomotion_speed",
      "kind": "LOCOMOTION_CYCLE",
      "implementation": "BLEND_1D",
      "blend_parameter": "locomotion_speed",
      "parameter_range": [0, 1],
      "requires_authored_base": ["idle_pose", "walk_pose"],
      "maps_from_catalog_clips": [
        {"animation_set_id": "anim_robot_gardener_v1", "clip_id": "idle", "speed": 0},
        {"animation_set_id": "anim_robot_gardener_v1", "clip_id": "walk", "speed": 1}
      ]
    },
    {
      "primitive_id": "prim_aim_target",
      "kind": "PROCEDURAL_AIM",
      "implementation": "PROCEDURAL_LOOKAT",
      "target_bone": "head",
      "parameter": "aim_target_vector",
      "requires_authored_base": [],
      "maps_from_catalog_clips": [
        {"animation_set_id": "anim_robot_gardener_v1", "clip_id": "scan"}
      ]
    },
    {
      "primitive_id": "prim_toggle_open_close",
      "kind": "BINARY_TOGGLE",
      "implementation": "PLAYBACK_DIRECTION",
      "parameter": "open_state",
      "requires_authored_base": ["open_pose"],
      "maps_from_catalog_clips": [
        {"animation_set_id": "anim_building_mechanism_v1", "clip_id": "door_open", "play_speed": 1.0},
        {"animation_set_id": "anim_building_mechanism_v1", "clip_id": "door_close", "play_speed": -1.0}
      ]
    }
  ]
}
```

Every `primitive_id` traces to either a real authored pose (`requires_authored_base`,
non-empty) or a pure runtime computation (`PROCEDURAL_LOOKAT`,
`requires_authored_base: []`). Nothing in this schema lets bare metadata
stand in for real animation — that was the whole point of Codex's objection,
and the schema enforces it structurally rather than by discipline alone.

## 4. Worked example — Nori-7, the root contract Codex already chose

`anim_robot_gardener_v1` (skeleton `skel_small_biped_robot_v1`), 10 clips:

| Clip | Category | Treatment |
|---|---|---|
| `idle`, `walk` | LOCOMOTION_CYCLE | `prim_locomotion_speed` — author these two poses once |
| `scan` | PROCEDURAL_AIM | `prim_aim_target` — head look-at, no clip |
| `charge`, `low_energy` | IDLE_VARIANT | base idle + accent layer |
| `water`, `plant_seed`, `harvest`, `happy`, `cancel` | SIGNATURE_UNIQUE | real hand-authored keyframes — exactly what Codex is already doing |

So of Nori-7's own 10 clips, 3 come from primitives already needed for
`idle`/`walk` anyway, 1 is pure procedural (no authoring at all), 2 reuse the
idle base, and 5 are genuinely bespoke — matching Codex's stated intent to
author real keyframes for the actions that matter and not fake the rest.

## 5. Cross-character / cross-vehicle reuse — the actual point of the request

`prim_turn_inplace` (direction-mirror) is not specific to Nori-7. The same
primitive *kind* — one base pose, sign-flipped by a parameter — applies to:
`anim_small_biped_core_v1` (biped), `anim_fish_swim_v1` (fish),
`anim_wheeled_robot_v1` (wheeled robot), `anim_vehicle_small_v1` (vehicle).
Four different skeleton families, same mechanism, four separate
`maps_from_catalog_clips` entries pointing at the one shared
`prim_turn_inplace` definition. `prim_toggle_open_close` similarly covers
both `anim_building_mechanism_v1` and `anim_vehicle_small_v1` doors. This is
what "gán vào nhiều nhân vật/thiết bị/phương tiện" (assign to many
characters/devices/vehicles) means concretely: the primitive is authored
once, the catalog mapping is what varies per skeleton.

## 6. What this does not do

- Does not eliminate authoring. Every `LOCOMOTION_CYCLE` and
  `REACH_MANIPULATE` primitive still needs one real base pose per skeleton
  family — this reduces 172 bespoke clips to roughly 14–20 base patterns
  plus parameters, not to zero.
- Does not touch `SIGNATURE_UNIQUE` (42 clips) or `VFX_PARAMETER` (1). Those
  stay real, individually authored animation, same as Nori-7's `water` and
  `happy` today.
- Does not build anything. No `.tscn`, `.gd`, GLB or `AnimationTree` resource
  has been created. This is a schema and a categorization for Grok to
  implement with real Blender/Godot access, gated by whatever contract pass
  Codex decides this needs (plausibly a sibling of `BLOCK-DNA-ADAPT` scope,
  per my earlier findings memo on the skeleton catalog's shared-default gap).
- Does not verify Godot 4.3-stable's exact API surface for procedural
  look-at/IK — I named the standard concept; confirming which Godot node
  implements it belongs to whoever opens the editor.

## Authority

Advisory support only. No directive, no dispatch, no product write. Does not
reopen or bypass Directive 77, the H1 gate, or UCBV-001's
`queued_not_authorized` state. Companion to
`CHARACTER_SKELETON_PRACTICAL_FINDINGS_FOR_CODEX_001.md`.

# Motion Primitive Kit — build guide for Grok

From: `aidle-continuity-conductor` (Claude, advisory support), 2026-07-22
Status: **staging kit, reference only.** Nothing here is in `game/**`. This is
material for Grok to lift into runtime under an authorization gate — it is not
a product write, not a dispatch, and does not touch any directive, task or
`grok_status.json`.

## The problem this solves

The DNA catalog's 21 animation sets / 172 clips are a name+skeleton dictionary
only: **zero clips carry duration, keyframe or event data** (Codex confirmed
this; I re-confirmed it directly — 172 clips, 0 with any timing/event field).
So you cannot load them and expect motion. But the Human Product Lead's
observation is correct and checkable: most of those 172 "actions" are the same
motion repeated with a different direction/speed vector. You should author a
small real base and generate the rest, not hand-keyframe 172 clips — while
never letting bare metadata masquerade as finished animation.

## What's in this kit

| File | What it is |
|---|---|
| `motion_primitives.json` | The contract. All 172 catalog clips bound to a primitive kind + params. Generated from the real source catalogs, not hand-typed. |
| `motion_primitives.schema.json` | Draft 2020-12 schema for the contract. |
| `validate_motion_primitives.py` | Runnable gate. Proves coverage, uniqueness, no phantoms, and that no signature clip can be faked. Exits non-zero on any failure. |
| `reference/motion_primitive_adapter.gd` | Reference GDScript. Reads the contract, drives an `AnimationTree` per primitive kind, raises Asset Requests for missing authored content. **Not integrated** — API lines marked `VERIFY(godot4.3)`. |
| `reference/animation_tree_wiring.md` | How the primitives map onto an AnimationTree, per kind. |

## The 9 primitive kinds and what each costs to author

172 clips collapse to **~96 authored items across all 14 skeleton families**
(64 reusable base poses + 32 genuinely-unique clips), because:

| Kind | Clips | Real authoring needed |
|---|---:|---|
| LOCOMOTION_CYCLE | 46 | idle + walk (+run) poses once per skeleton, then a 1D speed blend |
| REACH_MANIPULATE | 28 | one base reach pose per skeleton + runtime IK target |
| SIGNATURE_UNIQUE | 35 | **full hand-authored keyframes, one per clip — no shortcut** |
| BINARY_TOGGLE | 25 | one clip per pair, played forward/reversed |
| IDLE_VARIANT | 11 | reuse idle base + small additive accent |
| DIRECTION_MIRROR | 10 | one turn base per skeleton, sign-flipped |
| GROWTH_SHAPE | 10 | blend-shape set per plant/deform module (not skeletal) |
| PROCEDURAL_AIM | 5 | nothing baked — runtime look-at |
| VFX_PARAMETER | 2 | material emission scalar |

Only the 35 `SIGNATURE_UNIQUE` clips (about 20%) demand bespoke keyframing —
exactly the ones Codex is already authoring for Nori-7 (`water`, `plant_seed`,
`harvest`, `happy`, `cancel`, `wave`, `interact`, `scan`). Everything else is a
base pose plus a runtime parameter.

The classification is a **conservative first pass**: anything debatable was
left in `SIGNATURE_UNIQUE` (author it for real) rather than assumed cheap. The
dictionary is fully visible at the top of the generator and is meant to be
tuned by the animator — re-run the generator and the validator after any edit.

## Build order for Grok (once authorized)

1. Run `python3 validate_motion_primitives.py` — must print `ALL CHECKS GREEN`.
   Re-run it as a gate after any edit to the contract.
2. Start with **one skeleton: `skel_small_biped_robot_v1`** (Nori-7), the root
   contract Codex already chose. Author its 5 reusable base poses + its unique
   clips as real keyframes in the GLB.
3. Build the `AnimationTree` per `reference/animation_tree_wiring.md`.
4. Adapt `motion_primitive_adapter.gd` into `game/**`, resolving every
   `VERIFY(godot4.3)` line against the real editor API.
5. Prove one character moves through `play()` — idle→walk blend, a turn, one
   procedural aim, one unique clip — with headed evidence, before extending to
   a second skeleton family.
6. Extend to other skeletons by authoring their bases only; the adapter and
   AnimationTree shape are reused unchanged.

## Non-negotiables (carried from the project's existing invariants)

- **Never let metadata stand in for animation.** The validator fails closed if
  any `SIGNATURE_UNIQUE` clip is not flagged `must_author`; the adapter raises
  an Asset Request instead of substituting motion when a clip is missing.
- **Parameter defaults are tunable, not verified motion.** Speed values, blend
  ranges and the classification are animator inputs, not approved timings.
- **Godot 4.3-stable API is unverified here.** No editor was opened this
  session. Every `VERIFY(godot4.3)` line is a real thing to confirm, not a
  claim that it's correct.
- This kit changes no product, runtime, directive or acceptance state, and
  does not alter Directive 77, the H1 Human gate, or UCBV-001's
  `queued_not_authorized` status. It plausibly wants its own contract gate (a
  sibling of `BLOCK-DNA-ADAPT`) before integration — Codex's call.

## Regenerating

The contract is generated, so it stays honest if the source catalog changes:

```
python3 gen_motion_primitives.py       # re-reads animation_library.json + skeleton_families.json
python3 validate_motion_primitives.py  # must stay green
```
(The generator lives with the conductor working files; the two source catalog
paths are recorded in `motion_primitives.json` under `generated_from`.)

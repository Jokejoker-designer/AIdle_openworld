# Nori-7 end-to-end assembly — what got built, and my honest assessment

From: `aidle-continuity-conductor` (Claude, advisory support), 2026-07-22
Character: Nori-7 · `CCP-RH-001` (accepted Character Foundry record 1 of 28)
Artifacts: `character_assembly_nori7_001.json` (this folder),
`../motion_kit/*`, `../visual_reference/UCBV_VISUAL_MOCKUP_003_ANIMATED.html`
Status: reference/demonstration only — no product write, no dispatch, nothing
in `game/**`.

## What "create a character" actually produced here

I did not draw a picture and call it a character. I **composed CCP-RH-001 from
real catalog parts and machine-verified every join**, then resolved its whole
action set through the motion kit. The assembler checked 19 joins, all pass:

- identity → `char_nori7_base` exists, is the accepted record, not invented
- skeleton → `skel_small_biped_robot_v1` (14 bones, BIPED), and the animation
  set actually targets that skeleton (not a mismatch)
- 3 attachments → water tank / nozzle / sprout, each mounted through a socket
  pair that is valid in `socket_types.json` **and** declared by both modules
  (`character_back↔back_attachment`, `character_hand↔tool_grip`,
  `character_head↔head_attachment`)
- material → `mat_cozy_cream_leaf_v1`, body slot valid, colour `#F7E9C6`
- animation → all 10 clips of `anim_robot_gardener_v1` resolve in the motion kit

Then the build plan for its 10 actions came out concrete:

| Tier | Count | Clips |
|---|---:|---|
| procedural (no authoring) | 1 | scan |
| base-pose driven (author base once, reused) | 7 | idle, walk, water, plant_seed, harvest, happy, low_energy |
| **must author (real keyframes)** | 2 | charge, cancel |

So the whole gardening companion needs, at the floor, **2 bespoke clips + a
handful of shared base poses** — not 10 hand-animated clips. That is the point
of the exercise, and it is now demonstrated on a real character, not asserted.

## My honest assessment — and where I'd push back on myself

**What is genuinely real now.** A complete, validated character *build
specification*: every part exists in an accepted catalog, every join is
socket-legal, every action has a defined production method. If Grok opens
Blender/Godot tomorrow, there is no ambiguity about what Nori-7 is made of or
how each action is produced. That is real progress over "a name in a manifest."

**What is still NOT a character — say it plainly.**
1. **No geometry exists.** `char_nori7_base` is `status: DESIGN_READY` — a
   catalog id, not a mesh. There is no GLB. The animated figure in the preview
   is *my SVG illustration* of the spec, not the game asset. Nobody has modelled
   Nori-7 yet.
2. **The skeleton is still a placeholder.** `skel_small_biped_robot_v1` stores
   only `[root, body, head]` — the real 14-bone hierarchy the bone_count_target
   promises is not authored anywhere. "14 bones" is a target, not a rig.
3. **The animation clips still have zero keyframes.** The "base-pose driven"
   tier assumes base poses (`idle_pose`, `walk_pose`, `reach_pose`, `turn_pose`)
   that **do not exist yet**. The kit says *how* to build them cheaply; it does
   not contain them.
4. **My "2 must-author" is a floor, and I'd argue it's too low for a hero.**
   The kit classified `water`, `plant_seed`, `harvest` as generic reach+IK. But
   those are exactly the charming, character-defining gardening actions the art
   bible cares most about. A real animator may well want them hand-authored for
   personality — in which case Nori-7's bespoke count is more like 5, matching
   my earlier findings memo. The kit gives the cheap path; it should not be read
   as *mandating* it for a flagship character. This is a genuine tension, not a
   solved question.
5. **The two-palette problem is still open** — the recipe's `#F7E9C6` vs the
   art bible's `#fdf3e2`. Whoever models Nori-7 needs one canonical cream.
6. **Godot 4.3 API is unverified** — no editor opened; the adapter's wiring is
   reference, not confirmed.

**Verdict.** This is as far as "creating a character" can honestly go from here
without Blender/Godot and an authorization gate: a fully-wired, machine-checked
build specification plus a concrete, per-action authoring plan, demonstrated on
the exact character Codex already chose as the root contract. The remaining
work — modelling the mesh, authoring the real bone hierarchy, keyframing the
base poses and the 2–5 signature clips — is asset production that needs Grok
with real tools, and (my recommendation) its own contract gate, because it
inherits the skeleton-catalog placeholder gap and the palette conflict above.

The most useful thing this proved: the pipeline **holds end to end**. Parts →
sockets → skeleton → animation → motion primitives all connect with zero broken
joins on a real character. The gaps that remain are honest authoring gaps, not
architecture gaps.

## Authority

Advisory support only. No product/runtime/directive/acceptance change. Does not
alter Directive 77, the H1 Human gate, or UCBV-001's `queued_not_authorized`
state.

# Dispatch — Blender camera-match tooling for the 6-building redo-loop (paste to Grok, build parent 019f7ffd)

Human Product Lead authorized (2026-07-24, `codex_directive.json` object_level_human_decision
`blender_camera_match_tooling_authorized`): install two free/open-source Blender
addons as artist-side modeling aids, and use them to fix the likely root cause
of the 6-building redo-loop stalling at HIGH_PARTIAL across V3-V7.

## Root cause hypothesis (verify, don't assume)

`game/scripts/camera/cozy_camera.gd` already hard-locks the MVP camera exactly:

- `pitch_degrees = 42.0`
- `fov = 42.0` (perspective)
- three-quarter isometric read, per `MOCKUP_DESIGN_LOCK.md` §2 ("Camera |
  Fixed three-quarter / isometric")

The MOCKUP_SSOT_V2 reference renders were presumably produced at this same
locked angle. If your V3-V7 fidelity comparisons have been judging silhouette
match "by eye" or from a headed-QA screenshot taken at a slightly different
angle/distance/FOV than the mockup source, that alone could explain why
6 buildings keep landing HIGH_PARTIAL with a genuinely different mesh
approach each time (V5, V6, V7 all tried different strategies and all still
came up short) — you may be modeling correctly but comparing at a
mismatched angle.

## What's authorized now

1. Install **fSpy-Blender** (`github.com/stuffmatic/fSpy-Blender`, GPL-3.0,
   official fSpy importer add-on) into your local Blender.
2. Install **real_scale_references** (`github.com/Pullusb/real_scale_references`,
   free) into your local Blender.
3. Use both purely as Blender-side authoring aids. Nothing about either
   addon ships in `game/**` or in any exported GLB — they only help you
   build/verify geometry inside Blender before export.

Not authorized by this dispatch: any other dependency install, any change to
`cozy_camera.gd`'s locked values (read-only reference), any Godot version
change, any network/shipping action. Those remain Red F01 hard stops as
always.

## What to actually do

1. In Blender, set up a camera at the exact locked values: pitch 42° above
   horizontal, 42° perspective FOV. (fSpy-Blender can help you verify this
   against the mockup image directly if the mockup PNG has enough
   perspective cues; if not, just set the values manually — they're already
   known exactly, no need to solve for them.)
2. For each of the 6 still-open buildings (MARKET, GARDEN, WELL, WINDMILL,
   BRIDGE, LOOKOUT), load that building's `MOCKUP_SSOT_V2` reference image
   as the camera background at this exact camera setup.
3. Model/adjust the mesh with the mockup image visible behind it at the
   correct angle — this gives you a pixel-level silhouette overlay instead
   of comparing two separately-rendered screenshots by eye.
4. Use `real_scale_references` if useful to sanity-check absolute
   proportions (door/human height comparisons) while you work.
5. Re-run headed QA and fidelity scoring exactly as before (same honesty
   rules: `matching_100_pct` only if genuinely 100%, `same_sig_streak`
   tracking continues, 3x identical signature still routes NEED_HUMAN).
6. In the next fidelity receipt, add a field noting whether this camera-match
   workflow was used for each building, and whether the previous
   angle-mismatch hypothesis actually explains the prior residuals or not —
   report honestly either way. If it doesn't help, say so; don't force a
   narrative.

No other scope changes. Everything else (props, Nori-7 animation, HOME.CHAR,
architecture/story-bible adherence) continues exactly as already authorized
under `continuous_iteration_authorization`.

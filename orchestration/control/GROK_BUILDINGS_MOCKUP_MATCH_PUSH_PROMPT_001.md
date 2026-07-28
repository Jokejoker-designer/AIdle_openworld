# Dispatch — Push the 6 buildings to actual mockup match (paste to Grok, build parent 019f7ffd)

Human Product Lead: "Viết promt yêu cầu cho Grok làm khớp Mockup cho tôi" —
make the 6 buildings actually match `MOCKUP_SSOT_V2`, not just "improved."
This continues under the already-standing **100% mockup fidelity law**
(`AIDLE_GAME_VISION_LOCK_001.md` §12) and `continuous_iteration_authorization`
— no new permission is being granted here, this is a direct push on the
existing redo-loop using what V11 already found.

## Where this picks up

`BUILDINGS_FIDELITY_V11.json` (camera-match pass) reported honestly:
`angle_mismatch_hypothesis.result = "PARTIAL_SUPPORT"` — the locked-camera
overlay (pitch 42°, FOV 42°, per `cozy_camera.gd`) genuinely improved
silhouette proportions, but you yourself identified two remaining residual
causes that camera-matching alone does not fix:

1. **Material wash under town lighting** — colors read differently in the
   actual town lighting rig than in an isolated Blender viewport (you found
   this yourself in V9/V10: green→lavender, wood→cream). Your V10
   material/emission pass helped but didn't close it.
2. **Soft-clay topology vs mockup finish** — the mockups have a crisper,
   more defined surface language than the current meshes.

Per-building residual signatures as of V11 (all still `HIGH_PARTIAL`,
`same_sig_streak: 0` — fresh residual family, full redo-loop budget
available again):

| Plot | V11 signature | What's still short |
|---|---|---|
| MARKET.BLD | `market_camera_match_silhouette_open_front_high_partial` | front/awning read |
| GARDEN.BLD | `gazebo_camera_match_flower_dome_silhouette_high_partial` | dome finish |
| WELL.BLD | `well_camera_match_aframe_proportion_high_partial` | roof/body proportion |
| WINDMILL.BLD | `windmill_camera_match_sail_body_ratio_high_partial` | sail/body ratio |
| BRIDGE.BLD | `bridge_camera_match_arch_void_silhouette_high_partial` | arch void clarity |
| LOOKOUT.BLD | `watchtower_camera_match_cabin_thatch_ratio_high_partial` | cabin/thatch ratio |

## What to do now

1. **Keep the camera-match setup** (fSpy-Blender + real_scale_references,
   pitch 42° / FOV 42°, mockup jpg as background) — it's working, don't
   abandon it. Layer the next fixes on top of it, don't replace it.
2. **Fix the lighting/material mismatch specifically**: render your
   in-Blender comparison (or a headed Godot capture) under the *actual*
   town lighting rig, not an isolated studio-lit Blender viewport. Adjust
   base colors so they read correctly under town lighting, not just in
   isolation. This was your own finding — close it this time.
3. **Address the soft-clay-vs-crisp-mockup gap directly**: increase edge
   definition / add supporting geometry where the mockup shows sharper
   silhouette breaks (roof edges, window frames, structural beams) rather
   than relying on smooth/rounded default primitives. Reference each
   building's specific mockup image (`bld_05_market.jpg`, `bld_10_gazebo.jpg`,
   `bld_07_well.jpg`, `bld_06_windmill.jpg`, `bld_09_bridge.jpg`,
   `bld_08_watchtower.jpg`) for exactly which edges/details are missing.
4. **Redo-loop per the standing law**: iterate each of the 6 buildings
   until it genuinely reaches 100% match (silhouette, proportions, palette,
   stated key details) — or until the same residual signature repeats 3x,
   at which point that specific building stops and routes `NEED_HUMAN`
   (do not keep looping a stuck building; move to the others).
5. **No inflation**: `matching_100_pct` is only set `true` for a building
   that genuinely, visually matches — checked via headed screenshot
   evidence against the mockup art itself, the same standard used for every
   other object in this project (e.g. `cozy_house_small_A` v1→v9). "Close
   enough" or "much better" is not 100%.
6. Emit the usual schema-valid MAF receipt each pass: `accepted=false`,
   `self_accept=false`, honest `same_sig_streak` per building, note whether
   the lighting fix and topology fix are what's applied that pass (don't
   conflate with another camera-match-only pass — be specific about which
   lever you pulled).

## Still frozen / still out of scope

- No position, rotation, footprint, or grid-cell change for any of the 50
  plots — `town_grid_plan_v1.json` stays exactly as-is.
- `HOME.BLD` remains `CLOSED_PERMANENTLY`, untouched.
- No new addon installs beyond fSpy-Blender + real_scale_references already
  authorized. No `cozy_camera.gd` changes. No Godot version change. No
  network/shipping action.
- Props, Nori-7 animation, HOME.CHAR, and architecture/story-bible adherence
  continue exactly as already authorized — this dispatch is scoped to the
  6 buildings only.

Goal: an honest, evidence-backed push toward real 100% match on as many of
the 6 as genuinely achievable, with any building that's truly stuck (3x same
signature) surfaced to Human rather than silently iterated forever.

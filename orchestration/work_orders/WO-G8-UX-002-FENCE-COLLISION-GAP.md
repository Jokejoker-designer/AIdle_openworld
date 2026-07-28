# WO-G8-UX-002 — Fence collision gap

Authority: `PATCH_DRAFT` (Blue only) · State: `READY`
Issued by: `aidle-continuity-conductor` — **NOT Codex**
Authorized by: Human Product Lead, 2026-07-21, second live playtest after
WO-G8-UX-001. Same override basis as WO-G8-UX-001: Directive 50 forbids Godot
patches and `Control-1B` is BLOCKED; this narrow scope is explicitly
authorized by the Human Product Lead. Does not unblock `Control-1B` or `P1E`,
does not change `G8-001` from `HITL_REQUIRED`.

## Confirmed fixed — do not re-touch

Human live retest after restart confirms WO-G8-UX-001 fixed: action-bar
buttons no longer trap keyboard focus, movement works immediately after a
button click, and the player now collides correctly with a completed
manifestation (previously walked straight through). Do not modify
`playable_action_bar.gd`, `player_controller.gd`, `player.tscn`, or the
manifestation collision layer — those are done.

## New finding — fence is walkable through

Human report during second playtest: walking into the fence passes straight
through it.

**Root cause, confirmed by measurement, not guessed:**
`game/scripts/modules/asset/starter_realm_builder.gd:290-293`:

```gdscript
for i in range(5):
    _box(fence, "Post%d" % i, Vector3(0.12, 0.9, 0.12), Vector3((i - 2) * 1.1, 0.45, 0), p["wood"], true)
    if i < 4:
        _box(fence, "Rail%d" % i, Vector3(1.0, 0.08, 0.06), Vector3((i - 1.5) * 1.1, 0.55, 0), p["wood"], false)
```

Posts are 0.12m wide, spaced 1.1m center-to-center, so the gap between adjacent
post surfaces is 1.1 − 0.12 = **0.98m**. The player capsule
(`game/scenes/player/player.tscn`) has `radius = 0.35`, diameter **0.70m**.
Since 0.98 > 0.70, the player fits through the gap.

The `Rail` boxes are positioned and sized to span exactly that gap
(`Rail0` center −1.65 spans −2.15..−1.15, closing the −2.14..−1.16 opening
between `Post0` and `Post1`) but are created with `with_collision = false` —
they are visual-only. This is not a layer/mask defect like WO-G8-UX-001; the
fence has no collision at all in the gaps, by construction.

This is unrelated to the manifestation system — `starter_realm_builder.gd` is
static procedural geometry, separate from `manifestation_instance.gd`.

## Fix

Change the `Rail` boxes' `with_collision` argument from `false` to `true` in
`_build_fence()`. That is the entire functional change: the rails already have
correct position and size to seal the post-to-post gaps; they only lack a
collision body.

Do not change post geometry, spacing, or the visual mesh. Do not add new nodes
beyond what `with_collision = true` already produces via the existing `_box()`
helper.

## Also verify — do not assume

1. Confirm no other starter-realm prop with multiple discrete solid pieces has
   the same gap problem (stones, lamp poles, farm plot). These appeared to be
   single-piece or intentionally non-solid in the earlier audit
   (WO-G8-UX-001 defect 5) — re-check briefly, don't re-litigate.
2. Confirm the rail's vertical band (y = 0.51 to 0.59) actually blocks a
   grounded player capsule rather than only technically overlapping — add the
   regression test below rather than assuming geometry math is sufficient.

## Writer allowlist

- `game/scripts/modules/asset/starter_realm_builder.gd` (the `with_collision`
  flag only, plus anything defect-1 above requires if a second gap is found)
- a new regression test under `game/tests/` (or an addition to
  `game/tests/g8_ux_input_collision_smoke.gd`) proving the player is blocked
  when driven at the fence line between two posts
- its exclusive receipt, log and trace

If anything outside this list turns out to be necessary, stop and report
rather than writing it.

## Out of scope

Everything WO-G8-UX-001 already declared out of scope, plus: any change to
`manifestation_instance.gd`, `player_controller.gd`, `playable_action_bar.gd`,
or `player.tscn` — those are verified fixed. `E:/AIdle_Blender_Bridge_P0`
untouched.

## Dispatch graph

Same parent `019f7ffd-3995-71c0-aca1-51078e24a852`. Sequential, one child at a
time, no grandchildren: `aidle-worldgen-control-input` PATCH_DRAFT sole writer,
then `red` READ_ONLY_AUDIT, then `qa` VERIFY_ONLY, then `purple` VERIFY_ONLY.

## Acceptance criteria

1. Player driven at the fence line between any two posts does not pass through.
2. Rail collision does not change the fence's visual appearance.
3. WO-G8-UX-001 fixes (focus, jump, arrows, manifestation collision) unchanged.
4. No pre-existing test regresses.
5. Regression evidence — real physics simulation against the actual scene, not
   a mock — proving the fence blocks the player.

## Receipt requirements

Same as WO-G8-UX-001: real durable Grok child/transcript ref cross-checked
against `grok_status.json`, `accepted=false`, `self_accept=false`. Return
`REVIEW_REQUESTED`, `CHANGES_REQUESTED` or `WAITING_HUMAN`.

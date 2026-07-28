# WO-P1E-003 — P1E wave 1: exposure, missing props, density

Authority: `PATCH_DRAFT` (Blue only) · State: `READY`
Issued by: `aidle-continuity-conductor` — **NOT Codex**
Authorized by: Human Product Lead, 2026-07-21 — art direction approved from
mockup; Godot override already granted for the P1E intake path

Art spec: **`Scene/AIdle_Blender_Environment_Scene_Blueprint_v1.0/world_profiles/COZY_ART_BIBLE_001.md`**
Read it first. It carries exact hex values, animation durations and lighting
targets transcribed from the approved mockup. Build to those numbers.

## Why this wave exists

The Human Product Lead played the GLB realm and was disappointed. That reaction
is diagnostically correct and was confirmed by measurement:

- The old procedural placeholder realm used **12 builder categories** producing
  dozens of objects (fence, flowers, rocks, lamps, ground variation…).
- The new GLB realm places **9 module instances** from 7 module types.
- The kit has **no fence, no flowers, no lamp, no loose rocks** at all.

So the "upgrade" to real assets **lost world density and lost four object
categories**. The scene reads as seven objects on an empty plane.

Compounding it, the lighting fix overcorrected: measured **mean luma 231/255,
66.2 % of pixels blown past 245, 0 % shadow content**. With no shadow, the
fixed-angle 2.5D camera cannot read form, which makes the sparse scene look
flatter still.

## Task 1 — Fix exposure (do this first)

Per art bible §8:

| Metric | Target |
|---|---|
| Mean luma | 150–185 |
| Blown (> 245) | **< 3 %** |
| Shadow (< 40) | 5–15 % |

Warm high three-quarter key. Shadows soft, present, directional.

**Do this before authoring any material**, for the same reason the underexposure
fix was sequenced first in `WO-P1E-001`: materials colour-judged against a wrong
exposure have to be redone.

## Task 2 — Author the four missing modules

Follow the module record schema in `04_BLENDER_LIBRARY_AND_TEMPLATE_STANDARD.md`
plus the extended fields (`lods[]` with triangle counts, `collider_profile`,
`navigation_profile`, `lighting_profile`, `instancing_profile`).

| module_id | Class | Notes |
|---|---|---|
| `cozy_flower_cluster_A` | NATURE | 3 stems, colours `#f4a8c8` / `#f5c451` / `#c8a8e8`, `sway_small` 4.2 s. No collision. |
| `cozy_fence_section_A` | ARCHITECTURE | 3 posts + 2 rails. **Rails must carry collision** — the gap-walkthrough defect fixed in `WO-G8-UX-002` must not reappear in the GLB version. |
| `cozy_garden_lamp_A` | INTERACTIVE | Post `#5d6b7a`, glow `#f5d98f` core `#fdf0c8`, `pulse` 2.0 s. Post collides, glow does not. |
| `cozy_rock_small_A` | NATURE | Single boulder. Top face lighter (`#bdb5a8`) than sides (`#a8a094`) — art bible §6 technique 1. |

## Task 3 — Raise density and compose

Target **35–50 placed instances**, up from 9. This is placement work, not new
module authoring.

Composition intent — a place, not a product shelf:

- Fence sections forming an actual garden boundary, not one floating segment
- Flower clusters at wall bases and path edges, in odd-numbered groups
- Lamps along the path at irregular intervals
- Rocks scattered with varied rotation and scale, never in a line
- Path stones continuous enough to read as a path

**Vary rotation and scale per instance.** Identical transforms are what make
placement look procedural. Stagger every animation with a random 0–1.5 s delay
so nothing sways in unison — art bible §4.

Keep the build plot clear and the house, player and Companion silhouettes
unoccluded — those are P1E acceptance criteria.

## Out of scope

Wave 2 (tree/rock variants, detail pass), wave 3 (fauna and animation system),
wave 4 (toon shader). `P2E`–`P6E`. `Control-1B`. `Character-Foundry-1C`.
Approved catalog writes, World Commit. Red `F01`. `codex_directive.json`.

Do **not** promote generated GLB into `res://` or `game/assets/` — runtime load
from quarantine only. That boundary was established in `WO-P1E-002` and
verified (`GAME_GLB_COUNT=0`).

## Writer allowlist

State your complete proposed allowlist and confirm it back before touching any
file, as in `WO-P1E-002`. Expected shape:

- `E:/AIdle_Blender_Bridge_P0/libraries/environments/cozy_cyber_pixel/**`
- `E:/AIdle_Blender_Bridge_P0/config/environment_modules.yaml`
- `E:/AIdle_Blender_Bridge_P0/templates/environments/**`
- `E:/AIdle_Blender_Bridge_P0/tests/test_environment_*.py`
- Godot-side placement/composition under the existing intake path
- exclusive receipt, log, evidence

If something outside the confirmed list is needed — **stop and report.**

## Acceptance criteria

1. Exposure inside art bible §8 targets, **measured and reported numerically**.
2. Four new modules authored, registry records complete with extended fields.
3. Fence rails collide; player cannot walk between posts.
4. 35–50 instances placed, with varied rotation and scale.
5. Animations staggered — no visible synchronisation.
6. Build plot clear; house / player / Companion not occluded.
7. Quarantine boundary intact — `GAME_GLB_COUNT=0` under `game/`.
8. No regression: 44 tests, the `G8-UX` smokes, preview stages still non-solid.

## Receipt requirements

Real durable Grok child/transcript refs cross-checked against
`grok_status.json`. `accepted=false`, `self_accept=false`.

**Report measured mean luma, blown-pixel % and shadow %** — art bible §9.

**Headed visual evidence mandatory.** Density and charm are human judgements;
the entire reason this wave exists is that a human looked at a passing build and
found it disappointing.

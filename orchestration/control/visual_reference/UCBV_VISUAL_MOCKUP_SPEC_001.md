# UCBV Visual Mockup 001 — machine-readable spec

Status: `REFERENCE — vector mockup, not final art, not a dispatch`
Companion to: `UCBV_VISUAL_MOCKUP_001.html` (the actual visual sheet, SVG-based)
Prepared by: `aidle-continuity-conductor` (Claude, advisory support), 2026-07-22
For: Grok Desktop, as visual/composition reference for `UCBV-001`

Same reason `COZY_ART_BIBLE_001.md` exists: an SVG mockup is not a file an
agent can read as data, so every value that matters is transcribed here as
literal text. **Build to these values, not to a vibe.** Every hex, module id
and socket name below was copied from a real accepted file — none of it is
invented. Paths are given so you can re-verify independently rather than
trusting this transcription.

Authorization state: `UCBV-001` is `LOCKED_DIRECTION / QUEUED_AFTER_H1_HUMAN_PASS`
per `orchestration/control/UNIFIED_CHARACTER_BLOCK_VISUAL_DIRECTION_001.md` and
`orchestration/control/codex_directive.json` (directive 77). This mockup does
not authorize dispatch. It exists so the brief in step 2 of the UCBV sequencing
lock ("freeze a visual brief") has a concrete starting point once Codex opens
the gate.

---

## 1. Palette — copied from `COZY_ART_BIBLE_001.md` §2

Source: `Scene/AIdle_Blender_Environment_Scene_Blueprint_v1.0/world_profiles/COZY_ART_BIBLE_001.md`

Architecture: wall cream `#fdf3e2`, wall shade `#efe0c8`, roof terracotta `#e88b6f`,
roof shade `#d4785e`, door wood `#c98a5e`, window glass `#a8dced`,
chimney/trim `#e0d5c4`, warm light `#f5c451`.

Nature: foliage mid `#7fc98f`, foliage light `#95d9a3`/`#8ed69c`, foliage dark `#6bb87f`,
trunk `#a87d52`/`#96703f`, stem `#5aa06e`/`#4f9d6c`, blossom `#f4b8cf`/`#fbd0e0`,
fruit `#e8705c`, water `#8fd4e8`/`#a8e4f4`.

Stone & ground: rock mid `#a8a094`, rock light `#bdb5a8`, rock dark `#968e80`,
path stone `#ded4c2`/`#e8dfd0`/`#d5cab8`, farm soil `#9c7550`, furrow `#7d5c3c`.

Props: fence post `#b08560`, fence rail `#c99a72`, lamp post `#5d6b7a`,
lamp glow `#f5d98f`, lamp core `#fdf0c8`, flower pink `#f4a8c8`, yellow `#f5c451`,
purple `#c8a8e8`.

Manifestation (reserved, never on base kit): cyan primary `#3fd0e0`,
cyan highlight `#8ff0ff`.

Face: eye socket `#3d3226`, blush `#f4a09a` at ~55% opacity.

**Hard rule carried over unchanged: cyan is manifestation-only. No base-kit
character or block asset may use `#3fd0e0`/`#8ff0ff`.**

---

## 2. Character — Nori-7, `CCP-RH-001`

Source: `game_character/AIdle_Character_Foundry_MD/01_cozy_cyber_pixel/01_nori_7.md`
(record 1 of 28 in the accepted Character Foundry manifest,
`game_character/AIdle_Character_Foundry_MD/manifest.json`)

- Class `ROBOT_HELPER`. World `cozy_cyber_pixel`. Rig family
  `Biped-small-robot-01`, 8–10 main bones, nozzle and sprout as auxiliary bones.
- Silhouette: rounded teardrop body, short stable legs, head fused to body
  (no separate neck), mechanical sprout on crown, retractable watering nozzle
  in one arm, water-tank backpack.
- **Back-readable features (mandatory per Character Foundry quality gate):**
  full water tank centered on back, sprout crown visible from behind.
- Material read used in the mockup: body `#f2e9d8` (matte cream ceramic,
  slightly lighter than the art-bible wall cream so the character doesn't
  read as architecture), joints `#7fc98f` (= foliage mid, i.e. the character
  already shares a hue family with the world), eyes `#a8dced` iris on
  `#3d3226` socket with a white specular dot offset up-left, blush `#f4a09a`
  at 55% opacity — all exactly per art-bible §3 shape language.
- Proportion: **2 heads tall (chibi)**, head radius ≈ ½ body height (art
  bible §3, applied literally in the mockup's proportion-grid panel).
- 4 required readable states (Character Foundry quality gate — "idle,
  interaction, task-start, task-cancel" family, condensed here to the
  4 the mockup draws): idle/happy, active/watering, caution/needs-confirm,
  low-energy/rest. Real animation set required by the source record has
  12 entries (idle A/B, locomotion, turn, interact, react positive, react
  caution, signature, task start, task cancel, return/home, low-energy) —
  the mockup only illustrates 4 as static reference icons, not the full set.
- Animation timings reused verbatim from art bible §4, do not re-time:
  `bob` (character idle) 2.4 s, Y 0→−3→0 ease-in-out; `blink` 4.0 s,
  scaleY snap to 0.1 at 95%.
- **This is a candidate reference, not a locked decision.** Nori-7 was picked
  because it is record #1 of the cozy set and has a complete
  production-ready spec — not because Human Product Lead or Codex has chosen
  it as the permanent player-facing character. That choice is still open.

---

## 3. Architecture block kit — 9 modules

Source: `world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.1_Tier3/foundation_core/AIdle_Block_Module_Foundation_v1.0/catalogs/module_catalog.json`
(170 modules total) and `catalogs/socket_types.json` (40 socket types).

| module_id | category | socket_inputs | socket_outputs (as literally stored) | material_slots | status |
|---|---|---|---|---|---|
| `arch_foundation_square` | STRUCTURE | `vertical_stack` | `wall_edge, roof_edge, door_opening, window_opening, path_endpoint, prop_surface` | structure, trim, glass | DESIGN_READY |
| `arch_floor_square_4m` | STRUCTURE | `vertical_stack` | (same broad list) | structure, trim, glass | DESIGN_READY |
| `arch_wall_solid_4m` | STRUCTURE | `wall_edge` | (same broad list) | structure, trim, glass | DESIGN_READY |
| `arch_wall_door_4m` | STRUCTURE | `wall_edge` | (same broad list) | structure, trim, glass | DESIGN_READY |
| `arch_wall_window_4m` | STRUCTURE | `wall_edge` | (same broad list) | structure, trim, glass | DESIGN_READY |
| `arch_door_round` | STRUCTURE | `door_leaf` | (same broad list) | structure, trim, glass | DESIGN_READY |
| `arch_window_round` | STRUCTURE | `window_frame` | (same broad list) | structure, trim, glass | DESIGN_READY |
| `arch_roof_gable_4m` | STRUCTURE | `roof_edge` | (same broad list) | structure, trim, glass | DESIGN_READY |
| `cozy_fence_section_A` | PROP | n/a (not in this catalog) | n/a | — | **ACCEPTED, live in game (WO-P1E-003)**: 3 posts + 2 rails, collision on rails only |

**Known catalog gap, verified not assumed:** every STRUCTURE module above
stores the identical broad `socket_outputs` list
(`wall_edge, roof_edge, door_opening, window_opening, path_endpoint, prop_surface`)
regardless of what the module actually is — this reads as an unpopulated
per-module default rather than hand-authored data, and was already flagged
during `BLOCK-DNA-ADAPT-001` machine review. The mockup's socket-diagram
section only draws pairs independently confirmed against `socket_types.json`
compatibility lists (see §4), not the raw per-module output list.

No explicit meter dimensions exist in the JSON catalog — only the `_4m`
naming convention. Treat "4m" captions as nominal grid-unit labels, not
verified CAD dimensions, until a kit work order fixes real numbers.

---

## 4. Socket compatibility — confirmed pairs only

Source: `catalogs/socket_types.json`, read directly, `compatible_with` field.

Vertical stack chain (all confirmed):
`terrain_surface → building_foundation → vertical_stack → vertical_stack
(floor/foundation) → wall_edge (wall) → roof_edge (roof)`

Door insert (confirmed): wall's `door_opening` output is compatible with
`door_leaf` (door module's input) and `path_endpoint`. Door module declares
`socket_inputs: [door_leaf]` — this is a real, verified match.

Window insert (confirmed): wall's `window_opening` output is compatible with
`window_frame` only. Window module declares `socket_inputs: [window_frame]`
— also a real, verified match.

**Four socket relationships are declared one-directional in the source file,
even though the compatibility matrix elsewhere marks asymmetry as an error
condition.** Verified directly, not inherited from an earlier claim:

1. `terrain_surface → prop_base` (prop_base does not list terrain_surface back)
2. `building_foundation → vertical_stack` (vertical_stack only lists itself)
3. `wall_edge → window_opening` (window_opening only lists window_frame)
4. `wall_edge → door_opening` (door_opening only lists door_leaf, path_endpoint)

This is a real open item, currently owned by `BLOCK-DNA-ADAPT` scope, not
something to silently "fix" while building visual content.

---

## 5. Assembled example — `cluster_cozy_house_small_A`

Source: `module_catalog.json` (`cluster_cozy_house_small_A`, `HIGH_LEVEL`,
inputs `building_foundation, path_endpoint`) plus three already-accepted
P1E-003 props: `cozy_fence_section_A`, `cozy_garden_lamp_A` (post + glow
sphere, `pulse` 2.0 s), `cozy_flower_cluster_A` (pink/yellow/purple, 3 stems,
`sway_small` 4.2 s).

The mockup composes: rock foundation strip → cream wall row with one door
(warm-light dot at the threshold, art-bible technique 4) and two windows →
terracotta gable roof with a chimney → fence section beside the path →
garden lamp → flower cluster → a small tree → Nori-7 standing at true
relative scale near the door. This directly tests the UCBV success
condition: *"the player must look as though they belong to the same world
they construct."*

---

## 6. Manifestation staging (unchanged, reused)

Source: `COZY_ART_BIBLE_001.md` §7, verified by `WO-G8-UX-001`. Applies to
the house above while it is being built, not just to primitives.

| Stage | Visual | Collision |
|---|---|---|
| 1 Wireframe | edges only, `#3fd0e0`, dashed centre line | No |
| 2 Hologram | translucent fill 22–30%, solid edges, scan line | No |
| 3 Materializing | real material rising bottom-up, cyan above the fill line, rising sparks | No |
| 4 Complete | full warm palette, shadow, lit door/window | **Yes — only after explicit confirm + World Commit** |

---

## 7. Scope and non-authorization

- This spec and its companion HTML are a **visual brief**, step 2 of the
  UCBV sequencing lock in `UNIFIED_CHARACTER_BLOCK_VISUAL_DIRECTION_001.md`.
  They do not open the gate themselves.
- No dispatch, no product write, no acceptance is implied. `UCBV-001` remains
  `queued_not_authorized` until Human PASS on the H1 five-minute gate and a
  new monotonic Codex directive.
- Character choice (Nori-7 vs. another of the 28 records) is illustrative,
  not decided.
- Exact dimensions, full 12-entry animation sets, rig bone counts and final
  material shader setup are **not** specified here — those belong to the
  concept/turnaround production step (sequencing lock step 3), which this
  brief feeds into, not replaces.

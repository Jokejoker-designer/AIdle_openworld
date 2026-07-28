# Cozy Cyber-Pixel — Art Bible 001

Status: `REFERENCE` · Authored by: `aidle-continuity-conductor`
Approved as art direction by: Human Product Lead, 2026-07-21
Governs: P1E waves 1–4 (`WO-P1E-003` … `WO-P1E-006`)

This document is the **machine-readable form of an approved visual mockup**.
The mockup itself was rendered as SVG in the conductor session and is not a
file an agent can read, so every value that mattered has been transcribed here
as explicit numbers. **Build to these values, not to a vibe.**

Extends, does not replace, `01_COZY_CYBER_PIXEL.md`. Where they disagree, the
world profile wins and this document must be corrected.

---

## 1. Core principle

Charm comes from **expression, motion and density** — not from polygon count or
texture resolution. Reference point is the cozy social-sim look (Play Together
class), which reads as appealing at very low geometric complexity.

Consequences, and these are binding:

- **Never** add polygons where a secondary material slot would do.
- **Never** add texture detail where asymmetry would do.
- A looping 2–3 second idle animation buys more perceived life than any amount
  of static detail. Prefer motion.

---

## 2. Palette — exact values

### Architecture
| Role | Hex |
|---|---|
| Wall cream (primary) | `#fdf3e2` |
| Wall cream shade (under-eave band) | `#efe0c8` |
| Roof terracotta | `#e88b6f` |
| Roof shade (lower band) | `#d4785e` |
| Door / wood warm | `#c98a5e` |
| Window glass | `#a8dced` |
| Chimney / neutral trim | `#e0d5c4` |
| **Warm light point** | `#f5c451` |

### Nature
| Role | Hex |
|---|---|
| Foliage mid | `#7fc98f` |
| Foliage light | `#95d9a3` / `#8ed69c` |
| Foliage dark | `#6bb87f` |
| Trunk | `#a87d52`, alt `#96703f` |
| Stem / grass | `#5aa06e`, dark `#4f9d6c` |
| Blossom pink | `#f4b8cf`, light `#fbd0e0` |
| Fruit | `#e8705c` |
| Water surface | `#8fd4e8`, light `#a8e4f4` |

### Stone & ground
| Role | Hex |
|---|---|
| Rock mid | `#a8a094` |
| Rock light (top faces) | `#bdb5a8` |
| Rock dark | `#968e80` |
| Path stone | `#ded4c2` / `#e8dfd0` / `#d5cab8` |
| Farm soil | `#9c7550`, furrow `#7d5c3c` |

### Props
| Role | Hex |
|---|---|
| Fence post | `#b08560`, rail `#c99a72` |
| Lamp post | `#5d6b7a` |
| Lamp glow | `#f5d98f`, core `#fdf0c8` |
| Flower pink / yellow / purple | `#f4a8c8` / `#f5c451` / `#c8a8e8` |

### Manifestation — reserved, never used elsewhere
| Role | Hex |
|---|---|
| Cyan primary | `#3fd0e0` |
| Cyan highlight | `#8ff0ff` |

**Hard rule:** cyan is the manifestation language only. No base-kit asset may
use it. Neon stays sparse per the world profile.

---

## 3. Shape language

- Silhouettes rounded. Corner radius on every box form — no hard 90° edges.
- Character proportion **2 heads tall** (chibi). Head radius ≈ half body height.
- Eyes large, dark `#3d3226`, with a single white specular dot offset up-left.
- Blush ovals `#f4a09a` at ~55% opacity on cheeks.
- Matte everywhere. No specular highlights except water, glass, and the lamp.

---

## 4. Animation catalogue — exact durations

All loops, all ease-in-out unless stated. Timings chosen so nothing
synchronises visibly; stagger instances with a random 0–1.5 s delay offset.

| Name | Duration | Motion |
|---|---|---|
| `bob` (character idle) | 2.4 s | translate Y 0 → −3 → 0 |
| `bob_small` (robot) | 3.0 s | translate Y 0 → −1.5 → 0 |
| `blink` | 4.0 s | scaleY 1, snap to 0.1 at 95 %, back |
| `sway` (foliage) | 3.4–3.6 s | rotate −2.5° → +2.5°, origin bottom |
| `sway_small` (small plants) | 4.2 s | rotate −1.2° → +1.2° |
| `pulse` (glow) | 2.0 s | opacity 0.55 → 1 |
| `spin` (workshop gear) | 9.0 s | rotate 360°, linear |
| `steam_rise` | 2.6 s | translate Y +2 → −8, opacity 0.3 → 0 |
| `tail_flick` (cat) | 2.2 s | rotate −14° → +16°, origin tail base |
| `hop` (bird, squirrel) | 2.6 s | Y 0 held 70 %, −6 at 80 %, 0 at 90 % |
| `peck` (chicken) | 2.4 s | rotate head 0 → +26°, origin neck |
| `wing_flutter` | 0.3 s | scaleX 1 → 0.35 |
| `fly_circuit` (butterfly) | 5.0 s | 4-point loop, ±17 px X, ±7 px Y |
| `breathe` (frog) | 2.8 s | scale 1 → 1.09, origin bottom |
| `slide` (snail) | 8.0 s | translate X −6 → +8, alternate |
| `swim` (fish) | 6.0 s | X −7 → +9 with scaleX flip at turn |

---

## 5. Module inventory — target state

`✅` exists · `➕` to author

### Wave 1 — `WO-P1E-003`
| Module | Status |
|---|---|
| `cozy_flower_cluster_A` (pink/yellow/purple, 3 stems, `sway_small`) | ➕ |
| `cozy_fence_section_A` (3 posts + 2 rails, **collision on rails**) | ➕ |
| `cozy_garden_lamp_A` (post + glow sphere, `pulse`) | ➕ |
| `cozy_rock_small_A` (single boulder) | ➕ |

### Wave 2 — `WO-P1E-004`
| Module | Status |
|---|---|
| `cozy_tree_round_A` | ✅ (= `cozy_tree_landmark_A`) |
| `cozy_tree_pine_A` (3 stacked triangles) | ➕ |
| `cozy_tree_cluster_A` (3 overlapping canopies) | ➕ |
| `cozy_tree_blossom_A` (pink, falling-petal anchor) | ➕ |
| `cozy_tree_fruit_A` (3 fruit spheres) | ➕ |
| `cozy_tree_willow_A` (drooping strands, `sway_small`) | ➕ |
| `cozy_rock_mossy_A` / `_stacked_A` / `_cluster_A` / `_cracked_A` | ➕ |

### Wave 3 — `WO-P1E-005`
| Module | Animation |
|---|---|
| `fauna_cat_A` | `tail_flick` + `blink` |
| `fauna_bird_A` | `hop` + `wing_flutter` |
| `fauna_chicken_A` | `peck` |
| `fauna_butterfly_A` | `fly_circuit` + `wing_flutter` |
| `fauna_frog_A` | `breathe` |
| `fauna_snail_A` | `slide` |
| `fauna_fish_A` | `swim` (pond-bound) |
| `fauna_squirrel_A` | `hop` |

**Fauna are decorative.** No AI, no pathfinding, no navigation participation,
no collision. They are looping animations anchored to a spot.

---

## 6. Static-object detail technique

The approved mockup demonstrated a before/after at **near-identical polygon
count**. Four techniques, in priority order:

1. **Secondary material slot** — under-eave band darker than roof; rock top
   faces lighter than sides. Splits a flat form into readable planes for free.
2. **Asymmetry** — moss on one side only, offset child rock, flowers at one
   corner. Perfect symmetry reads as manufactured.
3. **Small attached props** — flower cluster at a wall base, grass in a rock
   crevice, chimney. Tens of polygons each.
4. **One warm light point** — a single `#f5c451` dot at a doorway. One dot of
   colour is what makes a building read as inhabited.

Apply in that order. Exhaust 1 and 2 before reaching for 3.

---

## 7. Manifestation staging — must read without text

The four stages currently share similar cyan box geometry (recorded G8
residual). They must become distinguishable at a glance:

| Stage | Visual | Solid? |
|---|---|---|
| 1 Wireframe | edges only, `#3fd0e0`, `pulse`, dashed centre line | **No** |
| 2 Hologram | translucent fill 22–30 %, solid edges, horizontal scan line | **No** |
| 3 Materializing | real material rising bottom-up, cyan remaining above the fill line, rising spark particles | **No** |
| 4 Complete | full warm palette, shadow, lit window, warm door light | **Yes** |

Collision activates **only at stage 4, only after explicit confirm plus World
Commit**. This invariant is already verified by `WO-G8-UX-001` — do not regress it.

---

## 8. Lighting

Current state is a defect: measured **mean luma 231/255 with 66.2 % of pixels
blown past 245 and 0 % shadow content**. That is an overcorrection of the
earlier underexposure (luma max 94).

Targets:

| Metric | Target |
|---|---|
| Mean luma | 150–185 |
| Blown pixels (> 245) | **< 3 %** |
| Shadow content (< 40) | 5–15 % |
| Key direction | high three-quarter, warm |
| Shadows | soft, present, visibly directional |

Shadow is not decoration — a fixed-angle 2.5D camera reads form through
shading. Zero shadow means zero depth.

---

## 9. Verification

Every wave must supply **headed visual evidence**, not only passing tests.
Readability, cuteness and density are judgements a test cannot make. Precedent:
43 green tests missed six real defects that a human found in ninety seconds.

Each wave receipt must additionally report measured **mean luma, blown-pixel %
and shadow %** against §8, since those are objective and cheap to check.

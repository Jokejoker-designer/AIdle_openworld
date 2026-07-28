# WO-P1E-006 — Per-style palette variants (Option B)

Authority: `PATCH_DRAFT` (Blue only) · State: `READY`
Issued by: `aidle-continuity-conductor` — **NOT Codex**
Authorized by: Human Product Lead, 2026-07-22 — chose **Option B** after the
root cause of the white pond was confirmed as art-style mismatch

Art spec: `Scene/AIdle_Blender_Environment_Scene_Blueprint_v1.0/world_profiles/COZY_ART_BIBLE_001.md`

---

## 1. Background — why this exists

The Cozy kit renders white in the Human Product Lead's game. Root cause,
confirmed from her screenshot HUD (`Art: Surrealism Canvas`) plus
`art_style_manager.gd`:

| | `cozy_cyber_pixel` | `surrealism_canvas` |
|---|---|---|
| ground | `8FBC8F` soft green | `8B7AA8` lavender |
| secondary | `7EC8E3` blue family | `9B6BCF` purple |
| neon_intensity | 0.25 | 0.45 |

Nobody rendered anything wrong. The Blender preview and the Godot evidence were
correct **for Cozy**. Her session is correct **for Surrealism**. The kit and
every hex in the art bible were authored against the Cozy palette only.

Grok's investigation established the override path: **`VisualGLB` repaints
pond, house, rock and path meshes**; GLTF materials otherwise survive intake;
the player capsule is an unstyled default mesh. Ambient additionally tints the
whole scene, and procedural fillers currently do consume the palette.

---

## 2. A taxonomy conflict that must be settled before any art is made

There are **two parallel, partially-overlapping** taxonomies in this project:

| Set | Members |
|---|---|
| **Art styles** — `game/scripts/core/constants.gd`, runtime `ArtStyleManager` | `cozy_cyber_pixel`, `surrealism_canvas`, `cyberpunk_dense`, `pastoral_fantasy`, `custom` |
| **World profiles** — `config/environment_world_profiles.yaml`, blueprint | `cozy_cyber_pixel`, `surrealism_canvas`, `tiny_diorama`, `solarpunk_haven`, `arcane_clockwork`, `spirit_valley`, `oceanpunk_abyss` |

**Only two members overlap.** `cyberpunk_dense` and `pastoral_fantasy` are not
world profiles at all — the Bridge does not recognise them. The five world
profiles with planned kits (`P2E`–`P6E`) are not art styles.

Building "a variant per style" without settling this produces work on the wrong
axis. **Do not resolve this yourself.**

### Scope decision — SETTLED by the Human Product Lead, 2026-07-22

> **The 7 world profiles are the primary axis. Art style is a future
> customisation layer. For now, map each world profile to the nearest existing
> art style and keep working.**

So the taxonomy is no longer ambiguous:

| Axis | Role |
|---|---|
| **World profile** (7) | **canonical** — content belongs to a world |
| **Art style** (4 + custom) | presentation layer, **future customisation**, not the content axis |

Consequences for this work order:

- Variants are authored **per world profile**, not per art style.
- Only **two world profiles** currently have any content: `cozy_cyber_pixel`
  (the P1E kit) and `surrealism_canvas` (what the Human Product Lead is
  actually playing). The other five — `tiny_diorama`, `solarpunk_haven`,
  `arcane_clockwork`, `spirit_valley`, `oceanpunk_abyss` — have no kit yet and
  arrive with `P2E`–`P6E`. Do not pre-author variants for worlds that have no
  content.
- `cyberpunk_dense` and `pastoral_fantasy` are art styles with **no
  corresponding world profile**. Use the nearest world profile's palette as
  their presentation until the customisation layer exists. **Do not author
  dedicated art for them.**

That makes this work order **11 modules × 2 world profiles**, not × 4 art
styles — and it means `P2E`–`P6E` each bring their own variants naturally as
their kits land, rather than this work order trying to pre-empt them.

The taxonomy reconciliation still deserves a written ADR eventually, but it is
**no longer blocking**: the Human Product Lead has stated which axis wins.

---

## 3. What to build

For each of the 11 kit modules, a palette variant per the two styles above:

`cozy_house_small_A`, `cozy_path_stone_A`, `cozy_pond_small_A`,
`cozy_tree_landmark_A`, `cozy_farm_plot_A`, `shared_light_brush_station_A`,
`cozy_greenhouse_preview_anchor_A`, `cozy_flower_cluster_A`,
`cozy_fence_section_A`, `cozy_garden_lamp_A`, `cozy_rock_small_A`.

### Reuse the mechanism that already exists

`PHYSICS_VISUAL_STATE_VARIANTS.md` and `PC_ASSET_AUTHORING_STANDARD.md` from the
DNA package already define a `STATE_VARIANTS` collection under `MOD_<id>/`, with
Godot selecting a variant deterministically from state (`wet`, `frozen`,
`restored`…). **Extend that mechanism to style rather than inventing a parallel
one.** A style variant is selected from active style exactly as a state variant
is selected from state.

If the existing mechanism genuinely cannot carry style as a selector, stop and
report rather than building a second system.

### Cozy variant is the reference

The Cozy variant is what already exists and what `COZY_ART_BIBLE_001.md`
specifies. **Do not re-author it.** Register the current materials as the
`cozy_cyber_pixel` variant.

### Surrealism variant — design intent

Per `art_style_manager.gd`, Surrealism is described as *"Dreamlike accents over
a readable ground — purple is accent, not a void field."* That description is
binding: **purple is an accent, not a wash.** The failure the Human Product Lead
photographed — everything white on lavender — is exactly what that description
warns against.

So the Surrealism variant must keep silhouettes readable and materials
distinguishable. A house must still read as a house. Water must still read as
water, even if its hue shifts toward the Surrealism palette. Apply the same
rule the art bible §8 applies to exposure: readability is not negotiable.

---

## 4. Explicitly out of scope

- `cyberpunk_dense`, `pastoral_fantasy`, `custom` — deferred pending the ADR.
- Changing the default art style, or changing which style loads.
- Deleting or editing the Human Product Lead's `world_meta.cfg`. A launcher at
  `E:/AIdle_openworld/AIdle_Chon_Lai_Art_Style.bat` renames it as a backup;
  that is the only sanctioned mechanism.
- Art programme waves 2–4 (tree/rock variants, fauna, toon shader).
- `P2E`–`P6E`, `Control-1B`, `Character-Foundry-1C`, approved catalog,
  World Commit, Red `F01`, `codex_directive.json`.
- No `res://` promotion; `GAME_GLB_COUNT` stays 0.

---

## 5. Acceptance criteria

1. All 11 modules carry a `cozy_cyber_pixel` and a `surrealism_canvas` variant.
2. The Cozy variant is byte-identical in appearance to today's verified output —
   **prove no regression**, do not re-author.
3. Switching style at runtime switches variants without reload artefacts.
4. Under Surrealism: house, player and Companion silhouettes remain readable;
   the pond still reads as water; nothing renders achromatic.
5. **HSL material check runs per style**, with per-style target values. The
   check that now catches beige/white/grey must catch a washed-out Surrealism
   variant too.
6. Headed visual evidence **for both styles**, and the receipt states which
   style each capture used — the QA rule established after tonight's
   evidence-validity defect.
7. No regression: full suite green, preview stages still non-solid, fence rails
   still collide.

---

## 6. Receipt requirements

Real durable child/transcript refs cross-checked against
`grok_status.json.completed_children`. Restore the `verdict` field, which is
still null from the last correction. `accepted=false`, `self_accept=false`.

State the taxonomy conflict in §2 as an open architectural item so it reaches
Codex, and record that `cyberpunk_dense` and `pastoral_fantasy` were
deliberately deferred rather than forgotten.

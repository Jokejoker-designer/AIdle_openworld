# U1 Unified Style Lock — UCBV-001 Character + Block Visual DNA

Status: `PATCH_DRAFT / REVIEW_REQUESTED`  
Work order: `WO-UCBV-001-UNIFIED-CHARACTER-BLOCK-VISUAL-FOUNDATION`  
Directive: `81` · **C0 amendment Directive `83` / WO-UCBV-001-STRICT-CORRECTION-002**  
Wave: `U1_STYLE_LOCK` + `C0_VISUAL_PRODUCTION_PREFLIGHT`  
Authority: `PATCH_DRAFT` (sole writer under exact lease)  
Profile: `aidle-character-style-guardian`  
Selected pair: **Nori-7 / CCP-RH-001** + first-slice construction family  
Accepted: `false` · Self-accept: `false`  
C0 artifacts: `C0_visual_production_preflight.md`, `C0_cream_reconciliation.json`

## 0. Purpose

Freeze one shared visual language so the detailed player character and the
matching construction block family read as the same world. This lock is design
and metadata truth for U2–U5. It does **not** author meshes, rigs, animations,
GLBs, runtime scripts, DNA v1.2, or Tier 3 physics.

Binding sources (do not invent new art truth):

| Source | Authority role |
|---|---|
| `COZY_ART_BIBLE_001.md` | Art-direction hex roles (Human-approved) |
| Live P1E `MAT_*` + `material_slot_mapping.contract.json` | Runtime material SSOT |
| `shared_2_5d_tokens.json` + `cozy_cyber_pixel_2_5d.json` | Dimensional / style profile tokens |
| `state_visual_variants.json` | `STATE_VARIANTS` reuse |
| Foundry `01_nori_7.md` + recipe `recipe_nori7_v1` | Character identity (no re-id) |
| Live `constants.gd` manifestation stages | 4-stage lock |
| U0 receipt `U0_ssot_preflight_001.json` | Character selection + gap decisions |

---

## 1. Silhouette family language

### Shared family name
`ucbv_cozy_rounded_readable_v1`

### Common rules (character + blocks)
- Shape language: **rounded_readable** (from shared 2.5D tokens).
- No hard 90° outer corners on primary volumes; every box form gets a soft
  corner radius so fixed three-quarter camera reads mass, not CAD edges.
- Silhouette must remain identifiable at ~10–15% screen height (Foundry gate).
- Prefer **secondary material planes + asymmetry** over polygon density
  (COZY_ART_BIBLE §1, §6).
- Character and blocks share the same edge softness / bevel scale family
  (see §2) so a Nori-7 standing beside a wall does not look like two art teams.

### Character silhouette (Nori-7 only)
- Family: teardrop robot helper — fused head/body, short stable biped legs,
  mechanical sprout crown, water-tank backpack, retractable watering nozzle.
- Proportion: **2 heads tall (chibi)**; head radius ≈ half body height.
- **Rear-view mandatory features:** sprout crown + centered water tank.
- ≤ **3** dominant palette groups (see §3).
- Eyes large, dark socket `#3d3226`, soft sky-glass iris (not manifestation cyan),
  single white specular up-left; optional blush `#f4a09a` @ ~55% opacity.
- Do not translate character joints into world-grid snap cubes.

### Block family silhouette
- Soft modular architecture kit; readable massing at H1 viewports
  `1280×720` and `868×517`.
- Outer corners share character-compatible bevel density.
- Openings (door / window) cut as clear negative space with thicker soft frames
  — never hairline UI strokes as mesh.
- Fence / prop keep chunky posts and rails so they read beside Nori-7 legs.

### Bound family module roles (first slice)
Role names are production contracts for U3. Catalog `module_id` values are
**bound only when already present** in accepted catalogs / runtime allowlists.
U1 does **not** invent recipes or new module IDs.

| Role | Preferred accepted id (if present) | Notes |
|---|---|---|
| foundation | `arch_foundation_square` (DNA catalog) | Structure base |
| floor | `arch_floor_square_4m` / runtime `arch_floor_round_4m` | U3 picks one accepted id |
| wall | `arch_wall_solid_4m` | Solid wall mass |
| corner | *select from accepted STRUCTURE catalog at U3* | No silent invent |
| door | `arch_door_round` (+ wall opening `arch_wall_door_4m`) | Leaf + opening pair |
| window | `arch_window_round` / runtime `arch_window_frame_simple` | Frame + opening pair |
| roof | `arch_roof_gable_4m` / runtime `arch_roof_dome_4m` | U3 picks one accepted id |
| fence | `cozy_fence_section_A` (live P1E) | Posts + rails |
| prop | runtime e.g. `prop_bench_simple` / `prop_crate_small` / `prop_lamp_post` | One prop only |

Nine construction roles above form the first-slice kit. U0’s “ten-module”
wording includes the shared material/state-variant package as the family
envelope, not a tenth invented mesh.

---

## 2. Edge / bevel density and surface detail

| Parameter | Lock value |
|---|---|
| Edge profile | Soft continuous bevel; no razor 90° |
| Bevel relative scale | ~3–6% of local primary face length on architecture; slightly higher readable roundness on Nori-7 body |
| Surface detail density | Calm foreground; max local density ≤ `0.55` (shared tokens) |
| Material surface | Matte tactile everywhere |
| Specular exception | Water, glass, warm lamp only |
| Metal budget | ≤ 0.15 of readable surface on character / kit (cozy profile) |
| Detail priority | (1) secondary material slot planes → (2) asymmetry → (3) tiny attached props → (4) one warm light point |

Forbidden: photoreal micro-noise, dense neon soup, hard chrome industrial edges,
thin unreadable limbs or frames.

---

## 3. Value hierarchy (readable planes)

Order from lightest to deepest on a lit three-quarter view:

1. **Warm emissive / lamp core** — habitation cue (`#f5c451` family).
2. **Top faces / light planes** — e.g. rock tops `#bdb5a8`, wall cream `#fdf3e2`.
3. **Primary mid** — main body / wall / leaf mid.
4. **Shade bands** — under-eave `#efe0c8`, roof shade `#d4785e`.
5. **Structure / ground darks** — trunk, soil furrow, soft directional shadow.

Lighting targets (COZY_ART_BIBLE §8) remain binding for evidence waves:

| Metric | Target |
|---|---|
| Mean luma | 150–185 |
| Blown pixels (>245) | < 3% |
| Shadow content (<40) | 5–15% |
| Key | High three-quarter, warm |
| Shadows | Soft, present, directional |

Character body cream may sit **slightly lighter than architecture wall cream**
so Nori-7 does not read as a wall piece — art direction target still roots in
bible cream role, not DNA `#F7E9C6` as SSOT.

---

## 4. Canonical palette (art truth → runtime)

### 4.1 Art-direction SSOT
`Scene/.../COZY_ART_BIBLE_001.md` §2 hex roles are the **canonical art truth**
for UCBV production color callouts.

### 4.2 Runtime SSOT
Semantic slots resolve **only** to live P1E `MAT_*` IDs via
`material_slot_mapping.contract.json`. No parallel palette system.

### 4.3 DNA theme non-authority
`mat_cozy_cream_leaf_v1` (`#F7E9C6` / `#78B65B`) is a **non-authoritative
recipe design alias** only. Do not ship it as a third palette or rewrite DNA.

### 4.3b C0 cozy-cream reconciliation (Directive 83 — explicit)

Both definitions are documented; production picks **one** canonical art SSOT:

| Source | Cream | Leaf | Status after C0 |
|---|---|---|---|
| COZY_ART_BIBLE | `#fdf3e2` (+ `#efe0c8` shade) | `#7fc98f` | **CANONICAL production art** |
| DNA `mat_cozy_cream_leaf_v1` | `#F7E9C6` | `#78B65B` | **NON_AUTHORITATIVE_ALIAS_ONLY** |

Rationale: bible already Human-approved and live for P1E architecture; character
must match the world kit; DNA rewrite is out of scope; nearly-white uncanny is
fixed by multi-value cream + darker joints/face, not by switching to DNA cream.
Machine table: `C0_cream_reconciliation.json`.

**Nearly-white rule:** forbid pure white / flat near-white monochrome body.
Require shade bands, leaf joints/panels, dark sockets, wood secondary planes.
Cyan remains manifestation-only and restrained.

### 4.4 Three palette groups for Nori-7 + kit family
| Group | Role | Bible hex anchors | Runtime MAT_* |
|---|---|---|---|
| G1 Warm cream ceramic | Body / walls / chimney trim | `#fdf3e2`, `#efe0c8`, `#e0d5c4` | `MAT_CozyCeramic`, shade via structure/stone warm |
| G2 Leaf / life green | Joints, sprout, foliage cues | `#7fc98f`, `#6bb87f`, `#95d9a3` | `MAT_CozyLeaf`, `MAT_CozyStem` |
| G3 Warm wood + soft sky-glass | Wood frames, door, glass, eye iris | `#c98a5e`, `#a8dced`, roof `#e88b6f` | `MAT_CozyWood`, `MAT_CozyDoor`, `MAT_CozyGlass`, `MAT_CozyRoof` |

**Reserved (not a body group):** manifestation cyan `#3fd0e0` / `#8ff0ff` —
never on base-kit character or complete architecture materials.

Full alias table: `unified_palette_material_alias_table.json`.

---

## 5. Shared material vocabulary

Slots are named for **both** character surfaces and the nine-module block family.
Every production mesh must declare slots from this vocabulary; runtime maps
slots → `MAT_*` only.

| Shared vocabulary slot | Character use (Nori-7) | Block family use | Semantic slot → MAT_* |
|---|---|---|---|
| `body` | Ceramic shell / primary mass | Foundation / wall primary plane | `body` → `MAT_CozyCeramic` |
| `cloth` | Soft strap / pad accents (if any); no fabric sim | Soft trim ribbons / non-structural pads | maps via `trim`/`accent` → `MAT_CozyWood` / `MAT_CozyFlowerPink` |
| `wood` | Tank strap bands, tool grip | Door frames, fence rails, roof trim wood | `wood` → `MAT_CozyWood` |
| `stone` | Foot pads / weight base | Foundation edges, path contact | `stone` / `structure` → `MAT_CozyStone` / `MAT_CozyStoneWarm` |
| `metal` | Joint rings, nozzle metal (budgeted) | Hinge accents, lamp post metal | `metal` → `MAT_CozyMetal` |
| `glass` | Eye lens / interface lens | Window panes | `glass` → `MAT_CozyGlass` |
| `emissive` | Soft UI blink on face only (non-cyan) | Lamp glow, warm door light | `emission` → `MAT_CozyLampWarm` |
| `interactive_highlight` | Selection / focus outline (shape+icon+label) | Preview / selected / invalid markers | uses outline + opacity + stage chrome; preview glass may use `MAT_CozyGlassPreview` / `MAT_CozyPreviewMarker` — **not color alone** |
| `leaf` | Sprout, joint green | Planter prop foliage accents | `leaf` → `MAT_CozyLeaf` |
| `roof` | n/a on character | Roof modules | `roof` → `MAT_CozyRoof` (+ shade `MAT_CozyRoofShade`) |
| `door` | n/a on character | Door leaf | `door` → `MAT_CozyDoor` |

Character recipe slot `body` with DNA theme id is remapped through the alias
table; production authors call out bible hex + MAT_*, never DNA hex as truth.

---

## 6. Modular ID policy

1. **Identity lock:** Character id remains `CCP-RH-001` / display `Nori-7`.
   Root module `char_nori7_base`. Attachments only from recipe:
   `attach_water_tank_small`, `attach_watering_nozzle_A`, `attach_mechanical_sprout_A`.
2. **No invented recipes** for the other 26 Foundry records; no silent Bác Bắp.
3. **Block modules** use accepted Block-DNA / runtime allowlist ids only.
   Family **roles** (foundation…prop) are stable; concrete `module_id` chosen
   in U3 from accepted catalogs.
4. **Provenance fields** required on every authored asset package:
   `asset_id`, `character_id` or `module_role`, `world_profile_id=cozy_cyber_pixel`,
   `style_lock_id=ucbv_001_style_lock_v1`, `source_hashes`, `author_wave`.
5. **Material slots** must be named from §5 vocabulary / existing semantic slots.
6. **Sockets:** Character uses skeleton attachment sockets; blocks use
   pair-compatible world sockets. Never mix semantics.
7. **IDs are lowercase snake / existing catalog spelling** — do not rename live
   `MAT_*` or accepted module ids.

---

## 7. LOD policy

Aligned with shared token budgets and Scene LOD notes; first-slice production
must ship LOD names even if intermediate LODs share simplified geometry.

| LOD | Character (Nori-7) | Block module |
|---|---|---|
| LOD0 | Full readable detail: sprout, tank, nozzle, eye highlight | Full bevels, secondary material planes, openings |
| LOD1 | Soften small joints; keep silhouette + rear sprout/tank | Keep massing + primary openings; drop micro props |
| LOD2 / billboard | Silhouette-readable teardrop + sprout tip | Box/wedge mass + roof pitch; fence as slab posts |

Budget soft caps (shared tokens):

- Starter part triangles: ≤ **96** soft cap per modular part
- Starter entity: ≤ **1200** soft cap for full character assembly
- Architecture module: prefer calm density; exhaust material-plane technique
  before raising poly count

Interactive objects (door leaf, character) must **not** be permanently fused into
HLOD clusters that remove interaction affordances.

---

## 8. STATE_VARIANTS reuse

Do **not** invent a parallel style-variant system.

| Mechanism | Path | UCBV rule |
|---|---|---|
| World profile variants | `game/resources/world_profiles/state_visual_variants.json` | `cozy_cyber_pixel` = identity_register (no recolor of verified MAT_*); `surrealism_canvas` may apply material_table on same MAT_* ids |
| Build interaction states | P2E / Block Assembly | `preview`, `valid`, `invalid`, `selected`, `materializing`, `complete` |
| Character readable states (visual) | Foundry quality gate | At minimum: idle/happy, active/build, caution/needs-confirm, low-energy/rest — full anim set owned by U4 |

State encoding **must** combine non-color signals (see §10): stage label, opacity,
outline weight/pattern, icon. Color may reinforce, never sole critical cue.

---

## 9. Manifestation stages (locked to live 4)

**Authoritative chain** (live game + COZY_ART_BIBLE §7 + shared tokens):

1. `wireframe`
2. `hologram`
3. `materializing`
4. `complete`

| Stage | Visual lock | Solid / collision |
|---|---|---|
| wireframe | Edges only, cyan primary `#3fd0e0`, pulse, dashed centre line | No |
| hologram | Translucent fill 22–30%, solid edges, horizontal scan line | No |
| materializing | Real material rises bottom-up; cyan remains above fill line; rising sparks | No |
| complete | Full warm palette, soft shadow, warm light allowed | **Yes** — only after explicit confirm + World Commit |

**Non-authoritative:** DNA package 5-stage list including `COMMITTING` is
package drift. Product must not introduce a fifth stage.

Cyan remains **manifestation language only**.

Duration language: shared tokens manifestation range **8–15 s** full chain;
reduced-motion may collapse motion while preserving stage order and labels.

---

## 10. Accessibility

| Requirement | Lock |
|---|---|
| Contrast | Cream/leaf/wood on soft ground must keep readable silhouette edges; dark eye socket `#3d3226` on cream for face features |
| Color-only ban | Critical states (invalid, selected, manifestation stage, confirm needed) always carry outline / pattern / icon / text label |
| Reduced motion | Honor `reduced_motion_supported`; replace continuous pulse/scan with static stage chrome + opacity steps |
| Dual resolution | Readable at `1280×720` and `868×517` without diagnostic walls, overlap, or clipped chrome |
| Focus / selection | Interactive highlight uses thickness + dashed/solid pattern + optional icon, not hue alone |
| Companion text | Text-only Companion; no identity swap; no emotional pressure for world mutation |

---

## 11. First-pair binding — Nori-7 + block family

### Character
| Field | Value |
|---|---|
| display_name | Nori-7 |
| character_id | CCP-RH-001 |
| world_profile_id | cozy_cyber_pixel |
| class | ROBOT_HELPER |
| recipe_id | recipe_nori7_v1 |
| root_module_id | char_nori7_base |
| skeleton_id (label) | skel_small_biped_robot_v1 |
| animation_set_id | anim_robot_gardener_v1 |
| style_lock_id | ucbv_001_style_lock_v1 |
| material theme alias | mat_cozy_cream_leaf_v1 → **non-authoritative**; use bible + MAT_* |

### Shared visual DNA tokens
Published machine token pack:
`game/resources/art_styles/tokens/ucbv_001_shared_character_block_tokens.json`

### Explicit non-bindings
- Not Bác Bắp / CCP-NW-003 (unresolved rig mapping).
- Not full 28-character wave.
- Not DNA v1.2 / Tier 3 activation.
- Not P2E-002.

---

## 12. Forbidden patterns (style lock)

- Photoreal beside toy low-poly
- Dense neon soup / manifestation cyan on complete base kit
- Instant pop-in (must use 4-stage manifestation for world modules)
- Free 3D camera MVP language in art briefs
- Neural mesh as world truth
- Palette-as-only state signal
- More than three dominant color families on Nori-7
- Hard 90° architecture without soft corner language
- Invented recipes, silent Bác Bắp rig resolve, shared skeleton placeholder as production bone truth
- Flat nearly-white / pure-white body without shade + joint + face contrast (C0)
- DNA `#F7E9C6` as production cream paint SSOT (C0)
- Treating Tier3 `anim_robot_gardener_v1` empty clips as keyed animation payload (C0)

---

## 13. Handoff

| Next wave | Duty |
|---|---|
| U2–U8 | Historical first-slice (immutable receipts under non-correction_002) |
| **C0** | Visual/production preflight + cream reconciliation + anim intent (**this amendment**) |
| **C1** | Real offline GLB skinned mesh/rig + keyed Layer A/B actions via Blender Bridge (no install) |
| C2 | Godot intake, 28-module selector, InputMap Q/R/elevation, delete World Commit path |
| C3–C5 | Red / QA evidence / Purple non-accepting gate |

Companion files in this lease:

- `unified_palette_material_alias_table.json`
- `DESIGN.md` (Open Design nine-section)
- `design-contract.md`
- `implementation-handoff.md` → routes to **C1**
- `C0_visual_production_preflight.md`
- `C0_cream_reconciliation.json`
- `game/resources/art_styles/tokens/ucbv_001_shared_character_block_tokens.json` (U1; not rewritten in C0 lease)

---

## 14. Quality gate for U1 (this wave) + C0 amendment

- [x] Silhouette family language locked
- [x] Edge/bevel + value hierarchy locked
- [x] Modular ID + LOD + STATE_VARIANTS reuse locked
- [x] Canonical palette = COZY_ART_BIBLE; MAT_* runtime map; DNA alias documented
- [x] **C0:** both cream hexes documented; canonical pick + nearly-white remediation
- [x] Shared material vocabulary for character + block family
- [x] Manifestation locked to live 4 stages
- [x] Accessibility constraints explicit
- [x] Nori-7 + nine module roles bound with shared DNA tokens
- [x] **C0:** animation contract intent locked (Tier3 names only + UCBV extension)
- [x] **C0:** fail-closed production checklist published (mesh/skin/rig/anim/catalog/controls/delete/evidence)
- [x] No meshes/GLBs authored in U1/C0 design waves
- [x] No Bác Bắp / invented recipes / DNA v1.2 / Tier 3

# U2 Character Visual Silhouette — Nori-7 / CCP-RH-001

Status: `PATCH_DRAFT / REVIEW_REQUESTED`  
Work order: `WO-UCBV-001-UNIFIED-CHARACTER-BLOCK-VISUAL-FOUNDATION`  
Directive: `81`  
Wave: `U2_VISUAL_SILHOUETTE`  
Authority: `PATCH_DRAFT` (sole writer under exact lease)  
Profile: `aidle-character-visual-silhouette`  
Identity lock: **Nori-7 / CCP-RH-001** only  
Style lock consumed: `ucbv_001_style_lock_v1`  
Accepted: `false` · Self-accept: `false`

## 0. Purpose

Freeze a production-ready **visual silhouette package** for Nori-7 so concept art,
SVG sheets, and later U4 mesh/rig can share one readable 2.5D turnaround language.
This wave does **not** author production mesh, skeleton hierarchy, animation clips,
or GLBs (U4). It does **not** author block modules (U3).

### Binding sources (do not re-id or invent)

| Source | Role |
|---|---|
| U1 `U1_unified_style_lock.md` + tokens | Visual DNA freeze |
| Foundry `01_nori_7.md` | Identity + silhouette narrative |
| Recipe `recipe_nori7_v1` | Root + three attachments only |
| COZY_ART_BIBLE hex roles | Art color truth |
| Live `MAT_*` via material_slot_mapping | Runtime materials |
| U0 select + U1 bind | Character locked; not re-selected |

---

## 1. Identity and silhouette family

| Field | Value |
|---|---|
| display_name | Nori-7 |
| character_id | CCP-RH-001 |
| world_profile_id | cozy_cyber_pixel |
| class | ROBOT_HELPER |
| recipe_id | recipe_nori7_v1 |
| root_module_id | char_nori7_base |
| attachments | `attach_water_tank_small`, `attach_watering_nozzle_A`, `attach_mechanical_sprout_A` |
| silhouette_family | `ucbv_cozy_rounded_readable_v1` |
| shape language | rounded_readable teardrop robot helper |
| proportion | **2 heads tall (chibi)** |
| style_lock_id | ucbv_001_style_lock_v1 |
| skeleton label (not production bones) | skel_small_biped_robot_v1 |
| animation set id (U4 owns clips) | anim_robot_gardener_v1 |

### Core silhouette (black-mass readable)

1. **Primary mass:** rounded teardrop ceramic body; head fused to torso (no neck).
2. **Stance:** two short stable biped legs; wide soft foot pads.
3. **Crown:** mechanical sprout growing from head apex (tallest point).
4. **Rear:** centered water-tank backpack (mandatory rear cue).
5. **Tool:** retractable watering nozzle on one arm (default stowed along forearm).

### Mandatory rear-view features

At pure back view and at LOD2 silhouette, at least:

- Mechanical sprout tip / leaf pair above crown
- Water tank oval bulk centered on back

Without these, the package **fails** Foundry quality gate and U1 lock.

### Dominant palette groups (≤3)

1. **G1 Warm cream ceramic** — body shell (`#fdf3e2` / `#efe0c8` → `MAT_CozyCeramic`)
2. **G2 Leaf / life green** — joints + sprout (`#7fc98f` → `MAT_CozyLeaf`)
3. **G3 Warm wood + sky-glass** — tank straps / wood bands + eye iris (`#c98a5e`, `#a8dced`)

**Forbidden on complete base kit:** manifestation cyan `#3fd0e0` / `#8ff0ff`.  
**DNA theme `mat_cozy_cream_leaf_v1` / `#F7E9C6`:** non-authoritative alias only — do not paint from DNA hex.  
**C0 reconciliation:** bible cream is canonical; DNA cream documented only; multi-value body + darker joints required against nearly-white uncanny (see `../style_lock/C0_cream_reconciliation.json`).

---

## 2. Silhouette sheet description

### Sheet layout (concept / SVG)

Single horizontal turnaround sheet, left → right:

| Panel | View | Purpose |
|---|---|---|
| A | Front | Face, eyes, leg split, stowed nozzle silhouette |
| B | Three-quarter (key game cam) | Primary readability under fixed 2.5D camera |
| C | Side (profile) | Teardrop depth, tank depth, sprout lean, leg thickness |
| D | Back | Sprout + tank mandatory proof |
| E | Black-mass row | Same four views filled solid black (no color dependence) |
| F | Proportion grid overlay | 2-head units on front + side |

Camera for panels A–D: orthographic design elevation (not free orbit).  
Game composition proof uses **fixed three-quarter** matching panel B, not free 3D.

### Black-mass test (pass criteria)

At ~10–15% of viewport height, black silhouette alone must remain distinct from:

1. **Mây Mạch** (CCP-NS-002) — humanoid with twin cloud buns + oversized mail satchel
2. **Bác Bắp** (CCP-NW-003) — stocky humanoid, corn-leaf moustache, hip tool box (**not produced here**)
3. **Bụi Mơ** (CCP-CT-004) — quadruped cat-bush with three back leaves + branch tail

Nori-7 differentiators in pure mass: **single fused teardrop + short biped + crown sprout + rear tank**, not humanoid shoulders, not quadruped, not satchel.

---

## 3. Front / side / back / three-quarter turnaround specs

Units: **Head Units (HU)**. 1 HU = head vertical span of the fused upper bulb.  
Total standing height crown-of-body (without sprout) = **2.0 HU**.  
Sprout tip reaches ≈ **2.35–2.45 HU** from ground.

### 3.1 Front view

| Element | Spec |
|---|---|
| Outer contour | Soft teardrop / inverted egg; max width ~1.05 HU at upper third; tapers to pelvis ~0.55 HU |
| Face plane | Slight forward disc on upper mass; no hard nose |
| Eyes | Two large ovals; outer corners soft; sockets dark `#3d3226`; iris sky-glass `#a8dced`; single white specular **up-left** on each |
| Eye size | Each eye height ~0.22 HU; spacing between inner corners ~0.12 HU |
| Blush | Optional soft `#f4a09a` @ 55% under outer eye — never primary ID |
| Sprout | Centered at apex; stem thin-to-medium; 1–2 leaf lobes; leaves read as soft diamond/teardrop, not needles |
| Arms | Short stub arms or sleeve-integrated; elbows not thin sticks |
| Nozzle (stowed) | Right forearm silhouette slightly thicker; nozzle tip may peek as small rounded barrel |
| Legs | Two short cylinders; gap between feet ~0.12 HU; foot pads wider than ankles |
| Ground contact | Flat soft pads; no toe separation required |

**Front fail conditions:** thin limbs, separate neck, human jaw, >3 color families, cyan body glow.

### 3.2 Side (right profile)

| Element | Spec |
|---|---|
| Body depth | ~0.85–0.95 HU at thickest (upper); rear tank adds ~0.35–0.40 HU behind back plane |
| Teardrop lean | Slight forward bias of face plane (~5–8°), rear bulk of tank balances |
| Legs | Forward of center mass slightly for stable chibi plant; knee break minimal (soft bend only) |
| Sprout | Leans very slightly back or vertical; must clear tank in side view |
| Nozzle | Along forearm; when stowed, almost flush; when active (action pose only) extends ~0.4–0.55 HU forward-down |
| Arms | Elbow near mid-body height |

**Side fail conditions:** tank missing, flat cardboard body, industrial backpack slab with hard 90° corners.

### 3.3 Back view

| Element | Spec |
|---|---|
| Primary mass | Same teardrop width as front; no face detail |
| Water tank | Centered oval/capsule; height ~0.55–0.65 HU; width ~0.50–0.60 HU; sits mid-back |
| Tank straps | Two soft wood-tone bands (material slot `wood`) arcing over shoulders — readable as secondary planes |
| Tank cap / fill gauge | One small top nub or soft window — optional; not required for silhouette ID |
| Sprout | Fully visible above crown; leaves slightly asymmetric OK |
| Legs | Same short biped; heel pads visible |

**Back fail conditions:** no tank, no sprout, human backpack straps only, rear feature smaller than LOD2 budget.

### 3.4 Three-quarter (key 2.5D game camera)

| Element | Spec |
|---|---|
| Camera | Fixed high three-quarter, warm key from upper-left of frame |
| Mass read | Teardrop body + one visible eye pair (or 1.5 eyes), sprout, partial tank arc, one leg pair |
| Asymmetry | Prefer slight arm pose offset; nozzle side must be guessable |
| Edge language | Soft continuous bevel; higher roundness than architecture walls |
| Value | Cream body slightly **lighter** than wall cream so character ≠ wall segment |

This is the **primary production pose** for readability proofs at `1280×720` and `868×517`.

---

## 4. Neutral vs action pose

### Neutral (idle sheet default)

- Feet planted shoulder-width (short legs: almost under hips)
- Arms relaxed; nozzle stowed
- Sprout upright; slight micro-lean allowed in motion notes only
- Face: soft open eyes, optional micro blush
- Tank full silhouette readable from ¾ and back

### Action (build / water cue — still silhouette, not U4 clip)

- Weight shift to one foot (still stable)
- Nozzle extended on tool arm toward ground/plant plane
- Sprout tip may tilt ~10–15° toward look target
- Eyes slightly more open or scanning (iris still sky-glass, **not** cyan)
- Tank remains locked to back — never detached in base kit

---

## 5. Signature props and sockets (recipe-bound)

| Instance | module_id | Socket (from recipe) | Silhouette duty |
|---|---|---|---|
| root | `char_nori7_base` | — | Teardrop primary mass |
| tank | `attach_water_tank_small` | root `character_back` → `back_attachment` | Rear ID + volume |
| nozzle | `attach_watering_nozzle_A` | root `character_hand` → `tool_grip` | Tool arm mass / action cue |
| sprout | `attach_mechanical_sprout_A` | root `character_head` → `head_attachment` | Crown ID + rear tip |

No additional attachments in U2. No outfit wardrobe system beyond strap/pad accents on slots.

---

## 6. Material callouts (aligned to U1 vocabulary)

See also `modular_body_outfit_definition.json` and visual package maps.

| Region | Shared slot | Bible hex role | Runtime MAT_* |
|---|---|---|---|
| Ceramic shell / primary body | `body` | cream `#fdf3e2` / shade `#efe0c8` | `MAT_CozyCeramic` |
| Joint rings, limb bands | `leaf` | foliage mid `#7fc98f` | `MAT_CozyLeaf` |
| Sprout stem + leaves | `leaf` | foliage mid / light | `MAT_CozyLeaf` (+ stem `MAT_CozyStem` optional) |
| Tank strap bands | `wood` | wood `#c98a5e` | `MAT_CozyWood` |
| Tank shell | `body` or secondary plane on tank mesh | cream shade | `MAT_CozyCeramic` |
| Soft pad accents | `cloth` | wood/trim or pink accent | `MAT_CozyWood` / `MAT_CozyFlowerPink` |
| Foot pads / weight base | `stone` | warm stone | `MAT_CozyStone` / `MAT_CozyStoneWarm` |
| Nozzle metal tip | `metal` | metal accent ≤15% surface | `MAT_CozyMetal` |
| Eye lens | `glass` | sky glass `#a8dced` | `MAT_CozyGlass` |
| Soft face UI blink (non-cyan) | `emissive` | warm lamp family only if used | `MAT_CozyLampWarm` |
| Selection / focus | `interactive_highlight` | outline+opacity+icon — not hue alone | `MAT_CozyPreviewMarker` / glass preview |

Metal budget: ≤ **0.15** of readable surface. Matte tactile everywhere except water/glass/lamp exceptions.

---

## 7. LOD silhouette targets

| LOD | Keep | Drop |
|---|---|---|
| LOD0 | Full sprout leaves, tank straps, nozzle tip, eye specular | — |
| LOD1 | Body mass, sprout silhouette, tank bulk, eye sockets | Small joint rings, strap stitches |
| LOD2 / billboard | Teardrop + sprout tip (+ tank blob if rear-facing billboard) | Face detail, nozzle separation |

Triangle soft caps (from U1 tokens): part ≤96, full entity ≤1200 — guidance for U4, not authored here.

---

## 8. Five-dimension difference (nearest roster)

| Dimension | Nori-7 | Mây Mạch | Bác Bắp | Bụi Mơ |
|---|---|---|---|---|
| Species/form | Teardrop robot | Small humanoid courier | Stocky humanoid mechanic | Cat-bush quadruped |
| Silhouette family | Fused head-body teardrop | Cloud twin-buns + coat | Boxy torso + corn moustache | Round cat + three back leaves |
| Signature prop | Water tank + nozzle + sprout | Oversized mail satchel | Hip modular toolbox | Branch tail / seed cache |
| Movement type | Short biped robot step | Quick biped walk | Slow stocky biped | Quadruped pad |
| Material family | Cream ceramic + leaf joints | Cloth coat + circuit stitch | Faded orange coveralls + dull metal | Soft fur-leaf hybrid |

Black-mass: Nori-7 cannot be mistaken for humanoid shoulders or quadruped limbs.

---

## 9. Explicit non-scope

- No Bác Bắp production package
- No invented recipes / other 26 Foundry records
- No block family meshes (U3)
- No production skeleton hierarchy or animation timing table (U4)
- No GLB / Godot scene integration (U5)
- No DNA v1.2 / Tier 3 / P2E-002
- No World Commit authority on character

---

## 10. Quality gate (U2)

- [x] Silhouette sheet + F/S/B/¾ written under style lock
- [x] Proportion guide 2-heads-tall with rear feature callout
- [x] Modular body/outfit slots → U1 vocabulary + MAT_*
- [x] Idle + build interaction readability notes @ 1280×720 / 868×517
- [x] SVG / structured sheets under lease (image optional)
- [x] Bible cream/leaf as paint truth; DNA hex alias only
- [x] ≤3 palette groups; cyan not on complete body
- [x] No mesh/rig/GLB; no block assets
- [x] Identity remains CCP-RH-001 / Nori-7

---

## 11. Companion files

| Path | Role |
|---|---|
| `proportion_guide.md` | Numeric HU grid + scale vs architecture |
| `modular_body_outfit_definition.json` | Modules + material slots machine map |
| `visual_states_readability.md` | Idle / build dual-res notes |
| `DESIGN.md` | OD nine-section character visual direction |
| `design-contract.md` | Keep/change/do-not-copy + gate |
| `implementation-handoff.md` | U3 / U4 operational handoff |
| `sheets/nori7_silhouette_turnaround.svg` | Black + line turnaround |
| `sheets/nori7_proportion_grid.svg` | 2-head grid |
| `game_character/ucbv_001/nori7/visual_package/**` | Package copy + visual_spec |

Next wave: **U3** block family art under Block-DNA contracts (nine roles).

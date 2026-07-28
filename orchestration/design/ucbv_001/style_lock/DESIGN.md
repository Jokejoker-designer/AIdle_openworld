# DESIGN.md — UCBV-001 Unified Character + Block Style

Product: AIdle Openworld first detailed character + matching construction kit  
World profile: `cozy_cyber_pixel`  
Style lock id: `ucbv_001_style_lock_v1`  
Wave: U1 · Directive 81 · **C0 amendment Directive 83 / WO-UCBV-001-STRICT-CORRECTION-002**  
Character binding: Nori-7 / `CCP-RH-001`  
C0 preflight: `C0_visual_production_preflight.md` · cream table: `C0_cream_reconciliation.json`

## 1. Visual Theme & Atmosphere

Warm cozy cyber-pixel 2.5D: rounded low-poly masses, matte handmade materials,
gentle tech, farming-community life. Charm comes from expression, motion, and
readable density — not polygon count. Fixed three-quarter camera; silhouette
priority over texture resolution. Character and architecture share one soft
edge language so the player looks like they belong to the world they build.

Mood: calm, inhabited, sun-warm, restrained cyber accents (neon_intensity ≤ 0.25).
Not industrial hard-surface, not photoreal, not dense cyberpunk.

## 2. Color

### Authority (C0 explicit cream reconciliation)
| Definition | Cream | Leaf | Production status |
|---|---|---|---|
| COZY_ART_BIBLE `wall_cream` / `foliage_mid` | `#fdf3e2` (+ shade `#efe0c8`) | `#7fc98f` | **CANONICAL art SSOT** |
| DNA `mat_cozy_cream_leaf_v1` | `#F7E9C6` | `#78B65B` | **NON_AUTHORITATIVE_ALIAS_ONLY** — document remap; do not paint as SSOT |

- Art truth hex roles: `COZY_ART_BIBLE_001.md` §2 (canonical for production).
- Runtime materials: live P1E `MAT_*` via semantic slots only.
- Full decision record: `C0_cream_reconciliation.json`.
- Do **not** invent a third blended cream.

### Three dominant groups (character + kit)
1. **Warm cream ceramic** — `#fdf3e2` / `#efe0c8` → `MAT_CozyCeramic`
2. **Leaf life green** — `#7fc98f` family → `MAT_CozyLeaf`
3. **Warm wood + sky-glass + terracotta roof** — `#c98a5e`, `#a8dced`, `#e88b6f` → `MAT_CozyWood` / `MAT_CozyGlass` / `MAT_CozyRoof`

### Nearly-white uncanny remediation (C0 / Human playtest)
Body must **not** ship as a flat near-white fill. Required multi-value treatment:
lit cream + shade bands + darker leaf joints/panels + dark face sockets + wood
secondary planes. Forbidden: pure white `#FFFFFF`, monochrome near-white body,
cyan as base-body accent.

### Reserved
Manifestation cyan `#3fd0e0` / `#8ff0ff` — restrained **manifestation chrome
only**; never on complete base-kit body or architecture materials.

### Face
Eye socket `#3d3226`; blush `#f4a09a` @ 55%; white specular up-left; iris
sky-glass `#a8dced` (not cyan).

### Value
Top faces lightest; under-eave/shade bands darker; soft directional shadows
required (mean luma 150–185; blown <3%; shadow 5–15%).

## 3. Typography

In-world assets are non-text. UI/Companion remains product shell typography.
Style lock does not introduce a new type system. Stage and state labels in
chrome must remain machine-readable strings from live constants
(`wireframe`, `hologram`, `materializing`, `complete`).

## 4. Spacing & Grid

- World construction: grid / elevation / rotation with pair-compatible sockets.
- Character: skeleton space only — **no** world-grid snap on joints.
- Nominal architecture labeling may use `_4m` catalog names as grid-unit
  labels until U3 measures accepted bounds.
- Soft corner radius ~3–6% of local primary face on architecture; higher
  readable roundness on Nori-7 primary mass.
- H1 dual viewports must remain uncluttered: no overlapping chrome walls.

## 5. Layout & Composition

- Camera: fixed three-quarter; free orbit forbidden for MVP language.
- Readability: character + block kit must compose in one frame during build
  select → preview → confirm.
- Rear-view features mandatory for Nori-7 (sprout + tank).
- Secondary material planes before extra props; one warm light point makes
  buildings feel inhabited.
- Asymmetry preferred over perfect manufactured symmetry.

## 6. Components

### Character components (Nori-7)
- Root body `char_nori7_base` (teardrop ceramic)
- Attachments: water tank, watering nozzle, mechanical sprout
- Material slots from shared vocabulary: body, wood, metal, glass, leaf, emissive, interactive_highlight

### Block family roles (9)
foundation, floor, wall, corner, door, window, roof, fence, prop  
— concrete `module_id` chosen in U3 from accepted catalogs only.

### Shared material vocabulary
body, cloth, wood, stone, metal, glass, emissive, interactive_highlight
(+ leaf, roof, door as extended semantic slots already in Block-DNA).

### State components
preview / valid / invalid / selected / materializing / complete  
encoded with outline, opacity, icon, stage label — not color alone.

## 7. Motion & Interaction

- Manifestation stages (locked 4): wireframe → hologram → materializing → complete.
- Collision only at `complete` after confirm + World Commit.
- Prop/creature loop timings from art bible remain reference for ambient motion
  (`bob` 2.4s, `bob_small` 3.0s for robot, `blink` 4.0s, `pulse` 2.0s).
- Character production clips: C0 locks intent from
  `UCBV_ANIMATION_BLOCK_INTEGRATION_MAP_001.md` — Tier3
  `anim_robot_gardener_v1` = **names/compatibility only**; C1 authors **real
  keyed GLB actions** for Layer A (`idle`,`walk`,`scan`,`happy`,`cancel`, …)
  plus UCBV build extension (`turn_left`,`turn_right`,`build_place`,
  `build_place_hold`,`confirm`). Markers never mutate World Commit.
- U4 timing table remains duration reference; C1 adapter records evidenced
  durations. No pelvis-bob-only / idle-alias placeholders for missing required
  clips in the Directive 83 correction target.
- Easing: ease-in-out; reduced-motion supported (static stage chrome allowed).
- Manifestation full-chain duration language: 8–15 seconds.

## 8. Voice & Brand

- World brand: Cozy Cyber-Pixel / Dreamy Low-Poly.
- Nori-7 voice (for later animation posing): short, clear, slightly perfectionist
  gardener helper; always asks before mutating care schedules.
- No emotional coercion for World Commit.
- Text-only Companion system remains separate; Nori-7 is not AIda unless a
  future Human decision says so.

## 9. Anti-patterns

- Photoreal materials beside toy low-poly
- Dense neon soup; cyan on complete base kit
- Instant pop-in of world modules
- Free 3D camera MVP framing in art
- Neural/generated mesh as world truth
- Color-only critical state
- >3 dominant color families on the character
- Hard CAD 90° edges without soft bevel family
- Invented recipes / silent Bác Bắp rig mapping
- DNA 5-stage `COMMITTING` manifestation
- Parallel style-variant system outside `STATE_VARIANTS` + MAT_*
- Shared skeleton placeholder bones treated as production hierarchy
- Flat nearly-white / pure-white body without shade + joint contrast
- Treating DNA `#F7E9C6` cream as production paint SSOT
- Claiming Tier3 catalog clips are animated payload without keyed GLB tracks
- AI-slop: generic purple gradients, noisy cyberpunk armor, unreadable thin limbs

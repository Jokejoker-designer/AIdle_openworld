# DESIGN.md — UCBV-001 Nori-7 Character Visual Package

Product: AIdle Openworld first detailed character visual silhouette  
World profile: `cozy_cyber_pixel`  
Style lock id: `ucbv_001_style_lock_v1`  
Wave: U2 · Directive 81 · **C0 amendment Directive 83 / WO-UCBV-001-STRICT-CORRECTION-002**  
Character binding: Nori-7 / `CCP-RH-001`  
C0 locks: `../style_lock/C0_cream_reconciliation.json`, `C0_animation_contract_lock.md`

## 1. Visual Theme & Atmosphere

Warm cozy cyber-pixel 2.5D helper robot: rounded low-poly teardrop ceramic,
matte handmade materials, gentle tech, garden-companion presence. Charm comes
from silhouette, eyes, and sprout status — not polygon density or neon armor.

Fixed three-quarter camera. Character must look like it belongs beside the
U3 construction kit that shares the same soft edge language
(`ucbv_cozy_rounded_readable_v1`).

Mood: calm, devoted gardener, slightly perfectionist, sun-warm.  
Not industrial hard-surface, not photoreal, not dense cyberpunk, not anime clone.

## 2. Color

### Authority (C0 cream reconciliation)
| Source | Cream | Leaf | Status |
|---|---|---|---|
| COZY_ART_BIBLE | `#fdf3e2` (+ `#efe0c8`) | `#7fc98f` | **CANONICAL production** |
| DNA `mat_cozy_cream_leaf_v1` | `#F7E9C6` | `#78B65B` | **NON_AUTHORITATIVE_ALIAS_ONLY** |

- Runtime: live `MAT_*` via semantic slots only.
- Full table: `../style_lock/C0_cream_reconciliation.json`.

### Three dominant groups
1. **Warm cream ceramic** — `#fdf3e2` / `#efe0c8` → `MAT_CozyCeramic` (body slightly lighter than wall cream **but not flat white**)
2. **Leaf life green** — `#7fc98f` → `MAT_CozyLeaf` (joints + sprout — **must read darker than body**)
3. **Warm wood + sky-glass** — `#c98a5e`, `#a8dced` → `MAT_CozyWood` / `MAT_CozyGlass`

### Nearly-white uncanny remediation
Require multi-value shell (lit + shade), readable leaf joints/panels, dark face
sockets, wood secondary planes. Forbid pure white / monochrome near-white body.

### Face
Eye socket `#3d3226`; iris sky-glass `#a8dced`; blush `#f4a09a` @ 55%; white specular up-left.

### Reserved
Manifestation cyan `#3fd0e0` / `#8ff0ff` — restrained manifestation chrome only;
never on complete character body materials.

## 3. Typography

Character is non-text. Stage/state chrome uses live machine strings only
(`wireframe`, `hologram`, `materializing`, `complete`, plus build states).
Companion remains separate text-only product shell. No new type system in U2.

## 4. Spacing & Grid

- Proportion: **2 heads tall**; HU grid in `proportion_guide.md`.
- Character lives in skeleton space — **no** world-grid snap on joints.
- Soft roundness higher on primary body mass than architecture bevels (3–6% faces).
- Dual viewports `1280×720` and `868×517` must keep sprout/tank inside safe margins.

## 5. Layout & Composition

- Primary game-read pose: fixed high three-quarter.
- Turnaround sheet: front / ¾ / side / back + black-mass row + proportion overlay.
- Rear-view mandatory: sprout crown + centered water tank.
- Secondary material planes (straps, joint rings) before extra props.
- Asymmetry OK (nozzle side, leaf lean); avoid manufactured bilateral perfection.

## 6. Components

### Body modules (recipe-locked)
- `char_nori7_base` — teardrop ceramic shell
- `attach_water_tank_small` — rear tank
- `attach_watering_nozzle_A` — tool
- `attach_mechanical_sprout_A` — crown status

### Material slots (U1 shared vocabulary)
body, cloth, wood, stone, metal, glass, emissive, interactive_highlight, leaf  
(mapped to MAT_* in `modular_body_outfit_definition.json`)

### State components
idle_happy, active_build, caution_needs_confirm, low_energy_rest  
World build: preview / valid / invalid / selected / materializing / complete  
— always with outline / opacity / icon / label, not color alone.

## 7. Motion & Interaction

- Manifestation on world modules only: wireframe → hologram → materializing → complete.
- Character does not become cyan during build.
- Ambient reference loops (bob, blink, sprout sway) from art bible.
- **C0 animation lock:** Tier3 `anim_robot_gardener_v1` = names/compatibility only.
  C1 authors real keyed GLB actions (Layer A: idle/walk/scan/happy/cancel + optional
  gardener; Layer B UCBV extension: turn_left/right, build_place, build_place_hold,
  confirm). Exact 14-bone hierarchy. Markers never mutate World Commit.
  See `C0_animation_contract_lock.md` + integration map.
- Easing: ease-in-out; reduced-motion → static stage chrome, preserve order.
- Nozzle stowed in idle; extended in active_build / water cue.

## 8. Voice & Brand

- World brand: Cozy Cyber-Pixel / Dreamy Low-Poly.
- Nori-7: short, clear, slightly perfectionist gardener helper; asks before care-schedule mutation.
- No emotional pressure for World Commit.
- Nori-7 is not AIda unless Human decides later.

## 9. Anti-patterns

- Photoreal ceramic / skin next to toy low-poly world
- Dense neon soup; cyan complete-body materials
- Thin unreadable limbs or hairline nozzle
- Missing rear tank or sprout
- >3 dominant color families
- DNA hex as paint SSOT
- Adult fashion proportions
- Free 3D orbit MVP framing
- Invented attachments / Bác Bắp package / other Foundry IDs
- Production mesh/GLB claimed complete in U2/C0 design-only waves
- Color-only invalid/selected/confirm states
- Parallel style-variant system outside STATE_VARIANTS + MAT_*
- Flat nearly-white / pure-white body; DNA cream as paint SSOT
- Empty Tier3 clips treated as real animation; idle aliases for missing required actions
- AI-slop: generic purple glow, noisy cyber armor, blank featureless blob face

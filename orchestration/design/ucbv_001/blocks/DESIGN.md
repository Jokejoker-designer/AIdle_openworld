# DESIGN.md — UCBV-001 U3 Cozy Architecture Block Family

Status: `PATCH_DRAFT / REVIEW_REQUESTED`  
Family: `ucbv_001_cozy_architecture_kit_v1`  
Style lock: `ucbv_001_style_lock_v1`  
Pair: Nori-7 / CCP-RH-001

## 1. Visual Theme & Atmosphere

Warm cozy rounded-readable modular architecture that belongs beside Nori-7’s
teardrop ceramic helper. Soft continuous bevels (3–6% of primary face), matte
tactile surfaces, fixed three-quarter camera, calm secondary planes instead of
polygon noise. Construction cyan is reserved for manifestation stages only.

## 2. Color

Three palette groups from U1 / COZY_ART_BIBLE → live `MAT_*`:

| Group | Hex anchors | MAT_* |
|---|---|---|
| G1 cream ceramic | `#fdf3e2`, `#efe0c8` | `MAT_CozyCeramic`, `MAT_CozyStoneWarm` |
| G2 leaf life | `#7fc98f` | `MAT_CozyLeaf` (prop accent; character joints) |
| G3 wood / glass / roof | `#c98a5e`, `#a8dced`, `#e88b6f` | Wood, glass, door, roof, fence mats |

Manifestation cyan `#3fd0e0` / `#8ff0ff` never on complete base kit.
DNA `mat_cozy_cream_leaf_v1` hex is non-authoritative alias only.
World profile `cozy_cyber_pixel` uses STATE_VARIANTS identity register (no recolor).

## 3. Typography

Kit sheet labels: UI sans for roles, monospace for `module_id`. In-world blocks
carry no body typography; stage labels are chrome only (wireframe / hologram /
materializing / complete + build interaction labels).

## 4. Spacing & Grid

| Token | Value | Source |
|---|---|---|
| snap_m | 0.5 | catalog_allowlists.grid |
| elevation_snap_m | 0.25 | catalog_allowlists.grid |
| rotation_snap_deg | 15 | catalog_allowlists.grid |
| primary span | 4.0 m | `*_4m` architecture modules |
| wall height | 2.8 m | cozy house placeholder scale |
| fence post min width | 0.12–0.14 m | readable next to Nori legs |

## 5. Layout & Composition

Kit sheet: 5×2 cells at 1280×720 proof; secondary proof 868×517. Modules read as
mass first, openings second, trim third. Belonging test: Nori-7 beside cream wall
+ fence post + crate without style clash.

## 6. Components

Ten allowlisted modules (roles → ids):

1. foundation → `block_platform`
2. floor → `arch_floor_round_4m`
3. wall → `block_panel`
4. corner → `block_cube_round`
5. door → `arch_door_round`
6. window → `arch_window_frame_simple`
7. roof → `arch_roof_dome_4m`
8. fence → `block_beam`
9. prop → `prop_crate_small`
10. wall_door → `arch_wall_door_4m`

Sockets and polarities reused from Block-DNA socket catalog + adapter
normalizations; no invented grammar. Godot mesh descriptors under
`game/assets/ucbv_001/blocks/mesh_descriptors/`.

## 7. Motion & Interaction

Live four-stage manifestation: wireframe → hologram → materializing → complete.
Build interaction states: preview, valid, invalid, selected, materializing,
complete. Collision only at complete after confirm + World Commit. Reduced motion:
static stage chrome, same order. Critical state never color-only (outline + icon
+ label + pattern).

## 8. Voice & Brand

Toy-readable cozy cyber pixel — friendly, soft, habitation-forward. Not neon
soup, not photoreal CAD, not hard industrial chrome. Metal ≤ 15% surface.
Wall cream slightly separates from Nori body value so the robot is not a wall
piece.

## 9. Anti-patterns

- Invented `module_id` or recipes
- Using U1 preferred ids outside adapter allowlist without remapping note
- DNA cream/leaf theme as art SSOT
- Manifestation cyan on complete architecture
- Parallel STATE_VARIANTS system
- Tier3 physics invention in U3
- Hard 90° outer corners on primary volumes
- Hairline door/window frames
- Character mesh/rig (U4) or runtime script patch (U5)
- Self-accept / grandchildren

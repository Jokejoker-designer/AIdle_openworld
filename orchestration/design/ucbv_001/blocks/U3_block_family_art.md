# U3 Block Family Art — Matching Ten-Module Kit

Wave: `U3_BLOCK_FAMILY_ART` · Directive 81 · WO-UCBV-001  
Profile: `aidle-worldgen-asset-art` · Authority: `PATCH_DRAFT`  
`accepted=false` · `self_accept=false` · no grandchildren

## Binding chain

| Wave | Ref | Deliverable |
|---|---|---|
| Parent | `019f7ffd-3995-71c0-aca1-51078e24a852` | Coordinator |
| U0 | `019f8a9c-e24f-7571-b057-186550c97383` | Nori-7 selected |
| U1 | `019f8aa1-a648-7ed2-84d9-46d982d79e7a` | Style lock + tokens |
| U2 | `019f8aa8-4de9-7f02-97f7-b61f28cdb3b8` | Nori silhouette |
| U3 | `019f8ab1-24d7-7d90-8018-2f4051361c41` | This kit |

## Module selection (allowlist only)

U1 preferred some DNA ids that are **not** on the adapter allowlist. U3 remaps:

| Role | U1 preferred (if present) | U3 selected (allowlisted) | Rationale |
|---|---|---|---|
| foundation | arch_foundation_square | **block_platform** | preferred not allowlisted |
| floor | arch_floor_round_4m | **arch_floor_round_4m** | match |
| wall | arch_wall_solid_4m | **block_panel** | preferred not allowlisted |
| corner | (empty) | **block_cube_round** | rounded corner pier |
| door | arch_door_round | **arch_door_round** | match |
| window | arch_window_frame_simple | **arch_window_frame_simple** | match |
| roof | arch_roof_dome_4m | **arch_roof_dome_4m** | match |
| fence | cozy_fence_section_A | **block_beam** | pilot id only |
| prop | prop_crate_small | **prop_crate_small** | match |
| wall_door (10th) | arch_wall_door_4m | **arch_wall_door_4m** | U0 ten-module |

## Deliverables map

Product lease `game/assets/ucbv_001/blocks/**`:

- `family_manifest.json` — package authority
- `modules/*.json` — per-module bounds, sockets, materials, silhouette
- `mesh_descriptors/*.meshdesc.json` — Godot-ready offline descriptors
- `visual_states.json` — manifestation + build interaction
- `material_bindings.json` — U1 vocabulary + MAT_* + STATE_VARIANTS
- `physics_residuals.json` — Tier3 unbound
- `kit_sheet/` — SVG kit sheet + index
- `provenance.json`

Design lease `orchestration/design/ucbv_001/blocks/**`:

- `DESIGN.md`, `design-contract.md`, `implementation-handoff.md`
- `U3_block_family_art.md` (this file)
- `sheets/module_kit_sheet.svg` (mirror)

## Visual state summary

Manifestation (live 4): wireframe → hologram → materializing → complete.  
Build: preview / valid / invalid / selected / materializing / complete.  
Non-color signals required for critical validity. Cyan never on complete kit.

## Physics residual

No Tier3 bindings invented. DNA collision_policy labels are authoring hints only.

## Out of scope

Character mesh (U4). Runtime patch outside assets (U5). DNA rewrite. GLB export
(no bridge run). Invented module ids / recipes / sockets.

## Next

`next_owner = U4_CHARACTER_MESH_RIG`

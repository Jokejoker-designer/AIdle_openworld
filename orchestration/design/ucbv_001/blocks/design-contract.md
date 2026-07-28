# Design contract — UCBV-001 U3 Block Family Art

## Goal and target artifact

**Goal:** Author the ten-module construction family that matches Nori-7 / U1 style
lock, using only accepted Block-DNA adapter allowlist `module_id`s, with
production-ready art definitions and Godot mesh descriptors for U5.

**Target artifacts:**

| Artifact | Path |
|---|---|
| Family manifest | `game/assets/ucbv_001/blocks/family_manifest.json` |
| Module defs (10) | `game/assets/ucbv_001/blocks/modules/*.json` |
| Mesh descriptors (10) | `game/assets/ucbv_001/blocks/mesh_descriptors/*.meshdesc.json` |
| Visual states | `game/assets/ucbv_001/blocks/visual_states.json` |
| Material bindings | `game/assets/ucbv_001/blocks/material_bindings.json` |
| Physics residuals | `game/assets/ucbv_001/blocks/physics_residuals.json` |
| Kit sheet | `game/assets/ucbv_001/blocks/kit_sheet/**` |
| Design package | `orchestration/design/ucbv_001/blocks/**` |

**Audience:** U4 character mesh/rig, U5 Godot integration, Red/Purple reviewers.

**Not in scope:** character mesh/rig, runtime scripts/scenes, DNA rewrite, Tier3
bindings, GLB (no offline bridge export this wave), P2E-002, invented ids.

## Evidence table

| Evidence | Confidence | Use |
|---|---|---|
| U1 style lock + tokens | observed | Silhouette, palette, manifestation, LOD |
| U2 Nori visual package | observed | Belonging / wall value separation |
| catalog_allowlists.json | observed | Accepted module_id SSOT |
| socket_catalog.contract.json | observed | Socket reuse only |
| material_slot_mapping.contract.json | observed | MAT_* SSOT |
| state_visual_variants.json | observed | Reuse, no parallel system |
| DNA module_catalog.json | observed | Sockets/materials for DNA-present ids |
| Block-DNA fixtures VALID-05/06/07/14 | observed | Socket pairing examples |
| cozy_house placeholders | observed | Scale reference only |

## Keep / Change / Do not copy

| Reference | Keep | Change | Do not copy |
|---|---|---|---|
| U1 preferred id table | Role names + policy | Remap ids not on allowlist | Invent missing preferred ids into allowlist |
| DNA arch_foundation_square / wall_solid | Awareness | Use block_platform / block_panel | Ship non-allowlisted ids |
| cozy_fence_section_A pilot | Fence material MAT_* | Geometry via block_beam | Treat pilot map as DNA allowlist |
| cozy_house recipe placeholders | Dimensions vibe | Bind to catalog module_ids | Placeholder ids as production module_ids |
| Tier3 physics | Residual documentation | — | Fake bindings |

## Final design stance

One soft modular architecture kit on allowlisted ids only, sharing
`ucbv_cozy_rounded_readable_v1` with Nori-7. Remap foundation/wall/fence where
U1 preferred ids are outside the adapter allowlist; document residuals; never
invent grammar or Tier3 physics.

## Risks and unknowns

| Risk | Impact | Mitigation |
|---|---|---|
| Primitives only expose snap_grid | Weak assembly sockets | Prefer arch_* modules for openings; residual noted |
| arch_window_frame_simple / props not in DNA full catalog | Authorship gap | Fixtures + allowlist authority; document |
| No GLB | U5 uses descriptors | Explicit meshdesc format |
| Bounds are art descriptors not DNA meters fields | Scale drift | 4m naming + grid + house scale; U5 may refine |

## Quality gate checklist (P0)

- [x] Ten modules, allowlisted ids only
- [x] Roles: foundation, floor, wall, corner, door, window, roof, fence, prop + wall_door
- [x] Visual states aligned to live 4-stage manifestation + build states
- [x] Materials from U1 vocabulary + MAT_* + STATE_VARIANTS reuse
- [x] Kit sheet + per-module bounds/socket refs
- [x] Mesh descriptors offline-safe
- [x] Physics unbound residual documented
- [x] No character mesh; no runtime patch
- [x] accepted=false; self_accept=false

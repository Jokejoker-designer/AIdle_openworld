# AIdle Town Build — 10 Phase Mockup-Parity System

## Mục tiêu

Dựng **thị trấn Cozy** từ mockup SSOT V2 theo **10 phase**, mỗi phase:

- **1 nhân vật** (animation thật, clip contract)
- **1 building**
- **3 vật thể**

**Khóa:** bám mockup **100%** (`MOCKUP_PARITY_100`) — chưa đạt thì **không được dừng / không claim complete**.

## Nguồn sự thật

| Layer | Path |
|-------|------|
| Visual SSOT | `../visual_reference/mockup_ssot_v2/MOCKUP_SSOT_V2.html` |
| Design lock | `../visual_reference/mockup_ssot_v2/MOCKUP_DESIGN_LOCK.md` |
| Town layout | `town/TOWN_LAYOUT_10PHASE.json` |
| Phases | `phases/PHASE_01.md` … `PHASE_10.md` |
| Parity gate | `contracts/mockup_parity_100.schema.json` |

## Subagents

| # | Agent | Authority |
|---|-------|-----------|
| 01 | Town Orchestrator | HUMAN_APPROVAL_REQUIRED |
| 02 | Mockup Parity Guardian | READ_ONLY_AUDIT |
| 03 | Character Animation Designer | PATCH_DRAFT |
| 04 | Building Module Designer | PATCH_DRAFT |
| 05 | Prop Set Designer | PATCH_DRAFT |
| 06 | Town Layout Planner | PATCH_DRAFT (layout only) |
| 07 | Godot Runtime Integrator | PATCH_DRAFT |
| 08 | Red Mockup Delta Reviewer | READ_ONLY_AUDIT |
| 09 | Purple Parity Gate | VERIFY_ONLY |
| 10 | Town QA Playability | VERIFY_ONLY |

Aligns with TrustLayer x16 + MAF (`E:\standards\maf\COMPLIANCE.md`).

## Workflow

`READY → CLAIMED → IN_PROGRESS → REVIEW_REQUESTED → PARITY_100_VERIFIED → HUMAN_ACCEPT`

Phase N+1 **BLOCKED** until phase N is `PARITY_100_VERIFIED` (or Human waived in writing).

## Town order (not inventory dump)

1 home_plot → 2 market_square → 3 workshop_row → 4 creature_garden → 5 pollinator_farm  
→ 6 water_edge → 7 craft_landmark → 8 barn_yard → 9 spirit_bridge → 10 canopy_lookout

## Runtime

Godot: `game/scripts/modules/town/town_layout_loader.gd` + resource  
`game/resources/town/town_layout_10phase.json`

## Honesty

- `accepted=false` / `self_accept=false` until Human Product Lead
- Missing production GLB for a slot = phase **FAIL** parity (no fake pass)
- Presentation spawn ≠ World Commit ownership

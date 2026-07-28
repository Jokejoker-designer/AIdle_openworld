# MASTER PLAN — Cozy Starter Town 10 Phase

**Status:** `SYSTEM_ACTIVE_PHASE1_READY`  
**Mockup:** MOCKUP_SSOT_V2  
**Gate:** MOCKUP_PARITY_100  

## Phase table

| Ph | District | Character | Building | Props (3) |
|---:|---|---|---|---|
| 1 | `home_plot` | Nori-7 (`CCP-RH-001`) | `cozy_house_small_A` | `cozy_path_stone_A`, `cozy_garden_lamp_A`, `cozy_mailbox_A` |
| 2 | `market_square` | Mây Mạch (`CCP-NS-002`) | `cozy_market_stall_A` | `cozy_bench_A`, `cozy_cart_A`, `cozy_signpost_A` |
| 3 | `workshop_row` | Bác Bắp (`CCP-NW-003`) | `cozy_workshop_A` | `cozy_tool_rack_A`, `cozy_crate_small_A`, `cozy_barrel_A` |
| 4 | `creature_garden` | Bụi Mơ (`CCP-CT-004`) | `cozy_gazebo_A` | `cozy_flower_cluster_A`, `cozy_flower_bed_B`, `cozy_bush_round_A` |
| 5 | `pollinator_farm` | Kito Thụ Phấn (`SPH-RH-011`) | `cozy_greenhouse_A` | `cozy_farm_plot_A`, `cozy_crop_row_A`, `cozy_scarecrow_A` |
| 6 | `water_edge` | Nereu-5 (`OA-RG-021`) | `cozy_well_house_A` | `cozy_pond_small_A`, `cozy_water_pump_A`, `cozy_birdbath_A` |
| 7 | `craft_landmark` | Cinder-04 (`AC-CO-015`) | `cozy_windmill_A` | `cozy_fence_section_A`, `cozy_grass_tuft_A`, `cozy_rock_cluster_A` |
| 8 | `barn_yard` | Patch Gấu Nút (`TD-CT-028`) | `cozy_barn_small_A` | `cozy_tree_fruit_A`, `cozy_rock_small_A`, `cozy_rock_stacked_A` |
| 9 | `spirit_bridge` | Trúc Nhi (`SV-NW-019`) | `cozy_bridge_arch_A` | `cozy_tree_willow_A`, `cozy_tree_blossom_A`, `cozy_rock_mossy_A` |
| 10 | `canopy_lookout` | Luma Tán Lá (`SPH-NG-009`) | `cozy_watchtower_A` | `cozy_tree_landmark_A`, `cozy_tree_pine_A`, `cozy_tree_cluster_A` |

## Execution rule

Không chuyển phase khi phase trước chưa `PARITY_100_VERIFIED`.  
Không claim market-ready / ship khi Human chưa ACCEPT.

## Next action

Run **Phase 01 home_plot** subagent pipeline against existing Nori + house assets; fill gaps until parity 100.

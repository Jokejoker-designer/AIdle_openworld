# UCBV Visual Mockup 002 — machine-readable spec (skeleton / element / location pass)

Status: `REFERENCE — vector mockup, not final art, not a dispatch`
Companion to: `UCBV_VISUAL_MOCKUP_002.html`
Extends: `UCBV_VISUAL_MOCKUP_001.html` + `UCBV_VISUAL_MOCKUP_SPEC_001.md` (read those first — palette,
Nori-7 full turnaround, 9-block architecture kit, socket-compatibility diagram)
Prepared by: `aidle-continuity-conductor` (Claude, advisory support), 2026-07-22
For: Grok Desktop, as visual/composition reference for `UCBV-001`

Same rule as before: every id, number and file path below was read directly from a real accepted file
in `world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.1_Tier3`. Two confidence levels are used
throughout and must not be conflated:

- **RECIPE-CONFIRMED** — a real JSON recipe file already specifies this exact combination.
- **PROPOSED MAPPING** — no recipe file exists yet; this document illustrates one reasonable pairing
  from the accepted catalogs. Nobody has decided this is correct.

---

## 1. Skeleton foundation — 14 families

Source: `foundation_core/AIdle_Block_Module_Foundation_v1.0/catalogs/skeleton_families.json`

| skeleton_id | Name | Locomotion | Bone target | Compatible animation sets |
|---|---|---|---|---|
| `skel_small_biped_robot_v1` | Small Biped Robot | BIPED | 14 | anim_small_biped_core_v1, anim_robot_gardener_v1 |
| `skel_stylized_humanoid_v1` | Stylized Humanoid | BIPED | 42 | anim_humanoid_social_v1, anim_humanoid_farming_v1 |
| `skel_modular_golem_v1` | Modular Golem | BIPED_HEAVY | 22 | anim_golem_heavy_v1, anim_builder_heavy_v1 |
| `skel_small_quadruped_v1` | Small Quadruped | QUADRUPED | 28 | anim_small_quadruped_pet_v1, anim_small_quadruped_work_v1 |
| `skel_large_quadruped_v1` | Large Quadruped | QUADRUPED_HEAVY | 34 | anim_large_quadruped_v1 |
| `skel_bird_origami_v1` | Bird / Origami | FLYING | 18 | anim_bird_origami_v1, anim_paper_flutter_v1 |
| `skel_flying_spirit_v1` | Flying Spirit | FLOATING | 16 | anim_spirit_float_v1 |
| `skel_fish_swimmer_v1` | Fish / Ray | SWIMMING | 20 | anim_fish_swim_v1, anim_ray_glide_v1 |
| `skel_serpentine_v1` | Serpentine | SERPENTINE | 28 | anim_serpentine_v1 |
| `skel_blob_v1` | Blob | DEFORM | 10 | anim_blob_v1 |
| `skel_wheeled_robot_v1` | Wheeled Robot | WHEELED | 12 | anim_wheeled_robot_v1 |
| `skel_tentacle_creature_v1` | Tentacle Creature | TENTACLE | 36 | anim_tentacle_creature_v1 |
| `skel_building_mechanism_v1` | Building Mechanism | STATIC_MECHANISM | 24 | anim_building_mechanism_v1 |
| `skel_plant_growth_v1` | Plant Growth | GROWTH | 20 | anim_plant_growth_v1 |
| `skel_vehicle_small_v1` | Small Vehicle | VEHICLE | 18 | anim_vehicle_small_v1 |

**Verified gap:** all families store the identical placeholder `required_bones: [root, body, head]` and
the identical 4-entry `attachment_sockets` list (`character_hand`, `character_back`, `character_head`,
`vfx_anchor`). No full bone hierarchy is authored anywhere in this package yet. Only locomotion type,
bone count target and animation-set names are individualized per family.

Full clip lists for every animation set referenced above are in
`foundation_core/AIdle_Block_Module_Foundation_v1.0/catalogs/animation_library.json` (21 sets total;
none of the 21 include per-clip duration/timing data — only clip ids, loop flags and an empty events array).

---

## 2. Character base + attachment modules

Source: `module_catalog.json`, categories `BASE` (12) and `PART` (16).

Character bases (each already links its own skeleton_id + default animation_set_id — this part of the
catalog is individualized, unlike the STRUCTURE modules flagged in spec 001):

`char_nori7_base`→skel_small_biped_robot_v1, `char_stylized_human_base`→skel_stylized_humanoid_v1,
`char_golem_base`→skel_modular_golem_v1, `char_small_quadruped_base`→skel_small_quadruped_v1,
`char_large_quadruped_base`→skel_large_quadruped_v1, `char_origami_bird_base`→skel_bird_origami_v1,
`char_spirit_float_base`→skel_flying_spirit_v1, `char_fish_base`→skel_fish_swimmer_v1,
`char_serpentine_base`→skel_serpentine_v1, `char_blob_base`→skel_blob_v1,
`char_wheeled_robot_base`→skel_wheeled_robot_v1, `char_tentacle_base`→skel_tentacle_creature_v1.

Attachment parts (all `category: PART`, no skeleton/animation of their own, socket into a character):
`attach_water_tank_small`, `attach_watering_nozzle_A`, `attach_mechanical_sprout_A`,
`attach_tool_hammer_small`, `attach_tool_scanner`, `attach_backpack_green`, `attach_hat_farmer`,
`attach_rune_core`, `attach_spirit_lantern`, `attach_biolume_fin`, `attach_wing_leaf_pair`,
`attach_horn_crystal_pair`, `attach_tail_paper`, `attach_tool_fishing_rod`, `attach_tool_seed_bag`,
`attach_saddle_small`.

---

## 3. Four characters — full mapping

### Nori-7 — `CCP-RH-001` — RECIPE-CONFIRMED
Source: `examples/01_nori7_character_recipe.json`
- Skeleton: `skel_small_biped_robot_v1` (14 bones, BIPED)
- Animation: `anim_robot_gardener_v1` — idle, walk, scan, water, plant_seed, harvest, charge, happy, low_energy, cancel
- Attachments: `attach_water_tank_small`→character_back, `attach_watering_nozzle_A`→character_hand, `attach_mechanical_sprout_A`→character_head
- Material: `mat_cozy_cream_leaf_v1`, body override `#F7E9C6`
- Behavior: `behavior_companion_helper_v1`

### Bụi Mơ — `CCP-CT-004` — RECIPE-CONFIRMED
Source: `examples/02_bui_mo_character_recipe.json`
- Skeleton: `skel_small_quadruped_v1` (28 bones, QUADRUPED)
- Animation: `anim_small_quadruped_pet_v1` — idle, walk, run, sniff, sit, sleep_loop, happy, pet_reaction, curl
- Attachments: `nature_bush_round`→character_back/plant_root, scale 0.45; root recipe scale 0.75
- Material: `mat_cozy_cream_leaf_v1`, body override `#9CBF75`
- Behavior: `behavior_pettable_v1`

### Mây Mạch — `CCP-NS-002` — PROPOSED MAPPING
Character Foundry text: *"Humanoid-small-01; túi đeo có xương phụ; tóc búi là mesh cứng"* — no literal
catalog id named this; no recipe file exists.
- Proposed skeleton: `skel_stylized_humanoid_v1` (42 bones, BIPED) — closest catalog match
- Proposed animation: `anim_humanoid_social_v1` — idle, walk, run, wave, talk_A, talk_B, sit, stand, give_item, receive_item, celebrate (fits "giao thư, kết nối cư dân")
- Proposed attachment: `attach_backpack_green`→character_back
- **Open gap:** no PART matches "tóc búi mesh cứng" (rigid hair-bun) — not in the catalog yet
- Material: no recipe; this sheet proposes `mat_cozy_cream_leaf_v1` with the sky accent `#87CFF0`

### Bác Bắp — `CCP-NW-003` — PROPOSED MAPPING, genuinely open
Character Foundry text: *"Humanoid-stocky-01; găng cơ khí có 3 khớp phụ"* — "stocky" also has no literal
catalog id. Two real candidates, not resolved here:
- (a) `skel_stylized_humanoid_v1`, 42 bones — humanoid but not stocky; animation `anim_humanoid_farming_v1` (hoe, plant_seed, water, harvest, carry, repair, sleep_loop)
- (b) `skel_modular_golem_v1`, 22 bones, BIPED_HEAVY, mechanical/clockwork — thematically closer to "găng cơ khí"; animation `anim_builder_heavy_v1` (dig, hammer, lift, carry, place_module, repair, cancel) — **arguably the better fit** for "sửa máy, nâng cấp robot, dạy chế tạo"
- Proposed attachment either way: `attach_tool_hammer_small`→character_hand

---

## 4. Elemental blocks — physics foundation

Source: `catalogs/element_catalog.json` (34 elements, 6 classes), `catalogs/physical_property_profiles.json`
(16 profiles), `catalogs/module_physics_bindings.json` (170 modules, 81 bound / 89 null).

| Class | Elements |
|---|---|
| MATTER (17) | EARTH, SOIL, STONE, SAND, CLAY, WOOD, METAL, GLASS, CRYSTAL, WATER, ICE, STEAM, AIR, CLOUD, ASH, MUD, OIL |
| ENERGY_STATE (1) | FIRE |
| BIOLOGICAL (2) | PLANT, CORAL |
| ENERGY (10) | HEAT, COLD, ELECTRICITY, LIGHT, KINETIC, SOLAR, SOUND, ARCANE, SPIRIT, BIOLUMINESCENCE |
| FORCE (3) | WIND, PRESSURE, GRAVITY |
| WORLD_RULE (1) | VOID |

Sample physical property profiles (0–1 scale traits):

| profile_id | element | flammability | structural_strength | water_resistance | buoyancy |
|---|---|---|---|---|---|
| `phys_wood_soft_v1` | element_wood | 0.82 | 0.48 | 0.28 | 0.65 |
| `phys_stone_soft_v1` | element_stone | 0.00 | 0.72 | 0.75 | 0.00 |
| `phys_metal_light_v1` | element_metal | 0.00 | 0.82 | 0.66 | 0.00 |
| `phys_glass_standard_v1` | element_glass | 0.00 | 0.35 | 0.90 | 0.00 |

Tie-back to the 9-block kit in `UCBV_VISUAL_MOCKUP_SPEC_001.md` §3 — which are physics-bound today:

| Block | Bound profile | Status |
|---|---|---|
| `arch_wall_window_4m` | `phys_glass_standard_v1` | bound |
| `arch_window_round` | `phys_glass_standard_v1` | bound |
| `arch_foundation_square` | — | unbound |
| `arch_floor_square_4m` | — | unbound |
| `arch_wall_solid_4m` | — | unbound |
| `arch_wall_door_4m` | — | unbound |
| `arch_door_round` | — | unbound |
| `arch_roof_gable_4m` | — | unbound |

---

## 5. Special location — cozy village site plan (real coordinates)

Source: `examples/04_cozy_village_build_graph.json` — **the only example file with real node positions**;
06/07/09 below list nodes with no coordinates.

- `bounds.size_m`: [128, 128, 64], center [0,0,0]
- `house` → `cluster_cozy_house_small_A` @ (−10, 5, 0)
- `greenhouse` → `cluster_cozy_greenhouse_droplet_A` @ (10, 5, 0)
- `farm` → `cluster_cozy_farm_A` @ (8, −12, 0)
- `nori` → `char_nori7_base` @ (0, −6, 0) — a character node in the same graph as the buildings
- Generators (seed 123, deterministic): `gen_terrain_gentle_hills_v1`, `gen_road_network_v1`, `gen_village_layout_v1`, `gen_farm_layout_v1`
- World rules: `rule_day_night_v1`, `rule_crop_growth_v1`
- Validation required: collision, navigation, style, performance. Rollback: `COMPENSATING_MUTATION`.

**Verified inconsistency:** this file's `manifestation.stages` lists 5 stages
(`WIREFRAME, HOLOGRAM, MATERIALIZING, COMMITTING, COMPLETE`) — the art bible and the live, verified game
implement 4 (no `COMMITTING`). Not resolved here; flagged for whoever owns the next DNA/runtime
reconciliation pass.

---

## 6. Other world profiles — breadth only, not art-tasked

No coordinates exist in these source files — node lists only.

| World profile | Build graph | Nodes | Generators | World rules |
|---|---|---|---|---|
| arcane_clockwork | `06_arcane_clocktower_build_graph.json` | tower→cluster_arcane_clocktower_A, workshop→cluster_arcane_workshop_A, **golem→char_golem_base** | gen_clock_tower_v1, gen_clockwork_mechanism_v1 | rule_arcane_energy_network_v1 |
| spirit_valley | `07_spirit_shrine_build_graph.json` | shrine→cluster_spirit_shrine_A, court→cluster_spirit_lotus_courtyard_A | gen_temple_courtyard_v1, gen_bamboo_grove_v1, gen_spirit_restoration_states_v1 | rule_spirit_restoration_v1 |
| oceanpunk_abyss | `09_ocean_bubble_district_build_graph.json` | home→cluster_ocean_bubble_home_A, library→cluster_ocean_coral_library_A, station→cluster_ocean_submarine_station_A | gen_terrain_ocean_depth_tiers_v1, gen_bubble_base_v1, gen_coral_reef_v1, gen_kelp_forest_v1 | rule_depth_pressure_v1, rule_biolume_response_v1 |

Note the arcane clocktower graph places a **character** (`char_golem_base`) as a build-graph node
alongside buildings — the same pattern used for Nori-7 in the cozy village graph. Characters and
locations already share one graph format in the source data; this is not a leap this sheet is making.

---

## 7. New findings this pass (logged, not resolved)

1. **Two "cozy cream" palettes.** Art bible architecture palette (`#fdf3e2`/`#7fc98f`, approved, live)
   vs. DNA character recipe palette `mat_cozy_cream_leaf_v1` (`#F7E9C6`/`#78B65B`, used by real recipes).
   Close, never reconciled. This sheet uses each source's own values rather than merging them.
2. **Manifestation stage count disagrees** — 5 (village build graph) vs. 4 (art bible, live game).
3. **Skeleton catalog has the same shared-default gap** as the block catalog's socket outputs.
4. **Character Foundry prose rig names have no literal catalog skeleton_id.** Affects Mây Mạch and
   Bác Bắp specifically; Bác Bắp is left with two named unresolved options.

---

## 8. Scope and non-authorization

Same as spec 001: visual + data brief only, step 2 of the UCBV sequencing lock. No dispatch, no product
write, no acceptance. `UCBV-001` remains `queued_not_authorized` per Directive 77 until Human PASS on the
H1 five-minute gate and a new monotonic Codex directive. Character-to-skeleton mappings marked PROPOSED
are illustrations, not decisions.

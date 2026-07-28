# MAPPING_TO_VNEXT_001 — Character Build Recipe (§15) → UniversalEntityRecipe

`accepted=false` · `self_accept=false` · design only

Source: `AIDLE_OBJECT_DNA_AI_BUILD_CARD_SYSTEM_SOURCE_001.md` §15  
Target SSOT: `dna_platform_vnext/schemas/universal_entity_recipe.schema.json`

| §15 field | UniversalEntityRecipe path | Notes |
|-----------|----------------------------|-------|
| `character_id` | `recipe_id` and/or `provenance.subject_id` | Normalize to `^[a-z0-9_]+$` |
| `design_card_id` | **Extension:** `provenance.design_card_id` or card session object | Not in UER 0.1 core — add via card session, do not fork IR |
| `world_profile` | `world_profile` | Same enum family |
| `skeleton_family` | `facets.motion.skeleton_id` | May need alias map (e.g. robot_biped_small_v1 ↔ skel_small_biped_robot_v1) |
| `rest_pose` | **Extension:** `facets.motion.rest_pose` optional | Not required in UER 0.1 |
| `body_modules[]` | `instances[]` with `role: ROOT` or body parts | Prefer one ROOT module + attachments |
| `attachments[]` | `instances[]` + `connections[]` | Match Nori example pattern |
| `animation_sets[]` | `facets.motion.animation_set_id` (+ array extension later) | UER 0.1 has single `animation_set_id`; multi-set = capability gap → list in blockers or facet extension later |
| `material_theme` | `facets.presentation.material_theme_id` | |
| `output.*` | `readiness` + `validation_expectations` + asset_requests | LOD/GLB/scene are deliverable claims, not free commits |

**Rule:** Writers emit UniversalEntityRecipe for any compiler work.  
`character_build_recipe_projection.schema.json` is a **view** for card confirmation UI only.

# Object DNA / Card System — design extensions for DNA Platform vNext

| Field | Value |
|-------|--------|
| Work order | `WO-OBJECT-DNA-CARD-SYSTEM-001` |
| Directive | **99** |
| Status | `STAGING / DESIGN_EXTENSION` |
| `accepted` | **false** |
| `self_accept` | **false** |

## Purpose

Additive design content that **fills** DNA Platform vNext holes (skeleton taxonomy, semantic node IDs, 5-level mockup cards). It does **not** fork a second compiler platform.

**SSOT for compilation / authority:** `orchestration/control/dna_platform_vnext/`  
**Merge decision:** `RECONCILIATION_001.md` (confirmed default: content → vNext L1 + V5)

## Files in this folder

| File | Task |
|------|------|
| `AIDLE_OBJECT_DNA_AI_BUILD_CARD_SYSTEM_SOURCE_001.md` | Human source transcription (read-only convenience) |
| `RECONCILIATION_001.md` | Task 1 — vs vNext (required before formalization) |
| `contracts/semantic_node_id_convention.schema.json` | Task 2 — marker vs semantic_id |
| `contracts/skeleton_family_definition.schema.json` | Task 2 — family entry shape |
| `contracts/mockup_card_system.schema.json` | Task 2 — 5-level card UX (V5 content) |
| `contracts/character_build_recipe_projection.schema.json` | Task 2 — §15 as **projection** of UniversalEntityRecipe (not IR SSOT) |
| `registries/skeleton_family_categories_v1.json` | Task 2 — 7 categories + named IDs + clip lists |
| `registries/nori7_robot_biped_small_v1_entry.json` | Task 3 — Nori under family + honest gaps |
| `MAPPING_TO_VNEXT_001.md` | Field map §15 → UniversalEntityRecipe |

## Out of scope (this WO)

- No `game/**` patches  
- No Blender production  
- No DNA Platform vNext V1–V6 execution  
- No Nori-7 asset rebuild  

## Relation to vision lock

`AIDLE_GAME_VISION_LOCK_001.md` §13: DNA Platform vNext remains **queued / not authorized for execution**. These files are design staging only. §12 AI design-build parity applies when any card is later realized in-game.

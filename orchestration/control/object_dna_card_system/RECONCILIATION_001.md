# RECONCILIATION_001 — Object DNA / Card System vs DNA Platform vNext

| Field | Value |
|-------|--------|
| `work_order` | `WO-OBJECT-DNA-CARD-SYSTEM-001` |
| `directive_id` | **99** (per dispatch; standing vision lock §13 living pointer also names DNA Platform vNext as QUEUED / not authorized for execution) |
| `author` | Design parent Grok `019f8e3c-e53b-74e0-a878-df6b8398338e` |
| `date` | 2026-07-24 |
| `authority` | `REPORT_ONLY` / design memo |
| `accepted` | **false** |
| `self_accept` | **false** |
| `purple` | **WAITING** (does not adjudicate this memo) |
| `scope` | Compare only; no `game/**`, no Blender, no vNext V1–V6 execution |

---

## 0. Files read for this memo (evidence, not memory)

### New Object DNA / Card System source

| Path | Role |
|------|------|
| `orchestration/control/object_dna_card_system/AIDLE_OBJECT_DNA_AI_BUILD_CARD_SYSTEM_SOURCE_001.md` | Full Human source transcription (L0–L7, §5 families, §4 semantic IDs, §9–13 cards, §15 recipe, §20 agents, §22 P0–P10, §24 DoD) |

### DNA Platform vNext

| Path | Role |
|------|------|
| `orchestration/control/dna_platform_vnext/README.md` | STAGING status; pipeline; Gate V0 only |
| `orchestration/control/dna_platform_vnext/DNA_PLATFORM_VNEXT_ARCHITECTURE_001.md` | L0–L6 platform layers; V0–V6 gates; invariants |
| `orchestration/control/dna_platform_vnext/SOURCE_REGISTRY.json` | Content-addressed sources; observed_limits (15 skeleton families, 172 clips names-only) |
| `orchestration/control/dna_platform_vnext/schemas/dna_catalog_entry.schema.json` | Typed catalog entry kinds + lifecycle |
| `orchestration/control/dna_platform_vnext/schemas/generation_request.schema.json` | Player intent → request |
| `orchestration/control/dna_platform_vnext/schemas/universal_entity_recipe.schema.json` | UniversalEntityRecipe IR |
| `orchestration/control/dna_platform_vnext/schemas/generation_result.schema.json` | 4 compiler statuses |
| `orchestration/control/dna_platform_vnext/prompts/00_MASTER_DNA_PLATFORM_SYSTEM.md` through `06_RELEASE_AUDITOR.md` | 7 prompt files (master + 6 roles) |
| `orchestration/control/dna_platform_vnext/examples/nori7_universal_recipe.json` | Staging Nori IR example |
| `orchestration/control/dna_platform_vnext/validate_dna_platform_vnext.py` | Listed in README; Gate V0 validator present |

### Nori-7 real asset (proof case only)

| Path | Role |
|------|------|
| `game/assets/ucbv_001/character/nori7/skeleton/skel_small_biped_robot_v1.hierarchy.json` | 14 production bones; `bone_count_production: 14` |
| `game/assets/ucbv_001/character/nori7/package_manifest.json` | Identity, deliverables, skeleton_id, animation_set_id |
| `game/assets/ucbv_001/character/nori7/animations/animation_state_machine.json` | 8 states / transitions |
| `game/assets/ucbv_001/character/nori7/animations/anim_robot_gardener_v1.timing_table.json` | Production timings; DNA residual names-only |
| `game/assets/ucbv_001/character/nori7/export/nori7_mockup_parity_v1_receipt.json` | 10 keyed clips in GLB |
| `game/assets/ucbv_001/character/nori7/sockets/attachment_sockets.json` | character_back/hand/head + vfx_anchor |

### Standing lock

| Path | Role |
|------|------|
| `orchestration/control/AIDLE_GAME_VISION_LOCK_001.md` | §12 AI design-build parity + 100% mockup fidelity; §13 DNA Platform vNext **queued / not authorized** |

---

## 1. Same problem, different names (concrete map)

| Object DNA / Card System (new doc) | DNA Platform vNext | Same shape? |
|------------------------------------|--------------------|-------------|
| Pipeline: intent → family → DNA → mockup cards → recipe → Blender → Godot → preview → confirm → catalog/commit (SOURCE §2) | `player intent → GenerationRequest → UniversalEntityRecipe → semantic gate → Build Recipe/Graph → quarantine → preview → Human confirm → World Commit` (README lines 11–13) | **Same product spine.** Card UX is the missing human-facing layer on the front half. |
| Object DNA layers L0–L7: Semantic Nodes, Bone Graph, Joint Rules, Contact Markers, Skeleton Family, Animation Library, Recipe, Runtime Module (SOURCE §3) | Platform layers L0–L6: source registry, typed DNA entries, GenerationRequest, UniversalEntityRecipe, semantic compiler, execution targets, artifact gates (ARCHITECTURE §4) | **Different layering axes.** New doc L* = **rig/motion content stack**. vNext L* = **platform compilation stack**. Not 1:1 renames; complementary. |
| Character Build Recipe (SOURCE §15) — `character_id`, `skeleton_family`, `body_modules[]`, `attachments[]`, `animation_sets[]`, `material_theme`, `output` | `UniversalEntityRecipe` — `entity_kind`, `instances[]`+`module_ref`, `connections[]`, `facets.motion` (`skeleton_id`, `animation_set_id`), `facets.presentation`, authority, readiness, fingerprint (schema `universal_entity_recipe.schema.json`) | **Compatible, not identical.** §15 is a **character-shaped projection** of a subset of UniversalEntityRecipe. §15 lacks authority block, readiness/blockers, payload fingerprint, compiler_target, 4-state result. vNext lacks explicit card selection IDs / multi-level UX fields. |
| Skeleton Family catalog with named IDs e.g. `robot_biped_small_v1` (SOURCE §5.5) | `entry_kind: "SKELETON"` in `dna_catalog_entry.schema.json`; SOURCE_REGISTRY points at Tier3 `skeleton_families.json` (15 families, required bones only `root/body/head` per ARCHITECTURE §2 + SOURCE_REGISTRY `observed_limits`) | **Same concept (catalog of skeletons).** New doc is **richer taxonomy content**; vNext/Tier3 is **shallow placeholder** until V1 migration. |
| Animation library per family (clip name lists in §5) | `entry_kind: "ANIMATION_SET"`; SOURCE_REGISTRY: 21 sets / 172 clips with fields only `clip_id`, `events`, `loop` | **Same concept.** Both currently design-level lists unless a production asset (Nori) supplies timings/GLB actions. |
| Validation Gate + quarantine + Human approve before APPROVED (SOURCE §2, §14, §24) | Invariants + `PROPOSAL_READY` / `ASSET_REQUEST_REQUIRED` / `REJECTED` / `HITL_REQUIRED` + L6 quarantine/promotion (ARCHITECTURE §3–4, generation_result.schema.json `status` enum) | **Same safety intent.** vNext is more machine-typed; new doc is more production-step narrative. |
| 12 agents (Intent, Classifier, Skeleton, Mockup, Recipe, Node Match, Rig, Anim, Blender, Godot, Validator, Review) (SOURCE §20) | 6 bounded prompts (Intent Architect, DNA Composer, Semantic Validator, Asset Authoring Planner, Runtime Integrator, Release Auditor) + master (prompts/) | **Overlapping roles, different grain.** Maptable: Intent↔01; Classifier+Skeleton+Recipe≈02; Validator↔03; Blender↔04; Godot↔05; Review↔06. Mockup/Node Match/Rig/Anim are **finer content workers** not yet first-class prompt files. |
| Build states DRAFT→…→APPROVED (SOURCE §14) | lifecycle_status on catalog entries: DESIGN_ONLY / AUTHORING_REQUIRED / QUARANTINED / VERIFIED / APPROVED / DEPRECATED (`dna_catalog_entry.schema.json`) + generation_result statuses | **Related but not equal.** §14 is a **build job state machine**; vNext separates **catalog lifecycle** from **compile result**. Both needed. |

---

## 2. What the new doc specifies that vNext does **not** yet write as contracts

Concrete gaps (new content to add as **extensions**, not a parallel platform):

1. **7-category skeleton-family taxonomy with named family IDs**  
   SOURCE §5.1–5.7: humanoid_*, quadruped_*, bird_*, fish_*, robot_*/door_*/water_wheel_*, plant_*/tree_*, vehicle_*.  
   vNext has the *slot* (`SKELETON` entry kind) and points at Tier3 catalog of **15** families with placeholder bones only (ARCHITECTURE §2; SOURCE_REGISTRY `skeleton_family_count: 15`, `all_skeleton_required_bones: [root, body, head]`). It does **not** encode the 7-category tree, per-family required clip lists, or production bone graphs.

2. **Semantic node-ID convention (marker-for-display vs semantic_id-for-data)**  
   SOURCE §4 example (`marker: "A"`, `semantic_id: "root"`).  
   vNext schemas do not define a `node_marker` / display-marker type. Universal recipe motion facet has `skeleton_id` / `animation_set_id` strings only (schema motion_facet around lines 571+).

3. **5-level mockup card UX**  
   SOURCE §9–13: Object Family → Skeleton Selection → Visual Style → Animation Package → Build Confirmation, with required card fields (§9.3).  
   vNext **names** gate **V5 Player creation UX** as future work (ARCHITECTURE §7) but provides **no** card schema, no selection state object, no multi-card proposal shape.

4. **Non-character object card packs**  
   SOURCE §19: door / water-wheel / tree skeletons + animations.  
   vNext `entity_kind` already includes PROP, VEHICLE, BUILDING, PLANT (universal_entity_recipe.schema.json) — but no door_mechanism / water_wheel / tree_standard **family content** or card templates.

5. **Pose DNA package filesystem layout**  
   SOURCE §6 (`Pose_DNA/<family>/skeleton_definition.json` …).  
   vNext uses content-addressed SOURCE_REGISTRY paths into Tier3; no Pose_DNA package contract.

6. **Narrative 11-phase roadmap P0–P10 and vertical-slice DoD**  
   SOURCE §22–§24.  
   vNext has V0–V6 implementation gates (ARCHITECTURE §7) — different numbering, overlapping intent (P0≈V0, P6≈V5, P7≈V3, P8≈V4).

7. **Node-matching pipeline for generative meshes**  
   SOURCE §16–§17.  
   vNext AssetRequest path is abstract; no landmark-matching steps schema.

---

## 3. What vNext has that the new doc does **not**

1. **Typed compiler IR** — `UniversalEntityRecipe` with instances, connections, facets, authority, readiness, payload_fingerprint (`universal_entity_recipe.schema.json`).

2. **GenerationRequest** — session, actor consent, budgets, constraints (`generation_request.schema.json`).

3. **4-state compiler output** — `PROPOSAL_READY` | `ASSET_REQUEST_REQUIRED` | `REJECTED` | `HITL_REQUIRED` (`generation_result.schema.json` `status` enum lines 30–36; ARCHITECTURE §4 L4).

4. **Lifecycle / provenance on every catalog entry** — lifecycle_status, artifacts with sha256/qa/license (`dna_catalog_entry.schema.json`).

5. **Content-addressed SOURCE_REGISTRY** — path + sha256 for Tier3 catalogs and accepted contracts (`SOURCE_REGISTRY.json`).

6. **Explicit refuse of parallel commit path** — compiles into existing strict Build Recipe/Graph + world_prompt only (ARCHITECTURE §4 L5; README lines 17–22).

7. **Gate V0 tooling** — validator script + adversarial invalid examples + Nori staging fixtures (README; `examples/`).

8. **Honesty about Tier3 shallowness** — 170 modules DESIGN_READY with no artifact URIs; 172 clips name-only (ARCHITECTURE §2; SOURCE_REGISTRY `observed_limits`).

9. **Binding to Architecture Lock / World Commit / no AI-executed code** — invariants stronger and more operationalized than SOURCE §24 bullets alone.

---

## 4. Character Build Recipe vs UniversalEntityRecipe (shape check)

### SOURCE §15 Character Build Recipe (excerpt fields)

- `schema_version`, `character_id`, `design_card_id`, `world_profile`
- `skeleton_family`, `rest_pose`
- `body_modules[]`, `attachments[]`
- `animation_sets[]`, `material_theme`
- `output.{lod_levels, collision, glb, godot_scene}`

### vNext UniversalEntityRecipe (required top-level)

- `recipe_id`, `request_id`, `entity_kind`, `world_profile`, `compiler_target`
- `root_instance_id`, `instances[]`, `connections[]`
- `facets` (presentation, motion, behaviors, physics, vfx, audio)
- `authority` (proposal_only, no commit, no generated code…)
- `readiness` (source_status, runtime_ready, blockers, asset_requests)
- `validation_expectations`, `provenance`, `payload_fingerprint`

### Verdict

| Question | Answer |
|----------|--------|
| Same shape? | **No** — §15 is a flat character DTO; UER is a graph IR + safety envelope. |
| Compatible? | **Yes** — §15 maps into UER: `character_id`→recipe/id; modules→instances; attachments→instances+connections; skeleton/anim→`facets.motion`; material→`facets.presentation`; `design_card_id` should become **new optional provenance/UX field** on request or recipe. |
| Competing schema? | **Would be harmful if forked.** Treat §15 as **profile view** / export of UER for character card confirmation, not a second recipe SSOT. |

---

## 5. Recommendation (default expectation — **confirmed**)

**Do not build a second platform.** Merge as follows:

1. **DNA Platform vNext remains the compiler/platform SSOT** (Gate V0 contracts, SOURCE_REGISTRY, 4-state results, authority, quarantine story). Status stays STAGING; **V1–V6 remain unauthorized** per vision lock §13 until a separate Human directive.

2. **Object DNA / Card System becomes concrete content + UX contracts that fill vNext holes:**
   - Skeleton taxonomy + required clip lists → **L1 typed `SKELETON` / `ANIMATION_SET` catalog content** (and/or additive registries under this WO folder that vNext V1 can ingest).
   - Semantic node-ID convention → **written contract** referenced by skeleton entries.
   - 5-level mockup cards → **first-draft schema for gate V5** (content for “Player creation UX”, not a second commit path).
   - Non-character packs (door/wheel/tree) → same skeleton/card registries with `entity_kind` already supported by UER.
   - Character Build Recipe §15 → **document mapping into UniversalEntityRecipe**; optional `character_build_recipe.view.schema.json` as a **projection**, not a parallel SSOT.

3. **Naming bridge (avoid dual IDs where possible):**
   | New doc | Existing production / Tier3 |
   |---------|----------------------------|
   | `robot_biped_small_v1` (SOURCE §5.5 Nori-7) | Production hierarchy id `skel_small_biped_robot_v1` (`skel_small_biped_robot_v1.hierarchy.json` `skeleton_id`) |
   | Prefer registry `aliases` field so both IDs resolve to one family entry until V1 migration renames. |

4. **Roadmap alignment (informational):**
   | SOURCE P* | vNext V* |
   |-----------|----------|
   | P0 Schema/registry | V0 done; V1 catalog migration |
   | P1 Nori robot biped | Proof case already partially exists in `game/assets/.../nori7/` (not product-accepted) |
   | P6 Mockup card UI | V5 Player creation UX |
   | P7 Blender Bridge | V3 Asset request/promotion |
   | P8 Godot runtime | V4 Runtime intake |
   | P9–P10 expansion | After V1–V5 honesty |

5. **Scope stop:** This WO’s Task 2/3 = **additive design artifacts only**. No Blender, no `game/**` patch, no executing vNext V1–V6. No claim that Tier3 15 families or 172 clips are runtime-ready.

---

## 6. Incompatibility check (escalate?)

| Risk | Finding |
|------|---------|
| Fundamentally incompatible compilers? | **No.** Same commit authority story; card system is UX + content richness. |
| Dual recipe SSOT? | **Risk if §15 is implemented as competing schema.** Mitigation: projection-only + map to UER (above). |
| Dual skeleton ID for Nori? | **Naming tension only** (`robot_biped_small_v1` vs `skel_small_biped_robot_v1`). Resolve with aliases, not two skeletons. |
| Would Task 2 require game/** or V1–V6? | **No** if additive files under `object_dna_card_system/` (+ optional pointer docs). |

**Escalation: not required.** Proceed Task 2 as **extension content for vNext L1 + V5**, not a fork.

---

## 7. Honesty flags for reviewers (Claude / Human)

- vNext Gate V0 is **contracts + validator + examples**, not a live player UX (README status line).
- Tier3 skeleton/animation catalogs remain **shallow** (ARCHITECTURE §2; SOURCE_REGISTRY `observed_limits`).
- Nori-7 is a **real** rigged GLB proof case (vision lock §13; package under `game/assets/ucbv_001/character/nori7/`) but **not product-accepted** (`accepted: false` on package_manifest and hierarchy).
- New doc’s “18 clips” on robot card mockups (SOURCE §9.2) is **illustrative UI copy**, not measured against Nori’s GLB (receipt lists **10** clips — Task 3 will detail).

---

## 8. Memo decision status

| | |
|--|--|
| `accepted` | **false** |
| `self_accept` | **false** |
| Recommendation | **Merge: Object DNA taxonomy + card UX fill vNext L1 content + V5 UX; keep UniversalEntityRecipe as recipe IR SSOT** |
| Next | Task 2 additive schemas/registries; Task 3 Nori-7 registry entry + gap report |
| Purple | WAITING |

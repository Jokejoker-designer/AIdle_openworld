# Design contract — UCBV-001 U1 Unified Style Lock (+ C0 Directive 83)

## Goal and target artifact

**Goal:** Freeze one reusable visual DNA so Nori-7 and the first construction
block family share silhouette, palette, materials, LOD, modular IDs,
STATE_VARIANTS, manifestation, and accessibility rules. **C0 (Directive 83)**
adds fail-closed production preflight, **explicit cozy-cream reconciliation**,
nearly-white remediation, and animation contract intent for C1–C2.

**Target artifacts (U1 + C0 amendment):**

| Artifact | Path |
|---|---|
| Style lock brief | `orchestration/design/ucbv_001/style_lock/U1_unified_style_lock.md` |
| Palette/material alias table | `orchestration/design/ucbv_001/style_lock/unified_palette_material_alias_table.json` |
| DESIGN.md | `orchestration/design/ucbv_001/style_lock/DESIGN.md` |
| Shared tokens (U1; immutable this wave unless separately leased) | `game/resources/art_styles/tokens/ucbv_001_shared_character_block_tokens.json` |
| C0 production preflight | `orchestration/design/ucbv_001/style_lock/C0_visual_production_preflight.md` |
| C0 cream reconciliation | `orchestration/design/ucbv_001/style_lock/C0_cream_reconciliation.json` |
| This contract | `orchestration/design/ucbv_001/style_lock/design-contract.md` |
| Implementation handoff | `orchestration/design/ucbv_001/style_lock/implementation-handoff.md` |

**Audience:** C1 character production, C2 Godot runtime, C3 Red, C4 QA, C5 Purple,
Codex/Human reviewers.

**Not in scope (C0):** meshes, GLBs, runtime scripts, DNA v1.2, Tier3 activation,
P2E-002, Bác Bắp, full 28-character wave, helper/temp files outside lease.

## Evidence table

| Evidence | Path | Confidence | Use |
|---|---|---|---|
| Directive 81 | `orchestration/control/codex_directive.json` | observed | Authorization U0–U8 |
| Work order | `orchestration/work_orders/WO-UCBV-001-...md` | observed | Scope + gates |
| Unified direction | `orchestration/control/UNIFIED_CHARACTER_BLOCK_VISUAL_DIRECTION_001.md` | observed | Shared DNA requirements |
| Practical findings | `orchestration/control/CHARACTER_SKELETON_PRACTICAL_FINDINGS_...md` | observed | Palette/manifestation gaps |
| U0 receipt | `orchestration/receipts/ucbv_001/U0_ssot_preflight_001.json` | observed | Nori-7 select + leases |
| COZY art bible | `Scene/.../COZY_ART_BIBLE_001.md` | observed | Canonical hex + 4 stages |
| Material mapping | `orchestration/contracts/block_dna_adapt_001/material_slot_mapping.contract.json` | observed | MAT_* SSOT |
| Shared 2.5D tokens | `game/resources/art_styles/tokens/shared_2_5d_tokens.json` | observed | Shape/motion/a11y |
| Cozy profile | `game/resources/art_styles/cozy_cyber_pixel_2_5d.json` | observed | Profile mood palette |
| STATE_VARIANTS | `game/resources/world_profiles/state_visual_variants.json` | observed | Reuse rule |
| constants.gd stages | `game/scripts/core/constants.gd` | observed | Live 4 stages |
| Foundry Nori-7 | `game_character/.../01_nori_7.md` | observed | Identity + silhouette |
| Recipe | `world_DNA/.../01_nori7_character_recipe.json` | observed | Modules + DNA theme alias |
| Runtime catalog | `game/resources/block_assembly/runtime_catalog.json` | observed | Allowlisted module ids |
| Visual mockup spec | `orchestration/control/visual_reference/UCBV_VISUAL_MOCKUP_SPEC_001.md` | observed | Composition reference |
| H1 human pass | `orchestration/reviews/CODEX_H1-CONSOLIDATE-001_HUMAN_ACCEPTANCE_007.json` | observed | Gate before UCBV |
| Directive 83 | `orchestration/control/codex_directive.json` | observed | AUTHORIZE_STRICT_UCBV_CORRECTION |
| WO correction 002 | `orchestration/work_orders/WO-UCBV-001-STRICT-CORRECTION-002.md` | observed | C0–C5 leases + gates |
| Anim integration map | `orchestration/control/UCBV_ANIMATION_BLOCK_INTEGRATION_MAP_001.md` | observed | Tier3 names + UCBV extension |
| Machine gate | `orchestration/reviews/CODEX_UCBV-001_MACHINE_GATE_001.json` | observed | Production GLB + lease blockers |
| Human strict auth | `orchestration/reviews/CODEX_UCBV-001_HUMAN_STRICT_AUTHORIZATION_002.json` | observed | No waiver |

## Keep / Change / Do not copy

| Reference | Keep | Change | Do not copy |
|---|---|---|---|
| COZY_ART_BIBLE | Hex roles, 4-stage manifestation, shape language, animation prop timings as ambient reference, lighting metrics | Character production clip timings (U4 owns) | Treat bible as mesh authority |
| DNA mat_cozy_cream_leaf | Recipe linkage awareness | Map cream/leaf to bible + MAT_* | Ship DNA hex as art SSOT; rewrite DNA package |
| DNA 5-stage manifestation | — | Lock product to live 4 | COMMITTING stage |
| Visual mockups 001–003 | Composition ideas, bible-aligned hex transcription | Mockup status was pre-lock; U0 locked Nori-7 | Invent module ids not in catalogs; treat mockup as acceptance |
| Play Together class (bible reference) | Low-complexity readable charm | AIdle original forms | Copyrighted mascots / costumes |
| P1E MAT_* kit | All live material ids + slot map | None for U1 | Parallel material system |
| skeleton_families placeholders | Family label + anim set linkage | Real bones in U4 | Shared [root,body,head] as production truth |

## Final design stance

One warm cozy rounded-readable language binds Nori-7’s teardrop ceramic helper
silhouette to a soft modular architecture kit. Color is three groups (cream,
leaf, wood/glass/roof) with cyan reserved for the live four-stage
manifestation chain. **C0 canonical cream is bible `#fdf3e2` / shade `#efe0c8`**;
DNA `#F7E9C6` remains non-authoritative alias only — both values are documented
in `C0_cream_reconciliation.json` so the pick is never silent. Production body
must use multi-value cream + darker joints/face to defeat nearly-white uncanny
reads. Animation: Tier3 gardener set = names only; C1 keys real GLB actions +
UCBV build extension. Runtime truth is MAT_* + STATE_VARIANTS. Character joints
never inherit world-grid sockets.

## Risks and unknowns

| Risk / unknown | Impact | Mitigation |
|---|---|---|
| Corner / some structure ids not yet pinned to one allowlisted id | U3 ambiguity | Role locked; U3 selects from accepted catalogs only |
| Recipe cream ≠ bible cream | Asset mismatch | C0 reconciliation + alias table force bible + MAT_* |
| Animation timings absent in DNA | Empty payload treated as real motion | C0 lock: names only; C1 keyed GLB + adapter |
| Skeleton bones are placeholders | Bad rig if trusted | Exact 14-bone production hierarchy locked for C1 |
| Profile manifestation `#62E6FF` vs bible `#3fd0e0` | Chrome hue drift | Stage chrome follows bible; profile field is mood anchor |
| Flat bible cream reads near-white | Uncanny Human finding | Multi-value body + leaf joints + face sockets required |

## Quality gate checklist (P0)

- [x] DESIGN.md uses nine Open Design headings
- [x] Contract names target artifact, audience, evidence
- [x] References split Keep / Change / Do not copy
- [x] Inferences labeled; DNA alias not presented as art truth
- [x] One coherent stance (not moodboard menu)
- [x] Implementation handoff operational for **C1** (C0 amendment)
- [x] Anti-patterns are concrete (incl. nearly-white + DNA cream SSOT)
- [x] Manifestation = live 4
- [x] Accessibility: contrast, reduced-motion, no color-only critical info
- [x] Nori-7 + nine module roles bound; no Bác Bắp / invented recipes
- [x] C0 cream table documents **both** hexes and picks canonical with rationale
- [x] C0 fail-closed checklist covers mesh/GLB/skin/rig/anim/palette/catalog/controls/delete/evidence
- [x] Animation Tier3 = names only; UCBV extension named; markers non-mutating
- [x] accepted=false / self_accept=false

# ASSET_REQUEST — P1E Art Polish 001 (ship-quality residual)

Status: **REQUEST_ONLY** · `accepted=false` · `self_accept=false`  
Parent WO: `WO-COMMERCIAL-P1E-ART-001` · Directive **99** · TIER2  
Authority: no free `write_approved_catalog`; quarantine → signed promotion only  
H1 only: cozy-cyber-pixel · cream SSOT `#fdf3e2` · no H2–H6 · no Text-to-3D

## Context

Machine smokes p1e003 / p1e004_art_style_manager / p1e006 are **PASS** (2026-07-23
commercial_p1e_001 run). Checklist gate 6 (density/styles/profiles) remains
machine-green. Residual ship quality is **content/art coherence** (checklist gate 12).

Package under test: `E:/AIdle_Blender_Bridge_P0/storage/generated_quarantine/BLD-03CB1AADD475`
(module_count=43, hash_ok 47/47, world_profile=cozy_cyber_pixel).

## Residual inventory (vs cozy art bible + UCBV style lock)

| ID | Area | Severity | Finding | Proposed resolution |
|----|------|----------|---------|---------------------|
| ART-G01 | Toon / outline | **HIGH** (ship look) | Style tokens require readable silhouette + outline as a non-color state signal (`shared_2_5d_tokens.json` accessibility). No mesh `*.gdshader` / toon / silhouette outline pipeline exists under `game/`; only UI font outlines. GLB modules rely on baked matte materials only. | Author inverted-hull or post-process outline material family for MAT_* / GLB surfaces; wire through `ArtStyleManager` / world_profile without photoreal mix. Headed visual gate required. |
| ART-G02 | Density / props | **MED** | Density band PASS (43 ∈ 35–50). Kit composition: fence×10, flower×9, path_stone×8, rock×6, lamp×4, landmarks×1 each (house, greenhouse, tree, pond, light_brush, farm_plot). Prior Red residual: fence multi-cluster (not continuous enclosure) — metrics PASS ≠ continuous charm. | New quarantine placement job: continuous yard fence ring + 1–2 mid-scale prop roles (bench/mailbox/path connector) while staying ≤50 instances. |
| ART-G03 | Palette variants | **MED** | `cozy_cyber_pixel` = identity_register (correct); `surrealism_canvas` material_table works (93 rewrites in smoke). Deferred: pastoral/cyberpunk art styles map nearest→cozy without kits; 5 world_profiles have no kit. Profile JSON `cream_light`=`#FFF1C7` drifts from production cream SSOT `#fdf3e2` (bible/U1/C0). UI chrome also hardcodes `FFF1C7`. | (a) Document chrome cream vs wall cream roles explicitly in style profile; (b) optional identity-safe cream alias field; (c) do **not** recolor verified MAT_* under cozy. HOLD product default flips without Human (P1E-004 option HOLD). |
| ART-G04 | Starter Realm coherence | **MED** | Live sessions can restore non-cozy `art_style` from `world_meta.cfg` while loading Cozy GLB kit (P1E-004 root-cause). GLB materials are not recolored by ArtStyleManager on cozy modules; only ground/sky/ambient + procedural fillers. Surrealism path rewrites MAT_* via selector (good for that profile). | Product options A/B/C still need Human pick (default cozy gate / per-style kits / env-tint-only). Recommend Option A for H1 ship: default + soft-gate non-cozy until kit exists. |
| ART-G05 | Cream SSOT enforcement | **LOW–MED** | Canonical `#fdf3e2` / shade `#efe0c8` locked in C0/U1. DNA `#F7E9C6` remains NON_AUTHORITATIVE. Risk is author confusion, not failing smokes. | Keep C0 table as gate; any new paint uses bible hex; no DNA theme rewrite this wave. |
| ART-G06 | Headed visual ship gate | **MED** | Headless smokes do not prove silhouette charm, outline readability, or continuous fence delight. | Headed capture harness under evidence lease; Human taste gate before ship gate 13. |

## Not requested (out of scope)

- H2–H6 horizons, unrestricted Text-to-3D, free catalog writes
- DNA Platform vNext execution, P2E-002, character-backbone program
- Ship/publish/network (Red F01)

## Preferred next executable WO (draft)

See `DRAFT_WO_P1E_ART_POLISH_002.md` in this evidence folder. Recommend sequenced mini-waves:

1. **W1 Outline/toon** — smallest runtime silhouette pass for H1 MAT_* + quarantine GLB next_pass or material_override outline.
2. **W2 Density charm** — continuous fence + 1–2 props via Bridge quarantine job (no free catalog).
3. **W3 Coherence policy** — Human pick of style-application Option A/B/C + cream_light role documentation.

## Decision this wave

**No product patch applied.** Residual fixes are multi-file / Blender / shader / product-policy and exceed the "one small named high-value fix" safety bar under VERIFY-first authority.

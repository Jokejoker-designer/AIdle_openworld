# DRAFT WO-P1E-ART-POLISH-002 — H1 toon/outline + fence charm (NOT AUTHORIZED)

Status: `DRAFT` · `accepted=false` · `self_accept=false`  
Execute only after Human / parent batch sign-off on `WO-COMMERCIAL-P1E-ART-001` inventory.  
Profile: `aidle-worldgen-asset-art` · TrustLayer blue-team-p0-remediator · UI ui-color-type-specialist  
Authority when approved: `PATCH_DRAFT` on **named** paths only · quarantine → signed promotion  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852` · Directive 99 · TIER2 · H1 only

## Goal

Close ship-quality residual **ART-G01** (mesh silhouette outline/toon) and optionally
**ART-G02** (continuous fence charm) for Cozy Cyber-Pixel Starter Realm without
opening H2–H6 or free catalog writes.

## Preconditions (already green)

- p1e003 / p1e004_art_style_manager / p1e006 exit 0 (see commercial_p1e_001 smokes)
- Package `BLD-03CB1AADD475` density 43, validation_passed, GAME allowlist OK
- Cream SSOT remains `#fdf3e2` / shade `#efe0c8` (C0)

## Proposed lease (approve before touch)

### Product (named only after approve)

- `game/shaders/**` (new outline/toon — create if absent)
- `game/scripts/modules/asset/glb_intake_runtime_builder.gd` (optional outline apply hook)
- `game/scripts/modules/asset/world_profile_variant_selector.gd` (cozy identity must keep outline)
- `game/autoload/art_style_manager.gd` (optional outline weight token only)
- `game/resources/art_styles/cozy_cyber_pixel_2_5d.json` (document outline params; cream roles)
- `game/tests/p1e003_density_exposure_smoke.gd` and/or new `p1e_outline_*_smoke.gd`

### Quarantine / Bridge (not free catalog)

- New Bridge job under `E:/AIdle_Blender_Bridge_P0/storage/generated_quarantine/**` only
- Promotion path requires signed gate (no `write_approved_catalog` without Human)

### Evidence / receipts

- `orchestration/evidence/commercial_p1e_001/**`
- `orchestration/receipts/commercial_p1e_001/**`
- `orchestration/logs/commercial_p1e_001/**`

## Acceptance (executable)

1. Headless: prior p1e003/004/006 still PASS; new outline smoke exit 0 if added.
2. Headed: side-by-side Starter Realm PNGs with outline on vs off; silhouette readable on cream/leaf/wood.
3. Cozy identity_register does not recolor MAT_* to white; surrealism still chromatic.
4. Density remains 35–50 if placement wave runs; fence collision bodies still present.
5. `accepted=false` / `self_accept=false` until Purple + Human.

## Forbidden

- TIER3 horizons (H2–H6, Text-to-3D unrestricted, DNA vNext EXECUTION)
- Ship/publish/network
- Grandchildren
- Overwriting verified cozy materials with DNA cream `#F7E9C6` as SSOT

## Suggested wave split

| Wave | Owner profile | Scope |
|------|---------------|-------|
| POLISH-W1 | asset-art | Outline shader + apply path for H1 MAT_*/GLB |
| POLISH-W2 | asset-art + Bridge | Continuous fence + optional props quarantine job |
| POLISH-W3 | asset-art + Human | Style Option A/B/C decision + cream_light role doc |
| POLISH-QA | purple-acceptance | VERIFY_ONLY headed + smoke matrix |

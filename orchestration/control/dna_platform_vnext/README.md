# AIdle DNA Platform vNext

Status: `STAGING / DESIGN_AND_CONTRACT_PROTOTYPE`  
Authority: Human Product Lead requested platform redesign; this directory is
not runtime authority and does not authorize `game/**`, catalog promotion,
network access, shipping, or World Commit.

This kit turns the existing DNA catalogs into a provider-neutral compilation
pipeline:

`player intent -> GenerationRequest -> UniversalEntityRecipe -> semantic gate
-> strict Build Recipe/Graph -> quarantine asset work -> Godot preview ->
Human confirm -> World Commit`

The design deliberately keeps the active AIdle contracts:

- `contracts/world_prompt.schema.json` remains the only world proposal language.
- `orchestration/contracts/block_dna_adapt_001/` remains the strict placement,
  socket, material, idempotency and revision gate.
- Existing Tier3 elemental/physics catalogs remain typed extensions.
- AI can configure registered data or request authoring. It cannot execute
  generated code, approve assets, or mutate canonical world state.

## Contents

- `DNA_PLATFORM_VNEXT_ARCHITECTURE_001.md` — architecture, findings and gates.
- `SOURCE_REGISTRY.json` — content-addressed bridge to the real v1.1 sources.
- `schemas/` — request, catalog-entry, universal recipe and result contracts.
- `prompts/` — shared prompt constitution plus six bounded role prompts.
- `examples/` — honest Nori-7 proposal plus adversarial invalid fixtures.
- `validate_dna_platform_vnext.py` — schema, source-hash and semantic gate.
- `MIGRATION_V1_1_TO_VNEXT.md` — compatibility path without a destructive rewrite.

## Run

```powershell
python E:\AIdle_openworld\orchestration\control\dna_platform_vnext\validate_dna_platform_vnext.py
```

Green means the staging contracts are internally consistent. It does **not**
mean the 170 design-only modules, 15 skeletons or 172 named animation clips are
runtime assets.


# Migration from DNA v1.1 to vNext

This is an additive migration. Do not rewrite or rename the current Tier3
package in place.

## Phase A — Lock

1. Verify every `SOURCE_REGISTRY.json` SHA-256.
2. Treat the Tier3 package as immutable legacy input.
3. Keep `BLOCK-DNA-ADAPT-001`, motion-kit and World Prompt gates green.

## Phase B — Generate typed entries

Generate, do not hand-type, one `DNAEntry` per legacy record:

| v1.1 source | vNext entry kind | Initial lifecycle |
|---|---|---|
| `module_catalog.json` | `MODULE` | `DESIGN_ONLY` |
| `socket_types.json` | `SOCKET` | `VERIFIED` contract data |
| `skeleton_families.json` | `SKELETON` | `AUTHORING_REQUIRED` |
| `animation_library.json` | `ANIMATION_SET` | `AUTHORING_REQUIRED` |
| `material_themes.json` | `MATERIAL_THEME` | `DESIGN_ONLY` |
| `behavior_blocks.json` | `BEHAVIOR` | `VERIFIED` only if runtime ID exists |
| `procedural_generators.json` | `GENERATOR` | `DESIGN_ONLY` until implementation hash |
| elemental/physics catalogs | matching entry kind | source-specific |

Preserve legacy IDs and store the legacy source path/hash in provenance.

## Phase C — Compile, do not bypass

Map a v1.1 Build Recipe into `UniversalEntityRecipe`, then compile it back into
the strict `block_dna_adapt_001` Recipe/Graph. The round trip is a consumer
contract test. The strict target adds placement, revision and payload
fingerprint semantics.

## Phase D — Attach real artifacts

As each kit is authored:

1. attach the GLB/animation/material/runtime artifact hash;
2. move to `QUARANTINED`;
3. run asset and runtime QA;
4. move to `VERIFIED`;
5. require a separate promotion gate before `APPROVED`.

Never bulk-promote the 170 `DESIGN_READY` modules.

## Phase E — Deprecate legacy reads

Only after all consumers read the vNext registry and round-trip tests pass:

- freeze direct AI reads of legacy catalogs;
- retain the legacy package for reproducibility;
- make the content-addressed vNext registry the AI-facing source.


# DNA Adaptation Specification 001 — Tier 3 Offline Simulation

## Source-package gap

Tier 3 was documented but did not exist in the source package. The original
`simulation_lod_controller.gd` only assigned tiers by observer distance and no
file performed elapsed-time catch-up, receipt creation or validated persistence.

## D1 — Missing state fields

Added clamped `growth` and `health` fields to `AIdleElementalState` and the
state schema. This gives the adopted crop-growth solver durable output fields.

## D3 — Missing physical profiles

The pilot source module bindings are explicitly populated:

- `prop_farm_plot_2x2` → `phys_soil_loam_v1`
- `water_pond_small` → `phys_water_v1`

DNA aliases from the work order are mapped in `tier3_pilot_module_map.json`.
`cozy_fence_A` remains a static control fixture only and is not promoted into
the approved module catalog.

## Residency adaptation

Chunk residency decides Tier 3. Distance refines loaded entities only across
Tier 0–2. Provisional distances are `[12, 32, 96]` metres.

## Node adaptation

Tier switching now acts on AnimationPlayer rate, simulation update frequency
and visual variant selection. It no longer relies on RigidBody3D or
GPUParticles3D branches that did not match the intake build.

## Manifestation authority

No manifestation state machine was added or replaced. `activate_after_commit()`
remains subordinate and is expected to be called by the existing authoritative
manifestation/World Commit path.

## Persistence extension

The source package had no validated persistence implementation. This work adds
`AIdleValidatedStatePersistence` as an explicit existing-record-only gateway.
Tier 3 cannot create a missing entity through this gateway.

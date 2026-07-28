# WO-P1E-004 — World-DNA pilot integration + water material root cause

Authority: `PATCH_DRAFT` (Blue only) · State: `READY`
Issued by: `aidle-continuity-conductor` — **NOT Codex**
Authorized by: Human Product Lead, 2026-07-21 — "chọn vài module, vài vật tĩnh
và 2 vật động làm thử trước… nếu cái nào lỗi kêu grok chỉnh lại cho khớp với hệ
thống"

Source package: `E:/AIdle_openworld/world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.0`

## Governing principle — our system is the incumbent

The DNA package adapts to AIdle, **not the reverse**. Our module IDs
(`cozy_*_A`, `shared_*_A`) stay canonical. DNA bindings are mapped **to** them
through a mapping layer; nothing gets renamed to `nature_rock_soft` or
`water_pond_small`. If a DNA construct does not fit, adjust the DNA side and
record why.

## What is being adopted — and what is explicitly NOT

**Adopted in this pilot (state/simulation layer only):**

- `catalogs/element_catalog.json` — only the 5 elements named below
- `catalogs/physical_property_profiles.json` — only the 4 profiles named below
- `catalogs/simulation_lod_profiles.json` — `sim_lod_pc_balanced_v1` only
- The override hierarchy from `08_MIGRATION_FROM_MOBILE_TO_PC.md`:
  `Core Module → World Profile → PC Platform Profile → Physics Binding → Instance Parameters`
- Per-entity small state (`temperature`, `wetness`, `integrity`, `growth`) —
  **never** whole-world rigid-body snapshots, per `02_ELEMENTAL_PHYSICS_ARCHITECTURE.md`

**Explicitly NOT adopted, and this matters:**

- **`03_PC_GRAPHICS_STANDARD.md`** — Forward+ high/ultra, reflection probes,
  dense vegetation, lightmap workflow. This **conflicts with the Architecture
  Lock** ("2.5D Dreamy Low-Poly only for the vertical slice", "No free-form 3D
  world… on the MVP critical path"). Changing that lock requires an ADR from
  the Human Product Lead. **The pilot deliberately touches only the
  state/simulation layer, which has no rendering dependency — so no ADR is
  needed and none is being smuggled in.**
- The package's own `P1-PC Water Wheel Vertical Slice` roadmap. Our slice is
  P1E Cozy Starter Realm. Do not adopt a competing slice definition.
- The other 29 solvers, 43 reaction rules, 34 elements, 170 bindings. They stay
  `DESIGN_READY`, unimported.

Record honestly in the receipt that the package README states it has **never
been run** against Godot or Blender executables. Everything adopted here is
therefore first-execution code, not proven code.

## Task 1 — Water material root cause (do this first)

`cozy_pond_small_A` still renders wrong. History:

| Build | Pond RGB | Target `#8fd4e8` |
|---|---|---|
| P1E-003 W1 | `(218,209,195)` beige | `(143,212,232)` |
| P1E-003 correction | `(255,255,255)` pure white | `(143,212,232)` |

The correction changed the symptom, not the cause, and made it worse in one
respect: pure white is fully clipped and contributed to blown pixels rising
from 0.097 % to 2.718 %.

**Find the root cause. Do not tune the colour until you know where it is lost.**
Trace the material through: Blender material assignment → GLB export → package
hash → runtime intake parse → Godot material resolution. State in the receipt
which stage drops it.

This matters beyond the pond: if a material can exist in Blender and not
survive to Godot, **every future module is silently affected**, and Task 2
below binds elemental state to exactly this asset.

Also report why the previous material integrity check reported PASS while the
pond was `(255,255,255)`. A check that passes a wrong value is worse than no
check.

## Task 2 — Static pilot: 3 modules, elemental state only, no simulation

| Our module | DNA binding | Element | Property profile |
|---|---|---|---|
| `cozy_rock_small_A` | `nature_rock_soft` | `element_stone` | `phys_stone_soft_v1` |
| `cozy_path_stone_A` | `path_stone_straight` | `element_stone` | `phys_stone_hard_v1` |
| `cozy_fence_section_A` | (wood analogue) | `element_wood` | `phys_wood_soft_v1` |

These carry state fields but **do not simulate**. Purpose is to prove the
binding and serialization path without introducing behaviour.

Note the DNA bindings ship with `physical_profile_id: null` — the profiles are
unassigned. Populating them for these three is part of the task; record it as a
gap found in the source package.

## Task 3 — Dynamic pilot: exactly 2 modules that actually simulate

Chosen because together they form a minimal system network and demonstrate the
idle mechanic:

**1. `cozy_farm_plot_A`** ← `prop_farm_plot_2x2`, `element_soil`,
`phys_soil_loam_v1`. State: `wetness`, `growth`. Grows over time; growth rate
scales with wetness.

**2. `cozy_pond_small_A`** ← `water_pond_small`, `element_water`,
`phys_water_v1`. Acts as a wetness source for nearby soil.

Together: **pond → soil wetness → crop growth.** This is a scaled-down version
of the package's own water→irrigation→greenhouse concept, built from modules we
already have.

**Simulation LOD is the point of the pilot.** Use `sim_lod_pc_balanced_v1`.
Tier 3 time-delta simulation — growth advancing while the chunk is unloaded and
being reconstructed from state on return — is the idle-game core mechanic and
the single most valuable thing in this package. Prove it works.

## Non-negotiable boundaries

- **Preview stays non-solid and non-simulating.** The DNA package agrees:
  *"Preview chỉ có hologram, collision/reaction tắt, temporary ID. Commit mới
  gán stable ID, bật physics."* That is the same invariant `WO-G8-UX-001`
  verified. Do not regress it.
- State mutations reach durable storage **only** through the existing
  validated path. No new write route to canonical state.
- No `res://` promotion. `GAME_GLB_COUNT` stays 0.
- Save data references stable IDs and state, never renderer or LOD, per
  `08_MIGRATION`.

## Out of scope

Waves 2–4 of the art programme (tree/rock variants, fauna, toon shader) —
those resume after this. `P2E`–`P6E`. `Control-1B`. `Character-Foundry-1C`.
Approved catalog, World Commit changes. Red `F01`. `codex_directive.json`.

`ArtStyleManager` script error (`R-LOW-06`, raised to medium) — you flagged it
needs a separate allowlist. Propose that allowlist here; do not fix it silently.

## Writer allowlist

State your complete proposed allowlist and confirm before touching any file.

## Acceptance criteria

1. Pond renders within tolerance of `#8fd4e8`; **root cause stated**, not just
   the colour corrected.
2. Material integrity check reworked so it would have failed on
   `(255,255,255)`; demonstrate it catching a deliberately wrong value.
3. Three static modules carry element + property profile, serialized and
   surviving save/reload.
4. Two dynamic modules simulate; growth responds to wetness.
5. Tier 3 time-delta proven: advance simulated time with the chunk unloaded,
   reload, and show state advanced correctly.
6. Preview stages remain non-solid and non-simulating.
7. Exposure metrics stay inside art bible §8, including blown < 3 % — note it
   rose to 2.718 % and is now close to the limit.
8. No regression: 44 tests plus all existing smokes.

## Receipt requirements

Real durable refs. `accepted=false`, `self_accept=false`. Report measured luma
metrics with spatial distribution, material samples versus art bible hex, and
the Tier 3 time-delta evidence.

**Headed visual evidence mandatory.** Also state plainly which parts of the DNA
package you executed for the first time ever, since none of it has run before.

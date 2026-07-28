# World-DNA adaptation spec 001 — fitting the DNA layer to AIdle

Status: `REFERENCE` · Authored by: `aidle-continuity-conductor`, 2026-07-22
Source: `world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.0`
Companion to: `WO-P1E-004-DNA-PILOT-AND-WATER-FIX.md`

Written while Grok executes the pilot, from **reading the actual GDScript**, not
the documentation. Where the code and the docs disagree, this document reports
the code.

Governing rule, from the Human Product Lead: **our system is the incumbent.**
Where the DNA layer does not fit, the DNA side is adjusted and the reason
recorded. Our IDs, our validated write paths, our manifestation state machine
stay canonical.

---

## 1. What is genuinely good — adopt as-is

### `elemental_state.gd`

A small `Resource` with `temperature`, `wetness`, `integrity`, `charge`,
`pressure`, all `@export_range(0,1)` and clamped, plus `entity_id`,
`module_id`, `elements[]`, `physical_profile_id`, `simulation_lod_tier`.

Tiny, serializable, and it matches the architecture doc's promise of small
per-entity state rather than whole-world rigid-body snapshots. **Adopt the
shape directly** — it slots into our save model, which already references
stable IDs and state.

### `elemental_body_3d.gd` — preview/commit separation

```gdscript
func configure_preview(state): reaction_enabled = false; canonical_committed = false; _set_physics_enabled(false)
func activate_after_commit(): canonical_committed = true; reaction_enabled = true; _set_physics_enabled(true)
```

This is **our invariant, independently implemented**. It is the same rule
`WO-G8-UX-001` fixed and `WO-P1E-002` preserved: preview is non-solid, physics
only after commit. Strong signal the two systems share a worldview.

### `biological_solver.gd`

```gdscript
static func crop_growth(water, light, fertility, temperature_fit, delta_s) -> Dictionary:
    var limiting := minf(minf(water,light),minf(fertility,temperature_fit))
```

Liebig's law of the minimum, as a pure static function with no side effects and
no dependencies. Seven lines. Trivially testable, trivially adoptable. This is
the correct shape for a solver.

### `MOD_<id>` collection structure

`MOD_<id>/VISUAL/LOD0..LOD3; STATE_VARIANTS; SOCKETS; COLLISION_HINTS;
PHYSICS_HINTS; VFX_ANCHORS; EXPORT`

Our `04_BLENDER_LIBRARY_AND_TEMPLATE_STANDARD.md` already uses
`collection_name: MOD_cozy_house_small_A`. Theirs is a **sub-structure under the
same root** — an extension, not a conflict. Adopt.

### State variants as the bridge from state to visuals

Fixed variants `intact / damaged / broken / wet / frozen / burning / corroded /
restored`, selected deterministically from state. This is how elemental state
becomes visible **without needing new shaders** — high `wetness` on
`cozy_farm_plot_A` selects the `wet` variant. Elegant, and it means the state
layer pays visual dividends before wave 4's toon shader lands.

---

## 2. Real defects found in the DNA package — fix on the DNA side

These are not misfits with our system. They are internal inconsistencies in the
source package, found by reading the code.

### DEFECT D1 — `growth` and `health` have nowhere to live

`biological_solver.crop_growth()` returns `growth_delta` and `health_delta`.
`AIdleElementalState` has `temperature`, `wetness`, `integrity`, `charge`,
`pressure` — **no `growth`, no `health`**.

The architecture doc lists `growth` and `corrosion` and `pollution` as tracked
state. The shipped Resource does not have them. **The solver's output has
nowhere to be written.**

*Adaptation:* add `growth` and `health` as clamped 0–1 exports on our adapted
state resource. Record as a source-package gap, not our invention.

### DEFECT D2 — Tier 3 time-delta does not exist

`04_SIMULATION_LOD_STANDARD.md` promises *"Tier 3: time-delta simulation khi
chunk xa/chưa tải"*, and I assessed this as the single most valuable thing in
the package — it is the idle-game core mechanic.

Searched every `.gd` in the addon for time-delta or catch-up logic.
**`simulation_lod_controller.gd` only assigns tier numbers by distance.** There
is no code anywhere that advances state for elapsed time on chunk reload.

*Adaptation:* we must **implement Tier 3 ourselves**. It is a documented promise
with no implementation behind it. This is exactly the "documentation is not
implementation" trap `AGENTS.md` warns about, and it would have been easy to
assume it was there.

### DEFECT D3 — `physical_profile_id` is null across all bindings

`module_physics_bindings.json` assigns elements but leaves
`physical_profile_id: null` on every entry inspected, while
`physical_property_profiles.json` defines 16 profiles. The join between them was
never made.

*Adaptation:* populate for the five pilot modules; record the rest as an
unfinished source catalog.

---

## 3. Misfits with our system — adjust the DNA side

### MISFIT M1 — LOD tier distances are wrong for our world by an order of magnitude

`simulation_lod_controller.gd` defaults: `tier_distances = [48.0, 144.0, 384.0]`.

Our Starter Realm terrain is **32 m × 32 m**. The deep-research synthesis
proposes 64 m chunks. At a 48 m tier-0 radius, **our entire world is permanently
tier 0** and the LOD system never engages — we would carry all its complexity
and receive none of its benefit.

*Adaptation:* scale to our world. Proposed starting values `[12, 32, 96]` for a
32 m realm, to be tuned against profiling rather than frozen now.

### MISFIT M2 — tier switching targets node types we do not use

```gdscript
if child is RigidBody3D: child.freeze = tier >= 2
elif child is GPUParticles3D: child.emitting = tier <= 1
```

Our intake builds **`StaticBody3D`**, and we have no `GPUParticles3D` anywhere.
Both branches would be dead code for every module we own.

*Adaptation:* tier switching must act on what we actually have — animation
players (stagger/stop), state simulation frequency, and visual variant
selection. Not rigid bodies we do not create.

### MISFIT M3 — observer-distance polling vs chunk residency

Theirs: each body polls distance from one observer node every 0.25 s.
Ours (deep-research synthesis): chunk residency tiers — active 3×3, preloaded
5×5, proxy 7×7.

These are different axes. Per-body distance does not know about chunk loading,
which is precisely what Tier 3 needs to react to.

*Adaptation:* drive tier from **chunk residency first**, per-body distance
second. A body in an unloaded chunk is tier 3 regardless of its distance number.

### MISFIT M4 — two state machines would collide

`elemental_body_3d.gd` owns `configure_preview` / `activate_after_commit`.
`manifestation_instance.gd` already owns
`wireframe → hologram → materializing → complete` and its collision layers, and
that is **verified, human-confirmed work**.

*Adaptation:* our manifestation state machine stays authoritative. The elemental
body is **subordinate** — it reacts to our stage transitions, never drives them.
Wire `activate_after_commit()` as a *consequence* of reaching `complete`, never
as an independent path.

---

## 4. Module mapping — full kit, beyond the pilot

| Our module | DNA binding | Elements | Property profile |
|---|---|---|---|
| `cozy_house_small_A` | *(no direct binding)* | `element_wood` | `phys_wood_treated_v1` |
| `cozy_path_stone_A` | `path_stone_straight` | `element_stone` | `phys_stone_hard_v1` |
| `cozy_pond_small_A` | `water_pond_small` | `element_water` | `phys_water_v1` |
| `cozy_tree_landmark_A` | `nature_tree_landmark_large` | `element_wood`, `element_plant` | `phys_plant_soft_v1` |
| `cozy_farm_plot_A` | `prop_farm_plot_2x2` | `element_soil` | `phys_soil_loam_v1` |
| `shared_light_brush_station_A` | `prop_light_brush_station` | *(none in source)* | — |
| `cozy_greenhouse_preview_anchor_A` | *(preview only)* | — | — |
| `cozy_flower_cluster_A` | `nature_flower_cluster` | `element_plant` | `phys_plant_soft_v1` |
| `cozy_fence_section_A` | *(no direct binding)* | `element_wood` | `phys_wood_soft_v1` |
| `cozy_garden_lamp_A` | `prop_lamp_garden` | *(none in source)* | — |
| `cozy_rock_small_A` | `nature_rock_soft` | `element_stone`, `element_plant` | `phys_stone_soft_v1` |

**9 of 11 map cleanly.** Three source bindings carry no elements
(`prop_light_brush_station`, `prop_lamp_garden`) — an unfinished catalog, not a
conflict. House and fence need bindings authored on our side.

---

## 5. What must NOT be adopted

- **`03_PC_GRAPHICS_STANDARD.md`** — Forward+ high/ultra, reflection probes,
  dense vegetation, lightmap workflow. Conflicts with the Architecture Lock's
  "2.5D Dreamy Low-Poly only" and "no free-form 3D world on the MVP critical
  path". **Requires an ADR from the Human Product Lead.** The state layer has no
  rendering dependency, so the pilot avoids this entirely.
- The `P1-PC Water Wheel` slice — competes with our P1E Cozy Starter Realm.
- The remaining 29 elements, 43 reaction rules, ~165 bindings, and the thermal /
  structural / energy / fluid solvers. Keep `DESIGN_READY`, unimported.
- Wholesale copy of the addon. The package README states **none of it has ever
  been executed** against Godot or Blender. Adapt the minimum; treat every
  derived line as untrusted first-execution code.

---

## 6. Note on the water material bug

Checked whether the DNA package solves it. **It does not.**
`BLENDER_TO_GODOT_4_3_CONTRACT.md` says only that Blender "exports material
slots" and Godot "creates StaticBody3D…" — no mechanism, no glTF material
specification, nothing about how a material survives export.

Recording this plainly so nobody later assumes the DNA package covers the
Blender→Godot material path. It does not, and `WO-P1E-004` Task 1 still has to
find the root cause on its own.

---

## 7. Recommended sequence after the pilot

1. Pilot verifies (5 modules, 2 dynamic) → judge whether the state layer earns
   its complexity.
2. If yes: implement **Tier 3 time-delta ourselves** (D2) — the idle mechanic,
   and the thing with the highest value-to-effort ratio in this whole package.
3. Wire state → visual variants (`wet`, `restored`) so state pays visual
   dividends before wave 4.
4. Extend bindings to the remaining 6 kit modules.
5. Only then consider elements beyond the pilot five.

The graphics standard question stays open and unanswered until the Human
Product Lead decides the product direction.

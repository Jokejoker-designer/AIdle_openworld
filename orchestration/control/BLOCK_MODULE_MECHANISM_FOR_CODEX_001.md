# Block & Module composition — explainer for Codex

From: `aidle-continuity-conductor` (Claude, support role)
To: Codex, coordinating
Date: 2026-07-22
Source read directly (not the docs alone — the catalogs and example graphs):
`world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.1_Tier3/foundation_core/AIdle_Block_Module_Foundation_v1.0`

Purpose: give Codex the mental model of how blocks compose into modules and
worlds, and — the part that matters most — show that **the P1E-006 palette
variant work we just shipped is one slice of this system**, not a parallel
invention.

---

## The five layers, bottom to top

**1. Block** — the atomic brick. Example `block_cube_round`
(`catalogs/module_catalog.json`):

```
domain: GEOMETRY   category: PRIMITIVE
world_profiles: [shared, cozy_cyber_pixel, tiny_diorama, solarpunk_haven,
                 arcane_clockwork, spirit_valley, surrealism_canvas, oceanpunk_abyss]
socket_inputs:  [snap_grid]
socket_outputs: [snap_grid]
material_slots: [body, accent]
performance_class: XS   collision_policy: CONVEX   lod_policy: AUTO_3_LEVEL
```

A block declares **where it can connect** (sockets), **which worlds it belongs
to** (world_profiles), and **which material slots it exposes**. Note that one
block already lists all 7 world profiles — a single mesh is meant to serve every
world, recoloured per profile. That is the foundation's own design, and it is
exactly what Option B needs.

**2. Socket** — the join. 40 socket types in `catalogs/socket_types.json`. A
block's `socket_outputs` connect to a compatible block's `socket_inputs`.
`catalogs/compatibility_matrix.json` decides which pairs are legal.
**Rule: snap sockets before free placement** (composition rule 2). Sockets are
how the system guarantees a door meets a wall and a path meets a plot, without
the AI choosing arbitrary coordinates.

**3. Module / cluster** — a named assembly of blocks. `cluster_cozy_house_small_A`
is a module; our `cozy_house_small_A` maps onto it. A module carries the same
metadata shape as a block but represents a finished, reusable unit.

**4. Build graph** — a whole scene as data
(`examples/04_cozy_village_build_graph.json`):

```
world_profile: cozy_cyber_pixel
nodes:  [ {house, cluster_cozy_house_small_A, pos}, {greenhouse...}, {farm...}, {nori...} ]
edges:  [ ... relationships ... ]
generators: [ gen_terrain_gentle_hills_v1(seed 123), gen_road_network_v1, gen_village_layout_v1 ]
world_rules: [ rule_day_night_v1, ... ]
```

`nodes` place modules, `edges` express relationships, `generators` fill the rest
**from a deterministic seed**, and `world_rules` apply behaviour. This is the
same shape as our Structured World Prompt — proposal as data, never as executed
code.

**5. World rules & behaviour** — config only. Composition rule 5: *"Behavior chỉ
là config, Godot thực thi."* Godot executes; the data never runs.

---

## The seven composition rules that constrain all of it

From `03_AI_BUILD_COMPOSITION_RULES.md`, and every one already matches an
invariant we enforce:

1. **World Profile chosen first** — this is exactly the ruling the Human Product
   Lead just made (world profile is the primary axis).
2. **Socket before free placement** — deterministic joins.
3. Skeleton must match animation set — relevant to art wave 3 fauna.
4. **Recolour via Material Theme ranges** — see the key insight below.
5. Behaviour is config, Godot executes — same as the elemental physics layer.
6. Complex graphs must be layered — HLOD/streaming.
7. Generators use a **deterministic seed** — same determinism requirement as
   Tier 3.
8. **Preview is not state** — our manifestation invariant, verified in
   WO-G8-UX-001.
9. Always performance-check.
10. **Missing module → Asset Request, never arbitrary code** — this IS our
    quarantine model.

---

## The key insight for Codex: P1E-006 is already this system

Composition rule 4 — *"Đổi màu qua Material Theme ranges"* — plus
`catalogs/material_themes.json` and `07_MATERIAL_COLOR_VARIATION_SYSTEM.md`,
define exactly what we just built as `world_profile_variant_selector.gd`:

- one mesh,
- `material_slots` (`body`, `accent`) recoloured per world profile,
- Cozy as the reference (`identity_register`), Surrealism as a `material_table`.

We did not invent a parallel mechanism. We implemented a slice of the Block &
Module Foundation's Material Theme system, on exactly the axis (world profile)
the foundation always intended. **This is a strong signal to adopt the block
grammar deliberately rather than re-deriving it piecemeal.**

Practical consequence for the roadmap: when P2E–P6E land, each new world profile
should extend the **material theme table**, not add code branches. The two
hardcoded dicts I flagged in `tier3_reconciliation_service.gd`
(`FARM_MODULES`, `POND_MODULES`) are the counter-example — they should become
catalog entries, because the foundation's whole point is that content lives in
catalogs and Godot only executes.

---

## What is NOT yet real — do not overtrust the docs

Every module in `module_catalog.json` reads `status: DESIGN_READY`. Per the
package README, none of the block/module runtime has been executed against Godot
or Blender. `socket_types.json` entries did not even parse cleanly into id/label
when I sampled them — the catalog is partly unpopulated, the same
`physical_profile_id: null` pattern seen in the elemental bindings.

So the **grammar** is sound and worth adopting; the **catalog data** is a
skeleton that needs filling as each world's kit is authored. Treat it as a
contract to build toward, not a library to import wholesale — the same posture
that kept the DNA pilot safe.

---

## One-paragraph version, if that is all there is time for

A block is a brick with declared sockets, world-profiles and material slots.
Sockets snap bricks together deterministically. A module is a named assembly of
bricks. A build graph places modules, wires relationships, and seeds generators
to fill the rest — all as data, never code. World profile is chosen first;
recolouring happens through material-theme ranges, which is precisely the
P1E-006 per-profile variant work we just verified. Missing pieces become Asset
Requests, never arbitrary code — the quarantine model. The grammar is solid; the
catalogs are `DESIGN_READY` skeletons to fill as kits land.

# WO-TOWN-GRID-IMPORT-001 — import the planned town cadastre into the game

Author: `aidle-continuity-conductor` (Claude), under Directive 99 (autonomous phase).
Human-directed: "thiết kế bản đồ thị trấn quy hoạch, chia ô cho từng vật thể, và
yêu cầu Grok đưa nó vào game." Class: Tier-1 town-layout wave (fits current realm).
Status: authorized to open as a MAF wave; **`accepted=false`, no self-accept**.

## Design input (read-only, do not edit)

- Plan: `orchestration/control/visual_reference/town_plan/TOWN_GRID_PLAN_V1.json`
  (50 named plots: 10 buildings + 30 props + 10 character spawns, on a 2-unit
  named grid within +/-12, content within +/-10 — fits the current starter realm).
- Visual: `orchestration/control/visual_reference/town_plan/TOWN_GRID_PLAN_V1.svg`
- Catalog: `orchestration/control/visual_reference/mockup_ssot_v2/MOCKUP_SSOT_V2.json`
  (+ its DESIGN_LOCK). Object ids in the plan are SSOT design ids.
- Coordinate convention matches the existing `game/resources/town/town_layout_10phase.json`
  ({x, y:0, z, rotation_deg}; x=east, z=north/depth, y=up).

## Goal

Put the PLANNED TOWN (the cadastre) into the game now, as a navigable layout of
**named plots**, so every future building/prop/character has a fixed home cell.
Grok fills each plot with the real authored object over time; the map itself
lands first.

## Exact scope (name exact files in the receipt; one writer per file)

**Blue write lease (narrow Godot override, delegated by Directive 99 Tier-1):**
- `game/resources/town/town_grid_plan_v1.json` — the imported plan resource
  (Grok produces it FROM the design plan; validate it round-trips).
- One town-loader script under `game/scripts/**` (name it exactly in the WO
  receipt, e.g. `game/scripts/modules/town/town_grid_loader.gd`) that reads the
  resource and, for each plot: draws the plot footprint + name label (cozy
  style), and instantiates the real object GLB **where a production GLB exists**,
  else an honest labeled placeholder marker at the plot anchor.
- Optional: wire the loader into the starter realm scene behind a flag; do NOT
  delete the existing `starter_realm_builder.gd` content — add, don't destroy.

**Forbidden:** editing `town_layout_10phase.json` in place (reconcile via the new
resource; note the prior file as superseded in a comment, do not silently
delete); any file outside the named set; Confirm-gate / manifestation-order
changes; promoting any not-yet-authored object to a real GLB (quarantine holds);
faking a GLB where only concept art exists — use an honest placeholder.

## Honesty rule (critical)

Only 10 cast + 10 modules currently have production GLBs (per SSOT honesty). For
plots whose object is still concept-art, place a **clearly-marked placeholder**
(footprint outline + name + "concept — not yet authored"), NOT a fake mesh and
NOT an idle-aliased stand-in. The map is complete; the objects fill in per wave.

## Acceptance criteria (QA, headed)

- The town loads: all 50 plots present at the exact plan coordinates/cells; a
  headed screenshot shows the gridded town within the current realm footprint.
- Real GLBs appear at their plots (at least Nori-7 + any authored modules);
  every unauthored plot shows an honest placeholder with its plot name.
- No object sits outside +/-12; no two building footprints overlap (matches the
  plan's validated cells).
- Zero new Godot errors; existing starter-realm play loop + build/manifestation
  invariants unregressed; art-style/world-profile recorded in evidence.
- The resource round-trips (loader re-reads it; plot ids/coords stable).

## MAF flow

Blue (produce resource + loader) → Red (findings-only audit: coords match plan,
no overlap, honest placeholders, lease clean) → QA (headed evidence of all
criteria) → Purple (VERIFY_ONLY, WAITING). Batch-accept by the Human. No
self-accept. `accepted=false` throughout.

## Later (per the user's intent)

As Grok authors each object GLB (quarantine → override → headed proof), it
replaces that plot's placeholder with the real object at the SAME named plot —
so the town fills in tidily, every object always in its own cell.

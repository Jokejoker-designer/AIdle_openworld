# Grok town-import prompt 001

Paste the block below into the Grok Desktop coordinator
(`019f7ffd-3995-71c0-aca1-51078e24a852`). It dispatches the town-cadastre import
as a Tier-1 wave under Directive 99.

---

```
TOWN CADASTRE IMPORT — put the planned town map into the game (Tier-1 wave)

The Human Product Lead planned a gridded cozy town: every building, prop, and
character has a fixed named plot on a 2-unit grid that fits the current starter
realm. Import the MAP now; you will fill each plot with the real object over time.

1. Read (read-only design input):
   - orchestration/control/visual_reference/town_plan/TOWN_GRID_PLAN_V1.json
     (50 named plots: 10 buildings + 30 props + 10 character spawns; coords in
     the same {x,y:0,z,rotation_deg} convention as
     game/resources/town/town_layout_10phase.json; all content within +/-10.)
   - orchestration/control/visual_reference/town_plan/TOWN_GRID_PLAN_V1.svg
   - orchestration/control/visual_reference/mockup_ssot_v2/MOCKUP_SSOT_V2.json (+ DESIGN_LOCK)
   - orchestration/work_orders/WO-TOWN-GRID-IMPORT-001.md (your work order)

2. Run the wave under Directive 99 (Tier-1, delegated narrow Godot override):
   - Blue: produce game/resources/town/town_grid_plan_v1.json (from the design
     plan; must round-trip) + a town loader script under game/scripts/** (name
     the EXACT file in the receipt) that, per plot, draws the footprint + name
     label and instantiates the real GLB where one exists, else an honest
     labeled placeholder. Name every game/** file you touch in the receipt; one
     writer per file; do NOT delete starter_realm_builder.gd content (add behind
     a flag); do NOT edit town_layout_10phase.json in place (note it superseded).
   - Red: findings-only — verify every plot's coords/cells match the plan, no
     building-footprint overlap, placeholders are honest (no fake GLB, no
     idle-alias), lease clean.
   - QA: headed evidence — town loads, all 50 plots at plan coordinates within
     the current realm, real GLBs at their plots + honest placeholders elsewhere,
     zero new Godot errors, play loop + manifestation invariants unregressed,
     art-style/world-profile recorded.
   - Purple: VERIFY_ONLY, WAITING. Batch-accept by the Human. No self-accept;
     accepted=false throughout.

3. HONESTY: only ~10 cast + 10 modules have production GLBs today. Every
   not-yet-authored plot MUST show a clearly-marked placeholder ("concept — not
   yet authored") with its plot name, never a fake mesh.

4. Escalate (do not proceed) if importing the map would require deleting existing
   realm content, changing the Confirm gate or manifestation order, or crossing
   any Red F01 hard stop.

5. Acknowledge with: the exact game/** files you will write, the live
   directive_id (99), and confirmation the map fits within +/-12 with no
   footprint overlap. Then run the wave.

After this lands: as you author each object GLB (quarantine -> narrow override ->
headed proof), replace that plot's placeholder with the real object at the SAME
named plot, so the town fills in tidily — every object always in its own cell.
```

# TOWN_PHASE_06 — water_edge

**Status:** `BLOCKED_UNTIL_PREV_PARITY_100`  
**District role:** Khu nước  
**Parity gate:** `MOCKUP_PARITY_100` — **không được dừng** khi còn lệch mockup.

## Bindings (SSOT mockup — exact IDs)

| Slot | ID | Name |
|------|-----|------|
| Character | `OA-RG-021` | Nereu-5 |
| Building | `cozy_well_house_A` | Nhà giếng |
| Prop 1 | `cozy_pond_small_A` | Ao nhỏ |
| Prop 2 | `cozy_water_pump_A` | Bơm nước |
| Prop 3 | `cozy_birdbath_A` | Bồn tắm chim |

## Mockup references

- Character art: `orchestration/control/visual_reference/mockup_ssot_v2/chars/char_06_nereu.jpg`
- Character video: `None`
- Building art: `orchestration/control/visual_reference/mockup_ssot_v2/buildings/bld_07_well.jpg`
- Prop arts: `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_pond.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_water_pump.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_birdbath.jpg`

## Animation contract

Clips required: `idle, walk, scan, happy, cancel`  
Motion class: `bob_small` · Signature: `sonar_pulse`  
Building ambient: `idle_static`  
Prop ambients: ripple, idle_static, ripple

## Town spawn (meters)

```json
{
  "character": {
    "x": -9.2,
    "y": 0,
    "z": 1.2,
    "rotation_deg": 45
  },
  "building": {
    "x": -11,
    "y": 0,
    "z": 0,
    "rotation_deg": 45
  },
  "props": [
    {
      "x": -12.6,
      "y": 0,
      "z": 1.6,
      "rotation_deg": 33
    },
    {
      "x": -9.8,
      "y": 0,
      "z": -1.6,
      "rotation_deg": 45
    },
    {
      "x": -12.0,
      "y": 0,
      "z": -1.2,
      "rotation_deg": 57
    }
  ]
}
```

## Subagent order (mandatory)

1. `mockup-parity-guardian` — lock target pixels/IDs  
2. `character-animation-designer` — GLB + real clips  
3. `building-module-designer` — building GLB  
4. `prop-set-designer` — 3 prop GLBs  
5. `town-layout-planner` — verify spacing / district  
6. `godot-runtime-integrator` — load + idle play in town  
7. `red-mockup-delta-reviewer` — findings only  
8. `purple-parity-gate` — MOCKUP_PARITY_100 verify only  

## Definition of Done (phase)

- [ ] Character loads and **idle plays** with required clip names  
- [ ] Building loads at spawn  
- [ ] All 3 props load at spawn  
- [ ] No AABB overlap with other accepted phases  
- [ ] Visual delta vs mockup = **0 fail criteria** (see `contracts/mockup_parity_100.schema.json`)  
- [ ] Receipt written under `receipts/TOWN_PHASE_06/`  
- [ ] **No self-accept** — Human ACCEPT required for product ship  

## Block rule

If previous phase is not `PARITY_100_VERIFIED` or `HUMAN_ACCEPTED`, this phase stays **BLOCKED**.

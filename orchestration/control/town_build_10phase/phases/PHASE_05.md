# TOWN_PHASE_05 — pollinator_farm

**Status:** `BLOCKED_UNTIL_PREV_PARITY_100`  
**District role:** Nông trại kính  
**Parity gate:** `MOCKUP_PARITY_100` — **không được dừng** khi còn lệch mockup.

## Bindings (SSOT mockup — exact IDs)

| Slot | ID | Name |
|------|-----|------|
| Character | `SPH-RH-011` | Kito Thụ Phấn |
| Building | `cozy_greenhouse_A` | Nhà kính |
| Prop 1 | `cozy_farm_plot_A` | Luống canh tác |
| Prop 2 | `cozy_crop_row_A` | Hàng cây trồng |
| Prop 3 | `cozy_scarecrow_A` | Bù nhìn |

## Mockup references

- Character art: `orchestration/control/visual_reference/mockup_ssot_v2/chars/char_05_kito.jpg`
- Character video: `orchestration/control/visual_reference/mockup_ssot_v2/anim/anim_kito_idle.mp4`
- Building art: `orchestration/control/visual_reference/mockup_ssot_v2/buildings/bld_02_greenhouse.jpg`
- Prop arts: `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_farm_plot.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_crop_row.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_scarecrow.jpg`

## Animation contract

Clips required: `idle, walk, scan, happy, cancel`  
Motion class: `bob_small` · Signature: `pollen_puff`  
Building ambient: `steam_rise`  
Prop ambients: idle_static, sway_small, sway_small

## Town spawn (meters)

```json
{
  "character": {
    "x": -7.4,
    "y": 0,
    "z": 8.2,
    "rotation_deg": 90
  },
  "building": {
    "x": -9,
    "y": 0,
    "z": 9,
    "rotation_deg": 90
  },
  "props": [
    {
      "x": -10.6,
      "y": 0,
      "z": 7.6,
      "rotation_deg": 78
    },
    {
      "x": -11.0,
      "y": 0,
      "z": 10.0,
      "rotation_deg": 90
    },
    {
      "x": -7.6,
      "y": 0,
      "z": 10.8,
      "rotation_deg": 102
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
- [ ] Receipt written under `receipts/TOWN_PHASE_05/`  
- [ ] **No self-accept** — Human ACCEPT required for product ship  

## Block rule

If previous phase is not `PARITY_100_VERIFIED` or `HUMAN_ACCEPTED`, this phase stays **BLOCKED**.

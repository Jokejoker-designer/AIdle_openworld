# TOWN_PHASE_01 — home_plot

**Status:** `PARITY_100_VERIFIED`  
**District role:** Nơi ở + lối vào  
**Parity gate:** `MOCKUP_PARITY_100` — **không được dừng** khi còn lệch mockup.

## Bindings (SSOT mockup — exact IDs)

| Slot | ID | Name |
|------|-----|------|
| Character | `CCP-RH-001` | Nori-7 |
| Building | `cozy_house_small_A` | Nhà nhỏ Cozy |
| Prop 1 | `cozy_path_stone_A` | Lối đá |
| Prop 2 | `cozy_garden_lamp_A` | Đèn vườn |
| Prop 3 | `cozy_mailbox_A` | Hộp thư |

## Mockup references

- Character art: `orchestration/control/visual_reference/mockup_ssot_v2/chars/char_01_nori7.jpg`
- Character video: `orchestration/control/visual_reference/mockup_ssot_v2/anim/anim_nori7_idle.mp4`
- Building art: `orchestration/control/visual_reference/mockup_ssot_v2/buildings/bld_01_house.jpg`
- Prop arts: `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_path_stone.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_garden_lamp.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_mailbox.jpg`

## Animation contract

Clips required: `idle, walk, scan, happy, cancel, turn_left, turn_right, build_place, build_place_hold, confirm`  
Motion class: `bob_small` · Signature: `sprout_sway + water_drip`  
Building ambient: `door_pulse`  
Prop ambients: idle_static, pulse, idle_static

## Town spawn (meters)

```json
{
  "character": {
    "x": 1.6,
    "y": 0,
    "z": 1.4,
    "rotation_deg": -35
  },
  "building": {
    "x": 0,
    "y": 0,
    "z": 0,
    "rotation_deg": -35
  },
  "props": [
    {
      "x": -1.4,
      "y": 0,
      "z": 1.6,
      "rotation_deg": -47
    },
    {
      "x": 1.2,
      "y": 0,
      "z": -1.1,
      "rotation_deg": -35
    },
    {
      "x": 0.9,
      "y": 0,
      "z": 1.8,
      "rotation_deg": -23
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
- [ ] Receipt written under `receipts/TOWN_PHASE_01/`  
- [ ] **No self-accept** — Human ACCEPT required for product ship  

## Block rule

If previous phase is not `PARITY_100_VERIFIED` or `HUMAN_ACCEPTED`, this phase stays **BLOCKED**.

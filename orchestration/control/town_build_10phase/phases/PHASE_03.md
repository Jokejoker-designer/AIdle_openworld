# TOWN_PHASE_03 — workshop_row

**Status:** `BLOCKED_UNTIL_PREV_PARITY_100`  
**District role:** Xưởng sửa chữa  
**Parity gate:** `MOCKUP_PARITY_100` — **không được dừng** khi còn lệch mockup.

## Bindings (SSOT mockup — exact IDs)

| Slot | ID | Name |
|------|-----|------|
| Character | `CCP-NW-003` | Bác Bắp |
| Building | `cozy_workshop_A` | Xưởng |
| Prop 1 | `cozy_tool_rack_A` | Giá dụng cụ |
| Prop 2 | `cozy_crate_small_A` | Thùng gỗ |
| Prop 3 | `cozy_barrel_A` | Thùng tròn |

## Mockup references

- Character art: `orchestration/control/visual_reference/mockup_ssot_v2/chars/char_03_bacbap.jpg`
- Character video: `orchestration/control/visual_reference/mockup_ssot_v2/anim/anim_bacbap_idle.mp4`
- Building art: `orchestration/control/visual_reference/mockup_ssot_v2/buildings/bld_04_workshop.jpg`
- Prop arts: `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_tool_rack.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_crate.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_barrel.jpg`

## Animation contract

Clips required: `idle, walk, scan, happy, cancel`  
Motion class: `bob` · Signature: `tool_tap`  
Building ambient: `steam_rise`  
Prop ambients: idle_static, idle_static, idle_static

## Town spawn (meters)

```json
{
  "character": {
    "x": 7.4,
    "y": 0,
    "z": 9.2,
    "rotation_deg": -90
  },
  "building": {
    "x": 9,
    "y": 0,
    "z": 9,
    "rotation_deg": -90
  },
  "props": [
    {
      "x": 10.6,
      "y": 0,
      "z": 7.8,
      "rotation_deg": -102
    },
    {
      "x": 11.0,
      "y": 0,
      "z": 9.8,
      "rotation_deg": -90
    },
    {
      "x": 7.6,
      "y": 0,
      "z": 10.6,
      "rotation_deg": -78
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
- [ ] Receipt written under `receipts/TOWN_PHASE_03/`  
- [ ] **No self-accept** — Human ACCEPT required for product ship  

## Block rule

If previous phase is not `PARITY_100_VERIFIED` or `HUMAN_ACCEPTED`, this phase stays **BLOCKED**.

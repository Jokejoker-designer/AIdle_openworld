# TOWN_PHASE_02 — market_square

**Status:** `BLOCKED_UNTIL_PREV_PARITY_100`  
**District role:** Quảng trường chợ  
**Parity gate:** `MOCKUP_PARITY_100` — **không được dừng** khi còn lệch mockup.

## Bindings (SSOT mockup — exact IDs)

| Slot | ID | Name |
|------|-----|------|
| Character | `CCP-NS-002` | Mây Mạch |
| Building | `cozy_market_stall_A` | Sạp chợ |
| Prop 1 | `cozy_bench_A` | Ghế dài |
| Prop 2 | `cozy_cart_A` | Xe kéo |
| Prop 3 | `cozy_signpost_A` | Biển chỉ đường |

## Mockup references

- Character art: `orchestration/control/visual_reference/mockup_ssot_v2/chars/char_02_maymach.jpg`
- Character video: `None`
- Building art: `orchestration/control/visual_reference/mockup_ssot_v2/buildings/bld_05_market.jpg`
- Prop arts: `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_bench.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_cart.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_signpost.jpg`

## Animation contract

Clips required: `idle, walk, scan, happy, cancel`  
Motion class: `bob` · Signature: `letter_flutter`  
Building ambient: `cloth_sway`  
Prop ambients: idle_static, idle_static, sway_small

## Town spawn (meters)

```json
{
  "character": {
    "x": 7.8,
    "y": 0,
    "z": 1.6,
    "rotation_deg": 0
  },
  "building": {
    "x": 9,
    "y": 0,
    "z": 0,
    "rotation_deg": 0
  },
  "props": [
    {
      "x": 7.2,
      "y": 0,
      "z": -1.4,
      "rotation_deg": -12
    },
    {
      "x": 10.4,
      "y": 0,
      "z": 1.2,
      "rotation_deg": 0
    },
    {
      "x": 9.0,
      "y": 0,
      "z": -2.2,
      "rotation_deg": 12
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
- [ ] Receipt written under `receipts/TOWN_PHASE_02/`  
- [ ] **No self-accept** — Human ACCEPT required for product ship  

## Block rule

If previous phase is not `PARITY_100_VERIFIED` or `HUMAN_ACCEPTED`, this phase stays **BLOCKED**.

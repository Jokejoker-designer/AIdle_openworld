# TOWN_PHASE_07 — craft_landmark

**Status:** `BLOCKED_UNTIL_PREV_PARITY_100`  
**District role:** Cối xay + rìa  
**Parity gate:** `MOCKUP_PARITY_100` — **không được dừng** khi còn lệch mockup.

## Bindings (SSOT mockup — exact IDs)

| Slot | ID | Name |
|------|-----|------|
| Character | `AC-CO-015` | Cinder-04 |
| Building | `cozy_windmill_A` | Cối xay gió |
| Prop 1 | `cozy_fence_section_A` | Hàng rào |
| Prop 2 | `cozy_grass_tuft_A` | Cỏ cụm |
| Prop 3 | `cozy_rock_cluster_A` | Cụm đá |

## Mockup references

- Character art: `orchestration/control/visual_reference/mockup_ssot_v2/chars/char_07_cinder.jpg`
- Character video: `None`
- Building art: `orchestration/control/visual_reference/mockup_ssot_v2/buildings/bld_06_windmill.jpg`
- Prop arts: `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_fence.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_grass_tuft.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_rock_cluster.jpg`

## Animation contract

Clips required: `idle, walk, scan, happy, cancel`  
Motion class: `bob` · Signature: `gear_spin`  
Building ambient: `spin`  
Prop ambients: idle_static, sway_small, idle_static

## Town spawn (meters)

```json
{
  "character": {
    "x": -7.2,
    "y": 0,
    "z": -7.8,
    "rotation_deg": 135
  },
  "building": {
    "x": -9,
    "y": 0,
    "z": -9,
    "rotation_deg": 135
  },
  "props": [
    {
      "x": -10.6,
      "y": 0,
      "z": -7.2,
      "rotation_deg": 123
    },
    {
      "x": -7.6,
      "y": 0,
      "z": -10.6,
      "rotation_deg": 135
    },
    {
      "x": -10.8,
      "y": 0,
      "z": -10.0,
      "rotation_deg": 147
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
- [ ] Receipt written under `receipts/TOWN_PHASE_07/`  
- [ ] **No self-accept** — Human ACCEPT required for product ship  

## Block rule

If previous phase is not `PARITY_100_VERIFIED` or `HUMAN_ACCEPTED`, this phase stays **BLOCKED**.

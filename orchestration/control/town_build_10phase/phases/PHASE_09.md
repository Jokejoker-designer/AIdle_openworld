# TOWN_PHASE_09 — spirit_bridge

**Status:** `BLOCKED_UNTIL_PREV_PARITY_100`  
**District role:** Cầu + đường tinh  
**Parity gate:** `MOCKUP_PARITY_100` — **không được dừng** khi còn lệch mockup.

## Bindings (SSOT mockup — exact IDs)

| Slot | ID | Name |
|------|-----|------|
| Character | `SV-NW-019` | Trúc Nhi |
| Building | `cozy_bridge_arch_A` | Cầu vòm |
| Prop 1 | `cozy_tree_willow_A` | Liễu rũ |
| Prop 2 | `cozy_tree_blossom_A` | Cây hoa |
| Prop 3 | `cozy_rock_mossy_A` | Đá rêu |

## Mockup references

- Character art: `orchestration/control/visual_reference/mockup_ssot_v2/chars/char_09_truc.jpg`
- Character video: `None`
- Building art: `orchestration/control/visual_reference/mockup_ssot_v2/buildings/bld_09_bridge.jpg`
- Prop arts: `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_tree_willow.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_tree_blossom.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_rock_mossy.jpg`

## Animation contract

Clips required: `idle, walk, scan, happy, cancel`  
Motion class: `bob` · Signature: `bamboo_sway`  
Building ambient: `idle_static`  
Prop ambients: sway, sway_small, idle_static

## Town spawn (meters)

```json
{
  "character": {
    "x": 7.6,
    "y": 0,
    "z": -7.4,
    "rotation_deg": -45
  },
  "building": {
    "x": 9,
    "y": 0,
    "z": -9,
    "rotation_deg": -45
  },
  "props": [
    {
      "x": 10.6,
      "y": 0,
      "z": -7.6,
      "rotation_deg": -57
    },
    {
      "x": 11.0,
      "y": 0,
      "z": -10.0,
      "rotation_deg": -45
    },
    {
      "x": 7.4,
      "y": 0,
      "z": -10.4,
      "rotation_deg": -33
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
- [ ] Receipt written under `receipts/TOWN_PHASE_09/`  
- [ ] **No self-accept** — Human ACCEPT required for product ship  

## Block rule

If previous phase is not `PARITY_100_VERIFIED` or `HUMAN_ACCEPTED`, this phase stays **BLOCKED**.

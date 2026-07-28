# TOWN_PHASE_10 — canopy_lookout

**Status:** `BLOCKED_UNTIL_PREV_PARITY_100`  
**District role:** Tháp + tán cây  
**Parity gate:** `MOCKUP_PARITY_100` — **không được dừng** khi còn lệch mockup.

## Bindings (SSOT mockup — exact IDs)

| Slot | ID | Name |
|------|-----|------|
| Character | `SPH-NG-009` | Luma Tán Lá |
| Building | `cozy_watchtower_A` | Tháp canh |
| Prop 1 | `cozy_tree_landmark_A` | Cây tròn mốc |
| Prop 2 | `cozy_tree_pine_A` | Cây thông |
| Prop 3 | `cozy_tree_cluster_A` | Cụm cây |

## Mockup references

- Character art: `orchestration/control/visual_reference/mockup_ssot_v2/chars/char_10_luma.jpg`
- Character video: `None`
- Building art: `orchestration/control/visual_reference/mockup_ssot_v2/buildings/bld_08_watchtower.jpg`
- Prop arts: `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_tree_landmark.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_tree_pine.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_tree_cluster.jpg`

## Animation contract

Clips required: `idle, walk, scan, happy, cancel`  
Motion class: `bob` · Signature: `leaf_sway`  
Building ambient: `flag_sway`  
Prop ambients: sway, sway, sway

## Town spawn (meters)

```json
{
  "character": {
    "x": 12.0,
    "y": 0,
    "z": 5.6,
    "rotation_deg": -20
  },
  "building": {
    "x": 13.5,
    "y": 0,
    "z": 4.5,
    "rotation_deg": -20
  },
  "props": [
    {
      "x": 13.5,
      "y": 0,
      "z": 2.6,
      "rotation_deg": -32
    },
    {
      "x": 15.0,
      "y": 0,
      "z": 4.8,
      "rotation_deg": -20
    },
    {
      "x": 15.2,
      "y": 0,
      "z": 2.8,
      "rotation_deg": -8
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
- [ ] Receipt written under `receipts/TOWN_PHASE_10/`  
- [ ] **No self-accept** — Human ACCEPT required for product ship  

## Block rule

If previous phase is not `PARITY_100_VERIFIED` or `HUMAN_ACCEPTED`, this phase stays **BLOCKED**.

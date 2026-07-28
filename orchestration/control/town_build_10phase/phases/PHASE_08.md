# TOWN_PHASE_08 — barn_yard

**Status:** `BLOCKED_UNTIL_PREV_PARITY_100`  
**District role:** Sân kho  
**Parity gate:** `MOCKUP_PARITY_100` — **không được dừng** khi còn lệch mockup.

## Bindings (SSOT mockup — exact IDs)

| Slot | ID | Name |
|------|-----|------|
| Character | `TD-CT-028` | Patch Gấu Nút |
| Building | `cozy_barn_small_A` | Nhà kho |
| Prop 1 | `cozy_tree_fruit_A` | Cây quả |
| Prop 2 | `cozy_rock_small_A` | Đá nhỏ |
| Prop 3 | `cozy_rock_stacked_A` | Đá xếp |

## Mockup references

- Character art: `orchestration/control/visual_reference/mockup_ssot_v2/chars/char_08_patch.jpg`
- Character video: `None`
- Building art: `orchestration/control/visual_reference/mockup_ssot_v2/buildings/bld_03_barn.jpg`
- Prop arts: `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_tree_fruit.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_rock_small.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_rock_stacked.jpg`

## Animation contract

Clips required: `idle, walk, scan, happy, cancel`  
Motion class: `breathe` · Signature: `stitch_wiggle`  
Building ambient: `idle_static`  
Prop ambients: sway, idle_static, idle_static

## Town spawn (meters)

```json
{
  "character": {
    "x": 1.4,
    "y": 0,
    "z": -9.4,
    "rotation_deg": 0
  },
  "building": {
    "x": 0,
    "y": 0,
    "z": -11,
    "rotation_deg": 0
  },
  "props": [
    {
      "x": -1.7,
      "y": 0,
      "z": -9.8,
      "rotation_deg": -12
    },
    {
      "x": 1.6,
      "y": 0,
      "z": -12.4,
      "rotation_deg": 0
    },
    {
      "x": -0.9,
      "y": 0,
      "z": -12.6,
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
- [ ] Receipt written under `receipts/TOWN_PHASE_08/`  
- [ ] **No self-accept** — Human ACCEPT required for product ship  

## Block rule

If previous phase is not `PARITY_100_VERIFIED` or `HUMAN_ACCEPTED`, this phase stays **BLOCKED**.

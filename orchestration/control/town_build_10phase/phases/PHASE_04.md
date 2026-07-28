# TOWN_PHASE_04 — creature_garden

**Status:** `BLOCKED_UNTIL_PREV_PARITY_100`  
**District role:** Vườn thư giãn  
**Parity gate:** `MOCKUP_PARITY_100` — **không được dừng** khi còn lệch mockup.

## Bindings (SSOT mockup — exact IDs)

| Slot | ID | Name |
|------|-----|------|
| Character | `CCP-CT-004` | Bụi Mơ |
| Building | `cozy_gazebo_A` | Chòi nghỉ |
| Prop 1 | `cozy_flower_cluster_A` | Cụm hoa |
| Prop 2 | `cozy_flower_bed_B` | Bồn hoa |
| Prop 3 | `cozy_bush_round_A` | Bụi tròn |

## Mockup references

- Character art: `orchestration/control/visual_reference/mockup_ssot_v2/chars/char_04_buimo.jpg`
- Character video: `orchestration/control/visual_reference/mockup_ssot_v2/anim/anim_buimo_idle.mp4`
- Building art: `orchestration/control/visual_reference/mockup_ssot_v2/buildings/bld_10_gazebo.jpg`
- Prop arts: `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_flower_cluster.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_flower_bed.jpg`, `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_bush_round.jpg`

## Animation contract

Clips required: `idle, walk, scan, happy, cancel`  
Motion class: `breathe` · Signature: `tail_flick`  
Building ambient: `idle_static`  
Prop ambients: sway_small, sway_small, sway_small

## Town spawn (meters)

```json
{
  "character": {
    "x": 1.7,
    "y": 0,
    "z": 9.8,
    "rotation_deg": 180
  },
  "building": {
    "x": 0,
    "y": 0,
    "z": 11,
    "rotation_deg": 180
  },
  "props": [
    {
      "x": -1.7,
      "y": 0,
      "z": 9.8,
      "rotation_deg": 168
    },
    {
      "x": 1.4,
      "y": 0,
      "z": 12.4,
      "rotation_deg": 180
    },
    {
      "x": -0.6,
      "y": 0,
      "z": 12.6,
      "rotation_deg": 192
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
- [ ] Receipt written under `receipts/TOWN_PHASE_04/`  
- [ ] **No self-accept** — Human ACCEPT required for product ship  

## Block rule

If previous phase is not `PARITY_100_VERIFIED` or `HUMAN_ACCEPTED`, this phase stays **BLOCKED**.

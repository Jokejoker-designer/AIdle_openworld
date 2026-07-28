# WO-TOWN-PHASE-01 — home_plot

**Status:** `IN_PROGRESS` (runtime usable; MOCKUP_PARITY_100 open)  
**Authority:** PATCH_DRAFT under lease · Purple VERIFY_ONLY · Human ACCEPT ship  
**Mockup:** MOCKUP_SSOT_V2  
**Gate:** `contracts/mockup_parity_100.schema.json`

## Bindings

| Slot | ID | Runtime now |
|------|-----|-------------|
| Character | `CCP-RH-001` Nori-7 | LOADED + idle play |
| Building | `cozy_house_small_A` | LOADED |
| Prop 1 | `cozy_path_stone_A` | LOADED |
| Prop 2 | `cozy_garden_lamp_A` | LOADED |
| Prop 3 | `cozy_mailbox_A` | **MISSING catalog GLB** |

## Smoke evidence (2026-07-23)

```
AIDLE_TOWN_PHASE_LAYOUT=RUNTIME_OK_PARITY_PENDING missing=1
missing: cozy_mailbox_A
chars=1 modules=3 idle=1
```

## Required rework (do not stop)

1. **Prop designer:** author `cozy_mailbox_A` GLB matching mockup art  
   `orchestration/control/visual_reference/mockup_ssot_v2/props/prop_mailbox.jpg`  
2. Promote into `game/assets/p1e_cozy/modules/cozy_mailbox_A.glb` + catalog row + SHA  
3. Re-run `res://tests/town_layout_10phase_smoke.gd` until `parity_ok=true`  
4. Red mockup delta → Purple PARITY_100 → Human accept  

## Subagents

Use prompts in `../agents/` in order listed in `PHASE_01.md`.

## Forbidden

- Claiming PARITY_100 while mailbox missing  
- Replacing mailbox with another prop without Human WO  
- Self-accept  

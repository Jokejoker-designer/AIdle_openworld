# WO-MOCKUP-CAST-PROPS-PRODUCTION-001

Directive: **99** · Human: *“thiết kế mockup được thì phải dựng y chang trong AIdle openworld”*  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852`  
Authority: `PATCH_DRAFT` · narrow Godot override for named paths  
Status: **DISPATCH** · `accepted=false` · no self-accept · not ship

## Goal

Promote MOCKUP_CAST_PROPS_001 from visual mockup to **runtime production assets**:

1. **10 characters** — rigged GLB + real AnimationPlayer clips under `game/assets/ucbv_001/cast/**`
2. **10 props** — P1E cozy library GLBs promoted into `game/assets/p1e_cozy/modules/**` + runtime catalog
3. **Runtime loader** — cast roster + generic presenter; prop kit mount for verification

## Product write lease (exact)

### Characters
- `game/assets/ucbv_001/cast/**` (per-character folders: export GLB, adapter snippets)
- `game/resources/ucbv_001/cast/cast_roster.json`
- `game/scripts/modules/ucbv_001/cast_presenter.gd`
- `game/scripts/modules/ucbv_001/cast_roster_loader.gd`
- `game/scripts/main/main.gd` (mount cast gallery only — no Confirm-gate change)
- `game/tests/mockup_cast_props_production_smoke.gd`

### Props
- `game/assets/p1e_cozy/modules/*.glb` (copy from Bridge library)
- `game/resources/p1e_cozy/module_catalog.json`
- `game/scripts/modules/p1e_cozy/p1e_module_kit.gd`

### Orchestration
- `orchestration/receipts/mockup_cast_props_production_001/**`
- `orchestration/logs/mockup_cast_props_production_001/**`
- Blender author: `orchestration/control/character_build/author_cast_batch_001.py`

## Forbidden

Ship/network, TIER3 horizons beyond this cast production slice, Confirm-gate change, free catalog invent IDs not in Foundry/P1E.

## Acceptance

- Headless smoke: 10 cast GLB load + idle clip, 10 prop GLB load
- Hashes recorded; Nori path unregressed
- `accepted=false` until Human batch

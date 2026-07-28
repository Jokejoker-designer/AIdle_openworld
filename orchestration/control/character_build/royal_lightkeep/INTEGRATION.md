# ROYAL LIGHTKEEP — AIdle Openworld Integration

**Date:** 2026-07-27  
**Module ID:** `royal_lightkeep_watchtower_barracks_01`  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`

## Status

| Flag | Value |
|------|--------|
| In AIdle Openworld game | **true** |
| GLB + P1E catalog | **true** |
| Main / PrivateReality landmark | **true** (full scale) |
| Town cadastre LOOKOUT.BLD | **true** (scale 0.14) |
| Smoke | `AIDLE_ROYAL_LIGHTKEEP_OPENWORLD=PASS` |
| `ASSET_FINAL_COMPLETE` | false (Human overlay optional) |

## Where it lives in-game

### 1) Full-scale landmark (24×19×38 m)
- **Parent:** `WorldRoot / PrivateReality / ManifestationHost / RoyalLightkeepLandmark`
- **Script:** `res://scripts/modules/p1e_cozy/royal_lightkeep_spawner.gd`
- **Scene:** `res://scenes/modules/p1e_cozy/royal_lightkeep_landmark.tscn`
- **Position:** `(-36, 0, 28)` · yaw `25°` (outside town ±12 ring)
- **Toggle:** `ENABLE_ROYAL_LIGHTKEEP_LANDMARK` in `main.gd` (default **true**)

### 2) Town LOOKOUT plot (cadastre)
- **Plan:** `game/resources/town/town_grid_plan_v1.json` → `LOOKOUT.BLD`
- **object_id:** `royal_lightkeep_watchtower_barracks_01`
- **Transform:** `(8, 0, -6)` · rot `150°` · **scale 0.14** (fits 4×4 unit pad)
- **District:** LOOKOUT — “Royal Lightkeep”
- Loaded by `town_grid_loader.gd` with all other buildings

### 3) Module catalog
- `game/resources/p1e_cozy/module_catalog.json`
- GLB: `res://assets/p1e_cozy/modules/royal_lightkeep_watchtower_barracks_01.glb`

## How to play / verify

```text
# Open Godot 4.3 project
E:\AIdle_openworld\tools\Godot_v4.3-stable_win64.exe --path E:\AIdle_openworld\game

# Or headless openworld smoke
Godot_v4.3-stable_win64_console.exe --path E:\AIdle_openworld\game --headless -s res://tests/royal_lightkeep_openworld_smoke.gd
# Expect: AIDLE_ROYAL_LIGHTKEEP_OPENWORLD=PASS
```

Run **main** (boot → main): Lightkeep appears as world landmark + LOOKOUT building in town grid.

## Materials (PASS 5)

Limestone · Dark foundation · Navy slate roof · Gold trim · Wood · Glass · Banner blue · Paving

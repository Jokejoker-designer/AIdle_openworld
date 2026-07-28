# PASS 1 — PRIMARY MASSING REPORT

**ASSET_ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  
**Name:** Watchtower + Barracks Complex — Royal Lightkeep  
**Date:** 2026-07-26  
**accepted:** false · **self_accept:** false

---

## A. PASS NAME

`PASS_1_PRIMARY_MASSING` (+ `PASS_1B_CAMERA_FIX`)

## B. OBJECTS CREATED

~83 mesh objects in collections:

| Collection | Role |
|------------|------|
| `WATCHTOWER_MAIN` | Base, shaft, observation, portal, banner mass, flag |
| `BARRACKS_LEFT_WING` | Main left mass, gable, roof link |
| `SERVICE_GATE_RIGHT_WING` | Right wing, gate arch tunnel |
| `LOWER_FORTIFIED_BASE` | Podium, walls ~6.5 m, terrace |
| `CENTRAL_COURTYARD` | Courtyard pad |
| `STAIRS` | Main front, left diagonal, rear steps |
| `ROOF_BLOCKOUT` | Tower pavilion, wing roofs, turret cones |
| `CORNER_TURRETS` | Barracks + gate turrets |
| `CAMERAS_MOCKUP_6` | CAM_01…CAM_06 |
| `SCALE_REF` | Human 1.8 m proxy |

## C. OBJECTS MODIFIED

- PASS 1B: camera locations/lens only (no massing edit).

## D. DIMENSIONS

| Metric | Value |
|--------|--------|
| Footprint | **24 m × 19 m** (target) |
| Tower height budget | **~38 m** (flag mast) |
| Wall height | **~6.5 m** |
| Unit | Metric, 1 BU = 1 m |
| Tower center (x,y) | (2.2, 1.5) — slight right of center, front-biased |
| Barracks center | (−5.5, 0.5) — left wing |
| Gate center | (7.5, −0.5) — right wing |

## E–J. SIX-VIEW MATCH (honest clay)

| View | Status | Notes |
|------|--------|--------|
| E. FRONT | **PARTIAL** | Tall tower + left wing + stairs readable; still boxy vs mockup Gothic roof cascade |
| F. REAR | **PARTIAL** | Single model continuity; rear gate/stair mass present; needs facade depth |
| G. LEFT | **PARTIAL** | Depth of tower + barracks; diagonal stair mass present |
| H. RIGHT | **PARTIAL** | Gate wing shorter than barracks; not mirrored wrong |
| I. FRONT 3/4 | **PARTIAL** | Hero angle shows tower+wings; camera pulled back after 1B |
| J. REAR 3/4 | **PARTIAL** | Same model; courtyard/link masses visible as blockout |

**Not claimed:** silhouette IoU ≥ mockup threshold. PASS 1 is **massing lock candidate**, not form-lock.

## K. REMAINING GAPS (before PASS 2)

1. Tower roof: mockup has multi-gable pavilion + pinnacles — blockout is simplified cone stack.  
2. Barracks front gable proportions need tighter mockup match.  
3. Courtyard is a pad, not carved void through solid.  
4. Wall openings (gate voids) not booleaned — solid masses only.  
5. No window/door recesses yet (PASS 2+).  
6. Stair landings coarse.  
7. Optional: orthographic cameras for pure silhouette check.

## L. RENDER PATHS

```
E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep\renders_pass1\
  CAM_01_FRONT.png
  CAM_02_REAR.png
  CAM_03_LEFT.png
  CAM_04_RIGHT.png
  CAM_05_FRONT_3Q.png
  CAM_06_REAR_3Q.png
```

Quarantine copies: `E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine\ROYAL_LIGHTKEEP_PASS1_MASSING\`

## M. BLEND FILE PATH

```
E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep\ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1.blend
```

Mockup staged:

```
...\royal_lightkeep\mockup_royal_lightkeep.jpg
```

## Materials

**CLAY ONLY** — neutral grey, no ornament materials, no foliage.

## Next

**Do not start PASS 2** until Human reviews six clay silhouettes and confirms massing direction.  
Proposed PASS 2: openings (portal boolean), courtyard carve, roof pitch refinement, wall thickness, stair cleanup — still no full trim/banners/stone detail.

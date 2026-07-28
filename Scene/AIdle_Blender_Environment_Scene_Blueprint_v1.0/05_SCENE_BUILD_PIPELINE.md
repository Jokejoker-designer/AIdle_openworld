# Environment Scene Build Pipeline

## Stage E0 — Intake

Grok tạo:

- World Profile
- target output class
- starter realm requirements
- module list
- terrain recipe
- spatial graph
- build plot
- camera target
- environmental parameters
- idempotency key and canonical validated request fingerprint
- expected Bridge revision and registry version
- server-bounded resource budget

## Stage E1 — Schema validation

Từ chối:

- unknown module
- unknown material
- absolute path
- arbitrary Python
- external download
- scale ngoài giới hạn
- unsupported terrain operation
- quá nhiều object/triangle/material

## Stage E2 — Scene template

Worker mở `starter_realm_empty_01.blend` bằng:

```text
--background
--factory-startup
--disable-autoexec
--python-exit-code
```

## Stage E3 — Terrain

Approved operations:

- create_flat_chunk
- create_diorama_block
- apply_height_profile
- cut_lake_basin
- cut_river_path
- create_island_shell
- create_ocean_floor_tiers

Không có sculpt AI tùy ý trong P0E/P1E.

## Stage E4 — Spatial assembly

Scene spec dùng graph:

```text
terrain center
→ onboarding path
→ starter house
→ build plot
→ landmark tree
→ pond
→ Light Brush station
```

Mỗi placement được kiểm tra:

- bounds
- overlap
- slope
- socket compatibility
- visibility
- camera obstruction
- build plot clearance

## Stage E5 — Nature

P0E dùng placement có kiểm soát, không procedural scatter không giới hạn.

```text
place_tree_cluster
place_bush_cluster
place_grass_patch
place_rock_cluster
```

Mật độ theo profile và seed, nhưng manifest phải deterministic.

## Stage E6 — Materials

Chỉ material IDs từ registry. Manifestation cyan, Companion aura và native world
emission phải tách thành material/VFX group khác nhau.

## Stage E7 — Lighting and preview camera

Blender lighting chỉ để:

- concept preview
- turnaround scene review
- World Genesis diorama render

Runtime day/night và gameplay lighting vẫn ở Godot.

## Stage E8 — LOD/HLOD

- Module LOD cho nhà/cây/prop.
- HLOD cluster cho cụm trang trí xa.
- Không gộp interactive object vào HLOD vĩnh viễn.
- Triangle budgets là giả thuyết cho đến khi Godot profiling xác nhận.

## Stage E9 — Export

```text
exports/modules/*.glb
exports/chunks/*.glb
scene_manifest.json
placement_manifest.json
material_manifest.json
validation.json
preview/*.png
```

## Stage E10 — Quarantine

Không copy trực tiếp sang `game/assets`.

## Two independent state dimensions

`content_phase` controls deterministic assembly order:

```text
TERRAIN -> PATH -> SHELTER -> NATURE -> INTERACTIVE -> LIGHTING -> LANDMARK
```

Godot's runtime manifestation state remains:

```text
wireframe -> hologram -> materializing -> complete
```

Blender may export `content_phase` and a stable `manifestation_order` integer.
It must not claim that a module is hologram/complete, activate collision, or
advance canonical world revision.

# Blender Library and Template Standard

## Library structure

```text
libraries/environment/
├── shared/
│   ├── terrain/
│   ├── paths/
│   ├── sockets/
│   ├── cameras/
│   └── manifestation/
├── cozy/
├── tiny_diorama/
├── solarpunk/
├── arcane/
├── spirit/
├── surrealism/
└── oceanpunk/
```

## Module record

```yaml
module_id: cozy_house_small_A
class: ARCHITECTURE
world_profiles: [cozy_cyber_pixel]
style_fit: NATIVE
blend_source: libraries/environment/cozy/architecture.blend
collection_name: MOD_cozy_house_small_A
dimensions_m: [6.0, 5.0, 4.5]
sockets:
  - SOCKET_DOOR_FRONT
  - SOCKET_PATH_FRONT
  - SOCKET_PROP_LEFT
materials:
  - cozy_wood_cream
  - cozy_roof_leaf
lod_policy: building_small_v1
collision_hint: simplified_mesh
```

## Required shared templates

1. `starter_realm_empty_01.blend`
2. `world_seed_diorama_01.blend`
3. `terrain_chunk_flat_01.blend`
4. `terrain_chunk_slope_01.blend`
5. `exterior_preview_stage_01.blend`
6. `manifestation_stage_01.blend`

## Linking policy

- Template và module library dùng Blender linking/append thông qua code cố định.
- Worker không mở arbitrary `.blend`.
- Library file phải có SHA-256 trong registry.
- Không dùng packed script hoặc auto-run handler.

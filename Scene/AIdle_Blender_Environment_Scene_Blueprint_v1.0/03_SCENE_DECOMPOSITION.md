# Scene Decomposition Standard

## Root collections

```text
AIDLE_ENV_ROOT
├── 00_REFERENCE
├── 10_TERRAIN
├── 20_ARCHITECTURE
├── 30_NATURE
├── 40_PROPS
├── 50_LANDMARKS
├── 60_INTERACTION_HINTS
├── 70_COLLISION_HINTS
├── 80_NAVIGATION_HINTS
├── 90_LIGHTING
├── 91_CAMERA_PREVIEW
├── 92_MANIFESTATION_PREVIEW
├── 95_LOD_HLOD
└── 99_EXPORT
```

## Spatial layers

### Terrain

- ground chunk
- slopes
- cliffs
- islands
- river/lake bed
- ocean floor
- cutaway diorama block

### Architecture

- shelter/house
- greenhouse
- workshop
- temple
- tower
- bridge
- rail
- bubble base
- portal frame

### Nature

- tree families
- bush families
- grass patches
- flowers
- bamboo
- kelp/coral
- rocks
- cloud masses

### Props

- bench
- lamp
- planter
- farming bed
- water tank
- turbine
- solar panel
- rune table
- lantern
- toy train

### Gameplay hints

Blender chỉ xuất metadata/hints:

```text
SOCKET_BUILD
SOCKET_PATH
SOCKET_DOOR
SOCKET_PROP
SOCKET_ELEVATION
NAV_AREA_HINT
INTERACTION_POINT
LANDMARK_FOCUS
CAMERA_OCCLUSION_VOLUME
```

Godot mới tạo runtime node thực.

## Chunk policy

Starter Realm MVP:

```text
1 center chunk
4 edge chunks
1 landmark cluster
1 build plot
1 onboarding path
```

Không xuất một mesh duy nhất cho cả scene. Terrain có thể là chunk, nhưng nhà,
cây, prop và landmark cần tách để culling, interaction và replacement.

## Coordinate policy

- Blender: Z-up.
- Unit scale: 1 Blender unit = 1 metre.
- Scene origin: center of Starter Realm.
- Approved rotation increments: registry-controlled.
- Transform phải applied trước export, trừ animation/controlled object.

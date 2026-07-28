# AIdle Blender Environment Scene Blueprint v1.1

## 1. Mục tiêu

Xây hệ thống để Grok có thể yêu cầu Blender tạo các **Starter Realm, diorama
preview, exterior modular kit và scene chunk** phù hợp AIdle, nhưng không được
tạo scene tùy ý rồi đưa thẳng vào game.

Đầu ra không phải một file `.blend` khổng lồ. Đầu ra là một package có cấu trúc:

```text
environment_scene_package/
├── scene_manifest.json
├── world_style_receipt.json
├── terrain/
├── architecture/
├── nature/
├── props/
├── landmarks/
├── lighting/
├── preview/
├── exports/
├── validation/
└── provenance/
```

## 2. Phân biệt Character Bridge và Environment Bridge

| Character Bridge | Environment Scene Bridge |
|---|---|
| Một entity chính | Nhiều asset và quan hệ không gian |
| Rig/animation | Terrain/chunk/placement/navigation |
| Collider đơn giản | Collision layers và walkable areas |
| LOD theo nhân vật | LOD + HLOD + culling groups |
| Một GLB chính | Nhiều GLB/module hoặc một scene package |
| Skeleton validation | Spatial/layout/occlusion validation |

Không nên gộp toàn bộ logic vào một worker duy nhất.

## 3. Nguyên tắc bất biến

1. Blender sản xuất asset và bố cục draft; Godot giữ runtime authority.
2. Grok không gửi Python, shell, absolute path hoặc URL tải asset.
3. Chỉ dùng template, module, material và operation có trong registry.
4. Scene phải được chia thành `Terrain`, `Architecture`, `Nature`, `Props`,
   `Landmarks`, `Lighting`, `NavigationHints`.
5. Preview không có ownership hoặc mutation canonical.
6. Collision chính thức và navigation bake xảy ra sau validation/commit ở Godot.
7. Generated mesh đi vào quarantine.
8. Camera 2.5D và silhouette readability là acceptance gate.
9. Mỗi world dùng cùng pipeline; khác nhau ở World Style Profile.
10. World N+1 không được tích hợp trước khi World N được ACCEPTED.
11. Content assembly phase không được dùng như runtime manifestation state.
12. Mọi scene job dùng cùng Bridge-wide single-worker lease và idempotency
    fingerprint do server kiểm soát.
13. `validation.json`, scene manifest, hashes và server-mediated job receipt là
    output bắt buộc; client không thể tắt evidence.

## 4. Hai loại job

### 4.1. Asset-kit job

Tạo module dùng lại:

- nhà modular
- mái
- cửa
- cầu
- cây
- đá
- hàng rào
- turbine
- lantern
- coral
- floating-island segment

### 4.2. Scene-assembly job

Lắp các module đã phê duyệt thành:

- World Genesis diorama
- Starter Realm
- landmark preview
- exterior test chunk
- manifestation demonstration scene

Asset-kit job có thể thực hiện trước. Scene-assembly job chỉ được dùng module đã
validated hoặc generated module đang ở quarantine với provenance rõ.

## 5. Output classes

```text
ENV_MODULE
ENV_CLUSTER
STARTER_REALM
WORLD_SEED_DIORAMA
LANDMARK
TERRAIN_CHUNK
BIOME_KIT
LIGHTING_RIG
PREVIEW_SCENE
```

## 6. Pipeline authority

```text
Player/Human brief
→ Grok World/Environment agents
→ Environment Scene Build Specification
→ Bridge schema validation
→ Registry validation
→ Blender headless assembly
→ Quarantine
→ Technical validation
→ Preview render
→ Godot intake test
→ Red findings
→ Purple verification
→ Codex/Human acceptance
→ Approved Environment Catalog
```

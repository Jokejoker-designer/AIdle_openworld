# AIdle Blender Environment Scene Blueprint v1.1

Status: `ARCHITECTURE FOUNDATION` · Updated: 2026-07-21

Đây là contract/design authority cho Environment Bridge, **không phải bằng
chứng rằng Environment Bridge hoặc Starter Realm đã được triển khai**.

Blueprint này mở rộng `AIdle Blender Bridge P0` từ probe/character asset sang
**scene ngoại cảnh modular 2.5D**.

## Kết luận kiến trúc

Blender không trở thành world runtime và không thay Godot.

- **Grok**: tạo `Environment Scene Build Specification`.
- **Blender Environment Bridge**: dựng terrain, modular architecture, nature,
  props, lighting rig, LOD/HLOD và export package trong quarantine.
- **Godot**: giữ gameplay, interaction, collision runtime, navigation bake,
  manifestation, persistence và World Commit.
- **AI output**: proposal/draft, không phải canonical world state.

## Bộ tài liệu

- `01_MASTER_BLUEPRINT.md`
- `02_SYSTEM_ARCHITECTURE.md`
- `03_SCENE_DECOMPOSITION.md`
- `04_BLENDER_LIBRARY_AND_TEMPLATE_STANDARD.md`
- `05_SCENE_BUILD_PIPELINE.md`
- `06_GODOT_INTAKE_AND_RUNTIME_BOUNDARY.md`
- `07_SECURITY_QUARANTINE_VALIDATION.md`
- `08_GROK_SUBAGENT_WORKFLOW.md`
- `09_P0_P6_IMPLEMENTATION_ROADMAP.md`
- `10_EXISTING_P0_EXTENSION_PLAN.md`
- `11_CURRENT_SYSTEM_ALIGNMENT_AND_GOVERNANCE.md`
- JSON Schemas, tool definitions, operation allowlist
- 7 World Profile environment specifications
- Cozy Starter Realm example build spec
- Work orders cho P0E và P1E

## Thứ tự world bị khóa

1. Cozy Cyber-Pixel
2. Tiny Diorama
3. Solarpunk Haven
4. Arcane Clockwork
5. Spirit Valley
6. Surrealism Canvas
7. Oceanpunk / Bioluminescent Abyss

Việc dựng library dùng chung có thể chuẩn bị trước; tích hợp world runtime vẫn
phải đi đúng gate của Scene Tracker.

## Trạng thái triển khai hiện tại

- Character Blender Bridge `B0-001`: `ACCEPTED` bằng machine gate độc lập.
- Environment Bridge `P0E`: `READY`, chưa có implementation acceptance.
- Cozy Starter Realm `P1E`: `BLOCKED` cho tới khi P0E được VERIFIED và Human
  Product Lead quyết định cổng G8.
- Runtime giữ Godot `4.3-stable`, 2.5D fixed-camera và Companion text-only.

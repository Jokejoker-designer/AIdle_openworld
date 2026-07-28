# AIdle Openworld — Giai đoạn (STAGES)

Repo monorepo được **đóng gói theo giai đoạn** để đọc/giao hàng gọn.  
**Mã nguồn chạy thật** vẫn nằm ở root (`game/`, `world_DNA/`, …) — STAGES chỉ là **bản đồ + gói tài liệu** theo phase.

| Stage | Tên | Nội dung chính (đường dẫn gốc) |
|-------|-----|--------------------------------|
| **00** | Blueprints & design SSOT | `AIdle_Openworld_Blueprint_v1.0/`, `v1.1/`, `DESIGN.md`, `AGENTS.md` |
| **01** | World DNA / Module foundation | `world_DNA/` |
| **02** | Control, contracts, standards | `Control/`, `contracts/`, `orchestration/contracts/` |
| **03** | Game runtime (Godot 4.3) | `game/` |
| **04** | Character Foundry & cast | `game_character/`, `game/assets/ucbv_001/` |
| **05** | Orchestration, mockup SSOT, build assets | `orchestration/` (work orders, visual_reference, character_build) |
| **06** | Integration & release | Lightkeep GLB + catalog + smokes; roadmap hoàn thiện |

Chi tiết từng stage: xem `STAGE_XX_*/README.md`.

## Roadmap gates (từ Blueprint v1.1)

G0 Foundation → G1 Contract lock → G2 2.5D shell → G3 Manifestation → G4 Persist → G5 Companion → G6 Multiplayer authority → G7 Art/perf → G8 Alpha → post-alpha (voxel, cities, marketplace…).

Nguồn: `AIdle_Openworld_Blueprint_v1.1/Docs/Development_Roadmap.md`.

## Chạy game nhanh

```bash
# Godot 4.3 (tải riêng; không commit binary)
godot --path game

# Smoke Lightkeep trong Openworld
godot --path game --headless -s res://tests/royal_lightkeep_openworld_smoke.gd
```

## License / public

Public research & product build of **AIdle Openworld**.  
Không commit secrets (`.env`, keys). Tools (Godot/Blender exe) không nằm trong repo.

# AIdle_openworld — Complete Pack (Manus AI, 08/08/2026)

Gói này chứa toàn bộ repo **AIdle_openworld** (bản tại 08/08/2026) cùng toàn bộ kết quả công việc đánh giá và hoàn thiện gameplay do Manus AI thực hiện. Nội dung gốc của repo không bị thay đổi cấu trúc; các file mới và sửa đổi được liệt kê dưới đây.

## 1. Các công việc đã thực hiện

| Hạng mục | File bàn giao |
|---|---|
| Báo cáo đánh giá hệ thống (chuyên gia trade engine) | `evaluation-docs/bao-cao-danh-gia-AIdle_openworld.md` |
| Đề xuất hoàn thiện hệ thống (Sprint 0–4) | `evaluation-docs/de-xuat-hoan-thien-AIdle_openworld.md` |
| Bản trò chơi hoàn thiện gameplay (8 module mới + 67 test pass) | `evaluation-docs/KEU_QUA_CHAY_GAME.md` |
| Thiết kế chi tiết gameplay (spec triển khai) | `GAMEPLAY_COMPLETION_DESIGN.md` |
| Tài liệu bản game hoàn thiện (hướng dẫn vận hành) | `BAN_GAME_HOAN_THIEN.md` |

## 2. File code mới (gameplay hoàn thiện)

Toàn bộ nằm trong `game/scripts/`:

| Đường dẫn | Vai trò |
|---|---|
| `modules/gameplay/game_economy.gd` | Resource ledger: balance check nguyên tử, undo, daily income, spirit |
| `modules/gameplay/game_quest_system.gd` | Quest FSM đầy đủ + goal tracking + reward grant |
| `modules/gameplay/game_relationship_meter.gd` | Relationship level, trait drift, mood |
| `modules/gameplay/game_day_night_weather.gd` | Day/night cycle + weather + EventBus events |
| `modules/gameplay/game_npc_interaction.gd` | Talk/pet/gift/quest NPC + cooldown + log |
| `modules/gameplay/game_day_journal.gd` | Nhật ký ngày append-only |
| `modules/gameplay/game_ui_overlay.gd` | HUD: tài nguyên/ngày/quest/quan hệ/tâm trạng |
| `modules/gameplay/game_play_session.gd` | Mount point + public API + starter quest |
| `tests/gameplay/game_logic_headless_test.gd` | 67 headless logic test (Godot 4.3 headless) |

`game/scripts/main/main.gd` được sửa 5 chỗ nhỏ: cờ `ENABLE_COZY_GAMEPLAY_LOOP`, cờ `DEMO_SCREENSHOT`, hook mount trong `_ready()`, hàm `_mount_cozy_gameplay_loop()`, và hàm `_take_demo_screenshot()`.

## 3. Cách chạy

1. Cài [Godot 4.3](https://godotengine.org/download), mở thư mục `game/` (chứa `project.godot`), bấm F5.
2. Trong game (console/debug):
   - `get_node("/root/Main/GamePlaySession").toggle_ui()` — bật HUD
   - `get_node("/root/Main/GamePlaySession").accept_quest("q_starter_garden")` — nhận quest đầu tiên
   - `get_node("/root/Main/GamePlaySession").advance_goal("q_starter_garden", "collect", "vegetable_bed", 3)` — hoàn thành quest (tự cộng thưởng)
   - `get_node("/root/Main/GamePlaySession").snapshot()` — xem toàn trạng thái
3. Headless QA: `godot --headless --path .` (in log boot đầy đủ).
4. Test: `godot --headless --path . -s res://scripts/tests/gameplay/game_logic_headless_test.gd` → PASS: 67 | FAIL: 0.
5. Python services: `python3 -m pytest services/` → 57 passed.

## 4. Cấu trúc gói

- `game/` — project Godot 4.3 (chứa toàn bộ thay đổi và module mới)
- `services/` — authority server + AGM gateway Python (không đổi)
- `orchestration/`, `contracts/`, `world_DNA/`, blueprint… — tài liệu thiết kế gốc của repo (không đổi)
- `evaluation-docs/` — 3 báo cáo kết quả của Manus AI

Ghi chú: thư mục cache Godot (`.godot/`, `.import/`) đã được loại khỏi gói; khi mở lần đầu, Godot sẽ tự import lại assets.

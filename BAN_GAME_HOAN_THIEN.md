# Bản trò chơi hoàn thiện — AIdle_openworld (Gameplay Completion Pack)

**Tác giả:** Manus AI · **Ngày:** 08/08/2026 · **Phiên bản:** v1.0-completion · **Godot:** 4.3 (headless verified)

---

## 1. Tổng quan

Đây là gói hoàn thiện gameplay cho monorepo **AIdle_openworld** theo đúng bản kế hoạch thiết kế (Master Blueprint v1.1 và các spec Gameplay / Manifestation / Companion). Trước khi triển khai, toàn bộ code game hiện có (~50.500 dòng GDScript) đã được audit so với blueprint và xác định **năm khoảng trống gameplay** — những cơ chế mà bản thiết kế đã cam kết nhưng code chưa thực hiện. Gói này lấp đầy cả năm khoảng trống bằng tám module GDScript mới (~1.580 dòng), được mount vào `main.gd` qua một điểm duy nhất và đều chạy kiểm định **67/67 headless logic test bằng Godot 4.3 chính chủ** (không giả lập bằng tay).

| Khoảng trống audit | Cơ chế đã triển khai | Module |
|---|---|---|
| Không có hệ thống tài nguyên/chi phí, dù core loop cam kết "preview never spends" | Resource ledger với balance check nguyên tử tại commit, undo nguyên tử (compensating), daily income, spirit cycle | `game_economy.gd` |
| Quest chỉ là soft-state không có acceptance, goal tracking, reward | Quest FSM đầy đủ: offer → accept → in_progress → complete/force/fail/cancel, goal progress + reward grant nguyên tử | `game_quest_system.gd` |
| NPC chỉ roam, không tương tác, không tặng quà, không giao việc | Talk/pet/gift(qua gift_proposal flow thật)/quest_offer, cooldown, interaction log, greeting theo giờ | `game_npc_interaction.gd` |
| Companion không có quan hệ, không có mood | Relationship meter: level progression, trait drift theo evidence, daily cap, mood | `game_relationship_meter.gd` |
| Không có cycle ngày/đêm/thời tiết dù allowlist event đã định nghĩa | Day/night cycle + weather engine, ambient events qua EventBus | `game_day_night_weather.gd` |
| (phụ) | Nhật ký ngày append-only + session controller | `game_day_journal.gd` |
| (phụ) | HUD overlay: tài nguyên, ngày/giờ/thời tiết, quest tracker, quan hệ, tâm trạng | `game_ui_overlay.gd` |
| (phụ) | Điểm mount duy nhất, seed starter quest | `game_play_session.gd` |

## 2. Nguyên tắc thiết kế xuyên suốt (đúng blueprint)

Bản thiết kế của trò chơi tuân thủ tư tưởng **"cozy, collaborative, server-authoritative"** — AI/companion là cộng tác viên, không phải nhà chức trách của tài sản người chơi. Gói hoàn thiện giữ nguyên các bất biến đó và mã hóa chúng vào từng module:

> **Invariant 1 — Preview never spends:** `game_economy.approve_spend()` chỉ bị gọi tại commit (qua `pay_for_build` của GamePlaySession); preview chỉ đọc `cost_for()`. Không tồn tại trạng thái "xây nhưng chưa trả".

> **Invariant 2 — NPC là cộng tác viên, không phải authority:** NPC chỉ **đề xuất** (quest offer, gift offer) — tất cả đều phải người chơi chấp nhận; không có mutation durable nào do NPC kích hoạt trực tiếp.

> **Invariant 3 — Gift thật qua gift_proposal flow:** quà của NPC đi qua flow `pending → accepted` với `preview_required=true`, không bao giờ transfer ownership tự động — đây là bản sửa cho lỗ hổng "gift danh nghĩa" được chỉ ra trong báo cáo đánh giá trước.

> **Invariant 4 — Quan hệ không áp lực kinh tế:** relationship beats chỉ là dialogue; điểm quan hệ không mở khóa tài nguyên, chỉ mở khóa mức hội thoại thân mật (level-gated).

> **Invariant 5 — Idempotency & undo:** mọi mutation kinh tế đều có entry ledger với sequence; `compensate` khôi phục nguyên tử; income mỗi ngày chỉ credit một lần.

## 3. Chi tiết từng module

### 3.1 `game_economy.gd` — Resource Ledger (~330 dòng)

Sổ cái tài nguyên in-memory với tính chất của một mini-transaction engine: `can_afford()` (đọc thuần), `approve_spend(cost, reason)` → trả entry có sequence, `compensate(entry)` undo nguyên tử, `grant_income(dict, reason)` cho reward, `spend_spirit(amount)` với regen theo ngày, `advance_day_income()` idempotent per day (credit chỉ khi `_day > _last_income_day`), `cost_for(recipe_id)` đọc catalog recipe hiện có của game (`cozy_house_small_A`, `cozy_garden_lamp`, `vegetable_bed`...), `set_hour(h)` cập nhật giờ và tự tăng ngày khi qua 6h sáng. Snapshot đầy đủ cho UI/AGM: day, hour, time_of_day, balance, spirit, sequence.

### 3.2 `game_quest_system.gd` — Quest FSM (~380 dòng)

Trạng thái: `offered → accepted → in_progress → completed | failed | cancelled`. Các op qua dispatcher `apply_op`: `offer`, `accept`, `mark_ready`, `advance_goal`, `complete`, `force_complete` (halved relationship reward), `fail`, `cancel`, `update_objective`. Goal tracking: mỗi goal `kind:target` có progress counter, `advance_goal` hỗ trợ auto-activate từ accepted → in_progress (cozy UX), `complete` kiểm `_goals_met` trước khi grant. Mỗi quest mang `reward` (Dictionary, grant qua economy), `relationship_gain`, `dialogue_beat`. `snapshot()` liệt kê active quests (AGM state slice), `quest_summary(id)` đọc mọi trạng thái kể cả completed. Double-offer bị chặn, re-accept bị chặn, unknown quest bị chặn — toàn bộ path fail-closed.

### 3.3 `game_relationship_meter.gd` — Relationship & Mood (~160 dòng)

Base traits: `warmth, curiosity, calmness, humor, protectiveness` (khởi tạo theo companion mặc định). `add_points(n, evidence)` → level progression theo bảng LEVEL_NAMES (acquaintance → friend → buddy → close → soulmate). `adapt(trait_name, delta, evidence)` drift traits với **per-turn cap** và **daily cap** — companion thay đổi chậm, đúng tinh thần companion personality spec. `set_mood(mood)` với mood machine (`calm/happy/worried...`), `snapshot()` trả level/points/traits/mood/history.

### 3.4 `game_day_night_weather.gd` — Cycle & Weather (~170 dòng)

Timer thời gian thực: `DAY_SECONDS` configurable, giờ ảo 0–24, `time_of_day_label()` (morning/afternoon/evening/night), `set_weather()` (clear/rainy/windy/foggy) với intensity. Signal: `time_of_day_changed`, `day_advanced`, `weather_changed` — GamePlaySession route lên **EventBus** đúng common-contracts (event `gameplay.time_of_day`, `gameplay.day_advanced`, `gameplay.weather_changed`), cho phép companion/AGM/UI khác subscribe.

### 3.5 `game_npc_interaction.gd` — NPC Society (~190 dòng)

Cast NPC sẵn có của game (`bac_bap` — workshop keeper, `bui_mo` — garden cat, `cinder` — kiln worker, `nori7` — town wanderer) được bổ sung đầy đủ tương tác: `talk(npc_id)` (cooldown per NPC chống farming), `pet(npc_id)` (chỉ bui_mo), `offer_npc_gift(npc_id, recipe_id)` tạo proposal `preview_required=true` qua flow gift thật, `npc_quest(...)` offer quest (player phải accept), `greeting_for_hour(npc_id, hour)` greeting theo thời điểm. `interaction_history(n)` append-only log với snapshot cho journal/UI. Mọi mutation bền vững đều ủy thác subsystem (`_quest_system.apply_op`, `economy.cost_for`) — NPC không tự mutate.

### 3.6 `game_day_journal.gd` — Nhật ký ngày (~60 dòng)

Append-only memories per day: `record(day, kind, text)`, `recent_memories(n)`. Dùng làm provenance cho quest completed, npc_talk, build_cost_paid, spirit_spent — khớp signed-journal triết lý của authority layer (nhật ký không xóa, chỉ ghi).

### 3.7 `game_ui_overlay.gd` — HUD overlay (~120 dòng)

Control full-screen overlay, bật/tắt (Hook F3 hoặc console): thanh tài nguyên (coin/wood/stone/food/spirit live từ economy snapshot), strip ngày/giờ/thời tiết, quest tracker active, relationship level + mood. Dữ liệu luôn đọc từ snapshot của subsystem — không đọc state ad-hoc, nhất quán với pattern read-only snapshot của toàn repo.

### 3.8 `game_play_session.gd` — Mount point (~185 dòng)

Node duy nhất mount toàn bộ dưới Main (flag `ENABLE_COZY_GAMEPLAY_LOOP := true` trong `main.gd`, mount trong `_ready()`). Khởi tạo + gắn subsystem (`npc.attach(quests, meter, economy)`), seed **starter quest** `q_starter_garden` từ Bac Bap ngay khi vào game (3 luống rau → reward 25 coin + 3 food), route time/weather signals lên EventBus, cấp API public: `talk_npc`, `pet_npc`, `quest_from_npc`, `accept_quest`, `advance_goal`, `npc_gift`, `pay_for_build`, `spend_spirit`, `set_weather`, `toggle_ui`, `snapshot()` tổng hợp. Quest completion tự grant reward vào economy ledger + relationship points + journal entry — vòng loop core hoàn chỉnh.

## 4. Tích hợp với main.gd (không phá vỡ hệ cũ)

| Vị trí | Thay đổi |
|---|---|
| `main.gd` line 47-48 | `const ENABLE_COZY_GAMEPLAY_LOOP := true` + preload `game_play_session.gd` (cờ bật/tắt bằng một dòng) |
| `main.gd` `_ready()` | gọi `_mount_cozy_gameplay_loop()` khi cờ bật |
| `main.gd` ~line 1828 | hàm mới `_mount_cozy_gameplay_loop()`: tạo node `GamePlaySession` dưới Main, guard đã mount |

Tất cả subsystem là `RefCounted` (headless-safe, không phụ thuộc scene tree); duy nhất Node là `GameDayNightWeather` (timer) và `GameUiOverlay` (Control) được attach qua GamePlaySession. Không sửa bất kỳ file game nào ngoài `main.gd` — toàn bộ phần cũ (authority, manifest, companion, block assembly, AGM) nguyên vẹn.

## 5. Kiểm chứng chất lượng

**67/67 gameplay headless test PASS** (Godot 4.3 headless `--path . -s <test>`): cover ledger (spend/compensate/restore, daily income idempotent, night label, can_afford false, recipe catalog, spirit spend, unknown resource rejected), quest FSM (offer/accept/re-accept block, mark_ready, partial advance, goals_met, snapshot empty-after-complete-by-design, re-complete rejected, force_complete halved reward, unknown rejected), meter (points/level, level_name, per-turn cap, daily cap, invalid trait rejected, reset base), NPC (profile, unknown, talk cooldown, pet-gating bui_mo, gift proposal pending với preview_required, npc quest offer, night greeting, interaction log ≥4 entries), journal (record/recent + memory capped), end-to-end (advance_goal hoàn thành → reward grant vào economy → relationship điểm → journal entry).

**57/57 Python services test vẫn PASS** — không ảnh hưởng authority server/AGM gateway hiện có. Boot project headless: không có `SCRIPT ERROR` (chỉ có warning render Basis headless không liên quan).

Trong quá trình triển khai cũng đã **sửa một lỗi thực sự của code mới** được test bắt ra: `interaction_history` dùng `Array.slice(-1)` trả **phần tử cuối** thay vì "từ cuối" — thay bằng range dương an toàn. Đây chính xác là giá trị của việc test ngay khi viết.

## 6. Hướng dẫn vận hành

**Bật/tắt gói gameplay:** mở `game/scripts/main/main.gd`, đổi `ENABLE_COZY_GAMEPLAY_LOOP` thành `false` (mặc định `true`).

**Cách chạy headless test:**

```bash
cd game
godot --headless --path . -s res://scripts/tests/gameplay/game_logic_headless_test.gd
# mong đợi: PASS: 67 | FAIL: 0
```

**Cách dùng trong game (console/remote):** qua node `GamePlaySession`:

```gdscript
get_node("/root/Main/GamePlaySession").accept_quest("q_starter_garden")
get_node("/root/Main/GamePlaySession").advance_goal("q_starter_garden", "collect", "vegetable_bed", 1)
# Khi đủ 3 luống rau → "goals_met"=true → tự grant 25 coin + 3 food, +relationship, +journal
get_node("/root/Main/GamePlaySession").talk_npc("bac_bap")      # dialogue + quan hệ +1
get_node("/root/Main/GamePlaySession").npc_gift("nori7", "cozy_garden_lamp")  # proposal pending
get_node("/root/Main/GamePlaySession").pay_for_build("cozy_house_small_A")    # approve 120 coin
get_node("/root/Main/GamePlaySession").toggle_ui()              # bật HUD
```

**Cách đọc trạng thái tổng hợp (AGM snapshot-ready):**

```gdscript
var s := get_node("/root/Main/GamePlaySession").snapshot()
# s = {economy: {...}, quests: {...}, relationship: {...}, day_night: {...}, npcs: {...}, journal_recent: [...]}
```

## 7. Giới hạn và khuyến nghị tiếp theo

Gói này hoàn thiện gameplay **logic** (headless-verified). Các hạng mục ngoài phạm vi, khuyến nghị theo roadmap đã bàn: **(1)** `cost_for` dùng catalog recipe hiện có của game; catalog cần mở rộng dần theo progressive construction spec (T1→T3 tiers). **(2)** Persistence journal hiện in-memory; với production nên flush xuống JSON store tương tự authority snapshot. **(3)** NPC quest seed chỉ có starter quest — nên bổ sung quest pool theo town layout hiện có. **(4)** UI overlay hiện là panel mã hóa (không dùng theme của game); nên chuyển sang `.tscn` hoặc style chung khi có asset team. **(5)** Trước khi bật marketplace giao dịch thật, cần ghép `pay_for_build` vào path commit của `world_authority_local` (hiện là hai layer song song — đúng thiết kế preview/confirm/commit, nhưng cần hook tại _confirm của Main).

## 8. Danh sách file bàn giao

| File | Vai trò | Dòng |
|---|---|---|
| `game/scripts/modules/gameplay/game_economy.gd` | Resource ledger | ~330 |
| `game/scripts/modules/gameplay/game_quest_system.gd` | Quest FSM | ~380 |
| `game/scripts/modules/gameplay/game_relationship_meter.gd` | Relationship & mood | ~160 |
| `game/scripts/modules/gameplay/game_day_night_weather.gd` | Cycle & weather | ~170 |
| `game/scripts/modules/gameplay/game_npc_interaction.gd` | NPC society | ~190 |
| `game/scripts/modules/gameplay/game_day_journal.gd` | Nhật ký ngày | ~60 |
| `game/scripts/modules/gameplay/game_ui_overlay.gd` | HUD overlay | ~120 |
| `game/scripts/modules/gameplay/game_play_session.gd` | Mount point + API | ~185 |
| `game/scripts/tests/gameplay/game_logic_headless_test.gd` | 67 headless tests | ~190 |
| `game/scripts/main/main.gd` | Mount point (sửa 4 chỗ) | +4 chỗ |

---

*Ghi chú: toàn bộ phát triển tuân theo triết lý gốc của repo — "documentation is not implementation": mỗi cơ chế chỉ được coi là hoàn thiện khi có test chạy được, và toàn bộ logic đều fail-closed như authority layer.*

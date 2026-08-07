# Thiết kế hoàn thiện gameplay — AIdle Openworld 2.5D Vertical Slice (v1.1-aligned)

Tài liệu thiết kế triển khai này bám sát Master Blueprint v1.1: core loop `Speak -> Interpret -> Structured Proposal -> Policy/Cost/Schema Validate -> Preview -> Human Confirm -> Progressive Manifestation -> Commit -> Observe`, experience pillars (conversation là công cụ sáng tạo chính; manifestation trực quan và khả hồi; mọi artifact có provenance; không gian cá nhân an toàn; AI surprise opt-in và không chi tiêu cho player) và system invariants (World Prompt là ngôn ngữ proposal duy nhất; thay đổi canonical là transactional, idempotent, revision-checked; preview không có hiệu ứng kinh tế/ownership; server authoritative; mọi action tốn kém/bạo lực/thương mại có HITL).

## Các module gameplay mới (thêm vào game/scripts/modules/gameplay/)

| Module | Vai trò | Blueprint rule thực thi |
|---|---|---|
| `game_economy.gd` | Resource ledger (coin, wood, stone, food, spirit) — earn/spend/cost-check | Core loop "Cost Validate"; preview không có hiệu ứng kinh tế; balance check nguyên tử cùng mutation |
| `game_quest_system.gd` | Quest FSM: offer → accepted → in_progress → complete/fail, goal conditions + rewards | AGM decision quest_operations; relationship beats không kinh tế |
| `game_relationship_meter.gd` | Relationship level với Companion/NPC, unlock dialogue beats | Companion personality §Relationship Context: level unlock dialogue, không economic pressure |
| `game_day_night_weather.gd` | Time-of-day cycle, weather stages, phát ambient events qua EventBus | Event Bus allowlist: ambient.weather_hint, ambient.time_of_day_hint |
| `game_npc_interaction.gd` | Talk/gift/quest với NPC (Bac Bap, Bui Mo, Cinder), tích hợp npc_town_roamer | H2 NPC society seed; companion là collaborator không phải authority trên tài sản player |
| `game_day_journal.gd` | Daily cycle summary: day log append-only (provenance), mood delta | Provenance: append-only lineage |

Toàn bộ là `RefCounted` + optional Node wrapper (headless-safe), không phá scene hiện có, mount tự động trong `main.gd`, tích hợp EventBus và world_authority_local. Test headless GDScript chạy bằng Godot 4.3 console binary trong sandbox.

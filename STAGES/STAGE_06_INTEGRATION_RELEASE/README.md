# STAGE 06 — Integration & Release Plan

## Đã tích hợp Openworld

| Item | Location |
|------|----------|
| GLB | `game/assets/p1e_cozy/modules/royal_lightkeep_watchtower_barracks_01.glb` |
| Catalog | `game/resources/p1e_cozy/module_catalog.json` |
| Spawner | `game/scripts/modules/p1e_cozy/royal_lightkeep_spawner.gd` |
| Main mount | `ENABLE_ROYAL_LIGHTKEEP_LANDMARK` in `main.gd` |
| Town LOOKOUT | `game/resources/town/town_grid_plan_v1.json` |
| Smokes | `game/tests/royal_lightkeep_*.gd` |

## Gameplay Completion Pack (Manus, 2026-08-08) — **đã merge**

Nguồn: `foLsQScwsAOzTVin/aidle-complete` — bản nâng cấp gameplay thật (8 module + 67 tests).

| Item | Location |
|------|----------|
| Economy / Quest / Relationship / DayNight / NPC / Journal / HUD / Session | `game/scripts/modules/gameplay/` |
| Headless tests | `game/scripts/tests/gameplay/game_logic_headless_test.gd` |
| Design | `GAMEPLAY_COMPLETION_DESIGN.md`, `BAN_GAME_HOAN_THIEN.md` |
| Evaluation | `evaluation-docs/` |
| Main flag | `ENABLE_COZY_GAMEPLAY_LOOP := true` |

## Kế hoạch hoàn thiện (public backlog)

### Ngắn hạn
1. Human overlay accept Lightkeep → `ASSET_FINAL_COMPLETE`
2. LOD / mesh merge (XL → L) cho runtime mobile budgets
3. Collision hull + navigation for landmark
4. Purple/acceptance report G8 refresh

### Trung hạn (post G8)
5. Voxel terrain (deferred)
6. Real-city hubs / multiplayer (G6 Nakama)
7. Marketplace / economy
8. TTS Companion (post-alpha)

### Chất lượng
9. Expand automated smoke matrix
10. Asset pipeline docs for contributors
11. CI: Godot headless smokes on push

## Release checklist

- [x] Public monorepo structure + STAGES map
- [x] Blueprints v1.0 + v1.1 in tree
- [x] Game runtime + DNA + Control
- [x] No tool binaries / secrets in git
- [ ] GitHub public remote + CI
- [ ] Human art FINAL on Lightkeep

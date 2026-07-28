# STAGE 03 — Game Runtime (Godot 4.3)

## Mục tiêu
Shell 2.5D playable: player, camera, world hierarchy, UI, town, modules.

## Thư mục nguồn

| Path | Mô tả |
|------|--------|
| `game/` | Godot project root |
| `game/project.godot` | Engine config |
| `game/scripts/main/main.gd` | Main playable shell |
| `game/scenes/` | Scenes |
| `game/assets/p1e_cozy/modules/` | Building/prop GLBs |
| `game/resources/p1e_cozy/module_catalog.json` | Runtime module registry |
| `game/resources/town/` | Town grid / street plans |
| `game/tests/` | Headless smokes |

## Chạy

```bash
godot --path game
godot --path game --headless -s res://tests/royal_lightkeep_openworld_smoke.gd
```

## Trạng thái
Alpha-path shell + town cadastre + landmark Lightkeep integrated.

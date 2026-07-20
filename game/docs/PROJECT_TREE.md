# Project tree (Agent-Core delivery)

```
E:\AIdle_openworld\game\
├── project.godot
├── icon.svg
├── .gitignore
├── README.md
├── autoload\
│   ├── event_bus.gd
│   ├── settings_manager.gd
│   ├── art_style_manager.gd
│   ├── provenance_logger.gd
│   ├── module_registry.gd
│   └── game_manager.gd
├── scripts\
│   ├── core\
│   │   ├── constants.gd
│   │   └── reality_space.gd
│   ├── player\
│   │   └── player_controller.gd
│   ├── camera\
│   │   └── cozy_camera.gd
│   ├── world\
│   │   └── world_root.gd
│   ├── main\
│   │   ├── boot.gd
│   │   └── main.gd
│   ├── ui\
│   │   ├── art_style_select.gd
│   │   ├── hud.gd
│   │   ├── debug_overlay.gd
│   │   ├── pause_menu.gd
│   │   └── settings_menu.gd
│   └── modules\
│       ├── interfaces\
│       │   ├── i_voxel_module.gd
│       │   ├── i_companion_module.gd
│       │   ├── i_executor_module.gd
│       │   ├── i_network_module.gd
│       │   └── i_schema_module.gd
│       └── stubs\
│           └── module_stub.gd
├── scenes\
│   ├── main\
│   │   ├── boot.tscn
│   │   └── main.tscn
│   ├── world\
│   │   └── world_root.tscn
│   ├── player\
│   │   └── player.tscn
│   ├── camera\
│   │   └── cozy_camera.tscn
│   └── ui\
│       ├── art_style_select.tscn
│       ├── hud.tscn
│       ├── debug_overlay.tscn
│       ├── pause_menu.tscn
│       └── settings_menu.tscn
├── resources\
│   ├── art_styles\
│   └── themes\
├── assets\
│   └── placeholders\
└── docs\
    ├── AGENT_INTEGRATION.md
    ├── BASE_CHECKLIST.md
    └── PROJECT_TREE.md
```

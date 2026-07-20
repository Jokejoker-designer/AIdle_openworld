# AIdle Openworld – Godot 4 Core

**Agent:** Agent-Core  
**Blueprint:** Master Blueprint v1.0  
**Engine:** Godot 4.3+ (GDScript, Forward Plus)

Base technical foundation: project layout, Reality Hierarchy, cozy player/camera, input/pause/debug/settings, autoloads, and clean mounts for all other agents.

## Open / run

1. Install [Godot 4.3+](https://godotengine.org/download) (standard build is enough).
2. Import project folder: `E:\AIdle_openworld\game`
3. Press **F5** (main scene = `scenes/main/boot.tscn`).

CLI:

```bash
godot4 --path E:\AIdle_openworld\game
```

## Controls

| Input | Action |
|-------|--------|
| WASD / Arrows | Move |
| Shift | Sprint |
| Q / R | Orbit camera 45° |
| Mouse wheel | Zoom |
| Esc | Pause |
| F3 | Debug overlay |

## Directory map

```
game/
├── project.godot
├── autoload/           # EventBus, GameManager, ArtStyle, Provenance, Settings, ModuleRegistry
├── scenes/
│   ├── main/           # boot, main
│   ├── world/          # WorldRoot hierarchy
│   ├── player/
│   ├── camera/
│   └── ui/             # art style, HUD, pause, settings, debug
├── scripts/
│   ├── core/           # constants, RealitySpace
│   ├── player|camera|world|ui|main/
│   └── modules/
│       ├── interfaces/ # contracts for other agents
│       └── stubs/      # temporary mounts
├── resources/
├── assets/
└── docs/
    ├── AGENT_INTEGRATION.md
    └── BASE_CHECKLIST.md
```

## Related blueprint docs

- `../AIdle_Openworld_Blueprint_v1.0/01_Master_Blueprint.md`
- `../AIdle_Openworld_Blueprint_v1.0/02_Visual_Concept_Pillars.md`
- `../AIdle_Openworld_Blueprint_v1.0/Interfaces/Common_Contracts.md`
- `../AIdle_Openworld_Blueprint_v1.0/Agents/Agent_01_Core.md`

## Next agents

See `docs/AGENT_INTEGRATION.md`. Suggested order: Schema → Voxel + Companion → Executor → Network → Asset → Persist.

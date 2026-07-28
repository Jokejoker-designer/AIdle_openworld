# AIdle Openworld

**Public monorepo** — game runtime (Godot 4.3), design blueprints, World DNA, Control contracts, Character Foundry, orchestration & landmark assets.

> Cozy Cyber-Pixel / Dreamy Low-Poly **2.5D** open world with Companion-led building, progressive manifestation, and modular P1E assets.

## Start here

| Doc | Path |
|-----|------|
| **Stages map (gói theo giai đoạn)** | [`STAGES/README.md`](STAGES/README.md) |
| Master blueprint v1.1 | [`AIdle_Openworld_Blueprint_v1.1/01_Master_Blueprint.md`](AIdle_Openworld_Blueprint_v1.1/01_Master_Blueprint.md) |
| Development roadmap | [`AIdle_Openworld_Blueprint_v1.1/Docs/Development_Roadmap.md`](AIdle_Openworld_Blueprint_v1.1/Docs/Development_Roadmap.md) |
| Design system | [`DESIGN.md`](DESIGN.md) |
| Agents | [`AGENTS.md`](AGENTS.md) |

## Repository layout

```
AIdle_openworld/
├── STAGES/                         # Gói đọc theo giai đoạn 00→06
├── AIdle_Openworld_Blueprint_v1.0/ # Blueprint v1
├── AIdle_Openworld_Blueprint_v1.1/ # Blueprint v1.1 + roadmap
├── world_DNA/                      # Module & elemental physics foundations
├── Control/                        # Control-1B contracts
├── contracts/                      # Shared contracts
├── game/                           # Godot 4.3 playable project
├── game_character/                 # Character Foundry sources
├── orchestration/                  # Work orders, mockup SSOT, asset builds
├── Scene/                          # Scene packages
├── services/                       # Supporting services
└── tools/                          # Local tools (binaries gitignored)
```

## Run the game

1. Install **Godot 4.3** (not committed).
2. Open folder `game/` as project.
3. Run main scene (`boot.tscn` → main).

```bash
godot --path game
# Landmark smoke
godot --path game --headless -s res://tests/royal_lightkeep_openworld_smoke.gd
```

## Highlights

- **Town cadastre** (50 plots) + street paths  
- **P1E cozy modules** (houses, props, **Royal Lightkeep** landmark)  
- **Companion / Control-1B** confirm flow  
- **Cast / Nori-7** presentation pipeline  
- **Blueprints + DNA** for multi-agent build  

## What is not in git

- Godot/Blender executables (`tools/*.exe`)
- `.env` secrets
- Blender BACKUP / intermediate PASS8 densify blends
- Local `.godot/` import cache

## License

Public product/research tree for AIdle Openworld.  
Add a formal `LICENSE` file if you require a specific open-source license.

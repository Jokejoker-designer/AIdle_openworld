# AIdle Openworld

[![Stars](https://img.shields.io/github/stars/Jokejoker-designer/AIdle_openworld?style=social)](https://github.com/Jokejoker-designer/AIdle_openworld/stargazers) [![Godot](https://img.shields.io/badge/Godot-4.3-blue)](https://godotengine.org/) [![License](https://img.shields.io/badge/license-UNLICENSE-lightgrey)](./LICENSE)

AIdle Openworld — blueprints, World DNA, Godot 4.3 runtime, orchestration & landmarks (staged 00-06).

This repository contains the Single Source of Truth (SSOT) blueprints and the Godot runtime scaffolding for AIdle: a cozy, conversation-driven creative world where a human and an AI Companion build persistent, reversible creations together.

Highlights
- Conversation-first creative loop: prompt → structured proposal → preview → confirm → manifest.
- Godot 4.3 based 2.5D runtime (fixed isometric camera for the MVP).
- Contracts and safety: JSON schema-based Structured World Prompt and server-authoritative World Commit flow.

Quick start
1. Prereqs
   - Godot Engine 4.3 (download from https://godotengine.org/)
   - Python 3.11+ (for orchestration scripts and tooling) and pip

2. Run the game (local preview)
   - Open Godot and import the `game/` project folder.
   - Set the main scene to `game/project/main.tscn` (or follow the in-project README if a different path).
   - Run the scene in the editor.

3. Developer tools
   - Many orchestration scripts live in `orchestration/` (Python). Install dependencies if a requirements file exists:
     ```bash
     python -m pip install -r orchestration/requirements.txt
     ```
   - See `AIdle_Openworld_Blueprint_v1.1/00_README.md` for the design read order and blueprint guidance.

Roadmap (high level)
- H1 (MVP): 2.5D Private Reality vertical slice — prompt → preview → confirm → manifest → commit (Playable).
- H2: Friends, NPC society, Shared District (server-authoritative social play).
- H3: Prompt Recipe marketplace & creator tools.
- H4+: Licensed hubs, orbital mechanics, and cross-space continuums (research).

Contributing
- See CONTRIBUTING.md for contributor setup, code style, and PR workflow.

Code of conduct
- We aim to be welcoming and inclusive. See CODE_OF_CONDUCT.md.

License
- This repo includes a placeholder license badge. If you have a preferred license, add it at the repository root (LICENSE).

Contact
- Project owner: Jokejoker-designer (@Jokejoker-designer)


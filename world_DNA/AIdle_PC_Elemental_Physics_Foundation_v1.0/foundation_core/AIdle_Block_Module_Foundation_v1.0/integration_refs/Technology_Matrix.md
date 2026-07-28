# Technology Matrix — evidence status 2026-07-20

## Foundation

- Godot 4 vanilla: client and 2.5D runtime; pin a tested minor version.
- Nakama: backend candidate pending the two-client authority POC.

## Conditional POC

- `godot_voxel`: MIT editable 3D terrain, not AIdle's construction/AI system.
  Multiplayer documentation is experimental and does not solve persistence,
  player authority or every terrain mode. Keep it off the 2.5D critical path.
- `Zylann/voxelgame`: MIT/incomplete Godot demo with very basic multiplayer;
  useful as a spike/reference, not a starter foundation.
- TripoSR/TRELLIS: asynchronous decorative-asset workers after conditioning.

## Reference only

- AI Town/Generative Agents: memory, planning and social simulation patterns.
- Veloren: Rust/GPL architecture research for world/network streaming.
- Luanti: C++/Lua/LGPL modding and large-world benchmark; not infinite and not a
  Godot module.
- Voyager: skill-library philosophy, never arbitrary code execution.

## Isolated research

- Matrix-Game and open-oasis: dream/video portals only; output is not collision,
  navigation, identity or authoritative state.
- Summer Engine: MIT agent layer/dev-tool experiment; desktop product is
  proprietary, so it is not a runtime foundation.

## License gates

Hunyuan3D-2, NobodyWho, local-llm-npc and every model checkpoint require a
separate code/model/data/output license record before use. “Open” is not treated
as equivalent to MIT.

Primary references include the official repositories/docs for
[Godot](https://github.com/godotengine/godot),
[godot_voxel](https://github.com/Zylann/godot_voxel),
[voxelgame](https://github.com/Zylann/voxelgame),
[Nakama](https://github.com/heroiclabs/nakama),
[Veloren](https://gitlab.com/veloren/veloren),
[Luanti](https://www.luanti.org/en/), and
[Summer Engine agent](https://github.com/SummerEngine/summer-engine-agent).


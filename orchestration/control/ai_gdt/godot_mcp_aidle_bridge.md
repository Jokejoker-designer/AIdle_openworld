# Godot-MCP ↔ AIdle bridge notes

Upstream: https://github.com/IvanMurzak/Godot-MCP  
Related: https://github.com/IvanMurzak/GameDev-MCP-Server  

## Why

AI-GDT lists **Godot-MCP** as the Godot-native agent bridge. AIdle agents currently use
**Godot CLI** (`tools/Godot_v4.3-stable_win64_console.exe --headless -s …`). MCP adds
editor-aware tools (scene tree, properties, runtime hooks) under an allowlist.

## Install (opt-in, Human HITL)

1. Use **Godot 4.3** (project pin) — verify plugin supports 4.3 before install.
2. Clone Godot-MCP into a **sidecar** folder (not inside `game/` unless WO names it):
   `E:/tools/Godot-MCP` (example).
3. Follow upstream README for C# / .NET requirements.
4. Point MCP client (Grok / Cursor / Claude) config at the local server.
5. **Do not** store API keys in the Godot project.

## AIdle allowlist (proposed)

| Op | Allowed | Lease |
|----|---------|-------|
| Run headless smoke script | Yes | QA evidence lease |
| Capture viewport PNG | Yes | evidence/** |
| Read scene tree | Yes | read-only |
| Place node under MockupCastGallery | Yes | named main.gd / scene lease |
| Call World Commit / mutate Persist | **No** | always |
| Push / publish / network | **No** | Red F01 |

## Fallback (default today)

If Godot-MCP is not installed, agents **must** keep using:

```text
E:\AIdle_openworld\tools\Godot_v4.3-stable_win64_console.exe --path E:\AIdle_openworld\game --headless -s res://tests/<smoke>.gd
```

This path is production-proven for cast/props/commercial smokes.

## Status

- Integration **documented + catalogued**
- Plugin **not auto-installed** (dependency install hard stop without Human)
- Next: Human authorizes install WO if desired

# Blender MCP ↔ Grok (AIdle)

Bridge: **Grok Build** → MCP server `blender-mcp` (ahujasid) → **Blender 5.2** socket addon.

Repo upstream: https://github.com/ahujasid/blender-mcp

## Already configured on this machine

| Piece | Path / value |
|-------|----------------|
| `uv` / `uvx` | `C:\Users\phant\.local\bin\uvx.exe` |
| Grok MCP config | `C:\Users\phant\.grok\config.toml` → `[mcp_servers.blender]` |
| Blender exe | `E:\blender.exe` (5.2.0 LTS) |
| Addon source | `E:\AIdle_openworld\tools\blender-mcp\addon.py` |
| Addon install script | `install_addon.py` (writes user addons + enables) |
| Socket | `localhost:9876` — **Port field in BlenderMCP must match** |
| Telemetry | `DISABLE_TELEMETRY=true` |

## One-time (if reinstall)

```powershell
# 1) Ensure uv on PATH
$env:Path = "C:\Users\phant\.local\bin;$env:Path"

# 2) Install / re-enable addon
& "E:\blender.exe" --background --python "E:\AIdle_openworld\tools\blender-mcp\install_addon.py"

# 3) Confirm Grok config has [mcp_servers.blender] (see config.toml)
```

Or in Blender GUI: **Edit → Preferences → Add-ons → Install** → pick `addon.py` → enable **Blender MCP**.

## Every session (required)

1. Open Blender (`E:\blender.exe`).
2. Open cast source if needed, e.g.  
   `E:\AIdle_openworld\game\assets\ucbv_001\cast\bui_mo\export\...` / cinder `.blend`.
3. **3D View** → press **N** (sidebar) → tab **BlenderMCP**.
4. Click **Connect** (server listens on port **9876**).
5. Start / restart **Grok** so MCP server spawns with config.
6. In Grok chat, ask Blender tasks (tools appear as `blender__*`).

**Only one MCP client** should own `blender-mcp` at a time (Grok *or* Claude/Cursor, not both).

## Smoke checklist (AIdle cast)

Ask Grok after Connect:

1. **Scene** — “List objects, armatures, and Action names in the open Blender file.”
2. **Walk** — “Does Action `walk` exist? How many keyframes on leg bones?”
3. **Zero scale** — “Find objects/bones with scale near 0; list them.”
4. **Export dry-run** — “Prepare glTF export settings for GLB with all actions; do not overwrite live game path unless I confirm.”
5. **Safe export** — “Export GLB to  
   `E:\AIdle_openworld\tools\blender-mcp\exports\<slug>_mcp_smoke.glb`  
   then stop.”

After a good export, install into live cast with the existing AIdle pipeline (copy + roster SHA + import clear) — **do not** point export straight at `game/assets/...` until SHA receipt is updated.

## AIdle-safe rules

- Prefer work on **copies** under `tools/blender-mcp/exports/`, not live `*_rigged.glb`.
- Save `.blend` before `execute_blender_code`.
- Game install still uses: copy GLB → update `cast_roster.json` SHA → clear `.godot/imported` → headless smoke.
- Telemetry off via env in Grok config.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Grok has no blender tools | Restart Grok after config.toml change; check `[mcp_servers.blender] enabled = true` |
| `Could not connect to Blender` | Blender open + **Connect** on BlenderMCP tab; port 9876 free |
| `uvx ENOENT` | PATH includes `C:\Users\phant\.local\bin` or use full path in config (already set) |
| Addon missing | Re-run `install_addon.py` or Install from Disk |
| Claude + Grok both hang | Stop one client — only one `uvx blender-mcp` |

## Helper scripts

| File | Role |
|------|------|
| `addon.py` | Upstream Blender addon |
| `install_addon.py` | Headless install + enable |
| `connect_check.py` | Optional: print if port 9876 is listening |
| `SMOKE_PROMPTS.md` | Copy-paste prompts for Grok |

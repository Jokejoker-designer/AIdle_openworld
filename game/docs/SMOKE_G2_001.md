# G2-001 Smoke — Pinned Godot 4.3 2.5D shell

## Binary (do not download; already in repo tools/)

- `tools/Godot_v4.3-stable_win64_console.exe` (headless/CI)
- `tools/Godot_v4.3-stable_win64.exe` (interactive window)

Project path: `game/` · features pin: `4.3` in `project.godot`.

## Headless smoke (acceptance)

From repo root (`E:\AIdle_openworld`):

```powershell
.\tools\Godot_v4.3-stable_win64_console.exe --path game --headless --quit-after 5
```

Expected:

- Exit code `0`
- No GDScript parse / compile errors
- Logs include GameManager boot and, after headless default style, Main fixed-angle + player ready lines
- Headless may print dummy renderer `mesh_get_surface_count` noise; non-fatal

Optional direct main scene:

```powershell
.\tools\Godot_v4.3-stable_win64_console.exe --path game --headless --quit-after 5 res://scenes/main/main.tscn
```

## Interactive playcheck

```powershell
.\tools\Godot_v4.3-stable_win64.exe --path game
```

1. First run: art style picker (headless auto-skips with default style, non-persisted).
2. WASD moves on ground plane; Shift sprints.
3. Camera stays three-quarter fixed pitch; Q/R = discrete 45° snaps only; wheel zoom.
4. No free mouse-look / FPS / continuous orbit.

## Camera contract (code)

- `game/scripts/camera/cozy_camera.gd` — `pitch_degrees` locked; `is_fixed_angle() == true`
- No `InputEventMouseMotion` look handling in shell camera/player scripts

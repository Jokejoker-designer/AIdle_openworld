# Base Project Readiness Checklist – Agent-Core

Use this before claiming Core complete and before other agents land modules.

## Project structure

- [x] Godot 4.x `project.godot` present
- [x] Modular folders: `autoload/`, `scenes/`, `scripts/`, `resources/`, `docs/`
- [x] Main scene chain: `boot.tscn` → art select (first run) → `main.tscn`
- [x] `.gitignore` for `.godot/` and user data

## Reality Hierarchy

- [x] `WorldRoot` with PrivateReality, SharedDistricts, DoppelgangerCities, Orbital, Exoplanets
- [x] Each space has `ManifestationHost` (empty for Agent-Voxel)
- [x] Each space has authority metadata (`RealitySpace`)
- [x] Hierarchy names match Master Blueprint (not renamed)

## Player / Camera / Input

- [x] Cozy third-person / soft isometric camera (`CozyCamera`)
- [x] Player `CharacterBody3D` with camera-relative WASD
- [x] Input map: move, sprint, interact, pause, debug, zoom, orbit
- [x] Pause menu (Esc) + resume/settings/quit
- [x] Debug overlay (F3)
- [x] Settings: volume, fullscreen, vsync, debug toggle

## Autoloads

- [x] `EventBus` – Common Contracts signals
- [x] `GameManager` – lifecycle / pause / space
- [x] `ArtStyleManager` – styles + persist `user://world_meta.cfg`
- [x] `ProvenanceLogger` – file + memory log
- [x] `SettingsManager` – `user://settings.cfg`
- [x] `ModuleRegistry` – mounts + register API

## Module attach points

- [x] ModuleMounts: Voxel, Companion, Executor, Network, Schema, Asset, Persist
- [x] Interface docs/scripts under `scripts/modules/interfaces/`
- [x] Stubs auto-mounted so registry is non-empty
- [x] Integration guide: `docs/AGENT_INTEGRATION.md`

## Art style

- [x] First-run Art Style select UI
- [x] Default: Cozy Cyber-Pixel / Dreamy Low-Poly
- [x] Persisted for subsequent boots
- [x] Environment ground/sky tint follows active style

## Progressive construction readiness

- [x] ManifestationHost nodes reserved per space
- [x] EventBus manifestation signals defined
- [x] No fake instant-spawn world content in Core

## Manual playtest (operator)

Run with Godot 4.3+ (Forward Plus):

```text
godot4 --path E:\AIdle_openworld\game
```

Verify:

1. [ ] First launch shows Art Direction picker
2. [ ] Confirm enters Private Reality with ground + soft sky
3. [ ] WASD moves player; Shift sprints; Q/R orbits camera; wheel zooms
4. [ ] Esc pause → Settings → Back → Resume
5. [ ] F3 toggles debug (FPS, art style, modules list)
6. [ ] Second launch skips art picker (style saved)
7. [ ] Scene tree shows full Reality Hierarchy + empty ManifestationHosts
8. [ ] No script errors in debugger

## Handoff status

| Item | Status |
|------|--------|
| Base runnable by design | YES |
| Hierarchy locked | YES |
| Module slots ready | YES |
| Godot binary on this machine | Check local install |
| Agent-Voxel integration | PENDING (slot ready) |
| Agent-Companion integration | PENDING (slot ready) |

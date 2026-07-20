# Purple VERIFY_ONLY review — G2-001

| Field | Value |
|---|---|
| Task | G2-001 — Create pinned Godot 4 2.5D shell |
| Reviewer | Purple / Devil's Advocate |
| Authority | VERIFY_ONLY (no product patches; no tasks.json ACCEPT) |
| Date | 2026-07-20 |
| Work order | `orchestration/work_orders/WO-G2-001.md` |
| Worker receipt | `orchestration/receipts/G2-001.json` |
| Prior Codex | `orchestration/reviews/CODEX_G2_001_REVIEW.md` (integration hold on G2-003 parse noise) |

## VERDICT

**ACCEPTED**

Independent Godot 4.3 tools smoke boots the shell with fixed-angle camera and
CharacterBody3D XZ locomotion. Prior Codex hold (companion parse errors) is
cleared in the live tree: boot registers `CompanionModule` without GDScript
parse/compile failures.

## Acceptance matrix

| Criterion | Result | Evidence |
|---|---|---|
| Godot 4.3 tools binary boots project | **PASS** | `tools/Godot_v4.3-stable_win64_console.exe --path game --headless --quit-after 5` → **exit 0**; log `Godot Engine v4.3.stable.official.77dcf97d8` |
| Fixed-angle isometric/three-quarter camera | **PASS** | `game/scripts/camera/cozy_camera.gd`: locked `pitch_degrees=42.0`; discrete 45° yaw snaps only; `is_fixed_angle() -> true`; no mouse-look / free orbit / FPS |
| Player moves on ground plane / 2.5D | **PASS** | `game/scripts/player/player_controller.gd`: `CharacterBody3D`, camera-relative **XZ** only, walk/sprint, soft gravity |
| No free 3D camera | **PASS** | Grep of `game/scripts/**`: no `InputEventMouseMotion` look; camera policy comments + code match ARCHITECTURE_LOCK |
| Smoke docs with local tools binary | **PASS** | `game/docs/SMOKE_G2_001.md` documents console/interactive paths |
| Receipt + no self-ACCEPT | **PASS** | `orchestration/receipts/G2-001.json` state `REVIEW_REQUESTED`, `self_accept: false` |

## Independent smoke (re-run)

```
tools\Godot_v4.3-stable_win64_console.exe --path game --headless --quit-after 5
→ EXIT=0
```

Stdout highlights observed:

- `[GameManager] AIdle Core 0.1.0-core booting…`
- `[Boot] Headless smoke → main with default art style.`
- `[WorldRoot] Hierarchy ready (Blueprint v1.0).`
- `[Main] Camera mode=fixed-angle 2.5D (pitch locked, no free orbit/FPS).`
- `[Main] Player ready: CharacterBody3D XZ locomotion on ground plane.`
- `[Main] Entered Private Reality | style=cozy_cyber_pixel`
- Companion upgrade also clean: `[ModuleStub] companion slot upgraded to CompanionModule (G2-003).`

Non-fatal headless dummy-renderer noise (does not fail acceptance):

- `ERROR: Parameter "m" is null` at `mesh_get_surface_count` (dummy storage) — exit code still 0; no GDScript parse/compile errors.

Also re-ran: `python scripts\validate_project.py` → `AIDLE_VALIDATION=PASS`.

## Code spot-checks

### Camera (`game/scripts/camera/cozy_camera.gd`)

- Pitch fixed via `@export var pitch_degrees: float = 42.0` (not player-driven).
- Yaw only via discrete action snaps when `allow_yaw_snaps`; continuous free orbit absent.
- `is_fixed_angle() -> true` acceptance helper present.
- Spherical offset + `look_at(pivot)` preserves three-quarter lock.

### Player (`game/scripts/player/player_controller.gd`)

- `CharacterBody3D` ground locomotion.
- Explicit XZ velocity update; no free-fly.
- Camera-relative basis via `get_yaw()`.

### Project pin

- `game/project.godot` `config/features=PackedStringArray("4.3", "Forward Plus")`
- Main scene: `res://scenes/main/boot.tscn`
- Local binary present: `tools/Godot_v4.3-stable_win64_console.exe` (no install required)

## Residual / non-blocking

1. Headless dummy mesh errors remain cosmetic.
2. Debug overlay copy still says `Q/R orbit` (`game/scripts/ui/debug_overlay.gd`) while policy is discrete snaps — wording only.
3. No interactive visual screenshot in receipt (worker correctly listed under `not_done`).
4. Manifestation module is **not** auto-upgraded on main boot (G2-002 scope); voxel slot still stub at shell boot — expected.

## Blockers

**None.**

## Control-plane note (conductor)

- Worker WO status: `REVIEW_REQUESTED`.
- Purple does **not** write `tasks.json` ACCEPT; conductor owns state transition after this review.
- Codex prior hold on companion parse is **superseded** by this re-run.

# Purple VERIFY_ONLY review — G2-002

| Field | Value |
|---|---|
| Task | G2-002 — Implement 2.5D manifestation renderer |
| Reviewer | Purple / Devil's Advocate |
| Authority | VERIFY_ONLY (no product patches; no tasks.json ACCEPT) |
| Date | 2026-07-20 |
| Work order | `orchestration/work_orders/WO-G2-002.md` |
| Worker receipt | `orchestration/receipts/G2-002.json` |

## VERDICT

**ACCEPTED**

Four ordered stages are enforced in pure stage code and instance/module pipeline.
Cancel/abort before complete disables collision and leaves no enabled collision
bodies. Headless smoke re-run: **PASS checks=8, exit 0**.

## Acceptance matrix

| Criterion | Result | Evidence |
|---|---|---|
| Four ordered stages | **PASS** | `ManifestationStages.ORDERED_STAGES = wireframe → hologram → materializing → complete`; monotonic `enforce_monotonic` / `can_advance` |
| Cancel leaves no durable collision | **PASS** | Preview stages `allows_durable_collision` false; `free_cleanup` / `cancel_manifestation` zeros layer + disables shape + frees; smoke asserts zero orphan collision |
| Reduced-motion / skip-animation flag-ready | **PASS** | `set_skip_animation(true)` + SettingsManager `gameplay/reduced_motion` / `gameplay/skip_manifestation_animation`; smoke exercises skip → immediate complete |
| Unit/smoke with receipt | **PASS** | Independent re-run of `manifestation_smoke.gd` → `AIDLE_MANIFESTATION_SMOKE=PASS checks=8` |
| REVIEW_REQUESTED only (no self-ACCEPT) | **PASS** | Receipt `self_accept: false`; WO status REVIEW_REQUESTED |

## Independent smoke (re-run)

```
tools\Godot_v4.3-stable_win64_console.exe --headless --path game -s res://scripts/modules/manifestation/manifestation_smoke.gd
→ EXIT=0
→ AIDLE_MANIFESTATION_SMOKE=PASS checks=8
```

Checks observed OK:

1. `ordered_stages_const`
2. `progress_mapping`
3. `monotonic_enforcement`
4. `collision_gate`
5. `instance_cancel_no_collision`
6. `instance_complete_has_collision`
7. `module_pipeline` (wireframe→hologram→materializing, cancel before complete, skip-animation path)
8. `interface_surface` (IManifestationModule + legacy IVoxelModule)

Non-fatal: dummy renderer `mesh_get_surface_count` null mesh; warnings for missing WorldRoot manifestation host in isolated `-s` smoke (fallback host used).

## Code spot-checks

### Stage machine — `game/scripts/modules/manifestation/manifestation_stages.gd`

- Schema-aligned order: wireframe / hologram / materializing / complete.
- Progress bands: 0 / 0.25 / 0.5 / 0.9+.
- `allows_durable_collision` **only** for `complete`.
- Regression clamp via `enforce_monotonic`.

### Instance — `manifestation_instance.gd`

- Preview meta `manifestation_preview`; collision layer 0 until complete.
- Complete enables `COLLISION_LAYER_MANIFESTATION` (bit 4).
- `free_cleanup` → mark cancelled, layer/mask 0, shape disabled, `queue_free`.

### Module — `manifestation_module.gd`

- `start_manifestation` / `update_construction_progress` / `finalize_manifestation` / `cancel_manifestation`.
- Skip path finalizes immediately with collision (intended for reduced motion).
- EventBus hooks documented in receipt design notes.

### Scope honesty

- Worker correctly lists **not** wired into main playable transaction (G3-001 owns integration).
- Placeholder `BoxMesh` only — acceptable for G2-002 (not G2-004 mesh library).
- No contracts edits; no voxel digging critical path.

## Residual / non-blocking

1. Main boot still mounts **voxel stub**, not ManifestationModule (G3 integrator path).
2. Headless mesh dummy errors are non-blocking.
3. `tasks.json` still shows G2-002 as `READY` while WO/receipt claim `REVIEW_REQUESTED` — control-plane lag for conductor; not a product defect.

## Blockers

**None.**

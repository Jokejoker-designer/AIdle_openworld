# WO-NORI7-REDESIGN-001 — Nori-7 visual redesign kickoff (+ 5 gardener clips)

Directive: **99** · Task: `NORI7-REDESIGN` · Residuals: **NORI7-V01**, **NORI7-ANIM-EXPRESS**
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852`
Authority: `PATCH_DRAFT` · TIER 1 · narrow Godot override for named files
Status: OPEN · `accepted=false` · no self-accept · Human visual accept is SEPARATE batch gate

## Goal

Resolve Human Finding 2: Nori-7 currently reads as a plain white/low-detail blob.
Keep identity (CCP-RH-001, 14-bone skel_small_biped_robot_v1, cozy-cyber-pixel,
cream `#fdf3e2` SSOT) but raise friendliness, multi-material readability, and
silhouette (sprout, tank, eyes, nozzle). Author the 5 deferred gardener clips
with **real keys** (never metadata/idle-alias):
`water`, `plant_seed`, `harvest`, `charge`, `low_energy`.

## Pipeline

1. Revise design/visual_spec notes for redesign wave (orchestration + game_character).
2. Offline Blender 5.2 LTS author (`E:/blender.exe`) → quarantine under
   `E:/AIdle_Blender_Bridge_P0/storage/generated_quarantine/NORI7_REDESIGN_V01/`.
3. Validate: 14 bones exact parents, skinned mesh, multi-material slots,
   required 10 clips + 5 gardener clips with real fcurves/durations.
4. Narrow Godot override: promote GLB + update hash bindings.
5. Headed dual-res proof (1280×720 + 868×517) idle/scan/happy + one gardener clip.

## Exact product write lease (named files only)

- `game/assets/ucbv_001/character/nori7/export/nori7_rigged.glb`
- `game/assets/ucbv_001/character/nori7/export/nori7_rigged.blend` (optional companion)
- `game/assets/ucbv_001/character/nori7/export/nori7_glb_validation.json`
- `game/assets/ucbv_001/character/nori7/export/nori7_bridge_job_manifest.json`
- `game/assets/ucbv_001/character/nori7/mesh/nori7_mesh_descriptor.json`
- `game/assets/ucbv_001/character/nori7/provenance.json` (if present hash fields)
- `game/assets/ucbv_001/character/nori7/package_manifest.json` (if hash fields)
- `game/resources/ucbv_001/character/nori7_animation_adapter.json`
- `game/scripts/modules/ucbv_001/ucbv_paths.gd` (expected sha256 only)
- `game_character/ucbv_001/nori7/visual_package/visual_spec.json` (redesign notes)

**Forbidden:** Confirm-gate, World Commit, catalog promotion outside Nori paths,
P2E-002, character-backbone program, DNA vNext execution, other characters.

## Design lock (do not invent)

- Palette SSOT: cream `#fdf3e2` / shade `#efe0c8` / leaf `#7fc98f` / eye glass
  `#a8dced` / socket `#3d3226` / wood `#c98a5e` — bible cream not recipe `#F7E9C6`.
- Silhouette: rounded teardrop robot helper, 2-heads-tall chibi, short biped.
- Materials: MAT_CozyCeramic, Leaf, Glass, Wood, Stone, Metal (no cyan on complete body).
- Skeleton: exact 14 bones from `ucbv_paths.gd` REQUIRED_BONES / BONE_PARENTS.
- Keep REQUIRED_ACTIONS (10) playable; add gardener clips as real keys.

## Acceptance criteria (machine — not Human visual)

- GLB sha256 updated and consistent across adapter + paths + validation.
- Bone hierarchy exact; skinned; multi-material (not single flat white).
- 15 clip names present with duration>0 and fcurve_count>0 for gardener five.
- Presenter `build_from_assets` PASS headless; zero ERROR in load path.
- Headed evidence PNGs at dual res; Purple may VERIFIED-with-residuals for
  Human visual batch — green smoke ≠ Human visual accept.

## MAF

Blue (author+promote) → Red → QA headed → Purple VERIFY_ONLY → **batch queue**.

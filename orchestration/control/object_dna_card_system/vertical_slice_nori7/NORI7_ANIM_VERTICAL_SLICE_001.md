# NORI7_ANIM_VERTICAL_SLICE_001 — Object DNA animation pilot on Nori-7

| Field | Value |
|-------|--------|
| Work order | `WO-OBJECT-DNA-NORI7-ANIM-VERTICAL-SLICE-001` |
| directive_id | **99** |
| Character | Nori-7 / `CCP-RH-001` |
| Skeleton family | `robot_biped_small_v1` (alias `skel_small_biped_robot_v1`) |
| Animation set | `anim_robot_gardener_v1` |
| `accepted` | **false** |
| `self_accept` | **false** |

## Goal

Implement the Object DNA / card-system **animation vertical slice** on the one real character that already has a rigged GLB — without inventing a second platform.

## What was already real (before this slice)

| Item | Evidence |
|------|----------|
| 14 bones | `game/assets/ucbv_001/character/nori7/skeleton/skel_small_biped_robot_v1.hierarchy.json` |
| 10 keyed core clips | mockup parity receipt + `nori7_animation_adapter.json` `required_actions_all` |
| Runtime presenter + AnimationTree path | `game/scripts/modules/ucbv_001/nori7_presenter.gd` |
| Deferred gardener clips (metadata only) | adapter `deferred_optional_gardener_clips` |

## What this slice does

1. **Design package** (this folder): card session L1–L5 filled for Nori; three animation packages; clip matrix; character recipe projection.
2. **Production:** Blender job `NORI7_GARDENER_CLIPS_V1` appends real keys for:
   - `water`, `plant_seed`, `harvest`, `charge`, `low_energy`
   - onto the **existing** mockup-parity mesh (no full mesh rebuild).
3. **Runtime contract:** extend `REQUIRED_ACTIONS` + state machine + adapter so Godot fail-closed expects 15 clips after export succeeds.

## Status after run (2026-07-24)

| Check | Result |
|-------|--------|
| GLB animation count | **15** re-keyed on mockup mesh (`NORI7_FULL_ANIM_V1`) |
| Gardener clips | water, plant_seed, harvest, charge, low_energy — **REAL_KEYS** |
| Core + build clips | idle…confirm re-keyed (non-root tracks pass Godot fail-closed) |
| GLB sha256 | `8259b0d3188bb6cc5c4778abee6bd6c97b6c135e1bef1b26f5dc0f1e8c0852aa` |
| Mesh rebuild | **false** (import mesh, re-key anim only) |
| Headed QA | **PASS** — `AIDLE_NORI7_ANIM_15CLIP_QA=PASS clips=15 captures=17` |
| Evidence | `orchestration/evidence/nori7_anim_15clip_001/*.png` |
| Receipt | `orchestration/receipts/nori7_anim_15clip_001/nori7_anim_15clip_qa_receipt.json` |
| UI gardener row | PlayableActionBar Row3 → Water/Plant/Harvest/Charge/Rest |
| Product accept | **false** (Human still required) |

## Animation packages (card level 4)

| Package ID | Clips | Role |
|------------|-------|------|
| `pkg_robot_core_v1` | idle, walk, scan, happy, cancel | Base robot life |
| `pkg_ucbv_build_v1` | turn_left, turn_right, build_place, build_place_hold, confirm | Block-assembly presentation |
| `pkg_gardener_v1` | water, plant_seed, harvest, charge, low_energy | Farm / energy |

## Authority

- Clips are **presentation only** — never World Commit.
- Product accept still **false** until Human + headed QA + mockup fidelity review.
- Vision lock §12 parity still applies to **visual mesh**; this slice primarily completes **motion inventory**.

## Files

| Path | Role |
|------|------|
| `nori7_card_session.json` | 5-level card session filled |
| `nori7_animation_packages.json` | Package definitions |
| `nori7_clip_matrix.json` | Real vs design-target matrix |
| `nori7_character_recipe_projection.json` | §15 projection |
| `../../character_build/author_nori7_gardener_clips_v1.py` | Offline author |
| `game/.../export/nori7_gardener_clips_v1_receipt.json` | Production receipt (after run) |

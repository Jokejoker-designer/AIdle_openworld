# Implementation handoff — next: C1 Character Production

## Read first (in order)

1. `orchestration/design/ucbv_001/style_lock/C0_visual_production_preflight.md`
2. `orchestration/design/ucbv_001/style_lock/C0_cream_reconciliation.json`
3. `orchestration/design/ucbv_001/character/nori7/C0_animation_contract_lock.md`
4. `orchestration/control/UCBV_ANIMATION_BLOCK_INTEGRATION_MAP_001.md`
5. `orchestration/design/ucbv_001/style_lock/U1_unified_style_lock.md`
6. `orchestration/design/ucbv_001/style_lock/DESIGN.md`
7. `orchestration/design/ucbv_001/style_lock/unified_palette_material_alias_table.json`
8. `orchestration/design/ucbv_001/character/nori7/DESIGN.md` + `modular_body_outfit_definition.json`
9. `orchestration/design/ucbv_001/character/nori7/technical/U4_character_rig_animation.md`
10. Foundry Nori-7 + `recipe_nori7_v1` (identity only; DNA cream alias remap)
11. WO: `orchestration/work_orders/WO-UCBV-001-STRICT-CORRECTION-002.md` §C1

## Token / palette / material constraints

- **Canonical cream:** COZY_ART_BIBLE `#fdf3e2` (+ shade `#efe0c8`) → `MAT_CozyCeramic`.
- **Canonical leaf joints:** `#7fc98f` → `MAT_CozyLeaf`.
- DNA `mat_cozy_cream_leaf_v1` / `#F7E9C6` / `#78B65B` = **alias documentation only**.
- Multi-value body mandatory: lit cream + shade + darker joints/panels/face — defeat nearly-white uncanny.
- Cyan `#3fd0e0`/`#8ff0ff` = restrained manifestation only.
- ≤3 palette groups; shared vocabulary → existing `MAT_*` only.

## Shape / rig constraints

- Silhouette family: `ucbv_cozy_rounded_readable_v1`
- Nori-7: teardrop, 2-heads-tall, short legs, sprout crown, rear tank, nozzle
- **14-bone hierarchy exact** (see C0 animation lock) — not `[root,body,head]`
- Rear-view readable features mandatory
- No world-grid snap language on character joints

## Animation constraints

- Tier3 `anim_robot_gardener_v1` = names/compatibility only
- C1 authors real keyed GLB actions: Layer A required + Layer B UCBV extension
  (`turn_left/right`, `build_place`, `build_place_hold`, `confirm`)
- `cozy_bouncy`, `root_motion=false`
- No idle aliases for missing required/optional clips
- Markers never mutate World Commit

## Asset / Bridge rules (C1)

- Offline **Blender Bridge only** — **no install**, no Godot version change
- Real skinned mesh + named materials + rig + full interaction clips inside GLB
- Descriptor / procedural SphereCapsule / pelvis-bob-only = **fail** for this correction
- Provenance: Bridge job/package hashes + style_lock_id + recipe_id + CCP-RH-001
- Log only to C1 leased log or OS temp outside repo — **no** `_tmp` helpers in orch/game
- Lease product: `game/assets/ucbv_001/character/nori7/**`,
  `game/resources/ucbv_001/character/**`,
  `orchestration/design/ucbv_001/character/nori7/**`
- Orch: `correction_002/C1_character_production_002.json` + matching log only

## Dual resolution

Proof at `1280×720` and `868×517` for C4; C1 still verifies silhouette/contrast
in authoring view against fixed three-quarter intent.

## First C1 artifact should prove

1. Non-empty `.glb` with skinned mesh and catalog-valid 14-bone rig
2. Named material slots: warm cream body (not flat white) + leaf joints + face
3. Distinct keyed actions for idle/walk/turn_left/turn_right/scan/build_place/
   build_place_hold/confirm/happy/cancel (optional gardener clips honest)
4. Adapter JSON declaring base Tier3 set + UCBV extension (no false Tier3 claims)
5. Bridge provenance hashes; no network shipping; no DNA rewrite

## Out of C1

- C2 InputMap / 28-module selector / delete mode / AnimationTree wiring
- Headed dual-res clean evidence (C4)
- P2E-002 AI Build Zone
- Self-accept / Purple ACCEPTED

## Authority

- Profile next: `aidle-worldgen-asset-art`
- Authority: `PATCH_DRAFT` within C1 exact lease only
- `accepted=false` / `self_accept=false`
- No grandchildren

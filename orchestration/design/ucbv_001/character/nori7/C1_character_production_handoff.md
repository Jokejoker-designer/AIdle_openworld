# C1 — Nori-7 Character Production Handoff

Wave: `C1R_MESH_WEIGHT_CORRECTION` (prior C1 production + Directive-85 weight fix)  
Directive: **85** (supersedes 84 production for mesh validity)  
Child: `019f8c18-933b-7d21-9ecd-bcdda4023cf8`  
Prior C1 (rejected as C2 input, immutable): `019f8c08-d346-7250-b834-1887b51713c6`  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852`  
Profile: `aidle-worldgen-asset-art`  
Authority: `PATCH_DRAFT` · `accepted=false` · `self_accept=false`

## Delivered

| Artifact | Path |
|---|---|
| Production GLB (skinned + 10 actions) | `game/assets/ucbv_001/character/nori7/export/nori7_rigged.glb` |
| Source blend | `game/assets/ucbv_001/character/nori7/export/nori7_rigged.blend` |
| Bridge job manifest | `game/assets/ucbv_001/character/nori7/export/nori7_bridge_job_manifest.json` |
| GLB validation | `game/assets/ucbv_001/character/nori7/export/nori7_glb_validation.json` |
| Animation adapter | `game/resources/ucbv_001/character/nori7_animation_adapter.json` |

## Identity binding

- Character: **Nori-7 / CCP-RH-001**
- Recipe: `recipe_nori7_v1`
- Skeleton: `skel_small_biped_robot_v1` (exact 14 bones, parents match production hierarchy)
- Base set id (names only): `anim_robot_gardener_v1`
- Blend: `cozy_bouncy` · root_motion: **false**
- Bridge job: `BLD-UCBV-C1R-NORI7-019F8C18`
- GLB sha256: `e16d6af8e121879bc3080f2b64d281ee00975ef195db60b622917c28ca594b7f`
- mesh.validate(clean_customdata=false, verbose=true) → `false` (zero deform-weight errors)
- Export: zero ERROR / traceback / `Mesh ... is not valid`

## Materials (C0 cream lock)

- Body cream bible `#fdf3e2` + shade `#efe0c8` (`MAT_CozyCeramic` / shade)
- Leaf joints `#7fc98f` (`MAT_CozyLeaf`)
- Face socket `#3d3226` · iris `#a8dced`
- Wood straps / metal nozzle present
- Cyan (`MAT_CozyManifestCyan`) manifestation accent slot only — not body fill
- DNA `#F7E9C6` remains non-authoritative alias only

## Layer A — Tier3 public names (real keyed GLB)

`idle`, `walk`, `scan`, `happy`, `cancel`

## Layer B — UCBV game-local extension (not from Tier3)

`turn_left`, `turn_right`, `build_place`, `build_place_hold`, `confirm`

## Deferred optional (not idle-aliased)

`water`, `plant_seed`, `harvest`, `charge`, `low_energy`

## Motion kit

- Read-only under `orchestration/control/motion_kit/**`
- Validator: exit 0, ALL CHECKS GREEN, 172/172, 35/35 SIGNATURE_UNIQUE must_author
- Kit hashes match binding review; kit not edited
- Scope limited to Nori-7 / one skeleton family

## C2 next (do not spawn from C1)

1. Load GLB via offline intake; fail closed if bones/clips missing
2. Implement AnimationTree + adapter wiring from integration map
3. Do not copy `motion_kit/reference/motion_primitive_adapter.gd` blindly
4. Remove procedural SphereMesh/CapsuleMesh presenter from normal play
5. Build catalog UI / InputMap Q-R / delete mode (C2 lease)

## Honesty

- Not descriptor-as-mesh; not pelvis-bob-only; not Tier3 payload
- Real skinned mesh (9 material primitives, armature skin), 14 joints, 10 animations with transform channels
- `accepted=false` / no self-accept

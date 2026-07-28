# WO-UCBV-001 C1 mesh-weight correction 004

Status: `READY UNDER CODEX DIRECTIVE 85`  
Task: `UCBV-001` only  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852` coordinator-only  
Authority: `PATCH_DRAFT`

## Purpose

Correct only the invalid deform weights and unclean Blender export discovered
by Codex in C1. Do not redesign Nori-7, change its palette, rename actions,
alter the 14-bone hierarchy, expand animation scope or touch runtime code.

The prior C1 receipt/log under `correction_002` are immutable rejected evidence.
Do not edit, delete or rehabilitate them.

## Worker

- Profile: `.grok/agents/aidle-worldgen-asset-art.md`
- TrustLayer: `blue-team-p0-remediator`
- UI: `ui-color-type-specialist`
- Real installed child; no grandchildren or support profiles
- `accepted=false`, `self_accept=false`

## Exact product lease

- `game/assets/ucbv_001/character/nori7/**`
- `game/resources/ucbv_001/character/**`
- `orchestration/design/ucbv_001/character/nori7/**`

## Exact orchestration lease

- `orchestration/receipts/ucbv_001/correction_003/C1R_character_mesh_weight_correction_003.json`
- `orchestration/logs/ucbv_001/correction_003/C1R_character_mesh_weight_correction_003.log`

## Required correction

1. Open the delivered `.blend` with the approved local Blender 5.2.0 LTS.
2. Clamp every deform weight to `[0,1]`, remove non-finite values, and normalize
   each weighted vertex without inventing new vertex groups or changing the
   14-bone hierarchy.
3. Before saving, run `mesh.validate(clean_customdata=false, verbose=true)` on
   every production mesh. It must return `false` and emit zero deform-weight
   errors. Record literal output in the leased correction log.
4. Export a fresh GLB. The export log must contain zero `ERROR`, zero failed
   traceback and zero `Mesh ... is not valid` warning. A deprecation warning
   must be removed from the correction script rather than waived.
5. Independently re-import the fresh GLB into an empty Blender scene and prove:
   exactly one scene mesh node, skinned to the exact 14 bones; 10 required
   actions with nonzero duration and transform channels; nine named production
   materials; four sockets; no extra scene mesh; imported meshes validate
   without correction.
6. Recompute GLB/blend/package/provenance/adapter/validation hashes and byte
   counts. Update only leased product artifacts that contain affected hashes.
7. Re-run the immutable motion-kit validator read-only and verify all seven kit
   hashes. Never edit `orchestration/control/motion_kit/**`.

## Stop and handoff

Write a schema-valid `agent_step_contract` receipt with the real durable child
UUID, literal commands/exits, exact product writes, `out_of_lease_writes=[]`,
`accepted=false`, `self_accept=false`, and return `REVIEW_REQUESTED` to Codex.
Do not spawn C2. C2 remains blocked until Codex independently accepts C1R.

All Directive-84 prohibitions remain: no P2E-002, parent product patch,
dependency install, Godot version change, credentials, live provider/public
network, push, deploy, publish or shipping. Red F01 remains a hard stop.

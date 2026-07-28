# WO-UCBV-001 — Unified Character + Block Visual Foundation

Status: `QUEUED / NOT AUTHORIZED TO DISPATCH`  
Dependency: `H1-CONSOLIDATE-001 HUMAN PASS`  
Decision source: `orchestration/control/UNIFIED_CHARACTER_BLOCK_VISUAL_DIRECTION_001.md`

## Objective

Deliver one detailed playable character and one matching production-quality
construction block family as a single visual foundation, then integrate them
into the accepted offline P2E Block Assembly flow.

## Scope

### Character

- Select exactly one existing approved Character Foundry identity.
- Produce silhouette sheet, front/side/back turnaround and proportion guide.
- Produce a modular body/outfit definition with named material slots.
- Build one production mesh, skeleton, skin and rig through the approved local
  Blender bridge workflow.
- Supply idle, walk, turn, build/place, confirm and cancel animations.
- Export through the existing offline GLB intake contract.

### Block family

- Foundation, floor, wall, corner, door, window, roof, fence and one prop.
- Reuse accepted Block-DNA socket, bounds, rotation, elevation and material-slot
  semantics.
- Supply preview, valid, invalid, selected, materializing and complete states.
- Reuse world-profile palette variants and existing `STATE_VARIANTS`.

### Integration

- Replace only the first-slice character and matching placeholder modules.
- Preserve Build Q/R separation, World Commit authority, idempotency, revision
  checks, persistence, undo and cancel.
- Show the character performing the build interaction with the matching kit.

## Planned workflow after authorization

1. SSOT/style preflight (`VERIFY_ONLY`).
2. Character silhouette and unified visual brief (`PATCH_DRAFT`, sole writer
   for its exact art-definition lease).
3. Matching block-family art production (`PATCH_DRAFT`, disjoint exact lease).
4. Character rig/animation production (`PATCH_DRAFT`, disjoint exact lease).
5. Godot/GLB integration (`PATCH_DRAFT`, sole runtime writer).
6. Red scope/originality audit (`READ_ONLY_AUDIT`).
7. QA headed evidence (`VERIFY_ONLY`).
8. Purple release recommendation (`VERIFY_ONLY`, never accepts).
9. Codex machine review, then Human visual acceptance.

Every active directive must name real installed profiles, exact TrustLayer/UI
bindings, five mandatory plus routed skills, durable transcript UUIDs, exact
one-writer leases and schema-valid MAF receipts with `accepted=false` and
`self_accept=false`.

## Acceptance gates

- Character and block kit visibly share silhouette, palette, materials and
  surface-detail language.
- Character identity matches its accepted Foundry record and provenance.
- No character mesh/rig/animation placeholder remains in the first slice.
- All ten block modules validate against current Block-DNA/P2E contracts.
- Character build/place/confirm/cancel animations align with actual runtime
  state transitions, not a prerecorded mockup.
- 1280x720 and 868x517 normal-play evidence is readable and free of diagnostic
  walls, overlap and clipping.
- Godot logs contain zero ERROR/USER ERROR/SCRIPT ERROR and clean teardown.
- Existing H1, P2E, Control, G3, G4 and persistence regressions stay green.
- Red/Purple receipts and independent Codex hashes pass.
- Human Product Lead approves the character and block family together.

## Explicit exclusions

- No full 28-character production wave.
- No broad Scene expansion, DNA v1.2 or Tier 3 activation.
- No network, shipping, economy, ownership or live-provider work.
- No new dependency, credential, Godot version, push, deploy or publish.


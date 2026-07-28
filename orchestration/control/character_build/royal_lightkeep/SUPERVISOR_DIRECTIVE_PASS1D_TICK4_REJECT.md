# MOCKUP MATCH SUPERVISOR DIRECTIVE

**Asset:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  
**Current phase:** PASS 1D — PRIMARY MASSING  
**Directive:** `REJECT_PASS1D_NO_PROMOTION`  
**Authority:** technical Supervisor verdict; Owner retains final approval

## Gate

- `PASS1D_INTERNAL_APPROVED=false`
- `accepted=false`
- `PASS 2` is blocked.
- AI Builder is execution-only and must not set `accepted=true`, self-approve, or self-promote.
- The mockup remains the single visual design reference. Do not alter or replace it.

## Evidence verdict

Tick #4 remains a clay blockout and does not match the mockup closely enough. Front and Front 3/4 still show box-assembly massing; the tower crown and wing roofs do not reproduce the Gothic cascade/steep roof silhouette; the overlay shows major residual silhouette mismatch. Artifact existence, object counts, hashes, and self-reported scores are not acceptance evidence.

## Required next execution scope

1. Keep work in PASS 1D only; no openings, tertiary detail, materials, lighting polish, or PASS 2.
2. Rebuild primary roof and crown geometry as continuous steep hip/gable forms, not stacked roof boxes or extra cosmetic spikes.
3. Correct the left barracks front gable and the right wing roof mass against the reference silhouette.
4. Preserve one canonical 3D model and all fixed camera relationships.
5. Resolve the footprint discrepancy (`24m × 19m` shown in the mockup versus the current widened blockout) from the reference; do not silently override the observed scale.
6. Before any promotion, export clean Front, Rear, Left, Right, Front 3/4, Rear 3/4, top plan, black silhouette, and reference overlay proofs from the same model.

## Promotion condition

Stop and wait for a fresh Supervisor verdict after proof export. Do not interpret `READY_FOR_SUPERVISOR_REVIEW` as permission to advance. No PASS 2 or `PASS1D_INTERNAL_APPROVED=true` until the Supervisor explicitly approves the current evidence; final acceptance still requires the Owner.

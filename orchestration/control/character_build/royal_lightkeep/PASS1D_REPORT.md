# PASS 1D — PRIMARY MASSING REBUILD

**ASSET_ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  
**Date:** 2026-07-26  
**accepted:** false · **self_accept:** false  
**PASS 2:** not started

---

## A. DIMENSIONS

| Metric | Value |
|--------|--------|
| Total width | **~44 m** (silhouette priority; not 24 m text footprint) |
| Total depth | **~30 m** |
| Total height | **~38 m** tower budget |
| Terrace | **~5.8 m** |
| Tower gatehouse | ~10.2 × 9.2 × 12 m |
| Tower shaft | ~8 × 8 × **14.5 m** (shortened from 19.5 — was column-like) |
| Observation | wider than shaft (~10.5 m), continuous snap to shaft |
| Barracks left | ~**22–24 m** long × **11 m** deep × eave ~9 m |
| Right wing | ~13 × 10 × eave 8 m + gatehouse |
| Courtyard | **13 × 11 m** open pad (COURTYARD_VOID_GUIDE) |
| Main stair width | **~6.2 m** |

## B. MAJOR MASSES CREATED

Fortified base (L0–L2 terraces, parapets, corner projections) · TOWER_GATEHOUSE_BASE · TOWER_SHAFT · TOWER_OBSERVATION_BLOCK · TOWER_ROOF_BLOCK + peak · BARRACKS_LEFT_MAIN / GABLE / ROOF · RIGHT_WING_MAIN / GATEHOUSE / tunnel sides · MAIN_STAIR + rails · SIDE_RAMP · REAR_STAIR · major turrets · connectors · scale human.

## C. MASSES REMOVED

- Entire PASS 1 **24×19 narrow** layout discarded.
- Backup: `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1_BACKUP.blend`
- Old renders: `renders_pass1_backup/` if present.

## D. SIX-VIEW MATCH (honest)

| View | Status |
|------|--------|
| Front | **IMPROVED / still PARTIAL** — wider complex, horizontal barracks, large stair, continuous tower after snap; roof crown still simplified vs mockup Gothic |
| Rear | **IMPROVED / PARTIAL** — U-ish wings + gatehouse mass + courtyard gap readable |
| Left | **IMPROVED / PARTIAL** — barracks depth + side ramp diagonal |
| Right | **IMPROVED / PARTIAL** — right wing + gate, not mirror of left |
| Front 3/4 | **IMPROVED / PARTIAL** — hero massing readable |
| Rear 3/4 | **IMPROVED / PARTIAL** |

**Not claimed:** silhouette equal to mockup. Still clay blockout.

## E. SILHOUETTE GAPS (remaining)

1. Tower roof crown not multi-gable Gothic cascade (blockout only).  
2. Barracks front gable proportions still rough.  
3. Courtyard is open pad but wings do not fully wrap U like mockup.  
4. Gate tunnel is mass proxy (side walls), not boolean void.  
5. Roof pitches are box volumes, not true hip angles.  
6. Mesh count includes stair steps (>30 objects) — functional, not pure 20 mass ideal.

## F. FILES

| | |
|--|--|
| Blend | `...\royal_lightkeep\ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend` |
| Renders | `...\royal_lightkeep\renders_pass1d\CAM_01…06.png` |
| Report JSON | `PASS1D_REPORT.json` |
| Backup PASS1 | `..._PASS1_BACKUP.blend` |

## Materials

**CLAY ONLY** — no windows, doors, molding, banners, vegetation.

## Loop progress (2026-07-26 scheduler)

- Opened **PASS1D.blend** (Blender had been on rejected PASS1 — corrected).  
- In-place fixes: gable height, roof peak shrink, obs crown, right gatehouse, spire centering.  
- Proofs exported under `pass1d_*` names in `renders_pass1d/`.  
- State file: `PASS1D_LOOP_STATE.md`.  

## Priority lock tick (stair / U-wrap / multi-gable)

1. **Main stair** large-mass flights + retains; axis gatehouse; ~7 m wide.  
2. **Courtyard U-wrap:** rear arm, rear wing, right face; void 12×10 usable.  
3. **Tower multi-gable blockout:** central roof + 4 gables + hips + 4 corner spires.  
4. Full final proof set re-exported.  
5. **status: READY_FOR_SUPERVISOR_REVIEW**  
6. **accepted=false** · model freeze until supervisor.  

## Next

**Mockup Match Supervisor** reviews Front + Front 3/4 + top plan + six-view.  
**PASS 2 only after** explicit supervisor / human go.  
Agents: no further massing while status is READY_FOR_SUPERVISOR_REVIEW.

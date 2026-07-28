# QA gap — town_grid_import_001 (updated after headed QA)

**Wave:** TOWN CADASTRE IMPORT  
**Directive:** 99 · **WO:** WO-TOWN-GRID-IMPORT-001  

## Template requirement

- QA headed receipt **must exist** before Purple proceeds  
- HEADED evidence (screenshots) + **raw log file path** (not marker-only)

## Current state (after QA follow-up)

| Item | Status |
|------|--------|
| Blue | Present (`BLUE_IMPORT_001.json`) |
| Red | Present (`RED_FINDINGS_001.json`) |
| Headless smoke | PASS (`AIDLE_TOWN_GRID_IMPORT_SMOKE=PASS`) |
| **QA_town_grid_headed_001.json** | **FILED** |
| Headed screenshots | **5 PNGs** under `orchestration/evidence/town_grid_import_001/` |
| Raw Godot log | `orchestration/evidence/town_grid_import_001/godot_headed_qa_001.log` |
| Purple | WAITING (correct) · Human batch accept only |
| MOCKUP_SSOT_V2 100% fidelity | **FAIL 0/21** — flagged in QA receipt (does not block structural QA file existence) |

## Fidelity law (standing)

Anything with a MOCKUP_SSOT_V2 entry must match 100% before **wave close**.  
Structural cadastre import QA is complete; **product/fidelity close is not**.

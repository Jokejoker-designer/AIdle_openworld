# G8-001 Headed Visual Acceptance Matrix (H0 schema · VERIFY_ONLY)

Source evidence: `orchestration/evidence/g8_human_gate/README.md`  
Codex headed review: launch/movement/camera **PASS**; presentation **FAIL**.

## Executable gates (must stay green)

| ID | Check | Proof |
|---|---|---|
| E1 | Validator | `AIDLE_VALIDATION=PASS` |
| E2 | G3 E2E | `G3_E2E_SMOKE=PASS checks=76` |
| E3 | G4 persist | `G4_PERSIST_SMOKE=PASS checks=22` |
| E4 | Six tracked exports | zero-diff vs baseline after G3/G4 |
| E5 | Clean boot 2.5D | fixed-angle camera marker |
| E6 | Manifestation smoke | stages + cancel collision |
| E7 | Companion headless | text-only, no commit tool |
| E8 | Bridge/edition smoke | Free no-API; secrets refused |
| E9 | G5/G6 targeted | gateway + two-client markers |

## Visual / headed gates (new)

| ID | Check | Evidence |
|---|---|---|
| V1 | Physical Starter Realm landmarks | house, path, farm, ≥3 prop groups visible |
| V2 | Not a single flat color field | contrasting ground/sky + landmark materials |
| V3 | Player + Companion readable silhouettes | capsule/low-poly + companion aura |
| V4 | HUD unclipped 1280×720 | screenshot |
| V5 | HUD unclipped 868×517 | screenshot |
| V6 | Companion chat mounted + toggle (E / button) | screenshot + log |
| V7 | Free Bridge Send Snapshot + Import Decision visible | screenshot |
| V8 | Preview stages visible before confirm | wireframe→… screenshot |
| V9 | Confirm and Cancel separate; cancel cleans collision | screenshot/log |
| V10 | Clean headed log | no SCRIPT/Parse/Compile ERROR |

## Honesty classes

- **Executable:** E1–E9 headless + V* only when screenshots/logs exist
- **Visual-only:** aesthetic taste beyond readable landmarks
- **Local POC:** Free Bridge manual; Paid fixture; no live LLM
- **Deferred:** voice, free 3D cam, production multiplayer, marketplace

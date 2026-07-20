# G8-001 Alpha Evidence Report — Directive 19 + CORRECTION-001 (Directive 20)

**Task:** G8-001 Independent 2.5D Alpha Evidence Gate  
**Authority:** VERIFY_ONLY (eight domain profiles) · parent collate only  
**Directive 19 machine claim:** `PASS_FOR_HUMAN_REVIEW` / `HITL_REQUIRED` — **superseded on scope honesty**  
**Codex Directive 19 review:** `CHANGES_REQUESTED` (six tracked prior-evidence mutations)  
**Directive 20 correction:** independently verified by Codex · state **`HITL_REQUIRED` / `PASS_FOR_HUMAN_REVIEW`** — **not** `ACCEPTED`  
**Final machine acceptor:** Codex · **Final alpha:** Human Product Lead  
**Parent self-accept:** false  

---

## 0. Directive 19 scope-honesty failure (preserved)

Directive 19 **functional** smokes (G3/G4 markers, validator, boot, G5/G6, eight receipts) are **not** invalidated as functional history.

What **failed** and must not be erased:

- VERIFY_ONLY G3/G4 runs **rewrote six tracked** export/evidence files under `game/scripts/modules/{executor,persist}/exports/`.
- Report/collate/status claimed `product_patches_this_gate=0` and no prior-evidence edits — **false**.
- Codex review: `orchestration/reviews/CODEX_G8-001_MACHINE_REVIEW.json` → `CHANGES_REQUESTED`.

### Correction-001 (Directive 20) — machine status for Codex re-verify

| Item | Result |
|---|---|
| G3 runtime exports | **only** `user://g3_e2e_smoke/` |
| G4 evidence | **only** `user://g4_persist_smoke/` (no res dual-write) |
| Six tracked files vs `60fccdd` after G3+G4 rerun | **`SIX_TRACKED_EXPORTS_ZERO_DIFF=PASS`** |
| G3 / G4 re-run | `checks=76` / `checks=22` PASS |
| Validator + clean 2.5D boot | PASS |
| Correction receipts C0–C2 MAF-valid | PASS |
| Report | `orchestration/reviews/G8-001_CORRECTION_001_REPORT.md` |
| Matrix log | `orchestration/logs/g8-correction-001-matrix.log` |

Codex independently re-ran G3 (76), G4 (22), the validator and clean 2.5D boot,
then confirmed the six tracked files stayed byte-identical to `60fccdd`. The
machine alpha handoff is therefore **`HITL_REQUIRED` /
`PASS_FOR_HUMAN_REVIEW`**, not `ACCEPTED`.

---

## 1. Executive machine verdict (Directive 19 functional matrix — historical)

| Gate | Result |
|---|---|
| Eight domain VERIFY_ONLY receipts | **8/8 PASS** (schema-valid) |
| Integrated machine matrix (validator → G6) | **PASS markers** (EXIT=0) |
| MAF schema validate eight G8 receipts | **PASS** |
| Secret / public-bind / forbidden / dependency scans | **PASS** (forbidden hits adjudicated) |
| Prior-evidence mutation claim | **FAILED** — six tracked files changed |
| Self-ACCEPT by parent or domains | **None** |

**Directive 19 machine outcome as claimed was incorrect on evidence purity.** Functional suite still green; honesty gate required CORRECTION-001.

---

## 2. Executable proof (machine-rerun this gate)

Evidence log: `orchestration/logs/g8-integrated-matrix.log`  
Security: `orchestration/logs/g8-security-scans.log`  
Domain receipts: `orchestration/receipts/g8/G8_<profile>.json`  
Collate: `orchestration/receipts/G8-001.json`

| Surface | Marker / count | Exit |
|---|---|---|
| Project validator | `AIDLE_VALIDATION=PASS` | 0 |
| Clean fixed-angle 2.5D boot | `Camera mode=fixed-angle 2.5D` + XZ locomotion markers | 0 |
| Manifestation stages/cancel | `AIDLE_MANIFESTATION_SMOKE=PASS checks=8` | 0 |
| Companion text-only AGM | `G2-003_GODOT_SMOKE=PASS` (+ Python companion smoke) | 0 |
| Free Desktop Bridge | `G2-005_GODOT_SMOKE=PASS checks=11` | 0 |
| Edition (Free/Paid parity, no secrets) | `G2-007_GODOT_SMOKE=PASS` | 0 |
| Deterministic executor + G3 prompt→house E2E | `G3_E2E_SMOKE=PASS checks=76` (rev=3 chain) | 0 |
| G4 signed persistence | `G4_PERSIST_SMOKE=PASS checks=22` | 0 |
| G5 AGM gateway (fixture) | `G5_AGM_GATEWAY_SMOKE=PASS` (36 tests network profile) | 0 |
| G5 Paid adapter | `G5_PAID_ADAPTER_SMOKE=PASS checks=14` | 0 |
| G6 world authority POC | `G6_WORLD_AUTHORITY_SMOKE=PASS` (21 tests) | 0 |
| G6 two-client Godot | `G6_TWO_CLIENT_SMOKE=PASS checks=13` | 0 |
| Eight G8 receipts × MAF schema | `MAF_SCHEMA_VALIDATE_ALL=PASS count=8` | 0 |

### Domain independent re-runs (Z0)

| Profile | Key executable proof | Receipt |
|---|---|---|
| schema | `validate_project.py` PASS; fixtures/schema inventory | `G8_schema.json` |
| core | Headless boot + edition smoke; fixed-angle + no client secrets | `G8_core.json` |
| manifestation | Stages wireframe→hologram→materializing→complete; cancel no collision | `G8_manifestation.json` |
| companion | Text-only dialogue; `has_commit_tool()==false`; no TTS/STT surface | `G8_companion.json` |
| asset | cozy_house_small grammar; provenance; optional G3 recipe smoke | `G8_asset.json` |
| executor | G3 E2E 76 checks; rev=3; complete/cancel/undo paths; paid adapter boundary | `G8_executor.json` |
| persist | HMAC journal; save/reload hash; fail-closed integrity; rev3→4 | `G8_persist.json` |
| network | G5 gateway+paid; G6 21 + two-client 13; no public bind | `G8_network.json` |

All domain receipts: `authority_token=VERIFY_ONLY`, `self_accept=false`, no nested grandchildren product writers.

---

## 3. Documentation-only claims (not re-executed as product code)

| Claim | Basis | Not executable proof of… |
|---|---|---|
| G0–G6 tasks ACCEPTED in `orchestration/tasks.json` | Task state inventory | Fresh product acceptance of G8 |
| Codex final/correction acceptances (G3–G6) | `orchestration/reviews/CODEX_*` | New G8 ACCEPTED |
| Purple reviews for G1–G6 | `orchestration/reviews/G*_PURPLE_REVIEW.md` | Headed visual QA |
| Blueprint v1.1 architecture narrative | Blueprint docs | Runtime multiplayer production |
| Commit policy narrative | `contracts/commit/commit_policy.md` | Server durability beyond POC |

**Note:** G2-005/006/007 lack dedicated `*-ACCEPT.json` files; historical acceptance is via Codex partial-wave docs + tasks.json (schema domain caveat — not a G8 FAIL).

---

## 4. Local POC limitations (honest boundary)

| Area | What was proved | What was **not** proved |
|---|---|---|
| **G5 Paid / AGM** | FixtureProvider gateway + local paid adapter; schema/consent/budget/idempotency | Live provider, real API keys, outbound network, billing |
| **G6 multiplayer** | In-process dual-client World Commit simulator; forge/stale/bypass rejected; converge hash | Nakama/Colyseus, public listener, cloud, cross-machine netcode |
| **G4 persistence** | Local signed journal, HMAC fail-closed, offline gate | Production KMS/HSM, multi-device sync server authority |
| **Manifestation** | Headless stage machine + collision/cancel invariants | Pixel-perfect headed presentation aesthetics |
| **Companion** | Text dialogue + personality drift caps; no commit tool | Voice, STT/TTS, avatar lip-sync |
| **Edition** | Free/Paid same contracts; secret keys refused at settings | Commercial SKU, store entitlement backend |

Edition smoke **intentionally** emits `ERROR:` refuse lines for `api_key` / `client_secret` storage — that is **PASS proof**, not boot regression.

---

## 5. Deferred roadmap (explicitly out of alpha machine gate)

- Voice / STT / TTS / companion audio  
- Free-form 3D camera / FPS orbit  
- Voxel terrain live worldgen  
- Real cities / open-world scale content  
- Production multiplayer stack selection & deploy  
- Marketplace / economy  
- Live AI provider integration (post-HITL)  
- Neural world models / paid generation APIs as runtime deps  

---

## 6. Security & scope scans

| Scan | Verdict | Notes |
|---|---|---|
| Public bind (`0.0.0.0`, HTTP/TCP servers in product runtime trees) | **PASS** | None in scoped network/bridge/gateway/POC trees |
| Live secret literals (non-test product) | **PASS** | No `sk-` / AWS / PEM private keys in product trees |
| Forbidden scope (voice/blockchain/live multiplayer stacks) | **PASS_ADJUDICATED** | Hits = doc **negations** (Nakama/Colyseus) + companion smoke **reject-list** (`AudioStreamMicrophone`) — not runtime features |
| Dependency inventory | **PASS** | Inventory only; **no install** performed this gate |

---

## 7. Residual risks for Human / Codex

1. Headless matrix ≠ headed play feel, camera framing, or art presentation.  
2. Fixture-only AGM path must not be marketed as “live AI ready.”  
3. G6 POC must not be marketed as multiplayer product.  
4. Local TEST_ONLY seal material must never ship as production secrets.  
5. Human Acceptance Checklist must be completed before any alpha ACCEPTED claim.

---

## 8. Required human path

1. Codex reviews this package + matrix log + eight receipts (machine gate).  
2. Human Product Lead runs `orchestration/reviews/G8-001_HUMAN_ACCEPTANCE_CHECKLIST.md` on a **local headed** Godot 4.3 build.  
3. Only after both may G8-001 (or a subsequent directive) become ACCEPTED — **not** by parent self-accept.

---

## 9. Directive 19 intended parent write surface (historical)

- `orchestration/work_orders/G8-001_DISPATCH_MAP.md`  
- `orchestration/receipts/G8-001.json`  
- `orchestration/reviews/G8-001_ALPHA_EVIDENCE_REPORT.md`  
- `orchestration/reviews/G8-001_HUMAN_ACCEPTANCE_CHECKLIST.md`  
- `orchestration/logs/g8-integrated-matrix.log` (footer append)  
- `orchestration/logs/g8-security-scans.log`  
- `orchestration/control/grok_status.json`  

Directive 19 violated this intended surface by regenerating six tracked prior
evidence files. Directive 20 disclosed and corrected that failure. Its three
authorized product/test patches redirect G3/G4 runtime evidence to `user://`;
the six tracked evidence files were restored to `60fccdd` and remained clean
after Codex's independent rerun.

# G8-001 UI-VISUAL-CORRECTION-003 Report (Directive 24)

**State:** `REVIEW_REQUESTED` / `WAITING_CODEX`  
**Self-accept:** false · **Not ACCEPTED**  
**Preserves:** Directives 21–23 code + Directive 22 character/skill bindings  
**Explicit non-scope:** Control Foundation (1B) — **not implemented** this directive  

## Five blockers closed

| ID | Fix | Evidence |
|---|---|---|
| CANCEL_VISUAL_NOT_PROVEN | Distinct cancel-mode demo at offset transform; `stage_cancel_preview` then cancel; entity_absent for that id; runner wide crop change | `CANCEL_CROP_WIDE_PASS`, cancel_proof in manifest |
| BRIDGE_EVIDENCE_INVALID_SNAPSHOT | UUID `a1b2c3d4-e5f6-4789-a012-3456789abcde`; status line on export | no `snapshot_id must look like uuid` in runner log |
| QUEST_STATUS_READABILITY | StatusPill high-contrast surface; **min 12px** labels; buttons **≥32px** | starter_realm_panel + action bar |
| ERROR_GATE_NOT_EXECUTABLE | GDScript ingests log → `_error_lines`; **canonical** `scripts/run_g8_headed_visual_c003.py` fails on ERROR | `CANONICAL_RUNNER=PASS` |
| SAVED_CHOICE_PROOF_MISSING | Isolated `user://c003_isolated_choice/world_meta.cfg` seed surrealism; ephemeral Cozy persist=false; hash/content preserved | `SAVED_CHOICE_RUNNER_PASS` |

## Canonical gate

```text
python scripts/run_g8_headed_visual_c003.py
→ CANONICAL_RUNNER=PASS
```

Evidence: `orchestration/evidence/g8_ui_visual_correction_003/`  
(10 PNGs + `evidence_manifest.json` with `final_verdict`, `cancel_proof`, `runner_log_sha256`)

## Regression preserved

| Gate | Result |
|---|---|
| G3 | 76 |
| G4 | 22 |
| Manifestation | 8 |
| Companion / Bridge | PASS |
| Validator | PASS |
| Six tracked exports | zero-diff |
| 8 C003 MAF receipts | PASS |

## Waves C0–C7

Reviewer waves (C0, C3–C7) do not patch product. C1/C2 sole writers only.

## Residual

- Codex crop box 550..900,100..250 may still be 0 if cancel entity is outside that box; **wide crop** and entity_absent are the authoritative cancel proofs.
- Control Foundation remains `PARTIAL` for Phase 1B after 1A acceptance.

Awaiting Codex independent re-run of the canonical runner + regressions.

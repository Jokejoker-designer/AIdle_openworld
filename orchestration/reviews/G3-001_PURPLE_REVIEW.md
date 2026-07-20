# Purple VERIFY_ONLY review — G3-001 W3_PURPLE_REVIEW

| Field | Value |
|---|---|
| Task | G3-001 — AGM onboarding vertical slice (prompt → house → confirm handoff) |
| Reviewer | Purple / Devil's Advocate (network profile, non-writer this wave) |
| Authority | **VERIFY_ONLY** (no product patches; **no tasks.json ACCEPT**) |
| Date | 2026-07-20 |
| Work order | `orchestration/work_orders/WO-G3-001.md` |
| Dispatch map | `orchestration/work_orders/G3-001_DISPATCH_MAP.md` |
| Worker receipt | `orchestration/receipts/g3/W2_executor.json` |
| Handoffs audited | `W0_schema.json`, `W0_network.json`, `W0_persist.json`, `W1_core.json`, `W1_manifestation.json`, `W1_companion.json`, `W1_asset.json`, `W2_executor.json` |

## VERDICT

**ACCEPTED**

The G3 vertical slice is executable, schema-boundary-preserving, and matches WO-G3-001
outcome steps under Private Reality / handoff-stub constraints. Independent re-run of
headless E2E smoke and `validate_project.py` both PASS. Cancel and undo semantics match
W0_persist evidence contract for G3 (preview teardown vs compensating stub; no history
erase; no live World Commit).

**This review does NOT ACCEPT `orchestration/tasks.json`.** Task G3-001 remains
`IN_PROGRESS` pending Codex final acceptance. Purple never patches and never self-accepts
worker output as ACCEPTED workflow state.

## Acceptance matrix (WO-G3-001 outcome)

| Criterion | Result | Evidence |
|---|---|---|
| 1. World State Snapshot | **PASS** | Fixture `contracts/fixtures/agm/valid/valid_snapshot_desktop_bridge.json`; `G3OnboardingSlice.load_world_state_snapshot` + realm `apply_snapshot_context` |
| 2. Schema-valid AGM onboarding decision | **PASS** | `valid_decision_desktop_bridge` + `valid_decision_with_build_proposal`; soft present only |
| 3. Companion text + quest UI | **PASS** | `present_g3_onboarding_decision` / presenter path; `StarterRealmController` quest/status/text |
| 4. Build → house recipe | **PASS** | `HouseRecipeResolver.resolve_cozy_house_for_starter`; complete receipt `entity_recipe_id=cozy_house_small`, `recipe_part_count=14` |
| 5. Preview wireframe→hologram→materializing→complete | **PASS** | `G3PreviewBridge.start_house_preview`; complete `stages_observed` length 4 |
| 6. Explicit confirm before handoff | **PASS** | `confirm_after_preview` requires non-empty `confirmed_by` + prior preview ok; no auto-confirm |
| 7. Execution / complete receipt | **PASS** | `exports/g3_complete_receipt.json`; `pipeline_stage=commit_handoff_stubbed`; stub status `rejected` |
| 8. Cancel + undo without canonical durable mutation | **PASS** | Cancel mid-`hologram`; confirm-after-cancel rejected; undo `mutation_class=compensating`, history preserved |
| World Commit is handoff stub only | **PASS** | All three receipts `world_commit_invoked=false`, `durable_mutation_applied=false` |
| Dispatch / ownership / no self-accept | **PASS** | W2 writes limited to executor surface + receipts; all wave `self_accept=false` |
| E2E smoke + validator | **PASS** | Purple re-run below |

## Independent verification (Purple re-run)

### Godot headless E2E

```
tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
  -s res://scripts/modules/executor/g3_e2e_smoke.gd
→ EXIT=0
→ G3_E2E_SMOKE=PASS checks=62
```

Log: `orchestration/logs/g3-purple-e2e.log` (also consistent with
`orchestration/logs/g3-e2e-parent.log` / `g3-w2-executor-e2e.log`).

Cleanliness:

- No `SCRIPT ERROR`, `Parse Error`, `Compile Error`, or Godot `ERROR:` lines.
- Expected non-fatal warnings only: `No mount for module: voxel`;
  `No manifestation host; using local fallback` (headless presentation residual).

### Project validator

```
python scripts\validate_project.py
→ EXIT=0
→ AIDLE_VALIDATION=PASS
scope=blueprint-links,all-schema-shapes,world-positive-negative,fixtures-valid-invalid,
      format-checker,commit-authority,event-envelope,agm-snapshot-decision,crew,task-dag,asset-grammar
```

### Export receipts vs W0_persist

| Receipt | Path | Contract spot-check |
|---|---|---|
| complete | `game/scripts/modules/executor/exports/g3_complete_receipt.json` | `receipt_kind=complete`; confirmation `preview_required=true` + `state=confirmed`; stages full four; `commit_request.authority.commit_path=world_commit_service`; `source=server_authoritative` (not client_authoritative); stub `status=rejected` not `committed`; durable/wci false |
| cancel | `.../g3_cancel_receipt.json` | `receipt_kind=cancel`; `pipeline_stage=cancelled`; `cancelled_during_stage=hologram`; collision false / orphan 0; **no** `mutation_class=compensating`; durable/wci false; revision not advanced |
| undo | `.../g3_undo_receipt.json` | `receipt_kind=undo`; `mutation_class=compensating`; new `request_id`/`receipt_id`; links `prior_receipt_id`/`prior_request_id` to complete; `history_erased=false`; `history_preserved=true`; prior complete file still present; durable/wci false |

Cross-link after Purple re-run: undo `prior_receipt_id` equals complete `receipt_id`.

## Adversarial challenges

### 1. Scope creep

| Claim | Assessment |
|---|---|
| W2 only owns coordinator + E2E + exports | **OK** — product writes under `game/scripts/modules/executor/g3_onboarding_slice.gd`, `g3_e2e_smoke.gd`, `exports/g3_*.json` |
| W1 domains stayed disjoint | **OK** from receipts/file lists (core UI, manifestation bridge, companion presenter, asset resolver) |
| No contracts / architecture / tasks / codex_directive edits by workers | **OK** for this wave surface; tasks.json still `IN_PROGRESS` for G3-001 |
| `.godot/global_script_class_cache.cfg` refresh | **Residual env note** (W2 self_audit) — not a product module; not treated as scope creep |

### 2. Authority bypass / dual soft-apply (RR-NET-02)

| Path | Assessment |
|---|---|
| Companion confirms or World-Commits | **Not found** — companion remains proposal/present only |
| Coordinator uses `ExecutorModule.execute_decision` **and** companion apply | **Mitigated** — `g3_onboarding_slice.gd` never calls `execute_decision`; single soft path via `present_g3_onboarding_decision` (or presenter/applier fallback) then executor **prompt** pipeline only |
| Silent durable commit | **Not found** — confirm builds handoff + synthetic rejected stub; `durable_mutation_applied` forced false on path success |

### 3. Cancel / undo correctness (W0_persist)

| Rule | Assessment |
|---|---|
| Cancel removes preview only; not compensating | **PASS** — cancel receipt has no compensating class; note field states preview-only |
| Cancel at hologram; re-cancel ok; confirm-after-cancel fails | **PASS** — exercised in `run_cancel_path` / smoke |
| Undo is NEW compensating stub; does not erase complete export | **PASS** — file remains; ids distinct; links present |
| G4 log/hash/reload not invented | **PASS** — undo note defers real compensation to G4 |

### 4. Test honesty

| Claim | Assessment |
|---|---|
| W2 `checks=62` / exit 0 | **Reproduced** by Purple |
| Receipts written by smoke | **Yes** — re-run refreshed export JSON |
| Collision/orphan on cancel | **Soft honesty residual** — `build_cancel_receipt` hardcodes `has_durable_collision=false` and `orphan_collision_count=0` rather than copying live cancel_preview payload / scene-tree orphan count. Mitigating: cancel_preview **is** invoked; manifestation cancel path itself returns collision false; confirm-after-cancel is behavioral. Not a WO fail, residual RR below |
| `world_commit_invoked` | Hardcoded false on builders — acceptable for G3 (no service call exists); matches pipeline design |

### 5. Stub commit / presentation collision (RR-NET-01 / RR-NET-03)

| Risk | Assessment |
|---|---|
| Complete enables local durable **collision** | **Documented residual** — complete receipt `has_durable_collision=true` while `durable_mutation_applied=false`. Presentation ≠ commit-log authority |
| Handoff looks like real commit_request | **Documented residual** — schema-shaped request + rejected stub; consumers must not local-apply |
| Undo after complete does not free solids | **Expected for G3 stub** — no live compensating commit; G4 owns real reverse |

### 6. World revision bind (W0_schema residual materialized)

Complete handoff shows `expected_world_revision=0` while starter snapshot fixture uses **`world_revision=3`**.

Root cause chain:

1. `CompanionModule._ensure_logic_state` configures builder with `expected_world_revision: 0`.
2. Slice sets companion **snapshot id** only on CompanionModule path; does not rebind builder revision from live snapshot.
3. `PromptPipeline.confirm` prefers `target.expected_world_revision` when present, overriding live snapshot rev passed from `ExecutorModule.confirm_prompt`.

**Not a G3 WO blocker** (no live commit, no revision advance claimed). **Must fix before live World Commit / G4** or handoffs will false-conflict / false-accept against wrong revision.

## Wave evidence integrity

| Wave | Profile | Authority | Self-accept | Artifact |
|---|---|---|---|---|
| W0 | schema / network / persist | VERIFY_ONLY | false | `orchestration/receipts/g3/W0_*.json` |
| W1 | core / manifestation / companion / asset | PATCH_DRAFT | false | `W1_*.json` + owned domain files |
| W2 | executor | PATCH_DRAFT | false | `W2_executor.json` + slice/smoke/exports |
| W3 | purple (this) | VERIFY_ONLY | n/a | **this file only** |

Parent may collate `REVIEW_REQUESTED` / `grok_status.json`; must **not** self-ACCEPT.

## Blockers

**None** for G3-001 vertical-slice acceptance evidence under WO scope.

## Residual risks (carry forward)

| ID | Severity | Detail |
|---|---|---|
| RR-G3-PURPLE-01 | **medium** | `expected_world_revision=0` on complete handoff vs snapshot revision 3; companion builder default + pipeline prefer-target-over-live. Fix before live commit / G4 |
| RR-NET-01 | medium | Manifestation complete local collision is presentation-only; do not treat as World Commit success; undo stub does not free solids |
| RR-NET-02 | low (mitigated for G3) | Dual soft-apply surfaces still exist in codebase; G3 coordinator avoids double wire — future scenes must keep single owner |
| RR-NET-03 | low | Commit handoff stub is schema-valid looking; forbid local apply of `commit_request` outside World Commit service |
| RR-G3-PURPLE-02 | low | Cancel receipt collision/orphan fields are receipt-hardcoded, not scene-tree measured; strengthen smoke if G4 requires collision forensics |
| RR-EXEC-G3-01 / host fallback | low | Headless manifestation host fallback warnings; non-fatal |
| RR-EXEC-G3-03 / G4 | medium | Real compensating commit, append-only log, entity hash save/reload remain G4-001 |
| Soft AGM effects on cancel | low | Mood/quest soft UI not fully rolled back on cancel (W0_persist remaining risk); non-canonical |
| Fixture path hardcode | low | Slice fixture loader includes workspace absolute path fallback `E:/AIdle_openworld` |

## What Purple did **not** do

- Did not edit `game/**`, `contracts/**`, `orchestration/tasks.json`, architecture, or codex directive.
- Did not write `*-ACCEPT.json` or set task state to ACCEPTED.
- Did not claim multiplayer, live World Commit, or G4 persistence complete.

## Recommendation to Codex (final acceptor)

Accept G3-001 **implementation evidence** as meeting WO-G3-001 vertical-slice bar.

Track **RR-G3-PURPLE-01** (revision rebind) as a hard precondition for any live commit path or G4 compensation wiring.

Do **not** treat this Purple document as tasks.json state transition; only Codex (or designated final acceptor) may move G3-001 → ACCEPTED after human/Codex review of this package.
)

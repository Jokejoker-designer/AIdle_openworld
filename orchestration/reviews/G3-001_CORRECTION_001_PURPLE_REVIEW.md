# Purple VERIFY_ONLY review — G3-001 CORRECTION-001 C3_NETWORK_PURPLE

| Field | Value |
|---|---|
| Task | G3-001 — Revision binding + cancel-evidence correction |
| Reviewer | Purple / Devil's Advocate (`aidle-network`) |
| Authority | **VERIFY_ONLY** (no product patches; **no tasks.json ACCEPT**) |
| Date | 2026-07-21 |
| Work order | `orchestration/work_orders/WO-G3-001-CORRECTION-001.md` |
| Directive | `orchestration/control/codex_directive.json` (id 11, wave C3_NETWORK_PURPLE) |
| Prior Codex | `orchestration/reviews/CODEX_G3-001_ADVERSARIAL_REVIEW.json` → **CHANGES_REQUESTED** |
| Wave receipts | `C0_schema.json`, `C1_executor.json`, `C2_persist.json`, this → `C3_network.json` |

## VERDICT

**ACCEPTED**

All four Codex adversarial challenges from directive-10 / `CODEX-G3-001-2026-07-21` are
closed by the bounded correction with independent executable evidence. Purple re-ran
headless E2E and the project validator; both PASS. Revision chain is live fixture **3**
end-to-end. Cancel collision/orphan fields are runtime-derived and inject tests fail
closed if hardcode is reintroduced. World Commit remains a **rejected** handoff stub
with no durable mutation. No wave self-accepted.

**This review does NOT ACCEPT `orchestration/tasks.json`.** Task G3-001 remains
`CHANGES_REQUESTED` until Codex (final acceptor) moves it. Purple never patches and
never self-accepts worker output as ACCEPTED workflow state.

`next_route`: **WAITING_CODEX**.

---

## Codex challenge matrix

| # | Codex challenge | Result | Evidence |
|---|---|---|---|
| 1 | Revision `3` equality across snapshot → prompt → commit → complete | **FIXED** | Static measure + smoke `rev_*` / `export_*` |
| 2 | Cancel evidence runtime-derived; tests fail if hardcode ignored | **FIXED** | `build_cancel_receipt` priority chain + inject contrast |
| 3 | No authority bypass / no durable mutation / stub still rejected | **PRESERVED** | All three receipts + smoke authority checks |
| 4 | No self-accept | **PRESERVED** | C0–C3 `self_accept: false`; no `*-ACCEPT.json`; tasks not edited |

---

## 1. Revision binding (Codex primary defect)

### Claim under review

Exported complete handoff bound `expected_world_revision=0` while starter snapshot
fixture is `world_revision=3` (optimistic-concurrency authority defect on the future
commit boundary).

### Independent measurement (post-C1, Purple re-run)

| Source | Field | Value |
|---|---|---|
| `contracts/fixtures/agm/valid/valid_snapshot_desktop_bridge.json` | `world_revision` | **3** |
| `exports/world_prompt_from_build.json` | `target.expected_world_revision` | **3** |
| `exports/commit_request_handoff_stub.json` | `expected_world_revision` | **3** |
| `exports/g3_complete_receipt.json` | `expected_world_revision` | **3** |
| `exports/g3_complete_receipt.json` | `commit_request.expected_world_revision` | **3** |
| complete receipt | `source_snapshot_id` | `11111111-1111-4111-8111-111111111111` (matches fixture) |

Invariant:

```
world_prompt.target.expected_world_revision
  == commit_request.expected_world_revision
  == complete_receipt.expected_world_revision
  == live_snapshot.world_revision
  == 3
```

**PASS.** Zero-leak contrast: no bound field is `0` while live is `3`.

### Code path (adversarial read)

1. `load_world_state_snapshot` always calls `_rebind_builder_revision_from_snapshot()`.
2. Companion path uses `CompanionModule.set_live_snapshot(snapshot)` which configures
   builder `expected_world_revision` from `snapshot.world_revision` (cold default `0`
   is placeholder only).
3. `present_build_proposal_decision` / preview path force-binds
   `_bind_world_prompt_revision_from_snapshot()` so `target.expected_world_revision`
   cannot remain at builder default when a snapshot is loaded.
4. `build_complete_receipt` treats **live** `_snapshot.world_revision` as authority;
   force-binds nested `commit_request.expected_world_revision`; only falls back to
   commit/prompt when `live_rev == 0` (no snapshot).

### Smoke contrast (must exist per Codex missing_evidence)

From `g3_e2e_smoke.gd` `_assert_revision_binding` (Purple re-run all **OK**):

- `live_snapshot_revision`
- `rev_eq_world_prompt` / `rev_eq_commit_request` / `rev_eq_complete_receipt`
- `rev_chain_equality`
- `export_wp_rev` / `export_cr_rev` / `export_complete_rev` / `export_complete_nested_cr_rev`
- Negative fail-closed labels if zero leaks: `fail_if_zero_leaks_on_*`

### Residual (not a blocker)

`prompt_pipeline.confirm` still prefers `target.expected_world_revision` when present
over the `world_revision` parameter. G3 mitigates by binding **target** before confirm
and force-binding in the complete receipt. Track as **RR-C3-01** for any future
non-G3 confirm entry points.

---

## 2. Cancel runtime evidence (Codex second defect)

### Claim under review

Cancel receipt hardcodes `has_durable_collision=false` and `orphan_collision_count=0`
instead of deriving from runtime cancellation / measured preview.

### Code path

`g3_onboarding_slice.gd` `build_cancel_receipt`:

| Field | Priority |
|---|---|
| `has_durable_collision` | manifestation → top-level cancel → preview → default `false` only if absent |
| `orphan_collision_count` | manifestation → top-level cancel → preview → default `0` only if absent |

Defaults are **fallbacks when keys are absent**, not unconditional assignment over a
present runtime payload.

### Smoke inject contrast (Codex missing_evidence closed)

`_assert_cancel_runtime_evidence` (all **OK** on Purple re-run):

| Check | Intent |
|---|---|
| `cancel_live_collision_matches_runtime` | Happy path false |
| `cancel_live_orphan_matches_runtime` | Happy path 0 |
| `cancel_inject_collision_reflected` | Inject manifestation collision=`true` must appear on receipt |
| `cancel_inject_orphan_reflected` | Inject orphan=`2` must appear |
| `cancel_top_level_payload_reflected` | Top-level cancel collision=`true` / orphan=`3` when manifestation omits |

Fail-closed labels if ignored: `cancel_inject_collision_ignored`,
`cancel_inject_orphan_ignored`, `cancel_top_level_payload_ignored`.

Happy-path export `g3_cancel_receipt.json`: collision false, orphan 0, not compensating,
`world_revision_advanced=false`, durable/wci false.

**PASS.**

---

## 3. Authority / durable mutation / stub

| Check | Result |
|---|---|
| Complete `commit_receipt_stub.status` | **rejected** (not committed) |
| Complete `durable_mutation_applied` / `world_commit_invoked` | **false** / **false** |
| Cancel durable / wci / revision advanced | **false** / **false** / **false** |
| Undo `mutation_class=compensating`, history not erased, prior complete still exists | **PASS** |
| `authority.commit_path` | `world_commit_service` |
| `authority.source` | not `client_authoritative` |
| Explicit confirm still required; confirm-after-cancel rejected | smoke **OK** |
| Four manifestation stages on complete | wireframe → hologram → materializing → complete |

No client / companion / bridge silent durable commit path introduced by the correction.
World Commit remains G3 handoff stub only.

**PASS** (authority invariants preserved).

---

## 4. Self-accept / ownership honesty

| Wave | Authority | Product writes | self_accept |
|---|---|---|---|
| C0 schema | VERIFY_ONLY | none | **false** |
| C1 executor | PATCH_DRAFT | sole product writer (slice/smoke/exports + required companion rebind) | **false** |
| C2 persist | VERIFY_ONLY | none | **false** |
| C3 network (this) | VERIFY_ONLY | none | **false** |

- No `G3-001-ACCEPT.json` created.
- `orchestration/tasks.json` **not edited** by this wave (still `CHANGES_REQUESTED`).
- `parent_may_self_accept: false` per directive 11.
- Companion edit was in C1 scope as “strictly required for revision context” and is
  justified by C0 root-cause (builder default 0 on companion-module path).

**PASS.**

---

## Independent verification (Purple re-run)

### Godot headless E2E

```
tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
  -s res://scripts/modules/executor/g3_e2e_smoke.gd
→ EXIT=0
→ G3_E2E_SMOKE=PASS checks=76
```

Logs:

- `orchestration/logs/g3-c3-purple-e2e.out.log` / `.err.log` (this wave)
- Consistent with `orchestration/logs/g3-c1-parent-e2e.log` and
  `g3-c1-executor-e2e.log` (`G3_E2E_SMOKE=PASS checks=76`)

Cleanliness:

- No `SCRIPT ERROR`, `Parse Error`, `Compile Error`, or Godot `ERROR:` lines.
- Expected non-fatal warnings only: `No mount for module: voxel`;
  `No manifestation host; using local fallback`.

### Project validator

```
python scripts\validate_project.py
→ EXIT=0
→ AIDLE_VALIDATION=PASS
```

### C0 → C1 transition honesty

| Stage | Invariant status |
|---|---|
| C0 pre-patch | `FAIL_ON_CURRENT_EXPORTS` (exports at 0, live 3) |
| C1 patch + smoke | `PASS` checks=76 |
| C2 static re-read | `PASS` |
| C3 independent re-run | `PASS` checks=76; export chain all 3 |

---

## Adversarial residuals (carry forward — not correction blockers)

| ID | Severity | Detail |
|---|---|---|
| RR-C3-01 | low | `prompt_pipeline.confirm` still prefers target rev when present; G3 force-binds target + complete receipt. Guard non-G3 entry points. |
| RR-NET-01 | medium | Complete `manifestation.has_durable_collision=true` is presentation-local; not World Commit success; undo stub does not free solids |
| RR-EXEC-G3-03 / G4 | medium | Real compensating commit, append-only log, entity hash save/reload remain G4 |
| RR-C3-02 | info | `exports/execution_receipt_build.json` (G2 surface) may still show rev 0; out of correction write scope; not the G3 complete handoff chain |
| Host fallback | low | Headless manifestation host warnings; non-fatal |

---

## What Purple did **not** do

- Did not edit `game/**`, `contracts/**`, `orchestration/tasks.json`, architecture,
  codex directive, or prior wave receipts.
- Did not write `*-ACCEPT.json` or set task state to ACCEPTED.
- Did not claim multiplayer, live World Commit, or G4 persistence complete.
- Did not spawn children.

## Recommendation to Codex (final acceptor)

Accept **G3-001 CORRECTION-001** implementation evidence as closing the two Codex
blockers (revision binding + cancel evidence honesty) while preserving authority and
no-self-accept rules.

Only Codex may transition G3-001 → ACCEPTED in `tasks.json` after reviewing this
package. Parent should set `grok_status` to `WAITING_CODEX` and stop.

Purple verdict is **ACCEPTED** for the correction package; **not** a workflow ACCEPT.

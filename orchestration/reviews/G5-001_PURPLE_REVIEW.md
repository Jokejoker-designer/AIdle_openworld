# Purple VERIFY_ONLY review — G5-001 A4_PERSIST_PURPLE

| Field | Value |
|---|---|
| Task | G5-001 — Provider-neutral Paid AGM gateway adapter |
| Reviewer | Purple / Devil's Advocate (`aidle-persist`, non-writer) |
| Authority | **VERIFY_ONLY** (no product patches; **no tasks.json ACCEPT**) |
| Date | 2026-07-21 |
| Work order | `orchestration/work_orders/WO-G5-001.md` |
| Dispatch map | `orchestration/work_orders/G5-001_DISPATCH_MAP.md` |
| Architecture | `orchestration/ARCHITECTURE_LOCK.md` Paid edition row |
| Wave receipts | `A0_schema.json`, `A1_network.json`, `A2_executor.json`, `A3_core.json` |
| This receipt | `orchestration/receipts/g5/A4_persist.json` |

## VERDICT

**ACCEPTED**

G5-001 meets the work-order acceptance bar under architecture-lock authority:
provider-neutral trusted gateway with FixtureProvider only, hard budget caps,
idempotency, bounded retry matrix, structured error envelopes, Free/Paid
identical Snapshot/Decision semantics, Godot paid client with no secrets/SDKs,
and decisions remaining untrusted proposals that cannot bypass World Commit.

Independent Purple re-runs:

| Check | Result |
|---|---|
| `python services/agm_gateway/run_gateway_tests.py` | **EXIT=0**, `G5_AGM_GATEWAY_SMOKE=PASS`, 20 tests OK |
| Godot paid adapter smoke | **EXIT=0**, `G5_PAID_ADAPTER_SMOKE=PASS`, checks=14 |
| `python scripts/validate_project.py` | **EXIT=0**, `AIDLE_VALIDATION=PASS` |

All eight adversarial challenges **PASS**.

**This review does NOT ACCEPT `orchestration/tasks.json`.** Task G5-001 remains
for Codex final acceptance. Purple never patches product code and never
self-accepts worker output as ACCEPTED workflow state.
`self_accept=false`. `next_route=WAITING_CODEX`.

## Authority boundary (ARCHITECTURE_LOCK)

| Rule | G5 claim |
|---|---|
| Paid edition: API adapter behind trusted gateway | **In scope** — `GatewayService` + Godot client adapter |
| Provider credentials never in Godot / world files | **In scope** — proven; fixture/local only |
| Free + Paid same validator and World Commit boundary | **In scope** — edition identity + shared contracts |
| Real provider / outbound network | **HITL_REQUIRED** — denied by default; out of G5 scope |
| LLM / AGM durable mutation | **Forbidden** — decision untrusted; no World Commit from gateway |

Product headers and evidence restate:

- `gateway.py`: `world_commit_invoked = False` always; success `untrusted=true`
- `paid_gateway_adapter.gd`: fixture/local path only; `uses_network()==false`;
  `holds_provider_secrets()==false`; confirm returns `executed=false`,
  `committed=false`
- A1/A2 remaining notes: production path Godot → trusted gateway (server-side
  credentials); G5 Godot path is a pure GDScript fixture **mirror** of
  GatewayService for offline smoke

## Ownership (dispatch map)

| Wave | Role | Authority | Product writes |
|---|---|---|---|
| A0 | schema | VERIFY_ONLY | receipt only |
| A1 | network | PATCH_DRAFT | sole `services/agm_gateway/**` |
| A2 | executor | PATCH_DRAFT | sole Godot paid adapter paths |
| A3 | core | VERIFY_ONLY | receipt only |
| A4 | persist Purple | VERIFY_ONLY | this receipt + review only |

Disjoint ownership respected: network never wrote Godot bridge; executor never
wrote `services/agm_gateway/**`.

## Acceptance matrix (WO-G5-001)

| Criterion | Result | Evidence |
|---|---|---|
| Provider-neutral interface; fixture only | **PASS** | `ProviderInterface` + `FixtureProvider`; `allow_real_provider=False` |
| Redact + validate snapshot before provider; validate decision after | **PASS** | `gateway.py` pipeline; AT-VALIDATION-ORDER; AT-REDACT-* |
| Decision untrusted; no consent/preview/commit bypass | **PASS** | `untrusted=true`; durable deny-list; adapter consent path |
| No API key / secret / provider SDK in Godot or fixtures/logs/receipts | **PASS** | secret scans + smokes |
| Deny outbound / real provider by default (HITL) | **PASS** | policy `provider_mode_denied` |
| Idempotency IDs; bounded timeouts/retries; no retry on validation/policy/auth | **PASS** | AT-IDEMPOTENCY-REPLAY; AT-RETRY-TIMEOUT-ONLY |
| Budget estimate + hard per-request/session caps; no negative balance | **PASS** | AT-BUDGET-*; `SessionBudgetLedger` |
| Structured error categories without secret leak | **PASS** | AT-ERROR-CATEGORIES; six categories |
| Free/Paid identical Snapshot/Decision semantics | **PASS** | AT-EDITION-IDENTITY; A3 same-contracts |
| Gateway + Godot smokes; validator clean; MAF + Purple | **PASS** | Purple re-runs below |
| No self-accept | **PASS** | all waves `self_accept=false` |

## Independent verification (Purple re-run)

### Gateway fixture-provider unittest

```
python services/agm_gateway/run_gateway_tests.py
→ EXIT=0
→ G5_AGM_GATEWAY_SMOKE=PASS
→ Ran 20 tests … OK
```

Covered acceptance IDs (A1 matrix):

- AT-EDITION-IDENTITY
- AT-SNAPSHOT-VALID-PAID / AT-DECISION-VALID-PAID
- AT-REDACT-API-KEY / AT-REDACT-DENYLIST-DEEP
- AT-VALIDATION-ORDER / AT-DECISION-INVALID-AFTER-PROVIDER / AT-BUILD-PREVIEW-LOCK
- AT-UNTRUSTED-FLAG
- AT-ERROR-CATEGORIES
- AT-IDEMPOTENCY-REPLAY
- AT-BUDGET-PER-REQUEST / AT-BUDGET-SESSION
- AT-RETRY-TIMEOUT-ONLY (timeout recovery, unavailable exhaustion, no-retry validation/policy/budget)
- AT-NO-SECRETS-IN-ARTIFACTS
- AT-FIXTURE-PROVIDER-DEFAULT
- durable mutation from provider rejected

### Godot paid adapter headless smoke

```
tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
  -s res://scripts/modules/bridge/paid_gateway_smoke.gd
→ EXIT=0
→ G5_PAID_ADAPTER_SMOKE=PASS checks=14
```

Log: `orchestration/logs/g5-a4-purple-paid-smoke.log`

Checks observed OK:

1. `source_secret_scan`
2. `source_no_network_symbols`
3. `interface_surface`
4. `snapshot_api_paid_identity`
5. `happy_path_untrusted_proposal`
6. `consent_required_no_commit`
7. `confirm_no_execute`
8. `validation_error_category`
9. `budget_reject`
10. `policy_provider_mode`
11. `error_categories_list`
12. `idempotency_replay`
13. `fixture_files_no_secrets`
14. `production_path_note`

Cleanliness: no SCRIPT ERROR / Parse Error in smoke run; EXIT=0.

### Project validator

```
python scripts\validate_project.py
→ EXIT=0
→ AIDLE_VALIDATION=PASS
→ scope includes agm-snapshot-decision
```

## Adversarial challenges (required)

### 1. No provider secrets in Godot / fixtures / logs / receipts

**PASS.**

- Godot adapter declares `holds_provider_secrets()==false` and
  `uses_network()==false`; no product use of `HTTPRequest` / WebSocket peers.
- Smoke scans adapter + paid fixtures for live-looking token markers and
  deny-list payload keys; zero hits.
- Gateway non-test modules free of `sk-live` / `sk-proj-` / `AKIA`.
- Intentional forged injection strings appear only in unit tests (e.g.
  `sk-MUST-NOT-REACH-PROVIDER`) and are asserted **not** echoed in responses.
- G5 receipts and bridge exports contain no live credential material.
- Aligns with ARCHITECTURE_LOCK: credentials never in Godot client or world files.

### 2. Budget hard caps + no negative balance

**PASS.**

- `check_budget` rejects `estimate > per_request_cap` and
  `session_spent + estimate > session_cap` **before** provider dispatch.
- Negative `estimate` or `session_spent` → `budget_negative_balance`.
- `SessionBudgetLedger` refuses negative init/charge; gateway charges only on
  success path after decision validation.
- Pre-dispatch budget rejects leave `provider.call_count == 0` and do not
  increase spent (session-cap test keeps spent at pre-request value).
- Godot fixture mirror implements the same reject categories for client smoke.

### 3. Idempotency

**PASS.**

- Completed `request_id` (and distinct `gateway_request_id`) short-circuit
  **before** budget/provider so replays neither double-bill nor false-cap.
- Store returns deep-copied prior success or terminal non-retryable error
  envelopes.
- Test: same `request_id` → single provider call; identical `decision_id`.
- Godot adapter maintains in-process `_idempotency` map; smoke
  `idempotency_replay` OK.

Note (remaining risk, not a reject): store is in-memory MVP — process restart
clears keys. Acceptable for G5 fixture scope.

### 4. Retry only timeout / unavailable; never validation / policy / auth

**PASS.**

- `RETRYABLE_CATEGORIES = {timeout, provider_unavailable}` only.
- Timeout with `fail_times=2` recovers within `max_attempts=3`.
- Permanent unavailable exhausts → `retry_exhausted`, `retryable=false`.
- Invalid provider decision (validation) → exactly one provider call.
- Real vendor `provider_mode` (policy) and budget caps → zero provider calls.
- No dedicated `auth` category in the six-category envelope; auth-like failures
  are policy/validation and are non-retryable by construction.

### 5. Free / Paid identical contract semantics

**PASS.**

- AT-EDITION-IDENTITY strips `edition` + `transport`; free/paid fixture pairs
  are byte-equal on semantic core.
- Shared schemas: `world_state_snapshot.schema.json`,
  `decision_envelope.schema.json`.
- Paid adapter reuses Free Bridge `snapshot_builder.gd` and
  `decision_import_guard.gd`; rebinds `edition=api_paid` and
  `transport.channel=api_gateway` only.
- A3: `uses_same_agm_contracts()==true`; edition enum exactly
  `desktop_bridge_free | api_paid`.

### 6. Decision untrusted; no World Commit bypass

**PASS.**

- Gateway success envelope always sets `untrusted=true` and never invokes World
  Commit (`world_commit_invoked` remains false).
- Provider smuggling of `durable_mutation` / scripts / commit fields is
  deny-listed and rejected as validation.
- Build proposals remain schema-locked to preview/confirm path.
- Client: `receive_untrusted_response` rejects missing `untrusted=true`;
  player confirm hands off with `executed=false`, `committed=false`,
  `routes_to=agm_decision_executor` — same consent → executor → preview →
  confirm → World Commit spine as Free Desktop Bridge.

### 7. Fixture provider only; real provider HITL

**PASS.**

- Default `GatewayService` provider is `FixtureProvider`;
  `allow_real_provider=False`.
- Non-fixture modes (e.g. `openai_live`, `anthropic`) →
  `policy` / `provider_mode_denied`.
- Godot default `provider_mode=fixture`; non-fixture denied at client policy
  layer.
- No provider SDK imports in gateway or Godot product code; no outbound HTTP
  enablement in G5.

### 8. No self-accept

**PASS.**

- A0–A3 and this A4 receipt all set `self_accept=false`.
- A1/A2 leave `REVIEW_REQUESTED`; A3 is VERIFY_ONLY handoff `PASS`.
- Purple does **not** edit `orchestration/tasks.json` and does not mark G5-001
  ACCEPTED in the task DAG.
- Final acceptor remains **Codex** (`next_route=WAITING_CODEX`).

## Residual risks (accepted, non-blocking)

1. In-memory idempotency (no durable store / TTL).
2. Error envelope not yet a published contracts JSON Schema (runtime shape only).
3. Godot G5 path is a fixture **mirror** of the trusted gateway — production
   must call server-side gateway with server-side credentials (documented in
   adapter `production_path_note()`).
4. Absolute workspace fixture fallback path in GDScript (non-secret;
   environment-specific).
5. Client-side budget unit scaling differs numerically from Python estimate
   constants; authoritative hard caps remain on the trusted gateway.
6. Real provider enablement remains HITL_REQUIRED.

## Conclusion

G5-001 product waves A1 (gateway) and A2 (Godot paid adapter), with A0/A3
verification scaffolding, satisfy the work order under Purple independent
re-execution. **VERDICT: ACCEPTED** for Codex review. Purple did not accept the
task in `tasks.json`, did not patch product code, and did not spawn children.

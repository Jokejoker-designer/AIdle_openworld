# Purple VERIFY_ONLY review — G5-001 CORRECTION-001 C4_PERSIST_PURPLE

| Field | Value |
|---|---|
| Task | G5-001 — Provider-neutral Paid AGM gateway (authority-boundary correction) |
| Reviewer | Purple / Devil's Advocate (`aidle-persist`, non-writer) |
| Authority | **VERIFY_ONLY** (no product patches; **no tasks.json ACCEPT**) |
| Date | 2026-07-21 |
| Work order | `orchestration/work_orders/WO-G5-001-CORRECTION-001.md` |
| Dispatch map | `orchestration/work_orders/G5-001_CORRECTION_001_DISPATCH_MAP.md` |
| Prior Codex | `orchestration/reviews/CODEX_G5-001_ADVERSARIAL_REVIEW.json` → **CHANGES_REQUESTED** |
| Architecture | `orchestration/ARCHITECTURE_LOCK.md` Paid edition / gateway authority |
| Wave receipts | `C0_schema.json`, `C1_network.json`, `C2_executor.json`, `C3_core.json` |
| This receipt | `orchestration/receipts/g5/C4_persist.json` |

## VERDICT

**ACCEPTED**

G5-001 CORRECTION-001 closes every Codex adversarial challenge with independent
executable evidence. Purple re-ran the gateway suite (**36** tests), Godot paid
adapter smoke (**14** checks), optional edition smoke, and the project
validator; all PASS. Server-owned budget caps and ledger, non-finite budget
reject-before-dispatch, fixture-only provider object authority, and idempotency
fingerprint bind/conflict are product-proven under `services/agm_gateway/**`.
Free/Paid contract identity, untrusted decision routing, secret-free artifacts,
and fixture-only HITL posture are preserved. C2 confirms the Godot paid adapter
remains an untrusted proposal consumer with no product patch required.

**This review does NOT ACCEPT `orchestration/tasks.json`.** Task G5-001 remains
`CHANGES_REQUESTED` until Codex (final acceptor) moves it. Purple never patches
product code and never self-accepts worker output as ACCEPTED workflow state.
`self_accept=false`. `next_route=WAITING_CODEX`.

---

## Codex challenge matrix (required)

| # | Codex / WO challenge | Result | Evidence |
|---|---|---|---|
| 1 | Client cannot raise server caps; ledger not client-resettable | **FIXED** | `resolve_effective_caps` min-clamp; constructor ledger only; TestServerBudgetAuthority raise/reset tests |
| 2 | NaN/Inf/bool/non-numeric budget rejected before dispatch | **FIXED** | `parse_budget_number` + check_budget isfinite/type guards; nan/inf/bool/non-numeric tests |
| 3 | Non-fixture provider injection rejected with real authority off | **FIXED** | `isinstance(FixtureProvider)` gate; `provider_not_approved`; allow_real flag alone insufficient |
| 4 | Idempotency fingerprint conflict vs identical replay | **FIXED** | store `{fp,response}`; hit replay / conflict codes; request_id + gateway_request_id tests |

Also preserved (WO + prior A4 bar): secret scan, Free/Paid identity, untrusted
decision, fixture-only.

---

## 1. Server-owned budget authority (Codex 1 + 2)

### Claim under review

Untrusted `budget_context` could replace configured server caps with larger
values, seed/reset the ledger via `session_spent`, and pass NaN/±Inf/bool so
comparisons fail open into provider dispatch.

### Product proof (static)

| Component | Role |
|---|---|
| `budget.parse_budget_number` | Rejects bool (before `numbers.Real`), non-Real, NaN, ±Inf, negative |
| `budget.resolve_effective_caps` | `effective = min(server, client)` when client valid; else server |
| Client `session_spent` | Type-validated if present; **never** ledger authority |
| `SessionBudgetLedger` | Constructor/server seed only; charge only on success |
| `gateway.handle_request` | Uses `self.ledger.session_spent` for `check_budget`; reject path never charges |

Pipeline order (correction): redact → validate snapshot → resolve effective
caps → fingerprint → idempotency → budget check → provider object/mode gate →
provider → validate decision → charge → store.

### Independent suite (Purple re-run)

```
python services/agm_gateway/run_gateway_tests.py
→ EXIT=0
→ G5_AGM_GATEWAY_SMOKE=PASS
→ Ran 36 tests … OK
```

Budget authority tests observed OK:

| Test | Result |
|---|---|
| `test_client_cannot_raise_server_per_request_cap` | **PASS** — client `1e9` clamped; `budget_per_request_exceeded`; call_count=0 |
| `test_client_cannot_raise_server_session_cap` | **PASS** — client `session_cap=1e9` ignored as raise; session exceeded |
| `test_client_session_spent_cannot_reset_server_ledger` | **PASS** — client spent=0 does not reset server 50.0 |
| `test_client_may_request_stricter_lower_cap` | **PASS** — client may tighten |
| `test_budget_nan_rejects_before_dispatch` | **PASS** — non-retryable; no provider; no charge |
| `test_budget_infinity_rejects_before_dispatch` | **PASS** — ±Inf closed |
| `test_budget_bool_rejects_before_dispatch` | **PASS** — `budget_type_invalid` (no `float(True)` trap) |
| `test_budget_negative_rejects_before_dispatch` | **PASS** |
| `test_budget_non_numeric_rejects_before_dispatch` | **PASS** |
| `test_rejected_budget_never_calls_provider_or_charges_ledger` | **PASS** |
| Baseline AT-BUDGET-PER-REQUEST / AT-BUDGET-SESSION | **PASS** (session seed via constructor) |

**PASS / FIXED.**

---

## 2. Provider authority (Codex 3)

### Claim under review

An arbitrary injected `ProviderInterface` was invoked when
`allow_real_provider=false` if the request labeled `provider_mode=fixture`.
`allow_real_provider=true` alone opened non-fixture mode deny without a HITL
real-provider path.

### Product proof (static)

- `is_approved_fixture_provider` → `isinstance(provider, FixtureProvider)` only
- `_assert_provider_approved` before any provider method →
  `policy` / `provider_not_approved` / `retryable=false`
- `_assert_provider_mode_allowed` → only `fixture`; **flag does not open** real
  modes (`provider_mode_denied` even when `allow_real_provider=True`)
- No real provider, SDK, credential, or outbound network added in C1

### Executable evidence (Purple re-run)

| Test | Result |
|---|---|
| `test_injected_non_fixture_provider_rejected_when_real_disabled` | **PASS** — call_count=0; code=`provider_not_approved` |
| `test_allow_real_provider_true_not_sufficient_for_real_enablement` | **PASS** — non-fixture object still denied; non-fixture mode denied with fixture object |
| `test_only_fixture_provider_enabled` | **PASS** (baseline mode string deny) |

**PASS / FIXED.**

---

## 3. Idempotency fingerprint bind (Codex 4)

### Claim under review

Idempotency keys were not bound to a canonical request fingerprint; reused
`request_id` / `gateway_request_id` with a different payload returned the prior
response.

### Product proof (static)

| Component | Role |
|---|---|
| `compute_request_fingerprint` | `aidle_gateway_idempotency_fp_v1` + SHA-256 of sorted compact JSON |
| Material | redacted snapshot, effective caps, provider_mode, session_id, edition, require_api_paid flag |
| `IdempotencyStore` | `{fingerprint, response}` records; `lookup` → hit / miss / conflict |
| Conflict | `policy` / `idempotency_key_conflict` / non-retryable; no provider; no charge |
| Replay | same key + same fp → stored response; no redispatch; no second charge |
| Secrets | fingerprint over post-redaction only; store blob must not contain raw secrets |

### Executable evidence (Purple re-run)

| Test | Result |
|---|---|
| `test_idempotency_identical_replay_returns_stored_response` | **PASS** — call_count=1; same decision_id; spent unchanged on 2nd |
| `test_idempotency_conflict_on_request_id_payload_change` | **PASS** — conflict; no second call; no decision on conflict |
| `test_idempotency_conflict_on_gateway_request_id_payload_change` | **PASS** |
| `test_idempotency_fingerprint_excludes_secrets` | **PASS** — no `sk-MUST-NOT-REACH-STORE` / `api_key` in store |
| `test_same_request_id_no_second_provider_call` | **PASS** (baseline identical replay) |

**PASS / FIXED.**

---

## 4. Preserved G5 bar (secret / Free-Paid / untrusted / fixture)

| Check | Result | Evidence |
|---|---|---|
| Secret scan gateway non-test `.py` | **PASS** | 13 files, 0 offenders (Purple independent markers) |
| Gateway package secret unittest | **PASS** | `test_gateway_package_secret_scan` |
| Godot adapter no secrets/SDK/network | **PASS** | paid smoke source_secret_scan + source_no_network_symbols + fixture_files_no_secrets |
| Free/Paid identical payload semantics | **PASS** | `test_free_paid_payload_semantics_identical`; edition smoke `same_contracts=true` |
| Decision untrusted; no World Commit | **PASS** | success `untrusted=true`; smoke consent_required_no_commit + confirm_no_execute |
| Fixture-only; real HITL | **PASS** | object + mode gates; C1 no real provider |

---

## Independent verification summary

### Gateway suite

```
python services/agm_gateway/run_gateway_tests.py
G5_AGM_GATEWAY_SMOKE=PASS
Ran 36 tests in ~0.12s
OK
EXIT=0
```

Includes baseline 20 + 16 CORRECTION adversarial regressions (C1 named list).

### Paid adapter smoke

```
tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
  -s res://scripts/modules/bridge/paid_gateway_smoke.gd
→ EXIT=0
→ G5_PAID_ADAPTER_SMOKE=PASS checks=14
```

Log: `orchestration/logs/g5-c4-purple-paid-smoke.log`

### Edition smoke (optional, re-run)

```
tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
  -s res://scripts/core/edition_headless_smoke.gd
→ EXIT=0
→ G2-007_GODOT_SMOKE=PASS
→ edition=api_paid same_contracts=true no_secrets=true
```

Log: `orchestration/logs/g5-c4-purple-edition-smoke.log`

(Expected ERROR/WARNING lines prove secret refuse + consent gate — not failures.)

### Project validator

```
python scripts\validate_project.py
→ EXIT=0
→ AIDLE_VALIDATION=PASS
```

---

## Prior-wave consistency

| Wave | Profile | Auth | Verdict / state | Product writes |
|---|---|---|---|---|
| C0 | schema | VERIFY_ONLY | HANDOFF_TO_C1 (four FAIL invariants) | 0 (receipt only) |
| C1 | network | PATCH_DRAFT | REVIEW_REQUESTED — three invariants FIXED + 16 tests | sole `services/agm_gateway/**` |
| C2 | executor | VERIFY_ONLY | PASS — untrusted consumer; no Godot patch | 0 |
| C3 | core | VERIFY_ONLY | PASS — edition/boot parity | 0 |
| C4 | persist Purple | VERIFY_ONLY | **ACCEPTED** → WAITING_CODEX | 0 (receipt + this md) |

All waves `self_accept=false`. No children. No architecture / contracts /
work-order / tasks / directive / prior-receipt edits by this wave.

Ownership: C1 sole product writer for the correction. C0/C2/C3/C4 verify-only.

---

## Residuals (non-blocking for correction acceptance)

1. **In-memory idempotency store:** No TTL/persistence across process restart
   (MVP; intentional for G5).
2. **Fingerprint field set:** Stable for current fixtures; future non-result
   noise must not be over-included (false conflicts) or under-included (false
   replays).
3. **Godot fixture mirror:** Local budget/idempotency in the paid adapter is
   offline smoke only — not server authority; production remains Godot → trusted
   gateway.
4. **Real provider path:** Remains HITL_REQUIRED and unimplemented;
   `allow_real_provider=true` alone must stay insufficient (proven by
   regression).

None of these residuals reopen Codex challenges 1–4 or WO required evidence.

---

## Codex handoff

- Purple verdict: **ACCEPTED** (correction quality / authority / smoke)
- Workflow task state: **do not flip** to ACCEPTED in `tasks.json` here
- `self_accept`: **false**
- `next_route`: **WAITING_CODEX**
- Parent may update `grok_status.json` only if conductor-owned; this Purple
  wave wrote **only** `C4_persist.json` + this review.

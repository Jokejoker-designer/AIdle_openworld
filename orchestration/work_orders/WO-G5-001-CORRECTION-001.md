# Work Order — G5-001 Correction 001

Final acceptor: Codex. Continue only in the existing Grok Desktop parent.
Real provider selection, credentials and outbound networking remain `HITL_REQUIRED`.

## Required installed-subagent workflow

1. `schema` (`VERIFY_ONLY`) records the exact four failed invariants and test contracts.
2. `network` (`PATCH_DRAFT`) is the sole writer under `services/agm_gateway/**`.
3. `executor` (`VERIFY_ONLY`) confirms the Godot adapter remains an untrusted proposal consumer and does not patch product files.
4. `core` (`VERIFY_ONLY`) reruns edition parity and integrated boot.
5. `persist` (`VERIFY_ONLY`) performs Purple review of budget, provider authority, idempotency and evidence.

One writer per file. Each subagent emits an `agent_step_contract`. No nested
grandchildren. The parent only dispatches and collates; it cannot accept G5.

## Mandatory corrections

### Server-owned budget authority

- Configured `GatewayService.per_request_cap` and `session_cap` are hard upper
  bounds. An untrusted request may only request a stricter lower cap; it cannot
  raise either configured cap.
- The server ledger is authoritative. Client `session_spent` must not reset,
  reduce or replace it.
- Reject booleans, negative values, `NaN`, positive/negative Infinity and other
  non-finite/non-numeric budget fields before provider dispatch.
- A rejected budget request must not call the provider or charge the ledger.

### Provider authority

- With real-provider authority disabled, an injected provider that is not an
  approved fixture provider must fail with a structured non-retryable policy
  error before any provider method is called, even when `provider_mode=fixture`.
- Do not add or call a real provider, SDK, credential or network transport.
- Any future real-provider enablement remains a separate HITL-approved path;
  this correction must not make `allow_real_provider=true` sufficient by itself.

### Idempotency binding

- Bind `request_id` and `gateway_request_id` records to a deterministic
  canonical fingerprint of the validated/redacted request inputs that affect
  the result.
- An identical replay returns the stored response without redispatch or charge.
- Reuse of either id with a different fingerprint fails closed with a
  structured non-retryable conflict/policy response and no provider call.
- Never include raw secrets, hidden prompts or credential values in a
  fingerprint, log, error or receipt.

## Required correction evidence

- Existing 20 gateway tests remain green, plus regression tests proving:
  1. client caps cannot raise server caps;
  2. `NaN` and Infinity reject before dispatch;
  3. arbitrary provider injection rejects while real-provider authority is off;
  4. changed payload with reused `request_id` or `gateway_request_id` rejects,
     while identical replay remains idempotent.
- Godot paid adapter smoke, edition smoke, clean integrated boot and project
  validator rerun.
- Secret scan over all changed G5 files.
- MAF receipts, ownership map and Purple review.

Do not edit `tasks.json`, `codex_directive.json`, architecture/contracts or prior
receipts. Do not install, push, deploy, publish or enable outbound calls. Finish
`REVIEW_REQUESTED`/`WAITING_CODEX` by updating only `grok_status.json`.

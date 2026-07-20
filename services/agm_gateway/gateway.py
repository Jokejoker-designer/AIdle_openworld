"""AGM GatewayService — orchestrates redaction, validation, budget, idempotency, fixture provider."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .budget import (
    DEFAULT_PER_REQUEST_CAP,
    DEFAULT_SESSION_CAP,
    SessionBudgetLedger,
    check_budget,
    estimate_budget,
    resolve_effective_caps,
)
from .errors import (
    ErrorCategories,
    GatewayError,
    ProviderProtocolError,
    ProviderTimeout,
    ProviderUnavailable,
    build_error_envelope,
)
from .idempotency import IdempotencyStore, compute_request_fingerprint
from .providers.base import ProviderInterface
from .providers.fixture_provider import FixtureProvider
from .redact import (
    DECISION_DENY_KEYS,
    SNAPSHOT_DENY_KEYS,
    contains_deny_keys,
    redact_payload,
)
from .retry import DEFAULT_MAX_ATTEMPTS, RetryPolicy
from .validators import validate_decision, validate_snapshot

ALLOWED_PROVIDER_MODES = frozenset({"fixture"})


def is_approved_fixture_provider(provider: Any) -> bool:
    """MVP approval: only FixtureProvider instances are approved for dispatch.

    Real providers remain a separate HITL path; allow_real_provider alone is never enough.
    """
    return isinstance(provider, FixtureProvider)


class GatewayService:
    """Trusted gateway entrypoint. Deny outbound/real providers by default."""

    def __init__(
        self,
        *,
        provider: ProviderInterface | None = None,
        idempotency_store: IdempotencyStore | None = None,
        retry_policy: RetryPolicy | None = None,
        session_spent: float = 0.0,
        per_request_cap: float = DEFAULT_PER_REQUEST_CAP,
        session_cap: float = DEFAULT_SESSION_CAP,
        require_api_paid_edition: bool = True,
        allow_real_provider: bool = False,  # HITL flag only; never sufficient alone
    ) -> None:
        self.provider: ProviderInterface = provider if provider is not None else FixtureProvider()
        # Empty store has __len__==0 and would be falsy under `or` — use explicit None check
        self.idempotency = (
            idempotency_store if idempotency_store is not None else IdempotencyStore()
        )
        self.retry_policy = (
            retry_policy if retry_policy is not None else RetryPolicy(max_attempts=DEFAULT_MAX_ATTEMPTS)
        )
        self.ledger = SessionBudgetLedger(session_spent=session_spent)
        self.per_request_cap = float(per_request_cap)
        self.session_cap = float(session_cap)
        self.require_api_paid_edition = bool(require_api_paid_edition)
        self.allow_real_provider = bool(allow_real_provider)
        # Observability: never log secrets
        self.last_provider_input_keys: list[str] | None = None
        self.last_fingerprint: str | None = None
        self.world_commit_invoked = False  # always false — gateway never commits

    def redact_payload(
        self, obj: Any, *, decision: bool = False
    ) -> tuple[Any, list[str]]:
        deny = DECISION_DENY_KEYS if decision else SNAPSHOT_DENY_KEYS
        return redact_payload(obj, deny_keys=deny)

    def validate_snapshot(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        return validate_snapshot(snapshot)

    def validate_decision(self, decision: dict[str, Any]) -> dict[str, Any]:
        return validate_decision(decision)

    def estimate_budget(
        self, snapshot: dict[str, Any], context: dict[str, Any] | None = None
    ) -> dict[str, float]:
        return estimate_budget(snapshot, context)

    def check_budget(
        self,
        estimate: float,
        per_request_cap: float | None = None,
        session_cap: float | None = None,
        session_spent: float | None = None,
    ) -> dict[str, Any]:
        return check_budget(
            estimate,
            per_request_cap if per_request_cap is not None else self.per_request_cap,
            session_cap if session_cap is not None else self.session_cap,
            session_spent if session_spent is not None else self.ledger.session_spent,
        )

    def _assert_provider_approved(self) -> None:
        """Fail closed before any provider method when object is not approved fixture.

        allow_real_provider=True is intentionally insufficient without a separate
        HITL-approved real-provider path (not implemented).
        """
        if is_approved_fixture_provider(self.provider):
            return
        raise GatewayError(
            ErrorCategories.POLICY,
            "provider_not_approved",
            "Injected provider is not an approved fixture provider; "
            "real provider enablement requires a separate HITL-approved path",
            retryable=False,
            details={
                "provider_type": type(self.provider).__name__,
                "allow_real_provider": self.allow_real_provider,
            },
        )

    def _assert_provider_mode_allowed(self, provider_mode: str) -> None:
        """Only fixture mode is allowed. allow_real_provider alone does not open real modes."""
        if provider_mode in ALLOWED_PROVIDER_MODES:
            return
        # Real modes remain HITL_REQUIRED even when allow_real_provider is True
        # (flag alone is not a real-provider implementation gate).
        raise GatewayError(
            ErrorCategories.POLICY,
            "provider_mode_denied",
            "Real provider selection is HITL_REQUIRED; only fixture mode allowed",
            retryable=False,
            details={
                "provider_mode": provider_mode,
                "allow_real_provider": self.allow_real_provider,
            },
        )

    def _build_fingerprint(
        self,
        *,
        snapshot: dict[str, Any],
        effective_per_request_cap: float,
        effective_session_cap: float,
        provider_mode: str,
        session_id: Any,
    ) -> str:
        """Canonical fingerprint over redacted result-affecting inputs only (no secrets)."""
        material = {
            "snapshot": snapshot,
            "effective_per_request_cap": effective_per_request_cap,
            "effective_session_cap": effective_session_cap,
            "provider_mode": provider_mode,
            "session_id": session_id,
            "edition": snapshot.get("edition"),
            "require_api_paid_edition": self.require_api_paid_edition,
        }
        return compute_request_fingerprint(material)

    def _idempotency_lookup(
        self, request_id: str, gateway_request_id: str, fingerprint: str
    ) -> dict[str, Any] | None:
        """Return stored response on fingerprint match; raise on mismatch; None on miss."""
        keys: list[str] = []
        if request_id:
            keys.append(request_id)
        if gateway_request_id and gateway_request_id not in keys:
            keys.append(gateway_request_id)

        first_hit: dict[str, Any] | None = None
        for key in keys:
            status, response = self.idempotency.lookup(key, fingerprint)
            if status == "conflict":
                raise GatewayError(
                    ErrorCategories.POLICY,
                    "idempotency_key_conflict",
                    "Idempotency key reused with a different request fingerprint",
                    retryable=False,
                    details={
                        "key_kind": (
                            "request_id" if key == request_id else "gateway_request_id"
                        ),
                    },
                )
            if status == "hit" and first_hit is None:
                first_hit = response
        return first_hit

    def _idempotency_store(
        self,
        request_id: str,
        gateway_request_id: str,
        fingerprint: str,
        response: dict[str, Any],
    ) -> None:
        if not fingerprint:
            return
        if request_id:
            self.idempotency.put(request_id, fingerprint, response)
        if gateway_request_id and gateway_request_id != request_id:
            self.idempotency.put(gateway_request_id, fingerprint, response)

    def handle_request(self, gateway_request: dict[str, Any]) -> dict[str, Any]:
        """Pipeline: redact → validate → fingerprint → idempotency → budget → provider → decision."""
        request_id = ""
        gateway_request_id = ""
        trace_id = ""
        fingerprint: str | None = None

        try:
            if not isinstance(gateway_request, dict):
                raise GatewayError(
                    ErrorCategories.VALIDATION,
                    "request_not_object",
                    "gateway_request must be an object",
                    retryable=False,
                )

            # Shallow copy of request wrapper (redact in place of copy)
            raw = deepcopy(gateway_request)
            request_id = str(raw.get("request_id") or "").strip()
            gateway_request_id = str(
                raw.get("gateway_request_id") or request_id or ""
            ).strip()
            if not request_id:
                raise GatewayError(
                    ErrorCategories.VALIDATION,
                    "request_id_missing",
                    "request_id is required",
                    retryable=False,
                )
            if len(request_id) > 128:
                raise GatewayError(
                    ErrorCategories.VALIDATION,
                    "request_id_too_long",
                    "request_id exceeds max length 128",
                    retryable=False,
                )

            # --- 1. Redact secrets (wrapper + snapshot) before schema / provider ---
            # Detect smuggling on raw snapshot body (names only — never log values).
            raw_snapshot = raw.get("snapshot")
            snapshot_inbound_deny: list[str] = []
            if isinstance(raw_snapshot, dict):
                snapshot_inbound_deny = contains_deny_keys(
                    raw_snapshot, SNAPSHOT_DENY_KEYS
                )

            redacted_request, stripped_wrapper = redact_payload(
                raw, deny_keys=SNAPSHOT_DENY_KEYS
            )
            snapshot = redacted_request.get("snapshot")
            if snapshot is None:
                raise GatewayError(
                    ErrorCategories.VALIDATION,
                    "snapshot_missing",
                    "snapshot is required",
                    retryable=False,
                )
            if not isinstance(snapshot, dict):
                raise GatewayError(
                    ErrorCategories.VALIDATION,
                    "snapshot_not_object",
                    "snapshot must be an object",
                    retryable=False,
                )

            snapshot, stripped_snapshot = redact_payload(
                snapshot, deny_keys=SNAPSHOT_DENY_KEYS
            )
            stripped_fields = stripped_wrapper + stripped_snapshot
            trace_id = str(snapshot.get("trace_id") or "")

            # Snapshot-body deny-list smuggling fails closed (after strip so secrets
            # never reach provider). Wrapper-only headers are stripped and allowed.
            if snapshot_inbound_deny or stripped_snapshot:
                raise GatewayError(
                    ErrorCategories.VALIDATION,
                    "snapshot_deny_list_rejected",
                    "Inbound snapshot contained forbidden secret or credential fields",
                    retryable=False,
                    details={
                        "fields_stripped": sorted(set(stripped_snapshot)),
                    },
                )

            # --- 2. Validate snapshot schema ---
            snap_result = validate_snapshot(snapshot)
            if not snap_result["ok"]:
                raise GatewayError(
                    ErrorCategories.VALIDATION,
                    "snapshot_schema_invalid",
                    "World State Snapshot failed schema validation",
                    retryable=False,
                    details={
                        "error_count": len(snap_result["errors"]),
                        # field paths only — no secret values
                        "errors": snap_result["errors"][:12],
                        "fields_stripped": sorted(set(stripped_fields)),
                    },
                )

            if self.require_api_paid_edition and snapshot.get("edition") != "api_paid":
                raise GatewayError(
                    ErrorCategories.POLICY,
                    "edition_not_api_paid",
                    "Paid gateway path requires edition=api_paid",
                    retryable=False,
                    details={"edition": snapshot.get("edition")},
                )

            # --- 3. Provider mode normalize + budget authority (before provider) ---
            provider_mode = str(
                redacted_request.get("provider_mode")
                or "fixture"
            )
            # Normalize fixture provider label to mode "fixture"
            if provider_mode in ("fixture", "fixture_provider"):
                provider_mode = "fixture"

            budget_context = redacted_request.get("budget_context") or {}
            if not isinstance(budget_context, dict):
                raise GatewayError(
                    ErrorCategories.VALIDATION,
                    "budget_context_invalid",
                    "budget_context must be an object when provided",
                    retryable=False,
                )

            # Server caps are hard upper bounds; client may only lower them.
            # Client session_spent is validated if present but NEVER seeds/replaces ledger.
            effective_per_request_cap, effective_session_cap = resolve_effective_caps(
                self.per_request_cap,
                self.session_cap,
                budget_context,
            )

            # --- 4. Canonical fingerprint (redacted result-affecting inputs only) ---
            fingerprint = self._build_fingerprint(
                snapshot=snapshot,
                effective_per_request_cap=effective_per_request_cap,
                effective_session_cap=effective_session_cap,
                provider_mode=provider_mode,
                session_id=snapshot.get("session_id")
                or redacted_request.get("session_id"),
            )
            self.last_fingerprint = fingerprint

            # --- 5. Idempotency: match → stored response; mismatch → conflict ---
            prior = self._idempotency_lookup(
                request_id, gateway_request_id, fingerprint
            )
            if prior is not None:
                return prior

            # --- 6. Budget check (server ledger authoritative) ---
            est = estimate_budget(snapshot, {"request_id": request_id})
            estimate = float(est["estimate"])
            check_budget(
                estimate,
                effective_per_request_cap,
                effective_session_cap,
                self.ledger.session_spent,
            )

            # --- 7. Provider object + mode authority gates (BEFORE any provider method) ---
            self._assert_provider_approved()
            self._assert_provider_mode_allowed(provider_mode)

            # Final assert: provider never sees deny-list keys
            residual = contains_deny_keys(snapshot, SNAPSHOT_DENY_KEYS)
            if residual:
                raise GatewayError(
                    ErrorCategories.POLICY,
                    "redaction_incomplete",
                    "Deny-list keys remained after redaction",
                    retryable=False,
                    details={"fields": residual},
                )

            self.last_provider_input_keys = sorted(snapshot.keys())
            provider_context = {
                "request_id": request_id,
                "gateway_request_id": gateway_request_id,
                "session_id": snapshot.get("session_id"),
                "provider_mode": provider_mode,
            }

            def _call_provider() -> dict[str, Any]:
                return self.provider.generate_decision(snapshot, provider_context)

            try:
                decision = self.retry_policy.run(_call_provider)
            except GatewayError:
                raise
            except Exception as exc:  # noqa: BLE001
                raise ProviderProtocolError(
                    "provider raised unexpected error",
                    details={"exc_type": type(exc).__name__},
                ) from exc

            if not isinstance(decision, dict):
                raise GatewayError(
                    ErrorCategories.VALIDATION,
                    "decision_not_object",
                    "Provider returned non-object decision",
                    retryable=False,
                )

            # --- 8. Validate decision + re-redact deny list ---
            # Provider-smuggled deny keys (durable_mutation, script, secrets, …)
            # are rejected — not silently accepted after strip.
            pre_deny = contains_deny_keys(decision, DECISION_DENY_KEYS)
            decision, decision_stripped = redact_payload(
                decision, deny_keys=DECISION_DENY_KEYS
            )
            residual_dec = contains_deny_keys(decision, DECISION_DENY_KEYS)
            if residual_dec:
                raise GatewayError(
                    ErrorCategories.VALIDATION,
                    "decision_deny_list_residual",
                    "Decision contained residual deny-list keys after redaction",
                    retryable=False,
                    details={"fields": residual_dec},
                )
            if pre_deny:
                raise GatewayError(
                    ErrorCategories.VALIDATION,
                    "decision_deny_list_rejected",
                    "Provider decision contained forbidden fields",
                    retryable=False,
                    details={"fields": sorted(set(pre_deny))},
                )

            dec_result = validate_decision(decision)
            if not dec_result["ok"]:
                raise GatewayError(
                    ErrorCategories.VALIDATION,
                    "decision_schema_invalid",
                    "AGM Decision Envelope failed schema validation",
                    retryable=False,
                    details={
                        "error_count": len(dec_result["errors"]),
                        "errors": dec_result["errors"][:12],
                        "fields_stripped": sorted(set(decision_stripped)),
                    },
                )

            # Bind check: source_snapshot_id must match
            if decision.get("source_snapshot_id") != snapshot.get("snapshot_id"):
                raise GatewayError(
                    ErrorCategories.VALIDATION,
                    "source_snapshot_mismatch",
                    "decision.source_snapshot_id must equal snapshot.snapshot_id",
                    retryable=False,
                )

            # --- 9. Return untrusted proposal; charge budget only on success ---
            session_spent_after = self.ledger.charge(estimate)
            response: dict[str, Any] = {
                "ok": True,
                "request_id": request_id,
                "gateway_request_id": gateway_request_id or request_id,
                "decision": decision,
                "untrusted": True,
                "provider_label": getattr(self.provider, "label", "fixture_provider"),
                "budget": {
                    "estimate": estimate,
                    "session_spent_after": session_spent_after,
                    "per_request_cap": effective_per_request_cap,
                    "session_cap": effective_session_cap,
                },
                "fields_stripped_count": len(stripped_fields),
            }
            # Gateway never invokes World Commit or sets confirmation confirmed
            assert self.world_commit_invoked is False

            self._idempotency_store(
                request_id, gateway_request_id, fingerprint, response
            )
            return response

        except GatewayError as exc:
            envelope = build_error_envelope(
                category=exc.category,
                code=exc.code,
                message=exc.message,
                request_id=request_id,
                trace_id=trace_id,
                retryable=exc.retryable,
                details=exc.details,
            )
            # Store terminal non-retryable outcomes only when fingerprint is known
            # (post-redaction/validation) so replays bind to the same inputs.
            if (
                fingerprint
                and request_id
                and exc.category
                in (
                    ErrorCategories.VALIDATION,
                    ErrorCategories.POLICY,
                    ErrorCategories.BUDGET,
                    ErrorCategories.RETRY_EXHAUSTED,
                )
                and exc.code != "idempotency_key_conflict"
            ):
                self._idempotency_store(
                    request_id, gateway_request_id, fingerprint, envelope
                )
            return envelope

        except (ProviderTimeout, ProviderUnavailable) as exc:
            # Should be wrapped by retry policy; if escapes, map directly
            return build_error_envelope(
                category=exc.category,
                code=exc.code,
                message=exc.message,
                request_id=request_id,
                trace_id=trace_id,
                retryable=exc.retryable,
                details=exc.details,
            )

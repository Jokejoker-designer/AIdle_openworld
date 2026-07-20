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
)
from .errors import (
    ErrorCategories,
    GatewayError,
    ProviderProtocolError,
    ProviderTimeout,
    ProviderUnavailable,
    build_error_envelope,
)
from .idempotency import IdempotencyStore
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
        allow_real_provider: bool = False,  # HITL only; default False
    ) -> None:
        self.provider: ProviderInterface = provider or FixtureProvider()
        self.idempotency = idempotency_store or IdempotencyStore()
        self.retry_policy = retry_policy or RetryPolicy(max_attempts=DEFAULT_MAX_ATTEMPTS)
        self.ledger = SessionBudgetLedger(session_spent=session_spent)
        self.per_request_cap = float(per_request_cap)
        self.session_cap = float(session_cap)
        self.require_api_paid_edition = require_api_paid_edition
        self.allow_real_provider = bool(allow_real_provider)
        # Observability: never log secrets
        self.last_provider_input_keys: list[str] | None = None
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

    def handle_request(self, gateway_request: dict[str, Any]) -> dict[str, Any]:
        """Pipeline: redact → validate snapshot → budget → idempotency → provider → validate decision."""
        request_id = ""
        gateway_request_id = ""
        trace_id = ""

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

            # Idempotency short-circuit: completed request_id returns prior without
            # re-dispatch / re-billing (checked before budget to avoid false rejects).
            prior = self.idempotency.get(request_id)
            if prior is not None:
                return prior
            if gateway_request_id and gateway_request_id != request_id:
                prior_gw = self.idempotency.get(gateway_request_id)
                if prior_gw is not None:
                    return prior_gw

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

            # --- 3. Budget + policy precheck (before provider) ---
            provider_mode = str(
                redacted_request.get("provider_mode")
                or "fixture"
            )
            # Normalize fixture provider label to mode "fixture"
            if provider_mode in ("fixture", "fixture_provider"):
                provider_mode = "fixture"

            if provider_mode not in ALLOWED_PROVIDER_MODES:
                if not self.allow_real_provider:
                    raise GatewayError(
                        ErrorCategories.POLICY,
                        "provider_mode_denied",
                        "Real provider selection is HITL_REQUIRED; only fixture mode allowed",
                        retryable=False,
                        details={"provider_mode": provider_mode},
                    )

            budget_context = redacted_request.get("budget_context") or {}
            if not isinstance(budget_context, dict):
                raise GatewayError(
                    ErrorCategories.VALIDATION,
                    "budget_context_invalid",
                    "budget_context must be an object when provided",
                    retryable=False,
                )

            per_request_cap = float(
                budget_context.get("per_request_cap", self.per_request_cap)
            )
            session_cap = float(budget_context.get("session_cap", self.session_cap))
            # Prefer request-provided session_spent only as override for first ledger init;
            # ongoing ledger is authoritative for multi-call sessions on this instance.
            if "session_spent" in budget_context and self.ledger.session_spent == 0.0:
                requested_spent = float(budget_context["session_spent"])
                if requested_spent < 0:
                    raise GatewayError(
                        ErrorCategories.BUDGET,
                        "budget_negative_balance",
                        "session_spent must be non-negative",
                        retryable=False,
                    )
                self.ledger = SessionBudgetLedger(session_spent=requested_spent)

            est = estimate_budget(snapshot, {"request_id": request_id})
            estimate = float(est["estimate"])
            check_budget(
                estimate,
                per_request_cap,
                session_cap,
                self.ledger.session_spent,
            )

            # --- 4. (idempotency already checked) Provider interface call ---
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

            # --- 6. Validate decision + re-redact deny list ---
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

            # --- 7. Return untrusted proposal; charge budget only on success ---
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
                    "per_request_cap": per_request_cap,
                    "session_cap": session_cap,
                },
                "fields_stripped_count": len(stripped_fields),
            }
            # Gateway never invokes World Commit or sets confirmation confirmed
            assert self.world_commit_invoked is False

            self.idempotency.put(request_id, response)
            if gateway_request_id and gateway_request_id != request_id:
                self.idempotency.put(gateway_request_id, response)
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
            # Store failed completed outcomes for true idempotency of terminal failures
            # only when request_id present and category is non-retryable terminal
            if request_id and exc.category in (
                ErrorCategories.VALIDATION,
                ErrorCategories.POLICY,
                ErrorCategories.BUDGET,
                ErrorCategories.RETRY_EXHAUSTED,
            ):
                # Do not cache validation failures that were incomplete requests without id —
                # we already require request_id above for most paths
                self.idempotency.put(request_id, envelope)
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

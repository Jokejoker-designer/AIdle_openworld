"""Budget estimate and hard caps — server-owned authority, reject before provider dispatch."""

from __future__ import annotations

import json
import math
import numbers
from typing import Any

from .errors import ErrorCategories, GatewayError


DEFAULT_PER_REQUEST_CAP = 100.0
DEFAULT_SESSION_CAP = 1000.0
# Deterministic unit estimate floor for a minimal valid snapshot turn
BASE_ESTIMATE = 1.0
# Scale by payload size (chars of JSON) — fixture-stable, not real billing
CHARS_PER_UNIT = 4000.0


def estimate_budget(snapshot: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, float]:
    """Compute non-negative estimate for this request before dispatch."""
    del context  # reserved for future token-model estimates
    try:
        size = len(json.dumps(snapshot, separators=(",", ":"), sort_keys=True))
    except (TypeError, ValueError):
        size = 0
    estimate = BASE_ESTIMATE + (size / CHARS_PER_UNIT)
    if estimate < 0 or not math.isfinite(estimate):
        estimate = 0.0
    return {"estimate": float(estimate)}


def parse_budget_number(value: Any, field_name: str) -> float:
    """Parse a budget field: finite non-negative real number; reject bool/NaN/Inf/non-numeric."""
    # bool is a subclass of int — must reject before numbers.Real check would accept True/False
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise GatewayError(
            ErrorCategories.BUDGET,
            "budget_type_invalid",
            f"{field_name} must be a finite non-negative number",
            retryable=False,
            details={"field": field_name, "value_type": type(value).__name__},
        )
    number = float(value)
    if not math.isfinite(number):
        raise GatewayError(
            ErrorCategories.BUDGET,
            "budget_non_finite",
            f"{field_name} must be finite (reject NaN and ±Infinity)",
            retryable=False,
            details={"field": field_name},
        )
    if number < 0:
        raise GatewayError(
            ErrorCategories.BUDGET,
            "budget_negative_balance",
            f"{field_name} must be non-negative",
            retryable=False,
            details={"field": field_name},
        )
    return number


def resolve_effective_caps(
    server_per_request_cap: float,
    server_session_cap: float,
    budget_context: dict[str, Any],
) -> tuple[float, float]:
    """Server caps are hard upper bounds; client may only request stricter (lower) caps.

    Client session_spent is validated when present but NEVER used as ledger authority.
    Returns (effective_per_request_cap, effective_session_cap).
    """
    server_pr = parse_budget_number(server_per_request_cap, "server_per_request_cap")
    server_sc = parse_budget_number(server_session_cap, "server_session_cap")

    effective_pr = server_pr
    effective_sc = server_sc

    if "per_request_cap" in budget_context:
        client_pr = parse_budget_number(
            budget_context["per_request_cap"], "per_request_cap"
        )
        effective_pr = min(server_pr, client_pr)

    if "session_cap" in budget_context:
        client_sc = parse_budget_number(budget_context["session_cap"], "session_cap")
        effective_sc = min(server_sc, client_sc)

    # Validate client session_spent type if provided; ignore for authority (server ledger only)
    if "session_spent" in budget_context:
        parse_budget_number(budget_context["session_spent"], "session_spent")

    return effective_pr, effective_sc


def check_budget(
    estimate: float,
    per_request_cap: float,
    session_cap: float,
    session_spent: float,
) -> dict[str, Any]:
    """Return {ok:true} or raise GatewayError with category=budget."""
    for name, value in (
        ("estimate", estimate),
        ("per_request_cap", per_request_cap),
        ("session_cap", session_cap),
        ("session_spent", session_spent),
    ):
        if isinstance(value, bool) or not isinstance(value, numbers.Real):
            raise GatewayError(
                ErrorCategories.BUDGET,
                "budget_type_invalid",
                f"{name} must be a finite non-negative number",
                retryable=False,
                details={"field": name},
            )
        if not math.isfinite(float(value)):
            raise GatewayError(
                ErrorCategories.BUDGET,
                "budget_non_finite",
                f"{name} must be finite",
                retryable=False,
                details={"field": name},
            )
        if float(value) < 0:
            raise GatewayError(
                ErrorCategories.BUDGET,
                "budget_negative_balance",
                "Budget values must be non-negative",
                retryable=False,
                details={"field": name, name: float(value)},
            )

    estimate_f = float(estimate)
    per_request_cap_f = float(per_request_cap)
    session_cap_f = float(session_cap)
    session_spent_f = float(session_spent)

    if estimate_f > per_request_cap_f:
        raise GatewayError(
            ErrorCategories.BUDGET,
            "budget_per_request_exceeded",
            "Request estimate exceeds per_request_cap",
            retryable=False,
            details={
                "estimate": estimate_f,
                "per_request_cap": per_request_cap_f,
            },
        )
    if session_spent_f + estimate_f > session_cap_f:
        raise GatewayError(
            ErrorCategories.BUDGET,
            "budget_session_exceeded",
            "Session cap would be exceeded",
            retryable=False,
            details={
                "estimate": estimate_f,
                "session_spent": session_spent_f,
                "session_cap": session_cap_f,
            },
        )
    return {"ok": True}


class SessionBudgetLedger:
    """In-memory session spend tracker. Failed pre-dispatch rejects do not charge.

    Server-owned: client budget_context.session_spent must never reset/replace this ledger.
    """

    def __init__(self, session_spent: float = 0.0) -> None:
        spent = parse_budget_number(session_spent, "session_spent")
        self._spent = spent

    @property
    def session_spent(self) -> float:
        return self._spent

    def charge(self, amount: float) -> float:
        amount_f = parse_budget_number(amount, "charge_amount")
        self._spent += amount_f
        return self._spent

"""Budget estimate and hard caps — reject before provider dispatch."""

from __future__ import annotations

import json
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
    if estimate < 0:
        estimate = 0.0
    return {"estimate": float(estimate)}


def check_budget(
    estimate: float,
    per_request_cap: float,
    session_cap: float,
    session_spent: float,
) -> dict[str, Any]:
    """Return {ok:true} or raise GatewayError with category=budget."""
    if estimate < 0 or session_spent < 0:
        raise GatewayError(
            ErrorCategories.BUDGET,
            "budget_negative_balance",
            "Budget values must be non-negative",
            retryable=False,
            details={
                "estimate": estimate,
                "session_spent": session_spent,
            },
        )
    if estimate > per_request_cap:
        raise GatewayError(
            ErrorCategories.BUDGET,
            "budget_per_request_exceeded",
            "Request estimate exceeds per_request_cap",
            retryable=False,
            details={
                "estimate": estimate,
                "per_request_cap": per_request_cap,
            },
        )
    if session_spent + estimate > session_cap:
        raise GatewayError(
            ErrorCategories.BUDGET,
            "budget_session_exceeded",
            "Session cap would be exceeded",
            retryable=False,
            details={
                "estimate": estimate,
                "session_spent": session_spent,
                "session_cap": session_cap,
            },
        )
    return {"ok": True}


class SessionBudgetLedger:
    """In-memory session spend tracker. Failed pre-dispatch rejects do not charge."""

    def __init__(self, session_spent: float = 0.0) -> None:
        if session_spent < 0:
            raise ValueError("session_spent must be non-negative")
        self._spent = float(session_spent)

    @property
    def session_spent(self) -> float:
        return self._spent

    def charge(self, amount: float) -> float:
        if amount < 0:
            raise ValueError("charge amount must be non-negative")
        self._spent += float(amount)
        return self._spent

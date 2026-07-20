"""Structured AGM gateway error envelopes (no secrets, no raw prompts)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class ErrorCategories:
    VALIDATION = "validation"
    POLICY = "policy"
    BUDGET = "budget"
    TIMEOUT = "timeout"
    RETRY_EXHAUSTED = "retry_exhausted"
    PROVIDER_UNAVAILABLE = "provider_unavailable"

    ALL = frozenset(
        {
            VALIDATION,
            POLICY,
            BUDGET,
            TIMEOUT,
            RETRY_EXHAUSTED,
            PROVIDER_UNAVAILABLE,
        }
    )


RETRYABLE_CATEGORIES = frozenset(
    {
        ErrorCategories.TIMEOUT,
        ErrorCategories.PROVIDER_UNAVAILABLE,
    }
)

NON_RETRYABLE_CATEGORIES = frozenset(
    {
        ErrorCategories.VALIDATION,
        ErrorCategories.POLICY,
        ErrorCategories.BUDGET,
        ErrorCategories.RETRY_EXHAUSTED,
    }
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_error_envelope(
    *,
    category: str,
    code: str,
    message: str,
    request_id: str | None = None,
    trace_id: str | None = None,
    retryable: bool | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if category not in ErrorCategories.ALL:
        raise ValueError(f"unknown error category: {category}")

    if retryable is None:
        retryable = category in RETRYABLE_CATEGORIES

    envelope: dict[str, Any] = {
        "ok": False,
        "error": True,
        "category": category,
        "code": code,
        "message": message,
        "request_id": request_id or "",
        "trace_id": trace_id or "",
        "retryable": bool(retryable),
        "occurred_at": utc_now_iso(),
    }
    if details is not None:
        # details must never carry raw deny-list values; caller responsibility
        envelope["details"] = details
    return envelope


class GatewayError(Exception):
    """Internal typed failure mapped to an error envelope."""

    def __init__(
        self,
        category: str,
        code: str,
        message: str,
        *,
        retryable: bool | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.code = code
        self.message = message
        self.retryable = (
            retryable
            if retryable is not None
            else category in RETRYABLE_CATEGORIES
        )
        self.details = details


class ProviderTimeout(GatewayError):
    def __init__(self, message: str = "provider timed out", **kwargs: Any) -> None:
        super().__init__(
            ErrorCategories.TIMEOUT,
            "provider_timeout",
            message,
            retryable=True,
            **kwargs,
        )


class ProviderUnavailable(GatewayError):
    def __init__(
        self, message: str = "provider unavailable", **kwargs: Any
    ) -> None:
        super().__init__(
            ErrorCategories.PROVIDER_UNAVAILABLE,
            "provider_unavailable",
            message,
            retryable=True,
            **kwargs,
        )


class ProviderProtocolError(GatewayError):
    """Non-retryable provider protocol / payload failure."""

    def __init__(
        self, message: str = "provider protocol error", **kwargs: Any
    ) -> None:
        super().__init__(
            ErrorCategories.VALIDATION,
            "provider_protocol_error",
            message,
            retryable=False,
            **kwargs,
        )

"""Bounded retry policy: only timeout / provider_unavailable are retryable."""

from __future__ import annotations

from typing import Callable, TypeVar

from .errors import (
    ErrorCategories,
    GatewayError,
    ProviderTimeout,
    ProviderUnavailable,
    RETRYABLE_CATEGORIES,
)

T = TypeVar("T")

DEFAULT_MAX_ATTEMPTS = 3  # including first attempt
DEFAULT_TIMEOUT_MS = 5000


class RetryPolicy:
    def __init__(
        self,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        self.max_attempts = int(max_attempts)
        self.timeout_ms = int(timeout_ms)

    def is_retryable(self, exc: BaseException) -> bool:
        if isinstance(exc, (ProviderTimeout, ProviderUnavailable)):
            return True
        if isinstance(exc, GatewayError):
            return exc.category in RETRYABLE_CATEGORIES and exc.retryable
        return False

    def run(self, fn: Callable[[], T]) -> T:
        """Execute fn with bounded retries. Raises GatewayError(retry_exhausted) on failure."""
        last_exc: BaseException | None = None
        attempts = 0
        while attempts < self.max_attempts:
            attempts += 1
            try:
                return fn()
            except Exception as exc:  # noqa: BLE001 — map to gateway categories
                last_exc = exc
                if not self.is_retryable(exc):
                    raise
                if attempts >= self.max_attempts:
                    break
                # Deterministic fixed backoff placeholder (no sleep in unit tests path)
                continue

        category = ErrorCategories.RETRY_EXHAUSTED
        code = "retry_exhausted"
        message = "Retry budget exhausted"
        details: dict = {"attempts": attempts}
        if isinstance(last_exc, GatewayError):
            details["last_category"] = last_exc.category
            details["last_code"] = last_exc.code
            message = f"Retry budget exhausted after {last_exc.category}"
        raise GatewayError(
            category,
            code,
            message,
            retryable=False,
            details=details,
        )

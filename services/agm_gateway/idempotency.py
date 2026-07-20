"""In-memory idempotency store for gateway request_id / gateway_request_id."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


class IdempotencyStore:
    """Maps completed request keys to a deep-copied response fingerprint.

    No secrets should be stored; callers must only store safe envelopes.
    """

    def __init__(self) -> None:
        self._by_key: dict[str, dict[str, Any]] = {}

    def get(self, key: str) -> dict[str, Any] | None:
        if not key:
            return None
        hit = self._by_key.get(key)
        if hit is None:
            return None
        return deepcopy(hit)

    def put(self, key: str, response: dict[str, Any]) -> None:
        if not key:
            return
        self._by_key[key] = deepcopy(response)

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and key in self._by_key

    def __len__(self) -> int:
        return len(self._by_key)

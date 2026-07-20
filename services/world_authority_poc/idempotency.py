"""In-memory idempotency store: request_id → fingerprint + receipt."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal

LookupStatus = Literal["miss", "hit", "conflict"]


class IdempotencyStore:
    """Maps completed request_id to {fingerprint, receipt}."""

    def __init__(self) -> None:
        self._by_key: dict[str, dict[str, Any]] = {}

    def lookup(self, key: str, fingerprint: str) -> tuple[LookupStatus, dict[str, Any] | None]:
        if not key:
            return "miss", None
        hit = self._by_key.get(key)
        if hit is None:
            return "miss", None
        if hit.get("fingerprint") != fingerprint:
            return "conflict", None
        return "hit", deepcopy(hit["receipt"])

    def put(self, key: str, fingerprint: str, receipt: dict[str, Any]) -> None:
        if not key or not fingerprint:
            return
        self._by_key[key] = {
            "fingerprint": fingerprint,
            "receipt": deepcopy(receipt),
        }

    def get_record(self, key: str) -> dict[str, Any] | None:
        hit = self._by_key.get(key)
        if hit is None:
            return None
        return {
            "fingerprint": hit["fingerprint"],
            "receipt": deepcopy(hit["receipt"]),
        }

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and key in self._by_key

    def __len__(self) -> int:
        return len(self._by_key)

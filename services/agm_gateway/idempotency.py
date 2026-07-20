"""In-memory idempotency store with canonical request fingerprint binding."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Literal


FINGERPRINT_SCHEMA_VERSION = "aidle_gateway_idempotency_fp_v1"

LookupStatus = Literal["miss", "hit", "conflict"]


def canonical_json(obj: Any) -> str:
    """Deterministic compact JSON for hashing (sorted keys, UTF-8 safe)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_request_fingerprint(material: dict[str, Any]) -> str:
    """SHA-256 hex of canonical JSON material. Caller must pass redacted-only inputs."""
    payload = {"v": FINGERPRINT_SCHEMA_VERSION, **material}
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return digest


class IdempotencyStore:
    """Maps completed request keys to {fingerprint, response}.

    No secrets should be stored; callers must only store safe envelopes and
    fingerprints computed over redacted material.
    """

    def __init__(self) -> None:
        # key -> {"fingerprint": str, "response": dict}
        self._by_key: dict[str, dict[str, Any]] = {}

    def lookup(self, key: str, fingerprint: str) -> tuple[LookupStatus, dict[str, Any] | None]:
        """Return (status, response).

        - miss: key absent
        - hit: key present and fingerprint matches → deep-copied response
        - conflict: key present and fingerprint differs → (conflict, None)
        """
        if not key:
            return "miss", None
        hit = self._by_key.get(key)
        if hit is None:
            return "miss", None
        stored_fp = hit.get("fingerprint")
        if stored_fp != fingerprint:
            return "conflict", None
        return "hit", deepcopy(hit["response"])

    def get(self, key: str) -> dict[str, Any] | None:
        """Return stored response without fingerprint check (introspection/tests only)."""
        if not key:
            return None
        hit = self._by_key.get(key)
        if hit is None:
            return None
        return deepcopy(hit["response"])

    def get_record(self, key: str) -> dict[str, Any] | None:
        """Return {fingerprint, response} deep copy or None."""
        if not key:
            return None
        hit = self._by_key.get(key)
        if hit is None:
            return None
        return {
            "fingerprint": hit["fingerprint"],
            "response": deepcopy(hit["response"]),
        }

    def put(self, key: str, fingerprint: str, response: dict[str, Any]) -> None:
        if not key:
            return
        if not fingerprint:
            return
        self._by_key[key] = {
            "fingerprint": fingerprint,
            "response": deepcopy(response),
        }

    def fingerprints_in_store(self) -> list[str]:
        return [rec["fingerprint"] for rec in self._by_key.values()]

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and key in self._by_key

    def __len__(self) -> int:
        return len(self._by_key)

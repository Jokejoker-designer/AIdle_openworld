"""Provider-neutral interface. Real providers are HITL_REQUIRED / denied by default."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProviderInterface(ABC):
    """Provider-neutral generate_decision surface."""

    label: str = "abstract_provider"

    @abstractmethod
    def generate_decision(
        self, snapshot: dict[str, Any], context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Return a decision dict or raise ProviderTimeout / ProviderUnavailable / ProviderProtocolError."""
        raise NotImplementedError

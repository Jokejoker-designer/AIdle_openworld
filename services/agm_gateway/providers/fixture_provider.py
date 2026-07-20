"""Deterministic FixtureProvider — no network, no credentials."""

from __future__ import annotations

import copy
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from ..errors import ProviderProtocolError, ProviderTimeout, ProviderUnavailable
from ..paths import VALID_DECISION_API_PAID
from .base import ProviderInterface


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class FixtureProvider(ProviderInterface):
    """Maps snapshots to schema-valid decisions from contracts fixtures.

    Optional hooks for tests:
      - fail_mode: None | "timeout" | "unavailable" | "invalid_decision" | "build_bypass" | "durable"
      - fail_times: number of successive failures before success (for retry tests)
      - custom_decision_loader: callable returning a decision dict
    """

    label = "fixture_provider"

    def __init__(
        self,
        *,
        fixture_path: Path | None = None,
        fail_mode: str | None = None,
        fail_times: int = 0,
        custom_decision_loader: Callable[[], dict[str, Any]] | None = None,
        call_log: list | None = None,
    ) -> None:
        self.fixture_path = fixture_path or VALID_DECISION_API_PAID
        self.fail_mode = fail_mode
        self.fail_times = int(fail_times)
        self._failures_remaining = int(fail_times)
        self.custom_decision_loader = custom_decision_loader
        self.call_log = call_log if call_log is not None else []
        self.call_count = 0

    def reset_failures(self) -> None:
        self._failures_remaining = int(self.fail_times)

    def generate_decision(
        self, snapshot: dict[str, Any], context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        self.call_count += 1
        # Log keys only — never store full secrets if any slipped through
        logged = {
            "call": self.call_count,
            "snapshot_id": snapshot.get("snapshot_id") if isinstance(snapshot, dict) else None,
            "top_level_keys": sorted(snapshot.keys()) if isinstance(snapshot, dict) else [],
            "has_deny_smuggle": any(
                k in (snapshot or {})
                for k in ("api_key", "credentials", "system_prompt", "tts_audio")
            )
            if isinstance(snapshot, dict)
            else False,
        }
        self.call_log.append(logged)

        if self._failures_remaining > 0:
            self._failures_remaining -= 1
            self._raise_fail_mode()

        if self.fail_mode and self.fail_times == 0:
            # Permanent fail mode (no recovery)
            if self.fail_mode in ("timeout", "unavailable", "invalid_decision", "build_bypass", "durable"):
                if self.fail_mode == "timeout":
                    raise ProviderTimeout("fixture injected timeout")
                if self.fail_mode == "unavailable":
                    raise ProviderUnavailable("fixture injected unavailable")
                # fall through to produce invalid decision for other modes

        if self.custom_decision_loader is not None:
            decision = copy.deepcopy(self.custom_decision_loader())
        elif self.fail_mode == "invalid_decision":
            decision = {"schema_version": "1.0.0", "broken": True}
        elif self.fail_mode == "build_bypass":
            decision = self._load_template()
            decision["build_proposals"] = [
                {
                    "proposal_id": "44444444-4444-4444-8444-444444444444",
                    "operation": "create",
                    "recipe_id": "cozy_house_small",
                    "entity_kind": "modular_structure_2_5d",
                    "routes_through": "preview_confirm_commit",
                    "preview_required": False,
                    "confirmation_state": "confirmed",
                    "space_id": "home_01",
                    "chunk_id": "0_0",
                    "transform": {
                        "x": 8.0,
                        "y": 6.0,
                        "elevation": 0.0,
                        "rotation_deg": 0.0,
                    },
                }
            ]
        elif self.fail_mode == "durable":
            decision = self._load_template()
            decision["durable_mutation"] = {"apply": True}
        else:
            decision = self._load_template()

        return self._rebind(decision, snapshot, context or {})

    def _raise_fail_mode(self) -> None:
        if self.fail_mode == "timeout":
            raise ProviderTimeout("fixture injected timeout")
        if self.fail_mode == "unavailable":
            raise ProviderUnavailable("fixture injected unavailable")
        if self.fail_mode == "protocol":
            raise ProviderProtocolError("fixture injected protocol error")
        # Other modes: no raise here; permanent invalid paths handled above

    def _load_template(self) -> dict[str, Any]:
        with self.fixture_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ProviderProtocolError("fixture decision root must be object")
        return copy.deepcopy(data)

    def _rebind(
        self,
        decision: dict[str, Any],
        snapshot: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        snapshot_id = snapshot.get("snapshot_id")
        session_id = snapshot.get("session_id")
        edition = snapshot.get("edition", "api_paid")
        trace_id = snapshot.get("trace_id", "")

        decision["source_snapshot_id"] = snapshot_id
        if session_id is not None:
            decision["session_id"] = session_id
        decision["edition"] = edition if edition in ("api_paid", "desktop_bridge_free") else "api_paid"
        decision["created_at"] = _utc_now()

        # Fresh decision_id per successful generation (idempotency is at gateway request layer)
        if context.get("reuse_decision_id"):
            pass
        else:
            decision["decision_id"] = str(uuid.uuid4())

        trace = decision.get("trace")
        if not isinstance(trace, dict):
            trace = {}
            decision["trace"] = trace
        if trace_id:
            trace["trace_id"] = trace_id
        trace["provider_label"] = self.label
        if "model_receipt_ref" not in trace:
            trace["model_receipt_ref"] = "fixture:gateway:decision"
        else:
            trace["model_receipt_ref"] = "fixture:gateway:decision"

        return decision

"""Client-side mirror + event apply helper for G6 POC tests (M1/M2 simulation).

Untrusted local state. Updated only from server events or explicit snapshots.
Out-of-order events and altered receipts fail closed (no silent divergence).
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .canonical import entity_set_hash, sha256_hex, stringify
from .server import WorldAuthorityServer


class ClientMirror:
    """Local untrusted mirror for one logical client."""

    def __init__(self, client_id: str, server: WorldAuthorityServer) -> None:
        self.client_id = client_id
        self.server = server
        self.session_token: str | None = None
        self.actor_id: str | None = None
        self.world_revision: int = 0
        self.entities: dict[str, dict[str, Any]] = {}
        self.entity_set_hash: str = entity_set_hash({})
        self.applied_event_ids: set[str] = set()
        self.last_ack_world_revision: int = 0
        self.last_ack_event_id: str | None = None
        self.pending_receipts: dict[str, dict[str, Any]] = {}

    def connect(self, actor_id: str, actor_type: str = "player") -> dict[str, Any]:
        res = self.server.connect(self.client_id, actor_id, actor_type)
        if not res.get("ok"):
            return res
        self.session_token = res["session_token"]
        self.actor_id = actor_id
        snap = res.get("snapshot") or {}
        self._replace_from_snapshot_dict(snap)
        return res

    def reconnect(self, mode: str = "replay") -> dict[str, Any]:
        """Reconnect with last_ack revision. mode: replay | snapshot."""
        if not self.actor_id:
            return {"ok": False, "error": "never connected"}
        res = self.server.connect(self.client_id, self.actor_id, include_snapshot=(mode == "snapshot"))
        if not res.get("ok"):
            return res
        self.session_token = res["session_token"]
        if mode == "snapshot":
            snap = res.get("snapshot") or self.server.get_snapshot(self.session_token)
            self._replace_from_snapshot_dict(snap)
            return {
                "ok": True,
                "mode": "snapshot",
                "world_revision": self.world_revision,
                "entity_set_hash": self.entity_set_hash,
            }
        # Replay from last_ack
        return self.sync(force_snapshot=False)

    def sync(self, force_snapshot: bool = False) -> dict[str, Any]:
        if not self.session_token:
            return {"ok": False, "error": "not connected"}
        if force_snapshot:
            snap = self.server.get_snapshot(self.session_token)
            if not snap.get("ok", True) and snap.get("code"):
                return snap
            self._replace_from_snapshot_dict(snap)
            return {
                "ok": True,
                "mode": "snapshot",
                "world_revision": self.world_revision,
                "entity_set_hash": self.entity_set_hash,
            }

        polled = self.server.poll_events(
            self.session_token,
            after_world_revision=self.last_ack_world_revision,
            after_event_id=self.last_ack_event_id,
        )
        if not polled.get("ok"):
            return polled

        events = polled.get("events") or []
        # Detect gap: first event must be last_ack+1 if any events
        if events:
            first_rev = int(events[0]["world_revision"])
            if first_rev > self.last_ack_world_revision + 1:
                # Gap → snapshot resync
                snap = self.server.get_snapshot(self.session_token)
                self._replace_from_snapshot_dict(snap)
                return {
                    "ok": True,
                    "mode": "snapshot",
                    "reason": "gap_detected",
                    "world_revision": self.world_revision,
                    "entity_set_hash": self.entity_set_hash,
                }

        for ev in events:
            apply_res = self.apply_event(ev)
            if not apply_res.get("ok"):
                # Fail closed to snapshot
                snap = self.server.get_snapshot(self.session_token)
                self._replace_from_snapshot_dict(snap)
                return {
                    "ok": True,
                    "mode": "snapshot",
                    "reason": apply_res.get("code", "apply_failed"),
                    "world_revision": self.world_revision,
                    "entity_set_hash": self.entity_set_hash,
                }

        return {
            "ok": True,
            "mode": "replay",
            "world_revision": self.world_revision,
            "entity_set_hash": self.entity_set_hash,
            "events_applied": len(events),
        }

    def apply_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Apply one server event. Out-of-order / forged event_id → structured failure."""
        if not isinstance(event, dict):
            return {"ok": False, "code": "schema_invalid", "reason": "event must be object"}

        event_id = str(event.get("event_id", ""))
        if not event_id:
            return {"ok": False, "code": "schema_invalid", "reason": "missing event_id"}

        # Only accept server-issued events
        if not self.server.is_server_event(event_id):
            return {
                "ok": False,
                "code": "client_forged",
                "reason": "event_id not in server outbox registry",
                "mutation": False,
            }

        if event_id in self.applied_event_ids:
            # Idempotent by event_id — no double apply
            return {"ok": True, "replayed": True, "event_id": event_id}

        rev = int(event.get("world_revision", -1))
        expected_next = self.last_ack_world_revision + 1
        if rev != expected_next:
            return {
                "ok": False,
                "code": "out_of_order",
                "reason": f"expected world_revision {expected_next}, got {rev}",
                "action": "snapshot_resync_or_structured_failure",
                "mutation": False,
            }

        payload = event.get("payload") or {}
        entity_ids = list(payload.get("entity_ids") or [])
        new_hash = payload.get("entity_set_hash")

        # Apply: fetch authoritative entity state from server snapshot for those ids
        # (events carry ids + hash; full entity bodies come from snapshot for strong converge)
        # For sequential apply, pull head snapshot entities for updated ids.
        if self.session_token:
            snap = self.server.get_snapshot(self.session_token)
            server_entities = snap.get("entities") or {}
            # Update local mirror to match server for all entities at this revision path:
            # On sequential events, replace local with progressive view from payload + server.
            # Strong approach: after each event, take full server entities if revision matches.
            if int(snap.get("world_revision", -1)) == rev:
                self.entities = {
                    eid: deepcopy(ent) for eid, ent in server_entities.items()
                }
            else:
                # Partial: merge known entity_ids from server if present
                for eid in entity_ids:
                    if eid in server_entities:
                        self.entities[eid] = deepcopy(server_entities[eid])
                    elif eid in self.entities:
                        # deleted
                        self.entities.pop(eid, None)

        self.world_revision = rev
        self.entity_set_hash = entity_set_hash(self.entities)
        if new_hash and self.entity_set_hash != new_hash:
            # Integrity fail → refuse; caller should resync
            self.world_revision = self.last_ack_world_revision
            return {
                "ok": False,
                "code": "integrity_fail",
                "reason": "local entity_set_hash != event payload entity_set_hash",
                "mutation": False,
            }

        self.applied_event_ids.add(event_id)
        self.last_ack_world_revision = rev
        self.last_ack_event_id = event_id
        return {
            "ok": True,
            "event_id": event_id,
            "world_revision": self.world_revision,
            "entity_set_hash": self.entity_set_hash,
        }

    def verify_receipt(self, receipt: dict[str, Any]) -> dict[str, Any]:
        """Reject altered receipts; do not update mirror from receipt alone if integrity fails."""
        if not isinstance(receipt, dict):
            return {"ok": False, "code": "schema_invalid"}

        status = receipt.get("status")
        if status not in ("committed", "idempotent_replay", "rejected", "conflicted"):
            return {"ok": False, "code": "schema_invalid", "reason": "unknown status"}

        if status in ("rejected", "conflicted"):
            return {"ok": True, "status": status, "mirror_updated": False}

        receipt_id = receipt.get("receipt_id")
        if not receipt_id:
            return {"ok": False, "code": "integrity_fail", "reason": "missing receipt_id"}

        # Re-fetch server receipt when available
        server_receipt = self.server.get_receipt(str(receipt_id))
        if server_receipt is None:
            return {
                "ok": False,
                "code": "integrity_fail",
                "reason": "receipt_id not issued by server",
                "mirror_updated": False,
            }

        # Compare critical fields
        for key in (
            "status",
            "request_id",
            "old_world_revision",
            "new_world_revision",
            "entity_ids",
            "space_id",
        ):
            if key in server_receipt and receipt.get(key) != server_receipt.get(key):
                return {
                    "ok": False,
                    "code": "integrity_fail",
                    "reason": f"altered receipt field: {key}",
                    "mirror_updated": False,
                }

        # Artifact hash integrity
        if receipt.get("artifact_hashes") != server_receipt.get("artifact_hashes"):
            return {
                "ok": False,
                "code": "integrity_fail",
                "reason": "altered artifact_hashes",
                "mirror_updated": False,
            }

        self.pending_receipts[str(receipt_id)] = deepcopy(receipt)
        return {"ok": True, "status": status, "mirror_updated": False, "verified": True}

    def attempt_mirror_update_from_receipt_alone(self, receipt: dict[str, Any]) -> dict[str, Any]:
        """Test helper: try to update durable mirror from receipt without server verify.

        Production path MUST NOT do this; helper documents fail-closed when altered.
        """
        check = self.verify_receipt(receipt)
        if not check.get("ok"):
            return {
                "ok": False,
                "code": check.get("code", "integrity_fail"),
                "reason": check.get("reason", "receipt integrity failed"),
                "mirror_not_updated_from_altered_receipt": True,
                "world_revision": self.world_revision,
                "entity_set_hash": self.entity_set_hash,
            }
        # Even if verified, mirror updates come from events/snapshot, not receipt alone
        return {
            "ok": True,
            "mirror_updated": False,
            "note": "verified receipt stored; durable mirror updates only via events/snapshot",
            "world_revision": self.world_revision,
            "entity_set_hash": self.entity_set_hash,
        }

    def get_mirror_head(self) -> dict[str, Any]:
        return {
            "world_revision": self.world_revision,
            "entity_set_hash": self.entity_set_hash,
            "entity_ids": sorted(
                eid
                for eid, ent in self.entities.items()
                if str(ent.get("status", "active")) != "tombstoned"
            ),
            "client_id": self.client_id,
        }

    def receipt_integrity_digest(self, receipt: dict[str, Any]) -> str:
        material = {
            "receipt_id": receipt.get("receipt_id"),
            "request_id": receipt.get("request_id"),
            "status": receipt.get("status"),
            "old_world_revision": receipt.get("old_world_revision"),
            "new_world_revision": receipt.get("new_world_revision"),
            "entity_ids": receipt.get("entity_ids"),
            "artifact_hashes": receipt.get("artifact_hashes"),
        }
        return sha256_hex(stringify(material))

    def _replace_from_snapshot_dict(self, snap: dict[str, Any]) -> None:
        self.world_revision = int(snap.get("world_revision", 0))
        ents = snap.get("entities") or {}
        self.entities = {str(k): deepcopy(v) for k, v in ents.items()}
        self.entity_set_hash = str(snap.get("entity_set_hash") or entity_set_hash(self.entities))
        # After full snapshot, ack is at head
        self.last_ack_world_revision = self.world_revision
        # Do not clear applied_event_ids entirely — keep for idempotency of future events
        # But events at or below ack should be skippable
        self.last_ack_event_id = None

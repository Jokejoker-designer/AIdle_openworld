"""In-process World Authority server (G6-001 M1).

Owns world_revision, entity set, ownership, commit receipts, and event outbox.
No public socket bind. Clients propose; only this service commits.
"""

from __future__ import annotations

import secrets
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from .canonical import compute_fingerprint, entity_hash, entity_set_hash, stringify
from .idempotency import IdempotencyStore
from .validators import validate_commit_request, validate_world_prompt

DEFAULT_SPACE_ID = "home_01"
POC_SOURCE_ALLOWED = frozenset({"server_authoritative"})


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _new_uuid() -> str:
    return str(uuid.uuid4())


class WorldAuthorityServer:
    """Local authoritative World Commit simulator (in-process only)."""

    def __init__(self, space_id: str = DEFAULT_SPACE_ID, seed_world_revision: int = 0) -> None:
        self.space_id = space_id
        self._world_revision = int(seed_world_revision)
        # entity_id -> entity dict (includes owner_id for ownership; not in set hash)
        self._entities: dict[str, dict[str, Any]] = {}
        # session_token -> {client_id, actor_id, actor_type, session_id}
        self._sessions: dict[str, dict[str, Any]] = {}
        # client_id -> session_token (single active session per client for POC)
        self._client_tokens: dict[str, str] = {}
        # request_id -> proposal record
        self._proposals: dict[str, dict[str, Any]] = {}
        self._idempotency = IdempotencyStore()
        # ordered outbox of event envelopes
        self._outbox: list[dict[str, Any]] = []
        # event_id registry (server-issued only)
        self._event_ids: set[str] = set()
        # receipt_id -> receipt
        self._receipts: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------ API

    def connect(
        self,
        client_id: str,
        actor_id: str,
        actor_type: str = "player",
        *,
        include_snapshot: bool = True,
    ) -> dict[str, Any]:
        if not client_id or not actor_id:
            return {"ok": False, "error": "client_id and actor_id required"}
        if actor_type not in ("player", "companion", "system"):
            return {"ok": False, "error": "invalid actor_type"}

        # Reconnect: reissue token for same client_id, keep actor binding
        old = self._client_tokens.get(client_id)
        if old and old in self._sessions:
            del self._sessions[old]

        token = f"tok_{client_id}_{secrets.token_hex(8)}"
        session_id = f"sess_{client_id}"
        self._sessions[token] = {
            "client_id": client_id,
            "actor_id": actor_id,
            "actor_type": actor_type,
            "session_id": session_id,
        }
        self._client_tokens[client_id] = token

        result: dict[str, Any] = {
            "ok": True,
            "session_token": token,
            "client_id": client_id,
            "actor_id": actor_id,
            "session_id": session_id,
            "world_revision": self._world_revision,
            "entity_set_hash": self.entity_set_hash(),
            "space_id": self.space_id,
        }
        if include_snapshot:
            result["snapshot"] = self._build_snapshot()
        return result

    def submit_proposal(self, session_token: str, world_prompt: dict[str, Any]) -> dict[str, Any]:
        session = self._auth(session_token)
        if session is None:
            return self._error_envelope("auth_failed", "invalid or missing session_token")

        v = validate_world_prompt(world_prompt)
        if not v["ok"]:
            return {
                "ok": False,
                "status": "rejected",
                "code": "schema_invalid",
                "errors": v["errors"],
                "world_revision": self._world_revision,
                "entity_set_hash": self.entity_set_hash(),
            }

        prompt = deepcopy(world_prompt)
        request_id = str(prompt["request_id"])
        actor_player = str(prompt.get("actor", {}).get("player_id", ""))

        # Session-bound actor: player commits must match registered actor
        if session["actor_type"] == "player" and actor_player != session["actor_id"]:
            return {
                "ok": False,
                "status": "rejected",
                "code": "client_forged",
                "reason": "world_prompt.actor.player_id does not match session actor",
                "world_revision": self._world_revision,
                "entity_set_hash": self.entity_set_hash(),
            }

        conf = prompt.get("confirmation") or {}
        if conf.get("preview_required") is not True:
            return {
                "ok": False,
                "status": "rejected",
                "code": "schema_invalid",
                "reason": "preview_required must be true",
                "world_revision": self._world_revision,
                "entity_set_hash": self.entity_set_hash(),
            }

        # INV-CONFIRM-SERVER-TRANSITION: client-supplied confirmation.state=confirmed
        # is NEVER authoritative on submit. Fail closed BEFORE proposal registration.
        # Only session-bound confirm_proposal may transition pending → confirmed.
        if conf.get("state") == "confirmed":
            return {
                "ok": False,
                "status": "rejected",
                "code": "client_forged",
                "reason": (
                    "confirmation.state=confirmed is not accepted on submit; "
                    "only confirm_proposal may confirm"
                ),
                "retryable": False,
                "world_revision": self._world_revision,
                "entity_set_hash": self.entity_set_hash(),
            }

        # Valid submit always enters pending; strip any client-supplied confirmed_by
        prompt.setdefault("confirmation", {})
        prompt["confirmation"]["state"] = "pending"
        prompt["confirmation"].pop("confirmed_by", None)
        state = "pending"

        space_id = str(prompt.get("target", {}).get("space_id", ""))
        if space_id != self.space_id:
            return {
                "ok": False,
                "status": "rejected",
                "code": "policy",
                "reason": f"space_id mismatch: expected {self.space_id}",
                "world_revision": self._world_revision,
                "entity_set_hash": self.entity_set_hash(),
            }

        if request_id in self._proposals:
            existing = self._proposals[request_id]
            # Same request_id re-submit with different body → conflict closed
            if stringify(existing["prompt"]) != stringify(prompt):
                return {
                    "ok": False,
                    "status": "rejected",
                    "code": "policy",
                    "reason": "duplicate request_id with different proposal body",
                    "world_revision": self._world_revision,
                    "entity_set_hash": self.entity_set_hash(),
                }
            return {
                "ok": True,
                "request_id": request_id,
                "status": existing["state"],
                "world_revision": self._world_revision,
                "entity_set_hash": self.entity_set_hash(),
            }

        self._proposals[request_id] = {
            "prompt": prompt,
            "state": state,
            "client_id": session["client_id"],
            "actor_id": session["actor_id"],
            "submitted_at": _utcnow_iso(),
        }
        # No entity mutation, no revision bump
        return {
            "ok": True,
            "request_id": request_id,
            "status": state,
            "world_revision": self._world_revision,
            "entity_set_hash": self.entity_set_hash(),
        }

    def confirm_proposal(
        self,
        session_token: str,
        request_id: str,
        confirmed_by: str,
    ) -> dict[str, Any]:
        session = self._auth(session_token)
        if session is None:
            return self._error_envelope("auth_failed", "invalid or missing session_token")

        prop = self._proposals.get(request_id)
        if prop is None:
            return {
                "ok": False,
                "status": "rejected",
                "code": "policy",
                "reason": "unknown request_id",
                "world_revision": self._world_revision,
                "entity_set_hash": self.entity_set_hash(),
            }

        if prop["client_id"] != session["client_id"]:
            return {
                "ok": False,
                "status": "rejected",
                "code": "client_forged",
                "reason": "proposal owned by another client",
                "world_revision": self._world_revision,
                "entity_set_hash": self.entity_set_hash(),
            }

        if confirmed_by != session["actor_id"]:
            return {
                "ok": False,
                "status": "rejected",
                "code": "client_forged",
                "reason": "confirmed_by does not match session actor",
                "world_revision": self._world_revision,
                "entity_set_hash": self.entity_set_hash(),
            }

        if prop["state"] == "confirmed":
            return {
                "ok": True,
                "request_id": request_id,
                "confirmation_state": "confirmed",
                "world_revision": self._world_revision,
                "entity_set_hash": self.entity_set_hash(),
            }

        prompt = prop["prompt"]
        prompt.setdefault("confirmation", {})
        prompt["confirmation"]["state"] = "confirmed"
        prompt["confirmation"]["confirmed_by"] = confirmed_by
        # Re-bind expected revision to current head at confirm time (M0 policy)
        prompt.setdefault("target", {})
        prompt["target"]["expected_world_revision"] = self._world_revision
        prop["state"] = "confirmed"
        prop["confirmed_at"] = _utcnow_iso()

        return {
            "ok": True,
            "request_id": request_id,
            "confirmation_state": "confirmed",
            "world_revision": self._world_revision,
            "entity_set_hash": self.entity_set_hash(),
        }

    def commit(
        self,
        session_token: str,
        commit_request: dict[str, Any],
        *,
        claimed_client_id: str | None = None,
    ) -> dict[str, Any]:
        """Commit pipeline. Server stamps authority; ignores client-asserted issuer power.

        claimed_client_id: optional explicit client_id claim for forge tests. When set and
        mismatched with session.client_id → rejected client_forged (no mutation).
        """
        session = self._auth(session_token)
        if session is None:
            return self._make_receipt_rejected(
                commit_request if isinstance(commit_request, dict) else {},
                code="auth_failed",
                reason="invalid or missing session_token",
            )

        if claimed_client_id is not None and claimed_client_id != session["client_id"]:
            return self._make_receipt_rejected(
                commit_request if isinstance(commit_request, dict) else {},
                code="client_forged",
                reason=f"claimed client_id={claimed_client_id} does not match session client_id",
                old_revision=self._world_revision,
            )

        if not isinstance(commit_request, dict):
            return self._make_receipt_rejected(
                {},
                code="schema_invalid",
                reason="commit_request must be an object",
                old_revision=self._world_revision,
            )

        # Schema validate (client_authoritative / wrong commit_path fail here)
        v = validate_commit_request(commit_request)
        if not v["ok"]:
            return self._make_receipt_rejected(
                commit_request,
                code="schema_invalid",
                reason="; ".join(v["errors"][:8]) or "schema_invalid",
                old_revision=self._world_revision,
            )

        req = deepcopy(commit_request)
        request_id = str(req["request_id"])
        prompt_id = str(req["prompt_id"])
        space_id = str(req["space_id"])
        expected_rev = int(req["expected_world_revision"])
        actor_id = str(req["actor"]["actor_id"])
        confirmed_by = str(req["confirmation"]["confirmed_by"])
        mutation_class = str(req["mutation_class"])
        source = str(req.get("authority", {}).get("source", ""))

        # POC allows only server_authoritative for durable two-client path
        if source not in POC_SOURCE_ALLOWED:
            return self._make_receipt_rejected(
                req,
                code="policy",
                reason=f"authority.source={source} not allowed in G6 POC (server_authoritative only)",
                old_revision=self._world_revision,
            )

        # Session / actor checks (server does not trust client authority labels for admission)
        if actor_id != session["actor_id"]:
            return self._make_receipt_rejected(
                req,
                code="client_forged",
                reason="actor.actor_id does not match session actor",
                old_revision=self._world_revision,
            )
        if confirmed_by != session["actor_id"]:
            return self._make_receipt_rejected(
                req,
                code="client_forged",
                reason="confirmation.confirmed_by does not match session actor",
                old_revision=self._world_revision,
            )
        if req.get("actor", {}).get("actor_type") != session["actor_type"]:
            return self._make_receipt_rejected(
                req,
                code="client_forged",
                reason="actor.actor_type does not match session",
                old_revision=self._world_revision,
            )

        if space_id != self.space_id:
            return self._make_receipt_rejected(
                req,
                code="policy",
                reason=f"space_id mismatch: expected {self.space_id}",
                old_revision=self._world_revision,
            )

        # Bind to confirmed world_prompt
        prop = self._proposals.get(request_id)
        if prop is None:
            return self._make_receipt_rejected(
                req,
                code="confirmation_missing",
                reason="no registered proposal for request_id",
                old_revision=self._world_revision,
            )
        if prop["state"] != "confirmed":
            return self._make_receipt_rejected(
                req,
                code="confirmation_missing",
                reason="proposal not confirmed",
                old_revision=self._world_revision,
            )
        prompt = prop["prompt"]
        if str(prompt.get("prompt_id")) != prompt_id:
            return self._make_receipt_rejected(
                req,
                code="policy",
                reason="prompt_id does not match registered proposal",
                old_revision=self._world_revision,
            )
        if str(prompt.get("target", {}).get("space_id")) != space_id:
            return self._make_receipt_rejected(
                req,
                code="policy",
                reason="space_id does not match proposal target",
                old_revision=self._world_revision,
            )
        if prop["actor_id"] != session["actor_id"] or prop["client_id"] != session["client_id"]:
            return self._make_receipt_rejected(
                req,
                code="client_forged",
                reason="proposal/session actor or client mismatch",
                old_revision=self._world_revision,
            )

        # Fingerprint over confirmed prompt + commit-affecting fields
        fingerprint = self._fingerprint(req, prompt)

        # Idempotency BEFORE revision check so same-payload replay is not
        # misclassified as revision_mismatch after the original advanced head.
        status, prior = self._idempotency.lookup(request_id, fingerprint)
        if status == "hit" and prior is not None:
            replay = deepcopy(prior)
            replay["status"] = "idempotent_replay"
            replay["occurred_at"] = _utcnow_iso()
            replay["idempotency"] = {
                "duplicate_of_request_id": request_id,
                "prior_receipt_id": prior["receipt_id"],
                "replayed": True,
            }
            replay.pop("rejection", None)
            replay.pop("conflict", None)
            return replay
        if status == "conflict":
            return self._make_receipt_rejected(
                req,
                code="policy",
                reason="idempotency payload mismatch for request_id",
                old_revision=self._world_revision,
            )

        # Ownership / operation apply prep (before revision so ownership fails closed cleanly)
        op = str(prompt.get("operation", "create"))
        ownership_err = self._check_ownership(op, prompt, session["actor_id"])
        if ownership_err is not None:
            return self._make_receipt_rejected(
                req,
                code="ownership",
                reason=ownership_err,
                old_revision=self._world_revision,
            )

        # Revision check (only for first-time apply of this request_id)
        if expected_rev != self._world_revision:
            return self._make_receipt_conflicted(
                req,
                expected=expected_rev,
                actual=self._world_revision,
            )

        # Apply mutation atomically
        old_rev = self._world_revision
        entity_ids, apply_err = self._apply_mutation(op, prompt, session["actor_id"], request_id)
        if apply_err is not None:
            return self._make_receipt_rejected(
                req,
                code="policy",
                reason=apply_err,
                old_revision=self._world_revision,
            )

        self._world_revision = old_rev + 1
        new_rev = self._world_revision
        set_hash = self.entity_set_hash()

        receipt_id = _new_uuid()
        set_hash_artifact = {
            "role": "entity_set",
            "algorithm": "sha256",
            "hash": set_hash,
        }
        entity_artifacts = [
            {
                "role": "entity_snapshot",
                "algorithm": "sha256",
                "hash": entity_hash(self._entities[eid]) if eid in self._entities else sha256_placeholder(),
            }
            for eid in entity_ids
            if eid in self._entities
        ]
        # For deletes, still record empty entity snapshot role via set hash only
        artifact_hashes = entity_artifacts + [set_hash_artifact]

        receipt: dict[str, Any] = {
            "schema_version": "1.0.0",
            "receipt_id": receipt_id,
            "request_id": request_id,
            "status": "committed",
            "occurred_at": _utcnow_iso(),
            "space_id": self.space_id,
            "authority": {
                "commit_path": "world_commit_service",
                "issuer": "world_commit_service",
            },
            "old_world_revision": old_rev,
            "new_world_revision": new_rev,
            "entity_ids": list(entity_ids),
            "artifact_hashes": artifact_hashes,
            "trace_id": str(req.get("trace_id") or f"trace-{request_id[:8]}"),
        }
        self._receipts[receipt_id] = deepcopy(receipt)
        self._idempotency.put(request_id, fingerprint, receipt)

        # Outbox event (server fields only — never copy client payload wholesale)
        event = self._append_outbox_event(
            request_id=request_id,
            actor_id=session["actor_id"],
            world_revision=new_rev,
            receipt=receipt,
            entity_set_hash=set_hash,
            trace_id=receipt["trace_id"],
        )
        # Attach event_id on a non-schema extension for tests (receipt stays contract-clean)
        receipt_out = deepcopy(receipt)
        receipt_out["_event_id"] = event["event_id"]
        receipt_out["_entity_set_hash"] = set_hash
        return receipt_out

    def get_snapshot(self, session_token: str, space_id: str | None = None) -> dict[str, Any]:
        session = self._auth(session_token)
        if session is None:
            return self._error_envelope("auth_failed", "invalid or missing session_token")
        if space_id is not None and space_id != self.space_id:
            return {
                "ok": False,
                "code": "policy",
                "reason": f"unknown space_id {space_id}",
            }
        snap = self._build_snapshot()
        snap["ok"] = True
        return snap

    def poll_events(
        self,
        session_token: str,
        after_world_revision: int,
        after_event_id: str | None = None,
    ) -> dict[str, Any]:
        session = self._auth(session_token)
        if session is None:
            return self._error_envelope("auth_failed", "invalid or missing session_token")

        events: list[dict[str, Any]] = []
        started = after_event_id is None
        for ev in self._outbox:
            rev = int(ev["world_revision"])
            if rev <= after_world_revision:
                continue
            if after_event_id is not None and not started:
                if ev["event_id"] == after_event_id:
                    started = True
                continue
            events.append(deepcopy(ev))

        return {
            "ok": True,
            "events": events,
            "head_world_revision": self._world_revision,
            "head_entity_set_hash": self.entity_set_hash(),
        }

    def get_head(self, session_token: str) -> dict[str, Any]:
        session = self._auth(session_token)
        if session is None:
            return self._error_envelope("auth_failed", "invalid or missing session_token")
        return {
            "ok": True,
            "world_revision": self._world_revision,
            "entity_set_hash": self.entity_set_hash(),
        }

    # ---- Forbidden durable APIs (fail closed) ----

    def client_write_entity(self, *_args: Any, **_kwargs: Any) -> dict[str, Any]:
        """There is no durable client write path. Always reject with zero mutation."""
        return {
            "ok": False,
            "status": "rejected",
            "code": "client_forged",
            "reason": "direct client entity write is forbidden; use preview→confirm→commit",
            "world_revision": self._world_revision,
            "entity_set_hash": self.entity_set_hash(),
            "mutation": False,
        }

    def client_set_world_revision(self, *_args: Any, **_kwargs: Any) -> dict[str, Any]:
        return {
            "ok": False,
            "status": "rejected",
            "code": "client_forged",
            "reason": "clients may not set world_revision",
            "world_revision": self._world_revision,
            "entity_set_hash": self.entity_set_hash(),
            "mutation": False,
        }

    def client_issue_receipt(self, *_args: Any, **_kwargs: Any) -> dict[str, Any]:
        return {
            "ok": False,
            "status": "rejected",
            "code": "client_forged",
            "reason": "only world_commit_service may issue receipts",
            "world_revision": self._world_revision,
            "entity_set_hash": self.entity_set_hash(),
            "mutation": False,
        }

    def client_publish_event(self, *_args: Any, **_kwargs: Any) -> dict[str, Any]:
        return {
            "ok": False,
            "status": "rejected",
            "code": "client_forged",
            "reason": "only server outbox may publish authoritative events",
            "world_revision": self._world_revision,
            "entity_set_hash": self.entity_set_hash(),
            "mutation": False,
        }

    # ---- Introspection (tests / client sim) ----

    def entity_set_hash(self) -> str:
        return entity_set_hash(self._entities)

    def world_revision(self) -> int:
        return self._world_revision

    def entity_count(self) -> int:
        return sum(
            1
            for e in self._entities.values()
            if str(e.get("status", "active")) != "tombstoned"
        )

    def get_entity(self, entity_id: str) -> dict[str, Any] | None:
        ent = self._entities.get(entity_id)
        return deepcopy(ent) if ent else None

    def get_receipt(self, receipt_id: str) -> dict[str, Any] | None:
        r = self._receipts.get(receipt_id)
        return deepcopy(r) if r else None

    def is_server_event(self, event_id: str) -> bool:
        return event_id in self._event_ids

    def outbox_len(self) -> int:
        return len(self._outbox)

    # ------------------------------------------------------------------ internals

    def _auth(self, session_token: str | None) -> dict[str, Any] | None:
        if not session_token:
            return None
        return self._sessions.get(session_token)

    def _error_envelope(self, code: str, reason: str) -> dict[str, Any]:
        return {
            "ok": False,
            "code": code,
            "reason": reason,
            "world_revision": self._world_revision,
            "entity_set_hash": self.entity_set_hash(),
        }

    def _build_snapshot(self) -> dict[str, Any]:
        entities = {
            eid: deepcopy(ent)
            for eid, ent in self._entities.items()
            if str(ent.get("status", "active")) != "tombstoned"
        }
        return {
            "world_revision": self._world_revision,
            "entities": entities,
            "entity_set_hash": self.entity_set_hash(),
            "space_id": self.space_id,
        }

    def _fingerprint(self, req: dict[str, Any], prompt: dict[str, Any]) -> str:
        material = {
            "request_id": str(req["request_id"]),
            "prompt_id": str(req["prompt_id"]),
            "space_id": str(req["space_id"]),
            "mutation_class": str(req["mutation_class"]),
            "actor_id": str(req["actor"]["actor_id"]),
            "confirmed_world_prompt": prompt,
        }
        return compute_fingerprint(material)

    def _check_ownership(self, op: str, prompt: dict[str, Any], actor_id: str) -> str | None:
        if op in ("create", "enrich", "gift_proposal"):
            return None
        if op in ("modify", "delete"):
            eid = prompt.get("target", {}).get("entity_id")
            if not eid:
                return "modify/delete requires target.entity_id"
            ent = self._entities.get(str(eid))
            if ent is None or str(ent.get("status", "active")) == "tombstoned":
                return f"entity not found: {eid}"
            owner = str(ent.get("owner_id", ""))
            if owner != actor_id:
                return f"actor {actor_id} does not own entity {eid} (owner={owner})"
        return None

    def _apply_mutation(
        self,
        op: str,
        prompt: dict[str, Any],
        actor_id: str,
        request_id: str,
    ) -> tuple[list[str], str | None]:
        target = prompt.get("target") or {}
        entity_body = prompt.get("entity") or {}
        space_id = str(target.get("space_id", self.space_id))
        chunk_id = str(target.get("chunk_id", "0_0"))
        prompt_id = str(prompt.get("prompt_id", ""))

        if op == "create":
            eid = f"ent_{request_id.replace('-', '')[:12]}"
            if eid in self._entities and str(self._entities[eid].get("status")) != "tombstoned":
                return [], f"entity id collision: {eid}"
            ent = {
                "entity_id": eid,
                "kind": entity_body.get("kind"),
                "recipe_id": entity_body.get("recipe_id"),
                "transform": deepcopy(entity_body.get("transform") or {}),
                "bounds": deepcopy(entity_body.get("bounds") or {}),
                "interaction_tags": list(entity_body.get("interaction_tags") or []),
                "space_id": space_id,
                "chunk_id": chunk_id,
                "status": "active",
                "origin_request_id": request_id,
                "origin_prompt_id": prompt_id,
                "owner_id": actor_id,
            }
            self._entities[eid] = ent
            return [eid], None

        if op == "modify":
            eid = str(target.get("entity_id"))
            ent = self._entities[eid]
            ent["kind"] = entity_body.get("kind", ent.get("kind"))
            ent["recipe_id"] = entity_body.get("recipe_id", ent.get("recipe_id"))
            if entity_body.get("transform"):
                ent["transform"] = deepcopy(entity_body["transform"])
            if entity_body.get("bounds"):
                ent["bounds"] = deepcopy(entity_body["bounds"])
            if "interaction_tags" in entity_body:
                ent["interaction_tags"] = list(entity_body.get("interaction_tags") or [])
            return [eid], None

        if op == "delete":
            eid = str(target.get("entity_id"))
            self._entities[eid]["status"] = "tombstoned"
            return [eid], None

        if op in ("enrich", "gift_proposal"):
            # POC: treat as no-op durable entity change (still bumps revision via commit path)
            # Prefer creating a marker only for enrich if entity_id present
            eid = target.get("entity_id")
            if eid and eid in self._entities:
                return [str(eid)], None
            return [], None

        return [], f"unsupported operation: {op}"

    def _append_outbox_event(
        self,
        *,
        request_id: str,
        actor_id: str,
        world_revision: int,
        receipt: dict[str, Any],
        entity_set_hash: str,
        trace_id: str,
    ) -> dict[str, Any]:
        event_id = _new_uuid()
        event: dict[str, Any] = {
            "event_id": event_id,
            "event_type": "world.mutation_committed",
            "event_version": "1.0.0",
            "occurred_at": receipt["occurred_at"],
            "request_id": request_id,
            "space_id": self.space_id,
            "world_revision": world_revision,
            "actor_id": actor_id,
            "payload": {
                "receipt_id": receipt["receipt_id"],
                "entity_ids": list(receipt.get("entity_ids") or []),
                "old_world_revision": receipt["old_world_revision"],
                "new_world_revision": receipt["new_world_revision"],
                "entity_set_hash": entity_set_hash,
            },
            "trace_id": trace_id,
        }
        self._outbox.append(event)
        self._event_ids.add(event_id)
        return event

    def _make_receipt_rejected(
        self,
        req: dict[str, Any],
        *,
        code: str,
        reason: str,
        old_revision: int | None = None,
    ) -> dict[str, Any]:
        request_id = str(req.get("request_id") or "00000000-0000-4000-8000-000000000000")
        # Ensure request_id looks like uuid for receipt shape when missing
        try:
            uuid.UUID(request_id)
        except ValueError:
            request_id = "00000000-0000-4000-8000-000000000000"
        receipt: dict[str, Any] = {
            "schema_version": "1.0.0",
            "receipt_id": _new_uuid(),
            "request_id": request_id,
            "status": "rejected",
            "occurred_at": _utcnow_iso(),
            "space_id": str(req.get("space_id") or self.space_id),
            "authority": {
                "commit_path": "world_commit_service",
                "issuer": "world_commit_service",
            },
            "rejection": {"code": code, "reason": reason[:512]},
        }
        if old_revision is not None:
            receipt["old_world_revision"] = old_revision
        if req.get("trace_id"):
            receipt["trace_id"] = str(req["trace_id"])
        return receipt

    def _make_receipt_conflicted(
        self,
        req: dict[str, Any],
        *,
        expected: int,
        actual: int,
    ) -> dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "receipt_id": _new_uuid(),
            "request_id": str(req["request_id"]),
            "status": "conflicted",
            "occurred_at": _utcnow_iso(),
            "space_id": str(req.get("space_id") or self.space_id),
            "authority": {
                "commit_path": "world_commit_service",
                "issuer": "world_commit_service",
            },
            "old_world_revision": actual,
            "conflict": {
                "code": "revision_mismatch",
                "expected_world_revision": expected,
                "actual_world_revision": actual,
                "diff_ref": f"conflict_diff://{self.space_id}/rev_{expected}_vs_{actual}",
            },
            "trace_id": str(req.get("trace_id") or f"trace-conflict-{expected}"),
        }


def sha256_placeholder() -> str:
    return "0" * 64

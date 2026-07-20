"""G6-001 M1 full test matrix for local World Authority POC."""

from __future__ import annotations

import copy
import unittest
import uuid
from typing import Any

from services.world_authority_poc.client_sim import ClientMirror
from services.world_authority_poc.server import WorldAuthorityServer


def _uuid() -> str:
    return str(uuid.uuid4())


def make_create_prompt(
    *,
    actor_id: str = "player_a",
    request_id: str | None = None,
    prompt_id: str | None = None,
    expected_world_revision: int = 0,
    space_id: str = "home_01",
    recipe_id: str = "cozy_house_small",
    state: str = "pending",
    confirmed_by: str | None = None,
    x: float = 8,
) -> dict[str, Any]:
    conf: dict[str, Any] = {
        "preview_required": True,
        "state": state,
        "rollback_window_seconds": 3600,
    }
    if state == "confirmed":
        conf["confirmed_by"] = confirmed_by or actor_id
    return {
        "schema_version": "1.1.0",
        "prompt_id": prompt_id or _uuid(),
        "request_id": request_id or _uuid(),
        "session_id": f"session_{actor_id}",
        "actor": {"player_id": actor_id, "companion_id": "companion_lumi"},
        "operation": "create",
        "target": {
            "space_type": "private_reality",
            "space_id": space_id,
            "chunk_id": "0_0",
            "expected_world_revision": expected_world_revision,
        },
        "style_profile": {
            "profile_id": "cozy_default",
            "profile_version": "1.0.0",
            "base_concept": "cozy_cyber_pixel_2_5d",
            "surrealism_budget": 0.15,
        },
        "entity": {
            "kind": "modular_structure_2_5d",
            "recipe_id": recipe_id,
            "transform": {"x": x, "y": 6, "elevation": 0, "rotation_deg": 0},
            "bounds": {"width": 8, "depth": 6, "height": 5},
            "interaction_tags": ["enterable", "lightable"],
        },
        "manifestation": {
            "stages": ["wireframe", "hologram", "materializing", "complete"],
            "presentation_duration_seconds": 12,
        },
        "budget": {
            "max_compute_units": 200,
            "max_entities": 32,
            "paid_compute_allowed": False,
        },
        "provenance": {
            "source_type": "player_request",
            "requested_by": actor_id,
            "generated_by": "companion_lumi",
            "created_at": "2026-07-20T15:00:00Z",
        },
        "confirmation": conf,
    }


def make_modify_prompt(
    *,
    actor_id: str,
    entity_id: str,
    expected_world_revision: int,
    request_id: str | None = None,
    prompt_id: str | None = None,
    space_id: str = "home_01",
) -> dict[str, Any]:
    p = make_create_prompt(
        actor_id=actor_id,
        request_id=request_id,
        prompt_id=prompt_id,
        expected_world_revision=expected_world_revision,
        space_id=space_id,
        recipe_id="garden_lamp_warm",
    )
    p["operation"] = "modify"
    p["target"]["entity_id"] = entity_id
    p["entity"]["kind"] = "prop_2_5d"
    p["entity"]["bounds"] = {"width": 0.5, "depth": 0.5, "height": 1.8}
    p["entity"]["interaction_tags"] = ["lightable", "toggleable"]
    return p


def make_commit_request(
    *,
    request_id: str,
    prompt_id: str,
    actor_id: str = "player_a",
    expected_world_revision: int = 0,
    space_id: str = "home_01",
    source: str = "server_authoritative",
    commit_path: str = "world_commit_service",
    confirmed_by: str | None = None,
    mutation_class: str = "durable_world",
    include_confirmation: bool = True,
) -> dict[str, Any]:
    req: dict[str, Any] = {
        "schema_version": "1.0.0",
        "request_id": request_id,
        "prompt_id": prompt_id,
        "session_id": f"sess_{actor_id}",
        "space_id": space_id,
        "expected_world_revision": expected_world_revision,
        "actor": {"actor_id": actor_id, "actor_type": "player"},
        "authority": {
            "commit_path": commit_path,
            "source": source,
            "durable_mutation": True,
        },
        "mutation_class": mutation_class,
        "trace_id": f"trace-{request_id[:8]}",
    }
    if include_confirmation:
        req["confirmation"] = {
            "state": "confirmed",
            "confirmed_by": confirmed_by or actor_id,
        }
    return req


def valid_commit_flow(
    server: WorldAuthorityServer,
    token: str,
    actor_id: str = "player_a",
    *,
    expected_world_revision: int | None = None,
    recipe_id: str = "cozy_house_small",
    x: float = 8,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    head = server.get_head(token)
    rev = (
        head["world_revision"]
        if expected_world_revision is None
        else expected_world_revision
    )
    prompt = make_create_prompt(
        actor_id=actor_id,
        expected_world_revision=rev,
        recipe_id=recipe_id,
        x=x,
    )
    sub = server.submit_proposal(token, prompt)
    assert sub.get("ok"), sub
    conf = server.confirm_proposal(token, prompt["request_id"], actor_id)
    assert conf.get("ok"), conf
    # After confirm, expected rev re-bound to head
    head2 = server.get_head(token)
    creq = make_commit_request(
        request_id=prompt["request_id"],
        prompt_id=prompt["prompt_id"],
        actor_id=actor_id,
        expected_world_revision=head2["world_revision"],
    )
    receipt = server.commit(token, creq)
    return prompt, creq, receipt


class TestWorldAuthorityPoc(unittest.TestCase):
    def setUp(self) -> None:
        self.server = WorldAuthorityServer(space_id="home_01", seed_world_revision=0)
        self.a = self.server.connect("client_a", "player_a", "player")
        self.b = self.server.connect("client_b", "player_b", "player")
        self.tok_a = self.a["session_token"]
        self.tok_b = self.b["session_token"]

    # ---------- TM-VALID-COMMIT-CONVERGE ----------

    def test_tm_valid_commit_converge(self) -> None:
        mirror_a = ClientMirror("client_a", self.server)
        mirror_b = ClientMirror("client_b", self.server)
        # reconnect using existing server sessions by re-connect
        mirror_a.connect("player_a")
        mirror_b.connect("player_b")
        self.tok_a = mirror_a.session_token  # type: ignore[assignment]
        self.tok_b = mirror_b.session_token  # type: ignore[assignment]

        r0 = self.server.world_revision()
        h0 = self.server.entity_set_hash()
        self.assertEqual(r0, 0)
        self.assertEqual(self.server.entity_count(), 0)

        _prompt, _creq, receipt = valid_commit_flow(
            self.server, self.tok_a, "player_a"
        )
        self.assertEqual(receipt["status"], "committed")
        self.assertEqual(receipt["old_world_revision"], r0)
        self.assertEqual(receipt["new_world_revision"], r0 + 1)
        self.assertEqual(len(receipt["entity_ids"]), 1)
        self.assertEqual(
            receipt["authority"],
            {"commit_path": "world_commit_service", "issuer": "world_commit_service"},
        )
        self.assertEqual(self.server.entity_count(), 1)
        self.assertEqual(self.server.outbox_len(), 1)

        # Client B converges via poll
        sync_b = mirror_b.sync()
        self.assertTrue(sync_b.get("ok"), sync_b)
        head_s = self.server.get_head(self.tok_a)
        head_a = mirror_a.sync()
        head_b = mirror_b.get_mirror_head()
        self.assertEqual(head_s["world_revision"], head_b["world_revision"])
        self.assertEqual(head_s["entity_set_hash"], head_b["entity_set_hash"])
        self.assertEqual(head_a["world_revision"], head_b["world_revision"])
        self.assertEqual(head_a["entity_set_hash"], head_b["entity_set_hash"])
        self.assertNotEqual(h0, head_s["entity_set_hash"])

    # ---------- TM-DIRECT-WRITE-REJECT ----------

    def test_tm_direct_write_reject(self) -> None:
        r0 = self.server.world_revision()
        h0 = self.server.entity_set_hash()
        res = self.server.client_write_entity(self.tok_a, {"entity_id": "hack"})
        self.assertFalse(res.get("ok"))
        self.assertEqual(res.get("code"), "client_forged")
        self.assertEqual(self.server.world_revision(), r0)
        self.assertEqual(self.server.entity_set_hash(), h0)
        self.assertFalse(res.get("mutation", True))

        for method in (
            self.server.client_set_world_revision,
            self.server.client_issue_receipt,
            self.server.client_publish_event,
        ):
            out = method(self.tok_a)
            self.assertFalse(out.get("ok"))
            self.assertEqual(self.server.world_revision(), r0)

    # ---------- TM-FORGED-ACTOR-REJECT ----------

    def test_tm_forged_actor_reject(self) -> None:
        prompt = make_create_prompt(actor_id="player_a")
        self.assertTrue(self.server.submit_proposal(self.tok_a, prompt).get("ok"))
        self.assertTrue(
            self.server.confirm_proposal(self.tok_a, prompt["request_id"], "player_a").get("ok")
        )
        r0 = self.server.world_revision()
        h0 = self.server.entity_set_hash()

        # actor claims player_b under client_a session
        creq = make_commit_request(
            request_id=prompt["request_id"],
            prompt_id=prompt["prompt_id"],
            actor_id="player_b",
            confirmed_by="player_b",
            expected_world_revision=r0,
        )
        receipt = self.server.commit(self.tok_a, creq)
        self.assertEqual(receipt["status"], "rejected")
        self.assertIn(receipt["rejection"]["code"], ("client_forged", "auth_failed", "ownership"))
        self.assertEqual(self.server.world_revision(), r0)
        self.assertEqual(self.server.entity_set_hash(), h0)

        # confirmed_by forged while actor matches
        creq2 = make_commit_request(
            request_id=prompt["request_id"],
            prompt_id=prompt["prompt_id"],
            actor_id="player_a",
            confirmed_by="player_b",
            expected_world_revision=r0,
        )
        receipt2 = self.server.commit(self.tok_a, creq2)
        self.assertEqual(receipt2["status"], "rejected")
        self.assertEqual(receipt2["rejection"]["code"], "client_forged")
        self.assertEqual(self.server.world_revision(), r0)

    # ---------- TM-FORGED-CLIENT-REJECT ----------

    def test_tm_forged_client_reject(self) -> None:
        prompt = make_create_prompt(actor_id="player_a")
        self.assertTrue(self.server.submit_proposal(self.tok_a, prompt).get("ok"))
        self.assertTrue(
            self.server.confirm_proposal(self.tok_a, prompt["request_id"], "player_a").get("ok")
        )
        r0 = self.server.world_revision()
        creq = make_commit_request(
            request_id=prompt["request_id"],
            prompt_id=prompt["prompt_id"],
            actor_id="player_a",
            expected_world_revision=r0,
        )
        receipt = self.server.commit(
            self.tok_a, creq, claimed_client_id="client_b"
        )
        self.assertEqual(receipt["status"], "rejected")
        self.assertIn(receipt["rejection"]["code"], ("client_forged", "auth_failed"))
        self.assertEqual(self.server.world_revision(), r0)

    # ---------- TM-FORGED-OWNER-REJECT ----------

    def test_tm_forged_owner_reject(self) -> None:
        _p, _c, receipt = valid_commit_flow(self.server, self.tok_a, "player_a")
        self.assertEqual(receipt["status"], "committed")
        eid = receipt["entity_ids"][0]
        r1 = self.server.world_revision()
        h1 = self.server.entity_set_hash()

        mod = make_modify_prompt(
            actor_id="player_b",
            entity_id=eid,
            expected_world_revision=r1,
        )
        self.assertTrue(self.server.submit_proposal(self.tok_b, mod).get("ok"))
        self.assertTrue(
            self.server.confirm_proposal(self.tok_b, mod["request_id"], "player_b").get("ok")
        )
        creq = make_commit_request(
            request_id=mod["request_id"],
            prompt_id=mod["prompt_id"],
            actor_id="player_b",
            expected_world_revision=self.server.world_revision(),
        )
        bad = self.server.commit(self.tok_b, creq)
        self.assertEqual(bad["status"], "rejected")
        self.assertEqual(bad["rejection"]["code"], "ownership")
        self.assertEqual(self.server.world_revision(), r1)
        self.assertEqual(self.server.entity_set_hash(), h1)

    # ---------- TM-CLIENT-AUTHORITATIVE-SCHEMA-REJECT ----------

    def test_tm_client_authoritative_schema_reject(self) -> None:
        prompt = make_create_prompt(actor_id="player_a")
        self.server.submit_proposal(self.tok_a, prompt)
        self.server.confirm_proposal(self.tok_a, prompt["request_id"], "player_a")
        r0 = self.server.world_revision()

        creq = make_commit_request(
            request_id=prompt["request_id"],
            prompt_id=prompt["prompt_id"],
            actor_id="player_a",
            expected_world_revision=r0,
            source="client_authoritative",
        )
        receipt = self.server.commit(self.tok_a, creq)
        self.assertEqual(receipt["status"], "rejected")
        self.assertIn(
            receipt["rejection"]["code"],
            (
                "schema_invalid",
                "client_forged",
                "client_authoritative_durable_forbidden",
            ),
        )
        self.assertEqual(self.server.world_revision(), r0)

        creq2 = make_commit_request(
            request_id=prompt["request_id"],
            prompt_id=prompt["prompt_id"],
            actor_id="player_a",
            expected_world_revision=r0,
            commit_path="client_local",
            source="server_authoritative",
        )
        # commit_path const world_commit_service → schema_invalid
        # but source must also be valid enum - use client_local path only
        creq2["authority"] = {
            "commit_path": "client_local",
            "source": "client_authoritative",
            "durable_mutation": True,
        }
        receipt2 = self.server.commit(self.tok_a, creq2)
        self.assertEqual(receipt2["status"], "rejected")
        self.assertEqual(self.server.world_revision(), r0)

    # ---------- TM-STALE-REVISION-CONFLICT ----------

    def test_tm_stale_revision_conflict(self) -> None:
        prompt = make_create_prompt(actor_id="player_a", expected_world_revision=0)
        self.server.submit_proposal(self.tok_a, prompt)
        self.server.confirm_proposal(self.tok_a, prompt["request_id"], "player_a")
        # Advance world via another commit first
        valid_commit_flow(self.server, self.tok_a, "player_a", x=1)
        r_head = self.server.world_revision()
        h_head = self.server.entity_set_hash()

        creq = make_commit_request(
            request_id=prompt["request_id"],
            prompt_id=prompt["prompt_id"],
            actor_id="player_a",
            expected_world_revision=0,  # stale
        )
        receipt = self.server.commit(self.tok_a, creq)
        self.assertEqual(receipt["status"], "conflicted")
        self.assertEqual(receipt["conflict"]["code"], "revision_mismatch")
        self.assertEqual(receipt["conflict"]["expected_world_revision"], 0)
        self.assertEqual(receipt["conflict"]["actual_world_revision"], r_head)
        self.assertEqual(self.server.world_revision(), r_head)
        self.assertEqual(self.server.entity_set_hash(), h_head)

    # ---------- TM-INVALID-SCHEMA-REJECT ----------

    def test_tm_invalid_schema_reject(self) -> None:
        r0 = self.server.world_revision()
        bad_prompt = make_create_prompt(actor_id="player_a")
        bad_prompt["schema_version"] = "9.9.9"
        sub = self.server.submit_proposal(self.tok_a, bad_prompt)
        self.assertFalse(sub.get("ok"))
        self.assertEqual(sub.get("code"), "schema_invalid")
        self.assertEqual(self.server.world_revision(), r0)

        # commit missing confirmation
        good = make_create_prompt(actor_id="player_a")
        self.server.submit_proposal(self.tok_a, good)
        self.server.confirm_proposal(self.tok_a, good["request_id"], "player_a")
        creq = make_commit_request(
            request_id=good["request_id"],
            prompt_id=good["prompt_id"],
            actor_id="player_a",
            include_confirmation=False,
        )
        receipt = self.server.commit(self.tok_a, creq)
        self.assertEqual(receipt["status"], "rejected")
        self.assertEqual(receipt["rejection"]["code"], "schema_invalid")
        self.assertEqual(self.server.world_revision(), r0)

    # ---------- TM-UNCONFIRMED-REJECT ----------

    def test_tm_unconfirmed_reject(self) -> None:
        prompt = make_create_prompt(actor_id="player_a")
        self.assertTrue(self.server.submit_proposal(self.tok_a, prompt).get("ok"))
        # skip confirm
        r0 = self.server.world_revision()
        creq = make_commit_request(
            request_id=prompt["request_id"],
            prompt_id=prompt["prompt_id"],
            actor_id="player_a",
            expected_world_revision=r0,
        )
        receipt = self.server.commit(self.tok_a, creq)
        self.assertEqual(receipt["status"], "rejected")
        self.assertEqual(receipt["rejection"]["code"], "confirmation_missing")
        self.assertEqual(self.server.world_revision(), r0)
        self.assertEqual(self.server.entity_count(), 0)

    # ---------- TM-IDEMPOTENT-REPLAY-SAME-PAYLOAD ----------

    def test_tm_idempotent_replay_same_payload(self) -> None:
        prompt, creq, receipt = valid_commit_flow(self.server, self.tok_a, "player_a")
        self.assertEqual(receipt["status"], "committed")
        rid = receipt["receipt_id"]
        r1 = self.server.world_revision()
        h1 = self.server.entity_set_hash()
        count1 = self.server.entity_count()
        outbox1 = self.server.outbox_len()

        replay = self.server.commit(self.tok_a, creq)
        self.assertEqual(replay["status"], "idempotent_replay")
        self.assertTrue(replay["idempotency"]["replayed"])
        self.assertEqual(replay["idempotency"]["prior_receipt_id"], rid)
        self.assertEqual(replay["old_world_revision"], receipt["old_world_revision"])
        self.assertEqual(replay["new_world_revision"], receipt["new_world_revision"])
        self.assertEqual(replay["entity_ids"], receipt["entity_ids"])
        self.assertEqual(self.server.world_revision(), r1)
        self.assertEqual(self.server.entity_set_hash(), h1)
        self.assertEqual(self.server.entity_count(), count1)
        self.assertEqual(self.server.outbox_len(), outbox1)

    # ---------- TM-IDEMPOTENCY-PAYLOAD-CONFLICT ----------

    def test_tm_idempotency_payload_conflict(self) -> None:
        prompt, creq, receipt = valid_commit_flow(
            self.server, self.tok_a, "player_a", recipe_id="cozy_house_small", x=8
        )
        self.assertEqual(receipt["status"], "committed")
        r1 = self.server.world_revision()
        h1 = self.server.entity_set_hash()
        count1 = self.server.entity_count()

        # Same request_id, different payload fingerprint via different registered prompt body.
        # Server stores original confirmed prompt; changing only commit fields that are in
        # fingerprint (mutation_class) still conflicts if fingerprint material differs.
        # To get different fingerprint with same request_id we must have stored a different
        # confirmed prompt — which the store won't allow for different body on same key.
        # Approach: fingerprint includes confirmed prompt; we cannot re-register different
        # body. Instead mutate mutation_class on commit (included in fingerprint).
        creq2 = copy.deepcopy(creq)
        creq2["mutation_class"] = "compensating"
        bad = self.server.commit(self.tok_a, creq2)
        self.assertNotEqual(bad.get("status"), "committed")
        self.assertEqual(bad["status"], "rejected")
        self.assertEqual(bad["rejection"]["code"], "policy")
        self.assertIn("idempotency", bad["rejection"]["reason"].lower())
        self.assertEqual(self.server.world_revision(), r1)
        self.assertEqual(self.server.entity_set_hash(), h1)
        self.assertEqual(self.server.entity_count(), count1)

    # ---------- TM-OUT-OF-ORDER-EVENT ----------

    def test_tm_out_of_order_event(self) -> None:
        mirror_b = ClientMirror("client_b", self.server)
        mirror_b.connect("player_b")
        self.tok_a = self.server.connect("client_a", "player_a")["session_token"]

        # Two commits from A
        valid_commit_flow(self.server, self.tok_a, "player_a", x=1)
        valid_commit_flow(self.server, self.tok_a, "player_a", x=2)
        polled = self.server.poll_events(mirror_b.session_token, after_world_revision=0)
        events = polled["events"]
        self.assertGreaterEqual(len(events), 2)

        # Deliver R+2 before R+1
        e2 = events[1]
        res = mirror_b.apply_event(e2)
        self.assertFalse(res.get("ok"))
        self.assertEqual(res.get("code"), "out_of_order")
        self.assertEqual(res.get("action"), "snapshot_resync_or_structured_failure")
        # Mirror still at 0
        self.assertEqual(mirror_b.world_revision, 0)

        # Resync converges
        sync = mirror_b.sync(force_snapshot=True)
        self.assertTrue(sync.get("ok"))
        head = self.server.get_head(mirror_b.session_token)
        self.assertEqual(mirror_b.world_revision, head["world_revision"])
        self.assertEqual(mirror_b.entity_set_hash, head["entity_set_hash"])

    # ---------- TM-ALTERED-RECEIPT ----------

    def test_tm_altered_receipt(self) -> None:
        mirror_a = ClientMirror("client_a", self.server)
        mirror_a.connect("player_a")
        self.tok_a = mirror_a.session_token  # type: ignore[assignment]

        _p, _c, receipt = valid_commit_flow(self.server, self.tok_a, "player_a")
        self.assertEqual(receipt["status"], "committed")
        before = mirror_a.get_mirror_head()

        altered = copy.deepcopy(receipt)
        altered["new_world_revision"] = 999
        if altered.get("artifact_hashes"):
            altered["artifact_hashes"] = copy.deepcopy(altered["artifact_hashes"])
            altered["artifact_hashes"][0]["hash"] = "a" * 64

        res = mirror_a.attempt_mirror_update_from_receipt_alone(altered)
        self.assertFalse(res.get("ok"))
        self.assertTrue(res.get("mirror_not_updated_from_altered_receipt"))
        after = mirror_a.get_mirror_head()
        self.assertEqual(before["world_revision"], after["world_revision"])
        self.assertEqual(before["entity_set_hash"], after["entity_set_hash"])

    # ---------- TM-RECONNECT-REPLAY ----------

    def test_tm_reconnect_replay(self) -> None:
        mirror_b = ClientMirror("client_b", self.server)
        mirror_b.connect("player_b")
        # Fresh token for A after B connected
        ca = self.server.connect("client_a", "player_a")
        self.tok_a = ca["session_token"]

        r0 = mirror_b.world_revision
        self.assertEqual(r0, 0)

        _p, _c, receipt = valid_commit_flow(self.server, self.tok_a, "player_a")
        self.assertEqual(receipt["status"], "committed")

        # B "disconnects" without applying event, then reconnects with last_ack=0
        reconnect = mirror_b.reconnect(mode="replay")
        self.assertTrue(reconnect.get("ok"), reconnect)
        head = self.server.get_head(mirror_b.session_token)
        self.assertEqual(mirror_b.world_revision, head["world_revision"])
        self.assertEqual(mirror_b.entity_set_hash, head["entity_set_hash"])
        self.assertEqual(self.server.entity_count(), 1)
        # No double entity on second sync
        mirror_b.sync()
        self.assertEqual(self.server.entity_count(), 1)
        self.assertEqual(len(mirror_b.get_mirror_head()["entity_ids"]), 1)

    # ---------- TM-RECONNECT-SNAPSHOT-RESYNC ----------

    def test_tm_reconnect_snapshot_resync(self) -> None:
        mirror_b = ClientMirror("client_b", self.server)
        mirror_b.connect("player_b")
        ca = self.server.connect("client_a", "player_a")
        self.tok_a = ca["session_token"]

        valid_commit_flow(self.server, self.tok_a, "player_a", x=3)
        # Simulate missing/reordered: force snapshot path
        res = mirror_b.reconnect(mode="snapshot")
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("mode"), "snapshot")
        head = self.server.get_head(mirror_b.session_token)
        self.assertEqual(mirror_b.world_revision, head["world_revision"])
        self.assertEqual(mirror_b.entity_set_hash, head["entity_set_hash"])

    # ---------- TM-TWO-CLIENT-HEADLESS-SMOKE ----------

    def test_tm_two_client_headless_smoke(self) -> None:
        print("client_ids:", "client_a", "client_b")
        mirror_a = ClientMirror("client_a", self.server)
        mirror_b = ClientMirror("client_b", self.server)
        mirror_a.connect("player_a")
        mirror_b.connect("player_b")
        self.tok_a = mirror_a.session_token  # type: ignore[assignment]

        _p, _c, receipt = valid_commit_flow(self.server, self.tok_a, "player_a")
        self.assertEqual(receipt["status"], "committed")
        mirror_b.sync()
        self.assertEqual(mirror_b.world_revision, self.server.world_revision())
        self.assertEqual(mirror_b.entity_set_hash, self.server.entity_set_hash())

        # forged reject
        r_before = self.server.world_revision()
        forged = make_commit_request(
            request_id=_uuid(),
            prompt_id=_uuid(),
            actor_id="player_b",
            expected_world_revision=r_before,
        )
        # use A's token with B actor
        bad = self.server.commit(self.tok_a, forged)
        self.assertEqual(bad["status"], "rejected")
        self.assertEqual(self.server.world_revision(), r_before)

        # reconnect B
        rec = mirror_b.reconnect(mode="replay")
        self.assertTrue(rec.get("ok"))
        self.assertEqual(mirror_b.world_revision, self.server.world_revision())

    # ---------- TM-FORGED-LEAVES-PEER-UNCHANGED ----------

    def test_tm_forged_leaves_peer_unchanged(self) -> None:
        mirror_b = ClientMirror("client_b", self.server)
        mirror_b.connect("player_b")
        ca = self.server.connect("client_a", "player_a")
        self.tok_a = ca["session_token"]

        h = self.server.get_head(self.tok_a)
        forged = make_commit_request(
            request_id=_uuid(),
            prompt_id=_uuid(),
            actor_id="player_b",
            expected_world_revision=h["world_revision"],
        )
        bad = self.server.commit(self.tok_a, forged)
        self.assertEqual(bad["status"], "rejected")
        mirror_b.sync()
        h2 = self.server.get_head(self.tok_a)
        self.assertEqual(h2["world_revision"], h["world_revision"])
        self.assertEqual(h2["entity_set_hash"], h["entity_set_hash"])
        self.assertEqual(mirror_b.world_revision, h["world_revision"])
        self.assertEqual(mirror_b.entity_set_hash, h["entity_set_hash"])

    # ---------- Extra: fake event injection ----------

    def test_rc_fake_event(self) -> None:
        mirror_b = ClientMirror("client_b", self.server)
        mirror_b.connect("player_b")
        fake = {
            "event_id": _uuid(),
            "event_type": "world.mutation_committed",
            "event_version": "1.0.0",
            "occurred_at": "2026-07-20T12:00:00Z",
            "request_id": _uuid(),
            "space_id": "home_01",
            "world_revision": 1,
            "actor_id": "player_a",
            "payload": {
                "receipt_id": _uuid(),
                "entity_ids": ["ent_fake"],
                "old_world_revision": 0,
                "new_world_revision": 1,
                "entity_set_hash": "0" * 64,
            },
            "trace_id": "trace-fake",
        }
        res = mirror_b.apply_event(fake)
        self.assertFalse(res.get("ok"))
        self.assertEqual(res.get("code"), "client_forged")
        self.assertEqual(mirror_b.world_revision, 0)

    # ---------- Preview does not mutate ----------

    def test_submit_preview_no_mutation(self) -> None:
        r0 = self.server.world_revision()
        h0 = self.server.entity_set_hash()
        prompt = make_create_prompt(actor_id="player_a")
        sub = self.server.submit_proposal(self.tok_a, prompt)
        self.assertTrue(sub.get("ok"))
        self.assertEqual(sub.get("status"), "pending")
        self.assertEqual(self.server.world_revision(), r0)
        self.assertEqual(self.server.entity_set_hash(), h0)
        conf = self.server.confirm_proposal(self.tok_a, prompt["request_id"], "player_a")
        self.assertTrue(conf.get("ok"))
        self.assertEqual(self.server.world_revision(), r0)
        self.assertEqual(self.server.entity_count(), 0)

    # ---------- G6-001 CORRECTION-001: client-supplied confirmed on submit ----------

    def test_submit_rejects_client_supplied_confirmed_state(self) -> None:
        """Client-supplied confirmation.state=confirmed is rejected before registration."""
        r0 = self.server.world_revision()
        h0 = self.server.entity_set_hash()
        e0 = self.server.entity_count()
        o0 = self.server.outbox_len()
        receipts0 = len(self.server._receipts)

        prompt = make_create_prompt(
            actor_id="player_a",
            state="confirmed",
            confirmed_by="player_a",
        )
        request_id = prompt["request_id"]
        sub = self.server.submit_proposal(self.tok_a, prompt)

        self.assertFalse(sub.get("ok"))
        self.assertEqual(sub.get("status"), "rejected")
        self.assertEqual(sub.get("code"), "client_forged")
        self.assertNotEqual(sub.get("retryable"), True)
        self.assertIn("confirm_proposal", str(sub.get("reason", "")).lower())

        # No proposal authority for that request_id
        self.assertNotIn(request_id, self.server._proposals)

        # Zero side effects
        self.assertEqual(self.server.world_revision(), r0)
        self.assertEqual(self.server.entity_set_hash(), h0)
        self.assertEqual(self.server.entity_count(), e0)
        self.assertEqual(self.server.outbox_len(), o0)
        self.assertEqual(len(self.server._receipts), receipts0)
        self.assertFalse(
            any(r.get("request_id") == request_id for r in self.server._receipts.values())
        )

    def test_commit_without_confirm_proposal_after_confirmed_submit_attempt(self) -> None:
        """Bypass chain closed: rejected confirmed-submit leaves no commit path."""
        r0 = self.server.world_revision()
        h0 = self.server.entity_set_hash()
        e0 = self.server.entity_count()
        o0 = self.server.outbox_len()

        prompt = make_create_prompt(
            actor_id="player_a",
            state="confirmed",
            confirmed_by="player_a",
        )
        request_id = prompt["request_id"]
        sub = self.server.submit_proposal(self.tok_a, prompt)
        self.assertFalse(sub.get("ok"))
        self.assertEqual(sub.get("code"), "client_forged")
        self.assertNotIn(request_id, self.server._proposals)

        creq = make_commit_request(
            request_id=request_id,
            prompt_id=prompt["prompt_id"],
            actor_id="player_a",
            confirmed_by="player_a",
            expected_world_revision=r0,
        )
        receipt = self.server.commit(self.tok_a, creq)
        self.assertEqual(receipt["status"], "rejected")
        self.assertEqual(receipt["rejection"]["code"], "confirmation_missing")
        self.assertEqual(self.server.world_revision(), r0)
        self.assertEqual(self.server.entity_set_hash(), h0)
        self.assertEqual(self.server.entity_count(), e0)
        self.assertEqual(self.server.outbox_len(), o0)


if __name__ == "__main__":
    unittest.main()

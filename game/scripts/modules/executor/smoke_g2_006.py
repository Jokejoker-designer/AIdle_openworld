#!/usr/bin/env python3
"""G2-006 smoke: AGM decision allowlist/idempotency policy + export shape checks.

Mirrors runtime executor policy against contracts fixtures (no paid SDKs).
"""
from __future__ import annotations

import json
import sys
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[4]  # AIdle_openworld
EXECUTOR = Path(__file__).resolve().parent
EXPORTS = EXECUTOR / "exports"

ALLOWED_EVENT_TYPES = {
    "pacing.slow_down",
    "pacing.speed_up",
    "ambient.weather_hint",
    "ambient.time_of_day_hint",
    "narrative.beat",
    "companion.attention",
    "quest.hint",
    "onboarding.nudge",
}
ALLOWED_QUEST_OPS = {
    "offer",
    "update_objective",
    "mark_ready",
    "complete",
    "fail",
    "cancel",
}
ALLOWED_DECISION_KEYS = {
    "schema_version",
    "decision_id",
    "source_snapshot_id",
    "created_at",
    "edition",
    "session_id",
    "dialogue",
    "quest_operations",
    "build_proposals",
    "event_proposals",
    "mood_delta",
    "relationship_delta",
    "next_trigger",
    "pacing_hint",
    "trace",
}
FORBIDDEN_KEYS = {
    "api_key",
    "script",
    "scripts",
    "code",
    "durable_mutation",
    "scene_tree_mutation",
    "direct_world_write",
    "commit_request",
    "tts_audio",
    "voice_sample",
}
MOOD_MIN, MOOD_MAX = -0.1, 0.1
REL_MIN, REL_MAX = -0.05, 0.05


def make_format_checker() -> FormatChecker:
    checker = FormatChecker()

    @checker.checks("date-time")
    def is_date_time(instance) -> bool:
        if not isinstance(instance, str):
            return True
        try:
            text = instance[:-1] + "+00:00" if instance.endswith("Z") else instance
            datetime.fromisoformat(text)
            return True
        except ValueError:
            return False

    @checker.checks("uuid")
    def is_uuid(instance) -> bool:
        if not isinstance(instance, str):
            return True
        try:
            uuid.UUID(instance)
            return True
        except ValueError:
            return False

    return checker


FORMAT_CHECKER = make_format_checker()


def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_uuid() -> str:
    return str(uuid.uuid4())


class MiniDecisionExecutor:
    """Python twin of AgmDecisionExecutor policy (deterministic allowlist)."""

    def __init__(self) -> None:
        self.seen: dict[str, dict] = {}
        self.mood = 0.5
        self.relationship = 0.5
        self.quests: dict[str, dict] = {}

    def execute(self, decision: dict, live_snapshot: dict | None = None) -> dict:
        live_snapshot = live_snapshot or {}
        for key in decision:
            if key in FORBIDDEN_KEYS:
                return self._reject(decision, "forbidden_or_unknown_field", f"forbidden field: {key}")
            if key not in ALLOWED_DECISION_KEYS:
                return self._reject(decision, "forbidden_or_unknown_field", f"unknown field: {key}")

        decision_id = str(decision.get("decision_id", "")).strip()
        if not decision_id:
            return self._reject(decision, "schema_invalid", "missing decision_id")

        if decision_id in self.seen:
            prior = deepcopy(self.seen[decision_id])
            return {
                **prior,
                "status": "replayed",
                "executed_at": now_iso(),
                "notes": "idempotent replay; effects not re-applied",
                "idempotency": {
                    "replayed": True,
                    "prior_receipt_id": prior.get("receipt_id"),
                    "duplicate_of_decision_id": decision_id,
                },
                "prior_status": prior.get("status"),
            }

        source = str(decision.get("source_snapshot_id", "")).strip()
        if live_snapshot:
            live_id = str(live_snapshot.get("snapshot_id", "")).strip()
            if live_id and live_id != source:
                receipt = {
                    "schema_version": "1.0.0",
                    "receipt_id": new_uuid(),
                    "decision_id": decision_id,
                    "source_snapshot_id": source,
                    "status": "stale_snapshot",
                    "executed_at": now_iso(),
                    "notes": "source_snapshot_id does not match live snapshot_id",
                    "rejection": {
                        "code": "stale_snapshot",
                        "reason": f"source={source} live={live_id}",
                    },
                    "build_handoffs": [],
                    "durable_mutation_applied": False,
                }
                self.seen[decision_id] = deepcopy(receipt)
                return receipt

        actions_applied: list[str] = []
        actions_rejected: list[dict] = []
        build_handoffs: list[dict] = []

        for ev in decision.get("event_proposals") or []:
            et = str(ev.get("event_type", ""))
            if et not in ALLOWED_EVENT_TYPES:
                actions_rejected.append(
                    {"action": "event_proposal", "reason": f"unknown_action: event_type {et}"}
                )
            else:
                actions_applied.append(f"event:{et}")

        for q in decision.get("quest_operations") or []:
            op = str(q.get("op", ""))
            if op not in ALLOWED_QUEST_OPS:
                actions_rejected.append(
                    {"action": "quest_operation", "reason": f"unknown_action: quest op {op}"}
                )
            else:
                qid = str(q.get("quest_id", ""))
                self.quests[qid] = {"op": op, "quest_id": qid}
                actions_applied.append(f"quest:{op}")

        md = decision.get("mood_delta") or {}
        if "delta" in md:
            delta = float(md["delta"])
            if delta < MOOD_MIN - 1e-9 or delta > MOOD_MAX + 1e-9:
                actions_rejected.append(
                    {"action": "mood_delta", "reason": f"forbidden_excessive_mood_delta: {delta}"}
                )
            else:
                self.mood = max(0.0, min(1.0, self.mood + delta))
                if abs(delta) > 1e-12:
                    actions_applied.append("mood_delta")

        rd = decision.get("relationship_delta") or {}
        if "delta" in rd:
            delta = float(rd["delta"])
            if delta < REL_MIN - 1e-9 or delta > REL_MAX + 1e-9:
                actions_rejected.append(
                    {
                        "action": "relationship_delta",
                        "reason": f"forbidden_excessive_relationship_delta: {delta}",
                    }
                )
            else:
                self.relationship = max(0.0, min(1.0, self.relationship + delta))
                if abs(delta) > 1e-12:
                    actions_applied.append("relationship_delta")

        for bp in decision.get("build_proposals") or []:
            if bp.get("routes_through") != "preview_confirm_commit":
                actions_rejected.append(
                    {
                        "action": "build_proposal",
                        "reason": "forbidden_build_bypass: routes_through must be preview_confirm_commit",
                    }
                )
                continue
            if bp.get("preview_required") is not True:
                actions_rejected.append(
                    {
                        "action": "build_proposal",
                        "reason": "forbidden_build_bypass: preview_required must be true",
                    }
                )
                continue
            if bp.get("confirmation_state") != "pending":
                actions_rejected.append(
                    {
                        "action": "build_proposal",
                        "reason": "forbidden_build_bypass: confirmation_state must be pending",
                    }
                )
                continue
            handoff = {
                "proposal_id": bp.get("proposal_id"),
                "prompt_id": new_uuid(),
                "request_id": new_uuid(),
                "recipe_id": bp.get("recipe_id"),
                "routes_through": "preview_confirm_commit",
                "preview_required": True,
                "confirmation_state": "pending",
                "pipeline_stage": "preview",
                "durable_mutation_applied": False,
                "world_prompt": self._world_prompt_from_build(bp, decision),
            }
            build_handoffs.append(handoff)
            actions_applied.append(f"build_preview:{bp.get('proposal_id')}")

        if any(
            str(r.get("reason", "")).startswith("unknown_action")
            or str(r.get("reason", "")).startswith("forbidden_")
            for r in actions_rejected
        ) and not actions_applied and not build_handoffs:
            status = "rejected"
        elif build_handoffs:
            status = "awaiting_player"
        elif actions_rejected and actions_applied:
            status = "partial"
        elif actions_rejected and not actions_applied:
            status = "rejected"
        else:
            status = "applied"

        # dialogue-only counts as applied
        if (decision.get("dialogue") or {}).get("lines") and status == "applied":
            actions_applied.append("dialogue")

        receipt = {
            "schema_version": "1.0.0",
            "receipt_id": new_uuid(),
            "decision_id": decision_id,
            "source_snapshot_id": source,
            "status": status,
            "executed_at": now_iso(),
            "notes": f"status={status}",
            "actions_applied": actions_applied,
            "actions_rejected": actions_rejected,
            "build_handoffs": build_handoffs,
            "mood_after": self.mood,
            "relationship_after": self.relationship,
            "durable_mutation_applied": False,
        }
        if status == "rejected":
            receipt["rejection"] = {
                "code": "policy",
                "reason": receipt["notes"],
            }
        self.seen[decision_id] = deepcopy(receipt)
        return receipt

    def _reject(self, decision: dict, code: str, reason: str) -> dict:
        decision_id = str(decision.get("decision_id", "")).strip() or None
        status = "stale_snapshot" if code == "stale_snapshot" else "rejected"
        receipt = {
            "schema_version": "1.0.0",
            "receipt_id": new_uuid(),
            "decision_id": decision_id,
            "source_snapshot_id": decision.get("source_snapshot_id"),
            "status": status,
            "executed_at": now_iso(),
            "notes": reason[:256],
            "rejection": {"code": code, "reason": reason[:512]},
            "build_handoffs": [],
            "durable_mutation_applied": False,
        }
        if decision_id:
            self.seen[decision_id] = deepcopy(receipt)
        return receipt

    def _world_prompt_from_build(self, bp: dict, decision: dict) -> dict:
        return {
            "schema_version": "1.1.0",
            "prompt_id": new_uuid(),
            "request_id": new_uuid(),
            "session_id": decision.get("session_id", "session_executor_01"),
            "actor": {"player_id": "player_01", "companion_id": "companion_lumi"},
            "operation": bp.get("operation", "create"),
            "target": {
                "space_type": "private_reality",
                "space_id": bp.get("space_id", "home_01"),
                "chunk_id": bp.get("chunk_id", "0_0"),
                "expected_world_revision": 0,
            },
            "style_profile": {
                "profile_id": "cozy_default",
                "profile_version": "1.0.0",
                "base_concept": "cozy_cyber_pixel_2_5d",
                "surrealism_budget": 0.15,
            },
            "entity": {
                "kind": bp.get("entity_kind", "modular_structure_2_5d"),
                "recipe_id": bp.get("recipe_id", "cozy_house_small"),
                "transform": bp.get(
                    "transform",
                    {"x": 8.0, "y": 6.0, "elevation": 0.0, "rotation_deg": 0.0},
                ),
                "bounds": {"width": 8.0, "depth": 6.0, "height": 5.0},
                "interaction_tags": ["enterable", "lightable"],
            },
            "manifestation": {
                "stages": ["wireframe", "hologram", "materializing", "complete"],
                "presentation_duration_seconds": 12.0,
            },
            "budget": {
                "max_compute_units": 200,
                "max_entities": 32,
                "paid_compute_allowed": False,
            },
            "provenance": {
                "source_type": "system",
                "requested_by": "companion_lumi",
                "generated_by": "agm_decision_executor",
                "created_at": "2026-07-20T16:05:00Z",
            },
            "confirmation": {
                "preview_required": True,
                "state": "pending",
                "rollback_window_seconds": 3600,
            },
        }


def build_commit_handoff(world_prompt: dict, confirmed_by: str = "player_01") -> dict:
    """Stub commit request — never applies durable mutation."""
    target = world_prompt.get("target", {})
    return {
        "schema_version": "1.0.0",
        "request_id": world_prompt.get("request_id", new_uuid()),
        "prompt_id": world_prompt.get("prompt_id"),
        "session_id": world_prompt.get("session_id", "session_executor_01"),
        "space_id": target.get("space_id", "home_01"),
        "expected_world_revision": int(target.get("expected_world_revision", 0)),
        "actor": {"actor_id": confirmed_by, "actor_type": "player"},
        "authority": {
            "commit_path": "world_commit_service",
            "source": "server_authoritative",
            "durable_mutation": True,
        },
        "confirmation": {"state": "confirmed", "confirmed_by": confirmed_by},
        "mutation_class": "durable_world",
        "trace_id": "executor_commit_handoff_smoke",
    }


def main() -> int:
    errors: list[str] = []

    decision_schema = load(ROOT / "contracts" / "agm" / "decision_envelope.schema.json")
    world_schema = load(ROOT / "contracts" / "world_prompt.schema.json")
    commit_req_schema = load(ROOT / "contracts" / "commit" / "commit_request.schema.json")
    decision_v = Draft202012Validator(decision_schema, format_checker=FORMAT_CHECKER)
    world_v = Draft202012Validator(world_schema, format_checker=FORMAT_CHECKER)
    commit_v = Draft202012Validator(commit_req_schema, format_checker=FORMAT_CHECKER)

    valid_dir = ROOT / "contracts" / "fixtures" / "agm" / "valid"
    build_decision = load(valid_dir / "valid_decision_with_build_proposal.json")
    soft_decision = load(valid_dir / "valid_decision_desktop_bridge.json")

    for label, doc in [("build", build_decision), ("soft", soft_decision)]:
        issues = list(decision_v.iter_errors(doc))
        if issues:
            errors.append(f"fixture {label} invalid: {issues[0].message}")

    # Policy fixtures
    replay_pair = load(ROOT / "contracts" / "fixtures" / "agm" / "policy" / "replay_decision_pair.json")
    stale_pair = load(ROOT / "contracts" / "fixtures" / "agm" / "policy" / "stale_snapshot_rejection.json")

    ex = MiniDecisionExecutor()
    live = {"snapshot_id": build_decision["source_snapshot_id"]}

    r1 = ex.execute(soft_decision, live)
    if r1.get("status") not in {"applied", "partial", "awaiting_player"}:
        errors.append(f"soft decision unexpected status {r1.get('status')}")
    if r1.get("durable_mutation_applied") is True:
        errors.append("soft decision applied durable mutation")

    # Idempotency: same decision_id
    mood_before = ex.mood
    r2 = ex.execute(soft_decision, live)
    if r2.get("status") != "replayed":
        errors.append(f"replay status expected replayed got {r2.get('status')}")
    if not (r2.get("idempotency") or {}).get("replayed"):
        errors.append("replay missing idempotency.replayed")
    if abs(ex.mood - mood_before) > 1e-12:
        errors.append("replay re-applied mood delta")

    # Stale
    stale_ex = MiniDecisionExecutor()
    stale_r = stale_ex.execute(
        stale_pair["stale_decision"],
        {"snapshot_id": stale_pair["live_snapshot"]["snapshot_id"]},
    )
    if stale_r.get("status") != "stale_snapshot":
        errors.append(f"stale expected stale_snapshot got {stale_r.get('status')}")

    # Build path
    build_ex = MiniDecisionExecutor()
    br = build_ex.execute(build_decision, {"snapshot_id": build_decision["source_snapshot_id"]})
    if br.get("status") != "awaiting_player":
        errors.append(f"build status expected awaiting_player got {br.get('status')}")
    handoffs = br.get("build_handoffs") or []
    if not handoffs:
        errors.append("build handoffs empty")
    else:
        h = handoffs[0]
        if h.get("routes_through") != "preview_confirm_commit":
            errors.append("handoff routes_through wrong")
        if h.get("preview_required") is not True:
            errors.append("handoff preview_required not true")
        if h.get("confirmation_state") != "pending":
            errors.append("handoff confirmation_state not pending")
        if h.get("durable_mutation_applied") is True:
            errors.append("handoff durable mutation true")
        wp = h.get("world_prompt") or {}
        wp_issues = list(world_v.iter_errors(wp))
        if wp_issues:
            errors.append(f"world_prompt schema: {wp_issues[0].message}")
        else:
            # confirm → commit handoff stub
            commit_req = build_commit_handoff(wp)
            cr_issues = list(commit_v.iter_errors(commit_req))
            if cr_issues:
                errors.append(f"commit_request schema: {cr_issues[0].message}")
            if commit_req["authority"]["commit_path"] != "world_commit_service":
                errors.append("commit path not world_commit_service")
            if commit_req["authority"]["source"] != "server_authoritative":
                errors.append("commit source not server_authoritative")

    # Bypass rejection
    bypass = deepcopy(build_decision)
    bypass["decision_id"] = "66666666-6666-4666-8666-666666666601"
    bypass["build_proposals"][0]["preview_required"] = False
    bypass["build_proposals"][0]["confirmation_state"] = "confirmed"
    bypass_r = MiniDecisionExecutor().execute(
        bypass, {"snapshot_id": bypass["source_snapshot_id"]}
    )
    if any(
        "forbidden_build_bypass" in str(x.get("reason", ""))
        for x in (bypass_r.get("actions_rejected") or [])
    ):
        pass
    else:
        errors.append("build bypass not rejected")

    # Unknown event
    bad_ev = deepcopy(soft_decision)
    bad_ev["decision_id"] = "66666666-6666-4666-8666-666666666602"
    bad_ev["event_proposals"] = [
        {"event_type": "economy.spawn_currency", "summary": "nope"}
    ]
    bad_ev["mood_delta"] = {"delta": 0.0}
    bad_ev["relationship_delta"] = {"delta": 0.0}
    bad_ev["dialogue"] = {"lines": []}
    bad_r = MiniDecisionExecutor().execute(
        bad_ev, {"snapshot_id": bad_ev["source_snapshot_id"]}
    )
    if not any(
        "unknown_action" in str(x.get("reason", ""))
        for x in (bad_r.get("actions_rejected") or [])
    ):
        errors.append("unknown event not rejected")

    # Write exports for receipt evidence
    EXPORTS.mkdir(parents=True, exist_ok=True)
    sample_receipt = br
    (EXPORTS / "execution_receipt_build.json").write_text(
        json.dumps(sample_receipt, indent="\t") + "\n", encoding="utf-8"
    )
    if handoffs:
        (EXPORTS / "world_prompt_from_build.json").write_text(
            json.dumps(handoffs[0]["world_prompt"], indent="\t") + "\n", encoding="utf-8"
        )
        (EXPORTS / "commit_request_handoff_stub.json").write_text(
            json.dumps(build_commit_handoff(handoffs[0]["world_prompt"]), indent="\t") + "\n",
            encoding="utf-8",
        )

    # Snapshot projection
    snap_receipt = {
        "decision_id": sample_receipt.get("decision_id"),
        "status": sample_receipt.get("status"),
        "executed_at": sample_receipt.get("executed_at"),
        "notes": str(sample_receipt.get("notes", ""))[:256],
    }
    (EXPORTS / "snapshot_last_execution_receipt.json").write_text(
        json.dumps(snap_receipt, indent="\t") + "\n", encoding="utf-8"
    )

    if errors:
        print("G2-006_SMOKE=FAIL")
        for e in errors:
            print(f" - {e}")
        return 1

    print("G2-006_SMOKE=PASS")
    print(
        "checks=fixture_schema,idempotency,stale,build_preview_commit_handoff,"
        "bypass_reject,unknown_event,exports"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

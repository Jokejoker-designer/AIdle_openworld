#!/usr/bin/env python3
"""G2-005 smoke: Free Desktop Bridge — schema export, policy rejects, no-network audit."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[4]  # AIdle_openworld
BRIDGE = Path(__file__).resolve().parent
EXPORTS = BRIDGE / "exports"


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
        return bool(
            re.fullmatch(
                r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
                instance,
            )
        )

    return checker


FORMAT_CHECKER = make_format_checker()


def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    snap_schema = load(ROOT / "contracts" / "agm" / "world_state_snapshot.schema.json")
    dec_schema = load(ROOT / "contracts" / "agm" / "decision_envelope.schema.json")
    snap_v = Draft202012Validator(snap_schema, format_checker=FORMAT_CHECKER)
    dec_v = Draft202012Validator(dec_schema, format_checker=FORMAT_CHECKER)

    # 1) Exported snapshot from bridge module must validate.
    export_path = EXPORTS / "exported_snapshot_desktop_bridge.json"
    if not export_path.is_file():
        errors.append(f"missing export {export_path}")
    else:
        snap = load(export_path)
        issues = list(snap_v.iter_errors(snap))
        if issues:
            errors.append(f"exported snapshot rejected: {issues[0].message}")
        else:
            if snap.get("edition") != "desktop_bridge_free":
                errors.append("export edition must be desktop_bridge_free")
            for bad in ("api_key", "credentials", "tts_audio", "system_prompt"):
                if bad in snap:
                    errors.append(f"export contains forbidden field {bad}")
            transport = snap.get("transport") or {}
            channel = transport.get("channel")
            if channel not in ("clipboard", "inbox_outbox_file"):
                errors.append(f"export transport.channel unexpected: {channel}")

    # 2) Canonical valid decision fixture still schema-valid (import target).
    valid_decision = load(
        ROOT / "contracts" / "fixtures" / "agm" / "valid" / "valid_decision_desktop_bridge.json"
    )
    d_issues = list(dec_v.iter_errors(valid_decision))
    if d_issues:
        errors.append(f"valid decision fixture broken: {d_issues[0].message}")

    # 3) Policy fixtures: stale + replay rules declared.
    stale = load(ROOT / "contracts" / "fixtures" / "agm" / "policy" / "stale_snapshot_rejection.json")
    if not stale.get("rules", {}).get("stale_must_reject"):
        errors.append("stale policy fixture missing stale_must_reject")
    live_id = stale["live_snapshot"]["snapshot_id"]
    stale_src = stale["stale_decision"]["source_snapshot_id"]
    if live_id == stale_src:
        errors.append("stale fixture live/source should differ")

    replay = load(ROOT / "contracts" / "fixtures" / "agm" / "policy" / "replay_decision_pair.json")
    if not replay.get("rules", {}).get("replay_must_reject"):
        errors.append("replay policy fixture missing replay_must_reject")
    if replay["original"]["decision_id"] != replay["replay"]["decision_id"]:
        errors.append("replay pair decision_id must match")

    # 4) Pure-Python policy mirror (same reject codes as BridgePaths).
    def evaluate_decision(decision: dict, live_snapshot_id: str, seen: set[str]) -> str | None:
        if decision.get("schema_version") != "1.0.0":
            return "schema_invalid"
        for bad in ("script", "code", "api_key", "credentials", "durable_mutation"):
            if bad in decision:
                return "forbidden_field"
        for req in (
            "decision_id",
            "source_snapshot_id",
            "edition",
            "dialogue",
            "quest_operations",
            "build_proposals",
            "event_proposals",
            "mood_delta",
            "relationship_delta",
            "next_trigger",
            "trace",
        ):
            if req not in decision:
                return "schema_invalid"
        if decision.get("source_snapshot_id") != live_snapshot_id:
            return "stale_snapshot"
        if decision.get("decision_id") in seen:
            return "replayed_decision"
        return None

    # Stale reject
    reason = evaluate_decision(stale["stale_decision"], live_id, set())
    if reason != "stale_snapshot":
        errors.append(f"policy mirror stale expected stale_snapshot got {reason}")

    # Replay reject
    rid = replay["original"]["decision_id"]
    reason = evaluate_decision(replay["replay"], replay["original"]["source_snapshot_id"], {rid})
    if reason != "replayed_decision":
        errors.append(f"policy mirror replay expected replayed_decision got {reason}")

    # Valid accept path (pending consent — policy allows through)
    reason = evaluate_decision(
        valid_decision,
        valid_decision["source_snapshot_id"],
        set(),
    )
    if reason is not None:
        errors.append(f"valid decision should pass policy mirror, got {reason}")

    # Malformed
    try:
        json.loads("not json {{{")
        errors.append("malformed json unexpectedly parsed")
    except json.JSONDecodeError:
        pass

    # 5) Source audit: no network SDK, no auto-apply default, consent present.
    sources = [
        BRIDGE / "desktop_bridge_module.gd",
        BRIDGE / "decision_import_guard.gd",
        BRIDGE / "snapshot_builder.gd",
        BRIDGE / "bridge_paths.gd",
        BRIDGE / "bridge_consent_dialog.gd",
    ]
    forbidden_net = (
        "HTTPRequest",
        "HTTPClient",
        "WebSocketPeer",
        "PacketPeerUDP",
        "StreamPeerTCP",
        "OPENAI_API",
        "Authorization",
    )
    for src in sources:
        if not src.is_file():
            errors.append(f"missing source {src}")
            continue
        text = read_text(src)
        for frag in forbidden_net:
            if frag in text:
                errors.append(f"{src.name} contains forbidden network fragment: {frag}")

    # `api_key` is expected inside the explicit deny-lists. Treating the name
    # itself as network usage creates a false positive and would punish the
    # security guard for naming the field it rejects.
    for guard_name in ("decision_import_guard.gd", "snapshot_builder.gd"):
        guard_text = read_text(BRIDGE / guard_name)
        if '"api_key"' not in guard_text:
            errors.append(f"{guard_name} must explicitly reject api_key")

    module_src = read_text(BRIDGE / "desktop_bridge_module.gd")
    if "confirm_pending_decision" not in module_src:
        errors.append("module missing confirm_pending_decision")
    if "auto_consent" not in module_src:
        errors.append("module missing auto_consent gate (default false expected)")
    if "uses_network" not in module_src:
        errors.append("module missing uses_network")
    if "stale_snapshot" not in module_src and "REJECT_STALE" not in read_text(
        BRIDGE / "bridge_paths.gd"
    ):
        errors.append("stale rejection code missing")
    if "replayed_decision" not in module_src and "REJECT_REPLAYED" not in read_text(
        BRIDGE / "bridge_paths.gd"
    ):
        errors.append("replay rejection code missing")

    consent_src = read_text(BRIDGE / "bridge_consent_dialog.gd")
    if "Accept decision" not in consent_src and "consent_accepted" not in consent_src:
        errors.append("consent dialog missing accept path")

    # 6) Consent scene exists under allowed path.
    scene = ROOT / "game" / "scenes" / "ui" / "bridge_consent_dialog.tscn"
    if not scene.is_file():
        errors.append(f"missing consent scene {scene}")

    # 7) Interface exists.
    iface = ROOT / "game" / "scripts" / "modules" / "interfaces" / "i_desktop_bridge_module.gd"
    if not iface.is_file():
        errors.append("missing i_desktop_bridge_module.gd")
    else:
        iface_text = read_text(iface)
        for meth in (
            "export_snapshot_to_clipboard",
            "export_snapshot_to_file",
            "import_decision_from_text",
            "confirm_pending_decision",
            "uses_network",
        ):
            if meth not in iface_text:
                errors.append(f"interface missing {meth}")

    if errors:
        print("G2-005_SMOKE=FAIL")
        for e in errors:
            print(f" - {e}")
        return 1

    print("G2-005_SMOKE=PASS")
    print("checks=export_schema,valid_decision,stale_policy,replay_policy,no_network,consent_ui,interface")
    return 0


if __name__ == "__main__":
    sys.exit(main())

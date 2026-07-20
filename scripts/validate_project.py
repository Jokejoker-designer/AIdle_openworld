from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
MIN_VALID_FIXTURES = 10
MIN_INVALID_FIXTURES = 10


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def make_format_checker() -> FormatChecker:
    """Draft 2020-12 FormatChecker plus date-time (not registered by default in jsonschema)."""
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

    return checker


FORMAT_CHECKER = make_format_checker()


def check_markdown_links(errors: list[str]) -> None:
    blueprint = ROOT / "AIdle_Openworld_Blueprint_v1.1"
    for document in blueprint.rglob("*.md"):
        text = document.read_text(encoding="utf-8")
        for target in re.findall(r"`([^`]+\.(?:md|json))`", text):
            if target.startswith(("http://", "https://", "E:\\")):
                continue
            candidates = [(document.parent / target).resolve(), (ROOT / target).resolve()]
            if not any(candidate.exists() for candidate in candidates):
                errors.append(f"broken reference: {document.relative_to(ROOT)} -> {target}")


def world_prompt_validator() -> Draft202012Validator:
    schema = load_json(ROOT / "contracts" / "world_prompt.schema.json")
    return Draft202012Validator(schema, format_checker=FORMAT_CHECKER)


def check_schema(errors: list[str]) -> None:
    schema_path = ROOT / "contracts" / "world_prompt.schema.json"
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    for candidate in (ROOT / "contracts").glob("*.schema.json"):
        Draft202012Validator.check_schema(load_json(candidate))

    validator = world_prompt_validator()
    valid = load_json(ROOT / "contracts" / "examples" / "valid_house.json")
    invalid = load_json(ROOT / "contracts" / "examples" / "invalid_reversed_stages.json")
    valid_errors = list(validator.iter_errors(valid))
    invalid_errors = list(validator.iter_errors(invalid))
    if valid_errors:
        errors.append("valid_house rejected: " + valid_errors[0].message)
    if not invalid_errors:
        errors.append("invalid_reversed_stages was accepted")


def check_fixtures(errors: list[str]) -> None:
    """G1-001: validate world_prompt fixtures under fixtures/valid|invalid (≥10 each when present)."""
    valid_dir = ROOT / "contracts" / "fixtures" / "valid"
    invalid_dir = ROOT / "contracts" / "fixtures" / "invalid"
    if not valid_dir.is_dir() and not invalid_dir.is_dir():
        return

    validator = world_prompt_validator()
    valid_paths = sorted(valid_dir.glob("*.json")) if valid_dir.is_dir() else []
    invalid_paths = sorted(invalid_dir.glob("*.json")) if invalid_dir.is_dir() else []

    # Only enforce min counts when the G1-001 fixture trees are in use (any files present).
    if valid_paths or invalid_paths:
        if len(valid_paths) < MIN_VALID_FIXTURES:
            errors.append(
                f"valid fixtures count {len(valid_paths)} < required {MIN_VALID_FIXTURES}"
            )
        if len(invalid_paths) < MIN_INVALID_FIXTURES:
            errors.append(
                f"invalid fixtures count {len(invalid_paths)} < required {MIN_INVALID_FIXTURES}"
            )

    for path in valid_paths:
        try:
            document = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"valid fixture not JSON: {path.relative_to(ROOT)}: {exc}")
            continue
        failures = list(validator.iter_errors(document))
        if failures:
            rel = path.relative_to(ROOT)
            errors.append(f"valid fixture rejected: {rel}: {failures[0].message}")

    for path in invalid_paths:
        try:
            document = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid fixture not JSON: {path.relative_to(ROOT)}: {exc}")
            continue
        failures = list(validator.iter_errors(document))
        if not failures:
            rel = path.relative_to(ROOT)
            errors.append(f"invalid fixture was accepted: {rel}")


def _schema_validator(schema_path: Path) -> Draft202012Validator:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FORMAT_CHECKER)


def _expect_valid(errors: list[str], validator: Draft202012Validator, path: Path, label: str) -> dict | None:
    if not path.is_file():
        errors.append(f"{label}: missing fixture {path.relative_to(ROOT)}")
        return None
    data = load_json(path)
    issues = list(validator.iter_errors(data))
    if issues:
        errors.append(f"{label}: expected valid but rejected: {issues[0].message} ({path.name})")
        return None
    return data


def _expect_invalid(errors: list[str], validator: Draft202012Validator, path: Path, label: str) -> None:
    if not path.is_file():
        errors.append(f"{label}: missing fixture {path.relative_to(ROOT)}")
        return
    data = load_json(path)
    issues = list(validator.iter_errors(data))
    if not issues:
        errors.append(f"{label}: expected invalid but accepted ({path.name})")


def check_commit_and_event_contracts(errors: list[str]) -> None:
    """G1-002: commit authority + event envelope (owns fixtures/commit and fixtures/events)."""
    commit_dir = ROOT / "contracts" / "commit"
    events_dir = ROOT / "contracts" / "events"
    fixtures_commit = ROOT / "contracts" / "fixtures" / "commit"
    fixtures_events = ROOT / "contracts" / "fixtures" / "events"

    request_schema = commit_dir / "commit_request.schema.json"
    receipt_schema = commit_dir / "commit_receipt.schema.json"
    envelope_schema = events_dir / "event_envelope.schema.json"

    for required in (request_schema, receipt_schema, envelope_schema):
        if not required.is_file():
            errors.append(f"commit/event: missing schema {required.relative_to(ROOT)}")
            return

    for schema_path in list(commit_dir.glob("*.schema.json")) + list(events_dir.glob("*.schema.json")):
        try:
            Draft202012Validator.check_schema(load_json(schema_path))
        except Exception as exc:  # noqa: BLE001 — surface schema errors as validation failures
            errors.append(f"invalid schema {schema_path.relative_to(ROOT)}: {exc}")

    request_validator = _schema_validator(request_schema)
    receipt_validator = _schema_validator(receipt_schema)
    envelope_validator = _schema_validator(envelope_schema)

    _expect_valid(
        errors,
        request_validator,
        fixtures_commit / "valid_commit_request.json",
        "commit_request.valid",
    )
    _expect_invalid(
        errors,
        request_validator,
        fixtures_commit / "invalid_client_forged_durable_request.json",
        "commit_request.client_forged",
    )
    _expect_invalid(
        errors,
        request_validator,
        fixtures_commit / "invalid_client_authoritative_source.json",
        "commit_request.client_authoritative",
    )

    original = _expect_valid(
        errors,
        receipt_validator,
        fixtures_commit / "valid_committed_receipt.json",
        "commit_receipt.committed",
    )
    replay = _expect_valid(
        errors,
        receipt_validator,
        fixtures_commit / "valid_idempotent_replay_receipt.json",
        "commit_receipt.idempotent_replay",
    )
    conflict = _expect_valid(
        errors,
        receipt_validator,
        fixtures_commit / "valid_revision_conflict_receipt.json",
        "commit_receipt.conflicted",
    )
    rejection = _expect_valid(
        errors,
        receipt_validator,
        fixtures_commit / "valid_client_forged_rejection_receipt.json",
        "commit_receipt.client_forged_rejection",
    )

    if rejection is not None:
        code = rejection.get("rejection", {}).get("code")
        if code not in {"client_forged", "client_authoritative_durable_forbidden"}:
            errors.append(
                "commit_receipt.client_forged_rejection: rejection.code must be "
                "client_forged or client_authoritative_durable_forbidden"
            )

    if conflict is not None:
        conf = conflict.get("conflict") or {}
        if conf.get("code") != "revision_mismatch":
            errors.append("commit_receipt.conflicted: conflict.code must be revision_mismatch")
        if conf.get("expected_world_revision") == conf.get("actual_world_revision"):
            errors.append(
                "commit_receipt.conflicted: expected_world_revision must differ from actual_world_revision"
            )

    pair_path = fixtures_commit / "idempotency_pair.json"
    if not pair_path.is_file():
        errors.append(f"commit_idempotency: missing {pair_path.relative_to(ROOT)}")
    elif original is not None and replay is not None:
        pair = load_json(pair_path)
        if original.get("request_id") != replay.get("request_id"):
            errors.append("commit_idempotency: original and replay request_id must match")
        idem = replay.get("idempotency") or {}
        if idem.get("prior_receipt_id") != original.get("receipt_id"):
            errors.append(
                "commit_idempotency: replay prior_receipt_id must equal original receipt_id"
            )
        if idem.get("duplicate_of_request_id") != original.get("request_id"):
            errors.append(
                "commit_idempotency: duplicate_of_request_id must equal original request_id"
            )
        if idem.get("replayed") is not True:
            errors.append("commit_idempotency: idempotency.replayed must be true")
        if (
            original.get("old_world_revision") != replay.get("old_world_revision")
            or original.get("new_world_revision") != replay.get("new_world_revision")
        ):
            errors.append(
                "commit_idempotency: replay must not change old/new world revision vs original"
            )
        if pair.get("rules", {}).get("same_request_id") is not True:
            errors.append("commit_idempotency: pair rules.same_request_id must be true")

    _expect_valid(
        errors,
        envelope_validator,
        fixtures_events / "valid_event_envelope.json",
        "event_envelope.valid",
    )
    _expect_invalid(
        errors,
        envelope_validator,
        fixtures_events / "invalid_event_missing_fields.json",
        "event_envelope.missing_fields",
    )
    _expect_invalid(
        errors,
        envelope_validator,
        fixtures_events / "invalid_event_with_secret_payload.json",
        "event_envelope.secret_payload",
    )

    required_fields = {
        "event_id",
        "event_type",
        "event_version",
        "occurred_at",
        "request_id",
        "space_id",
        "world_revision",
        "actor_id",
        "payload",
        "trace_id",
    }
    envelope = load_json(envelope_schema)
    schema_required = set(envelope.get("required") or [])
    if schema_required != required_fields:
        errors.append(
            "event_envelope.schema: required fields mismatch Event_Bus.md: "
            f"missing={sorted(required_fields - schema_required)} "
            f"extra={sorted(schema_required - required_fields)}"
        )
    if envelope.get("additionalProperties") is not False:
        errors.append("event_envelope.schema: additionalProperties must be false")


def check_orchestration(errors: list[str]) -> None:
    workflow = load_json(ROOT / "orchestration" / "workflow.json")
    tasks = load_json(ROOT / "orchestration" / "tasks.json")["tasks"]
    agents = sorted((ROOT / ".grok" / "agents").glob("*.md"))
    workers = [agent for agent in agents if agent.stem != "lead-orchestrator"]
    if workflow["max_concurrent_workers"] != 8 or len(workers) != 8:
        errors.append(f"crew mismatch: declared={workflow['max_concurrent_workers']} files={len(workers)}")
    ids = [task["id"] for task in tasks]
    if len(ids) != len(set(ids)):
        errors.append("duplicate task IDs")
    known = set(ids)
    for task in tasks:
        missing = set(task["dependencies"]) - known
        if missing:
            errors.append(f"{task['id']} has missing dependencies: {sorted(missing)}")


def main() -> int:
    errors: list[str] = []
    check_markdown_links(errors)
    check_schema(errors)
    check_fixtures(errors)
    check_commit_and_event_contracts(errors)
    check_orchestration(errors)
    if errors:
        print("AIDLE_VALIDATION=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("AIDLE_VALIDATION=PASS")
    print(
        "scope=blueprint-links,all-schema-shapes,world-positive-negative,"
        "fixtures-valid-invalid,format-checker,commit-authority,event-envelope,crew,task-dag"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

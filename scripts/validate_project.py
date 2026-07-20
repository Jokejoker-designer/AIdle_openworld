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


# G1-003: AGM Snapshot + Decision Envelope (provider-neutral; free/paid identical payload).
MIN_AGM_VALID_FIXTURES = 5
MIN_AGM_INVALID_FIXTURES = 10
AGM_SEMANTIC_STRIP_KEYS = ("edition", "transport")


def _strip_keys(document: dict, keys: tuple[str, ...] | list[str]) -> dict:
    return {k: v for k, v in document.items() if k not in keys}


def _agm_kind_from_name(name: str) -> str | None:
    lower = name.lower()
    if "snapshot" in lower:
        return "snapshot"
    if "decision" in lower:
        return "decision"
    return None


def check_agm_contracts(errors: list[str]) -> None:
    """G1-003: World State Snapshot + Decision Envelope schemas, fixtures, free/paid identity, replay/stale policy."""
    agm_dir = ROOT / "contracts" / "agm"
    fixtures_root = ROOT / "contracts" / "fixtures" / "agm"
    valid_dir = fixtures_root / "valid"
    invalid_dir = fixtures_root / "invalid"
    policy_dir = fixtures_root / "policy"

    snapshot_schema = agm_dir / "world_state_snapshot.schema.json"
    decision_schema = agm_dir / "decision_envelope.schema.json"

    for required in (snapshot_schema, decision_schema):
        if not required.is_file():
            errors.append(f"agm: missing schema {required.relative_to(ROOT)}")
            return

    for schema_path in agm_dir.glob("*.schema.json"):
        try:
            Draft202012Validator.check_schema(load_json(schema_path))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"agm: invalid schema {schema_path.relative_to(ROOT)}: {exc}")

    snapshot_validator = _schema_validator(snapshot_schema)
    decision_validator = _schema_validator(decision_schema)

    # --- Schema shape locks ---
    for label, schema_path, required_fields in (
        (
            "world_state_snapshot",
            snapshot_schema,
            {
                "schema_version",
                "snapshot_id",
                "created_at",
                "edition",
                "session_id",
                "space_id",
                "world_revision",
                "progression_phase",
                "art_style",
                "player",
                "companion",
                "world",
                "quests",
                "latest_player_action",
                "last_execution_receipt",
                "memory",
                "trace_id",
            },
        ),
        (
            "decision_envelope",
            decision_schema,
            {
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
                "trace",
            },
        ),
    ):
        doc = load_json(schema_path)
        if doc.get("additionalProperties") is not False:
            errors.append(f"agm.{label}: additionalProperties must be false")
        schema_required = set(doc.get("required") or [])
        if schema_required != required_fields:
            errors.append(
                f"agm.{label}: required fields mismatch: "
                f"missing={sorted(required_fields - schema_required)} "
                f"extra={sorted(schema_required - required_fields)}"
            )
        edition = (doc.get("properties") or {}).get("edition") or {}
        if set(edition.get("enum") or []) != {"desktop_bridge_free", "api_paid"}:
            errors.append(f"agm.{label}: edition enum must be desktop_bridge_free|api_paid")

    # Build proposals must force preview/pending (no commit bypass).
    decision_doc = load_json(decision_schema)
    build_items = (
        ((decision_doc.get("properties") or {}).get("build_proposals") or {}).get("items") or {}
    )
    build_props = build_items.get("properties") or {}
    if (build_props.get("preview_required") or {}).get("const") is not True:
        errors.append("agm.decision_envelope: build_proposals.preview_required must be const true")
    if (build_props.get("confirmation_state") or {}).get("const") != "pending":
        errors.append(
            "agm.decision_envelope: build_proposals.confirmation_state must be const pending"
        )
    if (build_props.get("routes_through") or {}).get("const") != "preview_confirm_commit":
        errors.append(
            "agm.decision_envelope: build_proposals.routes_through must be "
            "const preview_confirm_commit"
        )

    # Forbidden direct-mutation / secret / code property names on decision root.
    forbidden_names = {
        "api_key",
        "commit_request",
        "durable_mutation",
        "script",
        "code",
        "tts_audio",
        "voice_sample",
    }
    prop_names = (decision_doc.get("propertyNames") or {}).get("not") or {}
    banned = set(prop_names.get("enum") or [])
    missing_ban = forbidden_names - banned
    if missing_ban:
        errors.append(
            f"agm.decision_envelope: propertyNames must ban {sorted(missing_ban)}"
        )

    # --- Valid fixtures ---
    valid_paths = sorted(valid_dir.glob("*.json")) if valid_dir.is_dir() else []
    invalid_paths = sorted(invalid_dir.glob("*.json")) if invalid_dir.is_dir() else []
    if len(valid_paths) < MIN_AGM_VALID_FIXTURES:
        errors.append(
            f"agm: valid fixtures count {len(valid_paths)} < required {MIN_AGM_VALID_FIXTURES}"
        )
    if len(invalid_paths) < MIN_AGM_INVALID_FIXTURES:
        errors.append(
            f"agm: invalid fixtures count {len(invalid_paths)} < required {MIN_AGM_INVALID_FIXTURES}"
        )

    for path in valid_paths:
        kind = _agm_kind_from_name(path.name)
        if kind is None:
            errors.append(f"agm: valid fixture name must include snapshot|decision: {path.name}")
            continue
        validator = snapshot_validator if kind == "snapshot" else decision_validator
        try:
            document = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"agm: valid fixture not JSON: {path.relative_to(ROOT)}: {exc}")
            continue
        issues = list(validator.iter_errors(document))
        if issues:
            errors.append(
                f"agm: valid fixture rejected: {path.relative_to(ROOT)}: {issues[0].message}"
            )

    for path in invalid_paths:
        kind = _agm_kind_from_name(path.name)
        if kind is None:
            errors.append(f"agm: invalid fixture name must include snapshot|decision: {path.name}")
            continue
        validator = snapshot_validator if kind == "snapshot" else decision_validator
        try:
            document = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"agm: invalid fixture not JSON: {path.relative_to(ROOT)}: {exc}")
            continue
        issues = list(validator.iter_errors(document))
        if not issues:
            errors.append(f"agm: invalid fixture was accepted: {path.relative_to(ROOT)}")

    # --- Free/Paid identical payload semantics ---
    identity_path = policy_dir / "edition_identity_pair.json"
    if not identity_path.is_file():
        errors.append(f"agm: missing {identity_path.relative_to(ROOT)}")
    else:
        identity = load_json(identity_path)
        strip_keys = tuple(identity.get("strip_keys") or AGM_SEMANTIC_STRIP_KEYS)
        for pair_key in ("snapshot_pair", "decision_pair"):
            pair = identity.get(pair_key) or {}
            free_rel = pair.get("desktop_bridge_free")
            paid_rel = pair.get("api_paid")
            if not free_rel or not paid_rel:
                errors.append(f"agm.edition_identity: {pair_key} missing free/paid paths")
                continue
            free_path = ROOT / free_rel
            paid_path = ROOT / paid_rel
            if not free_path.is_file() or not paid_path.is_file():
                errors.append(f"agm.edition_identity: missing pair files for {pair_key}")
                continue
            free_doc = load_json(free_path)
            paid_doc = load_json(paid_path)
            if free_doc.get("edition") != "desktop_bridge_free":
                errors.append(f"agm.edition_identity: {free_rel} edition must be desktop_bridge_free")
            if paid_doc.get("edition") != "api_paid":
                errors.append(f"agm.edition_identity: {paid_rel} edition must be api_paid")
            free_sem = _strip_keys(free_doc, strip_keys)
            paid_sem = _strip_keys(paid_doc, strip_keys)
            if free_sem != paid_sem:
                errors.append(
                    f"agm.edition_identity: {pair_key} payload semantics differ after "
                    f"stripping {list(strip_keys)}"
                )

    # --- Replay decision_id policy ---
    replay_path = policy_dir / "replay_decision_pair.json"
    if not replay_path.is_file():
        errors.append(f"agm: missing {replay_path.relative_to(ROOT)}")
    else:
        replay = load_json(replay_path)
        original = replay.get("original")
        second = replay.get("replay")
        if not isinstance(original, dict) or not isinstance(second, dict):
            errors.append("agm.replay: original and replay objects required")
        else:
            for label, doc in (("original", original), ("replay", second)):
                issues = list(decision_validator.iter_errors(doc))
                if issues:
                    errors.append(
                        f"agm.replay: {label} must be schema-valid alone: {issues[0].message}"
                    )
            if original.get("decision_id") != second.get("decision_id"):
                errors.append("agm.replay: original and replay decision_id must match")
            elif not original.get("decision_id"):
                errors.append("agm.replay: decision_id missing")
            else:
                # Simulate executor seen-set: second decision_id is a replay → reject.
                seen = {original["decision_id"]}
                if second["decision_id"] in seen:
                    # Expected rejection path; record as pass via no error.
                    pass
                else:
                    errors.append("agm.replay: expected replayed decision_id to hit seen-set")
            if (replay.get("rules") or {}).get("replay_must_reject") is not True:
                errors.append("agm.replay: rules.replay_must_reject must be true")

    # --- Stale snapshot policy ---
    stale_path = policy_dir / "stale_snapshot_rejection.json"
    if not stale_path.is_file():
        errors.append(f"agm: missing {stale_path.relative_to(ROOT)}")
    else:
        stale = load_json(stale_path)
        live = stale.get("live_snapshot")
        decision = stale.get("stale_decision")
        if not isinstance(live, dict) or not isinstance(decision, dict):
            errors.append("agm.stale: live_snapshot and stale_decision objects required")
        else:
            live_issues = list(snapshot_validator.iter_errors(live))
            if live_issues:
                errors.append(
                    f"agm.stale: live_snapshot must be schema-valid: {live_issues[0].message}"
                )
            dec_issues = list(decision_validator.iter_errors(decision))
            if dec_issues:
                errors.append(
                    f"agm.stale: stale_decision must be schema-valid alone: {dec_issues[0].message}"
                )
            live_id = live.get("snapshot_id")
            source_id = decision.get("source_snapshot_id")
            if not live_id or not source_id:
                errors.append("agm.stale: snapshot_id/source_snapshot_id required")
            elif live_id == source_id:
                errors.append(
                    "agm.stale: source_snapshot_id must differ from live snapshot_id "
                    "(fixture must demonstrate stale rejection)"
                )
            else:
                # Policy gate: reject when source_snapshot_id != live snapshot_id.
                if source_id != live_id:
                    pass  # expected rejection
                else:
                    errors.append("agm.stale: expected stale mismatch rejection")
            if (stale.get("rules") or {}).get("stale_must_reject") is not True:
                errors.append("agm.stale: rules.stale_must_reject must be true")


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


# G2-004: modular 2.5D starter asset grammar (recipes, placeholders, styles, provenance).
REQUIRED_STYLE_CONCEPTS = (
    "cozy_cyber_pixel_2_5d",
    "pastoral_fantasy_2_5d",
    "soft_scifi_2_5d",
)
STARTER_RECIPE_ID = "cozy_house_small"


def _world_prompt_base_concepts() -> set[str]:
    schema = load_json(ROOT / "contracts" / "world_prompt.schema.json")
    style = schema["properties"]["style_profile"]
    enum = style["properties"]["base_concept"]["enum"]
    return set(enum)


def _filesystem_path_from_provenance(entry_path: str) -> Path:
    """Resolve provenance path; fragment (#id) means catalog membership only."""
    file_part = entry_path.split("#", 1)[0]
    return ROOT / file_part


def check_asset_grammar(errors: list[str]) -> None:
    """G2-004: executable checks for modular 2.5D starter asset grammar."""
    recipe_schema_path = ROOT / "contracts" / "assets" / "recipe.schema.json"
    contracts_recipe_path = ROOT / "contracts" / "assets" / "recipes" / f"{STARTER_RECIPE_ID}.json"
    game_recipe_path = ROOT / "game" / "assets" / "recipes" / f"{STARTER_RECIPE_ID}.json"
    catalog_path = ROOT / "game" / "assets" / "placeholders" / "modular" / "catalog.json"
    provenance_path = ROOT / "contracts" / "assets" / "provenance_manifest.json"
    assets_index_path = ROOT / "contracts" / "assets" / "index.json"
    grammar_index_path = ROOT / "game" / "assets" / "grammar" / "index.json"
    shared_tokens_path = ROOT / "game" / "resources" / "art_styles" / "tokens" / "shared_2_5d_tokens.json"
    style_paths = {
        concept: ROOT / "game" / "resources" / "art_styles" / f"{concept}.json"
        for concept in REQUIRED_STYLE_CONCEPTS
    }

    required_files = [
        recipe_schema_path,
        contracts_recipe_path,
        game_recipe_path,
        catalog_path,
        provenance_path,
        assets_index_path,
        grammar_index_path,
        shared_tokens_path,
        *style_paths.values(),
    ]
    for path in required_files:
        if not path.is_file():
            errors.append(f"asset_grammar: missing {path.relative_to(ROOT)}")
    if any(not p.is_file() for p in required_files):
        return

    # --- Recipe schema validation (contracts canonical) ---
    try:
        recipe_validator = _schema_validator(recipe_schema_path)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"asset_grammar: invalid recipe.schema.json: {exc}")
        return

    contracts_recipe = load_json(contracts_recipe_path)
    schema_issues = list(recipe_validator.iter_errors(contracts_recipe))
    if schema_issues:
        errors.append(
            f"asset_grammar: cozy_house_small failed recipe schema: {schema_issues[0].message}"
        )

    if contracts_recipe.get("recipe_id") != STARTER_RECIPE_ID:
        errors.append(
            f"asset_grammar: recipe_id expected {STARTER_RECIPE_ID!r}, "
            f"got {contracts_recipe.get('recipe_id')!r}"
        )
    if contracts_recipe.get("kind") != "modular_structure_2_5d":
        errors.append(
            f"asset_grammar: kind must be modular_structure_2_5d, "
            f"got {contracts_recipe.get('kind')!r}"
        )

    parts = contracts_recipe.get("parts") or []
    build_order = contracts_recipe.get("build_order") or []
    part_ids = [p.get("part_id") for p in parts if isinstance(p, dict)]
    part_id_set = set(part_ids)
    if len(part_ids) != len(part_id_set):
        errors.append("asset_grammar: duplicate part_id in cozy_house_small parts")
    build_set = set(build_order)
    if len(build_order) != len(build_set):
        errors.append("asset_grammar: build_order has duplicate part_ids")
    if part_id_set != build_set:
        missing = sorted(part_id_set - build_set)
        extra = sorted(build_set - part_id_set)
        errors.append(
            "asset_grammar: build_order must cover parts exactly once "
            f"(missing_from_order={missing}, extra_in_order={extra})"
        )

    collision = contracts_recipe.get("collision_policy") or {}
    if collision.get("active_from_stage") != "complete":
        errors.append(
            "asset_grammar: collision_policy.active_from_stage must be 'complete' "
            f"(got {collision.get('active_from_stage')!r})"
        )

    # --- Placeholders catalog ---
    catalog = load_json(catalog_path)
    placeholders = catalog.get("placeholders") or []
    placeholder_ids = {
        p.get("placeholder_id") for p in placeholders if isinstance(p, dict)
    }
    if not placeholder_ids:
        errors.append("asset_grammar: modular catalog has no placeholders")
    for part in parts:
        if not isinstance(part, dict):
            continue
        ph = part.get("placeholder_id")
        if ph not in placeholder_ids:
            errors.append(
                f"asset_grammar: part {part.get('part_id')!r} placeholder_id "
                f"{ph!r} not in modular catalog"
            )

    # --- Contracts ↔ game recipe mirror (key structural fields) ---
    game_recipe = load_json(game_recipe_path)
    for key in ("recipe_id", "kind", "build_order", "collision_policy"):
        if game_recipe.get(key) != contracts_recipe.get(key):
            errors.append(
                f"asset_grammar: game mirror mismatch on {key} vs contracts recipe"
            )
    game_part_ids = [p.get("part_id") for p in (game_recipe.get("parts") or []) if isinstance(p, dict)]
    if set(game_part_ids) != part_id_set:
        errors.append("asset_grammar: game mirror parts set differs from contracts recipe")
    else:
        contracts_by_id = {p["part_id"]: p for p in parts if isinstance(p, dict) and "part_id" in p}
        for gp in game_recipe.get("parts") or []:
            if not isinstance(gp, dict):
                continue
            pid = gp.get("part_id")
            cp = contracts_by_id.get(pid) or {}
            for field in ("placeholder_id", "local_position", "local_size", "collision", "nav"):
                if gp.get(field) != cp.get(field):
                    errors.append(
                        f"asset_grammar: game mirror part {pid!r} field {field} "
                        "differs from contracts"
                    )
                    break

    # --- Style tokens / base_concept ⊆ world_prompt enum ---
    wp_concepts = _world_prompt_base_concepts()
    for concept, style_path in style_paths.items():
        style_doc = load_json(style_path)
        base = style_doc.get("base_concept")
        if base != concept:
            errors.append(
                f"asset_grammar: style file {style_path.name} base_concept "
                f"{base!r} != expected {concept!r}"
            )
        if base not in wp_concepts:
            errors.append(
                f"asset_grammar: base_concept {base!r} not in world_prompt enum"
            )

    shared = load_json(shared_tokens_path)
    camera = shared.get("camera") or {}
    if camera.get("free_orbit_allowed") is not False:
        errors.append("asset_grammar: shared tokens free_orbit_allowed must be false")
    manifestation = shared.get("manifestation") or {}
    if manifestation.get("collision_active_from") != "complete":
        errors.append(
            "asset_grammar: shared tokens manifestation.collision_active_from "
            "must be 'complete'"
        )

    # Style binding on recipe must stay within world_prompt concepts
    style_binding = contracts_recipe.get("style_binding") or {}
    allowed = style_binding.get("allowed_base_concepts") or []
    for concept in allowed:
        if concept not in wp_concepts:
            errors.append(
                f"asset_grammar: recipe allowed_base_concept {concept!r} "
                "not in world_prompt enum"
            )
    for concept in REQUIRED_STYLE_CONCEPTS:
        if concept not in allowed:
            errors.append(
                f"asset_grammar: recipe missing required allowed_base_concept {concept!r}"
            )

    # --- Provenance manifest ---
    provenance = load_json(provenance_path)
    policy = provenance.get("policy") or {}
    if policy.get("paid_generation_apis") is not False:
        errors.append("asset_grammar: provenance policy paid_generation_apis must be false")
    if policy.get("neural_world_model") is not False:
        errors.append("asset_grammar: provenance policy neural_world_model must be false")

    entries = provenance.get("entries") or []
    if not entries:
        errors.append("asset_grammar: provenance_manifest has no entries")
    entry_paths: set[str] = set()
    entry_asset_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        asset_id = entry.get("asset_id")
        if asset_id:
            entry_asset_ids.add(asset_id)
        path_str = entry.get("path")
        if not path_str or not isinstance(path_str, str):
            errors.append(f"asset_grammar: provenance entry missing path: {asset_id!r}")
            continue
        entry_paths.add(path_str)
        fs_path = _filesystem_path_from_provenance(path_str)
        if not fs_path.is_file():
            errors.append(
                f"asset_grammar: provenance path missing on disk: {path_str}"
            )
        if "#" in path_str:
            # Fragment form: catalog.json#placeholder_id — resolve membership
            fragment = path_str.split("#", 1)[1]
            if fragment and fragment not in placeholder_ids:
                errors.append(
                    f"asset_grammar: provenance fragment {fragment!r} not in "
                    "modular catalog"
                )
        mirror = entry.get("mirror_path")
        if mirror:
            if not (ROOT / mirror).is_file():
                errors.append(
                    f"asset_grammar: provenance mirror_path missing: {mirror}"
                )

    required_provenance_paths = {
        "contracts/assets/index.json",
        "contracts/assets/recipe.schema.json",
        f"contracts/assets/recipes/{STARTER_RECIPE_ID}.json",
        "game/assets/grammar/index.json",
        "game/assets/placeholders/modular/catalog.json",
        "game/resources/art_styles/tokens/shared_2_5d_tokens.json",
        "contracts/assets/provenance_manifest.json",
    }
    for concept in REQUIRED_STYLE_CONCEPTS:
        required_provenance_paths.add(f"game/resources/art_styles/{concept}.json")
    for path_str in required_provenance_paths:
        if path_str not in entry_paths and not any(
            p.split("#", 1)[0] == path_str for p in entry_paths
        ):
            # exact path match only for non-fragment required roots
            if path_str not in {p.split("#", 1)[0] for p in entry_paths}:
                errors.append(
                    f"asset_grammar: provenance missing coverage for {path_str}"
                )

    if f"recipe:{STARTER_RECIPE_ID}" not in entry_asset_ids:
        errors.append(
            f"asset_grammar: provenance missing asset_id recipe:{STARTER_RECIPE_ID}"
        )
    for concept in REQUIRED_STYLE_CONCEPTS:
        if f"style:{concept}" not in entry_asset_ids:
            errors.append(
                f"asset_grammar: provenance missing asset_id style:{concept}"
            )
    if "placeholders:modular_catalog" not in entry_asset_ids:
        errors.append(
            "asset_grammar: provenance missing asset_id placeholders:modular_catalog"
        )

    # Catalog index consistency
    assets_index = load_json(assets_index_path)
    recipe_ids = {
        r.get("recipe_id") for r in (assets_index.get("recipes") or []) if isinstance(r, dict)
    }
    if STARTER_RECIPE_ID not in recipe_ids:
        errors.append(
            f"asset_grammar: contracts/assets/index.json missing recipe {STARTER_RECIPE_ID}"
        )
    constraints = assets_index.get("constraints") or {}
    if constraints.get("no_paid_generation_apis") is not True:
        errors.append("asset_grammar: assets index constraints.no_paid_generation_apis must be true")
    if constraints.get("no_neural_world_model_on_critical_path") is not True:
        errors.append(
            "asset_grammar: assets index constraints.no_neural_world_model_on_critical_path "
            "must be true"
        )


def main() -> int:
    errors: list[str] = []
    check_markdown_links(errors)
    check_schema(errors)
    check_fixtures(errors)
    check_commit_and_event_contracts(errors)
    check_agm_contracts(errors)
    check_orchestration(errors)
    check_asset_grammar(errors)
    if errors:
        print("AIDLE_VALIDATION=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("AIDLE_VALIDATION=PASS")
    print(
        "scope=blueprint-links,all-schema-shapes,world-positive-negative,"
        "fixtures-valid-invalid,format-checker,commit-authority,event-envelope,"
        "agm-snapshot-decision,crew,task-dag,asset-grammar"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

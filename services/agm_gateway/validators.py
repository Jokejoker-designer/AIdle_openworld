"""JSON Schema validators for World State Snapshot and Decision Envelope."""

from __future__ import annotations

import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .paths import DECISION_SCHEMA, SNAPSHOT_SCHEMA


def _make_format_checker() -> FormatChecker:
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


FORMAT_CHECKER = _make_format_checker()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"schema root must be object: {path}")
    return data


@lru_cache(maxsize=4)
def _snapshot_validator() -> Draft202012Validator:
    schema = _load_json(SNAPSHOT_SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FORMAT_CHECKER)


@lru_cache(maxsize=4)
def _decision_validator() -> Draft202012Validator:
    schema = _load_json(DECISION_SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FORMAT_CHECKER)


def _collect_errors(validator: Draft202012Validator, instance: Any) -> list[str]:
    errors: list[str] = []
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def validate_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Validate against world_state_snapshot.schema.json."""
    if not isinstance(snapshot, dict):
        return {"ok": False, "errors": ["snapshot must be an object"]}
    errors = _collect_errors(_snapshot_validator(), snapshot)
    return {"ok": len(errors) == 0, "errors": errors}


def validate_decision(decision: dict[str, Any]) -> dict[str, Any]:
    """Validate against decision_envelope.schema.json (+ build proposal locks in schema)."""
    if not isinstance(decision, dict):
        return {"ok": False, "errors": ["decision must be an object"]}
    errors = _collect_errors(_decision_validator(), decision)
    return {"ok": len(errors) == 0, "errors": errors}

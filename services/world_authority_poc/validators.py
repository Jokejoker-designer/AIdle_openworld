"""JSON Schema validators for world_prompt and commit_request."""

from __future__ import annotations

import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import UUID

from jsonschema import Draft202012Validator, FormatChecker

from .paths import COMMIT_REQUEST_SCHEMA, WORLD_PROMPT_SCHEMA


def _make_format_checker() -> FormatChecker:
    checker = FormatChecker()

    @checker.checks("date-time")
    def is_date_time(instance: object) -> bool:
        if not isinstance(instance, str):
            return True
        try:
            text = instance[:-1] + "+00:00" if instance.endswith("Z") else instance
            datetime.fromisoformat(text)
            return True
        except ValueError:
            return False

    @checker.checks("uuid")
    def is_uuid(instance: object) -> bool:
        if not isinstance(instance, str):
            return True
        try:
            UUID(instance)
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
def _world_prompt_validator() -> Draft202012Validator:
    schema = _load_json(WORLD_PROMPT_SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FORMAT_CHECKER)


@lru_cache(maxsize=4)
def _commit_request_validator() -> Draft202012Validator:
    schema = _load_json(COMMIT_REQUEST_SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FORMAT_CHECKER)


def _collect_errors(validator: Draft202012Validator, instance: Any) -> list[str]:
    errors: list[str] = []
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def validate_world_prompt(prompt: Any) -> dict[str, Any]:
    if not isinstance(prompt, dict):
        return {"ok": False, "errors": ["world_prompt must be an object"]}
    errors = _collect_errors(_world_prompt_validator(), prompt)
    return {"ok": len(errors) == 0, "errors": errors}


def validate_commit_request(req: Any) -> dict[str, Any]:
    if not isinstance(req, dict):
        return {"ok": False, "errors": ["commit_request must be an object"]}
    errors = _collect_errors(_commit_request_validator(), req)
    return {"ok": len(errors) == 0, "errors": errors}

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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


def check_schema(errors: list[str]) -> None:
    schema_path = ROOT / "contracts" / "world_prompt.schema.json"
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    for candidate in (ROOT / "contracts").glob("*.schema.json"):
        Draft202012Validator.check_schema(load_json(candidate))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    valid = load_json(ROOT / "contracts" / "examples" / "valid_house.json")
    invalid = load_json(ROOT / "contracts" / "examples" / "invalid_reversed_stages.json")
    valid_errors = list(validator.iter_errors(valid))
    invalid_errors = list(validator.iter_errors(invalid))
    if valid_errors:
        errors.append("valid_house rejected: " + valid_errors[0].message)
    if not invalid_errors:
        errors.append("invalid_reversed_stages was accepted")


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
    check_orchestration(errors)
    if errors:
        print("AIDLE_VALIDATION=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("AIDLE_VALIDATION=PASS")
    print("scope=blueprint-links,all-schema-shapes,world-positive-negative,crew,task-dag")
    return 0


if __name__ == "__main__":
    sys.exit(main())

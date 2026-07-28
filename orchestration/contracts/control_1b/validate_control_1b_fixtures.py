#!/usr/bin/env python3
"""Deterministic Control 1B fixture validator (Directive 57 / C0 correction).

Validates:
  1) valid_context_fixture.json against the full input_context schema + semantic rules.
  2) EACH of the twelve invalid payloads in invalid_context_fixture.json against its
     intended root document, subschema pointer, or semantic rule — NOT merely the
     invalid-suite wrapper object.

Exit codes:
  0  — valid PASS and all twelve invalid cases FAIL as expected
  1  — unexpected valid failure, unexpected invalid pass, missing case, or IO error

Suite-root rejection is never used as proof of invalid cases.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "input_context.schema.json"
VALID_PATH = ROOT / "valid_context_fixture.json"
INVALID_PATH = ROOT / "invalid_context_fixture.json"

# Locked hash for the valid fixture (must remain byte-stable).
# Directive 60 (S0): re-locked after Exploration allowed_actions + default binding
# include rotate_camera_right (Human R camera yaw); INV-08 dual-fire still FAIL.
VALID_FIXTURE_SHA256_LOCKED = (
    "211605f46db73a4308252d7f10867260b5f8a8dd9f8d5fefc970f3c65f2d719f"
)

REQUIRED_CONTEXT_IDS = (
    "exploration",
    "companion",
    "build",
    "inspect",
    "world_tool",
)

# Per-case validation targets. Keep in sync with invalid_context_fixture.json.
# target:
#   root      — validate payload as full contract document
#   subschema — validate payload (or field) against schema_pointer
#   semantic  — semantic-only rule (still may use payload structure)
CASE_SPECS: dict[str, dict[str, Any]] = {
    "INV-01-unknown_context_id": {
        "target": "root",
        "declared_reasons": ["unknown_context_id", "schema_enum"],
    },
    "INV-02-unknown_action_id": {
        "target": "subschema",
        "schema_pointer": "#/$defs/action_entry",
        "fallback_pointer": "#/properties/actions/items",
        "declared_reasons": ["unknown_action_id", "schema_enum"],
    },
    "INV-03-hud_more_than_four": {
        "target": "subschema",
        "schema_pointer": "#/properties/contexts/items",
        "declared_reasons": ["hud_max_actions", "schema_maxItems"],
    },
    "INV-04-direct_durable_delete_allowed": {
        "target": "subschema",
        "schema_pointer": "#/properties/safety",
        "declared_reasons": ["safety_const_false", "schema_const"],
    },
    "INV-05-preview_owns_collision": {
        "target": "subschema",
        "schema_pointer": "#/properties/safety",
        "declared_reasons": ["preview_collision_forbidden", "schema_const"],
    },
    "INV-06-preview_owns_ownership": {
        "target": "subschema",
        "schema_pointer": "#/properties/safety",
        "declared_reasons": ["preview_ownership_forbidden", "schema_const"],
    },
    "INV-07-pipeline_skips_preview": {
        "target": "subschema",
        "schema_pointer": "#/properties/safety/properties/pipeline",
        "payload_key": "pipeline",
        "declared_reasons": ["pipeline_incomplete", "missing_preview_stage"],
    },
    "INV-08-multi_context_r_binding": {
        "target": "semantic",
        "semantic_rule": "multi_context_r",
        "declared_reasons": ["conflict_rule_C1B-CF-01", "build_only_r_violation"],
    },
    "INV-09-esc_pause_before_cancel": {
        "target": "semantic",
        "semantic_rule": "esc_priority",
        "declared_reasons": ["esc_priority_violation"],
    },
    "INV-10-unknown_top_level_field": {
        "target": "root",
        "declared_reasons": ["additionalProperties", "unknown_field"],
    },
    "INV-11-wrong_schema_version": {
        "target": "subschema",
        "schema_pointer": "#/properties/schema_version",
        "payload_key": "schema_version",
        "declared_reasons": ["schema_version_const"],
    },
    "INV-12-confirmation_hold_not_configurable": {
        "target": "subschema",
        "schema_pointer": "#/properties/accessibility/properties/confirmation_hold",
        "payload_key": "confirmation_hold",
        "declared_reasons": ["a11y_confirmation_hold", "schema_const"],
    },
}

EXPECTED_CASE_COUNT = 12


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_pointer(doc: dict[str, Any], pointer: str) -> Any:
    """Resolve a JSON Pointer within a document (RFC 6901, #/ form)."""
    if not pointer or pointer == "#":
        return doc
    if pointer.startswith("#/"):
        parts = pointer[2:].split("/")
    elif pointer.startswith("/"):
        parts = pointer[1:].split("/")
    else:
        raise ValueError(f"unsupported pointer: {pointer}")
    cur: Any = doc
    for raw in parts:
        key = raw.replace("~1", "/").replace("~0", "~")
        if not isinstance(cur, dict) or key not in cur:
            raise KeyError(f"pointer {pointer} missing segment {key}")
        cur = cur[key]
    return cur


def build_validator(schema: dict[str, Any]) -> Draft202012Validator:
    resource = Resource.from_contents(schema, default_specification=DRAFT202012)
    registry = Registry().with_resource(schema.get("$id", "urn:control-1b"), resource)
    return Draft202012Validator(schema, registry=registry)


def subschema_validator(
    root_schema: dict[str, Any], pointer: str
) -> Draft202012Validator:
    """Build a validator for a subschema, preserving $defs via $ref wrap when needed."""
    sub = resolve_pointer(root_schema, pointer)
    # Wrap so $ref to #/$defs/... still resolves against the full schema id.
    if isinstance(sub, dict) and "$ref" not in sub:
        # Prefer validating with the full document's registry and a schema that
        # is the subschema itself with $defs injected when refs are local.
        wrapped = dict(sub)
        if "$defs" in root_schema and "$defs" not in wrapped:
            wrapped = {**wrapped, "$defs": root_schema["$defs"]}
        if "$id" in root_schema:
            # Keep id-less to avoid id conflicts; use registry from root.
            pass
        resource = Resource.from_contents(
            root_schema, default_specification=DRAFT202012
        )
        registry = Registry().with_resource(
            root_schema.get("$id", "urn:control-1b"), resource
        )
        # If subschema uses $ref to #/$defs, validate via a tiny host schema.
        host = {
            "$schema": root_schema.get(
                "$schema", "https://json-schema.org/draft/2020-12/schema"
            ),
            "$id": (root_schema.get("$id", "urn:control-1b") + "/sub/" + pointer),
            "$defs": root_schema.get("$defs", {}),
            # inline the subschema under a synthetic allOf/ref path
            **{k: v for k, v in wrapped.items() if k != "$defs"},
        }
        # When pointer is to a $ref object already, just use it with defs.
        return Draft202012Validator(host, registry=registry)
    resource = Resource.from_contents(root_schema, default_specification=DRAFT202012)
    registry = Registry().with_resource(
        root_schema.get("$id", "urn:control-1b"), resource
    )
    return Draft202012Validator(sub, registry=registry)


def schema_errors(validator: Draft202012Validator, instance: Any) -> list[str]:
    errs = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    out: list[str] = []
    for e in errs:
        path = "/".join(str(p) for p in e.absolute_path) or "<root>"
        out.append(f"{path}: {e.message}")
    return out


# --- Semantic rules ---------------------------------------------------------


def semantic_context_cardinality(doc: dict[str, Any]) -> list[str]:
    """Exactly one of each required context_id."""
    errors: list[str] = []
    contexts = doc.get("contexts")
    if not isinstance(contexts, list):
        return ["contexts: missing or not an array"]
    ids = [
        c.get("context_id")
        for c in contexts
        if isinstance(c, dict) and "context_id" in c
    ]
    for req in REQUIRED_CONTEXT_IDS:
        count = ids.count(req)
        if count == 0:
            errors.append(f"context_cardinality: missing required context_id '{req}'")
        elif count > 1:
            errors.append(
                f"context_cardinality: duplicate context_id '{req}' (count={count})"
            )
    extras = set(ids) - set(REQUIRED_CONTEXT_IDS)
    for x in sorted(extras):
        if x is not None:
            errors.append(f"context_cardinality: unknown context_id '{x}'")
    if len(contexts) != 5:
        errors.append(
            f"context_cardinality: expected 5 contexts, got {len(contexts)}"
        )
    return errors


def _event_key(event: dict[str, Any]) -> tuple[Any, ...]:
    mods = tuple(sorted(event.get("modifiers") or []))
    return (event.get("device"), event.get("code"), mods)


def semantic_multi_context_r(payload: dict[str, Any]) -> list[str]:
    """INV-08 / C1B-CF-01 / C1B-ACT-05: physical R must not dual-fire camera+build.

    Fail if the same physical R event can dispatch both rotate_camera_right and
    build_rotate_right without disjoint context isolation.
    """
    errors: list[str] = []
    bindings = payload.get("default_bindings")
    if not isinstance(bindings, list):
        return ["multi_context_r: default_bindings missing"]

    # Map physical event -> list of (action_id, frozenset contexts or None=all)
    by_event: dict[tuple[Any, ...], list[tuple[str, frozenset[str] | None]]] = {}
    for b in bindings:
        if not isinstance(b, dict):
            continue
        action_id = b.get("action_id")
        events = b.get("events") or []
        ctx = b.get("active_contexts")
        ctx_set: frozenset[str] | None
        if ctx is None:
            ctx_set = None  # unbound = all contexts
        else:
            ctx_set = frozenset(ctx)
        for ev in events:
            if not isinstance(ev, dict):
                continue
            key = _event_key(ev)
            by_event.setdefault(key, []).append((str(action_id), ctx_set))

    for key, actions in by_event.items():
        if key[0] != "keyboard" or str(key[1]).upper() not in {"R", "KEY_R"}:
            # Only enforce the R dual-fire rule here (INV-08 surface).
            # Broader multi-context matrix can extend this later.
            if not (
                any(a == "rotate_camera_right" for a, _ in actions)
                and any(a == "build_rotate_right" for a, _ in actions)
            ):
                continue
        cam = [c for a, c in actions if a == "rotate_camera_right"]
        bld = [c for a, c in actions if a == "build_rotate_right"]
        if not cam or not bld:
            continue
        # Overlap if any camera context set intersects any build context set
        # (None means all contexts → always overlaps).
        def overlaps(a: frozenset[str] | None, b: frozenset[str] | None) -> bool:
            if a is None or b is None:
                return True
            return bool(a & b)

        conflict = any(overlaps(c, d) for c in cam for d in bld)
        if conflict:
            errors.append(
                "build_only_r_violation: physical R dispatches rotate_camera_right "
                "and build_rotate_right without context isolation "
                f"(event={key}; conflict_rule_C1B-CF-01)"
            )
    if not errors:
        # Also catch explicit multi-context claim in description-only fixtures
        # where both actions share R even if contexts look disjoint but both
        # list build (invalid isolation).
        r_actions = []
        for b in bindings:
            if not isinstance(b, dict):
                continue
            for ev in b.get("events") or []:
                if (
                    isinstance(ev, dict)
                    and ev.get("device") == "keyboard"
                    and str(ev.get("code", "")).upper() in {"R", "KEY_R"}
                ):
                    r_actions.append(b.get("action_id"))
        if (
            "rotate_camera_right" in r_actions
            and "build_rotate_right" in r_actions
            and not errors
        ):
            # Re-check with looser rule: same physical R bound to both action ids
            # while either binding includes the other's primary context.
            cam_ctxs: set[str] = set()
            bld_ctxs: set[str] = set()
            for b in bindings:
                if not isinstance(b, dict):
                    continue
                acts_on_r = False
                for ev in b.get("events") or []:
                    if (
                        isinstance(ev, dict)
                        and ev.get("device") == "keyboard"
                        and str(ev.get("code", "")).upper() in {"R", "KEY_R"}
                    ):
                        acts_on_r = True
                if not acts_on_r:
                    continue
                ctx = b.get("active_contexts")
                if b.get("action_id") == "rotate_camera_right":
                    cam_ctxs |= set(ctx) if ctx else set(REQUIRED_CONTEXT_IDS)
                if b.get("action_id") == "build_rotate_right":
                    bld_ctxs |= set(ctx) if ctx else set(REQUIRED_CONTEXT_IDS)
            if cam_ctxs & bld_ctxs:
                errors.append(
                    "build_only_r_violation: overlapping contexts for R "
                    f"camera={sorted(cam_ctxs)} build={sorted(bld_ctxs)} "
                    "(conflict_rule_C1B-CF-01)"
                )
    return errors


def semantic_esc_priority(payload: dict[str, Any]) -> list[str]:
    """INV-09 / C1B-ESC-01: pause_menu must not precede cancel targets."""
    errors: list[str] = []
    steps = payload.get("esc_priority")
    if not isinstance(steps, list) or not steps:
        return ["esc_priority_violation: esc_priority missing or empty"]

    ordered = sorted(
        [s for s in steps if isinstance(s, dict) and "order" in s],
        key=lambda s: int(s["order"]),
    )
    if not ordered:
        return ["esc_priority_violation: no ordered steps"]

    targets = [s.get("target") for s in ordered]
    if "pause_menu" not in targets:
        errors.append("esc_priority_violation: pause_menu missing from priority list")
        return errors

    pause_idx = targets.index("pause_menu")
    cancel_targets = {
        "pending_confirmation",
        "preview_hologram",
        "prompt_composer_or_dialogue",
        "inspect_panel",
        "world_tool_panel",
    }
    preceding = set(targets[:pause_idx])
    # Fail if pause is first, or no cancel target precedes pause.
    if pause_idx == 0:
        errors.append(
            "esc_priority_violation: pause_menu is order-first; cancel must precede pause"
        )
    elif not (preceding & cancel_targets):
        errors.append(
            "esc_priority_violation: no cancel target precedes pause_menu"
        )

    # Explicit wrong-order detection used by INV-09 fixture.
    if targets and targets[0] == "pause_menu":
        if "esc_priority_violation: pause_menu is order-first" not in " ".join(errors):
            errors.append(
                "esc_priority_violation: pause precedes cancel (wrong priority)"
            )
    return errors


def run_semantic(rule: str, payload: dict[str, Any]) -> list[str]:
    if rule == "multi_context_r":
        return semantic_multi_context_r(payload)
    if rule == "esc_priority":
        return semantic_esc_priority(payload)
    if rule == "context_cardinality":
        return semantic_context_cardinality(payload)
    return [f"unknown semantic rule: {rule}"]


def ensure_action_entry_def(schema: dict[str, Any]) -> dict[str, Any]:
    """Expose actions/items as $defs/action_entry for stable INV-02 targeting."""
    schema = json.loads(json.dumps(schema))  # deep copy
    defs = schema.setdefault("$defs", {})
    if "action_entry" not in defs:
        defs["action_entry"] = resolve_pointer(schema, "#/properties/actions/items")
    return schema


def validate_valid(
    schema: dict[str, Any], valid_doc: dict[str, Any]
) -> tuple[bool, list[str]]:
    v = build_validator(schema)
    errors = schema_errors(v, valid_doc)
    errors.extend(semantic_context_cardinality(valid_doc))
    # Full document also must not contain multi-context R / bad Esc.
    errors.extend(semantic_multi_context_r(valid_doc))
    errors.extend(semantic_esc_priority(valid_doc))
    return (len(errors) == 0, errors)


def validate_invalid_case(
    schema: dict[str, Any],
    case: dict[str, Any],
    spec: dict[str, Any],
) -> tuple[bool, str, list[str]]:
    """Return (rejected: bool, detail, errors). rejected=True means FAIL as expected."""
    case_id = case["case_id"]
    payload = case.get("payload")
    target = spec["target"]
    errors: list[str] = []

    if target == "root":
        v = build_validator(schema)
        errors = schema_errors(v, payload)
        if isinstance(payload, dict):
            errors.extend(semantic_context_cardinality(payload))
    elif target == "subschema":
        pointer = spec.get("schema_pointer") or spec.get("fallback_pointer")
        assert pointer
        try:
            # Prefer $defs/action_entry when present.
            if pointer == "#/$defs/action_entry":
                if "action_entry" not in schema.get("$defs", {}):
                    pointer = spec.get("fallback_pointer", "#/properties/actions/items")
            instance = payload
            if "payload_key" in spec and isinstance(payload, dict):
                instance = payload[spec["payload_key"]]
            v = subschema_validator(schema, pointer)
            errors = schema_errors(v, instance)
        except Exception as exc:  # noqa: BLE001 — harness must report
            errors = [f"subschema_setup_error: {exc}"]
    elif target == "semantic":
        rule = spec["semantic_rule"]
        if not isinstance(payload, dict):
            errors = ["semantic payload must be object"]
        else:
            errors = run_semantic(rule, payload)
    else:
        errors = [f"unknown target {target}"]

    rejected = len(errors) > 0
    detail = "; ".join(errors[:5]) if errors else "NO_ERRORS (unexpected pass)"
    return rejected, detail, errors


def main() -> int:
    print("=== Control 1B fixture validator ===")
    print(f"schema:  {SCHEMA_PATH}")
    print(f"valid:   {VALID_PATH}")
    print(f"invalid: {INVALID_PATH}")

    if not SCHEMA_PATH.is_file() or not VALID_PATH.is_file() or not INVALID_PATH.is_file():
        print("FATAL: missing schema or fixtures", file=sys.stderr)
        return 1

    valid_hash = sha256_file(VALID_PATH)
    print(f"valid_fixture_sha256: {valid_hash}")
    if valid_hash != VALID_FIXTURE_SHA256_LOCKED:
        print(
            f"FATAL: valid fixture hash mismatch "
            f"(locked={VALID_FIXTURE_SHA256_LOCKED})",
            file=sys.stderr,
        )
        return 1
    print("valid_fixture_hash_lock: OK")

    try:
        schema = ensure_action_entry_def(load_json(SCHEMA_PATH))
        valid_doc = load_json(VALID_PATH)
        invalid_suite = load_json(INVALID_PATH)
        Draft202012Validator.check_schema(schema)
    except (OSError, json.JSONDecodeError, SchemaError) as exc:
        print(f"FATAL: load/schema error: {exc}", file=sys.stderr)
        return 1

    # Suite root must NEVER be treated as a catalog document for invalid proof.
    if invalid_suite.get("fixture_kind") != "invalid_suite":
        print("FATAL: invalid fixture is not fixture_kind=invalid_suite", file=sys.stderr)
        return 1

    results: list[dict[str, Any]] = []
    failures = 0

    # --- Valid ---
    ok, verrs = validate_valid(schema, valid_doc)
    valid_result = {
        "case_id": "VALID-01",
        "declared_reason": ["must_validate"],
        "result": "PASS" if ok else "FAIL",
        "detail": "schema+semantic OK" if ok else "; ".join(verrs[:8]),
    }
    results.append(valid_result)
    print(f"[VALID-01] expected=PASS actual={valid_result['result']} :: {valid_result['detail']}")
    if not ok:
        failures += 1

    # --- Invalid cases ---
    cases = invalid_suite.get("cases") or []
    if len(cases) != EXPECTED_CASE_COUNT:
        print(
            f"FATAL: expected {EXPECTED_CASE_COUNT} invalid cases, got {len(cases)}",
            file=sys.stderr,
        )
        return 1

    seen: set[str] = set()
    for case in cases:
        case_id = case.get("case_id")
        if not case_id or case_id not in CASE_SPECS:
            print(f"FATAL: unknown or missing case_id: {case_id}", file=sys.stderr)
            return 1
        seen.add(case_id)
        spec = CASE_SPECS[case_id]
        declared = case.get("expected_reject") or spec["declared_reasons"]
        rejected, detail, _errs = validate_invalid_case(schema, case, spec)
        # Expected: each invalid payload is REJECTED (FAIL validation).
        actual = "FAIL" if rejected else "PASS"
        expected = "FAIL"
        row = {
            "case_id": case_id,
            "declared_reason": declared,
            "validation_target": spec["target"],
            "schema_pointer": spec.get("schema_pointer") or spec.get("semantic_rule"),
            "result": actual,
            "expected": expected,
            "detail": detail,
            "ok": actual == expected,
        }
        results.append(row)
        status = "OK" if row["ok"] else "UNEXPECTED"
        print(
            f"[{case_id}] target={row['validation_target']} "
            f"declared={declared} expected={expected} actual={actual} "
            f"[{status}] :: {detail}"
        )
        if not row["ok"]:
            failures += 1

    missing = set(CASE_SPECS) - seen
    if missing:
        print(f"FATAL: missing cases in fixture: {sorted(missing)}", file=sys.stderr)
        return 1

    invalid_fail_count = sum(
        1
        for r in results
        if r["case_id"] != "VALID-01" and r.get("result") == "FAIL" and r.get("ok")
    )
    print("--- summary ---")
    print(f"valid: {'PASS' if ok else 'FAIL'}")
    print(f"invalid_rejected: {invalid_fail_count}/{EXPECTED_CASE_COUNT}")
    print(f"failures: {failures}")

    if failures:
        print("HARNESS_RESULT=FAIL", file=sys.stderr)
        return 1
    print("HARNESS_RESULT=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

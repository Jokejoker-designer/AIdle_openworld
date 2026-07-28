#!/usr/bin/env python3
"""Deterministic staging gate for AIdle DNA Platform vNext.

This validator reads existing sources only. It validates the staging schemas,
checks the content-addressed source registry, performs cross-catalog semantic
checks on the Nori-7 example, and proves two adversarial mutations fail.

It does not modify DNA, game files, catalogs, directives or world state.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SCHEMAS = HERE / "schemas"
EXAMPLES = HERE / "examples"
SOURCE_REGISTRY = HERE / "SOURCE_REGISTRY.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_fingerprint(doc: dict[str, Any]) -> str:
    projection = {k: v for k, v in doc.items() if k != "payload_fingerprint"}
    raw = json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def schema_errors(doc: Any, schema: dict[str, Any]) -> list[str]:
    errors = Draft202012Validator(schema).iter_errors(doc)
    out: list[str] = []
    for error in sorted(errors, key=lambda e: list(e.absolute_path)):
        path = "$"
        for part in error.absolute_path:
            path += f"[{part}]" if isinstance(part, int) else f".{part}"
        out.append(f"schema:{path}:{error.message}")
    return out


def unique_check(values: list[str], label: str) -> list[str]:
    seen: set[str] = set()
    errors: list[str] = []
    for value in values:
        if value in seen:
            errors.append(f"duplicate_{label}:{value}")
        seen.add(value)
    return errors


class SourceCatalogs:
    def __init__(self, registry: dict[str, Any]) -> None:
        self.registry = registry
        self.source_by_id = {s["source_id"]: s for s in registry["sources"]}

        def source(source_id: str) -> Any:
            return load_json(REPO / self.source_by_id[source_id]["path"])

        self.modules = {
            row["module_id"]: row for row in source("module_catalog")["modules"]
        }
        self.sockets = {
            row["socket_type"]: row for row in source("socket_types")["socket_types"]
        }
        self.skeletons = {
            row["skeleton_id"]: row
            for row in source("skeleton_families")["skeleton_families"]
        }
        self.animations = {
            row["animation_set_id"]: row
            for row in source("animation_library")["animation_sets"]
        }
        self.materials = {
            row["theme_id"]: row
            for row in source("material_themes")["material_themes"]
        }
        self.behaviors = {
            row["behavior_id"]: row
            for row in source("behavior_blocks")["behavior_blocks"]
        }
        self.elements = {
            row["element_id"]: row for row in source("element_catalog")["elements"]
        }
        self.physics = {
            row["module_id"]: row
            for row in source("module_physics_bindings")["bindings"]
        }


def validate_source_registry(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ids = [s.get("source_id") for s in registry.get("sources", [])]
    errors.extend(unique_check(ids, "source_id"))

    for source in registry.get("sources", []):
        path = REPO / source["path"]
        if not path.is_file():
            errors.append(f"source_missing:{source['source_id']}:{path}")
            continue
        actual = sha256_file(path)
        if actual != source["sha256"]:
            errors.append(
                f"source_hash_mismatch:{source['source_id']}:{actual}!={source['sha256']}"
            )

    try:
        catalogs = SourceCatalogs(registry)
    except Exception as exc:  # pragma: no cover - reported as a gate error
        errors.append(f"source_load_failed:{type(exc).__name__}:{exc}")
        return errors

    observed = registry["observed_limits"]
    if len(catalogs.modules) != observed["module_count"]:
        errors.append("observed_module_count_mismatch")
    if observed["all_modules_design_ready"] and any(
        m.get("status") != "DESIGN_READY" for m in catalogs.modules.values()
    ):
        errors.append("observed_module_status_mismatch")
    if len(catalogs.skeletons) != observed["skeleton_family_count"]:
        errors.append("observed_skeleton_count_mismatch")
    expected_bones = tuple(observed["all_skeleton_required_bones"])
    if any(tuple(s.get("required_bones", [])) != expected_bones for s in catalogs.skeletons.values()):
        errors.append("observed_skeleton_required_bones_mismatch")
    if len(catalogs.animations) != observed["animation_set_count"]:
        errors.append("observed_animation_set_count_mismatch")
    clips = [
        clip
        for animation in catalogs.animations.values()
        for clip in animation.get("clips", [])
    ]
    if len(clips) != observed["animation_clip_count"]:
        errors.append("observed_animation_clip_count_mismatch")
    expected_clip_keys = set(observed["animation_clip_fields_only"])
    if any(set(clip) != expected_clip_keys for clip in clips):
        errors.append("observed_animation_clip_shape_mismatch")
    return errors


def finite_numbers(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, bool):
        return errors
    if isinstance(value, float) and not math.isfinite(value):
        errors.append(f"non_finite_number:{path}")
    elif isinstance(value, dict):
        for key, child in value.items():
            errors.extend(finite_numbers(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(finite_numbers(child, f"{path}[{index}]"))
    return errors


def validate_request(doc: dict[str, Any]) -> list[str]:
    errors = finite_numbers(doc)
    expected = canonical_fingerprint(doc)
    if doc.get("payload_fingerprint") != expected:
        errors.append(
            f"request_fingerprint_mismatch:{doc.get('payload_fingerprint')}!={expected}"
        )
    return errors


def validate_recipe(
    doc: dict[str, Any],
    catalogs: SourceCatalogs,
    request: dict[str, Any],
) -> list[str]:
    errors = finite_numbers(doc)
    expected_fp = canonical_fingerprint(doc)
    if doc.get("payload_fingerprint") != expected_fp:
        errors.append(
            f"recipe_fingerprint_mismatch:{doc.get('payload_fingerprint')}!={expected_fp}"
        )

    if doc.get("request_id") != request.get("request_id"):
        errors.append("request_id_mismatch")
    if doc.get("world_profile") != request["target_context"]["world_profile"]:
        errors.append("world_profile_request_mismatch")
    if doc.get("entity_kind") != request["intent"]["entity_kind"]:
        errors.append("entity_kind_request_mismatch")
    if len(doc.get("instances", [])) > request["budgets"]["max_modules"]:
        errors.append("module_budget_exceeded")

    instances = doc.get("instances", [])
    instance_ids = [row.get("instance_id") for row in instances]
    errors.extend(unique_check(instance_ids, "instance_id"))
    instance_by_id = {row.get("instance_id"): row for row in instances}
    root_id = doc.get("root_instance_id")
    if root_id not in instance_by_id:
        errors.append(f"root_missing:{root_id}")
    root_roles = [row.get("instance_id") for row in instances if row.get("role") == "ROOT"]
    if root_roles != [root_id]:
        errors.append(f"root_role_invalid:{root_roles}!={[root_id]}")

    module_by_instance: dict[str, dict[str, Any]] = {}
    for row in instances:
        instance_id = row.get("instance_id")
        module_id = row.get("module_ref", {}).get("module_id")
        module = catalogs.modules.get(module_id)
        if module is None:
            errors.append(f"unknown_module:{instance_id}:{module_id}")
            continue
        module_by_instance[instance_id] = module
        profiles = set(module.get("world_profiles", []))
        if doc["world_profile"] not in profiles and "shared" not in profiles:
            errors.append(
                f"module_world_profile_mismatch:{instance_id}:{module_id}:{doc['world_profile']}"
            )

    kind_to_root_domains = {
        "CHARACTER": {"CHARACTER"},
        "CREATURE": {"CHARACTER"},
        "PROP": {"PROP", "GEOMETRY"},
        "VEHICLE": {"MODULE_CLUSTER", "PROP", "CHARACTER"},
        "BUILDING": {"ARCHITECTURE", "MODULE_CLUSTER"},
        "TERRAIN": {"TERRAIN"},
        "PLANT": {"NATURE", "CHARACTER"},
        "EFFECT": {"GEOMETRY", "PROP"},
        "SYSTEM": {"PROP", "MODULE_CLUSTER", "WORLD"},
        "REGION": {"WORLD", "MODULE_CLUSTER", "TERRAIN"},
    }
    root_module = module_by_instance.get(root_id)
    if root_module and root_module.get("domain") not in kind_to_root_domains[doc["entity_kind"]]:
        errors.append(
            f"root_domain_mismatch:{doc['entity_kind']}:{root_module.get('domain')}"
        )

    connections = doc.get("connections", [])
    errors.extend(
        unique_check([row.get("connection_id") for row in connections], "connection_id")
    )
    for connection in connections:
        label = connection.get("connection_id")
        from_id = connection.get("from_instance")
        to_id = connection.get("to_instance")
        if from_id == to_id:
            errors.append(f"self_connection:{label}")
        if from_id not in instance_by_id:
            errors.append(f"dangling_connection_from:{label}:{from_id}")
        if to_id not in instance_by_id:
            errors.append(f"dangling_connection_to:{label}:{to_id}")

        from_module = module_by_instance.get(from_id)
        to_module = module_by_instance.get(to_id)
        from_socket = connection.get("from_socket")
        to_socket = connection.get("to_socket")
        if from_socket not in catalogs.sockets:
            errors.append(f"unknown_socket:{label}:{from_socket}")
        if to_socket not in catalogs.sockets:
            errors.append(f"unknown_socket:{label}:{to_socket}")
        if from_module:
            declared = set(from_module.get("socket_inputs", [])) | set(
                from_module.get("socket_outputs", [])
            )
            if from_socket not in declared:
                errors.append(f"socket_not_declared:{label}:{from_id}:{from_socket}")
        if to_module:
            declared = set(to_module.get("socket_inputs", [])) | set(
                to_module.get("socket_outputs", [])
            )
            if to_socket not in declared:
                errors.append(f"socket_not_declared:{label}:{to_id}:{to_socket}")
        if from_socket in catalogs.sockets and to_socket in catalogs.sockets:
            forward = to_socket in catalogs.sockets[from_socket].get(
                "compatible_with", []
            )
            reverse = from_socket in catalogs.sockets[to_socket].get(
                "compatible_with", []
            )
            if not (forward and reverse):
                errors.append(
                    f"socket_not_mutually_compatible:{label}:{from_socket}:{to_socket}"
                )
        polarities = (connection.get("from_polarity"), connection.get("to_polarity"))
        if polarities not in {("output", "input"), ("input", "output"), ("peer", "peer")}:
            errors.append(f"socket_polarity_invalid:{label}:{polarities}")

    presentation = doc["facets"]["presentation"]
    theme = catalogs.materials.get(presentation.get("material_theme_id"))
    if theme is None:
        errors.append(f"unknown_material_theme:{presentation.get('material_theme_id')}")
    else:
        if doc["world_profile"] not in theme.get("world_profiles", []):
            errors.append("material_theme_world_profile_mismatch")
        palette = set(theme.get("palette", {}))
        for binding in presentation.get("material_bindings", []):
            ids = (
                list(module_by_instance)
                if binding["instance_id"] == "*"
                else [binding["instance_id"]]
            )
            if binding["palette_token"] not in palette:
                errors.append(
                    f"unknown_palette_token:{binding['palette_token']}"
                )
            for instance_id in ids:
                module = module_by_instance.get(instance_id)
                if module is None:
                    errors.append(f"material_dangling_instance:{instance_id}")
                elif binding["slot"] not in module.get("material_slots", []):
                    errors.append(
                        f"material_slot_not_declared:{instance_id}:{binding['slot']}"
                    )

    motion = doc["facets"]["motion"]
    skeleton_id = motion.get("skeleton_id")
    animation_id = motion.get("animation_set_id")
    skeleton = catalogs.skeletons.get(skeleton_id) if skeleton_id else None
    animation = catalogs.animations.get(animation_id) if animation_id else None
    if skeleton_id and skeleton is None:
        errors.append(f"unknown_skeleton:{skeleton_id}")
    if animation_id and animation is None:
        errors.append(f"unknown_animation_set:{animation_id}")
    if skeleton and animation and animation.get("skeleton_id") != skeleton_id:
        errors.append("skeleton_animation_mismatch")
    if root_module:
        if root_module.get("skeleton_id") != skeleton_id:
            errors.append("root_skeleton_mismatch")
        if root_module.get("animation_set_id") != animation_id:
            errors.append("root_animation_set_mismatch")
    if skeleton and skeleton_id not in set(
        next(
            (
                b.get("allowed_skeletons", [])
                for b in load_json(
                    REPO
                    / "world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.1_Tier3/foundation_core/AIdle_Block_Module_Foundation_v1.0/catalogs/world_profile_bindings.json"
                )["bindings"]
                if b.get("world_profile") == doc["world_profile"]
            ),
            [],
        )
    ):
        errors.append("skeleton_not_allowed_for_world_profile")
    if animation:
        clip_ids = {c["clip_id"] for c in animation.get("clips", [])}
        action_ids = {a["action_id"] for a in motion.get("actions", [])}
        if action_ids != clip_ids:
            errors.append(
                f"motion_action_coverage_mismatch:{sorted(action_ids)}!={sorted(clip_ids)}"
            )
        metadata_only = all(
            set(c) == {"clip_id", "loop", "events"} for c in animation.get("clips", [])
        )
        if metadata_only and any(
            a.get("runtime_payload_proven") for a in motion.get("actions", [])
        ):
            errors.append("motion_payload_false_proof")

    for binding in doc["facets"]["behaviors"]:
        instance_id = binding.get("instance_id")
        behavior_id = binding.get("behavior_id")
        behavior = catalogs.behaviors.get(behavior_id)
        if instance_id not in instance_by_id:
            errors.append(f"behavior_dangling_instance:{instance_id}")
        if behavior is None:
            errors.append(f"unknown_behavior:{behavior_id}")
        else:
            if behavior.get("runtime_owner") != "GODOT":
                errors.append(f"behavior_runtime_owner_invalid:{behavior_id}")
            if behavior.get("ai_authority") != "CONFIGURE_ONLY":
                errors.append(f"behavior_authority_invalid:{behavior_id}")
        if binding.get("ai_authority") != "CONFIGURE_ONLY":
            errors.append(f"behavior_binding_authority_invalid:{behavior_id}")

    for binding in doc["facets"]["physics"]["bindings"]:
        instance_id = binding.get("instance_id")
        module = module_by_instance.get(instance_id)
        if module is None:
            errors.append(f"physics_dangling_instance:{instance_id}")
            continue
        for element_id in binding.get("element_ids", []):
            if element_id not in catalogs.elements:
                errors.append(f"unknown_element:{instance_id}:{element_id}")
        source_binding = catalogs.physics.get(module["module_id"])
        if source_binding is None:
            errors.append(f"missing_module_physics_binding:{module['module_id']}")
            continue
        if binding.get("element_ids") != source_binding.get("elements"):
            errors.append(f"physics_element_mismatch:{instance_id}")
        if binding.get("physical_profile_id") != source_binding.get(
            "physical_profile_id"
        ):
            errors.append(f"physics_profile_mismatch:{instance_id}")
        if binding.get("reaction_rule_ids") != source_binding.get(
            "reaction_allowlist"
        ):
            errors.append(f"physics_reaction_mismatch:{instance_id}")

    registry_sources = catalogs.source_by_id
    for source in doc["provenance"]["sources"]:
        registered = registry_sources.get(source["source_id"])
        if registered is None:
            errors.append(f"unknown_provenance_source:{source['source_id']}")
        elif registered["sha256"] != source["sha256"]:
            errors.append(f"provenance_hash_mismatch:{source['source_id']}")

    authority = doc.get("authority", {})
    if authority.get("may_commit_world") is not False:
        errors.append("authority_may_commit_world")
    if authority.get("may_execute_generated_code") is not False:
        errors.append("authority_generated_code")
    if authority.get("may_write_catalog") is not False:
        errors.append("authority_catalog_write")

    design_only_selected = any(
        module.get("status") == "DESIGN_READY"
        for module in module_by_instance.values()
    )
    skeleton_stub = bool(
        skeleton
        and len(skeleton.get("required_bones", []))
        < int(skeleton.get("bone_count_target", 0))
    )
    animation_metadata_only = bool(
        animation
        and all(
            set(c) == {"clip_id", "loop", "events"}
            for c in animation.get("clips", [])
        )
    )
    source_not_runtime_ready = (
        design_only_selected or skeleton_stub or animation_metadata_only
    )
    readiness = doc["readiness"]
    if source_not_runtime_ready and readiness.get("runtime_ready"):
        errors.append("false_runtime_ready")
    if not readiness.get("runtime_ready"):
        if not readiness.get("blockers"):
            errors.append("missing_readiness_blockers")
        if not readiness.get("asset_requests"):
            errors.append("missing_asset_requests")

    return errors


def validate_result(
    result: dict[str, Any],
    request: dict[str, Any],
    recipe: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if result.get("request_id") != request.get("request_id"):
        errors.append("result_request_id_mismatch")
    recipe_ref = result.get("recipe_ref") or {}
    if recipe_ref.get("recipe_id") != recipe.get("recipe_id"):
        errors.append("result_recipe_id_mismatch")
    if recipe_ref.get("payload_fingerprint") != recipe.get("payload_fingerprint"):
        errors.append("result_recipe_fingerprint_mismatch")
    request_ids = {
        row["asset_request_id"] for row in recipe["readiness"]["asset_requests"]
    }
    result_ids = {row["asset_request_id"] for row in result["asset_requests"]}
    if request_ids != result_ids:
        errors.append("result_asset_request_coverage_mismatch")
    if not recipe["readiness"]["runtime_ready"]:
        if result.get("status") != "ASSET_REQUEST_REQUIRED":
            errors.append("result_status_readiness_mismatch")
        if result.get("next_route") != "ASSET_AUTHORING_GATE":
            errors.append("result_route_readiness_mismatch")
    return errors


def apply_pointer_mutation(base: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(base)
    pointer = fixture["mutation"]["json_pointer"]
    parts = [p.replace("~1", "/").replace("~0", "~") for p in pointer.split("/")[1:]]
    target: Any = out
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    last = parts[-1]
    if isinstance(target, list):
        target[int(last)] = fixture["mutation"]["value"]
    else:
        target[last] = fixture["mutation"]["value"]
    out["payload_fingerprint"] = canonical_fingerprint(out)
    return out


def main() -> int:
    failures: list[str] = []
    print("=== AIdle DNA Platform vNext staging gate ===")
    print(f"ROOT={HERE}")

    schema_files = sorted(SCHEMAS.glob("*.schema.json"))
    schemas: dict[str, dict[str, Any]] = {}
    for path in schema_files:
        schema = load_json(path)
        try:
            Draft202012Validator.check_schema(schema)
            print(f"PASS schema definition: {path.name}")
            schemas[path.name] = schema
        except Exception as exc:
            failures.append(f"schema_definition_invalid:{path.name}:{exc}")
            print(f"FAIL schema definition: {path.name}: {exc}")

    registry = load_json(SOURCE_REGISTRY)
    registry_errors = validate_source_registry(registry)
    if registry_errors:
        failures.extend(registry_errors)
        for error in registry_errors:
            print(f"FAIL source registry: {error}")
    else:
        print(f"PASS source registry hashes: {len(registry['sources'])}/{len(registry['sources'])}")

    catalogs = SourceCatalogs(registry)
    request = load_json(EXAMPLES / "nori7_generation_request.json")
    recipe = load_json(EXAMPLES / "nori7_universal_recipe.json")
    result = load_json(EXAMPLES / "nori7_generation_result.json")

    positive_checks = [
        (
            "generation_request",
            schema_errors(request, schemas["generation_request.schema.json"])
            + validate_request(request),
        ),
        (
            "universal_entity_recipe",
            schema_errors(recipe, schemas["universal_entity_recipe.schema.json"])
            + validate_recipe(recipe, catalogs, request),
        ),
        (
            "generation_result",
            schema_errors(result, schemas["generation_result.schema.json"])
            + validate_result(result, request, recipe),
        ),
    ]
    for label, errors in positive_checks:
        if errors:
            failures.extend(f"{label}:{error}" for error in errors)
            print(f"FAIL positive {label}: {len(errors)} error(s)")
            for error in errors:
                print(f"  {error}")
        else:
            print(f"PASS positive {label}")

    negative_files = sorted(EXAMPLES.glob("invalid_*_recipe.json"))
    for fixture_path in negative_files:
        fixture = load_json(fixture_path)
        mutated = apply_pointer_mutation(recipe, fixture)
        errors = schema_errors(
            mutated, schemas["universal_entity_recipe.schema.json"]
        ) + validate_recipe(mutated, catalogs, request)
        expected = fixture["expected_error"]
        if any(expected in error for error in errors):
            print(f"PASS negative rejected: {fixture_path.name} -> {expected}")
        else:
            failures.append(
                f"negative_not_rejected_as_expected:{fixture_path.name}:{expected}:{errors}"
            )
            print(
                f"FAIL negative: {fixture_path.name} expected={expected} errors={errors}"
            )

    if failures:
        print("--- FAILURES ---")
        for failure in failures:
            print(failure)
        print(f"FAIL gate: {len(failures)} failure(s)")
        return 1

    print("--- summary ---")
    print(f"schemas={len(schema_files)}")
    print(f"source_hashes={len(registry['sources'])}")
    print("positive_examples=3")
    print(f"negative_examples={len(negative_files)}")
    print("verdict=STAGING_CONTRACT_GREEN_NO_RUNTIME_ACCEPTANCE")
    return 0


if __name__ == "__main__":
    sys.exit(main())

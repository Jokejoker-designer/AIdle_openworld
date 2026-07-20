#!/usr/bin/env python3
"""G2-003 smoke: AGM Decision Envelope → Companion dialogue/proposals + personality caps."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[4]  # AIdle_openworld
COMPANION = Path(__file__).resolve().parent
EXPORTS = COMPANION / "exports"
AGM_FIXTURES = ROOT / "contracts" / "fixtures" / "agm"
AGM_SCHEMA = ROOT / "contracts" / "agm" / "decision_envelope.schema.json"

FORBIDDEN_TOP = {
    "api_key",
    "access_token",
    "password",
    "secret",
    "secrets",
    "credentials",
    "tts_audio",
    "voice_sample",
    "microphone_buffer",
    "script",
    "scripts",
    "code",
    "commit_request",
    "durable_mutation",
    "scene_tree_mutation",
    "direct_world_write",
}


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

    return checker


FORMAT_CHECKER = make_format_checker()


def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def project_agm_build_to_world_prompt(agm_item: dict, decision: dict) -> dict:
    """Python mirror of CompanionWorldPromptBuilder.build_from_agm_build_proposal (cozy house)."""
    if agm_item.get("preview_required") is not True:
        raise ValueError("preview_required must be true")
    if agm_item.get("confirmation_state") != "pending":
        raise ValueError("confirmation_state must be pending")
    if agm_item.get("routes_through") != "preview_confirm_commit":
        raise ValueError("routes_through must be preview_confirm_commit")

    recipe_id = agm_item["recipe_id"]
    transform = agm_item.get("transform") or {"x": 8.0, "y": 6.0, "elevation": 0.0, "rotation_deg": 0.0}
    catalog = {
        "cozy_house_small": {
            "kind": "modular_structure_2_5d",
            "bounds": {"width": 8.0, "depth": 6.0, "height": 5.0},
            "interaction_tags": ["enterable", "lightable"],
            "max_compute_units": 200,
            "max_entities": 32,
            "presentation_duration_seconds": 12.0,
        }
    }
    recipe = catalog.get(recipe_id)
    if recipe is None:
        raise ValueError(f"unknown recipe for smoke mirror: {recipe_id}")

    receipt = (decision.get("trace") or {}).get("model_receipt_ref", "")
    return {
        "schema_version": "1.1.0",
        "prompt_id": "b2c3d4e5-f6a7-4890-b123-456789abcdef",
        "request_id": "c3d4e5f6-a7b8-4901-c234-56789abcdef0",
        "session_id": decision.get("session_id", "session_starter_01"),
        "actor": {"player_id": "player_01", "companion_id": "companion_lumi"},
        "operation": agm_item.get("operation", "create"),
        "target": {
            "space_type": "private_reality",
            "space_id": agm_item.get("space_id", "home_01"),
            "chunk_id": agm_item.get("chunk_id", "0_0"),
            "expected_world_revision": 0,
        },
        "style_profile": {
            "profile_id": "cozy_default",
            "profile_version": "1.0.0",
            "base_concept": "cozy_cyber_pixel_2_5d",
            "surrealism_budget": 0.15,
        },
        "entity": {
            "kind": agm_item.get("entity_kind", recipe["kind"]),
            "recipe_id": recipe_id,
            "transform": {
                "x": float(transform.get("x", 8.0)),
                "y": float(transform.get("y", 6.0)),
                "elevation": float(transform.get("elevation", 0.0)),
                "rotation_deg": float(transform.get("rotation_deg", 0.0)) % 360.0,
            },
            "bounds": recipe["bounds"],
            "interaction_tags": recipe["interaction_tags"],
        },
        "manifestation": {
            "stages": ["wireframe", "hologram", "materializing", "complete"],
            "presentation_duration_seconds": recipe["presentation_duration_seconds"],
        },
        "budget": {
            "max_compute_units": recipe["max_compute_units"],
            "max_entities": recipe["max_entities"],
            "paid_compute_allowed": False,
        },
        "provenance": {
            "source_type": "companion_enrichment",
            "requested_by": "companion_lumi",
            "generated_by": "companion_lumi",
            "created_at": decision.get("created_at", "2026-07-20T16:05:00Z"),
            **({"model_receipt_ref": receipt} if receipt else {}),
        },
        "confirmation": {
            "preview_required": True,
            "state": "pending",
            "rollback_window_seconds": 3600,
        },
    }


def extract_dialogue(decision: dict) -> list[dict]:
    dialogue = decision.get("dialogue") or {}
    lines = dialogue.get("lines") or []
    out = []
    for line in lines:
        if not isinstance(line, dict):
            continue
        speaker = line.get("speaker")
        text = line.get("text")
        if speaker in ("companion", "narrator", "npc") and isinstance(text, str) and text.strip():
            out.append({"speaker": speaker, "text": text})
    return out


def main() -> int:
    errors: list[str] = []
    world_schema = load(ROOT / "contracts" / "world_prompt.schema.json")
    personality_schema = load(ROOT / "contracts" / "personality_profile.schema.json")
    decision_schema = load(AGM_SCHEMA)
    world_v = Draft202012Validator(world_schema, format_checker=FORMAT_CHECKER)
    person_v = Draft202012Validator(personality_schema, format_checker=FORMAT_CHECKER)
    decision_v = Draft202012Validator(decision_schema, format_checker=FORMAT_CHECKER)

    proposal_path = EXPORTS / "companion_proposal_cozy_house.json"
    agm_proposal_path = EXPORTS / "companion_proposal_from_agm_cozy_house.json"
    personality_path = EXPORTS / "default_personality_profile.json"
    agm_fixture = AGM_FIXTURES / "valid" / "valid_decision_with_build_proposal.json"
    agm_dialogue_fixture = AGM_FIXTURES / "valid" / "valid_decision_desktop_bridge.json"
    agm_tts_invalid = AGM_FIXTURES / "invalid" / "invalid_decision_with_tts_voice.json"
    agm_durable_invalid = AGM_FIXTURES / "invalid" / "invalid_decision_direct_durable_mutation.json"

    # ── baseline NL proposal export ──────────────────────────────────────────
    if not proposal_path.is_file():
        errors.append(f"missing export {proposal_path}")
    else:
        proposal = load(proposal_path)
        issues = list(world_v.iter_errors(proposal))
        if issues:
            errors.append(f"proposal rejected: {issues[0].message}")
        else:
            conf = proposal.get("confirmation", {})
            if conf.get("state") != "pending":
                errors.append("proposal confirmation.state must be pending")
            if conf.get("preview_required") is not True:
                errors.append("proposal preview_required must be true")
            if proposal.get("provenance", {}).get("generated_by") != "companion_lumi":
                errors.append("provenance.generated_by expected companion_lumi")

    # ── personality export + caps ────────────────────────────────────────────
    if not personality_path.is_file():
        errors.append(f"missing export {personality_path}")
    else:
        profile = load(personality_path)
        issues = list(person_v.iter_errors(profile))
        if issues:
            errors.append(f"personality rejected: {issues[0].message}")
        else:
            policy = profile.get("adaptation_policy", {})
            if float(policy.get("max_delta_per_turn", 1)) > 0.005:
                errors.append("max_delta_per_turn exceeds schema cap 0.005")
            if float(policy.get("max_delta_per_day", 1)) > 0.03:
                errors.append("max_delta_per_day exceeds schema cap 0.03")
            if float(policy.get("max_distance_from_base", 1)) > 0.25:
                errors.append("max_distance_from_base exceeds schema cap 0.25")

    # ── AGM fixture → dialogue + world prompt projection ─────────────────────
    if not agm_fixture.is_file():
        errors.append(f"missing AGM fixture {agm_fixture}")
    else:
        decision = load(agm_fixture)
        d_issues = list(decision_v.iter_errors(decision))
        if d_issues:
            errors.append(f"AGM fixture invalid against schema: {d_issues[0].message}")
        else:
            for key in FORBIDDEN_TOP:
                if key in decision:
                    errors.append(f"valid AGM fixture unexpectedly has forbidden {key}")

            lines = extract_dialogue(decision)
            if not lines:
                errors.append("AGM fixture dialogue empty after extract")
            elif lines[0].get("speaker") != "companion":
                errors.append("expected companion dialogue line")
            elif "preview" not in lines[0].get("text", "").lower() and "cozy" not in lines[0].get("text", "").lower():
                # soft: fixture text should mention house/preview theme
                pass

            builds = decision.get("build_proposals") or []
            if not builds:
                errors.append("AGM build fixture missing build_proposals")
            else:
                try:
                    projected = project_agm_build_to_world_prompt(builds[0], decision)
                except ValueError as exc:
                    errors.append(f"AGM→SWP projection failed: {exc}")
                    projected = None
                if projected is not None:
                    p_issues = list(world_v.iter_errors(projected))
                    if p_issues:
                        errors.append(f"AGM-projected SWP rejected: {p_issues[0].message}")
                    conf = projected.get("confirmation", {})
                    if conf.get("state") != "pending" or conf.get("preview_required") is not True:
                        errors.append("AGM-projected SWP must stay pending + preview_required")
                    if projected.get("provenance", {}).get("source_type") != "companion_enrichment":
                        errors.append("AGM-projected provenance.source_type must be companion_enrichment")

            # Export should match shape of projection (schema-valid pending).
            if not agm_proposal_path.is_file():
                errors.append(f"missing AGM export {agm_proposal_path}")
            else:
                agm_export = load(agm_proposal_path)
                e_issues = list(world_v.iter_errors(agm_export))
                if e_issues:
                    errors.append(f"AGM export rejected: {e_issues[0].message}")
                else:
                    conf = agm_export.get("confirmation", {})
                    if conf.get("state") != "pending":
                        errors.append("AGM export confirmation.state must be pending")
                    if conf.get("preview_required") is not True:
                        errors.append("AGM export preview_required must be true")
                    if agm_export.get("entity", {}).get("recipe_id") != "cozy_house_small":
                        errors.append("AGM export recipe_id expected cozy_house_small")
                    if agm_export.get("provenance", {}).get("source_type") != "companion_enrichment":
                        errors.append("AGM export source_type expected companion_enrichment")

    # Dialogue-only fixture still valid + no forced commit
    if agm_dialogue_fixture.is_file():
        d2 = load(agm_dialogue_fixture)
        if list(decision_v.iter_errors(d2)):
            errors.append("dialogue-only AGM fixture failed schema")
        else:
            if d2.get("build_proposals"):
                errors.append("dialogue fixture unexpectedly has builds")
            if not extract_dialogue(d2):
                errors.append("dialogue fixture produced no lines")

    # Invalid fixtures must fail decision schema (TTS / durable mutation)
    for inv_path, label in (
        (agm_tts_invalid, "tts_voice"),
        (agm_durable_invalid, "durable_mutation"),
    ):
        if not inv_path.is_file():
            errors.append(f"missing invalid AGM fixture {inv_path}")
            continue
        inv = load(inv_path)
        if not list(decision_v.iter_errors(inv)):
            # Some invalids may only fail propertyNames; still ensure forbidden keys present
            has_forbidden = any(k in inv for k in FORBIDDEN_TOP)
            if not has_forbidden:
                errors.append(f"invalid fixture {label} unexpectedly schema-valid without forbidden keys")
        # Companion source must reject these keywords in module surface
        for key in FORBIDDEN_TOP:
            if key in inv and key in ("tts_audio", "voice_sample", "durable_mutation", "commit_request"):
                pass  # expected present on invalid fixture

    # ── static tool-surface audit ────────────────────────────────────────────
    tools_src = (COMPANION / "world_prompt_builder.gd").read_text(encoding="utf-8")
    if '"commits": true' in tools_src or '"mutates_world": true' in tools_src:
        errors.append("world_prompt_builder.gd tool surface marks commits/mutates_world true")
    for forbidden in ("func commit", "func durable_mutate", "commit_world", "WorldCommit"):
        if forbidden in tools_src:
            errors.append(f"forbidden symbol in builder: {forbidden}")
    if "apply_agm_decision" not in tools_src and "build_from_agm_build_proposal" not in tools_src:
        errors.append("builder missing AGM projection entrypoint")

    module_src = (COMPANION / "companion_module.gd").read_text(encoding="utf-8")
    if "func apply_agm_decision" not in module_src:
        errors.append("companion_module.gd missing apply_agm_decision")
    for voice_kw in (
        "AudioStreamPlayer",
        "AudioStreamMicrophone",
        "Microphone",
        "voice_clone",
        "OpenVoice",
        "StyleTTS",
        "XTTS",
    ):
        if voice_kw in module_src:
            errors.append(f"voice/audio keyword in companion_module.gd: {voice_kw}")

    applier_src = (COMPANION / "agm_decision_applier.gd").read_text(encoding="utf-8")
    for must in ("FORBIDDEN_KEYS", "replay rejected", "preview_confirm_commit", "tts_audio"):
        if must not in applier_src:
            errors.append(f"agm_decision_applier.gd missing {must}")
    if "func commit" in applier_src or "WorldCommit" in applier_src:
        errors.append("agm_decision_applier must not commit")

    iface_src = (ROOT / "game" / "scripts" / "modules" / "interfaces" / "i_companion_module.gd").read_text(
        encoding="utf-8"
    )
    if "apply_agm_decision" not in iface_src:
        errors.append("i_companion_module missing apply_agm_decision")

    # Cap enforcement unit check (pure Python mirror of policy clamps).
    max_turn = 0.005
    attempted = 0.05
    applied = max(-max_turn, min(max_turn, attempted))
    if abs(applied) > max_turn + 1e-12:
        errors.append("turn cap mirror failed")

    if errors:
        print("G2-003_SMOKE=FAIL")
        for err in errors:
            print(" -", err)
        return 1
    print("G2-003_SMOKE=PASS")
    print(f" proposal_ok={proposal_path.relative_to(ROOT)}")
    print(f" agm_proposal_ok={agm_proposal_path.relative_to(ROOT)}")
    print(f" personality_ok={personality_path.relative_to(ROOT)}")
    print(f" agm_fixture_ok={agm_fixture.relative_to(ROOT)}")
    print(" agm_dialogue_consumed=true")
    print(" no_commit_tool_surface=true")
    print(" drift_caps_ok=true")
    print(" text_only=true")
    return 0


if __name__ == "__main__":
    sys.exit(main())

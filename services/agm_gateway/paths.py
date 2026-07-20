"""Repo-relative path resolution for schemas and fixtures."""

from __future__ import annotations

from pathlib import Path

# services/agm_gateway/paths.py -> parents[2] == repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

SNAPSHOT_SCHEMA = REPO_ROOT / "contracts" / "agm" / "world_state_snapshot.schema.json"
DECISION_SCHEMA = REPO_ROOT / "contracts" / "agm" / "decision_envelope.schema.json"

FIXTURES_AGM = REPO_ROOT / "contracts" / "fixtures" / "agm"
VALID_SNAPSHOT_API_PAID = FIXTURES_AGM / "valid" / "valid_snapshot_api_paid.json"
VALID_DECISION_API_PAID = FIXTURES_AGM / "valid" / "valid_decision_api_paid.json"
VALID_SNAPSHOT_DESKTOP = FIXTURES_AGM / "valid" / "valid_snapshot_desktop_bridge.json"
VALID_DECISION_DESKTOP = FIXTURES_AGM / "valid" / "valid_decision_desktop_bridge.json"
EDITION_IDENTITY_PAIR = FIXTURES_AGM / "policy" / "edition_identity_pair.json"
INVALID_SNAPSHOT_API_KEY = FIXTURES_AGM / "invalid" / "invalid_snapshot_with_api_key.json"
INVALID_SNAPSHOT_MISSING = FIXTURES_AGM / "invalid" / "invalid_snapshot_missing_required.json"
INVALID_DECISION_BUILD_BYPASS = (
    FIXTURES_AGM / "invalid" / "invalid_decision_build_bypasses_preview.json"
)
INVALID_DECISION_DURABLE = (
    FIXTURES_AGM / "invalid" / "invalid_decision_direct_durable_mutation.json"
)

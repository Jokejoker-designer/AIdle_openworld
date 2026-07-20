"""Repository path helpers for world_authority_poc."""

from __future__ import annotations

from pathlib import Path

POC_ROOT = Path(__file__).resolve().parent
REPO_ROOT = POC_ROOT.parents[1]
CONTRACTS_ROOT = REPO_ROOT / "contracts"

WORLD_PROMPT_SCHEMA = CONTRACTS_ROOT / "world_prompt.schema.json"
COMMIT_REQUEST_SCHEMA = CONTRACTS_ROOT / "commit" / "commit_request.schema.json"
COMMIT_RECEIPT_SCHEMA = CONTRACTS_ROOT / "commit" / "commit_receipt.schema.json"
EVENT_ENVELOPE_SCHEMA = CONTRACTS_ROOT / "events" / "event_envelope.schema.json"

"""Deep deny-list redaction for AGM gateway payloads.

Root-level JSON Schema propertyNames is not enough: nested smuggling must be
stripped before any provider interface call. Never log raw deny-list values.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

# Align with contracts/agm/*.schema.json propertyNames + A0 INV-REDACTION-DENYLIST
SNAPSHOT_DENY_KEYS: frozenset[str] = frozenset(
    {
        "api_key",
        "access_token",
        "password",
        "secret",
        "secrets",
        "credentials",
        "cookie",
        "cookies",
        "session_cookie",
        "auth_token",
        "raw_system_prompt",
        "system_prompt",
        "private_memory",
        "raw_prompt",
        "tts_audio",
        "voice_sample",
        "microphone_buffer",
        "provider_credentials",
    }
)

DECISION_EXTRA_DENY_KEYS: frozenset[str] = frozenset(
    {
        "script",
        "scripts",
        "code",
        "shader",
        "executable",
        "commit_request",
        "durable_mutation",
        "scene_tree_mutation",
        "direct_world_write",
    }
)

DECISION_DENY_KEYS: frozenset[str] = SNAPSHOT_DENY_KEYS | DECISION_EXTRA_DENY_KEYS

# Header-like wrapper fields (case-insensitive match on key name)
HEADER_DENY_KEYS_LOWER: frozenset[str] = frozenset(
    {
        "authorization",
        "x-api-key",
        "x_api_key",
        "cookie",
        "set-cookie",
        "bearer",
        "proxy-authorization",
    }
)


def _is_denied_key(key: str, deny_keys: frozenset[str]) -> bool:
    if key in deny_keys:
        return True
    if key.lower() in HEADER_DENY_KEYS_LOWER:
        return True
    return False


def redact_payload(
    obj: Any,
    *,
    deny_keys: frozenset[str] | None = None,
) -> tuple[Any, list[str]]:
    """Deep-strip deny-list keys from obj.

    Returns (redacted_copy, stripped_field_names) where stripped_field_names
    lists field names only (never values).
    """
    keys = deny_keys if deny_keys is not None else SNAPSHOT_DENY_KEYS
    stripped: list[str] = []
    redacted = _walk(deepcopy(obj), keys, stripped)
    return redacted, stripped


def _walk(node: Any, deny_keys: frozenset[str], stripped: list[str]) -> Any:
    if isinstance(node, dict):
        out: dict[str, Any] = {}
        for key, value in node.items():
            if not isinstance(key, str):
                # Non-string keys are not schema-legal; keep structure but walk value
                out[key] = _walk(value, deny_keys, stripped)
                continue
            if _is_denied_key(key, deny_keys):
                stripped.append(key)
                continue
            out[key] = _walk(value, deny_keys, stripped)
        return out
    if isinstance(node, list):
        return [_walk(item, deny_keys, stripped) for item in node]
    return node


def contains_deny_keys(obj: Any, deny_keys: frozenset[str] | None = None) -> list[str]:
    """Return deny-list key names found at any depth (names only)."""
    keys = deny_keys if deny_keys is not None else SNAPSHOT_DENY_KEYS
    found: list[str] = []

    def scan(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(key, str) and _is_denied_key(key, keys):
                    found.append(key)
                scan(value)
        elif isinstance(node, list):
            for item in node:
                scan(item)

    scan(obj)
    return found

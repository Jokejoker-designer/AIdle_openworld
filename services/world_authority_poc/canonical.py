"""aidle_canonical_json_v1 + entity / entity_set SHA-256 hashing (G4 parity)."""

from __future__ import annotations

import hashlib
import math
from typing import Any

SCHEMA_NAME = "aidle_canonical_json_v1"
FLOAT_FRAC_DIGITS = 6

# Durable entity fields for hash material (matches entity_hasher.gd ENTITY_FIELD_KEYS).
ENTITY_FIELD_KEYS = (
    "entity_id",
    "kind",
    "recipe_id",
    "transform",
    "bounds",
    "interaction_tags",
    "space_id",
    "chunk_id",
    "status",
    "origin_request_id",
    "origin_prompt_id",
)


def escape_string(s: str) -> str:
    out: list[str] = []
    for ch in s:
        code = ord(ch)
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\b":
            out.append("\\b")
        elif ch == "\f":
            out.append("\\f")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif code < 0x20:
            out.append(f"\\u{code:04x}")
        else:
            out.append(ch)
    return "".join(out)


def format_float(f: float) -> str:
    if math.isnan(f) or math.isinf(f):
        return "null"
    if f == 0.0:
        return "0"
    negative = f < 0.0
    abs_f = abs(f)
    scale = 10**FLOAT_FRAC_DIGITS
    scaled = round(abs_f * scale)
    whole = int(scaled // scale)
    frac_i = int(scaled % scale)
    if frac_i == 0:
        out = str(whole)
    else:
        frac_s = str(frac_i).zfill(FLOAT_FRAC_DIGITS).rstrip("0")
        out = f"{whole}.{frac_s}"
    return f"-{out}" if negative else out


def num_field(v: Any) -> int | float:
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        if math.isclose(v, round(v), rel_tol=0.0, abs_tol=1e-9) and abs(v) < 1e15:
            return int(round(v))
        return v
    if isinstance(v, str):
        try:
            if "." not in v and "e" not in v.lower():
                return int(v)
            return float(v)
        except ValueError:
            return 0
    return 0


def sorted_unique_strings(items: list[Any]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        s = str(item)
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
    out.sort()
    return out


def stringify(value: Any) -> str:
    """Compact canonical JSON string (aidle_canonical_json_v1 rules)."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return format_float(value)
    if isinstance(value, str):
        return f'"{escape_string(value)}"'
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(stringify(x) for x in value) + "]"
    if isinstance(value, dict):
        keys = sorted(value.keys(), key=lambda k: str(k))
        parts = [f'"{escape_string(str(k))}":{stringify(value[k])}' for k in keys]
        return "{" + ",".join(parts) + "}"
    # Fail closed for non-JSON types.
    return "null"


def sha256_hex(utf8_text: str) -> str:
    return hashlib.sha256(utf8_text.encode("utf-8")).hexdigest()


def canonicalize_entity(entity: dict[str, Any]) -> dict[str, Any]:
    """Normalize entity to hash material: known fields only."""
    out: dict[str, Any] = {}
    if "entity_id" in entity:
        out["entity_id"] = str(entity["entity_id"])
    if "kind" in entity:
        out["kind"] = str(entity["kind"])
    if "recipe_id" in entity:
        out["recipe_id"] = str(entity["recipe_id"])
    if isinstance(entity.get("transform"), dict):
        tr = entity["transform"]
        out["transform"] = {
            "x": num_field(tr.get("x", 0)),
            "y": num_field(tr.get("y", 0)),
            "elevation": num_field(tr.get("elevation", 0)),
            "rotation_deg": num_field(tr.get("rotation_deg", 0)),
        }
    if isinstance(entity.get("bounds"), dict):
        b = entity["bounds"]
        out["bounds"] = {
            "width": num_field(b.get("width", 0)),
            "depth": num_field(b.get("depth", 0)),
            "height": num_field(b.get("height", 0)),
        }
    if "interaction_tags" in entity:
        raw = entity["interaction_tags"]
        tags: list[Any] = list(raw) if isinstance(raw, (list, tuple)) else []
        out["interaction_tags"] = sorted_unique_strings(tags)
    if "space_id" in entity:
        out["space_id"] = str(entity["space_id"])
    if entity.get("chunk_id") not in (None, ""):
        out["chunk_id"] = str(entity["chunk_id"])
    out["status"] = str(entity.get("status", "active"))
    if "origin_request_id" in entity:
        out["origin_request_id"] = str(entity["origin_request_id"])
    if "origin_prompt_id" in entity:
        out["origin_prompt_id"] = str(entity["origin_prompt_id"])
    return out


def entity_hash(entity: dict[str, Any]) -> str:
    return sha256_hex(stringify(canonicalize_entity(entity)))


def active_entity_array(entities_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    ids = sorted(entities_by_id.keys())
    arr: list[dict[str, Any]] = []
    for eid in ids:
        ent = entities_by_id[eid]
        if not isinstance(ent, dict):
            continue
        if str(ent.get("status", "active")) == "tombstoned":
            continue
        arr.append(canonicalize_entity(ent))
    return arr


def entity_set_hash(entities_by_id: dict[str, dict[str, Any]]) -> str:
    return sha256_hex(stringify(active_entity_array(entities_by_id)))


def compute_fingerprint(material: dict[str, Any]) -> str:
    """SHA-256 hex of aidle_canonical_json_v1 material (idempotency bind)."""
    payload = {"v": "aidle_world_authority_fp_v1", **material}
    return sha256_hex(stringify(payload))

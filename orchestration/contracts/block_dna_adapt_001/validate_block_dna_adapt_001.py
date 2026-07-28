#!/usr/bin/env python3
"""Deterministic Block-DNA Adapt 001 strict contract gate
(WO-BLOCK-DNA-ADAPT-001 / B1 + CORRECTION-001 / C0).

Validates:
  1) build_recipe.schema.json and build_graph.schema.json (Draft 2020-12)
  2) semantic gates: catalog-bound polarity, pair-bound normalization,
     occupancy, snap, cycle, seeds, allowlists, material co-require +
     bidirectional P1E mapping, adapter authority, required payload_fingerprint,
     idempotency replay ledger, stale revision, code-shaped params
  3) fixtures/valid/** must PASS
  4) fixtures/invalid/** must FAIL (fail-closed)
  5) source_baseline.lock.json key files + BOTH DNA tree aggregates (read-only)

Exit codes:
  0  — all valid pass and all invalid reject as expected
  1  — any mismatch, unexpected pass, missing artifact, or IO error

No DNA/game/world_prompt mutation. No network. stdlib + already-present jsonschema.
Prefer: PYTHONDONTWRITEBYTECODE=1 python -B validate_block_dna_adapt_001.py
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
RECIPE_SCHEMA_PATH = ROOT / "build_recipe.schema.json"
GRAPH_SCHEMA_PATH = ROOT / "build_graph.schema.json"
SOCKET_PATH = ROOT / "socket_catalog.contract.json"
MATERIAL_PATH = ROOT / "material_slot_mapping.contract.json"
ADAPTER_PATH = ROOT / "world_prompt_adapter.contract.json"
ALLOWLIST_PATH = ROOT / "catalog_allowlists.json"
BASELINE_PATH = ROOT / "source_baseline.lock.json"
VALID_DIR = ROOT / "fixtures" / "valid"
INVALID_DIR = ROOT / "fixtures" / "invalid"

GRID_SNAP_M = 0.5
ELEV_SNAP_M = 0.25
ROT_SNAP_DEG = 15.0
SCALE_DELTA_MAX = 0.25

FINGERPRINT_RE = re.compile(r"^[a-f0-9]{64}$")

ASYMMETRIC_SOURCE_PAIRS: frozenset[frozenset[str]] = frozenset(
    {
        frozenset({"terrain_surface", "prop_base"}),
        frozenset({"building_foundation", "vertical_stack"}),
        frozenset({"wall_edge", "window_opening"}),
        frozenset({"wall_edge", "door_opening"}),
    }
)

FORBIDDEN_AUTHORITY_FIELDS: frozenset[str] = frozenset(
    {
        "direct_commit",
        "world_commit",
        "commit",
        "authority_token",
        "execute_code",
        "ownership_mutation",
        "economy_mutation",
        "inventory_mutation",
        "canonical_mutation",
        "confirmed_by",
        "mutate_ownership",
        "mutate_economy",
        "mutate_inventory",
        "execute_arbitrary_code",
    }
)

CODE_SHAPED_PARAM_KEYS: frozenset[str] = frozenset(
    {
        "script",
        "scripts",
        "command",
        "commands",
        "execute",
        "exec",
        "eval",
        "path",
        "path_to_executable",
        "executable",
        "tool_authority",
        "tool-authority",
        "shell",
        "code",
        "payload_code",
        "arbitrary_code",
    }
)

ALLOWED_PARAM_KEYS: frozenset[str] = frozenset(
    {
        "tint",
        "variant",
        "lod",
        "label",
        "note",
        "count",
        "enabled",
        "width",
        "height",
        "depth",
        "style_hint",
    }
)

INVALID_CASE_EXPECTATIONS: dict[str, list[str]] = {
    "INV-01-nodes-int-null": ["nodes", "type", "schema", "null", "42"],
    "INV-02-malformed-unknown-edge": ["edge", "unknown", "dangling", "from_node"],
    "INV-03-empty-bounds": ["bounds", "empty", "inverted"],
    "INV-04-inverted-bounds": ["bounds", "inverted"],
    "INV-05-negative-revision": ["revision", "minimum", "negative"],
    "INV-06-bool-numeric": ["bool", "boolean", "number", "type"],
    "INV-07-nan-numeric": ["nan", "finite", "number"],
    "INV-08-infinity-numeric": ["infinity", "finite", "number"],
    "INV-09-duplicate-node-ids": ["duplicate", "node_id"],
    "INV-10-duplicate-edge-ids": ["duplicate", "edge_id"],
    "INV-11-dangling-ref": ["dangling", "reference", "to_node"],
    "INV-12-same-polarity-socket": ["polarity", "same_polarity"],
    "INV-13-one-way-compatibility": ["compatibility", "one_way", "asymmetric", "mutual"],
    "INV-14-asymmetric-source-no-norm": [
        "asymmetric",
        "source_audit",
        "normalization",
        "terrain_surface",
        "prop_base",
    ],
    "INV-15-double-occupancy": ["occupancy", "double"],
    "INV-16-bounds-escape": ["bounds", "escape"],
    "INV-17-off-grid-transform": ["snap", "off_grid", "grid"],
    "INV-18-invalid-elevation": ["elevation", "snap"],
    "INV-19-off-snap-rotation": ["rotation", "snap"],
    "INV-20-forbidden-cycle": ["cycle", "forbidden"],
    "INV-21-missing-seed": ["seed", "required", "generator"],
    "INV-22-unknown-generator": ["generator", "unknown", "allowlist"],
    "INV-23-unknown-behavior": ["behavior", "unknown", "allowlist"],
    "INV-24-unknown-world-rule": ["world_rule", "rule", "unknown", "allowlist"],
    "INV-25-unknown-module": ["module", "unknown", "allowlist"],
    "INV-26-material-slot-mismatch": ["material", "slot", "mismatch"],
    "INV-27-direct-commit-authority": ["direct_commit", "authority", "forbidden"],
    "INV-28-stale-revision": ["stale", "revision"],
    "INV-29-idempotency-conflict": ["idempotency", "conflict", "fingerprint"],
    "INV-30-additional-properties": ["additionalProperties", "unknown", "not allowed"],
    # C0 correction fixtures
    "INV-31-missing-payload-fingerprint": ["payload_fingerprint", "required"],
    "INV-32-malformed-payload-fingerprint": ["payload_fingerprint", "pattern", "fingerprint"],
    "INV-33-wrong-payload-fingerprint": ["fingerprint", "mismatch", "idempotency"],
    "INV-34-idempotency-same-key-changed-payload": [
        "idempotency",
        "conflict",
        "replay",
        "changed",
    ],
    "INV-35-peer-launder-directed-sockets": ["polarity", "launder", "peer", "catalog"],
    "INV-36-catalog-polarity-mismatch": ["polarity", "catalog", "default", "mismatch"],
    "INV-37-wrong-known-normalization-id": [
        "normalization",
        "pair",
        "wrong",
        "adapter_normalization",
    ],
    "INV-38-material-slot-without-p1e": ["material", "co_require", "p1e_material", "required"],
    "INV-39-p1e-without-material-slot": ["material", "co_require", "material_slot", "required"],
    "INV-40-code-shaped-parameter-key": ["parameter", "code_shaped", "script", "execute", "eval"],
    "INV-41-validation-flag-false": ["validation", "const", "collision", "false"],
    "INV-42-reverse-material-mapping": ["material", "bidirectional", "reverse", "mismatch"],
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_aggregate_sha256(root: Path) -> tuple[str, int]:
    """SHA-256 over sorted relative-path UTF-8 + raw bytes; exclude __pycache__/Thumbs.db."""
    h = hashlib.sha256()
    count = 0
    files: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if "__pycache__" in p.parts or p.name == "Thumbs.db":
            continue
        files.append(p)
    for p in sorted(files, key=lambda x: x.relative_to(root).as_posix()):
        rel = p.relative_to(root).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(p.read_bytes())
        count += 1
    return h.hexdigest(), count


def load_json(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text, parse_constant=_reject_json_constant)


def _reject_json_constant(name: str) -> None:
    raise ValueError(f"non_finite_json_constant:{name}")


def canonical_payload_projection(doc: dict[str, Any]) -> Any:
    """Canonical JSON projection: exclude ONLY payload_fingerprint. No helper mutation."""
    return {k: v for k, v in doc.items() if k != "payload_fingerprint"}


def canonical_fingerprint(doc: dict[str, Any]) -> str:
    body = canonical_payload_projection(doc)
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def is_bool(v: Any) -> bool:
    return isinstance(v, bool)


def is_finite_number(v: Any) -> bool:
    if is_bool(v):
        return False
    if isinstance(v, (int, float)):
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return False
        return True
    return False


_NUMERIC_FIELD_NAMES: frozenset[str] = frozenset(
    {
        "x",
        "y",
        "z",
        "elevation",
        "rotation_deg",
        "scale",
        "seed",
        "expected_world_revision",
        "current_world_revision",
        "presentation_duration_seconds",
        "bounds_width",
        "bounds_depth",
        "cx",
        "cy",
        "cz",
    }
)


def walk_numeric_candidates(
    obj: Any, path: str = "$", parent_key: str | None = None
) -> list[tuple[str, Any]]:
    found: list[tuple[str, Any]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            found.extend(walk_numeric_candidates(v, f"{path}.{k}", parent_key=k))
    elif isinstance(obj, list):
        if parent_key in {"position", "rotation_deg", "scale", "size_m", "center"}:
            for i, v in enumerate(obj):
                found.append((f"{path}[{i}]", v))
        else:
            for i, v in enumerate(obj):
                found.extend(
                    walk_numeric_candidates(v, f"{path}[{i}]", parent_key=parent_key)
                )
    else:
        if parent_key in _NUMERIC_FIELD_NAMES:
            found.append((path, obj))
    return found


def nearly_multiple(value: float, step: float, eps: float = 1e-9) -> bool:
    if step <= 0:
        return False
    q = value / step
    return abs(q - round(q)) <= eps


def polarity_ok(from_p: str, to_p: str) -> bool:
    if from_p == "output" and to_p == "input":
        return True
    if from_p == "peer" and to_p == "peer":
        return True
    return False


def find_cycle(adj: dict[str, list[str]]) -> bool:
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {n: WHITE for n in adj}

    def dfs(u: str) -> bool:
        color[u] = GRAY
        for v in adj[u]:
            if v not in color:
                color[v] = WHITE
            if color[v] == GRAY:
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    for n in list(adj.keys()):
        if color.get(n, WHITE) == WHITE and dfs(n):
            return True
    return False


def deep_contains_forbidden(obj: Any, path: str = "$") -> list[str]:
    errs: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN_AUTHORITY_FIELDS:
                errs.append(f"forbidden_authority_field:{path}.{k}")
            errs.extend(deep_contains_forbidden(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            errs.extend(deep_contains_forbidden(v, f"{path}[{i}]"))
    return errs


class Catalog:
    def __init__(self) -> None:
        self.sockets = load_json(SOCKET_PATH)
        self.materials = load_json(MATERIAL_PATH)
        self.adapter = load_json(ADAPTER_PATH)
        self.allow = load_json(ALLOWLIST_PATH)
        self.baseline = load_json(BASELINE_PATH)
        self.socket_by_type: dict[str, dict[str, Any]] = {
            s["socket_type"]: s for s in self.sockets["socket_types"]
        }
        self.norm_by_id: dict[str, dict[str, Any]] = {
            n["normalization_id"]: n for n in self.sockets["adapter_normalizations"]
        }
        self.mutual: dict[str, set[str]] = {}
        for s in self.sockets["socket_types"]:
            st = s["socket_type"]
            self.mutual[st] = set(s["compatible_with"])
        for n in self.sockets["adapter_normalizations"]:
            a, b = n["pair"]
            self.mutual.setdefault(a, set()).add(b)
            self.mutual.setdefault(b, set()).add(a)

        self.module_ids = set(self.allow["module_ids"])
        self.generator_ids = set(self.allow["generator_ids"])
        self.behavior_ids = set(self.allow["behavior_ids"])
        self.world_rule_ids = set(self.allow["world_rule_ids"])
        self.slot_map: dict[str, str] = dict(self.materials["slot_to_material"])
        # Bidirectional: material → slot (unique materials required)
        self.material_to_slot: dict[str, str] = {
            mat: slot for slot, mat in self.slot_map.items()
        }
        self.live_mats = set(self.materials["live_p1e_material_ids"])
        self.seed_min = int(self.allow["seed_bounds"]["min"])
        self.seed_max = int(self.allow["seed_bounds"]["max"])

    def mutual_ok(self, a: str, b: str) -> bool:
        return b in self.mutual.get(a, set()) and a in self.mutual.get(b, set())

    def default_polarity(self, socket: str) -> str | None:
        s = self.socket_by_type.get(socket)
        return s.get("default_polarity") if s else None


class ReplayLedger:
    """Bounded in-memory idempotency ledger for the fixture harness."""

    def __init__(self, max_entries: int = 512) -> None:
        self.max_entries = max_entries
        self._key_to_fp: dict[str, str] = {}
        self.stable_replays = 0
        self.conflicts = 0

    def observe(self, key: str, fingerprint: str) -> list[str]:
        errs: list[str] = []
        if key in self._key_to_fp:
            if self._key_to_fp[key] == fingerprint:
                self.stable_replays += 1
            else:
                self.conflicts += 1
                errs.append(
                    f"idempotency_replay_conflict:same_key_changed_payload:{key}"
                )
        else:
            if len(self._key_to_fp) >= self.max_entries:
                # drop oldest insertion order (py3.7+ preserves order)
                oldest = next(iter(self._key_to_fp))
                del self._key_to_fp[oldest]
            self._key_to_fp[key] = fingerprint
        return errs


def check_fingerprint_and_ledger(
    doc: dict[str, Any], ledger: ReplayLedger | None
) -> list[str]:
    errs: list[str] = []
    fp = doc.get("payload_fingerprint")
    if fp is None:
        errs.append("missing_payload_fingerprint")
        return errs
    if not isinstance(fp, str) or not FINGERPRINT_RE.fullmatch(fp):
        errs.append("malformed_payload_fingerprint")
        return errs
    expected = canonical_fingerprint(doc)
    if fp != expected:
        errs.append(f"payload_fingerprint_mismatch:declared!={expected[:16]}")
    key = doc.get("idempotency_key")
    if not isinstance(key, str) or not key:
        errs.append("missing_idempotency_key")
    elif ledger is not None and not errs:
        # Only ledger when fingerprint is correct — wrong fingerprint already rejected
        errs.extend(ledger.observe(key, fp))
    elif ledger is not None and fp == expected and isinstance(key, str):
        errs.extend(ledger.observe(key, fp))
    return errs


def validate_edge_polarity_and_norm(
    e: dict[str, Any], cat: Catalog, edge_label: str
) -> list[str]:
    errs: list[str] = []
    fs, ts = e.get("from_socket"), e.get("to_socket")
    fp, tp = e.get("from_polarity"), e.get("to_polarity")
    norm_id = e.get("adapter_normalization_id")

    if not isinstance(fs, str) or fs not in cat.socket_by_type:
        errs.append(f"unknown_socket:{fs}")
        return errs
    if not isinstance(ts, str) or ts not in cat.socket_by_type:
        errs.append(f"unknown_socket:{ts}")
        return errs

    pair = frozenset({fs, ts})

    if norm_id is not None:
        if norm_id not in cat.norm_by_id:
            errs.append(f"unknown_normalization_id:{norm_id}")
            return errs
        nrec = cat.norm_by_id[norm_id]
        n_pair = frozenset(nrec["pair"])
        if pair != n_pair:
            errs.append(
                f"adapter_normalization_pair_mismatch:{norm_id}:{fs}/{ts}"
                f"!=expected_{'/'.join(sorted(n_pair))}"
            )
        # Must match an allowed orientation exactly
        orientations = nrec.get("allowed_orientations") or []
        matched = False
        for ori in orientations:
            if (
                ori.get("from_socket") == fs
                and ori.get("to_socket") == ts
                and ori.get("from_polarity") == fp
                and ori.get("to_polarity") == tp
            ):
                matched = True
                break
        if not matched:
            errs.append(
                f"normalization_orientation_or_polarity_mismatch:{edge_label}:{norm_id}"
            )
        # Effective polarities must still satisfy directed/peer policy
        if not polarity_ok(str(fp), str(tp)):
            errs.append(f"same_polarity_or_invalid_polarity:{edge_label}:{fp}->{tp}")
    else:
        # Non-normalized: polarities must match catalog defaults
        d_from = cat.default_polarity(fs)
        d_to = cat.default_polarity(ts)
        if fp != d_from or tp != d_to:
            errs.append(
                f"catalog_polarity_mismatch:{edge_label}:declared {fp}/{tp} "
                f"!= catalog {d_from}/{d_to}"
            )
        # Peer laundering detection: declaring peer when catalog default is directed
        if (d_from in ("input", "output") and fp == "peer") or (
            d_to in ("input", "output") and tp == "peer"
        ):
            errs.append(f"peer_launder_directed_sockets:{edge_label}:{fs}/{ts}")
        if not polarity_ok(str(fp), str(tp)):
            errs.append(f"same_polarity_or_invalid_polarity:{edge_label}:{fp}->{tp}")
        if pair in ASYMMETRIC_SOURCE_PAIRS:
            errs.append(f"asymmetric_source_without_normalization:{fs}/{ts}")

    if not cat.mutual_ok(fs, ts):
        errs.append(f"one_way_or_incompatible_sockets:{fs}/{ts}")

    return errs


def semantic_validate_graph(
    doc: dict[str, Any], cat: Catalog, ledger: ReplayLedger | None
) -> list[str]:
    errs: list[str] = []
    errs.extend(deep_contains_forbidden(doc))
    errs.extend(check_fingerprint_and_ledger(doc, ledger))

    for path, val in walk_numeric_candidates(doc):
        if is_bool(val):
            errs.append(f"bool_as_number:{path}")
        elif isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            errs.append(f"non_finite_number:{path}")
        elif not isinstance(val, (int, float)):
            errs.append(f"non_numeric_in_numeric_field:{path}")

    bounds = doc.get("bounds") or {}
    bmin = bounds.get("min") or {}
    bmax = bounds.get("max") or {}
    if not bounds:
        errs.append("bounds_empty")
    else:
        for axis in ("x", "y", "z"):
            if axis not in bmin or axis not in bmax:
                errs.append(f"bounds_missing_axis:{axis}")
                continue
            lo, hi = bmin[axis], bmax[axis]
            if not is_finite_number(lo) or not is_finite_number(hi):
                errs.append(f"bounds_non_finite:{axis}")
            elif not (hi > lo):
                errs.append(f"bounds_inverted_or_empty:{axis}")

    rev = doc.get("expected_world_revision")
    if is_bool(rev) or not isinstance(rev, int) or rev < 0:
        errs.append("negative_or_invalid_revision")
    cur = doc.get("current_world_revision")
    if cur is not None:
        if is_bool(cur) or not isinstance(cur, int) or cur < 0:
            errs.append("invalid_current_revision")
        elif isinstance(rev, int) and not is_bool(rev) and rev < cur:
            errs.append("stale_revision")

    # Validation policy switches must be true (schema const; semantic belt)
    val_pol = doc.get("validation") or {}
    for k in ("collision", "occupancy", "sockets", "cycle", "snap"):
        if val_pol.get(k) is not True:
            errs.append(f"validation_policy_must_be_true:{k}")

    nodes = doc.get("nodes")
    if not isinstance(nodes, list):
        errs.append("nodes_not_array")
        return errs

    node_by_id: dict[str, dict[str, Any]] = {}
    occ: dict[tuple[int, int, int], str] = {}
    for n in nodes:
        if not isinstance(n, dict):
            errs.append("node_not_object")
            continue
        nid = n.get("node_id")
        if not isinstance(nid, str):
            errs.append("node_id_invalid")
            continue
        if nid in node_by_id:
            errs.append(f"duplicate_node_id:{nid}")
        node_by_id[nid] = n

        mid = n.get("module_id")
        if mid not in cat.module_ids:
            errs.append(f"unknown_module:{mid}")

        tr = n.get("transform") or {}
        for key in ("x", "y", "elevation", "rotation_deg", "scale"):
            v = tr.get(key)
            if is_bool(v):
                errs.append(f"bool_as_number:transform.{key}")
            elif not is_finite_number(v):
                errs.append(f"non_finite_number:transform.{key}")

        x, y, elev = tr.get("x"), tr.get("y"), tr.get("elevation")
        rot, scale = tr.get("rotation_deg"), tr.get("scale")
        if is_finite_number(x) and is_finite_number(y):
            if not nearly_multiple(float(x), GRID_SNAP_M) or not nearly_multiple(
                float(y), GRID_SNAP_M
            ):
                errs.append(f"off_grid_transform:{nid}")
        if is_finite_number(elev) and not nearly_multiple(float(elev), ELEV_SNAP_M):
            errs.append(f"invalid_elevation_snap:{nid}")
        if is_finite_number(rot) and not nearly_multiple(float(rot), ROT_SNAP_DEG):
            errs.append(f"off_snap_rotation:{nid}")
        if is_finite_number(scale) and abs(float(scale) - 1.0) > SCALE_DELTA_MAX + 1e-9:
            errs.append(f"scale_delta_exceeded:{nid}")

        if (
            is_finite_number(x)
            and is_finite_number(y)
            and is_finite_number(elev)
            and "x" in bmin
            and "x" in bmax
        ):
            if not (
                float(bmin["x"]) <= float(x) <= float(bmax["x"])
                and float(bmin["y"]) <= float(y) <= float(bmax["y"])
                and float(bmin["z"]) <= float(elev) <= float(bmax["z"])
            ):
                errs.append(f"bounds_escape:{nid}")

        cell = n.get("occupancy_cell") or {}
        try:
            key = (int(cell["cx"]), int(cell["cy"]), int(cell["cz"]))
            if key in occ:
                errs.append(f"double_occupancy:{nid}:{occ[key]}")
            else:
                occ[key] = nid
        except Exception:
            errs.append(f"occupancy_cell_invalid:{nid}")

        slot = n.get("material_slot")
        mat = n.get("p1e_material_id")
        if slot is None and mat is None:
            errs.append(f"material_co_require_missing:{nid}")
        elif slot is None:
            errs.append(f"material_slot_required_with_p1e:{nid}")
        elif mat is None:
            errs.append(f"p1e_material_required_with_slot:{nid}")
        else:
            if slot not in cat.slot_map:
                errs.append(f"unknown_material_slot:{slot}")
            else:
                expected = cat.slot_map[slot]
                if mat != expected:
                    errs.append(f"material_slot_mismatch:{slot}:{mat}!={expected}")
                rev_slot = cat.material_to_slot.get(mat)
                if rev_slot is not None and rev_slot != slot:
                    errs.append(
                        f"bidirectional_material_reverse_mismatch:{mat}->{rev_slot}!={slot}"
                    )
                if mat not in cat.live_mats:
                    errs.append(f"unknown_p1e_material:{mat}")

    edges = doc.get("edges") or []
    edge_ids: set[str] = set()
    adj: dict[str, list[str]] = defaultdict(list)
    for e in edges:
        if not isinstance(e, dict):
            errs.append("edge_not_object")
            continue
        eid = e.get("edge_id")
        if not isinstance(eid, str):
            errs.append("edge_id_invalid")
            continue
        if eid in edge_ids:
            errs.append(f"duplicate_edge_id:{eid}")
        edge_ids.add(eid)

        fn, tn = e.get("from_node"), e.get("to_node")
        if fn not in node_by_id:
            errs.append(f"dangling_from_node:{fn}")
        if tn not in node_by_id:
            errs.append(f"dangling_to_node:{tn}")

        errs.extend(validate_edge_polarity_and_norm(e, cat, str(eid)))

        if isinstance(fn, str) and isinstance(tn, str):
            if fn == tn:
                errs.append(f"self_loop_forbidden:{eid}")
            adj[fn].append(tn)
            adj.setdefault(tn, [])

    if find_cycle(adj):
        errs.append("forbidden_cycle")

    for g in doc.get("generators") or []:
        if not isinstance(g, dict):
            errs.append("generator_not_object")
            continue
        gid = g.get("generator_id")
        if gid not in cat.generator_ids:
            errs.append(f"unknown_generator:{gid}")
        if "seed" not in g:
            errs.append(f"missing_seed:{gid}")
        else:
            seed = g.get("seed")
            if is_bool(seed) or not isinstance(seed, int):
                errs.append(f"non_deterministic_or_invalid_seed:{gid}")
            elif seed < cat.seed_min or seed > cat.seed_max:
                errs.append(f"seed_out_of_bounds:{gid}")

    for r in doc.get("world_rules") or []:
        if not isinstance(r, dict):
            errs.append("world_rule_not_object")
            continue
        rid = r.get("rule_id")
        if rid not in cat.world_rule_ids:
            errs.append(f"unknown_world_rule:{rid}")

    ap = doc.get("adapter_proposal")
    if ap is not None:
        if ap.get("kind") != "structured_world_prompt_proposal":
            errs.append("adapter_kind_invalid")
        if ap.get("confirmation_state") != "pending":
            errs.append("adapter_must_be_pending")
        if ap.get("preview_required") is not True:
            errs.append("adapter_preview_required")

    return errs


def semantic_validate_recipe(
    doc: dict[str, Any], cat: Catalog, ledger: ReplayLedger | None
) -> list[str]:
    errs: list[str] = []
    errs.extend(deep_contains_forbidden(doc))
    errs.extend(check_fingerprint_and_ledger(doc, ledger))

    for path, val in walk_numeric_candidates(doc):
        if is_bool(val):
            errs.append(f"bool_as_number:{path}")
        elif isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            errs.append(f"non_finite_number:{path}")

    if doc.get("root_module_id") not in cat.module_ids:
        errs.append(f"unknown_module:{doc.get('root_module_id')}")

    val_pol = doc.get("validation") or {}
    for k in ("check_sockets", "check_materials", "check_occupancy"):
        if val_pol.get(k) is not True:
            errs.append(f"validation_policy_must_be_true:{k}")

    inst_by_id: dict[str, dict[str, Any]] = {}
    for inst in doc.get("instances") or []:
        if not isinstance(inst, dict):
            errs.append("instance_not_object")
            continue
        iid = inst.get("instance_id")
        if not isinstance(iid, str):
            errs.append("instance_id_invalid")
            continue
        if iid in inst_by_id:
            errs.append(f"duplicate_instance_id:{iid}")
        inst_by_id[iid] = inst
        mid = inst.get("module_id")
        if mid not in cat.module_ids:
            errs.append(f"unknown_module:{mid}")

        params = inst.get("parameters") or {}
        if not isinstance(params, dict):
            errs.append(f"parameters_not_object:{iid}")
        else:
            for pk, pv in params.items():
                if pk in CODE_SHAPED_PARAM_KEYS or any(
                    tok in pk for tok in ("script", "exec", "eval", "command", "authority")
                ):
                    errs.append(f"code_shaped_parameter_key:{pk}")
                if pk not in ALLOWED_PARAM_KEYS:
                    errs.append(f"parameter_key_not_allowlisted:{pk}")
                if not isinstance(pv, (str, int, float, bool, type(None))) or is_bool(pv) and not isinstance(pv, bool):
                    pass  # type check via schema mostly
                if isinstance(pv, float) and (math.isnan(pv) or math.isinf(pv)):
                    errs.append(f"non_finite_parameter:{pk}")

        tr = inst.get("transform") or {}
        for arr_name, step, is_rot in (
            ("position", GRID_SNAP_M, False),
            ("rotation_deg", ROT_SNAP_DEG, True),
            ("scale", None, False),
        ):
            arr = tr.get(arr_name)
            if not isinstance(arr, list) or len(arr) != 3:
                errs.append(f"transform_{arr_name}_invalid:{iid}")
                continue
            for i, v in enumerate(arr):
                if is_bool(v):
                    errs.append(f"bool_as_number:transform.{arr_name}[{i}]")
                elif not is_finite_number(v):
                    errs.append(f"non_finite_number:transform.{arr_name}[{i}]")
                elif step is not None and is_finite_number(v):
                    if not nearly_multiple(float(v), step):
                        if is_rot:
                            errs.append(f"off_snap_rotation:{iid}")
                        else:
                            errs.append(f"off_grid_transform:{iid}")
            if arr_name == "scale":
                for v in arr:
                    if is_finite_number(v) and abs(float(v) - 1.0) > SCALE_DELTA_MAX + 1e-9:
                        errs.append(f"scale_delta_exceeded:{iid}")

    conn_ids: set[str] = set()
    adj: dict[str, list[str]] = defaultdict(list)
    for c in doc.get("connections") or []:
        if not isinstance(c, dict):
            errs.append("connection_not_object")
            continue
        cid = c.get("connection_id")
        if not isinstance(cid, str):
            errs.append("connection_id_invalid")
            continue
        if cid in conn_ids:
            errs.append(f"duplicate_connection_id:{cid}")
        conn_ids.add(cid)
        fi, ti = c.get("from_instance"), c.get("to_instance")
        if fi not in inst_by_id:
            errs.append(f"dangling_from_instance:{fi}")
        if ti not in inst_by_id:
            errs.append(f"dangling_to_instance:{ti}")

        # Map recipe connection shape to edge-like for polarity/norm checks
        edge_like = {
            "from_socket": c.get("from_socket"),
            "to_socket": c.get("to_socket"),
            "from_polarity": c.get("from_polarity"),
            "to_polarity": c.get("to_polarity"),
            "adapter_normalization_id": c.get("adapter_normalization_id"),
        }
        errs.extend(validate_edge_polarity_and_norm(edge_like, cat, str(cid)))

        if isinstance(fi, str) and isinstance(ti, str):
            if fi == ti:
                errs.append(f"self_loop_forbidden:{cid}")
            adj[fi].append(ti)
            adj.setdefault(ti, [])

    if find_cycle(adj):
        errs.append("forbidden_cycle")

    for mo in doc.get("material_overrides") or []:
        if not isinstance(mo, dict):
            errs.append("material_override_not_object")
            continue
        slot = mo.get("slot")
        mat = mo.get("p1e_material_id")
        if slot is None or mat is None:
            errs.append("material_override_co_require_slot_and_p1e")
            continue
        if slot not in cat.slot_map:
            errs.append(f"unknown_material_slot:{slot}")
        else:
            expected = cat.slot_map[slot]
            if mat != expected:
                errs.append(f"material_slot_mismatch:{slot}:{mat}!={expected}")
            rev_slot = cat.material_to_slot.get(mat)
            if rev_slot is not None and rev_slot != slot:
                errs.append(
                    f"bidirectional_material_reverse_mismatch:{mat}->{rev_slot}!={slot}"
                )
            if mat not in cat.live_mats:
                errs.append(f"unknown_p1e_material:{mat}")

    for b in doc.get("behavior_bindings") or []:
        if not isinstance(b, dict):
            errs.append("behavior_not_object")
            continue
        bid = b.get("behavior_id")
        if bid not in cat.behavior_ids:
            errs.append(f"unknown_behavior:{bid}")
        iid = b.get("instance_id")
        if iid not in inst_by_id:
            errs.append(f"dangling_behavior_instance:{iid}")

    outs = doc.get("outputs") or {}
    if outs.get("proposal_only") is not True:
        errs.append("outputs_must_be_proposal_only")

    return errs


def schema_validate(doc: Any, schema: dict[str, Any]) -> list[str]:
    v = Draft202012Validator(schema)
    return [
        f"schema:{e.message}"
        for e in sorted(v.iter_errors(doc), key=lambda e: list(e.path))
    ]


def detect_kind(doc: dict[str, Any]) -> str:
    if "build_graph_id" in doc:
        return "graph"
    if "recipe_id" in doc:
        return "recipe"
    return "unknown"


def validate_document(
    doc: Any,
    cat: Catalog,
    recipe_schema: dict[str, Any],
    graph_schema: dict[str, Any],
    ledger: ReplayLedger | None,
) -> list[str]:
    if not isinstance(doc, dict):
        return ["root_not_object"]
    kind = detect_kind(doc)
    if kind == "graph":
        errs = schema_validate(doc, graph_schema)
        errs.extend(semantic_validate_graph(doc, cat, ledger))
        return errs
    if kind == "recipe":
        errs = schema_validate(doc, recipe_schema)
        errs.extend(semantic_validate_recipe(doc, cat, ledger))
        return errs
    return ["unknown_document_kind"]


def expectation_match(case: str, errs: list[str]) -> bool:
    tags = INVALID_CASE_EXPECTATIONS.get(case)
    if not tags:
        return len(errs) > 0
    blob = " ".join(errs).lower()
    return any(t.lower() in blob for t in tags)


def verify_baseline(cat: Catalog) -> list[str]:
    errs: list[str] = []
    packs = cat.baseline["packages"]
    bmf = cat.baseline["block_module_foundation"]
    checks = [
        (
            REPO / "world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.0/manifest.json",
            packs["v1.0_manifest_json_sha256"],
        ),
        (
            REPO
            / "world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.1_Tier3/manifest.json",
            packs["v1.1_manifest_json_sha256"],
        ),
        (
            REPO
            / "world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.0/foundation_core/AIdle_Block_Module_Foundation_v1.0/schemas/build_recipe.schema.json",
            bmf["source_schemas"]["build_recipe.schema.json"],
        ),
        (
            REPO
            / "world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.0/foundation_core/AIdle_Block_Module_Foundation_v1.0/schemas/build_graph.schema.json",
            bmf["source_schemas"]["build_graph.schema.json"],
        ),
        (
            REPO
            / "world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.0/foundation_core/AIdle_Block_Module_Foundation_v1.0/catalogs/socket_types.json",
            bmf["v1.0_and_v1.1_socket_types_sha256"],
        ),
        (
            REPO / "contracts/world_prompt.schema.json",
            cat.baseline["active_project_refs"]["world_prompt_schema_sha256"],
        ),
    ]
    for path, expected in checks:
        if not path.is_file():
            errs.append(f"baseline_missing:{path}")
            continue
        got = sha256_file(path)
        if got != expected:
            errs.append(f"baseline_mismatch:{path.name}:{got}!={expected}")

    # BOTH immutable DNA package tree aggregates (recomputed live)
    v10 = REPO / "world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.0"
    v11 = REPO / "world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.1_Tier3"
    if v10.is_dir():
        agg, cnt = tree_aggregate_sha256(v10)
        exp = packs["v1.0_package_tree_aggregate_sha256"]
        exp_cnt = packs["v1.0_package_tree_file_count_ex_pycache"]
        if agg != exp:
            errs.append(f"tree_aggregate_mismatch:v1.0:{agg}!={exp}")
        if cnt != exp_cnt:
            errs.append(f"tree_file_count_mismatch:v1.0:{cnt}!={exp_cnt}")
    else:
        errs.append("baseline_missing:v1.0_root")
    if v11.is_dir():
        agg, cnt = tree_aggregate_sha256(v11)
        exp = packs["v1.1_Tier3_package_tree_aggregate_sha256"]
        exp_cnt = packs["v1.1_Tier3_package_tree_file_count_ex_pycache"]
        if agg != exp:
            errs.append(f"tree_aggregate_mismatch:v1.1_Tier3:{agg}!={exp}")
        if cnt != exp_cnt:
            errs.append(f"tree_file_count_mismatch:v1.1_Tier3:{cnt}!={exp_cnt}")
    else:
        errs.append("baseline_missing:v1.1_Tier3_root")
    return errs


def main() -> int:
    print("=== Block-DNA Adapt 001 contract gate (C0 correction) ===")
    print(f"ROOT={ROOT}")

    for p in (
        RECIPE_SCHEMA_PATH,
        GRAPH_SCHEMA_PATH,
        SOCKET_PATH,
        MATERIAL_PATH,
        ADAPTER_PATH,
        ALLOWLIST_PATH,
        BASELINE_PATH,
        VALID_DIR,
        INVALID_DIR,
    ):
        if not p.exists():
            print(f"FAIL missing artifact: {p}")
            return 1

    try:
        recipe_schema = load_json(RECIPE_SCHEMA_PATH)
        graph_schema = load_json(GRAPH_SCHEMA_PATH)
        Draft202012Validator.check_schema(recipe_schema)
        Draft202012Validator.check_schema(graph_schema)
    except (SchemaError, ValueError, json.JSONDecodeError) as e:
        print(f"FAIL schema load/check: {e}")
        return 1

    cat = Catalog()
    base_errs = verify_baseline(cat)
    if base_errs:
        print("FAIL source baseline:")
        for e in base_errs:
            print(f"  - {e}")
        return 1
    print("PASS source baseline key-file + BOTH DNA tree aggregates")

    valid_files = sorted(VALID_DIR.glob("*.json"))
    invalid_files = sorted(INVALID_DIR.glob("*.json"))
    if len(valid_files) < 12:
        print(f"FAIL need ≥12 valid fixtures, found {len(valid_files)}")
        return 1
    if len(invalid_files) < 37:
        print(f"FAIL need ≥37 invalid fixtures, found {len(invalid_files)}")
        return 1

    ledger = ReplayLedger()
    valid_pass = 0
    valid_fail: list[str] = []
    for vf in valid_files:
        try:
            raw = vf.read_text(encoding="utf-8")
            doc = json.loads(raw)
            if isinstance(doc, dict):
                doc.pop("_test_meta", None)
            errs = validate_document(doc, cat, recipe_schema, graph_schema, ledger)
            if errs:
                valid_fail.append(f"{vf.name}: {errs[:10]}")
            else:
                valid_pass += 1
                print(f"  VALID PASS {vf.name}")
        except Exception as e:
            valid_fail.append(f"{vf.name}: exception {e}")

    # Invalid fixtures: no shared ledger (avoids key pollution). Ledger only for
    # explicit seed-then-conflict injects with a fresh per-case ledger.
    invalid_reject = 0
    invalid_fail: list[str] = []
    inv_conflicts = 0
    inv_stable_replays = 0
    for inv in invalid_files:
        case = inv.stem
        try:
            raw = inv.read_text(encoding="utf-8")
            if '"__inject__"' in raw:
                wrapper = json.loads(raw)
                inject = wrapper["__inject__"]
                doc = wrapper["document"]
                if inject == "nan":
                    doc["nodes"][0]["transform"]["x"] = float("nan")
                elif inject == "inf":
                    doc["nodes"][0]["transform"]["x"] = float("inf")
                elif inject == "bool":
                    doc["nodes"][0]["transform"]["x"] = True  # type: ignore[assignment]
                elif inject == "nodes_int_null":
                    doc["nodes"] = [42, None]
                elif inject == "ledger_seed_then_conflict":
                    case_ledger = ReplayLedger()
                    seed = wrapper["seed_document"]
                    seed_errs = validate_document(
                        seed, cat, recipe_schema, graph_schema, case_ledger
                    )
                    if seed_errs:
                        invalid_fail.append(
                            f"{inv.name}: seed not valid for ledger test: {seed_errs[:4]}"
                        )
                        continue
                    errs = validate_document(
                        doc, cat, recipe_schema, graph_schema, case_ledger
                    )
                    inv_conflicts += case_ledger.conflicts
                    inv_stable_replays += case_ledger.stable_replays
                    if not errs:
                        invalid_fail.append(f"{inv.name}: unexpectedly PASSED")
                    elif not expectation_match(case, errs):
                        invalid_fail.append(
                            f"{inv.name}: rejected but tags miss; errs={errs[:6]}"
                        )
                    else:
                        invalid_reject += 1
                        print(f"  INVALID REJECT {inv.name}")
                    continue
                # Non-ledger injects: fingerprint correctness without cross-case ledger
                errs = validate_document(
                    doc, cat, recipe_schema, graph_schema, None
                )
            else:
                try:
                    doc = json.loads(raw, parse_constant=_reject_json_constant)
                except ValueError as ve:
                    errs = [str(ve)]
                    if expectation_match(case, errs):
                        invalid_reject += 1
                        print(f"  INVALID REJECT {inv.name} ({errs[0]})")
                        continue
                    invalid_fail.append(f"{inv.name}: parse error not matching: {ve}")
                    continue
                if isinstance(doc, dict):
                    doc.pop("_test_meta", None)
                errs = validate_document(
                    doc, cat, recipe_schema, graph_schema, None
                )

            if not errs:
                invalid_fail.append(f"{inv.name}: unexpectedly PASSED")
            elif not expectation_match(case, errs):
                invalid_fail.append(
                    f"{inv.name}: rejected but tags miss; errs={errs[:6]}"
                )
            else:
                invalid_reject += 1
                print(f"  INVALID REJECT {inv.name}")
        except Exception as e:
            errs = [f"exception:{e}"]
            if expectation_match(case, errs):
                invalid_reject += 1
                print(f"  INVALID REJECT {inv.name} (exception path)")
            else:
                invalid_fail.append(f"{inv.name}: exception {e}")

    print("--- summary ---")
    print(f"valid: {valid_pass}/{len(valid_files)} pass")
    print(f"invalid: {invalid_reject}/{len(invalid_files)} rejected")
    print(
        f"ledger: valid_stable_replays={ledger.stable_replays} "
        f"valid_conflicts={ledger.conflicts} "
        f"inv_stable_replays={inv_stable_replays} "
        f"inv_conflicts={inv_conflicts}"
    )
    ok = (
        not valid_fail
        and not invalid_fail
        and valid_pass == len(valid_files)
        and invalid_reject == len(invalid_files)
    )
    if valid_fail:
        print("VALID FAILURES:")
        for x in valid_fail:
            print(f"  - {x}")
    if invalid_fail:
        print("INVALID FAILURES:")
        for x in invalid_fail:
            print(f"  - {x}")
    if ok:
        print(
            f"PASS gate: valid_n={valid_pass} invalid_m={invalid_reject} "
            f"verdict=C0_BLOCK_DNA_CORRECTION_COMPLETE_NO_ACCEPT"
        )
        return 0
    print("FAIL gate")
    return 1


if __name__ == "__main__":
    sys.exit(main())

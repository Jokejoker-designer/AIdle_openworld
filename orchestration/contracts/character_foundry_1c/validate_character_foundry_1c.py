#!/usr/bin/env python3
"""Deterministic Character Foundry 1C intake validator (WO-CHAR-1C-001 / W1).

Validates:
  1) source_manifest.lock.json against live Foundry manifest bytes
  2) deterministic normalization of all 28 MD character records
  3) each CharacterSpec against character_spec.schema.json (Draft 2020-12)
  4) intake_report.json identity with live re-normalization
  5) fixtures/valid/** must PASS schema + semantic gates
  6) fixtures/invalid/** must FAIL as expected (fail-closed)

Exit codes:
  0  — 28 valid source records + all invalid fixtures rejected as expected
  1  — any mismatch, unexpected pass, missing artifact, or IO error

No Foundry source mutation. No network. stdlib + already-present jsonschema only.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
FOUNDRY = REPO / "game_character" / "AIdle_Character_Foundry_MD"
MANIFEST_PATH = FOUNDRY / "manifest.json"
SCHEMA_PATH = ROOT / "character_spec.schema.json"
LOCK_PATH = ROOT / "source_manifest.lock.json"
INTAKE_PATH = ROOT / "intake_report.json"
VALID_DIR = ROOT / "fixtures" / "valid"
INVALID_DIR = ROOT / "fixtures" / "invalid"

LOCKED_MANIFEST_SHA256 = (
    "bdba6b53174e1d6671f28302b4ae67275ad22bf3c2e978603791acd19e6cc4ba"
)
PACK_VERSION = "1.0"
PACKAGE_NAME = "AIdle Character Foundry MD"
EXPECTED_CHARACTER_COUNT = 28
EXPECTED_WORLD_COUNT = 7
SCHEMA_VERSION = "character_spec/1.0"

WORLD_BY_FOLDER: dict[str, dict[str, str]] = {
    "01_cozy_cyber_pixel": {
        "world_profile_id": "cozy_cyber_pixel",
        "world_profile_display": "Cozy Cyber-Pixel / Dreamy Low-Poly",
    },
    "02_surrealism_canvas": {
        "world_profile_id": "surrealism_canvas",
        "world_profile_display": "Surrealism Canvas",
    },
    "03_solarpunk_haven": {
        "world_profile_id": "solarpunk_haven",
        "world_profile_display": "Solarpunk Haven",
    },
    "04_arcane_clockwork": {
        "world_profile_id": "arcane_clockwork",
        "world_profile_display": "Arcane Clockwork",
    },
    "05_spirit_valley": {
        "world_profile_id": "spirit_valley",
        "world_profile_display": "Spirit Valley",
    },
    "06_oceanpunk_abyss": {
        "world_profile_id": "oceanpunk_abyss",
        "world_profile_display": "Oceanpunk / Bioluminescent Abyss",
    },
    "07_tiny_diorama": {
        "world_profile_id": "tiny_diorama",
        "world_profile_display": "Tiny Diorama World",
    },
}

DISPLAY_TO_ID = {
    v["world_profile_display"]: v["world_profile_id"] for v in WORLD_BY_FOLDER.values()
}

CHARACTER_CLASSES = {
    "COMPANION",
    "NPC_GUIDE",
    "NPC_WORKER",
    "NPC_SOCIAL",
    "NPC_QUEST",
    "CREATURE_TAMEABLE",
    "CREATURE_AMBIENT",
    "ROBOT_HELPER",
    "SPIRIT_ENTITY",
    "CONSTRUCT",
}

COZY_CAST_IDS = ("CCP-RH-001", "CCP-NS-002", "CCP-NW-003", "CCP-CT-004")
COZY_CAST_ID_SET = set(COZY_CAST_IDS)
NORI7_ID = "CCP-RH-001"

# Architecture-level denials always attached (fail-closed). Not invented gameplay.
UNIVERSAL_DENYLIST: tuple[str, ...] = (
    "direct_world_commit",
    "mutate_canonical_inventory",
    "mutate_ownership",
    "mutate_economy",
    "execute_arbitrary_code",
    "trustlayer_tool_invocation",
    "replace_or_merge_aida",
    "provider_credential_access",
)

# Aliases / authority-shaped tokens that must never appear on allowlists (F01).
AUTHORITY_ALLOWLIST_DENY_ALIASES: tuple[str, ...] = UNIVERSAL_DENYLIST + (
    "world_commit",
    "direct_commit",
    "canonical_inventory",
    "mutate_inventory",
    "inventory_mutate",
    "ownership_mutate",
    "economy_mutate",
    "arbitrary_code",
    "execute_code",
    "run_arbitrary_code",
    "trustlayer_tool",
    "trustlayer_tools",
    "invoke_trustlayer_tool",
    "replace_aida",
    "merge_aida",
    "aida_replace",
    "provider_credential",
    "credential_access",
    "credentials_access",
)

REQUIRED_DENY_MARKERS = (
    "direct_world_commit",
    "replace_or_merge_aida",
)

# Identity-bearing fields for AIda collision (F04/F08/F09). relationship_hooks intentionally
# excluded so legitimate relationship prose may mention AIda without claiming to be AIda.
AIDA_IDENTITY_FIELDS: tuple[str, ...] = (
    "display_name",
    "character_id",
    "species_form",
    "gameplay_role",
)

# Minimal confusable fold for AIda identity comparison only (F09). Comparison-only —
# never rewrites stored source strings. Maps lookalike Cyrillic/Greek A/I to Latin.
# Covers: Cyrillic A/a (U+0410/U+0430), Cyrillic Byelorussian-Ukrainian I/i (U+0406/U+0456),
# Greek Alpha/alpha (U+0391/U+03B1), Greek Iota/iota (U+0399/U+03B9).
_AIDA_IDENTITY_CONFUSABLE_MAP = str.maketrans(
    {
        "\u0410": "A",  # CYRILLIC CAPITAL LETTER A
        "\u0430": "a",  # CYRILLIC SMALL LETTER A
        "\u0406": "I",  # CYRILLIC CAPITAL LETTER BYELORUSSIAN-UKRAINIAN I
        "\u0456": "i",  # CYRILLIC SMALL LETTER BYELORUSSIAN-UKRAINIAN I
        "\u0391": "A",  # GREEK CAPITAL LETTER ALPHA
        "\u03b1": "a",  # GREEK SMALL LETTER ALPHA
        "\u0399": "I",  # GREEK CAPITAL LETTER IOTA
        "\u03b9": "i",  # GREEK SMALL LETTER IOTA
    }
)

# Batch envelope allowed root keys only (F05; additionalProperties:false).
BATCH_ROOT_ALLOWED_KEYS: frozenset[str] = frozenset(
    {
        "schema_version",
        "character_count",
        "world_count",
        "manifest_sha256",
        "records",
    }
)
BATCH_SCHEMA_VERSION = "character_foundry_1c_intake_batch/1.0"

AIDA_NAME_RE = re.compile(r"\baida\b", re.IGNORECASE)
ID_RE = re.compile(r"^[A-Z]{2,3}-[A-Z]{2}-[0-9]{3}$")

# Invalid fixture expected rejection reasons (case_id -> tags)
INVALID_CASE_EXPECTATIONS: dict[str, list[str]] = {
    "INV-01-authority-leakage-direct-commit": [
        "can_world_commit",
        "authority",
        "const",
    ],
    "INV-02-malformed-record": ["type", "character_id", "schema"],
    "INV-03-duplicate-ids": ["duplicate", "character_id"],
    "INV-04-stale-source-hash": ["stale", "source_sha256", "provenance"],
    "INV-05-missing-limitation": ["limitation", "required", "minLength"],
    "INV-06-empty-denylist": ["behavior_denylist", "minItems", "empty"],
    "INV-07-unknown-world": ["world_profile", "enum", "unknown"],
    "INV-08-unknown-class": ["character_class", "enum", "unknown"],
    "INV-09-missing-allowlist": ["behavior_allowlist", "minItems", "required"],
    "INV-10-unknown-fields": [
        "additionalProperties",
        "additional properties",
        "not allowed",
        "unknown",
    ],
    "INV-11-aida-identity-collision": ["aida", "identity", "collision"],
    "INV-12-false-counts": ["character_count", "false_count", "const"],
    "INV-13-tool-authority-true": ["tool_authority", "authority", "const"],
    "INV-14-empty-ability": ["world_ability", "minLength", "missing"],
    # Codex Directive 65 fail-closed correction fixtures (F01/F03/F04/F05/F06)
    "INV-15-allowlist-universal-deny-token": [
        "allowlist_universal_deny",
        "behavior_allowlist",
        "direct_world_commit",
        "authority",
    ],
    "INV-16-allow-deny-intersection": [
        "allow_deny_intersection",
        "behavior_allowlist",
        "behavior_denylist",
        "intersection",
    ],
    "INV-17-aida-normalized-identity-collision": [
        "aida",
        "identity",
        "collision",
        "normalized",
    ],
    "INV-18-batch-root-additional-properties": [
        "additionalProperties",
        "batch",
        "extra_backdoor",
        "tool_authority",
        "unknown",
    ],
    "INV-19-cozy-cast-binding-false": [
        "cozy_cast",
        "binding",
        "CCP-RH-001",
        "cozy",
    ],
    # Codex Directive 66 Unicode identity correction fixtures (F08/F09)
    "INV-20-aida-fullwidth-identity-collision": [
        "aida",
        "identity",
        "collision",
        "fullwidth",
        "nfkc",
        "normalized",
    ],
    "INV-21-aida-mixed-script-identity-collision": [
        "aida",
        "identity",
        "collision",
        "confusable",
        "mixed",
        "normalized",
    ],
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_action_token(token: str) -> str:
    """Normalize allow/deny tokens for intersection and universal-deny matching.

    Lowercases; maps separators (space/dot/hyphen/underscore/slash) to underscore;
    collapses repeats; strips non-alnum edges.
    """
    t = str(token).strip().lower()
    t = re.sub(r"[\s.\-_/\\|:;]+", "_", t)
    t = re.sub(r"[^a-z0-9_]+", "", t)
    t = re.sub(r"_+", "_", t).strip("_")
    return t


def fold_identity_confusables(value: str) -> str:
    """Map minimal mixed-script confusables to Latin for AIda identity compare only.

    Deliberately small allowlist (Cyrillic A/a I/i, Greek Alpha/alpha Iota/iota).
    Does not rewrite stored source strings — comparison path only (F09).
    """
    return str(value).translate(_AIDA_IDENTITY_CONFUSABLE_MAP)


def normalize_identity_text(value: str) -> str:
    """Normalize identity-bearing text for AIda collision (F04/F08/F09).

    Pipeline (comparison-only; never mutates stored source strings):
      1) unicodedata.normalize NFKC (fullwidth ＡＩｄａ -> AIda)  [F08]
      2) minimal confusable fold (Cyrillic/Greek A/I lookalikes -> Latin) [F09]
      3) casefold
      4) strip separators, punctuation, and zero-width chars (D65 retained)

    So AI-da / A.I.da / ai_da / fullwidth AIda / mixed-script Aіda / Аida /
    Aιda / Looks like AIda all collide with the AIda identity surface.
    relationship_hooks is intentionally not passed through this gate.
    """
    t = unicodedata.normalize("NFKC", str(value))
    t = fold_identity_confusables(t)
    t = t.casefold()
    # Strip zero-width and common punctuation/separators (D65)
    t = re.sub(r"[\s.\-_·•'\"`~!@#$%^&*()+=\[\]{};:,<>?/\\|]+", "", t)
    t = re.sub(r"[^\w]", "", t, flags=re.UNICODE)
    return t


def identity_claims_aida(value: str) -> bool:
    """True when normalized identity text is or embeds the AIda identity token."""
    norm = normalize_identity_text(value)
    if not norm:
        return False
    if norm == "aida":
        return True
    # Embeddings after separator strip: lookslikeaida, isaida, aidaform, ...
    if "aida" in norm:
        return True
    return False


# Precomputed normalized universal-deny / authority tokens
_UNIVERSAL_DENY_NORM: frozenset[str] = frozenset(
    normalize_action_token(t) for t in UNIVERSAL_DENYLIST
)
_AUTHORITY_ALLOW_DENY_NORM: frozenset[str] = frozenset(
    normalize_action_token(t) for t in AUTHORITY_ALLOWLIST_DENY_ALIASES
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def strip_md(value: str | None) -> str | None:
    if value is None:
        return None
    v = value.strip()
    v = v.strip("`").strip()
    v = re.sub(r"\s+", " ", v)
    return v


def table_cell(text: str, label: str) -> str | None:
    # Match markdown table rows: | Label | value |
    pat = re.compile(
        rf"^\|\s*{re.escape(label)}\s*\|\s*(.*?)\s*\|\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    m = pat.search(text)
    if not m:
        return None
    return strip_md(m.group(1))


def section_body(text: str, heading: str) -> str | None:
    """Return body under a ### heading until next ### or ##."""
    pat = re.compile(
        rf"^###\s+{heading}\s*\n+(.*?)(?=^###\s+|^##\s+|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    m = pat.search(text)
    if not m:
        return None
    body = m.group(1).strip()
    # drop trailing blank lines / single-paragraph only
    body = re.sub(r"\n+", " ", body)
    body = re.sub(r"\s+", " ", body).strip()
    return body or None


def split_phrases(text: str) -> list[str]:
    """Deterministic phrase split preserving source wording."""
    t = re.sub(r"\s+", " ", text.strip())
    t = t.rstrip(".")
    # Vietnamese " và " / English " and " as list separators when comma-like
    t = re.sub(r"\s+và\s+", ", ", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+and\s+", ", ", t, flags=re.IGNORECASE)
    parts = [p.strip(" .;") for p in t.split(",")]
    out: list[str] = []
    seen: set[str] = set()
    for p in parts:
        if not p:
            continue
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return out


def derive_allowlist(ability: str) -> list[str]:
    phrases = split_phrases(ability)
    if not phrases:
        # Fallback: whole ability as single allowlisted capability (preserve source)
        return [ability.strip()]
    return phrases


def derive_denylist(limitation: str) -> list[str]:
    phrases = split_phrases(limitation)
    out: list[str] = []
    seen: set[str] = set()
    for p in phrases:
        if p not in seen:
            seen.add(p)
            out.append(p)
    for u in UNIVERSAL_DENYLIST:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def parse_character_md(rel_path: str, file_bytes: bytes) -> dict[str, Any]:
    text = file_bytes.decode("utf-8")
    folder = rel_path.split("/", 1)[0]
    if folder not in WORLD_BY_FOLDER:
        raise ValueError(f"unknown world folder for path: {rel_path}")

    world = WORLD_BY_FOLDER[folder]
    source_sha = sha256_bytes(file_bytes)

    # display name from H1
    hm = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    display_name = strip_md(hm.group(1)) if hm else None

    character_id = strip_md(table_cell(text, "Character ID"))
    world_profile_display = strip_md(table_cell(text, "World Profile"))
    character_class = strip_md(table_cell(text, "Character Class"))
    species_form = strip_md(table_cell(text, "Species/Form"))
    gameplay_role = strip_md(table_cell(text, "Gameplay Role"))
    rig_family = strip_md(table_cell(text, "Rig Family"))
    source_status = strip_md(table_cell(text, "Status đề xuất"))
    if source_status is None:
        source_status = strip_md(table_cell(text, "Status"))

    ability = section_body(text, r"Năng lực chính")
    if ability is None:
        ability = section_body(text, r"N[ăa]ng l[ưu]c ch[ií]nh")
    limitation = section_body(text, r"Giới hạn bắt buộc")
    if limitation is None:
        limitation = section_body(text, r"Gi[ớo]i h[ạa]n b[ắa]t bu[ộo]c")

    spawn = section_body(text, r"Vị trí xuất hiện")
    rel_hooks = section_body(text, r"Quan hệ gợi ý")

    if not character_id or not ID_RE.match(character_id):
        raise ValueError(f"malformed character_id in {rel_path}: {character_id!r}")
    if not display_name:
        raise ValueError(f"missing display_name in {rel_path}")
    if not character_class or character_class not in CHARACTER_CLASSES:
        raise ValueError(f"unknown/missing class in {rel_path}: {character_class!r}")
    if not species_form or not gameplay_role:
        raise ValueError(f"missing species/role in {rel_path}")
    if not ability or len(ability) < 8:
        raise ValueError(f"missing/short ability in {rel_path}")
    if not limitation or len(limitation) < 8:
        raise ValueError(f"missing/short limitation in {rel_path}")

    # Prefer locked folder mapping; still require source display matches lock
    if world_profile_display and world_profile_display != world["world_profile_display"]:
        # tolerate exact source string if it maps via DISPLAY_TO_ID
        mapped = DISPLAY_TO_ID.get(world_profile_display)
        if mapped != world["world_profile_id"]:
            raise ValueError(
                f"world profile mismatch in {rel_path}: "
                f"source={world_profile_display!r} folder={folder}"
            )

    allowlist = derive_allowlist(ability)
    denylist = derive_denylist(limitation)
    if not allowlist:
        raise ValueError(f"empty allowlist after normalize: {rel_path}")
    if not denylist:
        raise ValueError(f"empty denylist after normalize: {rel_path}")

    spec: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "character_id": character_id,
        "display_name": display_name,
        "world_profile_id": world["world_profile_id"],
        "world_profile_display": world["world_profile_display"],
        "character_class": character_class,
        "species_form": species_form,
        "gameplay_role": gameplay_role,
        "world_ability": ability,
        "limitation": limitation,
        "behavior_allowlist": allowlist,
        "behavior_denylist": denylist,
        "authority": {
            "can_world_commit": False,
            "tool_authority": False,
            "trustlayer_worker": False,
            "is_system_companion": False,
            "durable_mutation_path": "proposal->validation->preview->confirm->world_commit",
        },
        "identity_boundary": {
            "is_aida": False,
            "aida_merge_or_replace": False,
            "replaces_system_companion": False,
        },
        "provenance": {
            "package": PACKAGE_NAME,
            "pack_version": PACK_VERSION,
            "source_path": rel_path.replace("\\", "/"),
            "source_sha256": source_sha,
            "manifest_sha256": LOCKED_MANIFEST_SHA256,
        },
        "cozy_cast": character_id in COZY_CAST_IDS,
    }
    if spawn:
        spec["spawn_location"] = spawn
    if rel_hooks:
        spec["relationship_hooks"] = rel_hooks
    if source_status:
        spec["source_status"] = source_status
    if rig_family:
        spec["rig_family"] = rig_family
    return spec


def list_character_paths(manifest: dict[str, Any]) -> list[str]:
    files = manifest.get("files") or []
    out: list[str] = []
    for f in files:
        f = str(f).replace("\\", "/")
        # character files: NN_folder/NN_name.md excluding 00_WORLD_INDEX
        if re.match(r"^[0-9]{2}_[^/]+/[0-9]{2}_.+\.md$", f) and not f.endswith(
            "00_WORLD_INDEX.md"
        ):
            out.append(f)
    return out


def normalize_all() -> tuple[list[dict[str, Any]], dict[str, Any], str, str]:
    """Return (records, lock_doc, sha_before, sha_after)."""
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(f"missing Foundry manifest: {MANIFEST_PATH}")
    sha_before = sha256_file(MANIFEST_PATH)
    man_bytes = MANIFEST_PATH.read_bytes()
    sha_after_read = sha256_bytes(man_bytes)
    if sha_before != sha_after_read:
        raise RuntimeError("manifest hash unstable during read")
    manifest = json.loads(man_bytes.decode("utf-8"))
    char_paths = list_character_paths(manifest)
    if len(char_paths) != EXPECTED_CHARACTER_COUNT:
        raise ValueError(
            f"expected {EXPECTED_CHARACTER_COUNT} character paths, got {len(char_paths)}"
        )
    if int(manifest.get("character_count", -1)) != EXPECTED_CHARACTER_COUNT:
        raise ValueError("manifest character_count != 28")
    if int(manifest.get("world_count", -1)) != EXPECTED_WORLD_COUNT:
        raise ValueError("manifest world_count != 7")
    if str(manifest.get("version")) != PACK_VERSION:
        raise ValueError(f"manifest version != {PACK_VERSION}")

    records: list[dict[str, Any]] = []
    lock_chars: list[dict[str, Any]] = []
    for rel in char_paths:
        path = FOUNDRY / rel
        if not path.is_file():
            raise FileNotFoundError(f"missing character source: {rel}")
        data = path.read_bytes()
        spec = parse_character_md(rel, data)
        records.append(spec)
        lock_chars.append(
            {
                "character_id": spec["character_id"],
                "display_name": spec["display_name"],
                "character_class": spec["character_class"],
                "world_profile_id": spec["world_profile_id"],
                "source_path": rel,
                "source_sha256": spec["provenance"]["source_sha256"],
                "cozy_cast": spec.get("cozy_cast", False),
            }
        )

    # stable order by character_id
    records.sort(key=lambda r: r["character_id"])
    lock_chars.sort(key=lambda r: r["character_id"])

    ids = [r["character_id"] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate character_id after normalize")

    worlds = []
    for folder, meta in WORLD_BY_FOLDER.items():
        worlds.append(
            {
                "folder": folder,
                "world_profile_id": meta["world_profile_id"],
                "world_profile_display": meta["world_profile_display"],
                "character_ids": [
                    c["character_id"]
                    for c in lock_chars
                    if c["world_profile_id"] == meta["world_profile_id"]
                ],
            }
        )

    sha_after = sha256_file(MANIFEST_PATH)
    lock_doc = {
        "schema_version": "source_manifest.lock/1.0",
        "package": PACKAGE_NAME,
        "version": PACK_VERSION,
        "source_root": "game_character/AIdle_Character_Foundry_MD",
        "manifest_path": "game_character/AIdle_Character_Foundry_MD/manifest.json",
        "manifest_sha256": LOCKED_MANIFEST_SHA256,
        "manifest_sha256_observed_before": sha_before,
        "manifest_sha256_observed_after": sha_after,
        "source_diff": "zero" if sha_before == sha_after == LOCKED_MANIFEST_SHA256 else "DIFF",
        "character_count": EXPECTED_CHARACTER_COUNT,
        "world_count": EXPECTED_WORLD_COUNT,
        "files_listed": len(manifest.get("files") or []),
        "character_classes_enum": sorted(CHARACTER_CLASSES),
        "world_profiles": worlds,
        "characters": lock_chars,
        "identity_boundary": {
            "aida_present_in_foundry": False,
            "merge_replace_aida_allowed": False,
            "nori7_id": NORI7_ID,
            "nori7_class": "ROBOT_HELPER",
            "nori7_is_system_companion": False,
            "cozy_cast_ids": list(COZY_CAST_IDS),
            "system_companion_mvp": "text_only_AIda_outside_foundry_pack",
        },
        "universal_denylist": list(UNIVERSAL_DENYLIST),
        "normalization_rules": {
            "ability_source": "### Năng lực chính",
            "limitation_source": "### Giới hạn bắt buộc",
            "allowlist": "split ability phrases on commas / 'và' / 'and'; preserve source strings",
            "denylist": "split limitation phrases + attach universal architecture denials",
            "authority_const": "can_world_commit=false tool_authority=false trustlayer_worker=false is_system_companion=false",
            "allowlist_fail_closed": "reject any normalized allowlist token intersecting UNIVERSAL_DENYLIST or authority aliases (F01)",
            "allow_deny_intersection": "reject allow∩deny and allow∩universal_deny after token normalization (F03)",
            "aida_identity_normalize": "comparison-only: NFKC then minimal confusable fold (Cyrillic A/a I/i, Greek Alpha/alpha Iota/iota) then casefold then strip punctuation/separators/zero-width on display_name,character_id,species_form,gameplay_role; reject AIda collisions including fullwidth and mixed-script; relationship_hooks prose allowed; never rewrite stored source strings (F04/F08/F09)",
            "batch_envelope": "intake_batch root additionalProperties:false; only schema_version,character_count,world_count,manifest_sha256,records (F05)",
            "cozy_cast_binding": "cozy_cast true iff character_id in CCP-RH-001,CCP-NS-002,CCP-NW-003,CCP-CT-004 else false (F06)",
            "no_foundry_source_edits": True,
        },
    }
    return records, lock_doc, sha_before, sha_after


def semantic_errors_spec(spec: dict[str, Any], lock: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(spec, dict):
        return ["spec: not an object"]

    cid = spec.get("character_id")

    # --- F04: normalized AIda identity collision on identity-bearing fields ---
    for field in AIDA_IDENTITY_FIELDS:
        raw = spec.get(field)
        if raw is None:
            continue
        text = str(raw)
        if identity_claims_aida(text) or AIDA_NAME_RE.search(text):
            errors.append(
                f"aida_identity_collision: normalized identity field {field} collides with AIda"
            )

    identity = spec.get("identity_boundary") or {}
    if isinstance(identity, dict):
        if identity.get("is_aida") is True:
            errors.append("aida_identity_collision: identity_boundary.is_aida=true")
        if identity.get("aida_merge_or_replace") is True:
            errors.append("aida_identity_collision: aida_merge_or_replace=true")
        if identity.get("replaces_system_companion") is True:
            errors.append("aida_identity_collision: replaces_system_companion=true")

    authority = spec.get("authority") or {}
    if isinstance(authority, dict):
        if authority.get("can_world_commit") is True:
            errors.append("authority_leakage: can_world_commit=true")
        if authority.get("tool_authority") is True:
            errors.append("authority_leakage: tool_authority=true")
        if authority.get("trustlayer_worker") is True:
            errors.append("authority_leakage: trustlayer_worker=true")
        if authority.get("is_system_companion") is True:
            errors.append("authority_leakage: is_system_companion=true (Foundry forbidden)")

    denylist = spec.get("behavior_denylist")
    if not isinstance(denylist, list) or len(denylist) == 0:
        errors.append("empty_denylist: behavior_denylist missing or empty")
    else:
        for marker in REQUIRED_DENY_MARKERS:
            if marker not in denylist:
                errors.append(f"denylist_missing_required:{marker}")

    allowlist = spec.get("behavior_allowlist")
    if not isinstance(allowlist, list) or len(allowlist) == 0:
        errors.append("missing_allowlist: behavior_allowlist missing or empty")
    else:
        # --- F01: allowlist must not name universal-deny / authority tokens ---
        for token in allowlist:
            if not isinstance(token, str):
                continue
            ntok = normalize_action_token(token)
            if not ntok:
                continue
            if ntok in _AUTHORITY_ALLOW_DENY_NORM or ntok in _UNIVERSAL_DENY_NORM:
                errors.append(
                    f"allowlist_universal_deny: behavior_allowlist token "
                    f"{token!r} names forbidden authority/UNIVERSAL_DENYLIST action"
                )
            else:
                # Also catch punctuated variants that collapse to a deny token
                for deny_n in _UNIVERSAL_DENY_NORM:
                    if ntok == deny_n or ntok.replace("_", "") == deny_n.replace("_", ""):
                        errors.append(
                            f"allowlist_universal_deny: behavior_allowlist token "
                            f"{token!r} matches universal deny {deny_n}"
                        )
                        break

        # --- F03: allow ∩ deny and allow ∩ universal_deny ---
        if isinstance(denylist, list):
            allow_norm = {
                normalize_action_token(t): t
                for t in allowlist
                if isinstance(t, str) and normalize_action_token(t)
            }
            deny_norm = {
                normalize_action_token(t): t
                for t in denylist
                if isinstance(t, str) and normalize_action_token(t)
            }
            inter = set(allow_norm) & set(deny_norm)
            for n in sorted(inter):
                errors.append(
                    f"allow_deny_intersection: token {allow_norm[n]!r} present in "
                    f"both behavior_allowlist and behavior_denylist"
                )
            inter_ud = set(allow_norm) & _UNIVERSAL_DENY_NORM
            for n in sorted(inter_ud):
                # May duplicate F01 messaging; keep explicit F03 tag
                errors.append(
                    f"allow_deny_intersection: allowlist token collides with "
                    f"UNIVERSAL_DENYLIST normalized={n}"
                )

    ability = spec.get("world_ability")
    limitation = spec.get("limitation")
    if not isinstance(ability, str) or len(ability.strip()) < 8:
        errors.append("missing_ability: world_ability too short or absent")
    if not isinstance(limitation, str) or len(limitation.strip()) < 8:
        errors.append("missing_limitation: limitation too short or absent")

    # --- F06: cozy_cast deterministic binding ---
    if isinstance(cid, str):
        expected_cozy = cid in COZY_CAST_ID_SET
        if "cozy_cast" not in spec:
            errors.append(
                f"cozy_cast_binding: cozy_cast required; expected {expected_cozy} for {cid}"
            )
        else:
            actual = spec.get("cozy_cast")
            if not isinstance(actual, bool) or actual is not expected_cozy:
                errors.append(
                    f"cozy_cast_binding: character_id={cid} requires "
                    f"cozy_cast={expected_cozy}, got {actual!r}"
                )

    prov = spec.get("provenance") or {}
    if isinstance(prov, dict):
        if prov.get("manifest_sha256") != LOCKED_MANIFEST_SHA256:
            errors.append("stale_source_hash: provenance.manifest_sha256 mismatch")
        src_sha = prov.get("source_sha256")
        src_path = prov.get("source_path")
        if lock is not None and isinstance(src_path, str) and isinstance(src_sha, str):
            by_path = {
                c["source_path"]: c["source_sha256"] for c in lock.get("characters", [])
            }
            if src_path in by_path and by_path[src_path] != src_sha:
                errors.append(
                    f"stale_source_hash: source_sha256 mismatch for {src_path}"
                )
            # Also reject known-bad zero / placeholder hashes
        if isinstance(src_sha, str) and (
            src_sha == ("0" * 64) or src_sha == ("f" * 64)
        ):
            errors.append("stale_source_hash: placeholder source_sha256")

    return errors


def schema_errors(validator: Draft202012Validator, instance: Any) -> list[str]:
    errs = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    out: list[str] = []
    for e in errs:
        path = "/".join(str(p) for p in e.absolute_path) or "<root>"
        out.append(f"{path}: {e.message}")
    return out


def validate_spec(
    validator: Draft202012Validator,
    spec: Any,
    lock: dict[str, Any] | None = None,
) -> list[str]:
    errors = schema_errors(validator, spec)
    if isinstance(spec, dict):
        errors.extend(semantic_errors_spec(spec, lock))
    return errors


def validate_batch_semantics(doc: dict[str, Any]) -> list[str]:
    """Strict intake batch envelope (F05) + count/hash/duplicate gates."""
    errors: list[str] = []
    if not isinstance(doc, dict):
        return ["batch: not an object"]

    # F05: additionalProperties:false at batch root
    extra_keys = sorted(set(doc.keys()) - BATCH_ROOT_ALLOWED_KEYS)
    if extra_keys:
        errors.append(
            "batch_additional_properties: unknown or authority-shaped root fields "
            f"not allowed: {extra_keys}"
        )
        # Explicit tags for common Codex probes
        if "extra_backdoor" in doc:
            errors.append(
                "batch_additional_properties: extra_backdoor rejected (additionalProperties:false)"
            )
        if "tool_authority" in doc:
            errors.append(
                "batch_additional_properties: tool_authority at batch root rejected "
                "(additionalProperties:false)"
            )

    # Required fields / types
    if doc.get("schema_version") != BATCH_SCHEMA_VERSION:
        errors.append(
            f"batch: schema_version must be {BATCH_SCHEMA_VERSION!r}, "
            f"got {doc.get('schema_version')!r}"
        )
    for req in ("character_count", "world_count", "manifest_sha256", "records"):
        if req not in doc:
            errors.append(f"batch: missing required field {req}")

    records = doc.get("records")
    if not isinstance(records, list):
        errors.append("records: missing or not array")
        return errors

    ids = [
        r.get("character_id")
        for r in records
        if isinstance(r, dict) and "character_id" in r
    ]
    seen: set[str] = set()
    for i in ids:
        if not isinstance(i, str):
            continue
        if i in seen:
            errors.append(f"duplicate_character_id:{i}")
        seen.add(i)
    declared = doc.get("character_count")
    if declared is not None and declared != len(records):
        errors.append(
            f"false_count: character_count={declared} but records={len(records)}"
        )
    if declared is not None and declared != EXPECTED_CHARACTER_COUNT:
        # batch claiming full pack must be 28
        if len(records) == EXPECTED_CHARACTER_COUNT or declared != len(records):
            errors.append(
                f"false_count: character_count must be {EXPECTED_CHARACTER_COUNT} for full pack claim (got {declared})"
            )
    wdecl = doc.get("world_count")
    if wdecl is not None and wdecl != EXPECTED_WORLD_COUNT:
        errors.append(f"false_count: world_count must be {EXPECTED_WORLD_COUNT}")
    if doc.get("manifest_sha256") not in (None, LOCKED_MANIFEST_SHA256):
        errors.append("stale_source_hash: batch manifest_sha256 mismatch")
    return errors


def build_validator(schema: dict[str, Any]) -> Draft202012Validator:
    return Draft202012Validator(schema)


def load_fixture_cases(directory: Path) -> list[tuple[str, Path, Any]]:
    cases: list[tuple[str, Path, Any]] = []
    if not directory.is_dir():
        return cases
    for path in sorted(directory.glob("*.json")):
        doc = load_json(path)
        case_id = path.stem
        if isinstance(doc, dict) and "case_id" in doc:
            case_id = str(doc["case_id"])
        cases.append((case_id, path, doc))
    return cases


def fixture_payload(doc: Any) -> Any:
    """Extract payload from fixture wrapper or return raw CharacterSpec/batch."""
    if isinstance(doc, dict) and "payload" in doc and "case_id" in doc:
        return doc["payload"]
    return doc


def is_batch(doc: Any) -> bool:
    if not isinstance(doc, dict):
        return False
    if doc.get("schema_version") == BATCH_SCHEMA_VERSION:
        return True
    # Treat authority-shaped or count/hash envelope shapes as batches even if
    # schema_version is wrong/missing so F05 additionalProperties still fires.
    if "records" in doc and (
        "character_count" in doc or "world_count" in doc or "manifest_sha256" in doc
    ):
        return True
    return False


def validate_fixture_payload(
    validator: Draft202012Validator,
    payload: Any,
    lock: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if is_batch(payload):
        # Strict batch envelope (F05) + each record schema/semantics
        errors.extend(validate_batch_semantics(payload))
        records = payload.get("records") if isinstance(payload, dict) else None
        if isinstance(records, list):
            for i, rec in enumerate(records):
                rec_errs = validate_spec(validator, rec, lock)
                for e in rec_errs:
                    errors.append(f"records[{i}]: {e}")
        # false count / wrong const on batch root
        if isinstance(payload, dict):
            if payload.get("character_count") != EXPECTED_CHARACTER_COUNT:
                errors.append("batch: character_count const violation")
            if payload.get("world_count") != EXPECTED_WORLD_COUNT:
                errors.append("batch: world_count const violation")
            if payload.get("manifest_sha256") != LOCKED_MANIFEST_SHA256:
                errors.append("batch: manifest_sha256 const violation")
        return errors
    return validate_spec(validator, payload, lock)


def expected_invalid_match(case_id: str, errors: list[str]) -> bool:
    tags = INVALID_CASE_EXPECTATIONS.get(case_id)
    if not tags:
        # unknown case: any rejection counts
        return len(errors) > 0
    blob = " ".join(errors).lower()
    return any(tag.lower() in blob for tag in tags)


def build_intake_report(
    records: list[dict[str, Any]],
    lock: dict[str, Any],
    sha_before: str,
    sha_after: str,
) -> dict[str, Any]:
    class_dist: dict[str, int] = {}
    for r in records:
        cls = r["character_class"]
        class_dist[cls] = class_dist.get(cls, 0) + 1
    for c in sorted(CHARACTER_CLASSES):
        class_dist.setdefault(c, 0)

    return {
        "schema_version": "character_foundry_1c_intake_report/1.0",
        "work_order_id": "WO-CHAR-1C-001-FOUNDRY-SCHEMA-INTAKE",
        "wave": "W1_SCHEMA",
        "package": PACKAGE_NAME,
        "pack_version": PACK_VERSION,
        "manifest_sha256_locked": LOCKED_MANIFEST_SHA256,
        "manifest_sha256_before": sha_before,
        "manifest_sha256_after": sha_after,
        "manifest_hash_match": sha_before == sha_after == LOCKED_MANIFEST_SHA256,
        "source_diff": "zero" if sha_before == sha_after == LOCKED_MANIFEST_SHA256 else "DIFF",
        "character_count": len(records),
        "world_count": EXPECTED_WORLD_COUNT,
        "unique_character_ids": len({r["character_id"] for r in records}),
        "class_distribution": class_dist,
        "world_profiles": lock["world_profiles"],
        "identity_boundary": lock["identity_boundary"],
        "normalization": {
            "reproducible": True,
            "preserve_source_strings": True,
            "structured_allowlist_source": "derived_from_world_ability_phrases",
            "structured_denylist_source": "derived_from_limitation_phrases_plus_universal",
            "universal_denylist": list(UNIVERSAL_DENYLIST),
            "foundry_source_edits": False,
        },
        "records": records,
        "valid_count": len(records),
        "invalid_count": 0,
    }


def main() -> int:
    print("=== Character Foundry 1C intake validator ===")
    print(f"repo:     {REPO}")
    print(f"foundry:  {FOUNDRY}")
    print(f"schema:   {SCHEMA_PATH}")
    print(f"lock:     {LOCK_PATH}")
    print(f"intake:   {INTAKE_PATH}")
    print(f"valid:    {VALID_DIR}")
    print(f"invalid:  {INVALID_DIR}")

    failures = 0
    report_lines: list[str] = []

    if not SCHEMA_PATH.is_file():
        print("FATAL: missing character_spec.schema.json", file=sys.stderr)
        return 1

    try:
        schema = load_json(SCHEMA_PATH)
        Draft202012Validator.check_schema(schema)
        validator = build_validator(schema)
    except (OSError, json.JSONDecodeError, SchemaError) as exc:
        print(f"FATAL: schema load error: {exc}", file=sys.stderr)
        return 1

    # --- Source normalize + hash identity ---
    try:
        records, live_lock, sha_before, sha_after = normalize_all()
    except Exception as exc:  # noqa: BLE001 — harness must report
        print(f"FATAL: normalize failed: {exc}", file=sys.stderr)
        return 1

    print(f"manifest_sha256_before: {sha_before}")
    print(f"manifest_sha256_after:  {sha_after}")
    print(f"manifest_sha256_locked: {LOCKED_MANIFEST_SHA256}")
    hash_ok = sha_before == sha_after == LOCKED_MANIFEST_SHA256
    print(f"source_hash_identity: {'PASS' if hash_ok else 'FAIL'}")
    if not hash_ok:
        failures += 1

    # --- Lock file ---
    if not LOCK_PATH.is_file():
        print("FATAL: missing source_manifest.lock.json", file=sys.stderr)
        return 1
    lock_doc = load_json(LOCK_PATH)
    if lock_doc.get("manifest_sha256") != LOCKED_MANIFEST_SHA256:
        print("FAIL: lock manifest_sha256 mismatch", file=sys.stderr)
        failures += 1
    if int(lock_doc.get("character_count", -1)) != EXPECTED_CHARACTER_COUNT:
        print("FAIL: lock character_count != 28", file=sys.stderr)
        failures += 1
    if int(lock_doc.get("world_count", -1)) != EXPECTED_WORLD_COUNT:
        print("FAIL: lock world_count != 7", file=sys.stderr)
        failures += 1
    # Compare character hashes with live recompute
    lock_by_id = {c["character_id"]: c for c in lock_doc.get("characters", [])}
    live_by_id = {c["character_id"]: c for c in live_lock["characters"]}
    if set(lock_by_id) != set(live_by_id):
        print("FAIL: lock character id set != live", file=sys.stderr)
        failures += 1
    else:
        for cid, live_c in live_by_id.items():
            if lock_by_id[cid].get("source_sha256") != live_c["source_sha256"]:
                print(f"FAIL: lock source_sha256 mismatch for {cid}", file=sys.stderr)
                failures += 1

    # --- Validate all 28 source records ---
    valid_source = 0
    invalid_source = 0
    source_errors: dict[str, list[str]] = {}
    for rec in records:
        errs = validate_spec(validator, rec, lock_doc)
        if errs:
            invalid_source += 1
            source_errors[rec["character_id"]] = errs
            print(f"[SOURCE {rec['character_id']}] FAIL :: {errs[0]}")
            failures += 1
        else:
            valid_source += 1
    print(f"source_records_valid: {valid_source}/{EXPECTED_CHARACTER_COUNT}")
    print(f"source_records_invalid: {invalid_source}")
    if valid_source != EXPECTED_CHARACTER_COUNT:
        failures += 1

    # --- Intake report identity ---
    if not INTAKE_PATH.is_file():
        print("FATAL: missing intake_report.json", file=sys.stderr)
        return 1
    intake = load_json(INTAKE_PATH)
    expected_intake = build_intake_report(records, live_lock, sha_before, sha_after)
    # Compare record sets (character_id + critical fields)
    intake_records = intake.get("records") or []
    if len(intake_records) != EXPECTED_CHARACTER_COUNT:
        print(
            f"FAIL: intake_report record count {len(intake_records)} != 28",
            file=sys.stderr,
        )
        failures += 1
    else:
        # deterministic equality of normalized records
        if json.dumps(intake_records, sort_keys=True, ensure_ascii=False) != json.dumps(
            expected_intake["records"], sort_keys=True, ensure_ascii=False
        ):
            print(
                "FAIL: intake_report records != live re-normalization",
                file=sys.stderr,
            )
            failures += 1
        else:
            print("intake_report_identity: PASS")
    if intake.get("manifest_sha256_locked") != LOCKED_MANIFEST_SHA256:
        print("FAIL: intake locked hash mismatch", file=sys.stderr)
        failures += 1
    if not intake.get("manifest_hash_match", False):
        print("FAIL: intake manifest_hash_match is false", file=sys.stderr)
        failures += 1

    # --- Valid fixtures ---
    valid_cases = load_fixture_cases(VALID_DIR)
    valid_pass = 0
    if not valid_cases:
        print("FAIL: no valid fixtures", file=sys.stderr)
        failures += 1
    for case_id, path, doc in valid_cases:
        payload = fixture_payload(doc)
        errs = validate_fixture_payload(validator, payload, lock_doc)
        if errs:
            print(f"[VALID {case_id}] expected=PASS actual=FAIL :: {errs[0]}")
            failures += 1
        else:
            valid_pass += 1
            print(f"[VALID {case_id}] PASS")
    print(f"valid_fixtures_pass: {valid_pass}/{len(valid_cases)}")

    # --- Invalid fixtures ---
    invalid_cases = load_fixture_cases(INVALID_DIR)
    invalid_rejected = 0
    if len(invalid_cases) < 12:
        print(
            f"FAIL: need >=12 invalid fixtures, got {len(invalid_cases)}",
            file=sys.stderr,
        )
        failures += 1
    for case_id, path, doc in invalid_cases:
        payload = fixture_payload(doc)
        errs = validate_fixture_payload(validator, payload, lock_doc)
        rejected = len(errs) > 0
        tag_ok = expected_invalid_match(case_id, errs) if rejected else False
        if rejected and tag_ok:
            invalid_rejected += 1
            print(
                f"[INVALID {case_id}] expected=FAIL actual=FAIL [OK] :: {errs[0][:160]}"
            )
        else:
            failures += 1
            detail = errs[0][:160] if errs else "NO_ERRORS (unexpected pass)"
            print(
                f"[INVALID {case_id}] expected=FAIL actual="
                f"{'FAIL_WRONG_REASON' if rejected else 'PASS'} [UNEXPECTED] :: {detail}"
            )
    print(f"invalid_fixtures_rejected: {invalid_rejected}/{len(invalid_cases)}")

    print("--- summary ---")
    print(f"source_valid: {valid_source}/{EXPECTED_CHARACTER_COUNT}")
    print(f"invalid_rejected: {invalid_rejected}/{len(invalid_cases)}")
    print(f"source_hash_identity: {'PASS' if hash_ok else 'FAIL'}")
    print(f"failures: {failures}")
    report_lines.append(
        f"SOURCE_VALID={valid_source}/{EXPECTED_CHARACTER_COUNT} "
        f"INVALID_REJECTED={invalid_rejected}/{len(invalid_cases)} "
        f"HASH_IDENTITY={'PASS' if hash_ok else 'FAIL'} failures={failures}"
    )
    for line in report_lines:
        print(line)

    if failures:
        print("HARNESS_RESULT=FAIL", file=sys.stderr)
        return 1
    print("HARNESS_RESULT=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

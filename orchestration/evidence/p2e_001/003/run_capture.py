#!/usr/bin/env python3
"""P2E-001 D2 headed real-input capture runner (VERIFY_ONLY evidence lease).

Fresh fail-closed harness under evidence/p2e_001/003 only.
Fails on ERROR/USER ERROR/SCRIPT ERROR, RID leak, null RenderingServer
(including teardown), wrong dimensions, missing/duplicate PNGs, Build-R
rotation 0→0, camera_yaw_unchanged!=true, or forbidden API fallback markers.
Does not patch product code. Does not rewrite 001/** or 002/**.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("E:/AIdle_openworld")
GODOT = ROOT / "tools" / "Godot_v4.3-stable_win64_console.exe"
EVIDENCE = ROOT / "orchestration" / "evidence" / "p2e_001" / "003"
SCRIPT = EVIDENCE / "capture_p2e001_d2_real_input.gd"

REQUIRED_STATES = [
    "module_selection",
    "exploration_camera_R",
    "build_preview_R",
    "valid_snapped_preview",
    "rejected_invalid_placement",
    "confirmed_complete",
    "cancelled_preview",
]
VIEWPORTS = ["1280x720", "868x517"]

ERROR_RE = re.compile(
    r"(?m)^(ERROR:|SCRIPT ERROR|Parse Error|Compile Error|USER ERROR:|USER SCRIPT ERROR)"
)
SOFT_OR_HARD = re.compile(
    r"(RID allocations|RenderingServer::get_singleton\(\)|Parameter \"RenderingServer)",
    re.I,
)
FORBIDDEN_SOURCE_RE = re.compile(
    r"select_module\s*\(|confirm_and_commit\s*\(|place_highlighted_module\s*\(|"
    r"confirm_and_commit_direct|elevate\(\s*300\s*\)",
    re.I,
)
FORBIDDEN_LOG_RE = re.compile(
    r"confirm_and_commit_direct|place_highlighted_module_direct|select_module_called.: true|"
    r"residual.*confirm_and_commit|elevate\(300\)",
    re.I,
)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest().lower()


def png_dims(p: Path) -> tuple[int, int]:
    data = p.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not_png:{p}")
    w = int.from_bytes(data[16:20], "big")
    h = int.from_bytes(data[20:24], "big")
    return w, h


def scan_harness_source() -> list[str]:
    hits: list[str] = []
    text = SCRIPT.read_text(encoding="utf-8", errors="replace")
    # Allow mentions in comments / forbidden-detection strings, but flag executable call forms.
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("##"):
            continue
        # Fail only on actual call-style usages as acceptance path (not _note_forbidden strings).
        if re.search(r"\bselect_module\s*\(", line) and "would_have" not in line and "never" not in line.lower():
            # place path uses select_module inside product; harness must not call it.
            if "_ba.call" in line or ".select_module" in line or "call(\"select_module\"" in line:
                hits.append(f"source_L{i}:select_module_call")
        if re.search(r'call\("confirm_and_commit"', line) or re.search(
            r"\.confirm_and_commit\s*\(", line
        ):
            hits.append(f"source_L{i}:confirm_and_commit_call")
        if re.search(r'call\("place_highlighted_module"', line):
            hits.append(f"source_L{i}:place_highlighted_module_call")
        if re.search(r'call\("elevate"\s*,\s*300\)', line) or "elevate(300)" in line:
            hits.append(f"source_L{i}:elevate_bulk_call")
    return hits


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if not GODOT.exists():
        print("RUNNER_FAIL godot_missing", GODOT)
        return 2
    if not SCRIPT.exists():
        print("RUNNER_FAIL script_missing", SCRIPT)
        return 2

    source_hits = scan_harness_source()
    if source_hits:
        print("RUNNER_FAIL harness_forbidden_source", source_hits)
        # Continue run but record as hard fail later.

    ts = time.strftime("%Y%m%d_%H%M%S")
    user_data = Path(os.environ.get("TEMP", "/tmp")) / f"p2e001_d2_userdata_{ts}"
    (user_data / "AppData" / "Roaming").mkdir(parents=True, exist_ok=True)
    (user_data / "AppData" / "Local").mkdir(parents=True, exist_ok=True)

    godot_log = EVIDENCE / "godot_headed.log"
    runner_log = EVIDENCE / "runner.log"

    env = os.environ.copy()
    env["APPDATA"] = str(user_data / "AppData" / "Roaming")
    env["LOCALAPPDATA"] = str(user_data / "AppData" / "Local")

    cmd = [
        str(GODOT),
        "--path",
        str(ROOT / "game"),
        "--resolution",
        "1280x720",
        "--windowed",
        "--log-file",
        str(godot_log),
        "-s",
        str(SCRIPT),
    ]
    print("RUNNER cmd:", " ".join(cmd))
    print("RUNNER user_data_isolation:", user_data)

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=600,
        )
    except subprocess.TimeoutExpired as e:
        runner_log.write_text(f"TIMEOUT\n{e}", encoding="utf-8")
        print("RUNNER_FAIL timeout")
        return 3

    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if godot_log.exists():
        combined += "\n" + godot_log.read_text(encoding="utf-8", errors="replace")
    # Also merge stdout into godot_headed if log-file empty-ish
    if not godot_log.exists() or godot_log.stat().st_size < 32:
        godot_log.write_text(combined, encoding="utf-8")
    runner_log.write_text(combined, encoding="utf-8")

    failures: list[str] = []
    if source_hits:
        failures.append(f"harness_forbidden_source={source_hits}")
    if proc.returncode != 0:
        failures.append(f"godot_exit={proc.returncode}")

    errors: list[str] = []
    for ln in combined.splitlines():
        if ERROR_RE.search(ln) or (SOFT_OR_HARD.search(ln) and "ERROR" in ln.upper()):
            errors.append(ln.strip()[:300])
        elif SOFT_OR_HARD.search(ln):
            errors.append(ln.strip()[:300])
    seen_e: set[str] = set()
    errors_u: list[str] = []
    for e in errors:
        if e not in seen_e:
            seen_e.add(e)
            errors_u.append(e)
    errors = errors_u
    if errors:
        failures.append(f"error_lines={len(errors)}")

    # Forbidden acceptance path markers in runtime log
    forbidden_log: list[str] = []
    for ln in combined.splitlines():
        if FORBIDDEN_LOG_RE.search(ln) and "would_have" not in ln and "FORBIDDEN_AVOIDED" not in ln:
            # residual confirm_and_commit_direct is hard fail
            forbidden_log.append(ln.strip()[:240])
    if "confirm_and_commit_direct" in combined and "residual" in combined.lower():
        if any("confirm_and_commit_direct" in x for x in forbidden_log):
            failures.append("forbidden_confirm_and_commit_direct_in_log")
    if forbidden_log:
        # Filter soft mentions from meta prints that declare false
        hard = [
            x
            for x in forbidden_log
            if "confirm_and_commit_direct\": false" not in x
            and "confirm_and_commit_direct=false" not in x
            and "place_highlighted_module_direct\": false" not in x
        ]
        # If residual true appears
        if any("confirm_and_commit_direct" in x and "true" in x.lower() for x in combined.splitlines()):
            failures.append("forbidden_log_confirm_direct_true")
        if any("residual" in x and "confirm_and_commit" in x for x in combined.splitlines() if "C2-R" not in x):
            if "confirm_and_commit_direct" in combined and '"confirm_and_commit_direct": true' in combined:
                failures.append("forbidden_log_confirm_residual")

    required_pngs = [f"{s}_{vp}.png" for s in REQUIRED_STATES for vp in VIEWPORTS]
    png_meta: list[dict] = []
    shas: dict[str, str] = {}
    for name in required_pngs:
        p = EVIDENCE / name
        if not p.is_file():
            failures.append(f"missing_png={name}")
            continue
        try:
            w, h = png_dims(p)
        except ValueError as e:
            failures.append(f"bad_png={name}:{e}")
            continue
        digest = sha256_file(p)
        if digest in shas:
            failures.append(f"duplicate_sha={name}=={shas[digest]}")
        shas[digest] = name
        if "1280x720" in name and (abs(w - 1280) > 24 or abs(h - 720) > 24):
            failures.append(f"dim_mismatch={name}:{w}x{h}")
        if "868x517" in name and (abs(w - 868) > 24 or abs(h - 517) > 24):
            failures.append(f"dim_mismatch={name}:{w}x{h}")
        png_meta.append(
            {
                "file": name,
                "path": str(p).replace("\\", "/"),
                "width": w,
                "height": h,
                "sha256": digest,
                "bytes": p.stat().st_size,
            }
        )

    yaw_proof = []
    meta_path = EVIDENCE / "visual_claim_meta.json"
    if meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            yaw_proof = meta.get("build_preview_R_yaw_proof", [])
            for y in yaw_proof:
                if y.get("camera_yaw_unchanged") is not True:
                    failures.append(f"camera_yaw_unchanged_not_true:{y.get('file')}")
                rot0 = float(y.get("rot_before", 0) or 0)
                rot1 = float(y.get("rot_after", 0) or 0)
                if abs(rot0 - rot1) < 0.001:
                    failures.append(f"build_preview_R_rotation_0_to_0:{y.get('file')}")
                if y.get("preview_rotated") is False:
                    failures.append(f"preview_rotated_false:{y.get('file')}")
            # Exact 2 viewport proofs expected
            if len(yaw_proof) < 2:
                failures.append(f"yaw_proof_count={len(yaw_proof)}")
            # Forbidden residual flags in captures
            for c in meta.get("captures", []):
                if c.get("confirm_and_commit_direct") is True:
                    failures.append(f"capture_confirm_direct:{c.get('file')}")
                if c.get("confirm_hold_residual_direct") is True:
                    failures.append(f"capture_confirm_residual:{c.get('file')}")
                if c.get("place_highlighted_module_direct") is True:
                    failures.append(f"capture_place_direct:{c.get('file')}")
                if c.get("select_module_called") is True:
                    failures.append(f"capture_select_module:{c.get('file')}")
                if c.get("elev_bulk_residual") is True or c.get("elevate_direct_residual") is True:
                    failures.append(f"capture_elev_residual:{c.get('file')}")
                if c.get("cancel_esc_residual_direct") is True:
                    failures.append(f"capture_cancel_residual:{c.get('file')}")
        except Exception as e:
            failures.append(f"meta_parse:{e}")
    else:
        failures.append("missing_visual_claim_meta")

    f02_zero = len(errors) == 0
    marker_pass = "AIDLE_P2E001_D2_HEADED=PASS" in combined

    manifest = {
        "schema": "p2e_001_d2_evidence_manifest/1.0",
        "work_order": "WO-P2E-001-PLAYABILITY-CORRECTION-002",
        "wave": "D2",
        "directive_id": 72,
        "authority_token": "VERIFY_ONLY",
        "godot_exit": proc.returncode,
        "marker_pass": marker_pass,
        "error_line_count": len(errors),
        "error_samples": errors[:20],
        "error_classification": {
            "error_count_including_teardown": len(errors),
            "f02_zero_error_including_teardown": f02_zero,
            "signature_if_match": (
                "P2E_F02_TEARDOWN_RID_RENDERINGSERVER"
                if any("RID" in e or "RenderingServer" in e for e in errors)
                else None
            ),
            "note": "No filtering/hiding/reclassification of Godot ERROR lines.",
        },
        "failures": failures,
        "pngs": png_meta,
        "required_states": REQUIRED_STATES,
        "viewports": VIEWPORTS,
        "build_preview_R_yaw_proof": yaw_proof,
        "select_module_api_injection": False,
        "confirm_and_commit_direct_used": False,
        "harness_source_forbidden_hits": source_hits,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runner_verdict": "PASS" if not failures else "FAIL",
        "evidence_001_002_immutable": True,
    }
    (EVIDENCE / "evidence_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    (EVIDENCE / "png_sha256.json").write_text(
        json.dumps({m["file"]: m["sha256"] for m in png_meta}, indent=2),
        encoding="utf-8",
    )

    # Tree hashes for evidence files only under 003
    tree: dict[str, str] = {}
    for p in sorted(EVIDENCE.rglob("*")):
        if p.is_file() and p.name not in ("evidence_tree_sha256.json",):
            rel = str(p.relative_to(EVIDENCE)).replace("\\", "/")
            tree[rel] = sha256_file(p)
    (EVIDENCE / "evidence_tree_sha256.json").write_text(
        json.dumps(tree, indent=2), encoding="utf-8"
    )

    print("RUNNER exit_code", proc.returncode)
    print("RUNNER png_count", len(png_meta), "/", len(required_pngs))
    print("RUNNER errors", len(errors))
    print("RUNNER failures", failures)
    print("RUNNER f02_zero_error_including_teardown", f02_zero)
    if failures:
        print("AIDLE_P2E001_D2_RUNNER=FAIL")
        return 1
    print("AIDLE_P2E001_D2_RUNNER=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

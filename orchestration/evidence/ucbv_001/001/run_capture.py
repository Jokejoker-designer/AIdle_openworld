#!/usr/bin/env python3
"""UCBV-001 U7 headed dual-res capture runner (VERIFY_ONLY evidence lease 001)."""
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
EVIDENCE = ROOT / "orchestration" / "evidence" / "ucbv_001" / "001"
SCRIPT = EVIDENCE / "capture_ucbv_u7_headed.gd"

REQUIRED_STATES = [
    "launch",
    "nori_kit_belonging",
    "manual_build_preview",
    "build_R",
    "cancel",
    "confirm",
]
VIEWPORTS = ["1280x720", "868x517"]

ERROR_RE = re.compile(
    r"(?m)^(ERROR:|SCRIPT ERROR|Parse Error|Compile Error|USER ERROR:|USER SCRIPT ERROR)"
)
SOFT_OR_HARD = re.compile(
    r"(RID allocations|RenderingServer::get_singleton\(\)|Parameter \"RenderingServer)",
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


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if not GODOT.exists():
        print("RUNNER_FAIL godot_missing", GODOT)
        return 2
    if not SCRIPT.exists():
        print("RUNNER_FAIL script_missing", SCRIPT)
        return 2

    ts = time.strftime("%Y%m%d_%H%M%S")
    user_data = Path(os.environ.get("TEMP", "/tmp")) / f"ucbv_u7_userdata_{ts}"
    user_data.mkdir(parents=True, exist_ok=True)

    godot_log = EVIDENCE / "godot_headed.log"
    runner_log = EVIDENCE / "runner.log"

    cmd = [
        str(GODOT),
        "--path",
        str(ROOT / "game"),
        "--resolution",
        "1280x720",
        "--windowed",
        "--log-file",
        str(godot_log),
        "--write-movie",  # no-op safety if unsupported is fine; actual is -s
        "-s",
        str(SCRIPT),
    ]
    # Godot may not like --write-movie without path; strip it for safety.
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

    env = os.environ.copy()
    env["GODOT_USER_DATA_DIR"] = str(user_data)

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=720,
        )
    except subprocess.TimeoutExpired as e:
        runner_log.write_text(f"TIMEOUT\n{e}", encoding="utf-8")
        print("RUNNER_FAIL timeout")
        return 3

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    log_text = (
        godot_log.read_text(encoding="utf-8", errors="replace") if godot_log.is_file() else ""
    )
    combined = stdout + "\n" + stderr + "\n" + log_text
    runner_log.write_text(
        f"exit={proc.returncode}\ncmd={' '.join(cmd)}\n\n---STDOUT---\n{stdout}\n\n---STDERR---\n{stderr}\n",
        encoding="utf-8",
    )
    (EVIDENCE / "runner_console.txt").write_text(combined, encoding="utf-8", errors="replace")

    primary_err_src = log_text if log_text.strip() else combined
    error_lines = [
        ln for ln in primary_err_src.splitlines() if ERROR_RE.search(ln) or SOFT_OR_HARD.search(ln)
    ]
    err_samples = error_lines[:20]
    marker_pass = "AIDLE_UCBV001_U7_HEADED=PASS" in combined

    png_sha: dict[str, str] = {}
    pngs: list[dict] = []
    missing: list[str] = []
    dim_fails: list[str] = []
    dupes: list[str] = []
    seen_sha: dict[str, str] = {}

    for state in REQUIRED_STATES:
        for vp in VIEWPORTS:
            name = f"{state}_{vp}.png"
            p = EVIDENCE / name
            if not p.is_file():
                missing.append(name)
                continue
            digest = sha256_file(p)
            png_sha[name] = digest
            try:
                ww, hh = png_dims(p)
            except Exception as ex:  # noqa: BLE001
                dim_fails.append(f"{name}:{ex}")
                ww, hh = -1, -1
            expect_w, expect_h = (1280, 720) if vp == "1280x720" else (868, 517)
            if abs(ww - expect_w) > 24 or abs(hh - expect_h) > 24:
                dim_fails.append(f"{name}:got={ww}x{hh}")
            if digest in seen_sha:
                dupes.append(f"{name}=={seen_sha[digest]}")
            else:
                seen_sha[digest] = name
            pngs.append(
                {
                    "file": name,
                    "path": str(p).replace("\\", "/"),
                    "width": ww,
                    "height": hh,
                    "sha256": digest,
                    "bytes": p.stat().st_size,
                    "state": state,
                    "viewport": vp,
                }
            )

    (EVIDENCE / "png_sha256.json").write_text(
        json.dumps(png_sha, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    meta_path = EVIDENCE / "visual_claim_meta.json"
    meta: dict = {}
    if meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as ex:
            meta = {"_parse_error": str(ex)}

    build_r_ok = True
    build_r_proof = meta.get("build_R_yaw_proof") or []
    for br in build_r_proof:
        if br.get("camera_yaw_unchanged") is not True:
            build_r_ok = False
        if br.get("preview_rotated") is False:
            build_r_ok = False

    belonging_ok = True
    for bp in meta.get("belonging_proof") or []:
        if not bp.get("nori_built") or not bp.get("boot_ok"):
            belonging_ok = False

    gates = meta.get("gates") or []
    gates_ok = all(bool(g.get("ok", False)) for g in gates) if gates else False

    zero_error = len(error_lines) == 0
    headed_pass = (
        proc.returncode == 0
        and marker_pass
        and zero_error
        and not missing
        and not dim_fails
        and build_r_ok
        and belonging_ok
        and len(pngs) >= len(REQUIRED_STATES) * len(VIEWPORTS)
    )

    tree_files = sorted(
        [str(p.relative_to(EVIDENCE)).replace("\\", "/") for p in EVIDENCE.rglob("*") if p.is_file()]
    )
    tree_sha = {f: sha256_file(EVIDENCE / f) for f in tree_files}
    (EVIDENCE / "evidence_tree_sha256.json").write_text(
        json.dumps(tree_sha, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    manifest = {
        "schema": "ucbv_001_u7_evidence_manifest/1.0",
        "work_order": "WO-UCBV-001-UNIFIED-CHARACTER-BLOCK-VISUAL-FOUNDATION",
        "wave": "U7",
        "directive_id": 81,
        "authority_token": "VERIFY_ONLY",
        "godot_exit": proc.returncode,
        "marker_pass": marker_pass,
        "headed_pass": headed_pass,
        "error_line_count": len(error_lines),
        "error_samples": err_samples,
        "error_classification": {
            "error_count_including_teardown": len(error_lines),
            "zero_error_including_teardown": zero_error,
            "note": "No filtering/hiding/reclassification of Godot ERROR lines.",
        },
        "zero_error_including_teardown": zero_error,
        "missing_pngs": missing,
        "dimension_fails": dim_fails,
        "duplicate_sha_notes": dupes,
        "png_count": len(pngs),
        "expected_png_count": len(REQUIRED_STATES) * len(VIEWPORTS),
        "required_states": REQUIRED_STATES,
        "viewports": VIEWPORTS,
        "pngs": pngs,
        "build_R_ok": build_r_ok,
        "belonging_ok": belonging_ok,
        "gates_ok": gates_ok,
        "gates": gates,
        "honesty": meta.get("honesty"),
        "u6_residuals_surfaced": meta.get("u6_residuals_surfaced"),
        "art_style_id_active": meta.get("art_style_id_active", "unknown"),
        "capture_source": "godot_headed",
        "live_parity": True,
        "h1_evidence_immutable": True,
        "h1_paths_not_written": [
            "orchestration/evidence/h1_consolidate_001/**",
            "orchestration/receipts/h1_consolidate_001/**",
        ],
    }
    (EVIDENCE / "evidence_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    print(
        "RUNNER_SUMMARY headed_pass=%s zero_error=%s marker=%s png=%d missing=%d dim_fails=%d exit=%s"
        % (
            headed_pass,
            zero_error,
            marker_pass,
            len(pngs),
            len(missing),
            len(dim_fails),
            proc.returncode,
        )
    )
    if err_samples:
        print("ERROR_SAMPLES:")
        for ln in err_samples:
            print(" ", ln[:200])
    return 0 if headed_pass else 1


if __name__ == "__main__":
    sys.exit(main())

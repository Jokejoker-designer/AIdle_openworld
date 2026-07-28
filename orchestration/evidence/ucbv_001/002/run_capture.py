#!/usr/bin/env python3
"""UCBV-001 C4 headed dual-res capture runner (VERIFY_ONLY evidence lease 002)."""
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
EVIDENCE = ROOT / "orchestration" / "evidence" / "ucbv_001" / "002"
SCRIPT = EVIDENCE / "capture_ucbv_c4_headed.gd"

REQUIRED_STATES = [
    "idle",
    "walk",
    "turn",
    "warm_cream",
    "catalog_28",
    "build_place",
    "qr_rotate",
    "elevation",
    "invalid_placement",
    "confirm",
    "placement_2",
    "cancel",
    "delete_select",
    "delete_cancel",
    "delete_confirm",
    "undo",
    "save_reload",
    "scan_action",
    "happy_action",
]
VIEWPORTS = ["1280x720", "868x517"]

ERROR_RE = re.compile(
    r"(?m)^(ERROR:|SCRIPT ERROR|Parse Error|Compile Error|USER ERROR:|USER SCRIPT ERROR)"
)
NAV_WARN_RE = re.compile(
    r"(Source geometry parsing\.\.\. RenderingServer meshes|"
    r"agent_height is ceiled|"
    r"agent_radius is ceiled)",
    re.I,
)
SOFT_OR_HARD = re.compile(
    r"(RID allocations|RenderingServer::get_singleton\(\)|Parameter \"RenderingServer|"
    r"Missing resource|Failed loading resource)",
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
    user_data = Path(os.environ.get("TEMP", "/tmp")) / f"ucbv_c4_userdata_{ts}"
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
        "-s",
        str(SCRIPT),
    ]
    print("RUNNER cmd:", " ".join(cmd))

    env = os.environ.copy()
    env["GODOT_USER_DATA_DIR"] = str(user_data)

    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=900,
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
        f"exit={proc.returncode}\ncmd={' '.join(cmd)}\nseconds={round(time.time()-t0,2)}\n\n"
        f"---STDOUT---\n{stdout}\n\n---STDERR---\n{stderr}\n",
        encoding="utf-8",
    )
    (EVIDENCE / "runner_console.txt").write_text(combined, encoding="utf-8", errors="replace")

    primary_err_src = log_text if log_text.strip() else combined
    error_lines = [
        ln
        for ln in primary_err_src.splitlines()
        if ERROR_RE.search(ln) or SOFT_OR_HARD.search(ln)
    ]
    nav_warn_lines = [ln for ln in primary_err_src.splitlines() if NAV_WARN_RE.search(ln)]
    marker_pass = "AIDLE_UCBV001_C4_HEADED=PASS" in combined

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
                dw, dh = png_dims(p)
            except ValueError as e:
                dim_fails.append(f"{name}:{e}")
                continue
            expect_w, expect_h = map(int, vp.split("x"))
            if abs(dw - expect_w) > 24 or abs(dh - expect_h) > 24:
                dim_fails.append(f"{name}:got={dw}x{dh}")
            if digest in seen_sha:
                dupes.append(f"{name}=={seen_sha[digest]}")
            else:
                seen_sha[digest] = name
            pngs.append(
                {
                    "file": name,
                    "sha256": digest,
                    "width": dw,
                    "height": dh,
                    "state": state,
                    "viewport": vp,
                }
            )

    (EVIDENCE / "png_sha256.json").write_text(
        json.dumps(png_sha, indent=2, sort_keys=True), encoding="utf-8"
    )

    # Tree hashes
    tree: dict[str, str] = {}
    for p in sorted(EVIDENCE.rglob("*")):
        if p.is_file() and p.name not in ("png_sha256.json", "evidence_tree_sha256.json"):
            rel = str(p.relative_to(EVIDENCE)).replace("\\", "/")
            tree[rel] = sha256_file(p)
    (EVIDENCE / "evidence_tree_sha256.json").write_text(
        json.dumps(tree, indent=2, sort_keys=True), encoding="utf-8"
    )

    zero_error = len(error_lines) == 0 and len(nav_warn_lines) == 0
    summary = {
        "schema": "ucbv_001_c4_headed_runner_summary/1.0",
        "wave": "C4",
        "directive_id": 91,
        "exit": proc.returncode,
        "marker_pass": marker_pass,
        "seconds": round(time.time() - t0, 2),
        "png_count": len(pngs),
        "png_expected": len(REQUIRED_STATES) * len(VIEWPORTS),
        "missing": missing,
        "dim_fails": dim_fails,
        "duplicate_sha_pairs": dupes,
        "error_count": len(error_lines),
        "error_samples": error_lines[:20],
        "nav_warn_count": len(nav_warn_lines),
        "nav_warn_samples": nav_warn_lines[:10],
        "zero_error": zero_error,
        "cmd": cmd,
        "godot": str(GODOT).replace("\\", "/"),
        "pngs": pngs,
    }
    (EVIDENCE / "headed_runner_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps({k: summary[k] for k in summary if k != "pngs"}, indent=2))
    ok = (
        proc.returncode == 0
        and marker_pass
        and not missing
        and not dim_fails
        and zero_error
    )
    print("RUNNER", "PASS" if ok else "FAIL", f"png={len(pngs)} zero_error={zero_error}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

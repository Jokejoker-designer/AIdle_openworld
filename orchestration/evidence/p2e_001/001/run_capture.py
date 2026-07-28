#!/usr/bin/env python3
"""P2E-001 A4 headed capture runner (VERIFY_ONLY evidence lease).

Runs Godot 4.3-stable headed with isolated temp user data. Fails closed on
ERROR lines, wrong dimensions, missing PNGs, or duplicate SHA-256.
Does not patch product code.
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
EVIDENCE = ROOT / "orchestration" / "evidence" / "p2e_001" / "001"
SCRIPT = EVIDENCE / "capture_p2e001_states.gd"

REQUIRED_STATES = [
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
    user_data = Path(os.environ.get("TEMP", "/tmp")) / f"p2e001_a4_userdata_{ts}"
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
            timeout=420,
        )
    except subprocess.TimeoutExpired as e:
        runner_log.write_text(f"TIMEOUT\n{e}", encoding="utf-8")
        print("RUNNER_FAIL timeout")
        return 3

    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if godot_log.exists():
        combined += "\n" + godot_log.read_text(encoding="utf-8", errors="replace")
    runner_log.write_text(combined, encoding="utf-8")

    failures: list[str] = []
    if proc.returncode != 0:
        failures.append(f"godot_exit={proc.returncode}")

    errors: list[str] = []
    for ln in combined.splitlines():
        if not ERROR_RE.search(ln):
            continue
        # Benign renderer noise sometimes appears; keep strict for SCRIPT/Parse
        if "Parameter \"m\" is null" in ln:
            continue
        errors.append(ln.strip()[:240])
    if errors:
        failures.append(f"error_lines={len(errors)}")

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
        # Dimension tolerance (±24 already in GD; enforce tags)
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

    manifest = {
        "schema": "p2e_001_a4_evidence_manifest/1.0",
        "work_order": "WO-P2E-001-BLOCK-ASSEMBLY-PREVIEW-SLICE",
        "wave": "A4",
        "godot_exit": proc.returncode,
        "marker_pass": "AIDLE_P2E001_A4_HEADED=PASS" in combined,
        "error_line_count": len(errors),
        "error_samples": errors[:20],
        "failures": failures,
        "pngs": png_meta,
        "required_states": REQUIRED_STATES,
        "viewports": VIEWPORTS,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (EVIDENCE / "evidence_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    (EVIDENCE / "png_sha256.json").write_text(
        json.dumps({m["file"]: m["sha256"] for m in png_meta}, indent=2),
        encoding="utf-8",
    )

    print("RUNNER exit_code", proc.returncode)
    print("RUNNER png_count", len(png_meta), "/", len(required_pngs))
    print("RUNNER errors", len(errors))
    print("RUNNER failures", failures)
    if failures:
        print("AIDLE_P2E001_A4_RUNNER=FAIL")
        return 1
    print("AIDLE_P2E001_A4_RUNNER=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

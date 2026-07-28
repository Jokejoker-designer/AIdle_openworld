#!/usr/bin/env python3
"""CTRL-1B-002 Q2 headed capture runner (VERIFY_ONLY).

Isolated temp user data via APPDATA/LOCALAPPDATA. Never writes human world_meta.
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
EVIDENCE = ROOT / "orchestration" / "evidence" / "control_1b_002"
SCRIPT = EVIDENCE / "capture_control_1b_states.gd"

ERROR_RE = re.compile(r"(?m)^(ERROR:|SCRIPT ERROR|Parse Error|Compile Error)")

REQUIRED_MIN_PNGS = [
    "H-01_exploration_1280x720.png",
    "H-02_composer_focused_1280x720.png",
    "H-05_build_mode_1280x720.png",
    "H-08_helper_pulse_1280x720.png",
    "H-09_homestead_panel_1280x720.png",
    "H-11_build_preview_rotate_1280x720.png",
    "H-13_esc_preview_cancelled_1280x720.png",
    "H-22_control_settings_1280x720.png",
    "H-01_exploration_868x517.png",
    "H-02_composer_focused_868x517.png",
]


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
    user_data = Path(os.environ.get("TEMP", "/tmp")) / f"ctrl1b_q2_userdata_{ts}"
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

    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        timeout=360,
    )
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if godot_log.exists():
        combined += "\n" + godot_log.read_text(encoding="utf-8", errors="replace")
    runner_log.write_text(combined, encoding="utf-8")

    failures: list[str] = []
    if proc.returncode != 0:
        failures.append(f"godot_exit={proc.returncode}")

    errors = []
    for ln in combined.splitlines():
        if not ERROR_RE.search(ln):
            continue
        if "Parameter \"m\" is null" in ln:
            continue
        # Accept only product/runtime errors; ignore navigation mesh WARNINGs already filtered by ERROR_RE
        if (
            ln.strip().startswith("ERROR:")
            or ln.strip().startswith("USER ERROR:")
            or "SCRIPT ERROR" in ln
            or "USER SCRIPT ERROR" in ln
            or "Parse Error" in ln
            or "Compile Error" in ln
        ):
            errors.append(ln)
    if errors:
        failures.append(f"error_lines={len(errors)}")
        for e in errors[:20]:
            print("ERR", e)

    png_meta: dict = {}
    sha_map: dict = {}
    dims_map: dict = {}
    for name in REQUIRED_MIN_PNGS:
        p = EVIDENCE / name
        if not p.exists():
            failures.append(f"missing_png={name}")
            continue
        try:
            w, h = png_dims(p)
        except Exception as ex:  # noqa: BLE001
            failures.append(f"png_dims_fail={name}:{ex}")
            continue
        sha = sha256_file(p)
        sha_map[name] = sha
        dims_map[name] = {"w": w, "h": h}
        png_meta[name] = {"sha256": sha, "width": w, "height": h, "bytes": p.stat().st_size}
        if name.endswith("1280x720.png") and (abs(w - 1280) > 16 or abs(h - 720) > 16):
            failures.append(f"dim_mismatch={name}:{w}x{h}")
        if name.endswith("868x517.png") and (abs(w - 868) > 16 or abs(h - 517) > 16):
            failures.append(f"dim_mismatch={name}:{w}x{h}")
        if p.stat().st_size < 2048:
            failures.append(f"tiny_png={name}")

    # Distinct hashes among required primary captures (868 may share layout family but should differ size)
    shas = list(sha_map.values())
    if len(shas) != len(set(shas)):
        failures.append("duplicate_sha_among_required")

    all_pngs = sorted(EVIDENCE.glob("H-*.png"))
    summary = {
        "godot_exit": proc.returncode,
        "error_line_count": len(errors),
        "error_lines_sample": errors[:12],
        "user_data_isolation": str(user_data).replace("\\", "/"),
        "required_pngs": png_meta,
        "png_sha256": sha_map,
        "png_dims": dims_map,
        "all_capture_count": len(all_pngs),
        "all_captures": [p.name for p in all_pngs],
        "failures": failures,
        "verdict": "PASS" if not failures else "FAIL",
        "pass_marker": "AIDLE_CTRL_1B_Q2_HEADED_CAPTURE=PASS" in combined,
    }
    (EVIDENCE / "headed_runner_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    print("RUNNER_VERDICT", summary["verdict"])
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())

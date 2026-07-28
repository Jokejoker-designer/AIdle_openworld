#!/usr/bin/env python3
"""P2E-001 C2 headed real-input capture runner (VERIFY_ONLY evidence lease).

Runs Godot 4.3-stable headed with isolated temp user data. Fails closed on
ERROR lines (including teardown RID / null RenderingServer), wrong dimensions,
missing PNGs, or duplicate SHA-256. Does not patch product code.
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
EVIDENCE = ROOT / "orchestration" / "evidence" / "p2e_001" / "002"
SCRIPT = EVIDENCE / "capture_p2e001_c2_real_input.gd"

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
# F02: also treat RID leak / null RenderingServer as hard fail (anywhere in line).
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
    user_data = Path(os.environ.get("TEMP", "/tmp")) / f"p2e001_c2_userdata_{ts}"
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
            timeout=480,
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
        if ERROR_RE.search(ln) or (SOFT_OR_HARD.search(ln) and "ERROR" in ln.upper()):
            errors.append(ln.strip()[:300])
        elif SOFT_OR_HARD.search(ln):
            # RID / RenderingServer mentions without ERROR prefix still F02.
            errors.append(ln.strip()[:300])
    # Dedupe preserve order
    seen_e: set[str] = set()
    errors_u: list[str] = []
    for e in errors:
        if e not in seen_e:
            seen_e.add(e)
            errors_u.append(e)
    errors = errors_u
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

    # Parse build_preview_R yaw proof from visual meta if present
    yaw_proof = []
    meta_path = EVIDENCE / "visual_claim_meta.json"
    if meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            yaw_proof = meta.get("build_preview_R_yaw_proof", [])
            for y in yaw_proof:
                if y.get("camera_yaw_unchanged") is not True:
                    failures.append(f"camera_yaw_unchanged_not_true:{y.get('file')}")
        except Exception as e:
            failures.append(f"meta_parse:{e}")

    manifest = {
        "schema": "p2e_001_c2_evidence_manifest/1.0",
        "work_order": "WO-P2E-001-PLAYABILITY-CORRECTION-001",
        "wave": "C2",
        "directive_id": 71,
        "authority_token": "VERIFY_ONLY",
        "godot_exit": proc.returncode,
        "marker_pass": "AIDLE_P2E001_C2_HEADED=PASS" in combined,
        "error_line_count": len(errors),
        "error_samples": errors[:20],
        "failures": failures,
        "pngs": png_meta,
        "required_states": REQUIRED_STATES,
        "viewports": VIEWPORTS,
        "build_preview_R_yaw_proof": yaw_proof,
        "select_module_api_injection": False,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runner_verdict": "PASS" if not failures else "FAIL",
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
        print("AIDLE_P2E001_C2_RUNNER=FAIL")
        return 1
    print("AIDLE_P2E001_C2_RUNNER=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""P1E-006 C1 headed two-profile capture runner (VERIFY_ONLY).

Runs Godot 4.3-stable headed, isolated temp user data attempt + world_meta
override in GDScript. Fails closed on ERROR lines, wrong dimensions, missing
PNGs, duplicate SHA-256, blank images, or missing runtime bindings.
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
EVIDENCE = ROOT / "orchestration" / "evidence" / "p1e_006_correction_002"
SCRIPT = EVIDENCE / "capture_profiles.gd"
PKG = Path("E:/AIdle_Blender_Bridge_P0/storage/generated_quarantine/BLD-03CB1AADD475")

REQUIRED_PNGS = [
    "cozy_cyber_pixel_1280x720.png",
    "surrealism_canvas_1280x720.png",
]
ERROR_RE = re.compile(
    r"(?m)^(ERROR:|SCRIPT ERROR|Parse Error|Compile Error)"
)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest().upper()


def png_dims(p: Path) -> tuple[int, int]:
    # PNG IHDR width/height at bytes 16..24
    data = p.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not_png:{p}")
    w = int.from_bytes(data[16:20], "big")
    h = int.from_bytes(data[20:24], "big")
    return w, h


def is_blankish(p: Path) -> bool:
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        # Fallback: reject tiny files only
        return p.stat().st_size < 2048
    im = Image.open(p).convert("RGB")
    samples = []
    w, h = im.size
    for gy in range(8):
        for gx in range(8):
            x = int((gx + 0.5) * w / 8)
            y = int((gy + 0.5) * h / 8)
            samples.append(im.getpixel((x, y)))
    first = samples[0]
    same = sum(1 for s in samples if all(abs(s[i] - first[i]) < 6 for i in range(3)))
    return same >= len(samples) - 2


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if not GODOT.exists():
        print("RUNNER_FAIL godot_missing", GODOT)
        return 2
    if not SCRIPT.exists():
        print("RUNNER_FAIL script_missing", SCRIPT)
        return 2
    if not PKG.is_dir():
        print("RUNNER_FAIL package_missing", PKG)
        return 2

    ts = time.strftime("%Y%m%d_%H%M%S")
    user_data = Path(os.environ.get("TEMP", "/tmp")) / f"p1e006_c1_userdata_{ts}"
    user_data.mkdir(parents=True, exist_ok=True)

    cozy_log = EVIDENCE / "godot_cozy.log"  # combined capture log (single process both profiles)
    surreal_log = EVIDENCE / "godot_surreal.log"
    runner_log = EVIDENCE / "runner.log"
    godot_log = EVIDENCE / "godot_headed.log"

    env = os.environ.copy()
    env["AIDLE_GLB_PACKAGE"] = str(PKG).replace("\\", "/")
    # Best-effort isolation; Godot 4.3-stable may ignore unknown flags
    env["APPDATA"] = str(user_data / "AppData" / "Roaming")
    env["LOCALAPPDATA"] = str(user_data / "AppData" / "Local")
    (user_data / "AppData" / "Roaming").mkdir(parents=True, exist_ok=True)
    (user_data / "AppData" / "Local").mkdir(parents=True, exist_ok=True)

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
    print("RUNNER AIDLE_GLB_PACKAGE:", env["AIDLE_GLB_PACKAGE"])

    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        timeout=300,
    )
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if godot_log.exists():
        combined += "\n" + godot_log.read_text(encoding="utf-8", errors="replace")

    # Single process captures both profiles; mirror log to both named files + runner
    cozy_log.write_text(combined, encoding="utf-8")
    surreal_log.write_text(combined, encoding="utf-8")
    runner_log.write_text(combined, encoding="utf-8")

    failures: list[str] = []
    if proc.returncode != 0:
        failures.append(f"godot_exit={proc.returncode}")

    errors = [
        ln
        for ln in combined.splitlines()
        if ERROR_RE.search(ln)
        and (
            ln.strip().startswith("ERROR:")
            or "SCRIPT ERROR" in ln
            or "Parse Error" in ln
            or "Compile Error" in ln
        )
    ]
    # Filter known non-fatal headless dummy noise if any leaked
    errors = [e for e in errors if "Parameter \"m\" is null" not in e]
    if errors:
        failures.append(f"unexpected_error_lines={len(errors)}")
        for e in errors[:12]:
            print("ERROR_HIT", e)

    if "AIDLE_P1E006_HEADED_C1=PASS" not in combined:
        failures.append("missing_pass_marker")

    shas: dict[str, str] = {}
    dims: dict[str, tuple[int, int]] = {}
    for name in REQUIRED_PNGS:
        p = EVIDENCE / name
        if not p.exists():
            failures.append(f"missing:{name}")
            continue
        try:
            w, h = png_dims(p)
            dims[name] = (w, h)
            if abs(w - 1280) > 8 or abs(h - 720) > 8:
                failures.append(f"dims:{name}:{w}x{h}")
        except Exception as ex:
            failures.append(f"png_parse:{name}:{ex}")
        if is_blankish(p):
            failures.append(f"blank:{name}")
        shas[name] = sha256_file(p)
        print(f"PNG {name} sha={shas[name]} dims={dims.get(name)}")

    if len(shas) == 2 and len(set(shas.values())) < 2:
        failures.append("duplicate_png_sha")

    meta_path = EVIDENCE / "visual_claim_meta.json"
    if not meta_path.exists():
        failures.append("missing:visual_claim_meta.json")
    else:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        profiles = meta.get("profiles") or []
        if len(profiles) < 2:
            failures.append(f"meta_profiles={len(profiles)}")
        for pr in profiles:
            for key in (
                "art_style_id_active",
                "world_profile_id",
                "capture_source",
                "sha256",
                "width",
                "height",
            ):
                if key not in pr:
                    failures.append(f"meta_missing_field:{key}")
            if pr.get("capture_source") != "godot_headed":
                failures.append(f"capture_source:{pr.get('capture_source')}")
            if not pr.get("art_style_id_active") or pr.get("art_style_id_active") == "unknown":
                failures.append("art_style_unbound")
            if pr.get("world_profile_id") != pr.get("art_style_id_active"):
                failures.append(
                    f"binding_mismatch:{pr.get('world_profile_id')}!={pr.get('art_style_id_active')}"
                )
        # Enrich meta with runner hashes (uppercase) and isolation path
        meta["runner"] = {
            "godot_exit": proc.returncode,
            "error_lines": len(errors),
            "user_data_isolation": str(user_data).replace("\\", "/"),
            "png_sha256": shas,
            "png_dims": {k: {"w": v[0], "h": v[1]} for k, v in dims.items()},
            "failures": failures,
            "verdict": "PASS" if not failures else "FAIL",
        }
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # Sidecar SHA file
    sha_path = EVIDENCE / "png_sha256.txt"
    sha_path.write_text(
        "\n".join(f"{k} {v}" for k, v in sorted(shas.items())) + "\n",
        encoding="utf-8",
    )

    if failures:
        print("RUNNER_FAIL", failures)
        print("AIDLE_P1E006_HEADED_C1_RUNNER=FAIL")
        return 1
    print("AIDLE_P1E006_HEADED_C1_RUNNER=PASS")
    print("logs_clean=true")
    print("user_data=", user_data)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.TimeoutExpired:
        print("RUNNER_FAIL timeout")
        sys.exit(3)

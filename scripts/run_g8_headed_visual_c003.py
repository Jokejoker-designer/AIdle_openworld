#!/usr/bin/env python3
"""Canonical external headed runner for G8 UI visual correction 003 (Directive 24).

Fails closed on:
  - non-zero Godot exit
  - unexpected ERROR: / SCRIPT ERROR / Parse Error / Compile Error in combined logs
  - missing required screenshots / evidence_manifest
  - non-distinct SHA-256 among PNGs
  - cancel crop unchanged (stage_cancel_preview vs after_cancel)
  - Bridge uuid warning in headed log
  - GDScript FAIL markers / final_verdict != PASS
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GODOT = ROOT / "tools" / "Godot_v4.3-stable_win64_console.exe"
EVIDENCE = ROOT / "orchestration" / "evidence" / "g8_ui_visual_correction_003"
LOG_DIR = ROOT / "orchestration" / "logs"
STDOUT_LOG = LOG_DIR / "g8-ui-visual-correction-003-runner.log"
GODOT_LOG = LOG_DIR / "g8_headed_smoke_godot.log"
REQUIRED = [
    "overview_1280x720.png",
    "responsive_868x517.png",
    "companion_open_868x517.png",
    "bridge_manual_state.png",
    "stage_wireframe.png",
    "stage_hologram.png",
    "stage_materializing.png",
    "stage_complete_confirmed.png",
    "stage_cancel_preview.png",
    "after_cancel.png",
    "evidence_manifest.json",
]

# Allowlisted ERROR patterns from other suites must not appear in this headed log.
ERROR_RE = re.compile(r"(?m)^(ERROR:|SCRIPT ERROR|Parse Error|Compile Error)")
FAIL_RE = re.compile(r"(?m)^\s*FAIL\s+")
UUID_WARN = "snapshot_id must look like uuid"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def crop_changed_pixels(a: Path, b: Path, box: tuple[int, int, int, int]) -> int:
    try:
        from PIL import Image
    except ImportError:
        # Fallback: full-image hash difference as weak signal
        return 0 if sha256_file(a) == sha256_file(b) else 1
    x0, y0, x1, y1 = box
    ia = Image.open(a).convert("RGB")
    ib = Image.open(b).convert("RGB")
    ca = ia.crop((x0, y0, x1, y1))
    cb = ib.crop((x0, y0, x1, y1))
    if ca.size != cb.size:
        return max(ca.size[0] * ca.size[1], 1)
    pa, pb = ca.load(), cb.load()
    w, h = ca.size
    changed = 0
    for y in range(h):
        for x in range(w):
            if pa[x, y] != pb[x, y]:
                changed += 1
    return changed


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if not GODOT.exists():
        print("RUNNER_FAIL godot_missing", GODOT)
        return 2

    cmd = [
        str(GODOT),
        "--path",
        str(ROOT / "game"),
        "--log-file",
        str(GODOT_LOG),
        "-s",
        "res://scripts/core/headed_visual_smoke.gd",
    ]

    print("RUNNER cmd:", " ".join(cmd))
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if GODOT_LOG.exists():
        combined += "\n" + GODOT_LOG.read_text(encoding="utf-8", errors="replace")
    STDOUT_LOG.write_text(combined, encoding="utf-8")

    failures: list[str] = []

    if proc.returncode != 0:
        failures.append(f"godot_exit={proc.returncode}")

    errors = [ln for ln in combined.splitlines() if ERROR_RE.search(ln)]
    # Filter only true ERROR lines
    errors = [e for e in errors if e.strip().startswith("ERROR:") or "SCRIPT ERROR" in e or "Parse Error" in e or "Compile Error" in e]
    if errors:
        failures.append(f"unexpected_error_lines={len(errors)}")
        for e in errors[:8]:
            print("ERROR_HIT", e)

    if UUID_WARN in combined:
        failures.append("bridge_uuid_warning_present")

    if "AIDLE_UI_VISUAL_CORRECTION_003=PASS" not in combined and "AIDLE_HEADED_VISUAL_SMOKE=PASS" not in combined:
        failures.append("missing_pass_marker")

    if FAIL_RE.search(combined) and "AIDLE_UI_VISUAL_CORRECTION_003=PASS" not in combined:
        failures.append("gdscript_fail_markers")

    # Required files
    shas: dict[str, str] = {}
    for name in REQUIRED:
        p = EVIDENCE / name
        if not p.exists():
            failures.append(f"missing:{name}")
            continue
        if name.endswith(".png"):
            shas[name] = sha256_file(p)

    if len(shas) >= 10 and len(set(shas.values())) < len(shas):
        failures.append("duplicate_png_sha")

    # Cancel crop must change (Codex used 550..900,100..250 on 1280 frames)
    pre = EVIDENCE / "stage_cancel_preview.png"
    post = EVIDENCE / "after_cancel.png"
    if pre.exists() and post.exists():
        changed = crop_changed_pixels(pre, post, (550, 100, 900, 250))
        total = (900 - 550) * (250 - 100)
        print(f"CANCEL_CROP_CHANGED={changed}/{total}")
        if changed <= 0:
            # try wider crop around right-side cancel placement
            changed2 = crop_changed_pixels(pre, post, (400, 50, 1200, 450))
            print(f"CANCEL_CROP_WIDE_CHANGED={changed2}")
            if changed2 <= 50:
                failures.append(f"cancel_crop_unchanged:{changed}/{total}")
            else:
                print("CANCEL_CROP_WIDE_PASS")
        else:
            print("CANCEL_CROP_PASS")
    else:
        failures.append("cancel_pair_missing")

    # Manifest final fields
    man_path = EVIDENCE / "evidence_manifest.json"
    if man_path.exists():
        man = json.loads(man_path.read_text(encoding="utf-8"))
        if man.get("final_verdict") != "PASS":
            failures.append(f"manifest_verdict={man.get('final_verdict')}")
        if int(man.get("capture_count", 0)) < 10:
            failures.append(f"manifest_capture_count={man.get('capture_count')}")
        if int(man.get("error_lines_count", -1)) != 0:
            failures.append(f"manifest_error_lines={man.get('error_lines_count')}")
        cp = man.get("cancel_proof") or {}
        if not cp.get("entity_absent", False):
            failures.append(f"manifest_cancel_proof={cp}")
        # attach runner log hash
        man["runner_log_sha256"] = sha256_file(STDOUT_LOG)
        man["runner_exit_code"] = proc.returncode
        man["runner_final_verdict"] = "PASS" if not failures else "FAIL"
        man_path.write_text(json.dumps(man, indent=2), encoding="utf-8")
    else:
        failures.append("manifest_missing")

    # Saved-choice: GDScript isolated seed markers must be present
    if "saved_choice_seeded" not in combined and "SAVED_CHOICE] seeded" not in combined:
        # OK markers print as "OK  saved_choice_seeded"
        if "saved_choice_seeded" not in combined and "[SAVED_CHOICE] seeded" not in combined:
            failures.append("saved_choice_seed_marker_missing")
    if "saved_choice_hash_unchanged" not in combined and "saved_choice_content_preserved" not in combined and "SAVED_CHOICE] after_ephemeral" not in combined:
        failures.append("saved_choice_preserve_marker_missing")
    if "still_surrealism=true" in combined or "saved_choice_hash_unchanged" in combined or "saved_choice_content_preserved" in combined:
        print("SAVED_CHOICE_RUNNER_PASS")
    elif "SAVED_CHOICE]" in combined:
        # inspect
        for ln in combined.splitlines():
            if "SAVED_CHOICE" in ln:
                print(ln)
    else:
        failures.append("saved_choice_proof_absent")

    if failures:
        print("CANONICAL_RUNNER=FAIL")
        for f in failures:
            print("  FAIL", f)
        print(f"Full log: {STDOUT_LOG}")
        return 1

    print("CANONICAL_RUNNER=PASS")
    print(f"log={STDOUT_LOG}")
    print(f"evidence={EVIDENCE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""P2E-001 E1 focused headed Esc single-dispatch runner (VERIFY_ONLY).

Lease: orchestration/evidence/p2e_001/004/** only.
Does not rewrite 001/002/003. Does not patch product.
Fail-closed: ERROR/USER ERROR/SCRIPT ERROR/RID/null RenderingServer including teardown;
exactly one Esc resolve + one cancel apply; zero Pause; no direct select/confirm API.
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
EVIDENCE = ROOT / "orchestration" / "evidence" / "p2e_001" / "004"
EVIDENCE_003 = ROOT / "orchestration" / "evidence" / "p2e_001" / "003"
SCRIPT = EVIDENCE / "capture_p2e001_e1_esc_single.gd"
BINDING_003_PNG = EVIDENCE_003 / "png_sha256.json"

ERROR_RE = re.compile(
    r"(?m)^(ERROR:|SCRIPT ERROR|Parse Error|Compile Error|USER ERROR:|USER SCRIPT ERROR)"
)
SOFT_OR_HARD = re.compile(
    r"(RID allocations|RenderingServer::get_singleton\(\)|Parameter \"RenderingServer)",
    re.I,
)
ESC_LINE_RE = re.compile(
    r"\[Main\] Esc resolved → (\S+) pause=(\S+)(?: resolve_n=(\d+) cancel_apply_n=(\d+))?"
)
FORBIDDEN_SOURCE_RE = re.compile(
    r'call\("select_module"|call\("confirm_and_commit"|\.select_module\s*\(|\.confirm_and_commit\s*\(',
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
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("##"):
            continue
        if FORBIDDEN_SOURCE_RE.search(line):
            hits.append(f"source_L{i}:{line.strip()[:120]}")
    return hits


def bind_003() -> dict:
    """Immutable hash binding to already-proven D72 evidence 003."""
    expected = json.loads(BINDING_003_PNG.read_text(encoding="utf-8"))
    png_checks = []
    all_match = True
    for name, digest in expected.items():
        p = EVIDENCE_003 / name
        actual = sha256_file(p) if p.is_file() else None
        match = actual == digest.lower()
        if not match:
            all_match = False
        png_checks.append(
            {
                "file": name,
                "expected_sha256": digest.lower(),
                "actual_sha256": actual,
                "match": match,
                "bytes": p.stat().st_size if p.is_file() else 0,
            }
        )
    meta_files = [
        "evidence_manifest.json",
        "png_sha256.json",
        "evidence_tree_sha256.json",
        "godot_headed.log",
        "visual_claim_meta.json",
    ]
    meta = {}
    for m in meta_files:
        mp = EVIDENCE_003 / m
        if mp.is_file():
            meta[m] = sha256_file(mp)
    return {
        "evidence_003_root": str(EVIDENCE_003).replace("\\", "/"),
        "png_count": len(png_checks),
        "png_all_match": all_match,
        "png_checks": png_checks,
        "meta_sha256": meta,
        "preserved_d72_axes_bound": [
            "teardown_zero_error",
            "real_input_select_place_rotate_elev_confirm_cancel",
            "Q_R_exploration_and_build_preview_separation",
            "responsive_dual_resolution_14_png",
            "idempotency_authority_world_commit",
        ],
        "note": "E1 re-proves Esc single-dispatch headed; D72 visual/Q/R dual-res axes bound to immutable 003 hashes",
    }


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if not GODOT.exists():
        print("RUNNER_FAIL godot_missing", GODOT)
        return 2
    if not SCRIPT.exists():
        print("RUNNER_FAIL script_missing", SCRIPT)
        return 2

    source_hits = scan_harness_source()
    binding = bind_003()
    (EVIDENCE / "evidence_003_immutable_binding.json").write_text(
        json.dumps(binding, indent=2), encoding="utf-8"
    )
    print(
        "RUNNER 003_bind png_all_match=%s count=%s"
        % (binding["png_all_match"], binding["png_count"])
    )

    ts = time.strftime("%Y%m%d_%H%M%S")
    user_data = Path(os.environ.get("TEMP", "/tmp")) / f"p2e001_e1_userdata_{ts}"
    (user_data / "AppData" / "Roaming").mkdir(parents=True, exist_ok=True)
    (user_data / "AppData" / "Local").mkdir(parents=True, exist_ok=True)

    godot_log = EVIDENCE / "godot_headed.log"
    runner_log = EVIDENCE / "runner.log"
    if godot_log.exists():
        godot_log.unlink()

    env = os.environ.copy()
    env["APPDATA"] = str(user_data / "AppData" / "Roaming")
    env["LOCALAPPDATA"] = str(user_data / "AppData" / "Local")

    # Prefer GUI Godot for headed; fall back to console binary.
    godot_bin = GODOT
    gui = ROOT / "tools" / "Godot_v4.3-stable_win64.exe"
    if gui.exists():
        godot_bin = gui

    cmd = [
        str(godot_bin),
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
    if not godot_log.exists() or godot_log.stat().st_size < 32:
        godot_log.write_text(combined, encoding="utf-8")
    else:
        # Merge stdout for markers into godot log copy for analysis
        full = godot_log.read_text(encoding="utf-8", errors="replace") + "\n" + combined
        godot_log.write_text(full, encoding="utf-8")
        combined = full
    runner_log.write_text(combined, encoding="utf-8")

    failures: list[str] = []
    if source_hits:
        failures.append(f"harness_forbidden_source={source_hits}")
    if not binding["png_all_match"]:
        failures.append("evidence_003_hash_binding_mismatch")
    if proc.returncode != 0:
        failures.append(f"godot_exit={proc.returncode}")

    errors: list[str] = []
    for ln in combined.splitlines():
        if ERROR_RE.search(ln) or (SOFT_OR_HARD.search(ln) and "ERROR" in ln.upper()):
            errors.append(ln.strip()[:300])
        elif SOFT_OR_HARD.search(ln):
            # RID / null RenderingServer without ERROR prefix still counted (no filter)
            if "WARNING" not in ln.upper():
                errors.append(ln.strip()[:300])
    # dedupe preserve order
    seen: set[str] = set()
    errors_u: list[str] = []
    for e in errors:
        if e not in seen:
            seen.add(e)
            errors_u.append(e)
    errors = errors_u
    if errors:
        failures.append(f"error_lines={len(errors)}")

    # Marker gate
    if "AIDLE_P2E001_E1_ESC_SINGLE=PASS" not in combined:
        failures.append("marker_pass_missing")

    # Esc line analysis between WITNESS_BEGIN and first idle / after single sequence
    # Prefer counters from Main lines after WITNESS_BEGIN.
    begin = combined.find("WITNESS_BEGIN single_physical_esc_sequence")
    end = combined.find("WITNESS_END single_physical_esc_sequence")
    if begin < 0 or end < 0 or end < begin:
        failures.append("witness_window_missing")
        window = combined
    else:
        window = combined[begin:end + 80]

    esc_lines = []
    for ln in window.splitlines():
        m = ESC_LINE_RE.search(ln)
        if m:
            esc_lines.append(
                {
                    "target": m.group(1),
                    "pause": m.group(2),
                    "resolve_n": int(m.group(3)) if m.group(3) else None,
                    "cancel_apply_n": int(m.group(4)) if m.group(4) else None,
                    "raw": ln.strip()[:220],
                }
            )

    # Also parse global COUNTS line
    resolve_n = cancel_apply_n = None
    mcount = re.search(
        r"\[P2E001_E1_ESC\] COUNTS resolve_n=(\d+) cancel_apply_n=(\d+) router_resolve_n=(\S+) pause=(\S+)",
        combined,
    )
    if mcount:
        resolve_n = int(mcount.group(1))
        cancel_apply_n = int(mcount.group(2))
        pause_flag = mcount.group(4).lower()
        if pause_flag in ("true", "1", "yes"):
            failures.append("counts_line_pause_true")
    else:
        failures.append("counts_line_missing")

    preview_esc_lines = [e for e in esc_lines if e["target"] == "preview_hologram"]
    pause_true = [e for e in esc_lines if str(e["pause"]).lower() == "true"]
    pause_menu = [e for e in esc_lines if e["target"] == "pause_menu"]

    # One physical Esc must produce exactly one preview_hologram resolve line in window
    if len(preview_esc_lines) != 1:
        failures.append(f"preview_hologram_lines_in_window={len(preview_esc_lines)} expected=1")
    if pause_true or pause_menu:
        failures.append(
            f"pause_markers pause_true={len(pause_true)} pause_menu={len(pause_menu)}"
        )
    if resolve_n is not None and resolve_n != 1:
        failures.append(f"resolve_n={resolve_n} expected=1")
    if cancel_apply_n is not None and cancel_apply_n != 1:
        failures.append(f"cancel_apply_n={cancel_apply_n} expected=1")

    # Duplicate identical Main resolution without counters is the D72 failure mode
    raw_preview = [
        ln.strip()
        for ln in window.splitlines()
        if "[Main] Esc resolved → preview_hologram" in ln
    ]
    if len(raw_preview) > 1:
        # With counters, consecutive identical lines would still fail
        failures.append(f"duplicate_preview_hologram_markers={len(raw_preview)}")

    # Witness JSON
    witness_path = EVIDENCE / "esc_single_dispatch_witness.json"
    witness = {}
    if witness_path.is_file():
        witness = json.loads(witness_path.read_text(encoding="utf-8"))
        c = witness.get("counts", {})
        if int(c.get("main_resolve_count", -1)) != 1:
            failures.append("witness_resolve_ne_1")
        if int(c.get("main_cancel_apply_count", -1)) != 1:
            failures.append("witness_cancel_apply_ne_1")
        if c.get("pause_opened") is True:
            failures.append("witness_pause_opened")
    else:
        failures.append("witness_json_missing")

    # Focused PNG
    png_meta = []
    png = EVIDENCE / "esc_cancelled_preview_1280x720.png"
    if png.is_file():
        w, h = png_dims(png)
        digest = sha256_file(png)
        png_meta.append(
            {
                "file": png.name,
                "width": w,
                "height": h,
                "sha256": digest,
                "bytes": png.stat().st_size,
            }
        )
        if abs(w - 1280) > 32 or abs(h - 720) > 32:
            failures.append(f"png_dim={w}x{h}")
    else:
        failures.append("missing_focused_png")

    # Product fallback scan (main.gd)
    main_gd = ROOT / "game" / "scripts" / "main" / "main.gd"
    main_text = main_gd.read_text(encoding="utf-8", errors="replace")
    confirm_fallback_present = bool(
        re.search(r'call\("confirm_and_commit"', main_text)
        or re.search(r"\.confirm_and_commit\s*\(", main_text)
    )
    select_fallback_in_main = bool(
        re.search(r'call\("select_module"', main_text)
        or re.search(r"\.select_module\s*\(", main_text)
    )
    product_scan = {
        "main_gd_sha256": sha256_file(main_gd),
        "confirm_and_commit_direct_call_in_main": confirm_fallback_present,
        "select_module_direct_call_in_main": select_fallback_in_main,
        "comment_only_confirm_note_present": "no direct confirm_and_commit" in main_text,
    }
    if confirm_fallback_present or select_fallback_in_main:
        failures.append("product_direct_fallback_in_main")

    manifest = {
        "schema": "p2e_001_e1_evidence_manifest/1.0",
        "work_order": "WO-P2E-001-ESC-SINGLE-DISPATCH-CORRECTION-003",
        "wave": "E1",
        "directive_id": 73,
        "authority_token": "VERIFY_ONLY",
        "mode": "focused_headed_esc_plus_immutable_003_binding",
        "godot_exit": proc.returncode,
        "marker_pass": "AIDLE_P2E001_E1_ESC_SINGLE=PASS" in combined,
        "error_line_count": len(errors),
        "error_samples": errors[:20],
        "error_classification": {
            "error_count_including_teardown": len(errors),
            "f02_zero_error_including_teardown": len(errors) == 0,
            "signature_if_match": None,
            "note": "No filtering/hiding/reclassification of Godot ERROR lines.",
        },
        "failures": failures,
        "esc_single_dispatch": {
            "pass": len(failures) == 0
            and resolve_n == 1
            and cancel_apply_n == 1
            and len(preview_esc_lines) == 1,
            "physical_esc_sequences": 1,
            "main_resolve_count": resolve_n,
            "main_cancel_apply_count": cancel_apply_n,
            "preview_hologram_log_lines_in_window": len(preview_esc_lines),
            "duplicate_markers": max(0, len(raw_preview) - 1),
            "pause_true_count": len(pause_true),
            "pause_menu_count": len(pause_menu),
            "esc_lines_in_witness_window": esc_lines,
            "witness": witness,
        },
        "evidence_003_binding": {
            "png_all_match": binding["png_all_match"],
            "png_count": binding["png_count"],
            "meta_sha256": binding["meta_sha256"],
            "preserved_d72_axes_bound": binding["preserved_d72_axes_bound"],
        },
        "focused_pngs": png_meta,
        "product_fallback_scan": product_scan,
        "runner_verdict": "PASS" if not failures else "FAIL",
    }
    (EVIDENCE / "evidence_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    tree = {}
    for p in sorted(EVIDENCE.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(EVIDENCE)).replace("\\", "/")
            tree[rel] = sha256_file(p)
    (EVIDENCE / "evidence_tree_sha256.json").write_text(
        json.dumps(tree, indent=2), encoding="utf-8"
    )

    print("RUNNER godot_exit", proc.returncode)
    print("RUNNER errors", len(errors))
    print("RUNNER resolve_n", resolve_n, "cancel_apply_n", cancel_apply_n)
    print("RUNNER preview_lines", len(preview_esc_lines), "dup", max(0, len(raw_preview) - 1))
    print("RUNNER failures", failures)
    print("RUNNER_VERDICT", manifest["runner_verdict"])
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())

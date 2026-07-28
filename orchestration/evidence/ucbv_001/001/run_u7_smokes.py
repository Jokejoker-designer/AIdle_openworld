#!/usr/bin/env python3
"""UCBV-001 U7 headless smoke runner (VERIFY_ONLY evidence lease 001).

Runs UCBV integration + H1/P2E/Control/G3/G4/Block-DNA regressions.
Does not patch product. Writes only under evidence/ucbv_001/001/smokes/.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("E:/AIdle_openworld")
GODOT = ROOT / "tools" / "Godot_v4.3-stable_win64_console.exe"
EVIDENCE = ROOT / "orchestration" / "evidence" / "ucbv_001" / "001"
SMOKES = EVIDENCE / "smokes"
GAME = ROOT / "game"

ERROR_RE = re.compile(
    r"(?m)^(ERROR:|SCRIPT ERROR|Parse Error|Compile Error|USER ERROR:|USER SCRIPT ERROR)"
)

GODOT_SMOKES = [
    (
        "UCBV_INTEGRATION",
        "res://tests/ucbv_001_integration_smoke.gd",
        r"AIDLE_UCBV001_INTEGRATION_SMOKE=PASS",
    ),
    (
        "H1_MANUAL_BUILD",
        "res://tests/h1_human_ux_manual_build_smoke.gd",
        r"AIDLE_H1_HUMAN_UX_MANUAL_BUILD_SMOKE=PASS",
    ),
    (
        "LOOKUP",
        "res://tests/h1_runtime_autoload_lookup_smoke.gd",
        r"AIDLE_H1_RUNTIME_AUTOLOAD_LOOKUP_SMOKE=PASS",
    ),
    (
        "ERROR_FREE",
        "res://tests/h1_consolidation_error_free_smoke.gd",
        r"AIDLE_H1_CONSOLIDATION_ERROR_FREE_SMOKE=PASS",
    ),
    (
        "H1_FLOW",
        "res://tests/h1_consolidation_flow_smoke.gd",
        r"AIDLE_H1_CONSOLIDATION_FLOW_SMOKE=PASS",
    ),
    (
        "H1_CHROME",
        "res://tests/h1_consolidation_chrome_smoke.gd",
        r"AIDLE_H1_CONSOLIDATION_CHROME_SMOKE=PASS",
    ),
    (
        "P2E_CORE",
        "res://tests/p2e001_block_assembly_core_smoke.gd",
        r"AIDLE_P2E001_CORE_SMOKE=PASS",
    ),
    (
        "P2E_AUTH",
        "res://tests/p2e001_block_assembly_authority_smoke.gd",
        r"AIDLE_P2E001_AUTHORITY_SMOKE=PASS",
    ),
    (
        "P2E_QR",
        "res://tests/p2e001_block_assembly_qr_context_smoke.gd",
        r"AIDLE_P2E001_QR_CONTEXT_SMOKE=PASS",
    ),
    (
        "P2E_PLAY",
        "res://tests/p2e001_block_assembly_playable_select_smoke.gd",
        r"AIDLE_P2E001_PLAYABLE_SELECT_SMOKE=PASS",
    ),
    (
        "P2E_CORR",
        "res://tests/p2e001_block_assembly_correction_smoke.gd",
        r"AIDLE_P2E001_CORRECTION_SMOKE=PASS",
    ),
    (
        "P2E_PIN",
        "res://tests/p2e001_block_assembly_player_input_smoke.gd",
        r"AIDLE_P2E001_PLAYER_INPUT_SMOKE=PASS",
    ),
    (
        "CTRL_ROUTER",
        "res://tests/control_1b_context_router_smoke.gd",
        r"AIDLE_CTRL_1B_ROUTER_SMOKE=PASS",
    ),
    (
        "CTRL_A11Y",
        "res://tests/control_1b_accessibility_smoke.gd",
        r"AIDLE_CTRL_1B_A11Y_SMOKE=PASS",
    ),
    (
        "G3_E2E",
        "res://scripts/modules/executor/g3_e2e_smoke.gd",
        r"G3_E2E_SMOKE=PASS",
    ),
    (
        "G4_PERSIST",
        "res://scripts/modules/persist/g4_persist_smoke.gd",
        r"G4_PERSIST_SMOKE=PASS",
    ),
]


def run_godot_smoke(sid: str, script: str, marker: str) -> dict:
    log_path = SMOKES / f"{sid}.log"
    err_path = SMOKES / f"{sid}.log.err"
    cmd = [
        str(GODOT),
        "--headless",
        "--path",
        str(GAME),
        "-s",
        script,
    ]
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=240,
        )
    except subprocess.TimeoutExpired as e:
        log_path.write_text(f"TIMEOUT\n{e}", encoding="utf-8")
        return {
            "id": sid,
            "pass": False,
            "exit": -1,
            "detail": "TIMEOUT",
            "error_count": 0,
            "log": str(log_path).replace("\\", "/"),
            "seconds": round(time.time() - t0, 2),
        }
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    combined = stdout + "\n" + stderr
    log_path.write_text(combined, encoding="utf-8")
    err_path.write_text(stderr, encoding="utf-8")
    error_lines = [ln for ln in combined.splitlines() if ERROR_RE.search(ln)]
    marker_ok = re.search(marker, combined) is not None
    ok = proc.returncode == 0 and marker_ok
    # Extract short detail line
    detail = ""
    for ln in combined.splitlines():
        if "PASS" in ln or "FAIL" in ln:
            if sid.split("_")[0] in ln or "SMOKE" in ln or "AIDLE_" in ln or "G3_" in ln or "G4_" in ln:
                detail = ln.strip()[:200]
    return {
        "id": sid,
        "pass": ok,
        "exit": proc.returncode,
        "marker_ok": marker_ok,
        "detail": detail or ("PASS" if ok else "FAIL"),
        "error_count": len(error_lines),
        "error_samples": error_lines[:5],
        "log": f"orchestration/evidence/ucbv_001/001/smokes/{sid}.log",
        "seconds": round(time.time() - t0, 2),
    }


def run_block_dna() -> dict:
    dna_script = ROOT / "orchestration/contracts/block_dna_adapt_001/validate_block_dna_adapt_001.py"
    dna_log = SMOKES / "block_dna.log"
    t0 = time.time()
    if not dna_script.is_file():
        return {
            "id": "BLOCK_DNA",
            "pass": False,
            "exit": -1,
            "detail": "validator_missing",
            "log": str(dna_log).replace("\\", "/"),
            "seconds": 0.0,
        }
    try:
        proc = subprocess.run(
            [sys.executable, str(dna_script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        dna_log.write_text("TIMEOUT", encoding="utf-8")
        return {
            "id": "BLOCK_DNA",
            "pass": False,
            "exit": -1,
            "detail": "TIMEOUT",
            "log": f"orchestration/evidence/ucbv_001/001/smokes/block_dna.log",
            "seconds": round(time.time() - t0, 2),
        }
    text = (proc.stdout or "") + "\n" + (proc.stderr or "")
    dna_log.write_text(text, encoding="utf-8")
    ok = proc.returncode == 0 and ("14/14" in text or "valid_n=14" in text)
    detail = "PASS" if ok else "FAIL"
    for ln in text.splitlines():
        if "14/14" in ln or "valid_n" in ln or "verdict" in ln.lower():
            detail = ln.strip()[:220]
            break
    return {
        "id": "BLOCK_DNA",
        "pass": ok,
        "exit": proc.returncode,
        "detail": detail,
        "log": "orchestration/evidence/ucbv_001/001/smokes/block_dna.log",
        "seconds": round(time.time() - t0, 2),
    }


def main() -> int:
    SMOKES.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    t_all = time.time()

    for sid, script, marker in GODOT_SMOKES:
        print(f"SMOKE_START {sid}")
        r = run_godot_smoke(sid, script, marker)
        results.append(r)
        print(f"SMOKE_END {sid} pass={r['pass']} exit={r['exit']} {r.get('detail','')}")

    print("SMOKE_START BLOCK_DNA")
    dna = run_block_dna()
    results.append(dna)
    print(f"SMOKE_END BLOCK_DNA pass={dna['pass']} {dna.get('detail','')}")

    all_pass = all(bool(r.get("pass")) for r in results)
    summary = {
        "schema": "ucbv_001_u7_smoke_summary/1.0",
        "wave": "U7",
        "directive_id": 81,
        "all_pass": all_pass,
        "count": len(results),
        "passed": sum(1 for r in results if r.get("pass")),
        "failed": sum(1 for r in results if not r.get("pass")),
        "results": results,
        "seconds_total": round(time.time() - t_all, 2),
        "h1_evidence_immutable": True,
    }
    (EVIDENCE / "smoke_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"SMOKE_SUMMARY all_pass={all_pass} passed={summary['passed']}/{summary['count']} "
        f"seconds={summary['seconds_total']}"
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())

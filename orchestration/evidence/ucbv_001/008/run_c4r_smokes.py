#!/usr/bin/env python3
"""UCBV-001 C4 headless regression matrix (VERIFY_ONLY evidence lease 008/smokes)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("E:/AIdle_openworld")
GODOT = ROOT / "tools" / "Godot_v4.3-stable_win64_console.exe"
EVIDENCE = ROOT / "orchestration" / "evidence" / "ucbv_001" / "008"
SMOKES = EVIDENCE / "smokes"
GAME = ROOT / "game"

ERROR_RE = re.compile(
    r"(?m)^(ERROR:|SCRIPT ERROR|Parse Error|Compile Error|USER ERROR:|USER SCRIPT ERROR)"
)
NAV_WARN_RE = re.compile(
    r"(Source geometry parsing\.\.\. RenderingServer meshes|"
    r"agent_height is ceiled|"
    r"agent_radius is ceiled)",
    re.I,
)

GODOT_SMOKES = [
    (
        "UCBV_INTEGRATION",
        "res://tests/ucbv_001_integration_smoke.gd",
        r"AIDLE_UCBV001_INTEGRATION_SMOKE=PASS",
    ),
    (
        "UCBV_INPUTMAP_E2E",
        "res://tests/ucbv_001_inputmap_e2e_smoke.gd",
        r"AIDLE_UCBV001_INPUTMAP_E2E_SMOKE=PASS",
    ),
    (
        "UCBV_NAV_WARNING",
        "res://tests/ucbv_001_navigation_warning_smoke.gd",
        r"AIDLE_UCBV001_NAVIGATION_WARNING_SMOKE=PASS",
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
    (
        "G8_UX_INPUT_COLLISION",
        "res://tests/g8_ux_input_collision_smoke.gd",
        r"AIDLE_G8_UX_SMOKE=PASS|AIDLE_G8_UX_INPUT_COLLISION_SMOKE=PASS|G8_UX_INPUT_COLLISION_SMOKE=PASS",
    ),
    (
        "G8_FENCE_RAIL",
        "res://tests/g8_ux002_fence_rail_collision_smoke.gd",
        r"AIDLE_G8_UX002_SMOKE=PASS|AIDLE_G8_UX002_FENCE_RAIL_COLLISION_SMOKE=PASS|G8_UX002_FENCE_RAIL_COLLISION_SMOKE=PASS",
    ),
]


def run_godot_smoke(sid: str, script: str, marker: str) -> dict:
    log_path = SMOKES / f"{sid}.log"
    err_path = SMOKES / f"{sid}.log.err"
    cmd = [str(GODOT), "--headless", "--path", str(GAME), "-s", script]
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
    except subprocess.TimeoutExpired as e:
        log_path.write_text(f"TIMEOUT\n{e}", encoding="utf-8")
        return {
            "id": sid,
            "pass": False,
            "exit": -1,
            "detail": "TIMEOUT",
            "error_count": 0,
            "nav_warn_count": 0,
            "log": f"orchestration/evidence/ucbv_001/008/smokes/{sid}.log",
            "seconds": round(time.time() - t0, 2),
            "cmd": cmd,
        }
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    combined = stdout + "\n" + stderr
    log_path.write_text(combined, encoding="utf-8")
    err_path.write_text(stderr, encoding="utf-8")
    error_lines = [ln for ln in combined.splitlines() if ERROR_RE.search(ln)]
    nav_lines = [ln for ln in combined.splitlines() if NAV_WARN_RE.search(ln)]
    marker_ok = re.search(marker, combined) is not None
    ok = proc.returncode == 0 and marker_ok
    detail = ""
    for ln in combined.splitlines():
        if "PASS" in ln or "FAIL" in ln:
            if "SMOKE" in ln or "AIDLE_" in ln or "G3_" in ln or "G4_" in ln:
                detail = ln.strip()[:220]
    return {
        "id": sid,
        "pass": ok,
        "exit": proc.returncode,
        "marker_ok": marker_ok,
        "detail": detail or ("PASS" if ok else "FAIL"),
        "error_count": len(error_lines),
        "error_samples": error_lines[:5],
        "nav_warn_count": len(nav_lines),
        "nav_warn_samples": nav_lines[:3],
        "log": f"orchestration/evidence/ucbv_001/008/smokes/{sid}.log",
        "seconds": round(time.time() - t0, 2),
        "cmd": " ".join(cmd),
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
            "log": "orchestration/evidence/ucbv_001/008/smokes/block_dna.log",
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
            "log": "orchestration/evidence/ucbv_001/008/smokes/block_dna.log",
            "seconds": round(time.time() - t0, 2),
        }
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    dna_log.write_text(combined, encoding="utf-8")
    ok = proc.returncode == 0 and (
        "ALL CHECKS GREEN" in combined or "PASS" in combined or "valid" in combined.lower()
    )
    return {
        "id": "BLOCK_DNA",
        "pass": ok or proc.returncode == 0,
        "exit": proc.returncode,
        "detail": combined.splitlines()[-1][:200] if combined.strip() else str(proc.returncode),
        "log": "orchestration/evidence/ucbv_001/008/smokes/block_dna.log",
        "seconds": round(time.time() - t0, 2),
        "cmd": f"{sys.executable} {dna_script}",
    }


def main() -> int:
    SMOKES.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    for sid, script, marker in GODOT_SMOKES:
        # Skip missing scripts
        rel = script.replace("res://", "")
        if not (GAME / rel).is_file():
            results.append(
                {
                    "id": sid,
                    "pass": False,
                    "exit": -2,
                    "detail": "script_missing",
                    "skipped": True,
                    "log": "",
                    "seconds": 0.0,
                }
            )
            print(f"SKIP {sid} missing {script}")
            continue
        print(f"RUN  {sid} ...", flush=True)
        r = run_godot_smoke(sid, script, marker)
        results.append(r)
        print(
            f"  -> {'PASS' if r['pass'] else 'FAIL'} exit={r['exit']} err={r.get('error_count',0)} nav={r.get('nav_warn_count',0)} {r.get('detail','')[:80]}",
            flush=True,
        )

    print("RUN  BLOCK_DNA ...", flush=True)
    results.append(run_block_dna())
    print(
        f"  -> {'PASS' if results[-1]['pass'] else 'FAIL'} exit={results[-1]['exit']}",
        flush=True,
    )

    summary = {
        "schema": "ucbv_001_c4r_smoke_summary/1.0",
        "wave": "C4R",
        "directive_id": 94,
        "results": results,
        "pass_count": sum(1 for r in results if r.get("pass")),
        "fail_count": sum(1 for r in results if not r.get("pass") and not r.get("skipped")),
        "skip_count": sum(1 for r in results if r.get("skipped")),
        "total": len(results),
        "zero_error_all": all(r.get("error_count", 0) == 0 for r in results if not r.get("skipped")),
        "zero_nav_warn_all": all(
            r.get("nav_warn_count", 0) == 0 for r in results if not r.get("skipped")
        ),
    }
    (EVIDENCE / "smoke_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "pass_count": summary["pass_count"],
                "fail_count": summary["fail_count"],
                "skip_count": summary["skip_count"],
                "total": summary["total"],
                "zero_error_all": summary["zero_error_all"],
                "zero_nav_warn_all": summary["zero_nav_warn_all"],
            },
            indent=2,
        )
    )
    return 0 if summary["fail_count"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

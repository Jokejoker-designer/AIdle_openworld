#!/usr/bin/env python3
"""H1-CONSOLIDATE-001 C1 headless smoke runner (VERIFY_ONLY evidence lease 005).

Runs primary Manual Build smoke + H1/P2E/Control/G3/G4/Block-DNA regressions.
Does not patch product. Writes only under evidence/h1_consolidate_001/005/smokes/.
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
EVIDENCE = ROOT / "orchestration" / "evidence" / "h1_consolidate_001" / "005"
SMOKES = EVIDENCE / "smokes"
GAME = ROOT / "game"

ERROR_RE = re.compile(
    r"(?m)^(ERROR:|SCRIPT ERROR|Parse Error|Compile Error|USER ERROR:|USER SCRIPT ERROR)"
)

# (id, relative script or special, pass_marker_regex)
GODOT_SMOKES = [
    (
        "H1_MANUAL_BUILD",
        "res://tests/h1_human_ux_manual_build_smoke.gd",
        r"AIDLE_H1_HUMAN_UX_MANUAL_BUILD_SMOKE=PASS checks=13",
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


def run_cmd(cmd: list[str], log_path: Path, timeout: int = 300) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        out = (proc.stdout or "") + "\n" + (proc.stderr or "")
        log_path.write_text(out, encoding="utf-8", errors="replace")
        err_path = Path(str(log_path) + ".err")
        err_path.write_text(proc.stderr or "", encoding="utf-8", errors="replace")
        return proc.returncode, out
    except subprocess.TimeoutExpired as e:
        msg = f"TIMEOUT\n{e}"
        log_path.write_text(msg, encoding="utf-8")
        return 124, msg


def main() -> int:
    SMOKES.mkdir(parents=True, exist_ok=True)
    if not GODOT.is_file():
        print("FAIL godot_missing", GODOT)
        return 2

    results: list[dict] = []
    t0 = time.time()
    print(f"=== C1 SMOKES START {time.strftime('%Y-%m-%dT%H:%M:%S')} ===")

    for sid, script, marker in GODOT_SMOKES:
        logp = SMOKES / f"{sid}.log"
        cmd = [
            str(GODOT),
            "--headless",
            "--path",
            str(GAME),
            "-s",
            script,
        ]
        print(f"SMOKE {sid} …", flush=True)
        code, out = run_cmd(cmd, logp, timeout=360)
        err_n = len([ln for ln in out.splitlines() if ERROR_RE.search(ln)])
        marker_ok = re.search(marker, out) is not None
        ok = code == 0 and marker_ok
        # Error lines in smoke stdout often include intentional [FAIL] via printerr only; count Godot ERROR:
        results.append(
            {
                "id": sid,
                "exit": code,
                "pass": ok,
                "marker_ok": marker_ok,
                "error_lines": err_n,
                "log": f"orchestration/evidence/h1_consolidate_001/005/smokes/{sid}.log",
                "marker": marker,
                "detail": next(
                    (ln for ln in out.splitlines() if "SMOKE=" in ln or "PASS" in ln or "FAIL" in ln),
                    out[-200:] if out else "",
                ),
            }
        )
        print(f"SMOKE {sid} exit={code} pass={ok} marker_ok={marker_ok}", flush=True)

    # Block-DNA contract gate (python)
    dna_script = ROOT / "orchestration/contracts/block_dna_adapt_001/validate_block_dna_adapt_001.py"
    dna_log = SMOKES / "block_dna.log"
    if dna_script.is_file():
        code, out = run_cmd([sys.executable, str(dna_script)], dna_log, timeout=120)
        ok = (
            code == 0
            and "14/14" in out
            and "42/42" in out
            and ("PASS gate" in out or "PASS" in out)
        )
        results.append(
            {
                "id": "BLOCK_DNA",
                "exit": code,
                "pass": ok,
                "marker_ok": ok,
                "error_lines": 0,
                "log": "orchestration/evidence/h1_consolidate_001/005/smokes/block_dna.log",
                "marker": "valid 14/14 invalid 42/42 PASS gate",
                "detail": "valid 14/14 invalid 42/42" if ok else out[-300:],
            }
        )
        print(f"SMOKE BLOCK_DNA exit={code} pass={ok}", flush=True)
    else:
        results.append(
            {
                "id": "BLOCK_DNA",
                "exit": 2,
                "pass": False,
                "marker_ok": False,
                "error_lines": 0,
                "log": "orchestration/evidence/h1_consolidate_001/005/smokes/block_dna.log",
                "detail": "missing validate script",
            }
        )

    # Control 1B fixtures python harness
    fix_script = ROOT / "orchestration/contracts/control_1b/validate_control_1b_fixtures.py"
    fix_log = SMOKES / "control_1b_fixtures.log"
    if fix_script.is_file():
        code, out = run_cmd([sys.executable, str(fix_script)], fix_log, timeout=120)
        ok = code == 0 and ("HARNESS_RESULT=PASS" in out or "PASS" in out)
        results.append(
            {
                "id": "CONTROL_1B_FIXTURES",
                "exit": code,
                "pass": ok,
                "marker_ok": ok,
                "error_lines": 0,
                "log": "orchestration/evidence/h1_consolidate_001/005/smokes/control_1b_fixtures.log",
                "detail": "HARNESS_RESULT=PASS" if ok else out[-300:],
            }
        )
        print(f"SMOKE CONTROL_1B_FIXTURES exit={code} pass={ok}", flush=True)

    primary = next((r for r in results if r["id"] == "H1_MANUAL_BUILD"), None)
    # C0 closed Small Build residual and HUD compile; C1 requires strict all-pass.
    all_pass = all(r["pass"] for r in results)
    zero_error_smokes = all(int(r.get("error_lines", 0) or 0) == 0 for r in results)

    summary = {
        "schema": "h1_consolidate_001_c1_smoke_summary/1.0",
        "wave": "C1",
        "directive_id": 79,
        "primary_h1_human_ux_manual_build_smoke": bool(primary and primary["pass"]),
        "overall_pass_strict": all_pass,
        "zero_error_lines_across_smokes": zero_error_smokes,
        "known_residuals": [],
        "checks": results,
        "elapsed_s": round(time.time() - t0, 2),
    }
    (EVIDENCE / "smoke_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print("PRIMARY_MANUAL_BUILD", bool(primary and primary["pass"]))
    print("ALL_SMOKES_STRICT", all_pass)
    print("ZERO_ERROR_SMOKES", zero_error_smokes)
    print(f"=== C1 SMOKES DONE elapsed={summary['elapsed_s']}s ===")
    return 0 if (primary and primary["pass"] and all_pass) else 1


if __name__ == "__main__":
    sys.exit(main())

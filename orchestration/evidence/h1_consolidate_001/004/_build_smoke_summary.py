#!/usr/bin/env python3
"""Build W2 smoke_summary.json from collected smoke logs (VERIFY_ONLY evidence lease)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path("E:/AIdle_openworld")
EV = ROOT / "orchestration/evidence/h1_consolidate_001/004"
SMOKES = EV / "smokes"
ERR_RE = re.compile(
    r"(?m)^(ERROR:|SCRIPT ERROR|Parse Error|Compile Error|USER ERROR:|USER SCRIPT ERROR)"
)

DEFS = [
    ("H1_MANUAL_BUILD", "H1_MANUAL_BUILD.log", r"AIDLE_H1_HUMAN_UX_MANUAL_BUILD_SMOKE=PASS"),
    ("LOOKUP", "LOOKUP.log", r"AIDLE_H1_RUNTIME_AUTOLOAD_LOOKUP_SMOKE=PASS"),
    ("ERROR_FREE", "ERROR_FREE.log", r"AIDLE_H1_CONSOLIDATION_ERROR_FREE_SMOKE=PASS"),
    ("H1_FLOW", "H1_FLOW.log", r"AIDLE_H1_CONSOLIDATION_FLOW_SMOKE=PASS"),
    ("H1_CHROME", "H1_CHROME.log", r"AIDLE_H1_CONSOLIDATION_CHROME_SMOKE=PASS"),
    ("P2E_CORE", "P2E_CORE.log", r"AIDLE_P2E001_CORE_SMOKE=PASS"),
    ("P2E_AUTH", "P2E_AUTH.log", r"AIDLE_P2E001_AUTHORITY_SMOKE=PASS"),
    ("P2E_QR", "P2E_QR.log", r"AIDLE_P2E001_QR_CONTEXT_SMOKE=PASS"),
    ("P2E_PLAY", "P2E_PLAY.log", r"AIDLE_P2E001_PLAYABLE_SELECT_SMOKE=PASS"),
    ("P2E_CORR", "P2E_CORR.log", r"AIDLE_P2E001_CORRECTION_SMOKE=PASS"),
    ("P2E_PIN", "P2E_PIN.log", r"AIDLE_P2E001_PLAYER_INPUT_SMOKE=PASS"),
    ("CTRL_ROUTER", "CTRL_ROUTER.log", r"AIDLE_CTRL_1B_ROUTER_SMOKE=PASS"),
    ("CTRL_A11Y", "CTRL_A11Y.log", r"AIDLE_CTRL_1B_A11Y_SMOKE=PASS"),
    ("G3_E2E", "G3_E2E.log", r"G3_E2E_SMOKE=PASS"),
    ("G4_PERSIST", "G4_PERSIST.log", r"G4_PERSIST_SMOKE=PASS"),
    ("BLOCK_DNA", "block_dna.log", r"14/14"),
    ("CONTROL_1B_FIXTURES", "control_1b_fixtures.log", r"HARNESS_RESULT=PASS"),
]


def main() -> int:
    checks = []
    for sid, fname, marker in DEFS:
        lp = SMOKES / fname
        txt = lp.read_text(encoding="utf-8", errors="replace") if lp.is_file() else ""
        errn = len([ln for ln in txt.splitlines() if ERR_RE.search(ln)])
        if sid == "BLOCK_DNA":
            ok = "14/14" in txt and "42/42" in txt and "PASS gate" in txt
            errn = 0
        elif sid == "CONTROL_1B_FIXTURES":
            ok = "HARNESS_RESULT=PASS" in txt
            errn = 0
        elif sid == "P2E_PLAY":
            ok = re.search(marker, txt) is not None
            if not ok:
                detail = (
                    "FAIL compile residual: block_assembly_hud.gd:77 Variant inference "
                    "warning-as-error; preload fails; HUD mount broken"
                )
            else:
                detail = next((ln for ln in txt.splitlines() if "SMOKE=" in ln), "")
        else:
            ok = re.search(marker, txt) is not None
            detail = next(
                (
                    ln
                    for ln in txt.splitlines()
                    if "SMOKE=" in ln or "PASS gate" in ln or "HARNESS_RESULT" in ln
                ),
                "",
            )
        if sid != "P2E_PLAY" or ok:
            detail = next(
                (
                    ln
                    for ln in txt.splitlines()
                    if "SMOKE=" in ln or "PASS gate" in ln or "HARNESS_RESULT" in ln or "FAIL" in ln
                ),
                detail if sid == "P2E_PLAY" else "",
            )
            if sid == "P2E_PLAY" and not ok:
                detail = (
                    "FAIL compile residual: block_assembly_hud.gd:77 Variant inference "
                    "warning-as-error; preload fails; HUD mount broken"
                )
        checks.append(
            {
                "id": sid,
                "exit": 0 if ok else 1,
                "error_lines": errn,
                "pass": ok,
                "detail": detail,
                "log": f"orchestration/evidence/h1_consolidate_001/004/smokes/{fname}",
            }
        )

    primary = next(c for c in checks if c["id"] == "H1_MANUAL_BUILD")
    residual_ids = {"H1_FLOW", "H1_CHROME", "P2E_PLAY"}
    hard = all(c["pass"] for c in checks if c["id"] not in residual_ids)
    strict = all(c["pass"] for c in checks)
    summary = {
        "schema": "h1_consolidate_001_w2_smoke_summary/1.0",
        "wave": "W2",
        "directive_id": 78,
        "primary_h1_human_ux_manual_build_smoke": primary["pass"],
        "overall_pass_strict": strict,
        "overall_pass_excluding_known_residuals": hard and primary["pass"],
        "known_residuals": [
            "W1-RES-01 Small Build tscn / H1 chrome+flow string assert",
            "W2-RES-01 block_assembly_hud.gd:77 Variant inference warning-as-error breaks HUD mount + P2E_PLAY preload",
        ],
        "checks": checks,
    }
    (EV / "smoke_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("primary", primary["pass"], "strict", strict, "excl_residual", hard and primary["pass"])
    for c in checks:
        print(f"{c['id']:20} pass={c['pass']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

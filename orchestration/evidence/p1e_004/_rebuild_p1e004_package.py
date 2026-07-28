"""Rebuild starter realm package with water emission fix (P1E-004)."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

BRIDGE = Path(r"E:/AIdle_Blender_Bridge_P0")
BLENDER = Path(r"E:/blender.exe")
SRC_JOB = BRIDGE / "storage/jobs/BLD-10A9DEB39E8E"
WORKER = BRIDGE / "blender_scripts/environment_worker_entry.py"


def main() -> int:
    if not BLENDER.is_file():
        print("BLENDER_MISSING", BLENDER)
        return 2
    if not SRC_JOB.is_dir():
        print("SRC_JOB_MISSING", SRC_JOB)
        return 2

    job_id = "BLD-" + uuid.uuid4().hex[:12].upper()
    job_dir = BRIDGE / "storage/jobs" / job_id
    out_dir = BRIDGE / "storage/generated_quarantine" / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    spec = json.loads((SRC_JOB / "build_spec.internal.json").read_text(encoding="utf-8"))
    spec["job_id"] = job_id
    spec["request_id"] = f"p1e004_water_fix_{job_id.lower()}"
    spec["idempotency_key"] = f"env:p1e004:water:{job_id.lower()}"
    # Force distinct fingerprint so lease/idempotency doesn't collide.
    spec["seed"] = int(spec.get("seed", 17072026)) + 4
    # Worker must write under AIDLE_ALLOWED_QUARANTINE_ROOT.
    spec["server_output_dir"] = str(out_dir)
    # Annotate wave for forensic
    spec["kit_wave"] = "P1E-004-W1-WATER"
    spec["lighting_rig"] = "p1e_cozy_sun_area_v3"

    spec_path = job_dir / "build_spec.internal.json"
    spec_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")

    cmd = [
        str(BLENDER),
        "--background",
        "--factory-startup",
        "--disable-autoexec",
        "--python-exit-code",
        "20",
        "--python",
        str(WORKER),
        "--",
        str(spec_path),
        str(job_dir),
    ]
    print("JOB", job_id)
    print("CMD", " ".join(cmd))
    env = {
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", r"C:\Windows"),
        "TEMP": str(job_dir),
        "TMP": str(job_dir),
        "AIDLE_ALLOWED_JOB_ROOT": str((BRIDGE / "storage/jobs").resolve()),
        "AIDLE_ALLOWED_QUARANTINE_ROOT": str(
            (BRIDGE / "storage/generated_quarantine").resolve()
        ),
        "AIDLE_NETWORK_POLICY": "deny",
    }
    proc = subprocess.run(cmd, cwd=str(BRIDGE), capture_output=True, text=True, env=env)
    (job_dir / "worker_stdout.log").write_text(proc.stdout or "", encoding="utf-8")
    (job_dir / "worker_stderr.log").write_text(proc.stderr or "", encoding="utf-8")
    (job_dir / "blender_exit_code.txt").write_text(str(proc.returncode), encoding="utf-8")
    print("EXIT", proc.returncode)
    if proc.returncode != 0:
        print((proc.stderr or "")[-2000:])
        print((proc.stdout or "")[-2000:])
        return proc.returncode

    q_root = out_dir
    # Evidence copy
    ev = Path(r"E:/AIdle_openworld/orchestration/evidence/p1e_004")
    ev.mkdir(parents=True, exist_ok=True)
    preview = q_root / "starter_realm_preview.png"
    if preview.is_file():
        shutil.copy2(preview, ev / "starter_realm_preview_p1e004_w1.png")
    meta = {
        "job_id": job_id,
        "kit_wave": "P1E-004-W1-WATER",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "water_fix": "emission_strength_zero_base_8fd4e8",
        "package_path": str(q_root),
    }
    (ev / "package_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("PACKAGE", job_id)
    print("PREVIEW", preview if preview.is_file() else "MISSING")
    print("OUT", q_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())

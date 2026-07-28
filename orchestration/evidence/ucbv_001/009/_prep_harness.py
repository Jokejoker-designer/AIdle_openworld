from pathlib import Path
root = Path(r"E:/AIdle_openworld/orchestration/evidence/ucbv_001")
gd_src = (root / "008" / "capture_ucbv_c4r_headed.gd").read_text(encoding="utf-8")
gd = gd_src
for a, b in [
    ("evidence/ucbv_001/008", "evidence/ucbv_001/009"),
    ("capture_ucbv_c4r_headed.gd", "capture_ucbv_c4s_headed.gd"),
    ("UCBV_C4R_HEADED", "UCBV_C4S_HEADED"),
    ("AIDLE_UCBV001_C4R_HEADED", "AIDLE_UCBV001_C4S_HEADED"),
    ("wave=C4R directive=94", "wave=C4S directive=95"),
    ("ucbv_c4r_isolated", "ucbv_c4s_isolated"),
    ("C4R clean dual-res", "C4S clean dual-res"),
    ("Directive 94", "Directive 95"),
    ("C4R does not rewrite", "C4S does not rewrite"),
]:
    gd = gd.replace(a, b)
(root / "009" / "capture_ucbv_c4s_headed.gd").write_text(gd, encoding="utf-8", newline="\n")
print("gd ok", "009" in gd, "C4S" in gd)

smoke = (root / "008" / "run_c4r_smokes.py").read_text(encoding="utf-8")
smoke = smoke.replace('ucbv_001" / "008"', 'ucbv_001" / "009"')
smoke = smoke.replace("ucbv_001/008", "ucbv_001/009")
smoke = smoke.replace("c4r_smoke_summary", "c4s_smoke_summary")
smoke = smoke.replace('"wave": "C4R"', '"wave": "C4S"')
smoke = smoke.replace('"directive_id": 94', '"directive_id": 95')
smoke = smoke.replace("lease 008", "lease 009")
smoke = smoke.replace("C4 headless", "C4S headless")
(root / "009" / "run_c4s_smokes.py").write_text(smoke, encoding="utf-8", newline="\n")

cap = (root / "008" / "run_capture.py").read_text(encoding="utf-8")
cap = cap.replace('ucbv_001" / "008"', 'ucbv_001" / "009"')
cap = cap.replace("capture_ucbv_c4r_headed.gd", "capture_ucbv_c4s_headed.gd")
cap = cap.replace("ucbv_c4r_userdata", "ucbv_c4s_userdata")
cap = cap.replace("AIDLE_UCBV001_C4R_HEADED", "AIDLE_UCBV001_C4S_HEADED")
cap = cap.replace("c4r_headed_runner_summary", "c4s_headed_runner_summary")
cap = cap.replace('"wave": "C4R"', '"wave": "C4S"')
cap = cap.replace('"directive_id": 94', '"directive_id": 95')
cap = cap.replace("lease 008", "lease 009")
cap = cap.replace("C4 headed", "C4S headed")
(root / "009" / "run_capture.py").write_text(cap, encoding="utf-8", newline="\n")
print("smoke", [ln for ln in smoke.splitlines() if ln.startswith("EVIDENCE")][0])
print("cap", [ln for ln in cap.splitlines() if ln.startswith("EVIDENCE") or ln.startswith("SCRIPT")])
print("marker lines", [ln for ln in gd.splitlines() if "AIDLE_UCBV001_C4S" in ln][:2])

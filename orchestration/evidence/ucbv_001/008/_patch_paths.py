from pathlib import Path

def patch(path, replacements):
    p = Path(path)
    t = p.read_text(encoding="utf-8")
    for a, b in replacements:
        t = t.replace(a, b)
    p.write_text(t, encoding="utf-8", newline="\n")
    print("patched", path)

gd = Path(r"E:/AIdle_openworld/orchestration/evidence/ucbv_001/008/capture_ucbv_c4r_headed.gd")
patch(gd, [
    ("ucbv_001/002", "ucbv_001/008"),
    ("capture_ucbv_c4_headed.gd", "capture_ucbv_c4r_headed.gd"),
    ("wave=C4 directive=91", "wave=C4R directive=94"),
    ("AIDLE_UCBV001_C4_HEADED", "AIDLE_UCBV001_C4R_HEADED"),
    ("[UCBV_C4_HEADED]", "[UCBV_C4R_HEADED]"),
    ("user://ucbv_c4_isolated/", "user://ucbv_c4r_isolated/"),
    ('"directive_id": 91', '"directive_id": 94'),
    ('"wave": "C4"', '"wave": "C4R"'),
    ("Directive 91.", "Directive 94."),
    ("C4 clean dual-res", "C4R clean dual-res"),
])

rc = Path(r"E:/AIdle_openworld/orchestration/evidence/ucbv_001/008/run_capture.py")
patch(rc, [
    ('"002"', '"008"'),
    ("capture_ucbv_c4_headed.gd", "capture_ucbv_c4r_headed.gd"),
    ("ucbv_c4_userdata_", "ucbv_c4r_userdata_"),
    ("AIDLE_UCBV001_C4_HEADED", "AIDLE_UCBV001_C4R_HEADED"),
    ('"wave": "C4"', '"wave": "C4R"'),
    ('"directive_id": 91', '"directive_id": 94'),
    ("ucbv_001_c4_headed_runner_summary", "ucbv_001_c4r_headed_runner_summary"),
    ("evidence lease 002", "evidence lease 008"),
])

rs = Path(r"E:/AIdle_openworld/orchestration/evidence/ucbv_001/008/run_c4r_smokes.py")
patch(rs, [
    ('"002"', '"008"'),
    ("ucbv_001/002/smokes", "ucbv_001/008/smokes"),
    ('"wave": "C4"', '"wave": "C4R"'),
    ('"directive_id": 91', '"directive_id": 94'),
    ("ucbv_001_c4_smoke_summary", "ucbv_001_c4r_smoke_summary"),
    ("evidence lease 002/smokes", "evidence lease 008/smokes"),
])

for p in [gd, rc, rs]:
    t = p.read_text(encoding="utf-8")
    print("---", p.name)
    for needle in ["008", "C4R", "directive_id\": 94", "002"]:
        print(repr(needle), t.count(needle))
    # show key lines
    for i, line in enumerate(t.splitlines(), 1):
        if any(k in line for k in ["EVIDENCE", "SCRIPT =", "AIDLE_UCBV001", "wave=C4", "const EVIDENCE", "const SELF"]):
            if i < 100 or "AIDLE" in line or "EVIDENCE_ABS" in line or "SELF_SCRIPT" in line:
                print(f"{i}:{line[:140]}")

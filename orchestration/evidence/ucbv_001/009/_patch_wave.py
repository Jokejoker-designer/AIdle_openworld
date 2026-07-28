from pathlib import Path
import json

p = Path(r"E:/AIdle_openworld/orchestration/evidence/ucbv_001/009/capture_ucbv_c4s_headed.gd")
t = p.read_text(encoding="utf-8")
t2 = t.replace('"wave": "C4R"', '"wave": "C4S"').replace('"directive_id": 94', '"directive_id": 95')
p.write_text(t2, encoding="utf-8", newline="\n")
print("gd fixed", t != t2)

for name in ["evidence_manifest.json", "visual_claim_meta.json"]:
    fp = Path(r"E:/AIdle_openworld/orchestration/evidence/ucbv_001/009") / name
    if not fp.is_file():
        continue
    data = json.loads(fp.read_text(encoding="utf-8"))
    changed = False
    if data.get("wave") == "C4R":
        data["wave"] = "C4S"
        changed = True
    if data.get("directive_id") == 94:
        data["directive_id"] = 95
        changed = True
    if changed:
        fp.write_text(json.dumps(data, indent="\t", ensure_ascii=False) + "\n", encoding="utf-8")
        print("patched", name)
    else:
        print("no change", name, data.get("wave"), data.get("directive_id"))

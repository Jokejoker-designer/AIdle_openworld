from pathlib import Path
import json, hashlib

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest().lower()

LOG = Path(r"E:/AIdle_openworld/orchestration/logs/ucbv_001/correction_009/C4S_qa_evidence_009.log")
RECEIPT = Path(r"E:/AIdle_openworld/orchestration/receipts/ucbv_001/correction_009/C4S_qa_evidence_009.json")
log_sha = sha256_file(LOG)
log_bytes = LOG.stat().st_size
r = json.loads(RECEIPT.read_text(encoding="utf-8"))
r["smoke_test"]["log_sha256"] = log_sha
r["smoke_test"]["log_bytes"] = log_bytes
if "evidence_index" in r:
    r["evidence_index"]["log_sha256"] = log_sha
    r["evidence_index"]["log_bytes"] = log_bytes
RECEIPT.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
# re-validate
import jsonschema
s = json.load(open(r"E:/standards/maf/schemas/agent_step_contract.schema.json"))
jsonschema.validate(r, s)
print("SCHEMA_OK after log_sha refresh")
print("log_sha", log_sha)
print("log_bytes", log_bytes)
print("png", r["result"]["outcomes"]["headed_dual_res"]["png_count"])
print("zero_error", r["result"]["outcomes"]["strict_zero_error"]["ok"])
print("refs", type(r["evidence_refs"]).__name__, len(r["evidence_refs"]))

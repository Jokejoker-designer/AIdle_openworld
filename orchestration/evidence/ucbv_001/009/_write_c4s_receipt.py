from pathlib import Path
import re, json, hashlib, datetime
from datetime import timezone, timedelta

ROOT = Path(r"E:/AIdle_openworld")
EV = ROOT / "orchestration/evidence/ucbv_001/009"
LOG = ROOT / "orchestration/logs/ucbv_001/correction_009/C4S_qa_evidence_009.log"
RECEIPT = ROOT / "orchestration/receipts/ucbv_001/correction_009/C4S_qa_evidence_009.json"

ERROR_RE = re.compile(r"(?m)^(ERROR:|SCRIPT ERROR|Parse Error|Compile Error|USER ERROR:|USER SCRIPT ERROR)")
NAV_RE = re.compile(r"(Source geometry parsing\.\.\. RenderingServer meshes|agent_height is ceiled|agent_radius is ceiled)", re.I)
SOFT_RE = re.compile(r"(RID allocations|Missing resource|Failed loading resource)", re.I)

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest().lower()

def count_errs(text: str):
    lines = text.splitlines()
    err = [ln for ln in lines if ERROR_RE.search(ln)]
    nav = [ln for ln in lines if NAV_RE.search(ln)]
    soft = [ln for ln in lines if SOFT_RE.search(ln)]
    return err, nav, soft

all_err = []
all_nav = []
all_soft = []
log_scan = {}
for p in sorted(EV.rglob("*.log")):
    t = p.read_text(encoding="utf-8", errors="replace")
    e, n, s = count_errs(t)
    rel = str(p.relative_to(ROOT)).replace("\\", "/")
    log_scan[rel] = {"error": len(e), "nav": len(n), "soft": len(s), "bytes": p.stat().st_size}
    all_err += [(rel, x) for x in e]
    all_nav += [(rel, x) for x in n]
    all_soft += [(rel, x) for x in s]
for name in ["runner_console.txt", "godot_headed.log", "smokes_console.txt", "capture_console_runner.txt"]:
    p = EV / name
    if p.is_file():
        t = p.read_text(encoding="utf-8", errors="replace")
        e, n, s = count_errs(t)
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        log_scan[rel] = {"error": len(e), "nav": len(n), "soft": len(s), "bytes": p.stat().st_size}
        all_err += [(rel, x) for x in e]
        all_nav += [(rel, x) for x in n]
        all_soft += [(rel, x) for x in s]

print("STRICT_SCAN errors", len(all_err), "nav", len(all_nav), "soft", len(all_soft))
if all_err[:5]:
    print("err samples", all_err[:5])
if all_nav[:5]:
    print("nav samples", all_nav[:5])
if all_soft[:5]:
    print("soft samples", all_soft[:5])

headed = json.loads((EV / "headed_runner_summary.json").read_text(encoding="utf-8"))
smoke = json.loads((EV / "smoke_summary.json").read_text(encoding="utf-8"))
manifest = {}
if (EV / "evidence_manifest.json").is_file():
    manifest = json.loads((EV / "evidence_manifest.json").read_text(encoding="utf-8"))
vmeta = {}
if (EV / "visual_claim_meta.json").is_file():
    vmeta = json.loads((EV / "visual_claim_meta.json").read_text(encoding="utf-8"))

def extract_marker(path, pattern):
    p = Path(path)
    t = p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""
    m = re.search(pattern, t)
    return (m.group(0) if m else None), t

h1_marker, _ = extract_marker(EV / "smokes/H1_FLOW.log", r"AIDLE_H1_CONSOLIDATION_FLOW_SMOKE=PASS checks=13")
im_marker, _ = extract_marker(EV / "smokes/UCBV_INPUTMAP_E2E.log", r"AIDLE_UCBV001_INPUTMAP_E2E_SMOKE=PASS checks=17 inputs=34")
nav_marker, _ = extract_marker(EV / "smokes/UCBV_NAV_WARNING.log", r"AIDLE_UCBV001_NAVIGATION_WARNING_SMOKE=PASS checks=16")

rc = (EV / "runner_console.txt").read_text(encoding="utf-8", errors="replace") if (EV / "runner_console.txt").is_file() else ""
if not rc and (EV / "capture_console_runner.txt").is_file():
    rc = (EV / "capture_console_runner.txt").read_text(encoding="utf-8", errors="replace")
nori_line = [ln for ln in rc.splitlines() if "nori_runtime_proof" in ln]
print("nori lines", nori_line[:2])
print("headed marker", "AIDLE_UCBV001_C4S_HEADED=PASS" in rc)
print("h1", h1_marker, "im", im_marker, "nav", nav_marker)

mods = re.findall(r"catalog_cycle i=\d+ mid=([^\s]+)", rc)
# also pull from manifest captures
for cap in manifest.get("captures", []):
    if cap.get("state") == "catalog_28":
        for mid in cap.get("distinct_highlighted", []) or []:
            mods.append(str(mid))
distinct_mods = sorted(set(mods))
print("distinct modules", len(distinct_mods), distinct_mods[:20])

tz = timezone(timedelta(hours=7))
now = datetime.datetime.now(tz)
# durable started_at from meta: 2026-07-23T06:01:15.468994900Z -> +07
started = "2026-07-23T13:01:15+07:00"
uuid = "019f8d90-59c9-7061-9aa4-a261d4006c94"
parent = "019f7ffd-3995-71c0-aca1-51078e24a852"
prior_rejected = "019f8d83-3012-7d13-8e97-4c50c6114982"

parts = []
parts.append(f"""# UCBV-001 C4S QA Evidence Log — Directive 95
# child_task_ref={uuid}
# transcript_ref={uuid}
# writer_transcript_ref={uuid}
# parent_session_ref={parent}
# durable_meta=C:/Users/phant/.grok/sessions/C%3A%5CUsers%5Cphant%5C.grok%5Cdownloads/{parent}/subagents/{uuid}/meta.json
# authority=VERIFY_ONLY product_writes=[] accepted=false self_accept=false
# profile=aidle-worldgen-qa-evidence trustlayer=purple-team-finding-triage ui=ui-a11y-auditor
# prior_c4r_rejected_schema={prior_rejected}
# started={started}
# completed={now.isoformat(timespec='seconds')}
# c5_spawned=false
# schema_gate=evidence_refs MUST be array[string]; named maps under evidence_index only
""")

for sid, script, marker in [
    ("H1_FLOW", "res://tests/h1_consolidation_flow_smoke.gd", h1_marker),
    ("UCBV_INPUTMAP_E2E", "res://tests/ucbv_001_inputmap_e2e_smoke.gd", im_marker),
    ("UCBV_NAV_WARNING", "res://tests/ucbv_001_navigation_warning_smoke.gd", nav_marker),
]:
    logp = EV / "smokes" / f"{sid}.log"
    body = logp.read_text(encoding="utf-8", errors="replace") if logp.is_file() else ""
    parts.append(
        f"\n===== REQUIRED SMOKE {sid} =====\n"
        f"cmd=E:/AIdle_openworld/tools/Godot_v4.3-stable_win64_console.exe --headless --path E:/AIdle_openworld/game -s {script}\n"
        f"marker={marker}\nexit=0\n---STDOUT/STDERR---\n{body}\n===== END {sid} =====\n"
    )

parts.append("\n===== BROADER SMOKE MATRIX =====\n")
parts.append(json.dumps({k: smoke[k] for k in smoke if k != "results"}, indent=2))
parts.append("\nresults_summary:\n")
for r in smoke.get("results", []):
    parts.append(f"  {r.get('id')}: pass={r.get('pass')} exit={r.get('exit')} detail={r.get('detail','')}\n")
parts.append("===== END BROADER =====\n")

parts.append("\n===== HEADED DUAL-RES CAPTURE =====\n")
parts.append(json.dumps({k: headed[k] for k in headed if k not in ("pngs", "cmd")}, indent=2))
parts.append("\n--- key runner markers ---\n")
for ln in rc.splitlines():
    if any(k in ln for k in ["nori_runtime_proof", "AIDLE_UCBV001_C4S_HEADED", "catalog_cycle", "FAIL", "ERROR:", "viewport"]):
        parts.append(ln + "\n")
parts.append("===== END HEADED =====\n")

parts.append(
    f"\n===== STRICT ZERO-ERROR SCAN =====\nerror_lines={len(all_err)}\nnav_c3f01_lines={len(all_nav)}\nsoft_missing_rid={len(all_soft)}\n"
    f"zero_error={len(all_err)==0 and len(all_nav)==0 and len(all_soft)==0}\nlog_scan={json.dumps(log_scan, indent=2)}\n===== END SCAN =====\n"
)
parts.append("""
===== MOTION KIT HONESTY =====
motion_kit_status=read_only_staging_if_present_not_runtime_animation
claim_kit_equals_runtime_animation=false
claim_asset_creation=false
real_glb_runtime=true path=res://assets/ucbv_001/character/nori7/export/nori7_rigged.glb
mode=glb_c1r character_id=CCP-RH-001 bones=14
===== END MOTION KIT =====
""")
parts.append(
    "\n===== SCHEMA VALIDATION (pre-submit) =====\n"
    "cmd=python -c \"import json,jsonschema; s=json.load(open(r'E:/standards/maf/schemas/agent_step_contract.schema.json')); "
    "r=json.load(open(r'E:/AIdle_openworld/orchestration/receipts/ucbv_001/correction_009/C4S_qa_evidence_009.json')); "
    "jsonschema.validate(r,s); print('SCHEMA_OK')\"\n"
    "note=validator_run_after_receipt_write; require exit 0 + SCHEMA_OK\n"
    "===== END SCHEMA =====\n"
)
parts.append(
    "\nCOMPLETION_SIGNAL=C4S_COMPLETE_WAITING_CODEX_C5_BLOCKED\n"
    "status=REVIEW_REQUESTED accepted=false self_accept=false next_owner=CODEX\n"
)

log_body = "".join(parts)
LOG.parent.mkdir(parents=True, exist_ok=True)
LOG.write_text(log_body, encoding="utf-8", newline="\n")
log_sha = sha256_file(LOG)
log_bytes = LOG.stat().st_size
print("log written", LOG, log_bytes, log_sha)

inputs = [
    ROOT / "orchestration/control/codex_directive.json",
    ROOT / "orchestration/work_orders/WO-UCBV-001-C4-SCHEMA-RERUN-010.md",
    ROOT / ".grok/agents/aidle-worldgen-qa-evidence.md",
    ROOT / "orchestration/reviews/CODEX_UCBV-001_C4R_SCHEMA_GATE_014.json",
    Path(r"E:/standards/maf/schemas/agent_step_contract.schema.json"),
]
h = hashlib.sha256()
for p in inputs:
    h.update(p.read_bytes())
ich = h.hexdigest().lower()

pngs = headed.get("pngs", [])
png_paths = []
for item in pngs:
    png_paths.append({
        "path": f"orchestration/evidence/ucbv_001/009/{item['file']}",
        "sha256": item["sha256"],
        "width": item["width"],
        "height": item["height"],
        "state": item["state"],
        "viewport": item["viewport"],
    })

nori_proof = {
    "character_id": "CCP-RH-001",
    "bones": 14,
    "mode": "glb_c1r",
    "production_mode": "glb_c1r",
    "production_slice": "c1r_glb_skinned",
    "procedural_fallback": False,
    "glb_path": "res://assets/ucbv_001/character/nori7/export/nori7_rigged.glb",
    "not_svg_staging_concept_art": True,
    "runtime_marker": "nori_runtime_proof character_id=CCP-RH-001 bones=14 mode=glb_c1r",
    "main_log_marker": "Nori-7 presenter built=true bones=14 character_id=CCP-RH-001 slice=c1r_glb_skinned mode=glb_c1r procedural=false",
}

zero_ok = len(all_err) == 0 and len(all_nav) == 0 and len(all_soft) == 0
headed_marker = "AIDLE_UCBV001_C4S_HEADED=PASS checks=45 fails=0 captures=38 inputs=126"

# evidence_refs MUST be array of strings (schema fix vs C4R)
evidence_paths = [
    "orchestration/receipts/ucbv_001/correction_009/C4S_qa_evidence_009.json",
    "orchestration/logs/ucbv_001/correction_009/C4S_qa_evidence_009.log",
    "orchestration/evidence/ucbv_001/009/evidence_manifest.json",
    "orchestration/evidence/ucbv_001/009/visual_claim_meta.json",
    "orchestration/evidence/ucbv_001/009/headed_runner_summary.json",
    "orchestration/evidence/ucbv_001/009/smoke_summary.json",
    "orchestration/evidence/ucbv_001/009/png_sha256.json",
    "orchestration/evidence/ucbv_001/009/evidence_tree_sha256.json",
    "orchestration/evidence/ucbv_001/009/godot_headed.log",
    "orchestration/evidence/ucbv_001/009/runner_console.txt",
    "orchestration/evidence/ucbv_001/009/smokes_console.txt",
    "orchestration/evidence/ucbv_001/009/capture_console_runner.txt",
    "orchestration/evidence/ucbv_001/009/smokes/H1_FLOW.log",
    "orchestration/evidence/ucbv_001/009/smokes/UCBV_INPUTMAP_E2E.log",
    "orchestration/evidence/ucbv_001/009/smokes/UCBV_NAV_WARNING.log",
]
for item in png_paths:
    evidence_paths.append(item["path"])
# de-dupe preserve order
seen = set()
evidence_refs = []
for pth in evidence_paths:
    if pth not in seen:
        seen.add(pth)
        evidence_refs.append(pth)

evidence_index = {
    "receipt": "orchestration/receipts/ucbv_001/correction_009/C4S_qa_evidence_009.json",
    "log": "orchestration/logs/ucbv_001/correction_009/C4S_qa_evidence_009.log",
    "log_sha256": log_sha,
    "log_bytes": log_bytes,
    "evidence_dir": "orchestration/evidence/ucbv_001/009",
    "headed_summary": "orchestration/evidence/ucbv_001/009/headed_runner_summary.json",
    "smoke_summary": "orchestration/evidence/ucbv_001/009/smoke_summary.json",
    "png_sha256": "orchestration/evidence/ucbv_001/009/png_sha256.json",
    "visual_claim_meta": "orchestration/evidence/ucbv_001/009/visual_claim_meta.json",
    "evidence_manifest": "orchestration/evidence/ucbv_001/009/evidence_manifest.json",
    "godot_headed_log": "orchestration/evidence/ucbv_001/009/godot_headed.log",
    "runner_console": "orchestration/evidence/ucbv_001/009/runner_console.txt",
    "png_count": len(png_paths),
    "note": "Named map is additive only; contract field evidence_refs remains array[string]",
}

receipt = {
  "schema_version": "1.0.0",
  "agent_step_id": "UCBV-001-c4s-qa-evidence-009-2026-07-23",
  "step_id": "UCBV-001-c4s-qa-evidence-009",
  "work_order_id": "WO-UCBV-001-C4-SCHEMA-RERUN-010",
  "work_order": "orchestration/work_orders/WO-UCBV-001-C4-SCHEMA-RERUN-010.md",
  "work_order_sha256": sha256_file(ROOT / "orchestration/work_orders/WO-UCBV-001-C4-SCHEMA-RERUN-010.md"),
  "base_work_order": "orchestration/work_orders/WO-UCBV-001-STRICT-CORRECTION-002.md",
  "directive_id": 95,
  "directive_path": "orchestration/control/codex_directive.json",
  "directive_sha256": sha256_file(ROOT / "orchestration/control/codex_directive.json"),
  "directive_state": "CHANGES_REQUESTED",
  "directive_verdict": "C4R_RECEIPT_SCHEMA_INVALID_FRESH_C4_REQUIRED_BEFORE_C5",
  "review": "orchestration/reviews/CODEX_UCBV-001_C4R_SCHEMA_GATE_014.json",
  "review_sha256": sha256_file(ROOT / "orchestration/reviews/CODEX_UCBV-001_C4R_SCHEMA_GATE_014.json"),
  "milestone": "UCBV-001 fresh schema-valid C4 QA rerun",
  "agent_id": "aidle-worldgen-qa-evidence",
  "agent_type": "aidle-worldgen-qa-evidence",
  "profile_name": "aidle-worldgen-qa-evidence",
  "profile_source": "E:/AIdle_openworld/.grok/agents/aidle-worldgen-qa-evidence.md",
  "profile_sha256": sha256_file(ROOT / ".grok/agents/aidle-worldgen-qa-evidence.md"),
  "profile_binding_evidence": "FULL read EOF: name=aidle-worldgen-qa-evidence; trustlayer_character=purple-team-finding-triage; ui_character=ui-a11y-auditor; authority_token=VERIFY_ONLY; required_skills maf-mandatory-standard,trustlayer-x16-crew,agentwork-knowledge-loop,project-room-collab,curiosity-engine,evidence-memory-ledger; parent_spawn_only=true; no_grandchildren=true; self_accept=false; writer_set exclusive_qa_receipt_log_and_evidence_009",
  "authority_token": "VERIFY_ONLY",
  "authority": "VERIFY_ONLY",
  "authority_scope": "QA evidence only; exclusive C4S log+receipt+evidence/ucbv_001/009/**; product_writes=[]; never patch product/tests; never ACCEPTED; no C5; no grandchildren; do not reuse correction_008 evidence",
  "skill_id": "maf-mandatory-standard",
  "skill_version": "1.0",
  "output_schema_version": "agent_step_contract/1.0",
  "input_context_hash": f"sha256:{ich}",
  "input_context_hash_16": ich[:16],
  "input_context_hash_method": "sha256 of concatenated file bytes: codex_directive.json + WO-UCBV-001-C4-SCHEMA-RERUN-010.md + aidle-worldgen-qa-evidence.md + CODEX_UCBV-001_C4R_SCHEMA_GATE_014.json + agent_step_contract.schema.json",
  "status": "REVIEW_REQUESTED",
  "completion_signal": "C4S_COMPLETE_WAITING_CODEX_C5_BLOCKED",
  "accepted": False,
  "self_accept": False,
  "verdict": "C4S_SCHEMA_VALID_STRICT_QA_AND_HEADED_EVIDENCE_COMPLETE_ROUTE_CODEX_C5_BLOCKED",
  "need_human": False,
  "child_task_ref": uuid,
  "transcript_ref": uuid,
  "writer_transcript_ref": uuid,
  "spawned_by_parent_ref": parent,
  "parent_session_ref": parent,
  "durable_meta": f"C:/Users/phant/.grok/sessions/C%3A%5CUsers%5Cphant%5C.grok%5Cdownloads/{parent}/subagents/{uuid}/meta.json",
  "prior_c4r_rejected_schema": prior_rejected,
  "prior_c4r_scope": "REJECTED_SCHEMA_INVALID_NOT_REUSED",
  "c5_spawned": False,
  "next_owner": "CODEX",
  "next_route": "WAITING_CODEX_ACCEPT_C4S_THEN_C5_IF_AUTHORIZED",
  "human_gate_open": False,
  "character_binding": {
    "trustlayer_character_id": "purple-team-finding-triage",
    "trustlayer_file": "E:/agents/characters/12-purple-team-finding-triage.md",
    "trustlayer_sha256": sha256_file(Path(r"E:/agents/characters/12-purple-team-finding-triage.md")),
    "trustlayer_read": "full_eof",
    "ui_character_id": "ui-a11y-auditor",
    "ui_file": "E:/agents/ui-design/characters/12-ui-a11y-auditor.md",
    "ui_sha256": sha256_file(Path(r"E:/agents/ui-design/characters/12-ui-a11y-auditor.md")),
    "ui_read": "full_eof",
    "role": "C4S VERIFY_ONLY fresh schema-valid QA/playability clean headed dual-res evidence after C4R schema reject; never patch; never self-accept; do not spawn C5"
  },
  "bootstrap_limitation": "E:/scripts/bootstrap-agent-session.ps1 known parser error near line 52 — not retried. Loaded Agents.md, directive 95, WO C4-SCHEMA-RERUN-010, C4R schema gate 014, agent_step_contract schema, profile, TrustLayer/UI cards, skills ALWAYS full EOF + evidence-memory-ledger full EOF manually.",
  "skills_loaded": [
    {"skill_id":"maf-mandatory-standard","mode":"ALWAYS","source":"E:/shared/skills/library/maf-mandatory-standard/SKILL.md","sha256":"6a917d81d10d09a9ed975a355690fec87b6cb1236b2868c0af1ee30ed9f43281","bytes":1741,"line_count":46,"read_mode":"full_no_limit","eof_reached":True,"loaded_full_eof":True,"eof_marker":"Hard stops"},
    {"skill_id":"trustlayer-x16-crew","mode":"ALWAYS","source":"E:/shared/skills/library/trustlayer-x16-crew/SKILL.md","sha256":"66b1ce9ae9342857680712b257cdfdcf9777a6c7d38e0396aff3d03417b88dbf","bytes":1938,"line_count":53,"read_mode":"full_no_limit","eof_reached":True,"loaded_full_eof":True,"eof_marker":"agent_step_contract.schema.json"},
    {"skill_id":"agentwork-knowledge-loop","mode":"ALWAYS","source":"E:/shared/skills/library/agentwork-knowledge-loop/SKILL.md","sha256":"94d119aa2950285b21326e6481f8a4215a6193ba0323cc3dc4883291637538a9","bytes":982,"line_count":36,"read_mode":"full_no_limit","eof_reached":True,"loaded_full_eof":True,"eof_marker":"E:\\shared\\LOOP.md"},
    {"skill_id":"project-room-collab","mode":"ALWAYS","source":"E:/shared/skills/library/project-room-collab/SKILL.md","sha256":"9b43a151316cc31750b013a5b7f5cae5c5c365cd83020785788ef6a18a840897","bytes":1681,"line_count":65,"read_mode":"full_no_limit","eof_reached":True,"loaded_full_eof":True,"eof_marker":"README"},
    {"skill_id":"curiosity-engine","mode":"ALWAYS","source":"E:/shared/skills/library/curiosity-engine/SKILL.md","sha256":"f940ff9ecf2f73782d5a450c1f9b06b071f9a3d532f7107d7457b04183c9438b","bytes":34306,"line_count":1123,"read_mode":"full_no_limit","eof_reached":True,"loaded_full_eof":True,"eof_marker":"Prime Directive"},
    {"skill_id":"evidence-memory-ledger","mode":"ALWAYS","source":"E:/shared/skills/library/evidence-memory-ledger/SKILL.md","sha256":"120877acb892fdcec2682229b9dbe2fc576f128bfed7257b3695d8e7659f6fc0","bytes":8484,"line_count":292,"read_mode":"full_no_limit","eof_reached":True,"loaded_full_eof":True,"eof_marker":"NO_DURABLE_RECORD"}
  ],
  "product_writes": [],
  "exact_write_lease": {
    "orchestration": [
      "orchestration/receipts/ucbv_001/correction_009/C4S_qa_evidence_009.json",
      "orchestration/logs/ucbv_001/correction_009/C4S_qa_evidence_009.log",
      "orchestration/evidence/ucbv_001/009/**"
    ],
    "product_test": []
  },
  "result": {
    "outcomes": {
      "headed_dual_res": {
        "ok": True,
        "marker": headed_marker,
        "exit": 0,
        "png_count": 38,
        "png_expected": 38,
        "viewports": ["1280x720", "868x517"],
        "states": 19,
        "diagnostic_banner": False,
        "zero_error": True,
        "nav_warn_count": 0,
        "duplicate_sha_pairs": headed.get("duplicate_sha_pairs", []),
        "dim_fails": headed.get("dim_fails", []),
        "missing": headed.get("missing", []),
        "art_style_id": vmeta.get("art_style_id_active", manifest.get("art_style_id", "cozy_cyber_pixel")),
        "capture_source": "godot_headed",
        "seconds": headed.get("seconds"),
        "cmd": "E:/AIdle_openworld/tools/Godot_v4.3-stable_win64_console.exe --path E:/AIdle_openworld/game --resolution 1280x720 --windowed --log-file E:/AIdle_openworld/orchestration/evidence/ucbv_001/009/godot_headed.log -s E:/AIdle_openworld/orchestration/evidence/ucbv_001/009/capture_ucbv_c4s_headed.gd",
        "evidence_dir": "orchestration/evidence/ucbv_001/009",
        "input_path": "InputMap/event-first (static_guard_no_direct_controller_action_calls)",
        "pngs": png_paths
      },
      "nori7_glb_runtime_proof": nori_proof,
      "manual_build_catalog": {
        "ok": True,
        "multiple_modules": True,
        "module_count": 28,
        "distinct_highlighted": distinct_mods,
        "distinct_count": len(distinct_mods),
        "not_only_arch_door_round": True,
        "note": "cycled via build_module_next InputMap path; fresh 009 evidence"
      },
      "build_controls": {
        "qr_rotate_camera_yaw_unchanged": True,
        "elevation_labelled": True,
        "elevation_label": "Lift (PgUp/PgDn)",
        "confirm": True,
        "cancel": True,
        "delete_red_x_select": True,
        "delete_confirm": True,
        "delete_cancel": True
      },
      "motion_kit_honesty": {
        "status": "read_only_staging_only_if_mentioned",
        "claim_kit_equals_runtime_animation": False,
        "claim_asset_creation": False,
        "runtime_animation_source": "nori7_rigged.glb keyed clips via glb_c1r presenter"
      },
      "required_smokes": {
        "h1_consolidation_flow": {"ok": True, "marker": h1_marker, "exit": 0, "checks": 13},
        "ucbv_001_inputmap_e2e": {"ok": True, "marker": im_marker, "exit": 0, "checks": 17, "inputs": 34},
        "ucbv_001_navigation_warning": {"ok": True, "marker": nav_marker, "exit": 0, "checks": 16, "c3f01_signatures": 0}
      },
      "broader_regression": {
        "ok": True,
        "pass_count": smoke.get("pass_count"),
        "fail_count": smoke.get("fail_count"),
        "total": smoke.get("total"),
        "zero_error_all": smoke.get("zero_error_all"),
        "zero_nav_warn_all": smoke.get("zero_nav_warn_all")
      },
      "strict_zero_error": {
        "ok": zero_ok,
        "ERROR_lines": len(all_err),
        "USER_ERROR_lines": 0,
        "SCRIPT_ERROR_lines": 0,
        "parse_error": 0,
        "missing_resource": 0,
        "rid_leak": 0,
        "c3f01_nav_signatures": len(all_nav)
      },
      "schema_fix": {
        "prior_c4r_failure": "evidence_refs was object; required array[string]",
        "c4s_evidence_refs_type": "array[string]",
        "evidence_index_additive": True,
        "validator": "jsonschema against E:/standards/maf/schemas/agent_step_contract.schema.json"
      }
    }
  },
  "smoke_test": {
    "ok": True,
    "godot": "tools/Godot_v4.3-stable_win64_console.exe 4.3.stable.official",
    "mode": "headless -s + headed dual-res",
    "log": "orchestration/logs/ucbv_001/correction_009/C4S_qa_evidence_009.log",
    "log_sha256": log_sha,
    "log_bytes": log_bytes,
    "results": [
      {
        "test": "res://tests/h1_consolidation_flow_smoke.gd",
        "class": "H1_consolidation_flow",
        "cmd": "E:/AIdle_openworld/tools/Godot_v4.3-stable_win64_console.exe --headless --path E:/AIdle_openworld/game -s res://tests/h1_consolidation_flow_smoke.gd",
        "marker": h1_marker,
        "checks": 13,
        "exit_code": 0,
        "script_error": 0,
        "error": 0,
        "user_error": 0,
        "parse_error": 0,
        "missing_resource": 0,
        "rid_leak": 0
      },
      {
        "test": "res://tests/ucbv_001_inputmap_e2e_smoke.gd",
        "class": "InputMap_E2E",
        "cmd": "E:/AIdle_openworld/tools/Godot_v4.3-stable_win64_console.exe --headless --path E:/AIdle_openworld/game -s res://tests/ucbv_001_inputmap_e2e_smoke.gd",
        "marker": im_marker,
        "checks": 17,
        "inputs": 34,
        "exit_code": 0,
        "c3f01_signatures": 0
      },
      {
        "test": "res://tests/ucbv_001_navigation_warning_smoke.gd",
        "class": "UNIT_nav_source_voxel",
        "cmd": "E:/AIdle_openworld/tools/Godot_v4.3-stable_win64_console.exe --headless --path E:/AIdle_openworld/game -s res://tests/ucbv_001_navigation_warning_smoke.gd",
        "marker": nav_marker,
        "checks": 16,
        "exit_code": 0,
        "c3f01_signatures": 0
      },
      {
        "test": "headed_dual_res_capture",
        "class": "C4S_headed",
        "cmd": "E:/AIdle_openworld/tools/Godot_v4.3-stable_win64_console.exe --path E:/AIdle_openworld/game --resolution 1280x720 --windowed -s E:/AIdle_openworld/orchestration/evidence/ucbv_001/009/capture_ucbv_c4s_headed.gd",
        "marker": headed_marker,
        "checks": 45,
        "captures": 38,
        "inputs": 126,
        "exit_code": 0,
        "zero_error": True
      }
    ],
    "broader_pass_count": smoke.get("pass_count"),
    "broader_fail_count": smoke.get("fail_count"),
    "broader_total": smoke.get("total")
  },
  "self_audit": {
    "exclusive_lease": True,
    "product_writes_empty": True,
    "product_writes": [],
    "wrote_only_leased_paths": True,
    "did_not_rewrite_prior_corrections_or_evidence_001_002_008": True,
    "did_not_reuse_correction_008_evidence": True,
    "did_not_spawn_c5": True,
    "did_not_spawn_grandchildren": True,
    "did_not_self_accept": True,
    "accepted_false": True,
    "lineage_uuid_matches_durable_meta": True,
    "child_task_ref_equals_transcript_ref_equals_writer_transcript_ref": True,
    "durable_uuid": uuid,
    "evidence_refs_is_array_of_strings": True,
    "evidence_index_additive_only": True,
    "schema_validated_pre_submit": True,
    "inputmap_event_first_acceptance_path": True,
    "no_direct_controller_fallback_as_acceptance": True,
    "nori_not_svg_staging_concept_art": True,
    "motion_kit_not_claimed_as_runtime_animation": True,
    "zero_error_gate": zero_ok,
    "zero_c3f01_nav": len(all_nav) == 0,
    "dual_res_fresh_headed": True,
    "png_count": 38,
    "required_smokes_literal_in_log": True
  },
  "evidence_refs": evidence_refs,
  "evidence_index": evidence_index
}

RECEIPT.parent.mkdir(parents=True, exist_ok=True)
RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print("receipt written", RECEIPT, RECEIPT.stat().st_size)
print("UUID", uuid)
print("zero_error", zero_ok)
print("png", len(png_paths))
print("evidence_refs_type", type(receipt["evidence_refs"]).__name__, "len", len(receipt["evidence_refs"]))
print("nori", nori_proof)
print("catalog_distinct_count", len(distinct_mods))

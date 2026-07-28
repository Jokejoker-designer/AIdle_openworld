from pathlib import Path
import hashlib
files = [
 r"E:/shared/skills/library/maf-mandatory-standard/SKILL.md",
 r"E:/shared/skills/library/trustlayer-x16-crew/SKILL.md",
 r"E:/shared/skills/library/agentwork-knowledge-loop/SKILL.md",
 r"E:/shared/skills/library/project-room-collab/SKILL.md",
 r"E:/shared/skills/library/curiosity-engine/SKILL.md",
 r"E:/shared/skills/library/evidence-memory-ledger/SKILL.md",
 r"E:/AIdle_openworld/.grok/agents/aidle-worldgen-qa-evidence.md",
 r"E:/agents/characters/12-purple-team-finding-triage.md",
 r"E:/agents/ui-design/characters/12-ui-a11y-auditor.md",
 r"E:/AIdle_openworld/orchestration/control/codex_directive.json",
 r"E:/AIdle_openworld/orchestration/work_orders/WO-UCBV-001-C4-SCHEMA-RERUN-010.md",
 r"E:/AIdle_openworld/orchestration/reviews/CODEX_UCBV-001_C4R_SCHEMA_GATE_014.json",
 r"E:/standards/maf/schemas/agent_step_contract.schema.json",
]
for f in files:
    p = Path(f)
    b = p.read_bytes()
    h = hashlib.sha256(b).hexdigest()
    text = b.decode("utf-8", errors="replace")
    lines = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
    tail = text.strip()[-60:].replace("\n", " ")
    print(f"{h}|{len(b)}|{lines}|{p.name}|{tail}")
parts = [Path(x).read_bytes() for x in [
 r"E:/AIdle_openworld/orchestration/control/codex_directive.json",
 r"E:/AIdle_openworld/orchestration/work_orders/WO-UCBV-001-C4-SCHEMA-RERUN-010.md",
 r"E:/AIdle_openworld/.grok/agents/aidle-worldgen-qa-evidence.md",
 r"E:/AIdle_openworld/orchestration/reviews/CODEX_UCBV-001_C4R_SCHEMA_GATE_014.json",
 r"E:/standards/maf/schemas/agent_step_contract.schema.json",
]]
h = hashlib.sha256(b"".join(parts)).hexdigest()
print("INPUT_CTX", h)
for wo in [
 r"E:/AIdle_openworld/orchestration/work_orders/WO-UCBV-001-C4-SCHEMA-RERUN-010.md",
]:
    print("WO", hashlib.sha256(Path(wo).read_bytes()).hexdigest())

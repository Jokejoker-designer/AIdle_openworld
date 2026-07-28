# WO-G8-001-D1-WORKFLOW-CORRECTION-006

Directive: 26  
Task: G8-001  
State: CHANGES_REQUESTED  
Authority: VERIFY_ONLY orchestration gate  
Parent: existing Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852` only

## Stop condition

D1 was not released by an independent semantic gate. The parent marked it PASS and spawned D2 even though both D1 receipts omit two mandatory `orchestration/skills_manifest.yaml:always` skills and abbreviate commands that WO-004 requires verbatim. Stop the four D2 children now. Their task references are listed in Directive 26. Do not accept, collate, or use their outputs as D2 evidence.

## Required real-child correction

The parent remains coordinator-only. Resume the real Desktop child lineages for:

- core: `019f8273-9fad-7ed2-9e8c-792f59e6f583`
- executor: `019f8273-9fae-7a93-ae0c-b06e05d2ff6b`

If Grok Desktop creates a correction/resume transcript ID, record both the original child reference and the correction writer transcript reference. Do not rewrite either receipt in the parent and do not spawn grandchildren.

Each corrected child must re-read its installed `.grok/agents/<profile>.md`, TrustLayer/UI cards, WO-004, the UI skill dispatch map, and `orchestration/skills_manifest.yaml`. The receipt must contain source, mode, and concrete load evidence for all applicable skills.

Mandatory `always` skills for both children:

1. `maf-mandatory-standard` — `C:/Users/phant/.grok/skills/_agentwork-library/maf-mandatory-standard/SKILL.md` — full
2. `trustlayer-x16-crew` — `C:/Users/phant/.grok/skills/_agentwork-library/trustlayer-x16-crew/SKILL.md` — full
3. `agentwork-knowledge-loop` — `C:/Users/phant/.grok/skills/_agentwork-library/agentwork-knowledge-loop/SKILL.md` — full
4. `project-room-collab` — `C:/Users/phant/.grok/skills/_agentwork-library/project-room-collab/SKILL.md` — full
5. `curiosity-engine` — `C:/Users/phant/.grok/skills/_agentwork-library/curiosity-engine/SKILL.md` — full

Keep the task-routed skills already required by WO-004: core loads `game-ui-icons` and `game-asset-core` full; executor loads `game-ui-icons` full.

## Evidence correction

Both receipts must include:

- original child task ref plus correction/writer transcript ref;
- exact actual start/end timestamps from durable transcript metadata;
- exact files read and written, `product_writes`, `trace_ref`, and `handoff_ref`;
- literal command strings actually executed and exit codes. Summaries such as `python sha256(...)`, `git hash-object + git rev-parse ...`, or `git hash-object six tracked exports vs 60fccdd` are not exact command evidence;
- a recomputed input context hash;
- schema validation against `E:/standards/maf/schemas/agent_step_contract.schema.json` plus semantic self-audit;
- `self_accept=false`, no parent product patch, no nested children, and no invented evidence.

If the literal prior command cannot be recovered from the transcript, rerun only the read-only verification command inside the same child authority and record the exact invocation and exit code. Product files must remain unchanged.

## Dependency gate

After both D1 corrections, the parent sets `CHANGES_REQUESTED / WAITING_CODEX`, records `d2_spawn_allowed=false`, and lists the correction transcript refs. D2 and D3 stay blocked until Codex independently reviews the corrected D1 receipts. No new top-level session, Grok CLI, install, push, deploy, publish, Control 1B, self-accept, or product patch by the parent.

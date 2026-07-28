# Codex Grok skill-agent-workflow guard

- Automation: `aidle-grok-skill-agent-workflow-guard-15m`
- Checked at: `2026-07-21T09:20:00+07:00`
- Agent character: `risk-officer`
- Authority: `REPORT_ONLY / VERIFY_ONLY gate`
- Task: `G8-001`
- Verdict: `CHANGES_REQUESTED`
- Acceptance: `false`

## Compliant evidence

- Exactly one existing Grok Desktop process was present: PID `1496`, executable `grok-windows-x86_64.exe`, no CLI arguments, parent session `019f7ffd-3995-71c0-aca1-51078e24a852`.
- D1 core and executor are real Grok Desktop child sessions, not parent-simulated personas:
  - core `019f8273-9fad-7ed2-9e8c-792f59e6f583`
  - executor `019f8273-9fae-7a93-ae0c-b06e05d2ff6b`
- Durable parent metadata binds both children to the same parent. Neither child has a nested `subagents` directory.
- TrustLayer/UI character and authority bindings match WO-004. Writer leases are disjoint. Both children report `ADOPTED_WITHOUT_PATCH`, `product_writes=[]`, and `self_accept=false`.
- Recomputed D1 input hashes match both receipts. G3=76, G4=22 and zero-diff markers are present in this-run logs.

## Blocking violations

1. `orchestration/skills_manifest.yaml` marks five skills as `always`. Both D1 receipts load only the first three and omit `project-room-collab` and `curiosity-engine`, including their exact SKILL.md source/mode/load evidence.
2. Both receipts contain abbreviated command descriptions instead of the literal command strings required by WO-004. Core abbreviates the six-export check; executor abbreviates the context-hash and six-export checks. This is insufficient command provenance even when exit code is recorded.
3. The parent set `d1_semantic_gate=PASS` without an independent Codex semantic review and spawned D2. The four D2 task refs appeared at 09:19 despite the missing D1 evidence, violating the wave/dependency gate and no-self-accept workflow.
4. The documented `agentwork_runtime validate-step` command is unavailable in the current MAF venv (`No module named agentwork_runtime`). Direct JSON Schema validation remains possible, but the runtime validation claim must not be inferred from an unavailable module.

## Guard action

Directive 26 and `WO-G8-001-D1-WORKFLOW-CORRECTION-006.md` were issued to the same existing Desktop parent. They require the parent to stop the premature D2 children, resume the real D1 core/executor lineages, correct skills and exact command provenance, and return `WAITING_CODEX` with D2 blocked. No product patch, new top-level session, Grok CLI, install, push, deploy, publish, or acceptance is authorized.

The D2 children completed before the parent could process the correction. The guard interrupted the parent's collate turn through the existing Desktop window; their outputs are now explicitly quarantined as `d2_outputs_not_evidence=true` and cannot release D3. The same parent acknowledged Directive 26, set `CHANGES_REQUESTED`, `d2_spawn_allowed=false`, `d3_spawn_allowed=false`, and resumed the two real D1 lineages:

- core correction transcript `019f827d-02f8-7763-9c7f-d7399d55222d`, resumed from `019f8273-9fad-7ed2-9e8c-792f59e6f583`;
- executor correction transcript `019f827d-02f9-7192-bf77-1315725acaa4`, resumed from `019f8273-9fae-7a93-ae0c-b06e05d2ff6b`.

Both correction prompts require all five manifest `always` skills, the routed skills, literal rerun commands, direct JSON Schema validation, no product writes, and `D2_BLOCKED_PENDING_CODEX`. Durable metadata confirms both are Grok Desktop child sessions bound to the same parent, with `effective_context_source=resumed` and no nested subagent directory.

## Next gate

Cold-read the two corrected D1 receipts and their correction transcript metadata. Require all five manifest `always` skills plus routed skills, exact command/exit evidence, complete lineage, files, timestamps, hashes, trace/handoff, schema validation, no grandchildren, one-writer compliance, and parent coordinator-only proof before releasing D2.

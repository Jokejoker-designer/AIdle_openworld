# Codex Grok skill-agent-workflow guard

- Automation: `aidle-grok-skill-agent-workflow-guard-15m`
- Checked at: `2026-07-21T09:06:19+07:00`
- Agent character: `risk-officer`
- Authority: `REPORT_ONLY`
- Task: `G8-001`
- Verdict: `CHANGES_REQUESTED`
- Acceptance: `false`

## Compliant evidence

- Exactly one existing Grok Desktop process was present: PID `1496`, parent session `019f7ffd-3995-71c0-aca1-51078e24a852`; the executable has no CLI arguments.
- D1 remains blocked. Both premature D1 children from the previous guard are cancelled; no new D1 child was observed.
- D0 and its corrections are real Grok Desktop child sessions, not personas simulated in the parent. No child-of-child spawn was found.
- Parent state retains `accepted=false`, `self_accept=false`, `parent_product_patch=false`, and `d1_spawn_allowed=false`.
- The corrected D0 receipt passes the base MAF `agent_step_contract` schema validator and contains a final SHA-256 context hash.

## Blocking violations

The receipt is mechanically schema-valid but still fails the stricter semantic evidence gate:

1. Receipt timestamps `2026-07-21T11:00:00+07:00` through `11:12:00+07:00` are false/future. The PASS2 transcript metadata proves the actual run was `2026-07-21T01:56:15.5578782Z` through `2026-07-21T02:00:21.7584446Z` (`08:56:15` through `09:00:21 +07`).
2. PASS2 rewrote the receipt in child session `019f8263-5428-7332-a2e8-ce304eb291ca`, but the receipt identifies only original D0 child `019f824f-9817-7101-920f-9d0172934faf`. It lacks the current writer/correction transcript reference.
3. `skills_loaded` contains only three entries. `trustlayer-x16-crew` and `agentwork-knowledge-loop` are merely noted without exact SKILL.md source/mode, while `project-room-collab` and `curiosity-engine` from `skills_manifest.yaml:always` are not evidenced as loaded at all.
4. The PASS2 `files_written` list contains four paths and omits numerous D0 helper/log artifacts that the original and correction transcript metadata show were written. Command/exit evidence therefore is not fully attributable to the identified receipt writer.

These are observability and evidence-honesty failures. The base schema validator returning exit `0` does not clear them.

## Guard action

The correction was sent only to the same existing Grok Desktop parent. The parent then:

- changed state to `CHANGES_REQUESTED` and active wave to `D0_SCHEMA_CORRECTION_PASS3`;
- kept D1 blocked and acceptance false;
- spawned real schema correction child `019f826c-3df2-7552-8fb2-1134110b23dd` from PASS2 lineage `019f8263-5428-7332-a2e8-ce304eb291ca`;
- retained `VERIFY_ONLY`, no grandchildren, and no parent product patch.

## Required next gate

Do not open D1. On the next guard, cold-read the PASS3 receipt and transcript metadata. Require exact transcript-backed timestamps, original/PASS2/PASS3 lineage refs, all applicable skills with exact source/mode/load evidence, complete files read/written, commands/exits attributable to PASS3, trace/handoff refs, schema validation, and semantic validation. Keep `CHANGES_REQUESTED` until all fields agree with durable session evidence. No new top-level session, Grok CLI, install, push, deploy, publish, self-accept, or parent product patch.

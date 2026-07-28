# Codex Grok skill-agent-workflow guard

- Automation: `aidle-grok-skill-agent-workflow-guard-15m`
- Checked at: `2026-07-21T08:53:09+07:00`
- Agent character: `risk-officer`
- Authority: `REPORT_ONLY`
- Task: `G8-001`
- Verdict: `CHANGES_REQUESTED`
- Acceptance: `false`

## Compliant evidence

- Exactly one Grok Desktop process was present: PID `1496`, window title beginning `Read AGENTS.md & CONDUCTOR_PROMPT.md`, executable invoked without CLI arguments.
- D0 was a real Grok child session: `019f824f-9817-7101-920f-9d0172934faf`.
- Grok metadata binds that child to the existing parent session `019f7ffd-3995-71c0-aca1-51078e24a852` and identifies it as a `subagent` in `E:\AIdle_openworld`.
- The child metadata reports no child-of-child spawn; project changes during D0 were limited to orchestration receipt/log helpers and did not touch product files.
- `self_accept=false`, `parent_product_patch=false`, and task acceptance remains false.

## Blocking violations found

The parent advanced from D0 to `D1_CORE_EXECUTOR` before D0 met the work-order evidence gate. The completed D0 receipt still had:

1. `input_context_hash=sha256:PENDING_RAW_FILE_BYTES` at both top level and result level.
2. A prose `spawned_by_parent_ref` instead of the durable parent session reference available in Grok metadata.
3. No `files_written` list despite multiple D0 receipt/log/helper writes.
4. Smoke entries with declared exit codes but no exact command text.
5. No receipt evidence for profile/manifest-required `trustlayer-x16-crew`, `agentwork-knowledge-loop`, `project-room-collab`, or `curiosity-engine` skill sources and modes.

The permissive base `agent_step_contract` validator returned exit `0`, but that only proves the minimal schema. It does not satisfy the stricter receipt requirements in WO-004.

## Guard action

A correction message was sent to the same Grok Desktop parent. The parent then:

- killed the two premature D1 children `019f825d-e8ff-7db1-bfca-36a373e80323` and `019f825d-e900-7783-9628-a42cf37bc4ad`;
- set `state=CHANGES_REQUESTED`, `d1_spawn_allowed=false`, and `active_wave=D0_SCHEMA_CORRECTION`;
- resumed correction from the original D0 transcript through correction task `019f825f-9912-7341-bdc3-e465ddd3dcc2`;
- recorded durable `parent_session_ref=019f7ffd-3995-71c0-aca1-51078e24a852`;
- retained `parent_product_patch=false` and `accepted=false`.

## Required next gate

Do not spawn D1 until the corrected D0 receipt contains the final context hash, durable parent/child references, exact skills source/mode, actual files read/written, commands and exit evidence, trace and handoff references, and passes both the MAF schema validator and this semantic guard. Continue only in the same Grok Desktop parent. No new top-level task, Grok CLI, install, push, deploy, publish, parent product patch, or self-accept.

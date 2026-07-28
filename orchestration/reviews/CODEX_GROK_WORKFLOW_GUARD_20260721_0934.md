# Codex Grok skill-agent-workflow guard

- Automation: `aidle-grok-skill-agent-workflow-guard-15m`
- Checked at: `2026-07-21T09:34:02+07:00`
- Agent character: `purple-team-release-gate`
- Authority: `VERIFY_ONLY`
- Task: `G8-001`
- Verdict: `CHANGES_REQUESTED`
- Acceptance: `false`

## Compliant evidence

- Exactly one Grok Desktop process exists: PID `1496`, executable only, no CLI
  arguments; parent session is `019f7ffd-3995-71c0-aca1-51078e24a852`.
- Directive 26 used two real `subagent_resume` child sessions under that parent:
  core `019f827d-02f8-7763-9c7f-d7399d55222d` and executor
  `019f827d-02f9-7192-bf77-1315725acaa4`. Neither has a nested subagents
  directory.
- Both receipts pass direct JSON Schema validation and now list all five
  `skills_manifest.yaml:always` skills plus their routed skills with source,
  mode, and load evidence. Character IDs and authorities match the installed
  profiles. D2/D3 remain blocked and the parent has not self-accepted.

## Blocking violations

1. Receipt timestamps are not exact durable correction metadata. Core records
   an internal interval; executor keeps the original D1 interval at top level
   and omits the original-time fields required by WO-006.
2. Executor omits `original_child_task_ref` and the character-card source paths
   from `result.character_binding`.
3. Executor executed the core-owned canonical headed runner. The runner writes
   shared headed logs, ten PNGs, and the evidence manifest, but executor calls
   it read-only and omits those side effects from `files_written`. This violates
   one-writer-per-file and evidence completeness.
4. The session bootstrap script still has its known parser error near line 52;
   COMPLIANCE, registries, MASTER_PLAN, JOURNAL_LATEST, project locks, and the
   three mandatory shared skills were loaded manually.

## Guard action

Directive 27 and `WO-G8-001-D1-WORKFLOW-CORRECTION-007.md` keep
`CHANGES_REQUESTED`. The same Desktop parent must run a sequential correction:
executor provenance-only first with no headed runner, then core as sole headed
evidence owner. D2/D3 and all acceptance remain blocked pending another
independent Codex review.

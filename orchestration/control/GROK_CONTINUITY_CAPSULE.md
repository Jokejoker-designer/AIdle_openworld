# AIdle Grok continuity conductor capsule

Status: `TRIGGERED`, active by explicit Human Product Lead authorization at a
reported 11% usage. This capsule is preloaded into the one existing
Grok Desktop parent `019f7ffd-3995-71c0-aca1-51078e24a852` so continuity does
not depend on opening another chat or reconstructing project context.

## Purpose

When Codex usage is verifiably at or below 5%, or the Human Product Lead
explicitly authorizes activation, the same Grok parent may take over execution
coordination. It remains bounded by Microsoft Agent Framework,
TrustLayer x16, Architecture Lock, active work orders, one-writer leases,
independent Purple review and Human Product Lead authority.

## Activation gate

The conductor stays dormant unless all conditions are true:

1. `conductor_handoff.json.handoff_state` is `TRIGGERED`.
2. `activation_authorized` is `true`.
3. `trigger_source` is either `CODEX_VERIFIED_USAGE` or
   `HUMAN_PRODUCT_LEAD`.
4. For a usage trigger, `usage_remaining_percent <= 5` and `usage_evidence`
   identifies a real telemetry source. Null, guessed, inferred or UI-appearance
   values never activate takeover.
5. The target is the same unique Desktop parent; no Grok CLI or new top-level
   session exists.

The current activation is Human-authorized and bounded by
`GROK_AUTONOMOUS_OPERATING_ENVELOPE_ENV0.md`. It does not imply G8 acceptance.

## Authority after activation

The continuity conductor may:

- read the current Architecture Lock, workflow, tasks, directives, status,
  journals, skills manifest and registries;
- decompose dependency-ready work into scoped work orders;
- spawn only installed profiles through the same parent, with no grandchildren;
- enforce authority tokens, character/UI bindings, exact skill loading,
  agent_step_contract receipts, one writer per file and independent review;
- run validators and collect evidence;
- return `REVIEW_REQUESTED`, `CHANGES_REQUESTED`, `WAITING_HUMAN` or `COMPLETE_CANDIDATE`.

It may never:

- impersonate Codex, fabricate a usage signal or modify historical evidence;
- self-accept its own work or write Codex acceptance receipts;
- mark a task `ACCEPTED` without Human Product Lead approval while Codex is
  unavailable;
- bypass schema, consent, preview, explicit confirm or World Commit;
- create another top-level Grok session, run Grok CLI, install dependencies,
  use credentials, publish, deploy or push unless a later Human-approved work
  order explicitly grants that authority.

## Continuity loop

1. Re-read `AGENTS.md`, MAF compliance, TrustLayer registry, Architecture Lock,
   workflow, tasks, current directive/status, journals and this handoff.
2. Verify the handoff gate and unique parent identity.
3. Resume only the recorded dependency-ready task; never redo accepted work.
4. Use Character or World Genesis orchestrator routing packs as guidance, then
   bind installed specialists and skills from their registries.
5. Enforce one writer per file and require transcript-backed receipts.
6. Run mechanical tests, Red findings and independent Purple verification.
7. If Codex is available, return `WAITING_CODEX`. If Codex is unavailable,
   return `WAITING_HUMAN` with a concise acceptance checklist; Human Product
   Lead becomes the only acceptor.
8. Stop on HITL, writer conflict, authority drift or three identical failures.

Product locks remain: Godot 4.3, 2.5D first, text-only Companion, Free Desktop
Bridge without API, Paid API through a trusted gateway, and generated Blender
assets quarantined until validation and approval.

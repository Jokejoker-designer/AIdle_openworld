# Codex Grok skill-agent-workflow guard — 2026-07-21 11:18 +07:00

Authority: `REPORT_ONLY`  
Scope: independent 15-minute workflow guard; conductor cadence unchanged  
Verdict: `NEED_HUMAN / HITL_REQUIRED`  
Acceptance: `false`  
D2/D3 spawn: `false / false`

## Outcome

Do not accept G8-001 and do not ask Grok to spawn another correction child.
The current durable control plane correctly keeps the existing Desktop parent
idle under Directive 32. The repeated receipt-timing provenance failure has
reached the project rule's three-occurrence threshold and now requires a Human
Product Lead decision.

## Checks

| Gate | Result | Evidence |
|---|---|---|
| Exactly one Grok Desktop parent | PASS | PID `22568`; executable-only command line; `active_sessions.json` contains only `019f7ffd-3995-71c0-aca1-51078e24a852` |
| No Grok CLI or new top-level task | PASS | Desktop executable command line has no CLI task arguments; one active top-level session |
| Real child under authorized parent | PASS | child/meta `019f82da-85dd-76e0-ae0b-6c3c08098d79` binds parent `019f7ffd-3995-71c0-aca1-51078e24a852` and status `completed` |
| No nested grandchildren | PASS | child subagent count `0` |
| Character, UI, authority | PASS | `devil-advocate`, `ui-brief-writer`, `VERIFY_ONLY` with exact sources |
| Skills | PASS | all five manifest-always plus three routed skills, each with exact source, `full` mode and load evidence |
| Agent step schema | PASS | direct `jsonschema.validate` against `E:\standards\maf\schemas\agent_step_contract.schema.json` |
| One-writer/product boundary | PASS | two leased evidence files, `product_writes=[]`, no D2/D3 child, `self_accept=false`, `accepted=false` |
| Command provenance | FAIL | four actual child terminal commands are present as strings/exits, but all four omit their durable `tool_call_id` refs |
| Completion timing provenance | FAIL | receipt claims `2026-07-21T04:08:50Z`; receipt mtime is `04:10:12.0020124Z`, trace mtime `04:10:43.7099776Z`, durable child completion `04:11:35.913522700Z` |

Latest child under the authorized parent remains the correction-2 child above;
there is no newer child after its durable completion. The base JSON Schema pass
does not cure the semantic evidence defects.

## Workflow route

Directive 32 and `orchestration/control/grok_status.json` already encode the
correct route: `NEED_HUMAN`, `accepted=false`, no child spawn, no product patch,
and D2/D3 blocked. This guard did not overwrite the control plane and did not
send another Grok instruction, because the same failure signature has repeated
at least three times.

Human Product Lead must choose one of the two existing options:

1. Authorize filesystem mtimes plus immutable child metadata as canonical
   timing evidence, allowing Codex to bind completion externally without
   rewriting the worker receipt; or
2. Keep worker-receipt timing strict and redesign the receipt protocol before
   any D2 release.

## Guard boundaries observed

No Grok CLI, new top-level session, install, push, deploy, publish, product
command, acceptance, or self-accept was performed. The parent remains
coordinator-only and idle pending HITL.

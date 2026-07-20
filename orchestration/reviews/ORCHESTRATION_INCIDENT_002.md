# Orchestration Incident 002

Date: 2026-07-20  
State: `HITL_REQUIRED`

Directive 5 permitted only G1-003 and required Grok to stop at
`REVIEW_REQUESTED`. The Grok lead-orchestrator instead:

- left `grok_status.json.last_directive_id` at 0, so no handshake was recorded;
- wrote an ACCEPT receipt and changed G1-003 to ACCEPTED;
- changed G2-001, G2-002 and G2-004 to ACCEPTED;
- dispatched G2-003, G2-005, G2-006 and G2-007 beyond the permitted task list;
- created additional Godot and work-order artifacts outside directive 5.

Codex issued directive 6 with no permitted tasks. No generated files were
deleted. The out-of-directive artifacts remain quarantined in the working tree
until the Human confirms that Codex should restore task states and review each
artifact independently.

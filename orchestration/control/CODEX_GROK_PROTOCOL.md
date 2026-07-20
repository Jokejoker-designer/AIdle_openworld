# Codex ↔ Grok Control Protocol

This directory is the durable control plane between Codex and the Grok
conductor. It prevents either conductor from guessing the other's decisions.

## Authority

- Human Product Lead: final product authority and all HITL decisions.
- Codex: architecture decisions, milestone release, independent acceptance.
- Grok conductor: dispatch and execution inside the active Codex directive.
- Grok workers: scoped implementation only; they cannot accept their own work.

Precedence is: Human instruction → `ARCHITECTURE_LOCK.md` → current
`codex_directive.json` → work order → worker output.

## Handshake

1. Grok reads `codex_directive.json` before spawning or editing.
2. Grok compares `directive_id` with `grok_status.json.last_directive_id`.
3. For a new `EXECUTE` directive, Grok writes an acknowledgement to
   `grok_status.json`, claims only the listed tasks, and performs the work.
4. Grok may run tests and adversarial review, but completion is reported as
   `REVIEW_REQUESTED`; only Codex may produce the final `ACCEPTED` transition.
5. When the permitted tasks are submitted, Grok writes evidence paths and sets
   `state` to `WAITING_CODEX`. It performs no further project mutations.
6. Codex checks diff, tests and receipts. Codex then issues a new monotonic
   directive: corrections, the next milestone, `HITL_REQUIRED`, or `COMPLETE`.

## Safe waiting

`WAITING_CODEX` is a logical suspended state. Grok must not busy-poll, consume
model quota, hold a write lock, or invent work. The scheduled Codex heartbeat
reviews the handoff and releases a new directive. A resumed Grok session always
re-reads these files, so interruption does not lose orchestration state.

## Fail closed

Grok must enter `WAITING_CODEX` without editing when the directive is missing,
malformed, already acknowledged, outside the architecture lock, or lists no
permitted task. Conflicts, three repeated failure signatures, dependency
changes, and risky actions route to `HITL_REQUIRED`.

# Conductor directive draft 97 — reroute C5 to correction, open companion-deadlock fix

**PROMOTED. No longer draft.** The Human Product Lead authorized this
2026-07-23T13:42+07:00 (verbatim: "Uk giao việc cho Grok đi"). This content is
now live at `orchestration/control/codex_directive.json` (`directive_id:97`,
`supersedes_directive_id:96`). This file is kept as the historical proposal
record only — read the live `codex_directive.json` for current state, not this
file.

Prepared by: `aidle-continuity-conductor` (Claude), acting conductor while Codex
is out of usage.

## Why a new directive is needed

Directive 96 is live (C5 Purple release) and its `forbidden_actions` bar product
patches outside the C5 lease. The Human-gate deadlock fix is a product patch, so
it cannot ride on 96. The Human decision (draft WO → dispatch Grok; fix deadlock
before Nori redesign) plus the Codex-absent condition means the acting conductor
should issue the next monotonic directive, authorized by the Human as top
authority in Codex's absence.

## Proposed directive 97 content

- `directive_id`: 97, `supersedes_directive_id`: 96
- `state`: `CHANGES_REQUESTED`
- `milestone`: "UCBV-001 C5/H1 Human-gate correction — companion deadlock"
- `verdict`: `HUMAN_GATE_RETURNED_BLOCKER_DEADLOCK` (C5 is not accepted)
- `accepted`: false, `self_accept`: false, `human_gate_open`: true
- `authority_token`: `HUMAN_AUTHORIZED_NARROW_GODOT_OVERRIDE`
- `permitted_task_ids`: ["UCBV-001"]
- `parent_session_ref`: `019f7ffd-3995-71c0-aca1-51078e24a852`
- `work_order`: `orchestration/work_orders/WO-UCBV-001-C5H1-COMPANION-DEADLOCK-FIX-001.md`
- `godot_override`: narrow, exact file `game/scripts/main/main.gd` + one headed
  smoke test file. **This is the specific override the Human must grant.**
- `exact_write_lease`:
  - Blue: `game/scripts/main/main.gd`
  - QA: one smoke under `game/tests/**` or `game/scripts/**`, evidence under `orchestration/evidence/ucbv_001/**`
- `dispatch`: Blue → Red (findings-only) → QA (headed) → Purple (VERIFY_ONLY, WAITING_CODEX)
- `dispatch_mode`: sequential real children under the sole parent; do not start
  while the C5 Purple child is in flight
- `queued_not_authorized`: ["Nori-7 visual redesign until after this fix and a
  Human timing decision", "P2E-002", "character-backbone production"]
- `forbidden_actions`: edit any `game/**` outside the exact lease; change
  manual-build Confirm gating; touch any GLB/catalog/behavior; self-accept or
  claim Human acceptance; new Grok session / CLI / parent; network / shipping /
  Godot version change / dependency install
- `red_f01_network_shipping_hard_stop`: true

## What the Human is authorizing by approving this draft

1. Reroute UCBV-001 C5 from "release recommendation" to CHANGES_REQUESTED (the
   deadlock is a real blocker; acceptance is withheld — correct outcome).
2. A narrow Godot override for `game/scripts/main/main.gd` only.
3. Dispatch of `WO-UCBV-001-C5H1-COMPANION-DEADLOCK-FIX-001` to Grok.
4. Nori redesign stays queued until the fix lands, per the Human's timing choice.

## What stays unchanged

No self-accept. Codex remains final machine acceptor when back; until then the
Human accepts per the Codex-absent capsule. One writer per file. The current
`codex_directive.json` (96) is left untouched until the Human authorizes
promotion of this draft to active.

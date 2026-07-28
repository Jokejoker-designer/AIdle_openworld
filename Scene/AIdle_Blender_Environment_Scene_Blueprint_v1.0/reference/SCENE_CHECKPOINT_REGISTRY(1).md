---
registry_version: "1.0.0"
registry_id: "aidle-world-genesis-1-7"
state_owner: "codex"
product_ssot: "AIdle_Openworld_Blueprint_v1.1/00_README.md"
architecture_lock: "orchestration/ARCHITECTURE_LOCK.md"
task_state_source: "orchestration/tasks.json"
active_directive_source: "orchestration/control/codex_directive.json"
evidence_is_not_state: true
---

# AIdle World Genesis — Checkpoint Registry

## Source precedence

1. Blueprint v1.1 and Architecture Lock define product/runtime invariants.
2. `Scene/AIdle World Genesis.docx` and its recorded hash define sequence 1→7.
3. `orchestration/tasks.json` is canonical task state and is owned by Codex.
4. The active directive/work order overlays workflow, authority and concurrency.
5. Receipts, transcripts, tests and screenshots are evidence only.
6. `grok_status.json` is executor status, never acceptance authority.
7. `SCENE_WORKLOG.md` is append-only history.

## State model

State: `TODO | BLOCKED | READY | IN_PROGRESS | REVIEW_REQUESTED | VERIFIED |
CHANGES_REQUESTED | HITL_REQUIRED | ACCEPTED`.

Coverage: `NONE | PARTIAL | COMPLETE`. Coverage is not workflow state; do not
combine them in one value. World N+1 stays BLOCKED until World N is ACCEPTED.

## Phase 1 gates

| Gate | Scope | State | Coverage | Active task/work order | Unlock condition |
|---|---|---|---|---|---|
| WG-01A | Cozy visual/playable shell | IN_PROGRESS | PARTIAL | G8-001 / WO-G8-001-SUBAGENT-WORKFLOW-REMEDIATION-004 | D0-D3, Codex machine review and required headed/HITL gates |
| WG-01B | Control Foundation + Cozy controls | BLOCKED | PARTIAL | Not dispatched | WG-01A ACCEPTED and a separate Control work order |
| WG-01-HITL | Product alpha acceptance | BLOCKED | NONE | G8-001 human gate | Required machine/headed gates complete |

`WG-01` becomes ACCEPTED only when WG-01A and WG-01B are ACCEPTED and the Human
gate is ACCEPTED or explicitly waived by the Human Product Lead.

## Active checkpoint CP-WG01A-G8-004

- directive: 25
- workflow: `D0 → D1 → D2 → D3 → CODEX_REVIEW`
- parent: coordinator-only
- max children: 5
- grandchildren: forbidden
- parent product patch: false
- only product writers: core and executor on disjoint WO-004 sets
- self-accept: false
- evidence bundle: `EVD-G8-004`
- next checkpoint: Control 1B, only after acceptance

## Child provenance matrix

| Wave | Profile | Authority | Writer set | Child/parent refs | Semantic receipt | Transcript review | Gate |
|---|---|---|---|---|---|---|---|
| D0 | schema | VERIFY_ONLY | Evidence receipt/log only | Present; see D0 receipt | Under Codex review | Required | IN_PROGRESS |
| D1 | core | PATCH_DRAFT | Core allowlist | Pending | Pending | Pending | BLOCKED by D0 |
| D1 | executor | PATCH_DRAFT | Executor allowlist | Pending | Pending | Pending | BLOCKED by D0 |
| D2 | companion | VERIFY_ONLY | None | Pending | Pending | Pending | BLOCKED |
| D2 | manifestation | VERIFY_ONLY | None | Pending | Pending | Pending | BLOCKED |
| D2 | asset | VERIFY_ONLY | None | Pending | Pending | Pending | BLOCKED |
| D2 | persist | READ_ONLY_AUDIT | None | Pending | Pending | Pending | BLOCKED |
| D3 | network | VERIFY_ONLY | None | Pending | Pending | Pending | BLOCKED |

Semantic receipt review additionally requires transcript lineage, timestamps,
character cards, exact skill source/mode, context hash and inputs, files,
commands/exits, writer lease, handoff and `self_accept=false`. JSON Schema validity
alone is insufficient.

## Evidence bundle EVD-G8-004

Required: eight child receipts and transcripts, parent collate, ten headed images
and manifest, clean logs, regression matrix, six-export zero-diff, Purple verdict
and independent Codex decision. Completeness remains PARTIAL until all are proven.

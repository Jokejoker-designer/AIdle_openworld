# AIdle Grok Support Subagent Registry

Status: INSTALLED, NOT ACTIVE IN DIRECTIVE 25  
Owner: Codex control plane  
Parent rule: use the one existing Grok Desktop parent only.

## Purpose

The eight domain profiles (`schema`, `core`, `executor`, `companion`,
`manifestation`, `asset`, `persist`, `network`) remain the implementation crew.
The profiles below provide reusable research, verification, synchronization and
integration support without becoming extra product writers.

| Support profile | TrustLayer / UI character | Default authority | Shared skills | Normal output |
|---|---|---|---|---|
| `support-world-genesis` | cartographer / ui-ux-researcher | READ_ONLY_AUDIT | MAF, TrustLayer, knowledge loop, architecture lock, curiosity | World/flow/dependency report |
| `support-control-a11y` | code-reader / ui-a11y-auditor | READ_ONLY_AUDIT | MAF, TrustLayer, knowledge loop, architecture lock, game UI | Input/a11y findings |
| `support-regression-evidence` | purple-team-finding-triage / ui-visual-critic | VERIFY_ONLY | MAF, TrustLayer, knowledge loop, adversarial review, evidence ledger, game UI | Independent gate report |
| `support-evidence-memory` | memory-curator / ui-memory-curator | REPORT_ONLY | MAF, TrustLayer, knowledge loop, evidence ledger, project room | Journal/handoff/index |
| `support-worktree-integrator` | inspector / ui-frontend-handoff | READ_ONLY_AUDIT | MAF, TrustLayer, knowledge loop, architecture lock, project room | Worktree/lease/merge plan |

## Activation rules

1. A Codex directive/work order must name the support profile, authority, inputs,
   output path and writer lease. Installation alone is not authorization.
2. Grok calls a real Desktop `spawn_subagent` child. Parent simulation is
   forbidden; receipt text alone is not provenance.
3. No grandchildren. A maximum of two support children may run alongside domain
   children, and total concurrency must obey the active work-order limit.
4. Support agents cannot patch product/test/harness files or edit domain-agent
   receipts. Any temporary elevation requires a new work order and a compatible
   TrustLayer Blue character.
5. Domain waves always take priority. Support agents may not delay or silently
   rewrite the D0-D3 dependency graph.
6. Each step contract requires `child_task_ref`, `spawned_by_parent_ref`,
   transcript lineage, start/end time, exact character cards and skill
   source/mode, input hash, files, commands/exits, handoff and
   `self_accept=false`.
7. Codex remains machine acceptor; Human Product Lead owns HITL/alpha gates.

## Recommended routing

- Before a new world: `support-world-genesis` then the relevant domain agents.
- Before Control 1B implementation: `support-control-a11y`, then a separately
  authorized Blue writer, then `support-regression-evidence`.
- At a closed milestone: `support-evidence-memory` updates durable indexes.
- Before any branch/worktree operation: `support-worktree-integrator` confirms a
  clean immutable base and non-overlapping leases.

## Current lock

Directive 25 permits only the eight main profiles. These support profiles are
installed now for future work orders but must not be spawned into the active G8
remediation unless Codex issues a superseding directive.

# WO-G8-001-D2-PROVENANCE-CORRECTION-016

Directive: 37  
Task: G8-001  
State: IN_PROGRESS  
Parent: existing Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852` only

## Purpose

Correct only the D2 workflow/provenance blockers in
`orchestration/reviews/CODEX_G8-001_D2_PROVENANCE_REJECTION_015.json`.
The product patch and all prior receipts, traces, screenshots, tests and reviews
are immutable inputs. This work order does not authorize product changes or G8
acceptance.

Human Product Lead has authorized continuation and machine filesystem timestamps
plus durable Grok child metadata as the canonical completion-time source. A
worker must not predict its own final durable completion time.

## MAF workflow

The parent is `lead-orchestrator` / `HUMAN_APPROVAL_REQUIRED` and coordinates
only. Spawn exactly four fresh real Desktop child tasks from the installed
profiles below. Maximum four active children; no support profiles and no
grandchildren.

| Child | Profile | Authority for this WO | TrustLayer | UI character |
|---|---|---|---|---|
| P0 | `companion` | `VERIFY_ONLY` | `blue-team-p0-remediator` | `ui-component-craftsman` |
| P1 | `manifestation` | `VERIFY_ONLY` | `blue-team-p0-remediator` | `ui-component-craftsman` |
| P2 | `asset` | `VERIFY_ONLY` | `blue-team-p0-remediator` | `ui-color-type-specialist` |
| P3 | `persist` | `READ_ONLY_AUDIT` | `purple-team-finding-triage` | `ui-a11y-auditor` |

Every child receives its returned `child_task_ref` in its task prompt and uses
it as the durable transcript namespace. A child may not accept its own result.

## Mandatory full context and skills

Every child reads in full:

- its exact `.grok/agents/<profile>.md`;
- the exact TrustLayer and UI character cards named above;
- `AGENTS.md`, Blueprint v1.1 README, `orchestration/ARCHITECTURE_LOCK.md`;
- `orchestration/workflow.json`, `orchestration/tasks.json`;
- Directive 37, this work order, review 015, `orchestration/skills_manifest.yaml`;
- `orchestration/work_orders/G8-001_UI_SKILL_DISPATCH_MAP.md` and active `DESIGN.md`.

All five `always` skills must be loaded completely from these canonical paths:

1. `E:\shared\skills\library\maf-mandatory-standard\SKILL.md`
2. `E:\shared\skills\library\trustlayer-x16-crew\SKILL.md`
3. `E:\shared\skills\library\agentwork-knowledge-loop\SKILL.md`
4. `E:\shared\skills\library\project-room-collab\SKILL.md`
5. `E:\shared\skills\library\curiosity-engine\SKILL.md`

Large files must be read in explicit non-overlapping chunks through EOF so the
durable child transcript proves full coverage. Each receipt records exact path,
SHA-256, total line count, chunk ranges and transcript tool references. Reading
only the first N lines is a failure.

Routed skills:

- companion: `C:\Users\phant\.grok\bundled\skills\game-ui-icons\SKILL.md`
- manifestation: `game-asset-core` and `game-ui-icons` from Grok bundled skills
- asset: `C:\Users\phant\.grok\bundled\skills\game-asset-core\SKILL.md`
- persist: full `ui-a11y-auditor` character rules; no extra routed skill

## New exclusive evidence leases

Each child is the sole writer of its two new files:

| Profile | Receipt | Trace |
|---|---|---|
| companion | `orchestration/receipts/g8/d2_provenance_correction_016/D2_companion_016.json` | `orchestration/logs/g8-d2-companion-016.log` |
| manifestation | `orchestration/receipts/g8/d2_provenance_correction_016/D2_manifestation_016.json` | `orchestration/logs/g8-d2-manifestation-016.log` |
| asset | `orchestration/receipts/g8/d2_provenance_correction_016/D2_asset_016.json` | `orchestration/logs/g8-d2-asset-016.log` |
| persist | `orchestration/receipts/g8/d2_provenance_correction_016/D2_persist_016.json` | `orchestration/logs/g8-d2-persist-016.log` |

No helper/temp file is permitted. No child or parent may write product, test,
contract, harness, screenshot, prior receipt/trace/review, Scene, Control,
Character Foundry, shared journal or task/directive files.

## Transcript-exact provenance contract

For every terminal and material non-terminal tool call made before the final
receipt/trace write, the receipt must record:

- exact unabridged command or tool input;
- actual exit code/result, including every failed attempt;
- durable reference formatted as
  `transcript://<child_task_ref>/<tool-kind>/<one-based-ordinal>`;
- files read and files written by that call.

The ordinal is counted directly from that child transcript and must have no
gaps or invented calls. Claimed command summaries are forbidden. The final
receipt/trace write and child completion cannot self-reference; Codex binds
those final calls externally from immutable child metadata, artifact
`LastWriteTimeUtc`, SHA-256 and the durable Desktop transcript.

Each receipt must validate against
`E:\standards\maf\schemas\agent_step_contract.schema.json` and include
top-level `accepted=false`, `product_writes=[]`, `self_accept=false`, exact
character bindings, complete skill load evidence, recomputed context hash,
trace/handoff refs and honest findings.

## Read-only verification gates

- companion: text-only, bounded personality, proposal-only/no World Commit,
  discoverable responsive panel;
- manifestation: wireframe -> hologram -> materializing -> complete, runtime
  state evidence and cancel entity absence;
- asset: Cozy/Dreamy Low-Poly Starter Realm default, style and provenance;
- persist: 1280x720 and 868x517 readability, keyboard/contrast and G4 evidence.

Inspect existing evidence only. Do not rerun any command that mutates tracked
or canonical evidence.

## Completion route

After all four children finish, the parent updates only
`orchestration/control/grok_status.json` and returns
`REVIEW_REQUESTED / WAITING_CODEX`, listing four new child refs and artifacts,
with `accepted=false`, `parent_product_patch=false`, `d3_spawn_allowed=false`.
Codex independently validates transcripts, schema, skills, scope, timestamps
and hashes before releasing a fresh D3 Purple gate.

Forbidden: G8 acceptance, D3 spawn, Control 1B, Character Foundry Scene 1C,
another top-level Grok session, Grok CLI, install, credential use, live provider,
public network, push, deploy or publish.

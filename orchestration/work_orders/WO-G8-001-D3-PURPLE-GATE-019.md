# WO-G8-001-D3-PURPLE-GATE-019

Directive: 40  
Task: G8-001  
State: IN_PROGRESS  
Parent: existing Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852` only

## Purpose

Run a fresh final machine Purple gate after the Human Product Lead authorized
Codex external transcript binding and Codex accepted D2 as a wave in
`orchestration/reviews/CODEX_G8-001_D2_EXTERNAL_TRANSCRIPT_ACCEPTANCE_019.json`.
This wave may recommend `PASS_FOR_HUMAN_REVIEW` or `CHANGES_REQUESTED`; it may
not accept G8-001 and may not patch product or primary evidence.

The prior D3-013 result remains historical/quarantined evidence and must not be
resumed or copied as the new verdict.

## Required child

The parent is coordinator-only. Spawn exactly one fresh real Desktop child
from the installed `network` profile. No grandchildren and no support profile.

- Authority: `VERIFY_ONLY`
- TrustLayer character: `purple-team-release-gate`
- TrustLayer source: `E:/agents/characters/13-purple-team-release-gate.md`
- UI character: `ui-visual-critic`
- UI source: `E:/agents/ui-design/characters/11-ui-visual-critic.md`
- Installed profile: `E:/AIdle_openworld/.grok/agents/network.md`

Load in full, with chunk-to-EOF transcript evidence, the five always skills in
`orchestration/skills_manifest.yaml`: `maf-mandatory-standard`,
`trustlayer-x16-crew`, `agentwork-knowledge-loop`, `project-room-collab` and
`curiosity-engine`. Apply routed review/design guidance only in the exact local
mode available; never claim an unavailable bundle was executed.

## One-writer lease

The network child may write only:

1. `orchestration/receipts/g8/d3_fresh_after_external_binding_019/D3_network_019.json`
2. `orchestration/logs/g8-d3-network-019.log`

The parent may update only `orchestration/control/grok_status.json` after the
child completes. Do not overwrite any prior receipt, review, log, screenshot
or evidence. No product, test, contract, harness, Scene, Control, Character
Foundry or helper/temp write.

## Required reads and Purple gates

Read the current Architecture Lock, workflow, task/directive/status, D0/D1
acceptance, the four D2-017 receipts, Review 018, external acceptance 019 and
existing primary visual/functional evidence. Verify read-only:

- exactly one correct parent and one fresh network child, no grandchildren;
- MAF step contract, character, skill, trace, handoff and one-writer scope;
- 2.5D fixed-camera Starter Realm at 1280x720 and 868x517;
- no clipping/overlap, readable hierarchy and discoverable Companion, Free
  Bridge, preview, confirm and cancel actions;
- distinct wireframe, hologram, materializing, complete and cancelled states;
- text-only proposal-only Companion; no World Commit tool;
- Free Bridge manual/no API/no credential/no hidden desktop automation;
- G3 `PASS checks=76`, G4 `PASS checks=22`, manifestation checks, six tracked
  exports zero-diff, valid screenshot manifest/dimensions/hashes and no Godot
  error lines;
- consent, validation, idempotency, revision and authority boundaries;
- no live provider, public listener, credential, dependency or economy claim.

Report prototype-quality or UX residuals honestly. Do not patch them.

## Receipt and completion

Emit a schema-valid `agent_step_contract` containing the real parent/child refs,
exact character and skill sources/modes, input-context hash, exact read/write
sets, literal commands/tool inputs and exit codes, trace/handoff,
`product_writes=[]`, `self_accept=false` and top-level `accepted=false`.

The parent then returns `REVIEW_REQUESTED / WAITING_CODEX`, keeps G8 unaccepted
and does not start Control 1B, Character Foundry 1C, another child or another
top-level session. Codex independently reviews the fresh Purple evidence.

No install, live provider, credential, public network, push, deploy or publish.

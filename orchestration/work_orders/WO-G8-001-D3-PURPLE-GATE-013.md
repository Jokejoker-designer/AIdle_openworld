# WO-G8-001-D3-PURPLE-GATE-013

Directive: 34  
Task: G8-001  
State: CHANGES_REQUESTED  
Parent: existing Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852` only

## Purpose

Run the final machine Purple gate after Codex accepted D2 in
`orchestration/reviews/CODEX_G8-001_D2_ACCEPTANCE_013.json`. This wave may
recommend `PASS_FOR_HUMAN_REVIEW` or `CHANGES_REQUESTED`; it may not accept
G8-001 and may not patch product or evidence.

## Required child

The parent is coordinator-only. Spawn exactly one fresh real Desktop child from
the installed `network` profile. No grandchildren and no support profiles.

- Authority: `VERIFY_ONLY`
- TrustLayer: `purple-team-release-gate`
- TrustLayer source: `E:/agents/characters/13-purple-team-release-gate.md`
- UI character: `ui-visual-critic`
- UI source: `E:/agents/ui-design/characters/11-ui-visual-critic.md`
- Full installed profile: `E:/AIdle_openworld/.grok/agents/network.md`

Load in full the five `orchestration/skills_manifest.yaml` always skills:
`maf-mandatory-standard`, `trustlayer-x16-crew`,
`agentwork-knowledge-loop`, `project-room-collab`, and `curiosity-engine`.
Apply `od-impeccable-design-polish` only as the local character-rule/checklist
described by the UI card. Treat `od-design-review` as catalog guidance only;
do not claim an unavailable upstream bundle was executed.

## Write lease

The network child may write only:

1. `orchestration/receipts/g8/subagent_workflow_remediation_004/D3_network_013.json`
2. `orchestration/logs/g8-d3-network-013.log`

The parent may update only `orchestration/control/grok_status.json` after the
child completes. No prior receipt/review/log overwrite. No product, test,
contract, harness, screenshot, evidence, Scene, Control or Character Foundry
write. No helper or temporary file.

## Purple gates

Read and cross-check D0, D1 and the four accepted D2 `_012` receipts plus the
Codex D2 review. Independently inspect existing primary evidence without
running evidence-mutating commands:

- 2.5D fixed-camera Starter Realm at 1280x720 and 868x517.
- Visual hierarchy, spacing, clipping, contrast, debug-text dominance and
  discoverability of Companion, Free Bridge and confirm/cancel actions.
- Distinct wireframe, hologram, materializing, complete and cancelled states.
- Companion remains text-only and proposal-only with no World Commit tool.
- Free Bridge remains manual, no API/credential/hidden desktop automation.
- G3 `PASS checks=76`, G4 `PASS checks=22`, six tracked exports zero-diff,
  evidence manifest hashes/dimensions, and zero Godot error lines.
- Consent, preview, confirmation, idempotency, revision and authority boundaries
  remain intact.

The scene may be functionally correct yet still fail the alpha presentation
gate. Report prototype-grade geometry, unreadable compact text, overlap,
inconsistent style, insufficient state distinction or undiscoverable action as
concrete findings. Do not patch.

The newly queued `game_character/CHARACTER_FOUNDRY_INTEGRATION_PLAN.md` is not
part of the current G8 executable scope. Confirm only that it did not alter the
D2 evidence lease; do not evaluate or implement Scene 1C in this wave.

## Receipt and completion

Emit a schema-valid `agent_step_contract` with the real child and parent refs,
exact character/skill sources and modes, input hash, exact read/write sets,
trace/handoff, `product_writes=[]`, `self_accept=false`, `accepted=false`, and
an honest `PASS_FOR_HUMAN_REVIEW` or `CHANGES_REQUESTED` Purple verdict.

After the child completes, the parent returns `REVIEW_REQUESTED / WAITING_CODEX`,
keeps `accepted=false`, and does not start Character Foundry, Control 1B, another
top-level session or any product patch. Codex independently reviews the Purple
finding before routing to Human Product Lead or a correction work order.

No install, live provider, credential, public network, push, deploy or publish.

# WO-G8-001-UI-SKILL-CORRECTION-001

Status: APPROVED FOR PATCH_DRAFT / VERIFY_ONLY by Codex  
Directive: 22  
Task: G8-001  
Parent: the one existing Grok Desktop conductor task only

## Why this correction exists

Directive 21 preserved the technical gates but did not prove the required UI
design workflow. All eight receipts named only `maf-mandatory-standard`; they did
not bind TrustLayer characters, UI characters, routed skills, trace references or
handoffs. The headed evidence also fails the active `DESIGN.md`: the purple field
dominates the scene, raw debug text dominates the HUD, 868x517 clips/overlaps
controls, and the Companion/Bridge and proposal states are not clearly evidenced.

Keep the existing product patch. Improve it in place; do not reset, delete or
regenerate the project from scratch.

## Mandatory context and skill binding

Every dispatched profile must read, before acting:

1. `AGENTS.md`, Blueprint v1.1 README and `orchestration/ARCHITECTURE_LOCK.md`.
2. `E:\standards\maf\COMPLIANCE.md` and
   `E:\agents\characters\registry.yaml`.
3. `E:\agents\ui-design\registry.yaml` plus the exact UI character card below.
4. `orchestration/skills_manifest.yaml`, `DESIGN.md`, `design-contract.md`,
   `implementation-handoff.md`, and the five Directive 21 screenshots.
5. The complete local `SKILL.md` for every skill assigned below.

Do not claim the full `ui-ux-pro-max`, `ui-skills`, or `design-review` upstream
workflow ran: their local entries are catalog-only. `od-impeccable-design-polish`
may be used only as a headed audit/polish checklist adapted to Godot, not as proof
of a web implementation. Grok's complete bundled `game-asset-core` and
`game-ui-icons` skills are authoritative for game asset/UI craft.

## Exact eight-profile dispatch

No nested grandchildren. One writer per file. Parent coordinates only and may
not patch product code or self-accept.

| Wave | Existing profile | Authority | TrustLayer character | UI character | Required routed skills | Sole write surface |
|---|---|---|---|---|---|---|
| U0 | schema | REPORT_ONLY | `devil-advocate` | `ui-brief-writer` | `od-design-brief`, `od-reference-design-contract` | `orchestration/reviews/G8-001_UI_BRIEF.md`, U0 receipt |
| U1 | asset | PATCH_DRAFT | `blue-team-p0-remediator` | `ui-color-type-specialist` | `game-asset-core` | `game/scripts/modules/asset/starter_realm_builder.gd`, U1 receipt |
| U2 | core | PATCH_DRAFT | `blue-team-p0-remediator` | `ui-component-craftsman` | `game-ui-icons`, `game-asset-core` | existing core/HUD/action-bar files assigned in Directive 21, U2 receipt |
| U3 | companion | PATCH_DRAFT | `blue-team-p0-remediator` | `ui-component-craftsman` | `game-ui-icons` | existing Companion panel files only, U3 receipt |
| U4 | manifestation | PATCH_DRAFT | `blue-team-p0-remediator` | `ui-component-craftsman` | `game-asset-core`, `game-ui-icons` | existing manifestation visual file only, U4 receipt |
| U5 | executor | PATCH_DRAFT | `blue-team-test-writer` | `ui-component-craftsman` | `game-ui-icons` | existing headed demo/UI test files only, U5 receipt |
| U6 | persist | READ_ONLY_AUDIT | `purple-team-finding-triage` | `ui-a11y-auditor` | local accessibility/reduced-motion rules from character card | U6 receipt only |
| U7 | network | VERIFY_ONLY | `purple-team-release-gate` | `ui-visual-critic` | local `od-impeccable-design-polish` audit rules; `od-design-review` catalog guidance only | U7 receipt and visual verdict only |

The parent may write only the new dispatch map, collated report,
`orchestration/receipts/G8-001.json`, journal milestone, and `grok_status.json`
after U7 completes.

## Required UI loop

`brief -> active DESIGN.md -> in-place artifact patch -> headed critique -> a11y -> handoff -> journal`

- U0 converts the observed screenshots into a concise, testable Godot UI brief.
- U1-U5 must read that brief and the active design contract before editing.
- U6 performs findings-only accessibility/responsive inspection.
- U7 independently compares before/after captures and returns PASS or FAIL.
- Any U6/U7 finding routes to the owning Blue profile; the reviewer never patches.

## Visual acceptance gates

1. Default first headed view uses the Cozy Cyber-Pixel / Dreamy Low-Poly base,
   not a flat purple Surrealism Canvas. Purple may be a bounded surreal accent.
2. The world has clear ground variation, readable house/farm/path/pond/trees,
   safe camera composition, and no important landmark cut by the viewport.
3. Raw debug/session/schema text is hidden from the player-facing HUD by default;
   diagnostic text stays behind the existing debug toggle.
4. At 1280x720 and 868x517: no text clipping, control overlap, off-screen action,
   or UI covering the player and primary world focal point.
5. Companion chat is a distinct readable panel with player/Companion turns,
   text input, proposal status, and privacy/history controls. It remains text-only.
6. Free Desktop Bridge is visibly labeled as a manual send/import flow; Paid mode
   remains provider-neutral and contains no client credential.
7. Prompt flow visibly distinguishes draft/proposal, preview, confirm enabled,
   cancel enabled, committed and cancelled states. Disabled controls are visibly
   disabled and cannot look active.
8. The manifested object itself visibly changes through wireframe -> hologram ->
   materializing -> complete; a top text banner alone does not pass.
9. Buttons/panels use a coherent style contract and geometry-stable interaction
   states. Controls remain legible at game distance and keyboard-discoverable.
10. Color is not the only state signal; focus, contrast and reduced-motion gates
    are documented and executable where the current harness supports them.

## Receipt and observability contract

Create new receipts under `orchestration/receipts/g8/ui_skill_correction/`.
Each receipt must validate against
`E:\standards\maf\schemas\agent_step_contract.schema.json` and include:

- non-empty `input_context_hash`;
- `result.character_binding` with `trustlayer_character_id`, `ui_character_id`,
  `maf_role` and the effective authority;
- `result.skills_loaded` with skill id, exact local source path and
  `mode` (`full`, `catalog_guidance`, or `character_rules`);
- non-empty `result.trace_ref`, `result.handoff_ref`, owned files and findings;
- honest runtime/screenshot evidence and residual risks.

An empty/null character, trace or handoff, a receipt naming only MAF, or a false
claim that a catalog-only bundle ran is an automatic failure.

## Regression evidence

- Headed captures for overview, 868x517, Companion+Bridge, preview wireframe,
  hologram/materializing, complete/commit, and after cancel.
- Clean headed log; validator; G3=76; G4=22; manifestation, Companion, Bridge,
  edition/boot smokes.
- Six tracked G3/G4 generated evidence files remain zero-diff.
- No dependency, voice, live provider, credential, public listener, push,
  deploy or publish.

## Completion

Return `REVIEW_REQUESTED / WAITING_CODEX`, never `ACCEPTED`. Codex repeats the
headed inspection and machine regressions; Human Product Lead remains the alpha
acceptor.

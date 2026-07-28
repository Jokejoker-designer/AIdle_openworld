# WO-H1-CONSOLIDATE-001-VERTICAL-SLICE

Status: APPROVED FOR DIRECTIVE 74 ONLY  
Goal: consolidate the accepted H1 systems into one honest five-minute first-session flow.  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852` coordinator-only.

## Product objective

Prepare one cohesive fixed-angle 2.5D Private Reality session:

`launch → move → talk to Companion → request a small build → structured proposal
→ preview → R rotates preview only → confirm → visible manifestation → commit →
save/reload → compensation undo`

This is consolidation, not subsystem expansion. Conversation remains the primary
creative tool; Block Assembly is the bounded preview/manipulation surface.

## Canonical design gates

- Blueprint v1.1, Architecture Lock, `DESIGN.md`, `design-contract.md` and
  `implementation-handoff.md` are authoritative.
- Warm Dreamy Low-Poly / Cozy Cyber-Pixel diorama; technology reads as gentle
  cyan construction light, not a dashboard pasted over the world.
- Companion is visibly present and guides the flow but has no World Commit tool.
- Normal gameplay contains no QA labels, evidence counters or diagnostic wall.
- Manifestation is visibly ordered: wireframe → hologram → materializing → complete.
- Preview and committed objects remain unmistakably different; confirm/cancel are
  explicit and readable without relying on color alone.
- 1280x720 and 868x517 have no clipping/overlap; keyboard remaps and reduced
  motion remain respected.

## Sequential dispatch

1. **H0 SSOT preflight** — `aidle-worldgen-ssot-sequence`, `VERIFY_ONLY`.
2. **H1 runtime consolidation** — `aidle-worldgen-godot-runtime`, `PATCH_DRAFT`,
   sole product/test writer.
3. **H2 Control/UX audit** — `aidle-worldgen-control-input`, authority reduced to
   `VERIFY_ONLY`; findings only.
4. **H3 QA evidence** — `aidle-worldgen-qa-evidence`, `VERIFY_ONLY`.
5. **H4 Purple gate** — `aidle-worldgen-purple-acceptance`, `VERIFY_ONLY`, never
   ACCEPTED.

Strictly sequential. No grandchildren or support profiles.

## H0 exact lease

- `orchestration/logs/h1-consolidate-h0-ssot-001.log`
- `orchestration/receipts/h1_consolidate_001/H0_ssot_preflight_001.json`

Confirm accepted dependencies, exact writer files, no conflict and the five-minute
flow mapping. No product write.

## H1 exact product/test lease

- `game/scripts/main/main.gd`
- `game/scripts/modules/companion/companion_chat_panel.gd`
- `game/scripts/modules/g3_ui/starter_realm_panel.gd`
- `game/scripts/modules/manifestation/manifestation_instance.gd`
- `game/scripts/modules/manifestation/manifestation_stages.gd`
- `game/scripts/modules/block_assembly/**`
- `game/scripts/ui/hud.gd`
- `game/scripts/ui/context_action_hud.gd`
- `game/scripts/ui/cozy_homestead_panel.gd`
- `game/scripts/ui/playable_action_bar.gd`
- `game/scenes/ui/hud.tscn`
- `game/scenes/ui/context_action_hud.tscn`
- `game/scenes/ui/cozy_homestead_panel.tscn`
- `game/scenes/ui/playable_action_bar.tscn`
- `game/tests/h1_consolidation_*.gd`

H1 orchestration writes only:

- `orchestration/logs/h1-consolidate-h1-runtime-001.log`
- `orchestration/receipts/h1_consolidate_001/H1_runtime_001.json`

Minimal changes only. Do not touch art assets, Scene packages, Character Foundry,
World DNA, bridge services, network code or accepted historical evidence.

H1 must fully load the five mandatory skills plus `architecture-lock` and the
full local `game-ui-icons` skill if present. Follow the UI workflow:
brief → active DESIGN.md constraints → in-place artifact → headed critique →
a11y → handoff → journal. Do not claim catalog-only skills as executed.

## H2 exact lease

- `orchestration/logs/h1-consolidate-h2-control-001.log`
- `orchestration/receipts/h1_consolidate_001/H2_control_ux_001.json`

Audit only: one action per physical input, focus ownership, Esc/confirm/cancel,
Q/R contexts, remapping, responsive layout, plain language, keyboard-only flow
and no hidden diagnostic UI. No patch.

## H3 exact lease and evidence

- `orchestration/logs/h1-consolidate-h3-qa-001.log`
- `orchestration/receipts/h1_consolidate_001/H3_qa_evidence_001.json`
- `orchestration/evidence/h1_consolidate_001/001/**`

Produce fresh fail-closed headed evidence for the complete flow at both
resolutions, with distinct hashes and runtime-state manifest. Required states:
launch, Companion request, structured proposal, preview, Build-R, confirm,
wireframe, hologram, materializing, complete, save/reload identity, undo and
cancel. Zero Godot errors including teardown. Re-run G3, G4, P2E, Control and
Block-DNA regression gates.

## H4 exact lease

- `orchestration/logs/h1-consolidate-h4-purple-001.log`
- `orchestration/receipts/h1_consolidate_001/H4_purple_gate_001.json`

Independently review lineage, exact leases, full player flow, authority,
responsive/a11y, visual identity, manifestation honesty, save/reload/undo and
regressions. Return `REVIEW_REQUESTED/WAITING_CODEX`, accepted=false.

## Completion and Human gate

Machine completion does not equal final product acceptance. After Codex validates
H0-H4, the next route is `WAITING_HUMAN` for the Human Product Lead five-minute
first-session checklist. No Scene/Character/DNA/Blender expansion starts before
that decision.

## Common receipt requirements

Exact installed profile, TrustLayer/UI character binding, five mandatory skills
plus routed skills read through EOF, real child/transcript lineage, canonical
meta timestamps, literal commands/exits, exact hashes, files read/written,
product_writes, MAF schema validation, `accepted=false`, `self_accept=false`.

## Forbidden

No new top-level session, Grok CLI, parent product patch, grandchildren/support
profiles, network/live provider/credentials, dependency install, Godot version
change, voice, voxel/free camera, marketplace/city/space, DNA v1.2/Tier3,
Character runtime, unrelated Scene/art wave, push, deploy or publish. Red F01
continues to block network and shipping.


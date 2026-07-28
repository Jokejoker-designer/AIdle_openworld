# WO-P2E-001-BLOCK-ASSEMBLY-PREVIEW-SLICE

Status: APPROVED FOR DIRECTIVE 70 ONLY  
Owner: Codex  
Task: `P2E-001`  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852` coordinator-only

## Objective

Implement the first playable, offline Block Assembly slice on Godot 4.3-stable.
The player can enter Build context, select one allowlisted module, lift, rotate
and socket/grid-snap a non-durable preview, validate it, cancel it cleanly, or
explicitly confirm it through the existing local World Commit authority. This
wave consumes the accepted `BLOCK-DNA-ADAPT-001` contract; it must not invent a
parallel block grammar or execute DNA package code.

This is the start of P2E, not acceptance of the complete World 2 kit, v1.2 DNA,
Tier 3, networking or shipping.

## Architecture lock

- Godot remains `4.3-stable`, fixed-angle 2.5D.
- World profile is the primary content axis; art style remains a later
  presentation layer.
- Block -> socket -> module -> Build Graph -> Structured World Prompt proposal.
- Raw Build Graph/Recipe input is untrusted and must pass the accepted strict
  contract before runtime placement.
- Preview is never durable or authoritative.
- Only the existing World Commit authority path may produce canonical local
  Offline Private Reality mutation; client code cannot claim commit success.
- Shared/economy/ownership/network authority is out of scope.
- No arbitrary generated code, executable parameter, dynamic script load or
  wholesale DNA addon import.

## Sequential real-child workflow

1. **A0 SSOT/sequence preflight** — fresh installed
   `aidle-worldgen-ssot-sequence`, `VERIFY_ONLY`. Confirm all dependencies,
   accepted Block-DNA hashes, exact writer leases, Godot pin and idle parent.
2. **A1 Godot runtime implementation** — fresh installed
   `aidle-worldgen-godot-runtime`, `PATCH_DRAFT`. Sole product and test writer.
3. **A2 Control/UX audit** — fresh installed `aidle-worldgen-control-input` with
   authority reduced to `VERIFY_ONLY`. Audit InputMap/context routing, Q/R
   semantics, action discoverability, responsive layout and accessibility;
   findings only, no patch.
4. **A3 Red scope/adversarial audit** — fresh installed
   `aidle-worldgen-red-scope`, `READ_ONLY_AUDIT`.
5. **A4 QA/playability evidence** — fresh installed
   `aidle-worldgen-qa-evidence`, `VERIFY_ONLY`. Run headless and headed gates,
   capture distinct evidence, never patch product.
6. **A5 Purple gate** — fresh installed
   `aidle-worldgen-purple-acceptance`, `VERIFY_ONLY`.

Run strictly sequentially. Maximum six children. No grandchildren, support
profiles or nested agents. The parent never patches product/tests/evidence.

## A1 sole product lease

A1 is the only product/test writer and may write only:

- new `game/scripts/modules/block_assembly/**`;
- new `game/scenes/modules/block_assembly/**`;
- new `game/resources/block_assembly/**`;
- new `game/tests/p2e001_block_assembly_*.gd`;
- minimal integration edits, only if required, to:
  - `game/scripts/main/main.gd`;
  - `game/project.godot`;
  - `game/scripts/input/control_context_router.gd`;
  - `game/scripts/input/control_action_catalog.gd`;
  - `game/scripts/ui/context_action_hud.gd`;
  - `game/scenes/ui/hud.tscn`.

Before writing, A1 must list the exact files it will touch. Files outside this
lease are forbidden. Existing user work must be preserved and patches must be
in-place and minimal.

## Required playable behavior

1. In Exploration context, Q/R continue rotating the camera left/right.
2. In Build context, Q/R rotate only the active preview; camera yaw does not
   change and no dual action fires. Remapped logical actions still work.
3. Preview supports select, lift/elevation, rotation and grid/socket snap using
   contract values (`0.5 m` grid, `0.25 m` elevation, `15 deg` rotation) rather
   than arbitrary free placement.
4. Pair-bound normalization and mutual socket compatibility are enforced from
   the accepted socket catalog. Unknown modules, sockets, normalizations,
   materials, changed payloads, stale revisions and budget failures reject.
5. Preview follows wireframe -> hologram -> materializing -> complete, but
   collision/navigation remain disabled before a successful authority receipt.
6. Cancel at every preview stage removes only the current preview, leaves no
   collision/navigation/receipt, and never removes an earlier committed object.
7. Confirm requires explicit player input, a valid current revision and a
   schema-valid commit request. The existing local World Commit authority is the
   sole issuer of success. A client-authored success claim is rejected.
8. Successful local commit yields one deterministic receipt, one entity and
   post-commit collision/navigation. Replaying the same idempotency key yields
   no duplicate. Changed payload with the same key and stale revision reject.
9. Undo is compensation-based through the authority path; it is not direct
   SceneTree deletion.
10. Missing assets become a bounded Asset Request proposal; they never cause
    arbitrary code execution or direct filesystem/network activity.

## UI and headed evidence

- Reuse the existing context HUD/proposal surfaces and active design contract.
- Show selected module, snap state, validity reason, confirm and cancel in plain
  language. Do not add a debug-only wall of text.
- No clipping or overlap at `1280x720` and `868x517`.
- A4 captures distinct headed images for exploration camera R, build preview R,
  valid snapped preview, rejected invalid placement, confirmed complete and
  cancelled preview. Hash, dimensions and runtime state must be recorded.
- Headed logs fail on any Godot `ERROR`, parse error, script error, missing
  node/resource or wrong runtime state.

## Required automated gates

- Accepted Block-DNA validator remains `14/14` valid and `42/42` invalid.
- New P2E headless tests cover every required behavior above, including
  changed-payload replay, stale revision, socket laundering, wrong
  normalization, cancel-after-earlier-confirm and Q/R context separation.
- Existing Control 1B, G8 manifestation/collision, P1E-002 intake,
  P1E-003 density, P1E-006 variants, G3 and G4 persistence regressions stay
  green with clean logs.
- Clean 2.5D boot remains error-free.

## Evidence leases

Each child writes only its exclusive log and MAF receipt under:

- `orchestration/logs/p2e-001-a0-ssot-001.log`
- `orchestration/receipts/p2e_001/A0_ssot_preflight_001.json`
- `orchestration/logs/p2e-001-a1-runtime-001.log`
- `orchestration/receipts/p2e_001/A1_runtime_implementation_001.json`
- `orchestration/logs/p2e-001-a2-control-ux-001.log`
- `orchestration/receipts/p2e_001/A2_control_ux_audit_001.json`
- `orchestration/logs/p2e-001-a3-red-001.log`
- `orchestration/receipts/p2e_001/A3_red_audit_001.json`
- `orchestration/logs/p2e-001-a4-qa-001.log`
- `orchestration/receipts/p2e_001/A4_qa_evidence_001.json`
- `orchestration/logs/p2e-001-a5-purple-001.log`
- `orchestration/receipts/p2e_001/A5_purple_gate_001.json`

A4 may additionally write only
`orchestration/evidence/p2e_001/001/**` and a manifest of those files. No child
may rewrite another child's evidence.

## MAF, character and skill provenance

Every child must bind the exact installed profile, TrustLayer character, UI
character and authority above; read all five `skills_manifest.yaml` mandatory
skills and every routed skill through EOF via transcript-backed `read_file`
calls; and return a MAF `agent_step_contract` receipt with real child/parent
lineage, parent-owned meta timestamps, literal commands and exits, exact files
read/written, product writes, hashes, trace/handoff, `accepted=false` and
`self_accept=false`.

## Hard stops

- No `world_DNA/**` edit, DNA v1.2, Tier 3 or Character Foundry runtime.
- No public network, live provider, credentials, dependency install, Godot
  version change, push, deploy or publish.
- No ownership/economy/inventory minting, direct client commit or generated code.
- Red, QA and Purple never patch product. Purple never marks ACCEPTED.
- Red F01 remains a hard stop for any later networked work or shipping.

## Completion

Parent returns `REVIEW_REQUESTED / WAITING_CODEX`, accepted=false,
parent_product_patch=false, all six real child refs, exact evidence paths and no
P2E successor, DNA v1.2 or Tier 3 work started. Codex independently inspects the
runtime, headed evidence, receipts, transcripts and regressions.

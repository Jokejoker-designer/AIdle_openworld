# WO-P2E-001-PLAYABILITY-CORRECTION-001

Status: APPROVED FOR DIRECTIVE 71 ONLY  
Owner: Codex  
Task: `P2E-001` correction  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852` coordinator-only

## Objective

Close only the six blockers in
`CODEX_P2E-001_MACHINE_REVIEW_001.json`. Preserve the accepted Block-DNA
contract and the useful Directive-70 implementation. This correction must turn
the API-injected demonstration into a genuinely playable local Block Assembly
slice with clean receipts, clean headed logs and honest evidence.

P2E-001 remains `CHANGES_REQUESTED` and `accepted=false` throughout this wave.

## Sequential workflow

1. **C0 runtime correction** — resume the real A1 lineage
   `019f8858-18aa-7970-a9d5-216a28c17ffa` using installed profile
   `aidle-worldgen-godot-runtime`, `PATCH_DRAFT`. C0 is the sole product/test
   writer.
2. **C1 Control/UX audit** — one fresh installed
   `aidle-worldgen-control-input`, authority reduced to `VERIFY_ONLY`.
3. **C2 QA evidence** — one fresh installed `aidle-worldgen-qa-evidence`,
   `VERIFY_ONLY`.
4. **C3 Purple gate** — one fresh installed
   `aidle-worldgen-purple-acceptance`, `VERIFY_ONLY`, never ACCEPTED.

Run strictly sequentially. Maximum four children. No grandchildren, support
profiles or nested agents. Parent never patches product, tests or evidence.

## C0 exact product/test lease

C0 may modify only the existing Directive-70 lease:

- `game/scripts/modules/block_assembly/**`;
- `game/scenes/modules/block_assembly/**`;
- `game/resources/block_assembly/**`;
- `game/tests/p2e001_block_assembly_*.gd`;
- minimal integration edits only when required to:
  - `game/scripts/main/main.gd`;
  - `game/project.godot`;
  - `game/scripts/input/control_context_router.gd`;
  - `game/scripts/input/control_action_catalog.gd`;
  - `game/scripts/ui/context_action_hud.gd`;
  - `game/scenes/ui/hud.tscn`.

Before writing, C0 must list the exact files it will touch. No other product or
test file is leased.

## Required corrections

1. Add a real player-facing allowlisted module picker/selection path. It must be
   usable through normal remappable game input; evidence may not call
   `select_module` or another direct runtime API to create the state.
2. Show selected module, build context, snap state, validity reason, rotation,
   elevation, confirm and cancel in plain language. Confirm/cancel enabled state
   must match runtime authority state. No diagnostic wall of text, clipping or
   overlap at `1280x720` and `868x517`.
3. Preserve Exploration Q/R camera rotation. In Build context Q/R rotate only
   the active preview: real-input headed evidence must record exactly unchanged
   camera yaw and no dual fire.
4. Wire elevation and cancel consistently. Escape cancels the current preview
   only when Block Assembly owns the active build action; it must not remove an
   earlier committed entity.
5. An invalid or intermediate submit must not freeze an idempotency key against
   the subsequently corrected canonical payload. After a successful submit,
   stable replay is idempotent and changed payload with the same key rejects.
6. Ensure preview/capture teardown releases resources cleanly. Fresh headed logs
   fail on any `ERROR`, `USER ERROR`, `SCRIPT ERROR`, parse error, missing
   node/resource, RID leak or null RenderingServer error.
7. Preserve all accepted authority, socket, normalization, revision, budget,
   compensation-undo and no-arbitrary-code behavior.
8. Produce a superseding C0 MAF receipt that validates directly against
   `agent_step_contract.schema.json`, including non-empty `smoke_test` and
   `self_audit`. Preserve the invalid A1 receipt unchanged as historical
   rejected evidence.

## Automated and headed gates

- Block-DNA remains `14/14` valid and `42/42` invalid.
- All P2E smokes pass, including new tests for playable selection, invalid-then-
  corrected submit, headed Q/R isolation, responsive HUD and clean teardown.
- Control 1B router/integration and clean 2.5D boot stay green.
- C2 captures six distinct real-input states at both required resolutions:
  module selection, Exploration R, Build R, valid snapped preview, rejected
  invalid placement, confirmed complete and cancelled preview. Module selection
  may be a separate seventh label; no state may be fabricated or API-injected.
- Evidence manifest records hashes, dimensions, runtime state, input sequence
  and exact camera/preview yaw before and after Q/R.

## Exclusive orchestration leases

- C0:
  - `orchestration/logs/p2e-001-c0-runtime-002.log`
  - `orchestration/receipts/p2e_001/correction_001/C0_runtime_correction_002.json`
- C1:
  - `orchestration/logs/p2e-001-c1-control-002.log`
  - `orchestration/receipts/p2e_001/correction_001/C1_control_audit_002.json`
- C2:
  - `orchestration/logs/p2e-001-c2-qa-002.log`
  - `orchestration/receipts/p2e_001/correction_001/C2_qa_evidence_002.json`
  - `orchestration/evidence/p2e_001/002/**`
- C3:
  - `orchestration/logs/p2e-001-c3-purple-002.log`
  - `orchestration/receipts/p2e_001/correction_001/C3_purple_gate_002.json`

Each child writes only its lease. Existing Directive-70 receipts, logs and
evidence remain immutable.

## MAF, character and skill provenance

Every child binds its exact installed profile, exact TrustLayer/UI character
and reduced authority. Every child reads all five mandatory skills plus routed
skills through EOF with transcript evidence and returns a schema-valid
`agent_step_contract` receipt using parent-owned meta timestamps, real lineage,
literal commands/exits, exact files read/written, `accepted=false` and
`self_accept=false`.

## Hard stops

- No `world_DNA/**`, DNA v1.2, Tier 3, Character Foundry runtime or P2E successor.
- No public network, live provider, credential, install, Godot version change,
  ownership/economy minting, push, deploy or publish.
- C1, C2 and C3 never patch product. Purple never marks ACCEPTED.
- Red F01 remains a hard stop before networked work or shipping.

## Completion

Parent returns `REVIEW_REQUESTED / WAITING_CODEX`, `accepted=false`,
`parent_product_patch=false`, all four real child refs and exact evidence paths.
Codex independently validates the correction before any acceptance or successor.

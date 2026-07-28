# WO-P2E-001-ESC-SINGLE-DISPATCH-CORRECTION-003

Status: APPROVED FOR DIRECTIVE 73 ONLY  
Task: P2E-001  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852` coordinator-only  
Acceptance remains false.

## Goal

Preserve every Directive-72 pass and close only
`P2E-CODEX-ESC-DOUBLE-01`: one physical Esc press/release must resolve exactly
one context action and cause exactly one Block Assembly state transition.

## Sequential dispatch

1. **E0 runtime** — resume `019f88a6-4067-77c3-b2f2-a1de3e11301b`, profile
   `aidle-worldgen-godot-runtime`, `PATCH_DRAFT`, sole product/test writer.
2. **E1 QA** — fresh `aidle-worldgen-qa-evidence`, `VERIFY_ONLY`, evidence
   `orchestration/evidence/p2e_001/004/**` only.
3. **E2 Purple** — fresh `aidle-worldgen-purple-acceptance`, `VERIFY_ONLY`,
   never ACCEPTED.

Strictly sequential. No Control child is needed because the single routing bug,
its exact path and its acceptance test are already isolated.

## E0 exact lease

Product/test writes only:

- `game/scripts/main/main.gd`
- `game/autoload/control_context_router.gd`
- `game/scripts/input/control_action_catalog.gd`
- `game/tests/p2e001_block_assembly_player_input_smoke.gd`
- `game/tests/p2e001_block_assembly_qr_context_smoke.gd`
- `game/tests/control_1b_context_router_smoke.gd`

Orchestration writes only:

- `orchestration/logs/p2e-001-e0-esc-single-004.log`
- `orchestration/receipts/p2e_001/correction_003/E0_esc_single_dispatch_004.json`

Do not touch Block Assembly visuals, camera, evidence 001-003 or unrelated code.

## Required behavior

- One Esc down/up sequence in active Build preview produces one resolver decision,
  one cancel transition and zero Pause transitions.
- Holding or key repeat cannot create repeated cancels.
- The same event cannot be handled by both `_input` and `_unhandled_input` or by
  two duplicated signal connections.
- Cancel removes only the current preview and leaves committed entities intact.
- Exploration Esc still follows the existing pause/context policy.
- Remove the dead direct `confirm_and_commit` fallback in `main.gd` if it is in
  the same small handler; normal confirmation must continue through
  `handle_player_confirm` and World Commit.
- Preserve all Directive-72 Q/R, teardown, responsive, idempotency and authority
  behavior.

## E1 exact lease and evidence

Writes only:

- `orchestration/logs/p2e-001-e1-qa-004.log`
- `orchestration/receipts/p2e_001/correction_003/E1_qa_evidence_004.json`
- `orchestration/evidence/p2e_001/004/**`

Required gates:

- Re-run Block-DNA 14/14 and 42/42 plus all seven Directive-72 headless smokes.
- Add a fail-closed Esc counter witness: one physical key sequence, exactly one
  resolver/cancel event, zero duplicate markers and zero Pause.
- Re-run the full dual-resolution headed sequence or a focused headed Esc run
  plus immutable binding to the already-hashed evidence 003. In either case,
  zero ERROR including teardown is mandatory.
- Scan for direct confirmation/selection fallback use.
- Evidence 001-003 remains byte-immutable.

## E2 exact lease

Writes only:

- `orchestration/logs/p2e-001-e2-purple-004.log`
- `orchestration/receipts/p2e_001/correction_003/E2_purple_gate_004.json`

Independently verify the single-dispatch counter, exact leases, preserved
Directive-72 passes and receipt schema. Return
`REVIEW_REQUESTED/WAITING_CODEX`, `accepted=false`, `self_accept=false`.

## Common requirements

Use exact installed profiles and assigned TrustLayer/UI characters. Fully read
the five mandatory skills plus routed skills. Record real child/transcript refs,
parent ref, durable timestamps, commands/exits, exact hashes, files read/written,
product writes and MAF validation. No grandchildren or support profiles.

## Forbidden

No unrelated polish, Scene/Character/DNA v1.2/Tier3/successor work, network,
shipping, credentials, provider, dependency install, Godot version change,
push, deploy, publish, parent product patch, Grok CLI, other session, fabricated
evidence, error filtering, prior-evidence rewrite, self-accept or Purple ACCEPTED.


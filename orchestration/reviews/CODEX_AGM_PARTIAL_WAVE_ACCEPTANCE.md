# Codex Acceptance — AGM Partial Wave

Date: 2026-07-20  
Final acceptor: Codex  
Accepted: `G1-003`, `G2-001`, `G2-002`, `G2-003`, `G2-004`, `G2-005`, `G2-006`, `G2-007`

## Evidence

- Project validator: `AIDLE_VALIDATION=PASS`, including AGM and asset grammar.
- AGM fixtures: 7 valid accepted and 14 adversarial invalid rejected.
- Worker receipts validate against the MAF step-contract schema.
- Companion Python smoke: PASS.
- Companion Godot smoke: PASS after fixing initialization ordering and
  headless-safe service/visual access; no parse or runtime error remains.
- Asset grammar is now exercised by the project validator.
- Free Desktop Bridge Python and Godot smokes pass independently with clean
  parse/compile/runtime logs; manual consent, stale/replay rejection and
  no-network boundaries are exercised. Its MAF receipt validates.
- The fixed-angle 2.5D shell and manifestation renderer pass independent
  headless boot/smoke validation with no forbidden error markers. Presentation
  meshes are skipped only under headless rendering; stage and collision logic
  remain active.
- Decision-executor Python and Godot smokes pass, including allowlist rejection,
  replay idempotency, stale-snapshot rejection, and enforced
  preview/confirm/commit handoff. Its scoped MAF receipt validates and does not
  claim self-acceptance.
- Edition-selector Godot smoke: PASS; both editions share contract semantics
  and the settings layer rejects client secrets.

All out-of-directive source files are preserved. Acceptance state was reset;
no gameplay code was rolled back.

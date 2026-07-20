# Codex Acceptance — AGM Partial Wave

Date: 2026-07-20  
Final acceptor: Codex  
Accepted: `G1-003`, `G2-003`, `G2-004`, `G2-007`

## Evidence

- Project validator: `AIDLE_VALIDATION=PASS`, including AGM and asset grammar.
- AGM fixtures: 7 valid accepted and 14 adversarial invalid rejected.
- Worker receipts validate against the MAF step-contract schema.
- Companion Python smoke: PASS.
- Companion Godot smoke: PASS after fixing initialization ordering and
  headless-safe service/visual access; no parse or runtime error remains.
- Asset grammar is now exercised by the project validator.
- Edition-selector Godot smoke: PASS; both editions share contract semantics
  and the settings layer rejects client secrets.

## Not accepted

- `G2-001`: integrated headless run still emits dummy-renderer mesh errors.
- `G2-002`: functional smoke passes but emits mesh/fallback log noise.
- `G2-005`: Python smoke passes after correcting a false-positive test, but the
  Godot bridge smoke exposes unresolved class loading and UI type errors.
- `G2-006`: Python and Godot smokes pass, but no scoped MAF worker receipt exists.

All out-of-directive source files are preserved. Acceptance state was reset;
no gameplay code was rolled back.

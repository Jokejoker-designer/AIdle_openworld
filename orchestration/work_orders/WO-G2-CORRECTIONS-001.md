# Work Order — G2 Corrections 001

Authority: `PATCH_DRAFT`  
Final acceptor: Codex  
Permitted tasks: G2-001, G2-002, G2-005, G2-006

## Corrections

### G2-001 / G2-002

- Preserve fixed-angle 2.5D movement and manifestation behavior.
- Eliminate headless dummy-renderer mesh errors by skipping presentation-only
  mesh creation in headless mode; do not hide or filter real errors.
- Integrated and manifestation smoke logs must contain no `SCRIPT ERROR`,
  `Parse Error`, `Compile Error`, or `ERROR:` lines.

### G2-005

- Fix Bridge class loading under standalone Godot `--script` execution.
- Fix dialog/window type errors and inferred-null variables.
- Smoke must fail if any required script fails to load; a printed PASS alongside
  parse errors is forbidden.
- Retain manual visible consent, no networking, stale/replay rejection and
  explicit secret deny-lists.

### G2-006

- Preserve the currently passing Python and Godot executor behavior.
- Produce `orchestration/receipts/G2-006.json` as a valid MAF step contract.
- Do not implement durable commit; retain preview/confirm/commit handoff only.

## File ownership

Workers may edit only their existing module paths and their own receipt. They
must not edit `orchestration/tasks.json`, `codex_directive.json`, architecture
files, other modules, or create `*-ACCEPT.json`.

Return `REVIEW_REQUESTED` to `grok_status.json`. Codex will rerun every test.

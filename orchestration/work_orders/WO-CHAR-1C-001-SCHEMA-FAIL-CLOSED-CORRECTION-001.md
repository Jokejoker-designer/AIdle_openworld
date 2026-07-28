# WO-CHAR-1C-001 — Fail-closed schema intake correction 001

Status: `AUTHORIZED_BY_DIRECTIVE_65`  
Task: `CHAR-1C-001`  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852`  
Review: `orchestration/reviews/CODEX_CHAR-1C-001_SCHEMA_INTAKE_REVIEW_001.json`

## Purpose

Close only the five independently reproduced CharacterSpec/batch bypasses and
the verification bytecode-write defect. Preserve the 28/7 source intake,
Foundry source files, prior receipts/logs and all unrelated product code.

## Required corrections

1. Reject any normalized `behavior_allowlist` token that intersects
   `UNIVERSAL_DENYLIST` or otherwise names direct commit, ownership, inventory,
   economy, arbitrary-code, TrustLayer-tool, AIda replacement or credential authority.
2. Reject any normalized token present in both allowlist and denylist.
3. Normalize case, punctuation, dots, spaces, hyphens and underscores for AIda
   identity checks. Apply the guard to `display_name`, `character_id`,
   `species_form` and other identity-bearing fields selected explicitly by the
   contract without banning legitimate relationship prose.
4. Validate the intake batch envelope strictly: required fields, types, exact
   counts/hash, records and `additionalProperties:false`. Root fields such as
   `extra_backdoor` or `tool_authority` must fail closed.
5. Bind `cozy_cast` exactly to `CCP-RH-001`, `CCP-NS-002`, `CCP-NW-003` and
   `CCP-CT-004`; all other IDs must be false.
6. Add deterministic adversarial fixtures and explicit rejection tags for all
   five cases. Preserve the original 14 invalid and 3 valid fixtures.
7. Run Python only with `-B` and `PYTHONDONTWRITEBYTECODE=1`. Preserve the
   existing `__pycache__` as rejected evidence; do not delete, rewrite or use it.

## Sequential child dispatch

Parent remains coordinator-only. Exactly three fresh real installed children,
sequentially. No support profiles or grandchildren.

### C0 — `schema` / `aidle-schema` — `PATCH_DRAFT`

Binding: `devil-advocate` + `ui-brief-writer`. Load all five mandatory skills
plus `architecture-lock` and `securing-agentic-ai-tool-invocation` fully.

Sole allowed product writes:

- `orchestration/contracts/character_foundry_1c/character_spec.schema.json`
- `orchestration/contracts/character_foundry_1c/validate_character_foundry_1c.py`
- new or amended fixtures under `orchestration/contracts/character_foundry_1c/fixtures/**`
- `orchestration/contracts/character_foundry_1c/intake_report.json` only if the
  corrected deterministic normalizer changes its exact generated record form
- `orchestration/contracts/character_foundry_1c/source_manifest.lock.json` only
  if the corrected deterministic rule description changes; source hashes/counts must not

Exclusive evidence writes:

- `orchestration/logs/char-1c-001-c0-schema-correction-002.log`
- `orchestration/receipts/character_1c/CHAR_1C_001_c0_schema_correction_002.json`

Run the full existing harness plus five direct adversarial probes. Keep
`accepted=false`, `self_accept=false`.

### C1 — `aidle-character-red-originality` — `READ_ONLY_AUDIT`

Binding: `red-team-source-auditor` + `ui-visual-critic`. Load all five mandatory
skills plus `adversarial-review`. Reproduce each Codex probe independently,
check for bypass variants and verify source/hash/28/7 fidelity. Findings only.

Exclusive writes:

- `orchestration/logs/char-1c-001-c1-red-correction-002.log`
- `orchestration/receipts/character_1c/CHAR_1C_001_c1_red_correction_002.json`

### C2 — `aidle-character-purple-acceptance` — `VERIFY_ONLY`

Binding: `purple-team-release-gate` + `ui-visual-critic`. Load all five mandatory
skills plus `evidence-memory-ledger` and `adversarial-review`. Run the full
harness, all five direct probes, MAF receipt validation, source hashes, writer
lease and durable lineage checks. Purple never patches or accepts.

Exclusive writes:

- `orchestration/logs/char-1c-001-c2-purple-correction-002.log`
- `orchestration/receipts/character_1c/CHAR_1C_001_c2_purple_correction_002.json`

## Required evidence discipline

- Use real child refs and exact parent binding.
- Every child fully reads its profile, TrustLayer/UI cards, five mandatory and routed skills with transcript-backed EOF ranges.
- Every receipt validates against `E:/standards/maf/schemas/agent_step_contract.schema.json`.
- Literal commands, exit codes, read/write sets, product writes, context hash,
  trace/handoff, `accepted=false`, `self_accept=false`.
- No parent product/evidence patch and no extra helper, temp, cache, redirect,
  delete, move or rename.

## Forbidden

Foundry Markdown edits; Godot/Blender/Scene/visual/rig/animation/behavior
implementation; Block-DNA/P2E/v1.2/Tier3; AIda replacement; network/shipping;
dependency install; Godot version change; credential; public network; push,
deploy or publish.

## Completion

Return `REVIEW_REQUESTED` / `WAITING_CODEX`, all three child refs, before/after
source hashes, full harness counts, five probe results, receipt schema results,
exact writer leases, `parent_product_patch=false`, `accepted=false` and
`self_accept=false`.


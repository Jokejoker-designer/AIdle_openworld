# WO-CHAR-1C-001-UNICODE-IDENTITY-CORRECTION-002

Status: APPROVED FOR DIRECTIVE 66 ONLY  
Task: `CHAR-1C-001`  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852`  
Machine verdict remains: `CHANGES_REQUESTED`, `accepted=false`

## Objective

Close only the Unicode compatibility and mixed-script confusable bypasses on
the protected AIda identity surface. Preserve the passing Directive-65 contract,
all 28 Foundry records, all prior fixtures/evidence, and the locked manifest hash.

## Sequential real-child dispatch

1. `U0` — installed profile `schema`, `PATCH_DRAFT`, sole contract writer.
   Bind the profile's registered TrustLayer and UI characters, load the five
   mandatory skills plus routed `architecture-lock` and
   `securing-agentic-ai-tool-invocation` fully through EOF, and record exact
   transcript ranges.
2. `U1` — installed profile `aidle-character-red-originality`,
   `READ_ONLY_AUDIT`, findings only after U0. Bind its registered TrustLayer/UI
   characters and load the five mandatory skills plus `adversarial-review`.
3. `U2` — installed profile `aidle-character-purple-acceptance`, `VERIFY_ONLY`,
   only after U1. Bind its registered TrustLayer/UI characters and load the five
   mandatory skills plus `evidence-memory-ledger` and `adversarial-review`.

No grandchildren, support profiles, parent product patch, or parallel writers.

## U0 implementation lease

Allowed product writes only:

- `orchestration/contracts/character_foundry_1c/validate_character_foundry_1c.py`
- new invalid fixtures `INV-20-*` and `INV-21-*` under
  `orchestration/contracts/character_foundry_1c/fixtures/invalid/`
- `source_manifest.lock.json` only if a truthful normalization-rule annotation
  must change; character/source hashes and counts may not change

Exclusive evidence:

- `orchestration/logs/char-1c-001-u0-unicode-correction-003.log`
- `orchestration/receipts/character_1c/CHAR_1C_001_u0_unicode_correction_003.json`

Required behavior:

- apply `unicodedata.normalize("NFKC", value)` before `casefold`
- apply a documented, deliberately small confusable fold only for the AIda
  identity comparison, covering at minimum Cyrillic A/a and I/i, Greek
  Alpha/alpha and Iota/iota; do not rewrite stored source strings
- retain separator, punctuation and zero-width handling
- run the gate only on documented identity-bearing fields; relationship prose
  remains outside the identity claim gate
- add deterministic invalid fixtures for fullwidth AIda and mixed-script AIda
- preserve every original valid/invalid fixture and all five Directive-65 gates

## U1/U2 verification

Both reviewers rerun the full harness and direct probes for:

- fullwidth `ＡＩｄａ`
- Cyrillic `Aіda` and `Аida`
- Greek-iota `Aιda`
- existing `AI-da` and zero-width variants
- all Directive-65 F01/F03/F04/F05/F06 probes

All must reject while the clean source remains `28/28`, valid fixtures remain
`3/3`, manifest hash identity remains exact, and every invalid fixture rejects.
Purple never accepts the task; it returns `WAITING_CODEX` with
`accepted=false`, `self_accept=false`.

## Evidence and execution rules

- Every Python command uses `PYTHONDONTWRITEBYTECODE=1` and `python -B`.
- Preserve the existing 09:16:57 pycache artifact unchanged as rejected
  evidence; never delete, import, overwrite, or cite it as passing evidence.
- Each child writes only its exclusive new `003` receipt and log plus U0's
  product lease. Receipts must validate against
  `E:/standards/maf/schemas/agent_step_contract.schema.json` and include real
  durable child refs, exact commands/exits, timestamps, hashes, skills,
  character bindings, `product_writes`, `accepted=false`, `self_accept=false`.
- Foundry MD, manifest, Godot, Blender, Scene, Block-DNA, P2E, network, World
  Commit, prior evidence, task and directive files are immutable to children.

## Completion

Parent returns `REVIEW_REQUESTED / WAITING_CODEX`, lists all three real child
refs, declares `parent_product_patch=false`, and does not start any later wave.

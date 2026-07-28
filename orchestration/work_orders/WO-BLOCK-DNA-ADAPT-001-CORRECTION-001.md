# WO-BLOCK-DNA-ADAPT-001-CORRECTION-001

Status: APPROVED CORRECTION ONLY  
Owner: Codex  
Task: `BLOCK-DNA-ADAPT-001`  
Supersedes execution posture of Directive 68; preserves all Directive-68 artifacts and evidence  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852` coordinator-only

## Objective

Close the three independently reproduced fail-open contract defects from
`CODEX_BLOCK-DNA-ADAPT-001_MACHINE_REVIEW_001.json`. This remains a project-local,
offline contract gate. It does not authorize P2E Block Assembly runtime, Godot,
Scene, Character runtime, PersistModule, World Commit, network or shipping work.

## Sequential dispatch

1. **C0 Schema** — resume real B1 lineage
   `019f8804-7915-71d2-b3b1-573b701a202e`, authority `PATCH_DRAFT`.
   Sole product writer for `orchestration/contracts/block_dna_adapt_001/**`.
2. **C1 Red** — fresh installed `aidle-worldgen-red-scope`,
   authority `READ_ONLY_AUDIT`.
3. **C2 QA** — fresh installed `aidle-worldgen-qa-evidence`,
   authority `VERIFY_ONLY`.
4. **C3 Purple** — fresh installed `aidle-worldgen-purple-acceptance`,
   authority `VERIFY_ONLY`.

Run strictly sequentially. Maximum four children. No grandchildren or support
profiles. Parent must not patch product, contracts, tests or evidence.

## C0 mandatory fixes

### F-B2-01 — canonical idempotency binding

- Make `payload_fingerprint` schema-legal and required in both Build Graph and
  Build Recipe. Format is lowercase SHA-256 hex.
- Define one canonical JSON payload projection and hash it deterministically.
  Exclude only the fingerprint field itself; do not mutate the input document
  with an internal helper property.
- Add a bounded in-memory replay ledger in the contract harness:
  - identical key + identical canonical payload = stable replay, no duplicate;
  - same key + changed canonical payload = conflict and fail closed;
  - missing, malformed or incorrect fingerprint = reject.
- Add explicit valid replay and invalid changed-payload fixtures/tests. A test
  that greens only because the fingerprint field is illegal is forbidden.

### F-B2-02 — catalog-bound polarity

- A non-normalized edge must declare polarities matching the socket catalog
  defaults and must satisfy the directed/peer policy.
- An adapter normalization may override an asymmetric source pair only when its
  record declares explicit effective polarities for that exact pair. The edge
  must match those effective polarities.
- Directed sockets cannot be laundered to `peer/peer`; peer sockets cannot be
  relabeled as directed unless the exact pair-bound normalization says so.
- Add adversarial fixtures for peer laundering and catalog polarity mismatch.

### F-B2-03 — pair-bound normalization

- When `adapter_normalization_id` is present, require its catalog pair to match
  the edge socket pair exactly under the documented orientation policy.
- Reject a known normalization ID used for any other pair.
- Cover all four source-asymmetric relations and add a wrong-known-ID fixture.

### Same-file hardening required in this correction

- Co-require `material_slot` and `p1e_material_id`; require the live P1E-006
  mapping in both directions.
- Constrain recipe parameters to an allowlisted key/type contract and reject
  code-shaped keys such as script, command, execute, eval, path-to-executable or
  tool-authority forms.
- Make validation policy switches `const: true` or remove them; input cannot
  disable collision, occupancy, socket, cycle or snap enforcement.
- Recompute and verify both recorded immutable DNA tree aggregate hashes in the
  validator. Do not edit either DNA package.

## Required matrix

- Preserve every currently valid behavior, updating fingerprints and explicit
  normalization polarity data where required.
- Preserve all 30 current invalid cases and add dedicated cases for every fix.
- Minimum after correction: 12 valid plus at least 37 invalid/adversarial cases.
- Codex will independently replay F-B2-01 through F-B2-03, material pairing,
  code-shaped parameters, false validation flags and full tree baselines.

## Evidence leases

- C0:
  - `orchestration/logs/block-dna-adapt-001-c0-schema-correction-002.log`
  - `orchestration/receipts/block_dna_adapt_001/C0_schema_correction_002.json`
- C1:
  - `orchestration/logs/block-dna-adapt-001-c1-red-correction-002.log`
  - `orchestration/receipts/block_dna_adapt_001/C1_red_correction_002.json`
- C2:
  - `orchestration/logs/block-dna-adapt-001-c2-qa-correction-002.log`
  - `orchestration/receipts/block_dna_adapt_001/C2_qa_correction_002.json`
- C3:
  - `orchestration/logs/block-dna-adapt-001-c3-purple-correction-002.log`
  - `orchestration/receipts/block_dna_adapt_001/C3_purple_correction_002.json`

Prior B0–B4 receipts and logs are immutable and must not be rewritten.

## MAF, characters and skills

Each child must use the exact installed profile binding, authority token,
TrustLayer character and UI character. Each child reads all five mandatory
`skills_manifest.yaml` skills through EOF and its routed skills through EOF via
durable semantic `read_file` calls. Receipts validate against
`E:/standards/maf/schemas/agent_step_contract.schema.json` and include exact
child/parent lineage, timestamps, commands and exits, files read/written,
product writes, hashes, trace/handoff, `accepted=false` and `self_accept=false`.

## Hard stops

- No `world_DNA/**`, `game/**`, Scene, Control, Character, PersistModule or
  existing World Prompt contract edit.
- No P2E runtime, World Commit expansion, network or shipping.
- No helper/temp/cache/scratch/out-of-lease write.
- Red and Purple never patch. Parent never self-accepts.

## Completion

Parent returns `REVIEW_REQUESTED / WAITING_CODEX`, `accepted=false`, all four
real child refs, `parent_product_patch=false`, `p2e_spawn_allowed=false`, and no
later wave started. Codex independently decides acceptance or another correction.

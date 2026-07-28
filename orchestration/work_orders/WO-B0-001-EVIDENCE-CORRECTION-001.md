# WO-B0-001 Evidence Correction 001

Directive: 47  
Task: B0-001  
State: CHANGES_REQUESTED  
Parent: existing Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852` only  
Authority: VERIFY_ONLY

## Objective

Correct the evidence semantics and writer-lease defects identified by
`orchestration/reviews/CODEX_B0-001_MACHINE_REVIEW_001.json`. This is an
evidence-only correction. Do not patch Blender Bridge, Godot, Scene, Character,
Control, tests or prior evidence.

## Preserved evidence

- Preserve `blender-p0-schema-001-hash.txt` unchanged as rejected evidence. It
  is outside the original lease and must not count toward acceptance.
- Preserve all Directive 46 receipts, logs, jobs and failed probe evidence.
- Codex independently created server-mediated real job `BLD-8A8D63935D6B` via
  FastAPI `TestClient` and `CharacterJobService`; its canonical
  `job_receipt.json` reports `QUARANTINED_COMPLETE`, real mode and exit 0.

## Dispatch

The parent remains coordinator-only. Run exactly three real installed children
sequentially; no support profiles and no grandchildren:

1. Resume the `schema` lineage `019f8373-dc17-7b02-914f-073b4ae5c03a` as
   `VERIFY_ONLY`. Write only:
   - `orchestration/receipts/blender_p0/B0_schema_correction_002.json`
   - `orchestration/logs/blender-p0-schema-correction-002.log`
   The receipt must mark the original schema receipt rejected for exact-lease
   acceptance, list the unauthorized file and its SHA-256, and prove no new
   out-of-lease write.
2. Resume the `aidle-character-rig-animation` lineage
   `019f8373-dc18-7010-bc49-97f61e6402b5` with authority reduced to
   `VERIFY_ONLY`. Write only:
   - `orchestration/receipts/blender_p0/B0_rig_correction_002.json`
   - `orchestration/logs/blender-p0-rig-correction-002.log`
   The receipt must state that `BLD-D2C21066E6F2` is a direct command-contract
   probe without a service job receipt. Independently rehash and bind Codex job
   `BLD-8A8D63935D6B`, including its receipt, validation, artifacts, stderr and
   preview, without claiming the rig child created it.
3. Spawn one fresh `aidle-worldgen-purple-acceptance` child as
   `VERIFY_ONLY` after steps 1 and 2. Write only:
   - `orchestration/receipts/blender_p0/B0_purple_correction_002.json`
   - `orchestration/logs/blender-p0-purple-correction-002.log`
   Purple must verify exact write leases, distinguish direct from
   server-mediated probes, review all blockers in the Codex review, and return
   `PASS_FOR_CODEX_REVIEW` or `CHANGES_REQUESTED`; never ACCEPT B0.

Each child must retain its registered TrustLayer/UI binding, fully load all five
mandatory skills plus routed skills, emit a MAF-valid receipt with real
transcript refs, literal commands/exits, hashes, `product_writes=[]`,
`accepted=false` and `self_accept=false`.

## Stop conditions

Stop on any new out-of-lease write, product patch, missing real transcript,
writer conflict, authority drift or repeated identical failure. Parent returns
`REVIEW_REQUESTED / WAITING_CODEX` with `accepted=false`. No install,
credentials, public network, push, deploy or publish.

# WO-B0-001 — Blender Bridge P0 independent machine gate

Directive: 46  
Task: B0-001  
State: IN_PROGRESS  
Parent: existing Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852`
only  
Authority: VERIFY_ONLY

## Objective

Independently verify the hardened bridge at `E:/AIdle_Blender_Bridge_P0`
against the AIdle Blender–Grok Blueprint. This wave is evidence-only. It does
not patch Bridge product code, build Nori-7, start Character Foundry/Scene 1C,
publish to Godot or approve G8.

## Dispatch

Parent is coordinator-only. Use exactly four real installed child profiles,
sequential where dependencies require it, maximum four active, no support
profiles and no grandchildren:

1. `schema` as `VERIFY_ONLY`: request/tool schema, template/profile policy,
   path boundary, operation allowlist and fail-closed negative cases.
2. `aidle-character-rig-animation` with authority reduced to `VERIFY_ONLY`:
   Blender 5.2 compatibility, real GLB/Blend/preview/validation technical
   evidence, triangle/object limits and future Godot intake boundary.
3. `aidle-worldgen-qa-evidence` as `VERIFY_ONLY`: run the executable matrix and
   inspect real preview evidence.
4. `aidle-worldgen-purple-acceptance` as final independent `VERIFY_ONLY`
   reviewer after children 1–3 finish; Purple never patches.

Each child binds its registered TrustLayer/UI character and fully loads the
five mandatory skills from `orchestration/skills_manifest.yaml`; load routed
skills from its profile/work order only. Every child writes one exclusive
MAF-valid receipt and one trace under:

- `orchestration/receipts/blender_p0/B0_schema_001.json`
- `orchestration/logs/blender-p0-schema-001.log`
- `orchestration/receipts/blender_p0/B0_rig_001.json`
- `orchestration/logs/blender-p0-rig-001.log`
- `orchestration/receipts/blender_p0/B0_qa_001.json`
- `orchestration/logs/blender-p0-qa-001.log`
- `orchestration/receipts/blender_p0/B0_purple_001.json`
- `orchestration/logs/blender-p0-purple-001.log`

One writer per file. Receipts include real child/transcript refs, exact skill
sources/modes/full-read evidence, commands and exit codes, files read/written,
hashes, findings, trace/handoff, `product_writes=[]`, `accepted=false` and
`self_accept=false`.

## Required evidence

- `E:/blender.exe --version` reports Blender 5.2.0 LTS.
- `python -m pytest -q` reports 11 passed without installing anything.
- `python -m compileall -q app tests blender_scripts` exits 0.
- A fresh real-mode probe using only `E:/blender.exe`, the approved worker and
  server-generated paths ends `QUARANTINED_COMPLETE` with exit 0.
- The fresh quarantine contains non-empty `.blend`, `.glb`, PNG,
  `validation.json` and `artifact_hashes.json` with matching job/character IDs.
- Preview is visually inspected and is not a flat/blank frame; validation
  visual signal is at least 0.15.
- Worker stderr has no error or traceback. Warnings are reported honestly.
- Negative cases remain fail-closed: extra fields, disabled validation,
  unknown template, path escape, duplicate request and exit-zero/missing
  artifacts.
- No shell/Python/download/add-on/output-path tool is exposed to Grok.
- Output remains quarantine-only; no Godot copy, catalog approval or direct
  state mutation.
- The failed compatibility probe `BLD-0B63ED79CCFD` remains preserved as
  evidence; no cleanup or rewrite.

## Stop conditions

On a blocker, preserve evidence and return `CHANGES_REQUESTED`. After the four
receipts, parent returns `REVIEW_REQUESTED / WAITING_CODEX`; Grok does not
accept B0-001. No install, credentials, outbound provider/network, push,
deploy or publish.

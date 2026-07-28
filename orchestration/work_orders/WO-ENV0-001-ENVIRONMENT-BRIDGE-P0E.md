# WO-ENV0-001 — Environment Bridge P0E

Authority: `PATCH_DRAFT` (Blue only) · State: `READY`

## Objective

Extend `E:/AIdle_Blender_Bridge_P0` with a fail-closed, server-mediated
environment scene job skeleton and one real Blender Starter Realm probe, using
the aligned Blueprint at
`Scene/AIdle_Blender_Environment_Scene_Blueprint_v1.0` as design/contract input.

## Dependencies and locks

- B0-001 is ACCEPTED.
- Blender is pinned to `E:/blender.exe` 5.2.0 LTS.
- Godot is pinned to 4.3-stable; no Godot changes are permitted.
- Character and environment jobs share the global `max_active_jobs = 1` lease.
- G8 remains HITL_REQUIRED; P1E is blocked.

## Dispatch graph (same parent, max five children)

### E0 — `schema`, VERIFY_ONLY

Validate the v1.1 Blueprint contracts/example/tool reference, enumerate at
least 10 valid and 10 adversarial cases, and write only:

- `orchestration/receipts/environment_p0/ENV0_schema_001.json`
- `orchestration/logs/environment-p0-schema-001.log`

### E1 — `aidle-worldgen-asset-art`, PATCH_DRAFT

Sole product writer. It may write only:

- `E:/AIdle_Blender_Bridge_P0/app/api/environment_jobs.py`
- `E:/AIdle_Blender_Bridge_P0/app/environment_models.py`
- `E:/AIdle_Blender_Bridge_P0/app/services/environment_job_service.py`
- environment-only additions in `app/dependencies.py` and `app/main.py`
- `E:/AIdle_Blender_Bridge_P0/blender_scripts/environment_worker_entry.py`
- `E:/AIdle_Blender_Bridge_P0/config/environment_*.yaml`
- `E:/AIdle_Blender_Bridge_P0/templates/environments/**`
- `E:/AIdle_Blender_Bridge_P0/libraries/environments/**`
- `E:/AIdle_Blender_Bridge_P0/tests/test_environment_*.py`
- its exclusive ENV0 receipt/log/trace

It must not edit character models/service/worker/tests except the minimal
router/dependency wiring explicitly listed above.

### E2 — `aidle-worldgen-red-scope`, READ_ONLY_AUDIT

Findings only: authority bypass, path traversal, client budget/concurrency
control, idempotency collision, arbitrary Blender operation, output promotion,
runtime boundary and evidence gaps.

### E3 — `aidle-worldgen-qa-evidence`, VERIFY_ONLY

Run full character regression plus ENV0 tests, compileall and server-mediated
real Blender probe. Preserve stdout/stderr, job receipt, validation, manifest,
artifact hashes and nonblank preview evidence. Direct CLI output is diagnostic
only and cannot replace service lifecycle proof.

### E4 — `aidle-worldgen-purple-acceptance`, VERIFY_ONLY

Independently verify work-order scope, contracts, one-writer leases, negative
cases, test evidence, probe identity and runtime/HITL boundaries. Purple never
patches and returns only VERIFIED, CHANGES_REQUESTED or NEED_HUMAN.

## Acceptance criteria

1. Existing 11 Character Bridge tests remain green.
2. Strict environment request rejects unknown fields, paths, URLs, code and
   arbitrary operations.
3. Unknown template/module/profile is rejected before Blender execution.
4. Identical idempotency replay is stable; same key + changed canonical payload
   conflicts without mutation.
5. Server hard caps cannot be raised/reset by a client; all jobs share one
   Bridge-wide active lease.
6. Artifact references are quarantine-relative and traversal-safe.
7. Validation report and scene manifest cannot be disabled.
8. Mock manifest is deterministic.
9. Server-mediated real job reaches `QUARANTINED_COMPLETE`, exits 0 and emits
   `.blend`, GLB, preview, manifest, validation, hashes and logs.
10. No Godot, Scene runtime, approved catalog or World Commit mutation occurs.

## Receipt requirements

Each significant child writes a schema-valid `agent_step_contract` with real
child/transcript ref, TrustLayer/UI character binding, authority, all five
mandatory skills plus routed skills loaded to EOF, input context hash, exact
read/write set, literal commands and exit codes, trace/handoff,
`product_writes`, `accepted=false` and `self_accept=false`.

No install, credential, live provider/public network, push, deploy or publish.

# WO-ENV0-001-CORRECTION-001 - Environment Bridge P0E remediation

Authority: `PATCH_DRAFT` for Blue only. State: `READY`.

## Objective

Remediate the blocking ENV0 Purple findings from
`orchestration/receipts/environment_p0/ENV0_purple_001.json` without expanding
scope beyond the Environment Bridge P0E.

This work order supersedes no accepted work. It is a correction pass for
`ENV0-001`, which remains `CHANGES_REQUESTED` and `accepted=false`.

## Required context

Read before action:

- `AGENTS.md`
- `E:/standards/maf/COMPLIANCE.md`
- `E:/agents/characters/registry.yaml`
- `E:/agents/ui-design/registry.yaml`
- `orchestration/ARCHITECTURE_LOCK.md`
- `orchestration/workflow.json`
- `orchestration/tasks.json`
- `orchestration/control/codex_directive.json`
- `orchestration/control/grok_status.json`
- `orchestration/control/GROK_CONTINUITY_CAPSULE.md`
- `orchestration/control/GROK_AUTONOMOUS_OPERATING_ENVELOPE_ENV0.md`
- `orchestration/skills_manifest.yaml`
- `orchestration/receipts/environment_p0/ENV0_red_001.json`
- `orchestration/receipts/environment_p0/ENV0_purple_001.json`
- `E:/AIdle_Blender_Bridge_P0/app/services/job_service.py`
- `E:/AIdle_Blender_Bridge_P0/app/services/environment_job_service.py`
- `E:/AIdle_Blender_Bridge_P0/tests/test_api.py`
- `E:/AIdle_Blender_Bridge_P0/tests/test_environment_api.py`
- `E:/AIdle_Blender_Bridge_P0/tests/test_environment_runner.py`

## Blocking fixes

### BLK-ENV0-01 / ENV0-RED-F02 / WO AC5

Implement a mutual Bridge-wide active lease:

- character job create must reject while an environment job is `QUEUED` or
  `RUNNING`;
- environment job create must continue rejecting while a character job is
  `QUEUED` or `RUNNING`;
- both paths must use one shared create-lock or equivalent atomic guard;
- the shared `BlenderRunner` execution semaphore remains a second line of
  defense, not the only lease proof.

### BLK-ENV0-02 / ENV0-RED-F09 / WO AC5

Add automated evidence proving mutual exclusion:

- active environment blocks character create;
- active character blocks environment create;
- no dual queued character+environment pair is produced by valid API paths;
- rejection leaves existing receipts and generated quarantine artifacts
  unchanged.

### BLK-ENV0-03 / ENV0-RED-F03 / WO AC4

Fix idempotency semantics:

- canonical idempotency fingerprint must exclude `request_id` and
  `idempotency_key`;
- same idempotency key plus same semantic request but rotated `request_id`
  must replay the original job;
- same idempotency key plus changed semantic payload must fail closed with
  conflict and no mutation.

## Recommended hardening included in this correction

Include these if they fit the same files and do not require dependency install:

- enforce `expected_bridge_revision` against a server-owned revision constant;
- re-hash `build_spec.internal.json` against `build_spec.sha256` immediately
  before Blender execution and fail closed on mismatch;
- add a bounded stale-active receipt recovery path or explicit operator
  recovery test for stale `QUEUED` / `RUNNING` receipts.

## Dispatch graph

Use the same Grok Desktop parent
`019f7ffd-3995-71c0-aca1-51078e24a852`.

No Grok CLI. No new top-level session. No grandchildren. No support profiles.

Run sequentially:

1. `aidle-worldgen-asset-art`, `PATCH_DRAFT`, sole product writer.
2. `aidle-worldgen-red-scope`, `READ_ONLY_AUDIT`, findings only.
3. `aidle-worldgen-qa-evidence`, `VERIFY_ONLY`, tests and evidence only.
4. `aidle-worldgen-purple-acceptance`, `VERIFY_ONLY`, final gate only.

## Product write lease for Blue

Blue may write only:

- `E:/AIdle_Blender_Bridge_P0/app/services/job_service.py`
- `E:/AIdle_Blender_Bridge_P0/app/services/environment_job_service.py`
- `E:/AIdle_Blender_Bridge_P0/app/dependencies.py` only if needed for shared
  lease wiring
- `E:/AIdle_Blender_Bridge_P0/app/config.py` only if needed for
  `bridge_revision`
- `E:/AIdle_Blender_Bridge_P0/tests/test_api.py`
- `E:/AIdle_Blender_Bridge_P0/tests/test_environment_api.py`
- `E:/AIdle_Blender_Bridge_P0/tests/test_environment_runner.py`
- its exclusive correction receipt/log/trace

No Godot, Scene runtime, Control, Character Foundry, approved catalog,
World Commit, G8 acceptance, P1E, credentials, public network, install, push,
deploy or publish.

## Required verification

QA and Purple must run and record:

- `python -m compileall -q app tests blender_scripts`
- `python -m pytest tests/test_api.py tests/test_runner.py tests/test_security.py -q --tb=short`
- `python -m pytest tests/test_environment_api.py tests/test_environment_runner.py -q --tb=short`
- `python -m pytest tests/ -q --tb=line`
- at least one server-mediated real environment Blender probe reaching
  `QUARANTINED_COMPLETE`, exit code 0, with hash re-verification and nonblank
  preview;
- adversarial tests for request-id rotation replay, same-key changed-payload
  conflict, mutual character/environment lease, stale revision, and tampered
  build spec.

## Receipt requirements

Each child must write a schema-valid `agent_step_contract` with:

- real Grok child task ref and transcript ref;
- parent session ref;
- TrustLayer character and UI character binding;
- all five mandatory skills plus routed skills loaded fully through EOF;
- exact files read/written and `product_writes`;
- literal commands and exit codes;
- input context hash;
- `accepted=false`;
- `self_accept=false`.

Purple may return only `VERIFIED`, `CHANGES_REQUESTED`, or `NEED_HUMAN`.
ENV0 cannot be accepted by Grok.

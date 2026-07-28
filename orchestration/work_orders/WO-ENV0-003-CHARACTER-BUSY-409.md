# WO-ENV0-003 — Character API busy status code

Authority: `PATCH_DRAFT` (Blue only) · State: `READY`
Issued by: `aidle-continuity-conductor` — **NOT Codex**
Scope: `E:/AIdle_Blender_Bridge_P0` only. No Godot involved, no override needed —
this is ordinary Bridge patch work already permitted under Directive 50.

## Source of the finding

`ENV0-RED-F02`-adjacent residual, first surfaced as `ENV0-C2-R01` during
WO-ENV0-002 wave C2 (`ENV0_c2_red_002.json`): *"Character jobs.py returns 500
instead of 409 on BridgeBusyError, asymmetric with the environment API."*
Marked non-blocking at the time, carried forward in
`CONDUCTOR_JOURNAL.md` open items.

## Confirmed by reading current source, not assumed

`E:/AIdle_Blender_Bridge_P0/app/api/jobs.py` `create_job()` has `except`
clauses for `DuplicateRequestError`, `KeyError`, and
`IncompatibleTemplateProfileError`, but **no clause for `BridgeBusyError`** (the
base class `EnvironmentBusyError` extends, defined in
`app/services/blender_runner.py`). When the shared Bridge-wide lease is held
and `CharacterJobService.create()` raises `BridgeBusyError`, it is unhandled and
falls through to FastAPI's default 500 response.

Contrast with `app/api/environment_jobs.py`, which explicitly catches
`EnvironmentBusyError` and returns 409 with a structured detail body
(`reason: "worker_lease_busy"`).

## Fix

Add an `except BridgeBusyError` clause to `create_job()` in
`app/api/jobs.py`, returning `status_code=409` with a detail body matching the
shape already used on the environment side (`message`, `reason`). Import
`BridgeBusyError` from `app.services.blender_runner`.

Do not change `EnvironmentBusyError` handling — it is already correct. Do not
change lease/busy logic itself — `WO-ENV0-002` already verified that logic.
This is purely an HTTP status-code mapping fix.

## Writer allowlist

- `E:/AIdle_Blender_Bridge_P0/app/api/jobs.py`
- `E:/AIdle_Blender_Bridge_P0/tests/test_api.py` (add one test: character
  create returns 409, not 500, while a lease is held)
- its exclusive receipt, log and trace

If anything outside this list is needed, stop and report rather than writing it.

## Out of scope

Everything already out of scope for prior ENV0 work orders. In particular: no
Godot, Scene runtime, Control, Character Foundry, approved catalog, World
Commit; no other Red findings (F01, F04–F10 already deferred and not
authorized here); no change to `codex_directive.json`.

## Dispatch graph

Same parent `019f7ffd-3995-71c0-aca1-51078e24a852`. Sequential, one child at a
time, no grandchildren: `aidle-worldgen-asset-art` PATCH_DRAFT sole writer,
then `red` READ_ONLY_AUDIT, then `qa` VERIFY_ONLY, then `purple` VERIFY_ONLY.

## Acceptance criteria

1. Character job create returns 409 (not 500) when the Bridge-wide lease is
   held, with a detail body shaped like the environment API's.
2. Environment API busy handling unchanged.
3. All pre-existing tests remain green (11 character + 17 environment + 10
   lease + fence regression = current full suite).
4. New regression test proves the fix.
5. No file outside the writer allowlist is touched.

## Receipt requirements

Same standard as all prior ENV0 work orders this session: real durable Grok
child/transcript ref cross-checked against `grok_status.json`, `accepted=false`,
`self_accept=false`. Return `REVIEW_REQUESTED`, `CHANGES_REQUESTED` or
`WAITING_HUMAN`.

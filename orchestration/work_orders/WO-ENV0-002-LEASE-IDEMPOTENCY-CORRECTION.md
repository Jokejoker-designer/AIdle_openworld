# WO-ENV0-002 — ENV0 lease and idempotency correction

Authority: `PATCH_DRAFT` (Blue only) · State: `READY`
Issued by: `aidle-continuity-conductor` — **NOT Codex**
Authorized by: Human Product Lead, 2026-07-21
Scope: correction pass inside ENV0-001. This work order does **not** create new
scope, does not supersede Directive 49, and does not modify
`codex_directive.json`.

## Why this exists

E4 Purple returned `CHANGES_REQUESTED` on ENV0-001 with three blocking defects.
ENV0-001 is not accepted. This work order closes exactly those three defects and
nothing else.

Precedent evidence: `orchestration/receipts/environment_p0/ENV0_purple_001.json`,
`orchestration/receipts/environment_p0/ENV0_red_001.json`.

## Dependencies and locks

- WO-ENV0-001 waves E0–E4 are complete; receipts corrected and ref-consistent.
- Blender pinned `E:/blender.exe` 5.2.0 LTS. Godot pinned 4.3-stable, no Godot changes.
- Global `max_active_jobs = 1` remains the single Bridge-wide lease.
- G8-001 stays `HITL_REQUIRED`. P1E, Scene runtime, Control 1B, Character
  Foundry 1C stay blocked.

## Blocking defects to fix

### BLK-ENV0-01 — Bridge-wide lease is asymmetric (AC5, Red F02)

`EnvironmentJobService._bridge_busy` scans environment receipts, character
receipts and probes the runner gate. `CharacterJobService._create_locked` checks
neither environment receipts nor Bridge busy state, and each service holds its
own `_create_lock`. Concurrent character and environment creates can therefore
both reach `QUEUED`.

Required: a single Bridge-wide create lock shared by both services, and a single
shared busy predicate consulted by **both** create paths. The character create
path must refuse with the existing busy semantics when an environment job is
`QUEUED` or `RUNNING`.

Also remove the private-attribute reach-in: `_bridge_busy` currently probes
`self.runner._worker_gate` with a non-blocking acquire/release. Replace it with
an explicit public accessor or a shared lease object. The probe is a TOCTOU
pattern and depends on another class's internals.

### BLK-ENV0-02 — No mutual lease evidence (AC5, Red F09)

Required tests, both directions, and they must prove refusal at **create** time
without ever running two Blender processes:

1. Active environment job `QUEUED`/`RUNNING` causes a character create to be refused.
2. Active character job `QUEUED`/`RUNNING` causes an environment create to be refused.

### BLK-ENV0-03 — Idempotency fingerprint includes identity fields (AC4, Red F03)

`canonical_request_fingerprint` uses a full `model_dump`, which includes
`request_id` and `idempotency_key`. Same key plus same semantic body plus a
rotated `request_id` therefore false-conflicts.

Required: exclude `request_id` from the canonical fingerprint (and preferably
`idempotency_key`, since it is the lookup key, not payload). Keep `request_id`
uniqueness enforcement as a separate concern. Add a test proving stable replay
across a rotated `request_id` with an unchanged body, and keep the existing
changed-payload conflict test green.

Consider ordering while you are here: the duplicate `request_id` check currently
fires before the idempotency replay check. Confirm and document the intended
semantics rather than changing it silently.

## Investigate, do not guess

`ENV0-BACKLOG-HTTP-PROBE-DEADLOCK` — E3 recorded that the TestClient POST hung
before create, so the real probe bypassed the HTTP layer. Produce a root-cause
finding on whether `BackgroundTasks` plus the shared worker gate deadlock under
TestClient. **A retry that happens to pass is not a root cause.** If the cause is
a real deadlock, it is in scope for this work order; if it is a harness artifact,
record the evidence and leave the code alone.

## Out of scope — do not touch

- `ENV0-BACKLOG-PREVIEW-UNDEREXPOSURE` (P1E lighting quality)
- Red F01 authentication, F04 `expected_bridge_revision`, F05 spec re-verify,
  F06 stuck-job reaper, F07 secondary registry ids, F08 output toggles, F10
  network deny hardening — all recorded, none authorized here
- Any Godot, Scene runtime, Character behaviour, Control, approved catalog or
  World Commit change
- `codex_directive.json` and all historical acceptance evidence

## Dispatch graph (same parent `019f7ffd-3995-71c0-aca1-51078e24a852`)

Sequential, one child at a time, no grandchildren.

- **C1** — `aidle-worldgen-asset-art`, `PATCH_DRAFT`, sole product writer.
  May write only: `app/services/environment_job_service.py`,
  `app/services/job_service.py` (lease wiring only), `app/dependencies.py`
  (shared lease wiring only), `tests/test_environment_*.py`, a new
  `tests/test_bridge_lease.py`, and its exclusive receipt/log/trace.
- **C2** — `aidle-worldgen-red-scope`, `READ_ONLY_AUDIT`, findings only.
  Must confirm the character-side refusal cannot be bypassed and that the
  fingerprint change does not weaken conflict detection.
- **C3** — `aidle-worldgen-qa-evidence`, `VERIFY_ONLY`. Full character
  regression plus environment suite plus the new lease tests, `compileall`, and
  one server-mediated real Blender probe. **This time the probe must go through
  the HTTP API end-to-end**, or the receipt must carry the root-cause finding
  explaining why that is impossible.
- **C4** — `aidle-worldgen-purple-acceptance`, `VERIFY_ONLY`. Re-verify AC4 and
  AC5 specifically, plus that criteria 1–3 and 6–10 have not regressed.

## Acceptance criteria

1. All 11 character regression tests remain green.
2. Environment suite remains green; new lease tests pass.
3. Character create is refused while an environment job is active — proven by test.
4. Environment create is refused while a character job is active — proven by test.
5. Stable replay holds across a rotated `request_id` with an unchanged body.
6. Same idempotency key with a changed canonical payload still conflicts without mutation.
7. No two Blender processes can run concurrently.
8. Real probe reaches `QUARANTINED_COMPLETE` exit 0 with full artifact set, or a
   documented root cause explains any HTTP-path limitation.
9. Criteria 1–10 of WO-ENV0-001 do not regress.
10. No Godot, Scene runtime, approved catalog or World Commit mutation.

## Receipt requirements

Every child writes a schema-valid `agent_step_contract` with a **real, durable
Grok Desktop `child_task_ref` and `transcript_ref`** — process-local UUIDs are a
defect, see the E2/E4 correction in `CONDUCTOR_JOURNAL.md` entry 008. Cross-check
each ref against `grok_status.json.completed_children` before finishing.

Also required: TrustLayer/UI character binding, authority token, all mandatory
plus routed skills loaded to EOF, input context hash, exact read/write set,
literal commands with exit codes, trace and handoff refs, `product_writes`,
`accepted=false`, `self_accept=false`.

Return `REVIEW_REQUESTED`, `CHANGES_REQUESTED` or `WAITING_HUMAN`. Never
self-accept. While Codex is unavailable, only the Human Product Lead may accept.

No install, credential, live provider or public network, push, deploy or publish.

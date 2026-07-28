# Codex re-entry handoff — AIdle ENV0

Prepared by: `aidle-continuity-conductor` (Claude)
Prepared at: 2026-07-21, during the Human-authorized continuity takeover
Purpose: hand coordination back to Codex, or forward to the next conductor, with
zero context reconstruction.

Trigger this handoff when conductor usage approaches its limit, or when Codex
becomes available again — whichever comes first.

---

> ## ⚠ THIS FILE IS STALE — superseded 2026-07-22 01:45
>
> **Written 2026-07-21 15:40. Everything below predates:**
> `G8 HUMAN PASS` · `ENV0-001` acceptance · the World 1 gate opening ·
> all of `P1E` (5 work orders) · the `world_DNA` integration · Tier 3 ·
> KIDI · the four-wave art programme · and an unresolved evidence-validity
> defect.
>
> **Read `CONDUCTOR_HANDOFF_FULL_001.md` in this same folder instead.**
> It is current and carries the full path index, open-defect ledger and lessons.
>
> The **paths** in Part 2 below remain accurate and useful.
> The **status, gates and the paste-ready prompt in Part 3 are superseded and
> must not be used** — a Codex session loading the old prompt would reconstruct
> a world in which G8 has not passed and P1E has not started. Both are now false.
>
> `codex_usage_hard_blocked_until` has since **disappeared** from
> `grok_status.json`, so Codex availability could **not be confirmed** at
> handoff time. Verify it directly; do not assume either state.

---

## Part 1 — State at handoff

**Directive in force:** 49. ENV0-001 only. Directive 47 is stale, ignore it.
**Parent session:** Grok Desktop `019f7ffd-3995-71c0-aca1-51078e24a852`. Unique.
Do not open another top-level session. Do not run Grok CLI.

**ENV0-001 status:** waves E0–E4 complete. Purple returned `CHANGES_REQUESTED`.
ENV0-001 is **NOT ACCEPTED**. `grok_status.json` holds
`state=CHANGES_REQUESTED`, `completion_signal=WAITING_HUMAN`,
`accepted=false`, `self_accept=false`.

**What is verified and trustworthy:**

- E0 `input_context_hash` reproduced byte-exact by the conductor
- Directive 49 `blueprint_contract_sha256` matches the build-spec schema exactly
- Real Blender probe `BLD-E89FC8A3F472`: exit 0, `QUARANTINED_COMPLETE`, all 8
  artifact hashes recomputed and matched, preview confirmed a genuine render
- 11 character + 17 environment = 28 tests pass, `compileall` clean
- All 5 receipt `child_task_ref` values now agree with `grok_status.json`

**What is open:** see Part 4.

---

## Part 2 — Exact paths

Everything below is absolute. Nothing else needs to be discovered.

### Control plane
```
E:\AIdle_openworld\orchestration\control\codex_directive.json          (Directive 49 — READ ONLY, never edit)
E:\AIdle_openworld\orchestration\control\grok_status.json              (Grok parent is the writer)
E:\AIdle_openworld\orchestration\control\conductor_handoff.json
E:\AIdle_openworld\orchestration\control\GROK_CONTINUITY_CAPSULE.md
E:\AIdle_openworld\orchestration\control\GROK_AUTONOMOUS_OPERATING_ENVELOPE_ENV0.md
E:\AIdle_openworld\orchestration\control\CONDUCTOR_JOURNAL.md          (conductor-owned, append-only)
E:\AIdle_openworld\orchestration\control\CODEX_REENTRY_HANDOFF.md      (this file)
```

### Work orders
```
E:\AIdle_openworld\orchestration\work_orders\WO-ENV0-001-ENVIRONMENT-BRIDGE-P0E.md          (done, CHANGES_REQUESTED)
E:\AIdle_openworld\orchestration\work_orders\WO-ENV0-002-LEASE-IDEMPOTENCY-CORRECTION.md    (current)
```

### Receipts and logs
```
E:\AIdle_openworld\orchestration\receipts\environment_p0\ENV0_schema_001.json
E:\AIdle_openworld\orchestration\receipts\environment_p0\ENV0_blue_001.json
E:\AIdle_openworld\orchestration\receipts\environment_p0\ENV0_red_001.json      (has evidence_correction)
E:\AIdle_openworld\orchestration\receipts\environment_p0\ENV0_qa_001.json
E:\AIdle_openworld\orchestration\receipts\environment_p0\ENV0_purple_001.json   (has evidence_correction)

E:\AIdle_openworld\orchestration\logs\environment-p0-schema-001.log
E:\AIdle_openworld\orchestration\logs\environment-p0-blue-001.log
E:\AIdle_openworld\orchestration\logs\environment-p0-red-001.log
E:\AIdle_openworld\orchestration\logs\environment-p0-qa-001.log
E:\AIdle_openworld\orchestration\logs\environment-p0-purple-001.log
```

### Governance
```
E:\AIdle_openworld\AGENTS.md
E:\AIdle_openworld\orchestration\ARCHITECTURE_LOCK.md
E:\standards\maf\COMPLIANCE.md                 (NOT readable from the Cowork conductor session)
E:\agents\characters\registry.yaml             (NOT readable from the Cowork conductor session)
E:\AIdle_openworld\orchestration\skills_manifest.yaml
E:\AIdle_openworld\.grok\agents\                (installed profiles)
```

### Blueprint (design contract input)
```
E:\AIdle_openworld\Scene\AIdle_Blender_Environment_Scene_Blueprint_v1.0\
  contracts\environment_scene_build_spec.schema.json    <- sha256 pinned in Directive 49
  contracts\environment_scene_manifest.schema.json
  contracts\environment_module_record.schema.json
  examples\cozy_starter_realm_build_spec.json
  grok_tools\environment_tool_definitions.json
  operations\environment_operation_allowlist.yaml
```

### Product under change (Bridge P0E)
```
E:\AIdle_Blender_Bridge_P0\app\environment_models.py
E:\AIdle_Blender_Bridge_P0\app\services\environment_job_service.py     <- BLK-01, BLK-03 live here
E:\AIdle_Blender_Bridge_P0\app\services\job_service.py                 <- BLK-01 character side
E:\AIdle_Blender_Bridge_P0\app\api\environment_jobs.py
E:\AIdle_Blender_Bridge_P0\app\dependencies.py
E:\AIdle_Blender_Bridge_P0\app\main.py
E:\AIdle_Blender_Bridge_P0\blender_scripts\environment_worker_entry.py
E:\AIdle_Blender_Bridge_P0\config\environment_*.yaml
E:\AIdle_Blender_Bridge_P0\templates\environments\
E:\AIdle_Blender_Bridge_P0\libraries\environments\
E:\AIdle_Blender_Bridge_P0\tests\
```

### Evidence artifacts from the accepted-quality probe
```
E:\AIdle_Blender_Bridge_P0\storage\jobs\BLD-E89FC8A3F472\environment_job_receipt.json
E:\AIdle_Blender_Bridge_P0\storage\jobs\BLD-E89FC8A3F472\blender_command.json
E:\AIdle_Blender_Bridge_P0\storage\jobs\BLD-E89FC8A3F472\blender_exit_code.txt
E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine\BLD-E89FC8A3F472\artifact_hashes.json
E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine\BLD-E89FC8A3F472\scene_manifest.json
E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine\BLD-E89FC8A3F472\validation.json
E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine\BLD-E89FC8A3F472\starter_realm_preview.png
E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine\BLD-E89FC8A3F472\starter_realm_probe.blend
E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine\BLD-E89FC8A3F472\modules\*.glb
```

### Known broken
```
E:\scripts\bootstrap-agent-session.ps1    <- parser error near line 52. Load context manually.
```

---

## Part 3 — Paste-ready Codex re-entry prompt

Copy everything between the markers into a fresh Codex session.

<<<BEGIN CODEX RE-ENTRY PROMPT>>>

You are resuming Codex coordination of the AIdle project. Project root
`E:\AIdle_openworld`. Do NOT run `E:\scripts\bootstrap-agent-session.ps1` — it has
a parser error near line 52. Load context manually by reading these files first:

E:\AIdle_openworld\AGENTS.md
E:\standards\maf\COMPLIANCE.md
E:\agents\characters\registry.yaml
E:\AIdle_openworld\orchestration\ARCHITECTURE_LOCK.md
E:\AIdle_openworld\orchestration\control\codex_directive.json
E:\AIdle_openworld\orchestration\control\grok_status.json
E:\AIdle_openworld\orchestration\control\conductor_handoff.json
E:\AIdle_openworld\orchestration\control\GROK_CONTINUITY_CAPSULE.md
E:\AIdle_openworld\orchestration\control\GROK_AUTONOMOUS_OPERATING_ENVELOPE_ENV0.md
E:\AIdle_openworld\orchestration\control\CONDUCTOR_JOURNAL.md
E:\AIdle_openworld\orchestration\control\CODEX_REENTRY_HANDOFF.md
E:\AIdle_openworld\orchestration\work_orders\WO-ENV0-001-ENVIRONMENT-BRIDGE-P0E.md
E:\AIdle_openworld\orchestration\work_orders\WO-ENV0-002-LEASE-IDEMPOTENCY-CORRECTION.md
E:\AIdle_openworld\orchestration\receipts\environment_p0\*.json
E:\AIdle_openworld\Scene\AIdle_Blender_Environment_Scene_Blueprint_v1.0

Situation. Directive 49 is the only authoritative directive; ENV0-001 only;
Directive 47 is stale. The Grok Desktop parent is
019f7ffd-3995-71c0-aca1-51078e24a852 and is the ONLY session — do not create a
new top-level session, do not run Grok CLI, do not spawn grandchildren.

ENV0-001 waves E0 through E4 are complete under a Human-authorized continuity
takeover run by the Claude conductor. E4 Purple returned CHANGES_REQUESTED, so
ENV0-001 is NOT ACCEPTED. Three blocking defects are open: BLK-ENV0-01 asymmetric
Bridge lease (AC5), BLK-ENV0-02 missing mutual lease tests (AC5), BLK-ENV0-03
idempotency fingerprint includes request_id (AC4). WO-ENV0-002 has already been
authored to close exactly those three and is the current work order.

Evidence you can rely on: E0 input_context_hash was independently reproduced
byte-exact; Directive 49 blueprint_contract_sha256 matches the build-spec schema
exactly; real Blender probe BLD-E89FC8A3F472 exited 0 at QUARANTINED_COMPLETE
with all 8 artifact hashes independently recomputed and matched and a confirmed
non-blank isometric render; 11 character plus 17 environment tests pass.

Known defect already corrected: the E2 and E4 receipts originally carried
process-local UUIDs instead of real Grok child ids. They were corrected with
explicit evidence_correction blocks preserving the previous values. All five
receipts now agree with grok_status.json. Do not treat this as tampering — read
CONDUCTOR_JOURNAL.md entry 008.

Open items you must not lose: the suspected BackgroundTasks / _worker_gate
deadlock that prevented an end-to-end HTTP probe; preview underexposure as a P1E
quality item; E:\standards\maf\COMPLIANCE.md and E:\agents\characters\registry.yaml
were unreadable from the conductor session so character binding claims are still
unverified; the E0 adversarial schema suite was never independently re-executed;
Grok Desktop is running in always-approve mode against AGENTS.md deny-by-default.

Constraints that remain in force: G8-001 stays HITL_REQUIRED; P1E, Scene runtime,
Control 1B and Character Foundry 1C stay blocked; no Godot, Scene runtime,
Character, Control, approved catalog or World Commit mutation; no dependency
install, credential, live provider, public network, push, deploy or publish;
accepted and self_accept remain false and only the Human Product Lead accepts
while you were unavailable.

Your task: verify the state above against disk yourself rather than trusting this
summary, then either issue the next directive superseding 49 for the WO-ENV0-002
correction pass, or record an acceptance decision. Append your own entry to
CONDUCTOR_JOURNAL.md when you take over.

<<<END CODEX RE-ENTRY PROMPT>>>

---

## Part 4 — Open items ledger

| # | Item | Where | Severity |
|---|---|---|---|
| 1 | `BLK-ENV0-01` asymmetric Bridge lease | `job_service.py`, `environment_job_service.py` | blocking AC5 |
| 2 | `BLK-ENV0-02` no mutual lease tests | `tests/` | blocking AC5 |
| 3 | `BLK-ENV0-03` fingerprint includes `request_id` | `environment_job_service.py` | blocking AC4 |
| 4 | HTTP probe deadlock, root cause unknown | `api/environment_jobs.py` + runner gate | high |
| 5 | COMPLIANCE.md / registry.yaml unreadable, bindings unverified | conductor session mount | evidence gap |
| 6 | E0 adversarial suite never re-executed independently | conductor sandbox jsonschema 3.2.0 | evidence gap |
| 7 | Red F01 unauthenticated env API | `app/` | high, deferred |
| 8 | Red F04/F05/F06 medium findings | `environment_job_service.py` | medium, deferred |
| 9 | Preview underexposed, luma max ~94/255 | lighting rig | P1E quality |
| 10 | `always-approve` mode vs AGENTS.md deny-by-default | Grok Desktop settings | governance |
| 11 | `bootstrap-agent-session.ps1` parser error line ~52 | `E:\scripts\` | tooling |

## Part 5 — Handover hygiene

Whoever takes over must:

1. Re-verify state against disk rather than trusting this document.
2. Append a new entry to `CONDUCTOR_JOURNAL.md` — never rewrite an existing one.
3. Keep `accepted=false` and `self_accept=false` until the Human Product Lead
   decides.
4. Never edit `codex_directive.json` unless acting as Codex proper.
5. Never impersonate Codex. A conductor signs as `aidle-continuity-conductor`.

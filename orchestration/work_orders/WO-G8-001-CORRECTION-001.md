# Work Order — G8-001 Correction 001: Non-mutating verification gate

Final machine acceptor: Codex. Continue only in the existing Grok Desktop
parent session. This correction supersedes the false machine-pass claim from
Directive 19; it does not invalidate the underlying G3/G4 functional results.

## Evidence-backed blocker

Directive 19 was `VERIFY_ONLY` and explicitly prohibited product, test and
prior-evidence edits. Its G3/G4 verification runs nevertheless changed these
tracked files:

- `game/scripts/modules/executor/exports/commit_request_handoff_stub.json`
- `game/scripts/modules/executor/exports/g3_cancel_receipt.json`
- `game/scripts/modules/executor/exports/g3_complete_receipt.json`
- `game/scripts/modules/executor/exports/g3_undo_receipt.json`
- `game/scripts/modules/executor/exports/world_prompt_from_build.json`
- `game/scripts/modules/persist/exports/g4_persist_smoke_evidence.json`

The changes are runtime-generated UUIDs, timestamps, receipt links and HMAC
seal values. They are not accepted product changes, but they contradict the
G8 report, collate receipt and status claims that prior evidence was untouched.

## Authorized workflow

Use only installed profiles in the existing parent; no nested grandchildren.

1. `executor` — `PATCH_DRAFT`, sole writer for the minimum G3 runtime/smoke
   files needed to send generated exports to an isolated `user://` test output
   location rather than tracked `res://` evidence. Runtime output must remain
   readable to the smoke and must not weaken revision, confirmation, cancel or
   undo assertions.
2. `persist` — `PATCH_DRAFT`, sole writer for the minimum G4 smoke file needed
   to stop copying generated HMAC evidence into tracked `res://` exports. Keep
   the isolated `user://g4_persist_smoke/` evidence and all 22 assertions.
3. The corresponding sole writer restores the six listed generated export
   files exactly to the committed baseline at `60fccdd`, using a minimal
   non-destructive patch. Do not use reset/checkout and do not alter accepted
   semantics.
4. `core` — `VERIFY_ONLY` Purple gate. Re-run G3 (76 checks), G4 (22 checks),
   validator and clean Godot boot, then prove the six tracked export files have
   zero diff from `60fccdd` after the runs.
5. `schema` — `VERIFY_ONLY` validates the three new correction step receipts
   directly against
   `E:/standards/maf/schemas/agent_step_contract.schema.json` using installed
   `jsonschema`; do not install `agentwork_runtime`.

One writer per file. Every profile writes only its new correction receipt under
`orchestration/receipts/g8/correction/`. Parent may update only the G8 report,
collate receipt, correction report and `grok_status.json` after verification.

## Acceptance

- G3 smoke still reports `G3_E2E_SMOKE=PASS checks=76`.
- G4 smoke still reports `G4_PERSIST_SMOKE=PASS checks=22`.
- Validator and clean fixed-angle 2.5D boot pass.
- The six pre-existing tracked export/evidence files remain byte-for-byte equal
  to commit `60fccdd` after every rerun.
- New runtime evidence exists only in an isolated `user://` test location.
- All correction receipts validate against the canonical MAF schema.
- G8 report/collate/status explicitly disclose Directive 19's failed scope
  claim and the correction evidence; no claim is silently rewritten.
- Machine verdict may return to `PASS_FOR_HUMAN_REVIEW` / `HITL_REQUIRED` only
  after Codex independently verifies these conditions.

No dependency install, live provider/network, credential, push, deploy or
publish. Parent cannot self-accept.

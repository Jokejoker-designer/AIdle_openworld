# WO-UCBV-001-C5H1-COMPANION-DEADLOCK-FIX-001

Author: `aidle-continuity-conductor` (Claude), acting conductor while Codex is out.
Class: UCBV-001 C5/H1 Human-gate correction (NOT a new program).
Status: **DISPATCHED. Directive 97 is active (`orchestration/control/codex_directive.json`),
superseding 96. Human authorized 2026-07-23T13:42+07:00, verbatim "Uk giao việc
cho Grok đi". Narrow Godot override for `game/scripts/main/main.gd` is granted.
Open for Grok's Blue worker under parent `019f7ffd-3995-71c0-aca1-51078e24a852`.
Still `accepted=false` — no self-accept; Purple/Codex/Human accept later.**
Source finding: `orchestration/control/HUMAN_GATE_FINDINGS_UCBV_001_H1_001.md`.
Evidence/receipt/log lease for this wave: `orchestration/{receipts,logs,evidence}/ucbv_001/c5h1_001/**`.

## Why this exists

The Human Product Lead play-tested the C5 build and hit a hard deadlock:
the Companion cannot be closed with E, and manual-build Confirm never enables.
Root cause is verified in code (read-only). The C5 Human gate therefore returned
a blocking finding — UCBV-001 must route to correction, not acceptance.

## Root cause (verified, for the Blue worker)

- `game/scripts/main/main.gd:235-238` — E key (`companion_call`) and
  `main.gd:228-231` (`prompt_quick_open`) unconditionally call
  `_open_companion_composer(true)`. They only OPEN.
- The correct toggle `_toggle_companion_chat()` (`main.gd:1190`) is wired only to
  the action-bar button (`companion_toggled`, `main.gd:1144-1145`), not to E.
- Open composer calls `player.set_locomotion_suppressed(true)` and holds focus,
  blocking build aim / LMB preview placement, so Confirm (gated on a placed
  preview) can never enable. Escape resolves `preview_hologram`/build before
  `prompt_composer_or_dialogue`, so it doesn't cleanly dismiss the Companion.

## Exact scope (one Blue writer, narrow Godot override)

**Write lease (Blue):** `game/scripts/main/main.gd` only.
**Test/evidence lease (QA):** one headed smoke script under
`game/scripts/**` or `game/tests/**` + evidence under
`orchestration/evidence/ucbv_001/**`.
**Forbidden:** any other `game/**` file, any catalog, any GLB, any directive,
any receipt. No behavior/authority change. No manual-build gating change (the
Confirm gate itself is correct and must stay).

## Required change (intent, Blue implements)

1. Route the E-key paths so that when the Companion is already open, E **closes**
   it. Candidate: in the `companion_call` and `prompt_quick_open` blocks, branch
   on `_chat_visible` — if open, call `_close_companion_composer()`; else keep the
   current `try_dispatch(...)` + `_open_companion_composer(true)`. (The existing
   `_toggle_companion_chat()` already encodes this open/close logic; reuse it, but
   ensure the router `try_dispatch` is only fired on open so closing requests the
   exploration context via `_close_companion_composer`.)
2. Confirm closing releases input: `_close_companion_composer` already calls
   `set_locomotion_suppressed(false)` — verify it actually fires on the E-close
   path and that build input resumes.
3. Secondary safety: ensure Escape can dismiss the Companion even when a build
   preview is active (either raise `prompt_composer_or_dialogue` so an open
   composer is resolved first, or add an explicit companion-close on Escape when
   `_chat_visible`). Do not regress the verified build-Esc-no-pause behavior.

## Acceptance criteria (QA must show, headed)

- Open Companion with E, press E again → Companion closes; player can move.
- Open Companion, close with E, enter build, LMB place a preview → **Confirm
  enables**; confirm commits through World Commit as before.
- Open Companion during an active build preview, press Escape → a defined,
  non-deadlocked outcome (either preview cancels then Companion closes on a
  second Escape, or Companion closes first — documented, not stuck).
- Zero new Godot errors; existing manifestation/collision and build-Esc-no-pause
  invariants unregressed.
- Headed evidence records the active art style / world profile (pond-white rule).

## MAF flow

Blue (patch `main.gd`) → Red (findings-only audit of the diff + the deadlock
scenarios) → QA (headed evidence of all criteria) → Purple (verify, never patch,
`WAITING_CODEX`). No self-accept. With Codex absent, machine acceptance waits for
Codex OR the Human Product Lead accepts explicitly per the Codex-absent capsule.

## Gate — satisfied, dispatched

(a) Human authorized the narrow Godot override for `game/scripts/main/main.gd`
— granted 2026-07-23T13:42+07:00. (b) Directive 97 is active, supersedes 96,
reroutes C5 to CHANGES_REQUESTED and opens this correction. (c) Verified before
promotion: `orchestration/receipts/ucbv_001/correction_010/` and
`orchestration/logs/ucbv_001/correction_010/` (directive 96's C5 Purple child)
do not exist on disk — nothing was in flight, so nothing was interrupted.
Dispatch is under the sole Grok Desktop parent `019f7ffd-3995-71c0-aca1-51078e24a852`.

# Codex re-entry — paste-ready prompt + forward direction

Prepared by: `aidle-continuity-conductor` (Claude), 2026-07-22 02:05 +07
Supersedes: the Part 3 prompt in `CODEX_REENTRY_HANDOFF.md`, which is stale
Companion: `CONDUCTOR_HANDOFF_FULL_001.md` (full state), `CONDUCTOR_JOURNAL.md`
(authoritative narrative, entries 001–035)

---

## The first thing Codex must know

**The work has outrun the directive.** Directive 50 is still current; its
milestone reads *"ENV0 Environment Bridge P0E correction"*. That finished hours
ago. Since then, under Human Product Lead authority: `ENV0-001` was accepted,
`G8` passed, the World 1 gate opened, and six further work orders ran
(`P1E-001` … `P1E-006`) plus `WO-OPS-004`.

**Codex's first act should be to issue Directive 51** covering the P1E art
programme, so the directive record matches reality. Everything done since 15:46
on 2026-07-21 was authorised by the Human Product Lead directly, not by
Directive 50, and the journal records each authorisation individually.

---

## Chosen forward direction — decided by the Human Product Lead

### Settled decisions, do not re-litigate

| Question | Decision |
|---|---|
| Engine version | **Stay Godot 4.3-stable.** 4.6 changes default physics to Jolt and default Windows backend to D3D12; that would invalidate every physics/visual measurement taken this session for no feature we need. Closed. |
| Taxonomy: art style vs world profile | **The 7 world profiles are the primary axis.** Art style is a future customisation layer. Each world profile maps to the nearest existing art style for now. |
| White-pond root cause | Art-style mismatch, not a material bug. Style tints ground/sky/ambient and procedural fillers, but **does not override GLB module materials**. |
| Fix approach | **Option B** — per-world-profile palette variants, reusing the existing `STATE_VARIANTS` mechanism rather than building a parallel system. |
| Red `F01` (unauthenticated env API) | **Deferred** by explicit decision — infrastructure and graphics first. Becomes a hard blocker before any networked work or shipping build. |
| Tier 3 | Taken out of the main queue to run as a separate track. `WO-P1E-005` written; the v1.1 DNA package now implements it. |
| KIDI | Adopt the **pattern**, not the package. `WO-OPS-004` written, not dispatched. |

### Immediate queue

1. **`WO-P1E-006`** — per-world-profile palette variants, 11 modules × 2
   profiles (`cozy_cyber_pixel`, `surrealism_canvas`). **Dispatched, in
   progress.** The other 5 world profiles get their variants when their kits
   land with P2E–P6E; do not pre-author.
2. **Art programme waves 2–4**, held until 006 verifies:
   - Wave 2 — 6 tree + 6 rock variants, static detail pass. Blender-only, no new override.
   - Wave 3 — 8 fauna + `AnimationPlayer` loop system. Override granted.
   - Wave 4 — toon shader + outline. Override granted. **First `.gdshader` in the project.**
3. **`WO-P1E-005`** — Tier 3 offline simulation, separate track.
4. **`WO-OPS-004`** — KIDI QA profile, separate session, no UI.

### Explicitly not started

`Control-1B` and `Character-Foundry-1C` — unblocked by G8 but never begun.
`P2E`–`P6E`. Any networked work.

---

## Paste-ready prompt

Copy everything between the markers into a fresh Codex session.

<<<BEGIN CODEX RE-ENTRY PROMPT>>>

You are resuming Codex coordination of AIdle. Project root `E:\AIdle_openworld`.
Do NOT run `E:\scripts\bootstrap-agent-session.ps1` — parser error near line 52.
Load context manually.

Read in this order:
E:\AIdle_openworld\orchestration\control\CONDUCTOR_HANDOFF_FULL_001.md
E:\AIdle_openworld\orchestration\control\CODEX_REENTRY_PROMPT_002.md
E:\AIdle_openworld\orchestration\control\CONDUCTOR_JOURNAL.md   (entries 001-035, append-only)
E:\AIdle_openworld\AGENTS.md
E:\standards\maf\COMPLIANCE.md
E:\agents\characters\registry.yaml
E:\AIdle_openworld\orchestration\ARCHITECTURE_LOCK.md
E:\AIdle_openworld\orchestration\workflow.json
E:\AIdle_openworld\orchestration\control\codex_directive.json
E:\AIdle_openworld\orchestration\control\grok_status.json
E:\AIdle_openworld\orchestration\tasks.json

Ignore the Part 3 prompt inside CODEX_REENTRY_HANDOFF.md — it is stale, written
before G8 passed and before P1E existed.

SITUATION. You issued Directive 50 at 15:46 on 2026-07-21 via a scheduled task,
then immediately exhausted your usage. A Claude continuity conductor coordinated
from then until now under Human Product Lead authority, never accepting anything
and never editing codex_directive.json or tasks.json. Your directive is now
stale: its milestone says ENV0 P0E correction, which is long done.

YOUR FIRST ACT should be to issue Directive 51 covering the P1E art programme so
the directive record matches reality.

WHAT HAPPENED SINCE. ENV0-001 was ACCEPTED by the Human Product Lead at 20:00 on
2026-07-21, scope = git tag env0-d50-verified at commit 1322b95 in
E:\AIdle_Blender_Bridge_P0. G8-001 was PASSED by her at 20:21 after a live
playtest, which also opened the World 1 integration gate and unblocked
Control-1B and Character-Foundry-1C, neither of which has been started. Work
orders completed: ENV0-002 closed the three blocking lease/idempotency defects;
Directive 50 waves W1-W4 closed Red F04/F05/F06; ENV0-003 fixed character API
busy to HTTP 409; G8-UX-001 fixed an action-bar focus trap plus player-vs-
manifestation collision; G8-UX-002 fixed fence rail collision; P1E-001 built the
7-module Cozy kit and fixed the lighting rig; P1E-002 built the Godot GLB intake
with runtime load from quarantine and no res:// promotion; P1E-003 fixed
exposure and added 4 missing props and raised density from 9 to 43 instances;
P1E-004 integrated a thin world_DNA pilot with 3 static and 2 dynamic modules
and proved Tier 3. P1E-006 is dispatched and in progress.

FOUR SCOPED GODOT OVERRIDES were granted by the Human Product Lead, each
recorded, since Directive 50 forbids Godot patches: G8-UX-001, G8-UX-002,
P1E-002 intake, and P1E art waves 3-4.

SETTLED DECISIONS, do not re-litigate: stay on Godot 4.3-stable; the 7 world
profiles are the primary axis and art style is a future customisation layer;
the white-pond defect was art-style mismatch not a material bug; fix approach is
Option B, per-world-profile palette variants reusing the existing STATE_VARIANTS
mechanism; Red F01 unauthenticated environment API is deferred by explicit
decision but becomes a hard blocker before any networked work or shipping build.

OPEN DEFECTS you must not lose: receipt verdict fields are still null; the G8
residual where a prior confirmed building can remain after cancelling a later
preview is unfixed; Red F07/F08/F10 deferred; TrustLayer character bindings were
never verified because E:\standards and E:\agents were unreadable from the
conductor session; the E0 adversarial schema suite was never independently
re-executed; receipts have never been validated against
agent_step_contract.schema.json and that gap is what let null child refs through;
Grok runs in always-approve mode against AGENTS.md deny-by-default.

HARD-WON LESSONS, each cost real time. A metric can pass for the wrong reason:
shadow=10.1% passed while 96% of that budget was one black void. A check that
fails one wrong value can still pass another: the pond was beige then white then
grey and all three passed the same RGB-distance check, because grey sits
numerically between colours while being visually nothing. Null is our NaN: a
null child_task_ref absorbs four distinct causes and destroys the evidence
needed to tell them apart. An incomplete allowlist is a work-order defect, not a
writer violation. Documentation is not implementation: the DNA package promised
Tier 3 and shipped only tier-number assignment. Presence of output is not
presence of capacity: a fresh directive appeared and the conductor wrongly
concluded you were back, retracted in journal entry 014. Evidence must be the
same artefact the human plays: the pond looked fixed in every PNG and was still
white on her screen because her session ran a different art style.

CONSTRAINTS unchanged: Grok Desktop parent 019f7ffd-3995-71c0-aca1-51078e24a852
is the only session, no new top-level session, no Grok CLI, no grandchildren.
No dependency install, credential, live provider, public network, push, deploy
or publish. P2E-P6E blocked. Never open_application on Grok, it spawns a
duplicate window; click the taskbar icon.

YOUR TASK: verify all of the above against disk rather than trusting this
summary, issue Directive 51, then resume machine acceptance. The Human Product
Lead has been the sole acceptor in your absence and every acceptance is recorded
in the journal with its evidence.

<<<END CODEX RE-ENTRY PROMPT>>>

---

## Handover hygiene

1. Verify against disk. This is a summary written by an agent; the receipts and
   the journal are the evidence.
2. Append to `CONDUCTOR_JOURNAL.md`, never rewrite an entry.
3. The Human Product Lead accepted `ENV0-001` and passed `G8` personally. Those
   are her decisions, recorded as hers, not agent decisions.
4. The conductor never edited `codex_directive.json` or `tasks.json`. Both are
   yours and both are untouched.

# Human-gate findings — UCBV-001 H1 / C5 play-test

Recorded by: `aidle-continuity-conductor` (Claude), acting continuity conductor
while Codex is out of usage. 2026-07-23.
Authority: advisory/coordination. **`accepted=false`. No self-accept.** When
Codex is absent, only the Human Product Lead accepts. This record does not edit
any directive, receipt, or `game/**` file.

## Context

The Human Product Lead play-tested the running UCBV-001 build (the exact product
surface at directive 96 / C5 Purple release) and returned two findings. This is
the H1 five-minute Human gate doing its job — machine gates C0–C5 passed while a
real deadlock and a visual-polish gap survived, the same pattern as the earlier
"43 green tests missed 6 defects a human caught in 90 seconds."

## Finding 1 — HARD BLOCKER: Companion + manual-build input deadlock

**Symptom (Human):** cannot close the Companion, and the manual-build Confirm
button stays disabled. Both panels stuck open (screenshot evidence).

**Root cause (verified in code, read-only):**
- `game/scripts/main/main.gd:235-238` — the **E key** (`companion_call`, and
  `prompt_quick_open` at 228-231) unconditionally calls
  `_open_companion_composer(true)`. It only ever OPENS.
- The function that correctly toggles open/close, `_toggle_companion_chat()`
  (`main.gd:1190`), is wired **only** to the action-bar button signal
  `companion_toggled` (`main.gd:1144-1145`), **not** to the E key.
- The HUD tells the user "Companion: press E to chat" — but pressing E again
  cannot close it.
- While the composer is open, `_open_companion_composer` calls
  `player.set_locomotion_suppressed(true)` and the composer holds focus, so
  build aiming / LMB preview placement is blocked. Manual-build Confirm is gated
  on a placed preview ("Status: Not ready — Aim cursor, then LMB to place
  preview"), so Confirm can never enable while the Companion holds input.
- Escape resolves `preview_hologram` / build cancel **before**
  `prompt_composer_or_dialogue` (`control_context_router.gd` resolve_escape
  priority), so in the tangled build+companion state Escape does not cleanly
  dismiss the Companion either.

**Net:** a genuine deadlock — E won't close the Companion, and no preview can be
placed to enable Confirm. The "Confirm stuck" symptom is a **consequence** of the
Companion deadlock, not a separate Confirm bug (the Confirm gating itself is
correct).

**Precise fix (small, surgical):** route the E-key paths (`companion_call` and
`prompt_quick_open` in `main.gd`) through `_toggle_companion_chat()` instead of
the unconditional `_open_companion_composer(true)`, so E closes an open Companion.
Confirm that closing releases locomotion suppression (`_close_companion_composer`
already calls `set_locomotion_suppressed(false)`). Optionally raise the Companion
in the Escape priority so it can always be dismissed. Estimated change: a few
lines in one file, plus a headed smoke proving open→E→closed and
open→place-preview→Confirm-enabled.

**Severity:** blocker. It sits on the product surface currently at C5 acceptance,
so **UCBV-001 should not be accepted as-is** — this is a C5/H1 correction, not a
pass.

## Finding 2 — VISUAL POLISH: Nori-7 reads as a plain white blob, wants "prettier/friendlier"

**Symptom (Human):** the in-game Nori-7 is not cute/friendly enough; redesign
requested.

**Assessment.** The runtime is the real `glb_c1r` GLB (verified previously:
14 bones, 10 clips, 9 materials incl. cream `#fdf3e2`), so this is a genuine
visual-quality gap, not a broken render. A redesign revises the design docs
(`game_character/ucbv_001/nori7/visual_package/visual_spec.json` +
`orchestration/design/ucbv_001/character/nori7/{U2_character_visual_silhouette.md,
modular_body_outfit_definition.json, proportion_guide.md, sheets/*}`) and then
**re-authors the Blender GLB** → a new GLB revision.

**Conflict to decide (not inferable):** the current Nori GLB is the artifact at
C5 acceptance. Redesigning it now competes with that acceptance. Three timing
options exist and belong to the Human/Codex, not to me:
1. Fix the deadlock, let UCBV-001 C5 close with the current Nori, then redesign
   as a follow-up character-backbone wave (keeps C5 moving).
2. Pull Nori from C5 and redesign now (larger scope, delays C5).
3. Treat the redesign as non-blocking visual polish layered after acceptance.

## Routing

- Finding 1 (deadlock): needs a code fix. As conductor I will not patch `game/**`
  on my own initiative — that needs an explicit narrow Godot override
  (Human grant, since Codex is out) or a Grok dispatch under lease. Diagnosis and
  the exact fix are ready above.
- Finding 2 (redesign): needs a Human/Codex timing decision vs C5 before any work.
- Machine acceptance of UCBV-001 remains withheld regardless — Codex absent, and
  the Human gate returned blocking findings.

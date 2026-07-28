# Grok town mockup redo-loop prompt 001

Paste into the BUILD session (`019f7ffd-3995-71c0-aca1-51078e24a852`). This
SUPERSEDES the framing in `GROK_TOWN_IMPORT_QA_FOLLOWUP_PROMPT_001.md` — that
one asked for evidence + honest disclosure of mismatches. The Human Product
Lead has now raised the bar: do not stop at disclosure, ITERATE until it
actually matches.

---

```
TOWN CADASTRE — DO NOT STOP UNTIL IT MATCHES THE MOCKUP (directive 99, WO-TOWN-GRID-IMPORT-001)

New standing instruction from the Human Product Lead, binding for this wave and
every future wave that places a mockup-sourced object into the game:

A wave is NOT done when a real GLB loads without error. It is done when:
  (1) the object in-game visually matches its MOCKUP_SSOT_V2 concept art 100%
      — silhouette, proportions, palette (art direction lock §5), key details —
      confirmed by a headed screenshot comparison, and
  (2) the object sits at the EXACT position, rotation, and named plot assigned
      to it in TOWN_GRID_PLAN_V1.json / game/resources/town/town_grid_plan_v1.json
      — not "close enough," the exact plot.

If either check fails, DO NOT report the mismatch and stop. Fix it and re-check,
in a loop, the same way the cozy_house_small_A redesign iterated v1 -> v7 until
the silhouette was stable. Budget: iterate freely; if the SAME failure signature
repeats 3 times unchanged, that is when you stop and route NEED_HUMAN (per the
standing 3-strikes rule) — not before.

Scope for this pass:
1. Re-run town cadastre QA headed (still owed from the last request): screenshot
   showing all 50 plots, zero new Godot errors, attach the raw headed log FILE
   PATH (not just a restated marker) so Claude can decode it independently.
2. For every plot that has a real production GLB (>=21 today): place its
   MOCKUP_SSOT_V2 concept art frame next to the in-game headed screenshot of
   that plot and self-assess match. Any silhouette/proportion/palette mismatch
   -> go fix it (author loop), re-render, re-compare. Log each iteration's
   attempt number in the receipt, same style as the cozy_house_small_A entries
   in CONDUCTOR_JOURNAL.md.
3. Verify placement: cross-check every plot's actual runtime transform
   (position/rotation) against its plan entry's transform. Any drift beyond
   float rounding is a placement bug, not a visual one -- fix the loader/data,
   not the mockup.
4. Keep going through the remaining 29 concept-only plots as you author each
   object over time (per the WO's "later" section) -- same rule applies to
   every one of them the day it gets a real GLB, not just today's 21.

Still binding: accepted=false, self_accept=false throughout; Purple stays
WAITING; one writer per file; no game/** file outside the named set; do not
delete starter_realm_builder.gd content or edit town_layout_10phase.json in
place; Red F01 hard stops unchanged.

Acknowledge with: (a) confirmation you will iterate-to-match rather than
report-and-stop, (b) the live directive_id, (c) which of the 21 real-GLB plots
you assess as already matching vs needing rework right now.

Full background: orchestration/receipts/town_grid_import_001/CLAUDE_VERIFY_001.json
```

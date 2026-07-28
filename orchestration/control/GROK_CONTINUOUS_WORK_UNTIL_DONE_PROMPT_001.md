# Grok build session (019f7ffd) — continuous work authorization (buildings + props + Nori-7 animation realism)

Paste the block below into Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852`
(the Build parent — this is the correct session for all of this; it is all game/**-touching
work). Authored by Claude conductor after relaying the Human Product Lead's ruling.

---

```
[SUPERVISOR DIRECTIVE] Continuous work authorized — keep going until each item is actually done

Human Product Lead watched the gardener animation live (real play, buttons work now) and
gave two pieces of feedback, plus one standing instruction:

1. Animation quality: "chưa đủ thực tế" — not realistic enough yet. Walking specifically
   should also have real animation, not read as a simplified/stub cycle.
2. The town/map is not finished — 6 buildings + 21 props still open.
3. Standing instruction: "kêu Grok tiếp tục công việc đến khi xong thì thôi" — keep working
   until each of these is actually done. This removes the "stop after one pass and come
   back to me" requirement that governed BUILDINGS_FIDELITY_V4 — you do not need to return
   to Human after every single iteration on the 6 buildings anymore. Same for props and the
   animation pass: keep iterating using your own judgment.

Full reference: orchestration/control/codex_directive.json → object_level_human_decisions →
"continuous_iteration_authorization" entry (decided_at 2026-07-24T12:30:00+07:00).

Three work streams, all now open for continued autonomous iteration:

A) 6 buildings toward 100% (MARKET.BLD, GARDEN.BLD, WELL.BLD, WINDMILL.BLD, BRIDGE.BLD,
   LOOKOUT.BLD): keep targeting each one's own residual signature (see
   BUILDINGS_FIDELITY_V4.json need_human_again for the latest signatures). Try genuinely
   different approaches if repeating the same fix isn't closing the gap (e.g. if density-only
   passes plateau, consider whether a different mesh/material approach or a new GLB module is
   needed — you flagged this possibility yourself for the street pavers earlier, same logic
   may apply here). File each iteration honestly (matching_100_pct per object, no inflation).

B) 21 missing props: author these to completion, same standard as the 8 buildings — real
   GLBs, headed QA, honest fidelity scoring, no placeholder-as-done.

C) Nori-7 animation realism (this is already-authorized tier1 "Nori-7 visual redesign" scope,
   confirmed by the Human as applying here — not a new permission, just confirming it covers
   this): improve overall motion naturalism across the 15 clips, and specifically give walk a
   real walk-cycle (weight shift / arm-leg counter-motion / not just a translate-in-place or
   overly simple loop) instead of whatever currently reads as a stub. Re-key on the existing
   mockup-parity mesh (no full mesh rebuild unless you determine one is genuinely required —
   if so, say so explicitly and treat it as its own decision point, don't silently do it).

Safety valve (still applies — this is not unlimited silent looping):
- If any ONE building or the animation pass hits the SAME residual signature 3 consecutive
  times even under this extended authorization (genuinely stuck, not just still-in-progress),
  file it as NEED_HUMAN and move on to other open items rather than looping indefinitely on
  that one object. Don't silently drop it either — name it in your status.
- HOME.BLD stays CLOSED_PERMANENTLY, untouched, always.
- No self-accept, ever. accepted=false, self_accept=false on every receipt regardless of how
  many iterations you run. Purple stays WAITING.
- Continue to work through your own "next" priority list; you do not need to check in with
  Human between passes on these three streams specifically — but DO still surface anything
  outside this defined scope (new conflicts, new blockers, anything requiring a product
  judgment call you can't make yourself) exactly like you did with CONFLICT_WD_GAZEBO_VS_HOME_BLD.

Work continuously; report progress in your normal receipts/journal-style updates, not by
waiting for a reply after each item.
```

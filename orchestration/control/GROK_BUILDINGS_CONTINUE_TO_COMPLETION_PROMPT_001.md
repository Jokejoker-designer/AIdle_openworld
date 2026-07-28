# Dispatch — Continue the 6 buildings to completion (paste to Grok, build parent 019f7ffd)

V12 (lighting root-cause fix in `town_grid_loader.gd`) and V13 (topology
residual pass) are verified real and honest — genuine progress, still
correctly not claiming 100% on any of the 6. Keep going with the same
method. This is a continuation, not a new instruction set.

## Keep doing exactly what's working

- Camera-match setup (fSpy-Blender + real_scale_references, pitch 42° /
  FOV 42°, mockup jpg background) stays in use.
- Keep pulling both levers per building as needed: town-lighting material
  accuracy (the `_boost_mockup_materials` key-map you already fixed once —
  check for other missed keys the same way if a building's color still
  reads wrong) and topology sharpness (edge definition, frames, discrete
  detail vs. smooth/soft-clay primitives).
- Redo-loop each of the 6 (MARKET, GARDEN, WELL, WINDMILL, BRIDGE, LOOKOUT)
  toward genuine 100% match against its own mockup jpg. V13's per-building
  notes already say exactly what's still short on each one (e.g. market
  awning still boxier than `bld_05`, windmill window density short of
  `bld_06`, bridge hue lighter than `bld_09`) — use those as your next
  target per building, don't restart from scratch.

## Safety valve, still binding

Any single building that hits the **same residual signature 3 times in a
row** stops iterating and routes `NEED_HUMAN` in its receipt — move on to
the others rather than looping it forever. So far all 6 have hit a fresh
signature every pass (V11→V12→V13), which is a good sign; keep it that way
by making a genuinely different adjustment each time, not a cosmetic
re-export.

## Quota awareness

Your weekly usage is running low. Prioritize whichever buildings are
closest to a real 100% match first — don't spend a full pass on a building
that's proportionally further away if a nearly-there one could close out
first. If you run out of usage mid-work, make sure the latest receipt
(`BUILDINGS_FIDELITY_V##.json`) and `CONTINUOUS_WORK_STATUS_###.json` are
written and saved *before* stopping, with an honest, complete snapshot of
exactly where each of the 6 stands — a future session will resume from
those files, not from memory of this conversation.

## Still frozen / unchanged

No plot position/rotation/footprint/grid-cell change. `HOME.BLD` stays
`CLOSED_PERMANENTLY`. No `cozy_camera.gd` changes. No new addon installs
beyond the two already authorized. No Godot version change, no
network/shipping. `accepted=false` / `self_accept=false` on every receipt,
always. Props, Nori-7 animation, HOME.CHAR, and architecture/story-bible
adherence continue exactly as already authorized in parallel — this
dispatch is just reinforcing the 6-buildings push, not replacing the other
streams.

Goal: as many of the 6 as genuinely reach 100% as possible, with any
truly-stuck one surfaced honestly rather than forced.

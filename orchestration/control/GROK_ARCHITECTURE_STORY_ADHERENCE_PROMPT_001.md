# Dispatch — Architecture + Story Bible Strict Adherence (paste to Grok, build parent 019f7ffd)

Human Product Lead directive (verbatim, 2026-07-24): "Bạn hãy thiết kế map
kiến trúc trò chơi thật hoàn chỉnh cũng như xây dựng cho tôi 1 bộ câu chuyện
cho AIdle openworld. Phát triển dựa trên map đang sử dụng hiện tại chứ đừng
thay đổi nó và yêu cầu Grok bám thật sát theo kiến trúc được thiết kế đó."
(Design a complete architecture map and a story bible, built on top of the
CURRENT map — do not change it — and require Grok to strictly follow that
design.)

Claude (conductor) has authored two new binding reference documents:

1. `orchestration/control/AIDLE_TOWN_ARCHITECTURE_DESIGN_001.md`
2. `orchestration/control/AIDLE_STORY_BIBLE_001.md`

Both read and re-confirm — never alter — `game/resources/town/town_grid_plan_v1.json`
(50 plots / 10 districts, positions/rotations/footprints frozen) and
`orchestration/control/visual_reference/town_plan/TOWN_FAIRY_STREET_PLAN_V1.json`
(path network, frozen). Read both new documents in full before doing anything
below.

## What this changes about your continuous work (WO-TOWN-GRID-IMPORT-001 +
## WO-OBJECT-DNA-NORI7-ANIM-VERTICAL-SLICE-001)

Nothing about scope or authorization changes. `continuous_iteration_authorization`
(codex_directive.json, decided_at 2026-07-24T12:30) still governs: keep
iterating the 6 buildings toward 100%, keep finishing the 21 props' fidelity
pass, keep refining Nori-7 animation realism, fix HOME.CHAR's sha mismatch
when convenient. The safety valve (3x identical signature -> NEED_HUMAN) still
applies. No self-accept, ever.

What changes is that from now on, **any building, prop, character, signage,
or dialogue identity work must match the identity given to that plot in
`AIDLE_TOWN_ARCHITECTURE_DESIGN_001.md` §3 and, where a character is
involved, `AIDLE_STORY_BIBLE_001.md`.** Concretely:

- Do not rename, reskin, or reassign any building/character/prop to a
  different district than the one `town_grid_plan_v1.json` already places it
  in. The architecture document explains why each is where it is; it does
  not permit moving it.
- If a future wave adds signage text, ambient dialogue, or flavor detail to
  a plot, it must be consistent with that plot's identity page (§3.1–3.10 of
  the architecture doc) and, for characters, with their bible entry (§3–§5
  of the story bible) — e.g. Bụi Mơ (Garden) is written as non-verbal/quiet;
  do not give her a chatty dialogue tree. Nori-7's voice must stay inside
  the Vision Lock §6 character lock (never claims certainty it doesn't have,
  never manipulates attachment).
- The six "visitor" characters' origin stories stay **unresolved** on
  purpose (story bible §5) — do not author a definitive backstory for any of
  them without a fresh Human directive; the mystery is intentional.
- No new plot, district, position, rotation, footprint, character,
  world_profile, or game system (trade economy, multiplayer visiting, farming
  loop, energy mechanic) is authorized by these documents. If a task seems to
  need one of those, stop and route to Human/Claude — same Red-F01-style
  discipline as everything else in this project.
- `HOME.BLD` remains CLOSED_PERMANENTLY, untouched, exactly as already
  decided.

## What to actually do now

1. Read both new documents end to end.
2. Continue the existing continuous-work streams (buildings V6+, props
   fidelity, Nori animation) exactly as already authorized — no new
   permission is being granted or needed here.
3. When you next touch any plot's presentation (signage, dialogue stub,
   ambient prop placement **within that plot's existing footprint**), match
   it to that plot's identity/voice as defined above. Do not backfill this
   retroactively across all 50 plots as a new task unless a future directive
   asks for that explicitly — this is a standing constraint on future work,
   not a new work order by itself.
4. Emit the usual schema-valid MAF receipt, `accepted=false`,
   `self_accept=false`, honest per-object status, for anything you do touch.
5. If anything in either document appears to conflict with
   `town_grid_plan_v1.json`, `TOWN_FAIRY_STREET_PLAN_V1.json`, or the Vision
   Lock, flag it — do not silently resolve it or silently ignore the new
   documents.

No file paths beyond the two named above are in scope for this dispatch by
itself; it is a reference/constraint update layered onto already-authorized
continuous work, not a new build task.

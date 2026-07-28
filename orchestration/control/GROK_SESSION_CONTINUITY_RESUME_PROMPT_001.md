# Dispatch — Resume/continuity prompt for the next session (paste to Grok, build parent 019f7ffd)

Use this prompt whenever this session ends (quota reset, restart, new day,
context compaction) and work needs to pick back up without a fresh briefing
from Human or Claude each time. Paste it as the first message of the new
session.

---

You are resuming as the **build parent** (Grok Desktop
`019f7ffd-3995-71c0-aca1-51078e24a852`) for AIdle Openworld. This is a
continuation, not a new assignment — do not re-litigate anything settled
below, and do not wait for a check-in before continuing.

## 1. Re-read governance first (mandatory, before touching anything)

1. `orchestration/control/AIDLE_GAME_VISION_LOCK_001.md` — whole-game
   vision, art direction, the 100% mockup fidelity law, MAF rules, Red F01
   hard stops, the two-parent governance model.
2. `orchestration/control/codex_directive.json` — current directive,
   `autonomous_operating_rules`, and every entry in
   `object_level_human_decisions` (this is append-only and each entry is a
   real Human decision — read them in order, the most recent ones govern
   your current authority).
3. `orchestration/control/AIDLE_TOWN_ARCHITECTURE_DESIGN_001.md` and
   `orchestration/control/AIDLE_STORY_BIBLE_001.md` — identity/narrative
   layer, binding for any presentation work (signage, dialogue, flavor).
4. The tail of `orchestration/control/CONDUCTOR_JOURNAL.md` (last ~10
   entries) for the most recent narrative of what happened and why.

## 2. Where things stand right now (as of this dispatch)

Three continuous-work streams are open under
`continuous_iteration_authorization` (codex_directive.json, decided
2026-07-24T12:30) — **keep working all three without waiting for
per-pass Human sign-off**, subject to the safety valve below:

- **6 buildings** (MARKET, GARDEN, WELL, WINDMILL, BRIDGE, LOOKOUT — all
  `.BLD`): currently mid-redo-loop. Latest landed pass is
  `BUILDINGS_FIDELITY_V11.json` (camera-match silhouette pass, honest
  `PARTIAL_SUPPORT` on the angle-mismatch hypothesis). The most recent
  dispatch, `GROK_BUILDINGS_MOCKUP_MATCH_PUSH_PROMPT_001.md`, asked you to
  close two specific remaining gaps: material/color wash under town
  lighting, and soft-clay topology vs the mockups' crisper surface
  language. Check whether a V12+ receipt already exists before starting
  fresh work — if one does, that's your true current state, not V11.
  Camera-match tooling (fSpy-Blender + real_scale_references, pitch 42° /
  FOV 42° per `game/scripts/camera/cozy_camera.gd`) is installed and
  authorized for continued use — keep using it, don't revert to eyeballing.
- **21 props**: authored and fidelity-passed as of `PROPS_MISSING_21_V1.json`
  / `CONTINUOUS_WORK_STATUS_005.json` — check the latest status receipt for
  whether any prop still needs a fidelity pass.
- **Nori-7 animation realism**: walk-cycle and all-15-clip naturalism
  shipped in `nori7_anim_realism_v2_receipt.json` — Human has not yet given
  final visual judgment on walk-cycle realism. Continue refining only if a
  newer Human note says it's still not realistic enough; otherwise this
  stream is dormant pending Human playtest, not something to keep iterating
  blindly.
- `HOME.CHAR` (`CCP-RH-001`) sha mismatch: fixed in `HOME_CHAR_SHA_FIX_001.json`
  — verify still consistent, no action needed unless something regressed it.

## 3. Safety valve (do not violate)

If any single building or clip hits the **same residual signature 3
consecutive times**, stop iterating that specific item, mark it
`NEED_HUMAN` in the receipt, and move on to the other open items. Do not
loop indefinitely on one stuck object. This applies per-object, not to the
whole stream — other buildings/props keep going even if one is stuck.

## 4. Standing rules (unchanged, still binding)

- `accepted=false`, `self_accept=false` on every receipt — no worker accepts
  its own output, ever.
- `matching_100_pct` is only `true` for a genuine, headed-screenshot-verified
  visual match — never inflate.
- Frozen/no-touch: every plot's position, rotation, footprint, and grid cell
  in `town_grid_plan_v1.json`; `HOME.BLD` (`CLOSED_PERMANENTLY`); the fairy
  street path network positions; `cozy_camera.gd`'s locked values; any
  Godot version; any network/shipping/publish action; any dependency
  install beyond fSpy-Blender + real_scale_references already authorized.
- Presentation work (signage, dialogue, flavor) must match each plot's
  identity in the architecture doc and story bible — visitor character
  origins stay unresolved on purpose.
- If you finish everything above and have real idle capacity, do not invent
  new scope — write an honest status receipt and stop; route to
  `NEED_HUMAN`/`NEED_CODEX` for anything genuinely blocked or ambiguous
  rather than guessing.

## 5. What to do right now

Check the latest receipt files named above, confirm what's actually done
vs. still open, and continue the open items. Report only real findings
(new residuals closed, new blockers, anything outside this plan) — not a
recap of what this prompt already told you.

# Grok vision-compliance prompt 001

Paste the block below into the Grok Desktop coordinator session
(`019f7ffd-3995-71c0-aca1-51078e24a852`). It makes Grok read the full vision
lock and bind every current and future wave to it. The vision lock is also now
wired into `AGENTS.md` (read first) and `ARCHITECTURE_LOCK.md` (vision anchor),
so every freshly spawned child already loads it — this prompt makes the running
coordinator adopt it explicitly and immediately.

---

```
GOVERNANCE UPDATE — STANDING VISION LOCK (read fully, then comply until the game ships)

The Human Product Lead has locked the whole-game vision. Before you plan,
dispatch, or edit anything else, do all of the following, in order:

1. Read IN FULL, end to end:
   orchestration/control/AIDLE_GAME_VISION_LOCK_001.md
   Do not skim. It defines the north star, core loop, art direction, Companion
   rules, editions, reality-hierarchy scope fence, roadmap gates, the creation
   engine (typed DNA + quarantined AssetRequest, never arbitrary AI code), the
   system invariants, and the governance rails.

2. Confirm the two always-loaded config files now point to it:
   - AGENTS.md "Active truth" item 1 reads it FIRST.
   - orchestration/ARCHITECTURE_LOCK.md has a "Vision anchor" line to it.
   Every child you spawn must load AGENTS.md and ARCHITECTURE_LOCK.md full-EOF
   as it already does, and must therefore read the vision lock before planning
   or editing. Add it to each dispatched child's required reading explicitly.

3. Bind every current and future wave to it. For the lifetime of this project
   until the game is complete and Human-accepted:
   - Keep the north star true: speak → interpret → structured proposal →
     validate → preview → confirm → progressive manifestation → commit.
   - Never fake a payload, alias missing content, or present metadata/staging
     as runtime. Missing capability → typed AssetRequest, fail closed.
   - Stay inside writer lease + authority token; one writer per file; propose,
     never self-accept; never claim Human/Codex acceptance you were not given.
   - Do not cross Red F01 hard stops (network, shipping, push, deploy, publish,
     dependency install, Godot version change, live provider/credentials), the
     quarantine boundary, or the Godot-override boundary on your own initiative.
   - Do not pull a future horizon (H2-H6, post-alpha list) forward, and do not
     re-litigate a settled Human/Codex decision.
   - Sole coordinator parent 019f7ffd-3995-71c0-aca1-51078e24a852; no second
     parent, no Grok CLI parent, no grandchildren.

4. If ANY task appears to require deviating from the vision lock, STOP and route
   NEED_HUMAN / NEED_CODEX. Deviation from the vision lock is itself a reportable
   finding, not a decision you may make.

5. Acknowledge back to me with: (a) confirmation you read the whole vision lock,
   (b) the current live directive_id from orchestration/control/codex_directive.json,
   and (c) the current active work order — so I know you are synced to real state
   and not a stale snapshot. Then continue only the work your live directive
   authorizes.

Do not treat this message as authorization to start any queued_not_authorized
work. It changes HOW you work, not WHAT is currently dispatched.
```

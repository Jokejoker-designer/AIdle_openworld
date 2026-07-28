# Grok session self-persist vision prompt 001

Paste the block below into the Grok Desktop session you want to bind
(the running coordinator `019f7ffd-3995-71c0-aca1-51078e24a852`, or a fresh
chat). It asks Grok to write a durable vision-compliance record **into its own
session directory** under `C:/Users/phant/.grok/sessions/...` and prove it.

Honest notes (from the conductor):

- I (Claude) **cannot** write to `C:/Users/phant/.grok/**` — it is outside my
  access and is Grok's own application space. Only Grok can safely write there,
  because only Grok knows its exact session layout. That is why this is a prompt
  for Grok, not something I did directly.
- I also cannot guarantee Grok auto-reloads a file dropped in its session dir on
  every future turn — that is Grok-internal behavior. So the **durable,
  guaranteed** layer is still the project file
  `orchestration/control/AIDLE_GAME_VISION_LOCK_001.md`, already wired into
  `AGENTS.md` and `ARCHITECTURE_LOCK.md` (which every child loads full-EOF).
  This session-path write is an **extra reinforcement** for the live session,
  not a replacement.
- The prompt is deliberately **safe**: it creates a NEW adjunct file and forbids
  overwriting `meta.json` or any existing internal session-state file.

---

```
SELF-PERSIST THE VISION LOCK INTO YOUR OWN SESSION MEMORY

You are the AIdle coordinator. The Human Product Lead wants this session to
durably remember and obey the whole-game vision for the rest of the project.
Do the following, carefully and in order:

1. Read IN FULL:
   E:/AIdle_openworld/orchestration/control/AIDLE_GAME_VISION_LOCK_001.md

2. Determine your own session root directory. It is the parent-session folder
   under your Grok home, i.e. the directory that contains your subagents/ and
   meta.json for parent session 019f7ffd-3995-71c0-aca1-51078e24a852. It looks
   like:
     C:/Users/phant/.grok/sessions/<encoded-downloads-path>/019f7ffd-3995-71c0-aca1-51078e24a852/
   Confirm the exact path from your own environment — do NOT guess it. If you
   maintain a proper durable-memory store or notes mechanism, use that as the
   primary target.

3. Write a NEW file in that session root named:
     VISION_LOCK_COMPLIANCE.md
   containing:
     - a one-line pledge: "This session obeys AIdle_GAME_VISION_LOCK_001 until
       the game is complete and Human-accepted."
     - the absolute source path
       E:/AIdle_openworld/orchestration/control/AIDLE_GAME_VISION_LOCK_001.md
     - the sha256 of that source file (compute it) so drift is detectable
     - the current live directive_id from
       E:/AIdle_openworld/orchestration/control/codex_directive.json
     - the 8-point standing operating contract from section 14 of the vision lock
     - the sole coordinator parent id 019f7ffd-3995-71c0-aca1-51078e24a852

   SAFETY: create only this new adjunct file. Do NOT overwrite, truncate, or
   edit meta.json or any existing internal session-state file. If a same-named
   file exists, read it first and update in place, preserving anything else.

4. Re-read the file you just wrote to confirm it persisted.

5. Acknowledge back to me with:
   (a) the exact absolute path you wrote,
   (b) the sha256 you recorded for the vision lock source,
   (c) the live directive_id you read,
   (d) confirmation you did NOT touch meta.json or any internal state file.

6. From now on, at the start of each work turn, re-read VISION_LOCK_COMPLIANCE.md
   (and the project vision lock it points to) before planning or editing, and
   keep every wave aligned to it. If any task conflicts with it, STOP and route
   NEED_HUMAN / NEED_CODEX — deviation is a reportable finding, not your call.

This message changes HOW you work and what you remember. It does NOT authorize
starting any queued_not_authorized work.
```

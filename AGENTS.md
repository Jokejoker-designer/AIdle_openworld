# AIdle Openworld agent rules

## Active truth

1. Read `orchestration/control/AIDLE_GAME_VISION_LOCK_001.md` FIRST — it is the
   standing whole-game vision every agent must follow until the game is
   complete. Then read `AIdle_Openworld_Blueprint_v1.1/00_README.md` and
   `orchestration/ARCHITECTURE_LOCK.md` before planning or editing.
1b. For **character, animation, prop, building, manifestation visuals**, also
   read and obey `orchestration/control/visual_reference/mockup_ssot_v2/MOCKUP_DESIGN_LOCK.md`
   and open `MOCKUP_SSOT_V2.html` (15 cast + 30 props + 10 buildings). Game art
   must bám sát that mockup; mockup delta fail = CHANGES_REQUESTED.
1c. For **town production (10 phases: 1 cast + 1 building + 3 props each)** use
   `orchestration/control/town_build_10phase/` — subagents, layout, and
   `MOCKUP_PARITY_100` gate. Do not stop a phase until parity 100. Runtime town:
   `game/scripts/modules/town/town_layout_loader.gd` +
   `game/resources/town/town_layout_10phase.json`.
1d. **Wave packets** must follow `orchestration/control/WAVE_PACKET_TEMPLATE_V1.md`
   (Read list → Blue/Red/QA/Purple → Honesty → Mockup fidelity if SSOT → Escalate →
   Acknowledge then run). Purple cannot proceed without `QA_<wave>_001.json`
   existing (headed evidence + raw log file path).
2. `AIdle_Openworld_Blueprint_v1.0/` is historical input, never implementation authority.
3. Every world mutation uses `contracts/world_prompt.schema.json`.
4. An LLM proposes; only the World Commit service mutates canonical state.
5. Deviating from `AIDLE_GAME_VISION_LOCK_001.md` is itself a reportable
   finding; if a task appears to require it, stop and route `NEED_HUMAN` /
   `NEED_CODEX` rather than proceed.

## MAF and TrustLayer

- `E:\scripts\bootstrap-agent-session.ps1` is currently known to have a parser
  error near line 52. Do not retry it in a loop. Load COMPLIANCE, registry,
  MASTER_PLAN and JOURNAL_LATEST manually and record the bootstrap limitation.
- Agent = named role + context + tools + authority token.
- Use project files for session/state; do not depend on hidden chat context.
- Tool calls are deny-by-default. Shell, dependency installation, publishing,
  destructive changes, paid compute and external uploads require HITL.
- Significant steps return an `agent_step_contract` and evidence references.
- Red/reviewer finds only; Blue worker patches only an approved work order;
  Purple verifies and never patches.
- A worker cannot accept its own output. One writer owns each file at a time.

## Required workflow

`READY -> CLAIMED -> IN_PROGRESS -> REVIEW_REQUESTED -> VERIFIED -> ACCEPTED`

Failures route to `CHANGES_REQUESTED`. Three identical failure signatures route
to `NEED_HUMAN`. Production deploy, public publish, marketplace money, city-data
licensing and irreversible world changes always stop at `HITL_REQUIRED`.

## Product invariants

- Prompt -> structured proposal -> validate -> preview -> confirm -> commit.
- Manifestation: wireframe -> hologram -> materializing -> complete.
- Offline Private Reality may simulate locally; durable ownership/economy and
  every visited/shared space are server-authoritative.
- World-model video and generated meshes are untrusted artifacts, never world truth.
- No arbitrary AI-generated code executes in the game or authoritative server.
- Provenance, idempotency, rollback and world revision checks are mandatory.

## Completion honesty

Do not claim complete without executable acceptance evidence. Documentation is
not implementation; a passing unit test is not multiplayer or visual proof.

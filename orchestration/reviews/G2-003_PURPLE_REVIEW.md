# Purple VERIFY_ONLY review — G2-003

| Field | Value |
|---|---|
| Task | G2-003 — Companion proposal + bounded personality boundary |
| Reviewer | Purple / Devil's Advocate |
| Authority | VERIFY_ONLY (no product patches; no tasks.json ACCEPT) |
| Date | 2026-07-20 |
| Work order | `orchestration/work_orders/WO-G2-003.md` |
| Worker receipt | `orchestration/receipts/G2-003.json` |

## VERDICT

**ACCEPTED**

Text-only Companion produces schema-valid World Prompt proposals with
`confirmation.state=pending`, exposes no commit/durable-mutate tool, enforces
personality drift caps from `personality_profile.schema.json`, and implements
inspect / lock / reset / delete controls (API + text commands). Python and Godot
smokes re-run **PASS**.

## Acceptance matrix

| Criterion | Result | Evidence |
|---|---|---|
| Schema-valid World Prompt proposal | **PASS** | Export `game/scripts/modules/companion/exports/companion_proposal_cozy_house.json` validates against `contracts/world_prompt.schema.json` via `smoke_g2_003.py` (jsonschema Draft 2020-12 + format checker) |
| No direct commit tool | **PASS** | `CompanionWorldPromptBuilder.has_commit_tool() == false`; tool list marks `commits/mutates_world` false; source audit forbids commit symbols |
| Slow drift caps | **PASS** | Caps hard-coded ≤ schema: turn 0.005 / day 0.03 / distance 0.25; Godot smoke rejects over-cap + min-obs gates |
| Inspect / lock / reset / delete | **PASS** | API on `CompanionPersonalityProfile` + `CompanionModule`; text `/inspect`, `/lock`, `/reset`, `/delete` |
| Text-only (no STT/TTS/voice) | **PASS** | Module comments + smoke keyword audit; no AudioStreamMicrophone/TTS deps in companion tree |
| REVIEW_REQUESTED + receipt | **PASS** | Receipt no self-ACCEPT |

## Independent smoke (re-run)

### Python

```
python game\scripts\modules\companion\smoke_g2_003.py
→ EXIT=0
→ G2-003_SMOKE=PASS
   proposal_ok=.../companion_proposal_cozy_house.json
   personality_ok=.../default_personality_profile.json
   no_commit_tool_surface=true
   drift_caps_ok=true
   text_only=true
```

### Godot

```
tools\Godot_v4.3-stable_win64_console.exe --headless --path game -s res://scripts/modules/companion/companion_headless_smoke.gd
→ EXIT=0
→ G2-003_GODOT_SMOKE=PASS
```

Godot smoke asserts: NL→house proposal pending + recipe `cozy_house_small`, no commit tools, observation min gates, turn cap, lock blocks drift, reset/delete, inspect text contains caps.

### Integrated boot interaction

Full project boot (`--quit-after 5`) registers:

- `[ModuleRegistry] Registered module: companion (CompanionModule)`
- `[CompanionModule] Ready – text-only, proposal-only (no commit tool).`
- `[ModuleStub] companion slot upgraded to CompanionModule (G2-003).`

No companion GDScript parse errors (clears prior Codex G2-001 integration hold).

### Project validator

`python scripts\validate_project.py` → `AIDLE_VALIDATION=PASS`.

## Code / export spot-checks

### Proposal export

- `schema_version: 1.1.0`
- `entity.kind: modular_structure_2_5d`, `recipe_id: cozy_house_small`
- `style_profile.base_concept: cozy_cyber_pixel_2_5d` (enum member)
- `confirmation.preview_required: true`, `state: pending` (companion does not confirm/commit)
- `provenance.generated_by: companion_lumi`

### Personality

- Export + runtime defaults align with schema caps.
- Controls: `inspect` / `lock_trait` / `reset_adaptive_to_base` / `delete_adaptation_history`.
- `apply_observation` clamps desired step to turn/day remaining and distance-from-base.

### Tool surface

- Builder documents proposal-only tools; `has_commit_tool()` scans for commit/mutate names and flags.
- Module explicitly refuses durable SceneTree world mutation authority (Executor/World Commit owns pipeline).

### Forbidden paths

- No STT/TTS/voice cloning/microphone pipeline in companion module sources (static audit).
- Contracts schemas not edited (consume-only).

## Residual / non-blocking

1. No free-form LLM gateway — deterministic intent map only (correctly listed `not_done`).
2. Chat panel scene provided; not auto-instanced into main HUD (main.gd outside allowed paths).
3. Executor hand-off is stub — G3-001 owns transaction.
4. `tasks.json` still `READY` while WO/receipt claim `REVIEW_REQUESTED` — conductor control-plane lag.

## Blockers

**None.**

# WO-OPS-002 — Grok parent routing preload

Task: OPS-002  
State: TODO / blocked by OPS-001 acceptance  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852` only

## Objective

Load the two user-provided orchestrator documents directly into the existing
Grok Desktop parent so it cannot confuse Character and World Genesis routing.
This task creates no child and no new top-level session.

## Parent-only required reads

The parent itself—not an onboarding child—must read both files completely
through EOF:

1. `game_character/AIdle_Grok_Character_Subagents_v1.0/01_GROK_ORCHESTRATOR.md`
2. `Scene/AIdle_Grok_WorldGenesis_Subagents_v1.0/01_MASTER_ORCHESTRATOR.md`

It must also read the accepted
`orchestration/registries/grok_specialist_profiles_v1.json` from OPS-001 and
reconcile all 21 profile names with the two routing workflows.

## Evidence

The parent records in `orchestration/control/grok_status.json`:

- exact path, SHA-256, line count and full-read chunk ranges for each file;
- `character_orchestrator_loaded_by_parent=true`;
- `worldgen_orchestrator_loaded_by_parent=true`;
- `specialist_registry_count=21`;
- `new_top_level_sessions=0` and `specialists_spawned=0`;
- routing precedence: Architecture Lock → current directive/work order →
  Character/World Genesis orchestrator pack → specialist source profile.

No child, profile, product, test, evidence, Scene, Character or Control file is
written. Parent may update only `grok_status.json`, then returns
`REVIEW_REQUESTED / WAITING_CODEX`, `accepted=false`.

## Gate

No Character or World Genesis specialist may be spawned until Codex accepts
OPS-001 and independently verifies this parent-side preload. The first product
wave remains a separate future directive.

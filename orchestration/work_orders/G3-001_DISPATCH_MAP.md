# G3-001 Dispatch Map — Directive 10

Parent: existing Grok Desktop conductor (aidle-conductor)  
Task: G3-001 only  
Final acceptor: Codex (parent must not self-ACCEPT)  
Profiles: all 8 installed under `.grok/agents/`

## Wave order

| Wave | Profiles | Authority | Writes |
|---|---|---|---|
| W0_VERIFY | schema, network, persist | READ_ONLY_AUDIT / VERIFY_ONLY | receipts + handoff notes only under `orchestration/receipts/g3/` |
| W1_DOMAIN_PATCH | core, manifestation, companion, asset | PATCH_DRAFT | disjoint owned files only |
| W2_EXECUTOR_INTEGRATE | executor | PATCH_DRAFT | integration coordinator + E2E smoke only |
| W3_PURPLE_REVIEW | network (non-writer this wave) | VERIFY_ONLY | review file only |

## File ownership (one writer per file)

### Reserved for W2 executor (do not write in W1)

- `game/scripts/modules/executor/**` (all)
- `game/scripts/modules/g3/**` (transaction coordinator if created)
- `game/scripts/modules/g3_vertical_slice/**` or `game/scripts/modules/executor/g3_onboarding_slice.gd`
- `game/scripts/modules/executor/g3_e2e_smoke.gd`
- `game/scripts/modules/executor/exports/**` (complete/cancel/undo receipts)
- `orchestration/receipts/G3-001.json` (parent collates final; executor may draft smoke section)

### W1 core

- `game/scripts/main/main.gd` (wire G3 entry / mount only if needed)
- `game/scenes/main/main.tscn` (minimal mount nodes only if needed)
- `game/scripts/modules/g3_ui/**` OR `game/scenes/ui/g3_onboarding_hud.gd` + `.tscn` (Starter Realm UI shell)
- `game/scripts/world/starter_realm.gd` (if created; scene wiring only)

### W1 manifestation

- `game/scripts/modules/manifestation/manifestation_module.gd`
- `game/scripts/modules/manifestation/manifestation_instance.gd`
- `game/scripts/modules/manifestation/g3_preview_bridge.gd` (if needed)

### W1 companion

- `game/scripts/modules/companion/companion_module.gd`
- `game/scripts/modules/companion/agm_decision_applier.gd`
- `game/scripts/modules/companion/g3_onboarding_presenter.gd` (if needed)

### W1 asset

- `game/scripts/modules/asset/**` (create if missing)
- `game/assets/recipes/cozy_house_small.json` (mirror only if needed)
- `game/scripts/modules/asset/house_recipe_resolver.gd`
- `game/scripts/modules/asset/g3_recipe_smoke.gd` (optional)

### W0 read-only (no product writes)

- schema / network / persist: contracts, existing modules — reports only

### W3 purple

- `orchestration/reviews/G3-001_PURPLE_REVIEW.md` only

## Handoff artifacts (W0 → W1)

Each W0 agent writes `orchestration/receipts/g3/W0_<profile>.json` agent_step_contract.

## Handoff artifacts (W1 → W2)

Each W1 agent writes `orchestration/receipts/g3/W1_<profile>.json` with exported APIs used by executor.

## Constraints

- No nested grandchildren subagents
- No tasks.json / codex_directive / architecture / contracts edits
- No TTS/STT/API credentials/voxel/blockchain/push/deploy
- Text-only Companion; 2.5D fixed-angle; World Commit is handoff stub

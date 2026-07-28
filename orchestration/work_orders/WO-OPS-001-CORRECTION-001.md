# WO-OPS-001-CORRECTION-001

Directive: 42  
Task: OPS-001  
State: CHANGES_REQUESTED  
Parent: existing Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852` only

## Scope

Correct only the two canonical-authority mismatches and missing required-read
evidence identified in
`orchestration/reviews/CODEX_OPS-001_PROFILE_ONBOARDING_REVIEW_021.json`.
OPS-002 and all specialist execution remain blocked.

## Child

Parent coordinator-only. Resume exactly the real OPS-001 schema lineage
`019f8347-f5fa-7aa3-b5ce-d24170e1aeb3` as one correction child with
`PATCH_DRAFT` authority. No second child, support profile or grandchild.

## Required full reads

The correction child must read completely through EOF and record exact paths,
line counts, SHA-256, chunk ranges and transcript refs for:

1. `game_character/AIdle_Grok_Character_Subagents_v1.0/01_GROK_ORCHESTRATOR.md`
2. `game_character/AIdle_Grok_Character_Subagents_v1.0/workflow/CHARACTER_DEVELOPMENT_WORKFLOW.md`
3. `Scene/AIdle_Grok_WorldGenesis_Subagents_v1.0/01_MASTER_ORCHESTRATOR.md`
4. `Scene/AIdle_Grok_WorldGenesis_Subagents_v1.0/workflow/MULTI_SESSION_OPERATING_PROCEDURE.md`

These child reads repair OPS-001 synthesis evidence but do not replace the
future parent-only preload required by OPS-002.

## Authorized patches

1. `.grok/agents/aidle-worldgen-qa-evidence.md`
   - keep `authority_token: VERIFY_ONLY`;
   - replace `inspector` with `purple-team-finding-triage`.
2. `.grok/agents/aidle-worldgen-tracker-steward.md`
   - keep `authority_token: PATCH_DRAFT`;
   - replace `memory-curator` with `blue-team-test-writer`.
3. `orchestration/registries/grok_specialist_profiles_v1.json`
   - update the same two bindings and mapping policy;
   - preserve all 21 source hashes, names, scopes and routing matrices.

Write new evidence only:

4. `orchestration/receipts/OPS-001-CORRECTION-001.json`
5. `orchestration/logs/ops-grok-specialist-profile-correction-001.log`

No other profile, original receipt, product, test, evidence, Scene, Character,
Control or source-package file may change.

## Acceptance

- All 21 profile authority tokens exactly equal the authority of their bound
  TrustLayer character in `E:/agents/characters/registry.yaml`.
- All 21 UI character IDs exist in the UI registry.
- All source hashes remain exact.
- The four required full reads have transcript-backed coverage.
- No specialist or grandchild spawned; no new top-level session.
- New receipt is MAF-valid, `accepted=false`, `self_accept=false`,
  `product_writes=[]` and reports exact files written.

Return `REVIEW_REQUESTED / WAITING_CODEX`. Do not start OPS-002 automatically;
Codex must validate this correction first.

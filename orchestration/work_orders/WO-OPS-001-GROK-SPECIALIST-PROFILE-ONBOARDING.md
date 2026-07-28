# WO-OPS-001 — Grok specialist profile onboarding

Directive: 41  
Task: OPS-001  
State: IN_PROGRESS  
Parent: existing Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852` only

## Objective

Register the user-provided Character and World Genesis specialist packs as
Grok child profiles without creating another top-level session and without
starting Character, Scene or Control implementation.

Source packages:

1. `game_character/AIdle_Grok_Character_Subagents_v1.0`
2. `Scene/AIdle_Grok_WorldGenesis_Subagents_v1.0`

The existing Desktop parent remains the sole conductor. The two source
orchestrator documents are routing guidance for that parent; they are not new
top-level sessions and must never spawn grandchildren.

Human Product Lead requires both routing packs to be loaded into the parent
itself. Because the OPS-001 schema child was already running when this
requirement arrived, OPS-001 may finish registry creation, but no specialist
may be spawned until dependent task OPS-002 proves parent-side full reads of
both orchestrator files. Child-side reads do not satisfy OPS-002.

## Required execution

The parent is coordinator-only. Spawn exactly one fresh real installed
`schema` child with `PATCH_DRAFT` authority for registry onboarding. No support
profiles and no grandchildren.

The child must read fully:

- both package README, manifest, orchestrator and workflow/governance files;
- all 8 Character agent source files;
- all 13 World Genesis agent source files;
- current `.grok/agents/*.md`, `orchestration/skills_manifest.yaml`, both
  character registries, MAF Compliance and Architecture Lock.

## Profiles to register

Create exactly 21 uniquely named profiles under `.grok/agents/`:

### Character — 8

- `aidle-character-architect.md`
- `aidle-character-style-guardian.md`
- `aidle-character-visual-silhouette.md`
- `aidle-character-gameplay-narrative.md`
- `aidle-character-rig-animation.md`
- `aidle-character-prompt-factory.md`
- `aidle-character-red-originality.md`
- `aidle-character-purple-acceptance.md`

### World Genesis — 13

- `aidle-worldgen-ssot-sequence.md`
- `aidle-worldgen-concept-gameplay.md`
- `aidle-worldgen-ux-camera.md`
- `aidle-worldgen-control-input.md`
- `aidle-worldgen-character-foundry.md`
- `aidle-worldgen-godot-runtime.md`
- `aidle-worldgen-world-commit.md`
- `aidle-worldgen-asset-art.md`
- `aidle-worldgen-ai-gateway.md`
- `aidle-worldgen-qa-evidence.md`
- `aidle-worldgen-tracker-steward.md`
- `aidle-worldgen-red-scope.md`
- `aidle-worldgen-purple-acceptance.md`

Do not register either package orchestrator as another parent profile. Instead,
record their paths as parent routing packs in the specialist registry.

## Profile contract

Each installed profile must include valid Grok frontmatter and:

- unique `name` and bounded description;
- canonical TrustLayer authority token;
- exact source agent path and source-local writer scope;
- one TrustLayer character and one UI character from the canonical registries;
- all five mandatory skills from `skills_manifest.yaml` plus only relevant
  routed skills;
- parent-only spawn rule, no grandchildren and no self-accept;
- explicit one-writer/file-lease rule;
- AIdle invariants: 2.5D first, text-only Companion, proposal → validation →
  preview → confirmation → World Commit, no arbitrary AI code;
- no credential, live provider, install, push, deploy or publish authority.

Normalize package-local authorities to canonical tokens:

- Character workers 01–06: `PATCH_DRAFT` within their source-local document
  scope only.
- Character Red 07: `READ_ONLY_AUDIT`, findings only.
- Character Purple 08: `VERIFY_ONLY`, never patch.
- World Genesis 01, 10 and 13: `VERIFY_ONLY`.
- World Genesis 02–09 and 11: `PATCH_DRAFT` within their writer set only.
- World Genesis 12: `READ_ONLY_AUDIT`, findings only.

The onboarding child must not broaden these scopes.

## Write lease

The schema child may write only:

1. the 21 new `.grok/agents/aidle-character-*.md` and
   `.grok/agents/aidle-worldgen-*.md` profiles listed above;
2. `orchestration/registries/grok_specialist_profiles_v1.json`;
3. `orchestration/receipts/OPS-001.json`;
4. `orchestration/logs/ops-grok-specialist-profile-onboarding-001.log`.

The parent may update only `orchestration/control/grok_status.json` after the
child completes. No existing profile overwrite, no product/test/contract,
Scene tracker, Character Foundry content, screenshot or primary evidence edit.
No temporary/helper file.

## Acceptance

- Exactly 21 new profile files and zero overwritten existing profiles.
- Registry lists source SHA-256, canonical authority, TrustLayer/UI bindings,
  skills and allowed writer set for each profile.
- All source files exist; all profile names are unique.
- Red/Purple authority is fail-closed; workers cannot accept their output.
- Parent routing packs point to the two supplied orchestrator documents.
- A dry-run routing matrix demonstrates which profiles would be used for Cozy
  Character 1C and Cozy Control/Scene work, but spawns none of them.
- Receipt validates against the MAF step-contract schema with
  `self_accept=false`, `accepted=false` and `product_writes=[]`.

After completion, return `REVIEW_REQUESTED / WAITING_CODEX`. Do not start the
21 specialists yet. Codex will inspect every installed profile before release.
The next permitted route is OPS-002 parent routing preload, not Character or
Scene implementation.

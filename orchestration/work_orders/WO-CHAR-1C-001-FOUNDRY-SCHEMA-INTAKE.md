# WO-CHAR-1C-001 — Character Foundry schema and provenance intake

Status: `AUTHORIZED_BY_DIRECTIVE_64`  
Task: `CHAR-1C-001`  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852`  
Machine acceptor: Codex  
Human Product Lead: final product/visual acceptor

## Outcome

Convert the existing Character Foundry Markdown vocabulary into a strict,
versioned machine intake contract and prove that all 28 source character records
can be represented without modifying the source pack. This is a contract and
provenance gate only. It does not create meshes, animations, Godot NPCs,
behaviour runtime, Scene 2 content or World Commit authority.

## Locked inputs

- `game_character/AIdle_Character_Foundry_MD/manifest.json`
  - version `1.0`
  - 28 characters, 7 world profiles
  - SHA-256 `bdba6b53174e1d6671f28302b4ae67275ad22bf3c2e978603791acd19e6cc4ba`
- `game_character/AIdle_Character_Foundry_MD/00_README.md`
- `game_character/AIdle_Character_Foundry_MD/01_CHARACTER_SCHEMA.md`
- `game_character/AIdle_Character_Foundry_MD/03_CHARACTER_INDEX.md`
- every source path listed by the manifest
- `game_character/CHARACTER_FOUNDRY_INTEGRATION_PLAN.md`
- `game_character/AIdle_Grok_Character_Subagents_v1.0/01_GROK_ORCHESTRATOR.md`
- `game_character/AIdle_Grok_Character_Subagents_v1.0/workflow/CHARACTER_DEVELOPMENT_WORKFLOW.md`
- `orchestration/ARCHITECTURE_LOCK.md`
- existing AGM Snapshot/Decision, confirmation, executor and World Commit contracts

The Markdown pack is immutable design input. Record source hashes before and
after the wave and require zero source diff.

## Mandatory invariants

1. Game characters are never TrustLayer/UI workers and receive no project-tool authority.
2. No Foundry character can directly mutate canonical world, inventory, ownership or economy state.
3. Any durable action remains proposal -> validation -> preview -> explicit confirm -> World Commit.
4. Ability requires a non-empty meaningful limitation and explicit allowlist/denylist.
5. Stable `character_id`, source path, world profile, source version and provenance are required.
6. Unknown fields, duplicate IDs, unknown worlds/classes, missing limitation, empty denylist, direct-commit authority, stale source hash and malformed records fail closed.
7. Nori-7 and the other Cozy cast do not replace, merge with or rename AIda. That decision remains Human/architecture-gated.
8. Text-only Companion remains the MVP boundary. No voice, provider call, generated code or external asset generation.

## Required skills and binding evidence

Every child fully loads the five `orchestration/skills_manifest.yaml` always
skills: `maf-mandatory-standard`, `trustlayer-x16-crew`,
`agentwork-knowledge-loop`, `project-room-collab`, `curiosity-engine`.
Add routed skills exactly where listed below. Receipts must name exact source,
mode, full-read ranges/EOF evidence, TrustLayer character, UI character,
authority token, input context hash, trace, handoff, durable child metadata,
commands and exit codes. No false full-read claim is acceptable.

## Sequential dispatch and writer leases

The existing Grok Desktop parent is coordinator-only. Run exactly four real
installed children sequentially. No support profiles, no grandchildren, no
parent patch, and no child may write another child's files.

### W0 — `aidle-character-architect` — `VERIFY_ONLY`

Binding: `blue-team-p0-remediator` + `ui-brief-writer`. Add
`architecture-lock`. Audit the source schema/index, all manifest paths, and the
four Cozy records. Produce an intake mapping and ambiguity list; do not patch
source or contract.

Exclusive writes:

- `orchestration/logs/char-1c-001-w0-architect-intake-001.log`
- `orchestration/receipts/character_1c/CHAR_1C_001_w0_architect_intake_001.json`

### W1 — `schema` / `aidle-schema` — `PATCH_DRAFT`

Binding: `devil-advocate` + `ui-brief-writer`. Add
`architecture-lock` and `securing-agentic-ai-tool-invocation`. Sole contract
writer. Implement only:

- `orchestration/contracts/character_foundry_1c/character_spec.schema.json`
- `orchestration/contracts/character_foundry_1c/source_manifest.lock.json`
- `orchestration/contracts/character_foundry_1c/intake_report.json`
- `orchestration/contracts/character_foundry_1c/validate_character_foundry_1c.py`
- `orchestration/contracts/character_foundry_1c/fixtures/valid/**`
- `orchestration/contracts/character_foundry_1c/fixtures/invalid/**`
- `orchestration/logs/char-1c-001-w1-schema-001.log`
- `orchestration/receipts/character_1c/CHAR_1C_001_w1_schema_001.json`

Requirements:

- Draft 2020-12, `additionalProperties:false`, anchored formats/enums.
- Deterministically normalize and validate exactly 28 source records and seven worlds.
- Preserve source strings and provenance; normalization must be reproducible.
- At least 12 adversarial invalid fixtures covering the mandatory fail-closed cases.
- Validator reports exact valid count, invalid rejection count and source hash identity.
- No dependency install; use Python standard library and already-present libraries only.

### W2 — `aidle-character-red-originality` — `READ_ONLY_AUDIT`

Binding: `red-team-source-auditor` + `ui-visual-critic`. Add
`adversarial-review`. Findings only. Audit source fidelity, duplicate/stable IDs,
authority leakage, weak ability/limitation pairs, missing deny rules, AIda identity
collision, false 28/7 counts, and schema bypasses. Do not patch.

Exclusive writes:

- `orchestration/logs/char-1c-001-w2-red-001.log`
- `orchestration/receipts/character_1c/CHAR_1C_001_w2_red_001.json`

### W3 — `aidle-character-purple-acceptance` — `VERIFY_ONLY`

Binding: `purple-team-release-gate` + `ui-visual-critic`. Add
`evidence-memory-ledger` and `adversarial-review`. Independently rerun the
validator, validate every step receipt against
`E:/standards/maf/schemas/agent_step_contract.schema.json`, recompute locked
hashes, check exact writer leases and verify all P0/P1 findings are closed.
Purple never patches and never accepts.

Exclusive writes:

- `orchestration/logs/char-1c-001-w3-purple-001.log`
- `orchestration/receipts/character_1c/CHAR_1C_001_w3_purple_001.json`

## Required receipt state

All receipts use the MAF agent step contract, `accepted=false`,
`self_accept=false`, truthful `product_writes`, exact files read/written,
literal commands and exit codes, and durable transcript lineage. The parent
returns `REVIEW_REQUESTED` / `WAITING_CODEX`; it does not update task acceptance.

## Forbidden scope

- Source Foundry edits, Godot runtime/scene/player/UI patch, Blender work, image generation or asset promotion.
- Character visual/rig/animation/behavior implementation, Prompt Factory, Scene 2, Block-DNA, P2E, v1.2 or Tier 3 work.
- AIda replacement/merge, direct commit tool, live provider, credential, public network or Red F01 bypass.
- Dependency install, Godot version change, push, deploy, publish, fabricated refs, helper/temp files outside explicit leases.

## Completion

Return `REVIEW_REQUESTED` and `WAITING_CODEX`, list four real child refs in
sequence, all receipts/logs, source-before/after hashes, validator counts,
`parent_product_patch=false`, `accepted=false`, `self_accept=false`, and the
remaining risks. Character visual slice remains blocked pending Codex acceptance.


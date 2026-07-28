# Codex -> Claude Handoff: Character Build System Backbone 001

## Purpose

Human Product Lead directs that `orchestration/control/GROK_CHARACTER_BUILD_SYSTEM_001.md` become the controlled backbone for character production, beginning with Nori-7 (`CCP-RH-001`). Claude is asked to take over **advisory coordination, evidence synthesis, and work-order drafting** for this program. Claude is not the final machine acceptor and must not dispatch Grok, patch `game/**`, alter a directive, or promote/quarantine assets without a current Codex directive and a Human decision where required.

## Canonical current state (verify again before acting)

- Sole Grok Desktop parent: `019f7ffd-3995-71c0-aca1-51078e24a852`; coordinator-only. Never create a second parent/session or use Grok CLI.
- Highest directive at handoff: **94**, opening only C4R strict QA under `VERIFY_ONLY`. Its child `019f8d83-3012-7d13-8e97-4c50c6114982` was running when this handoff was written. Do not interrupt it or add a competing dispatch.
- UCBV remains `accepted=false`; C5, P2E-002, network, shipping, push/deploy/publish remain blocked. Red F01 remains a hard stop.
- Nori-7 runtime evidence from a fresh normal-runtime log says `character_id=CCP-RH-001`, `bones=14`, `slice=c1r_glb_skinned`, `mode=glb_c1r`, `procedural=false`. This is evidence of a GLB runtime path, not proof that every motion primitive has real authored keys.
- Motion kit is staging input only: `orchestration/control/motion_kit/`. Its validator was independently rerun green: schema valid, 172/172 coverage, no duplicate/phantom binding, all 35 signature clips `must_author`.

## Backbone source of truth

Read in this order and treat the following as read-only reference until a directive grants a phase-specific lease:

1. `orchestration/control/GROK_CHARACTER_BUILD_SYSTEM_001.md`
2. `orchestration/control/character_build/{assemble_nori7.py,character_assembly_nori7_001.json,ASSESSMENT_NORI7_ASSEMBLY_001.md}`
3. `orchestration/control/motion_kit/{README_BUILD_GUIDE.md,motion_primitives.json,motion_primitives.schema.json,validate_motion_primitives.py}`
4. DNA package contracts named in the SOP: world-profile bindings, module/skeleton/animation/material/behavior/socket catalogs, build recipe schema, Blender operation map, and Nori-7 recipe.
5. Current `codex_directive.json`, UCBV reviews/work orders/receipts, `AGENTS.md`, MAF compliance, character/UI registries, Blueprint v1.1, and `ARCHITECTURE_LOCK.md`.

## Non-negotiable architecture

- World profile is the primary selection axis; recipe -> validator -> motion plan -> Blender quarantine artifact -> explicit Godot override -> headed runtime evidence -> Purple/Codex/Human gates.
- A name-only DNA animation binding is not animation. Every signature/must-author clip requires real keyed content; missing content is `ASSET_REQUEST_REQUIRED`, never a substitute pose or metadata claim.
- Blender output stays quarantined. `write_approved_catalog` remains forbidden. No promotion to `game/**` or an approved catalog without a separate signed Codex/Human gate.
- Godot runtime wiring requires a separate, narrow override and exact `game/**` writer lease. Behavior blocks are `CONFIGURE_ONLY`; no AI canonical-state mutation authority.
- One writer per file; every material child action has real durable UUID lineage and schema-valid MAF receipt with `accepted=false` and `self_accept=false`.
- Codex is final machine acceptor. Human Product Lead owns product acceptance. Claude and Purple may never self-accept.

## Claude's immediate assignment (advisory only)

1. Maintain a phase ledger for Nori-7 Phases 0-6: observed fact, evidence path/hash, unknown, required gate, and allowed next owner.
2. Independently inspect the full SOP against the real DNA contracts, specifically checking whether `character_assembly_nori7_001.json` is a recipe/plan versus a runtime artifact, whether the recipe schema has all required fields, and whether the real GLB/manifest has actual keyframe evidence.
3. Draft—do not execute—the next phase-specific work order only after the current UCBV C4R/C5 path closes. The draft must be split by writer lease: recipe assembly, read-only validation, motion planning, Blender quarantine build, Godot integration, then evidence/acceptance. Do not collapse them into one wide job.
4. Produce a concise discrepancy ledger for: palette conflict (`#F7E9C6` vs `#fdf3e2`), skeleton-stub versus 14-bone runtime proof, zero-keyframe/real-keyframe proof, Godot 4.3 adapter `VERIFY(...)` lines, and live 4-stage versus package 5-stage disagreement.
5. If any input is missing or contradictory, route `NEED_CODEX`/`NEED_HUMAN`; do not infer a waiver.

## Required future Grok directive shape (draft, not dispatch)

The first character-backbone directive after UCBV is machine/Human-gated must authorize **one phase only**. Recommended opening order:

1. `NORI7-P0/P1` Blue recipe revalidation and motion-plan artifact under orchestration-only lease.
2. Red `NORI7-P2` verifier under findings-only lease.
3. `NORI7-P4` Blender quarantine asset build only after Codex accepts P0/P2 and explicit authoring scope is resolved.
4. `NORI7-P5` Godot integration only under a new explicit Godot override with named `game/**` files.
5. `NORI7-P6` headed runtime proof, Purple verification, Codex machine acceptance, then Human product acceptance.

Never start a later phase because a prior document says "ready". A current directive, exact writer lease, and predecessor evidence are mandatory.

## Handoff completion contract

Claude returns a read-only evidence-backed phase ledger and proposed narrow work-order draft to Codex. It must state `accepted=false`, must name all unknowns, must cite actual files/commands, and must not claim that the character is complete merely because assembly joins or the motion-kit validator pass.

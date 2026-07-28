# Grok Object DNA & AI Build Card System — kickoff prompt 001

Paste the block below into Grok Desktop session `019f8e3c-e53b-74e0-a878-df6b8398338e`
(the Design parent). Authored by Claude conductor from the Human's source document
`E:\AIdle_openworld\Animation_sculb\AIdle Object DNA & AI Build Card System.docx`,
following `STANDARD_GROK_WORK_ORDER_PROMPT_TEMPLATE_001.md`.

**Before you paste this:** this WO deliberately makes the design session reconcile
your new document against an existing, more advanced staged system (`DNA Platform
vNext`, authored by Codex, currently queued/not-authorized in the vision lock) before
building anything — so effort isn't spent on two competing schemas for the same
problem. See "Why this two-step shape" at the bottom if you want the reasoning.

---

```
WO-OBJECT-DNA-CARD-SYSTEM-001 — reconcile + formalize the Object DNA / skeleton /
animation / mockup-card framework (directive 99, design-parent scope)

1. Read (in full, before planning anything):
   - orchestration/control/object_dna_card_system/AIDLE_OBJECT_DNA_AI_BUILD_CARD_SYSTEM_SOURCE_001.md
     (faithful transcription of the Human's source docx — the new spec you are
     implementing: Object DNA layers L0-L7, 7 skeleton-family categories, semantic
     node-ID convention, 5-level mockup card UX, Build Recipe schema, 12-agent
     role split, 11-phase roadmap P0-P10, Definition of Done)
   - orchestration/control/dna_platform_vnext/README.md
   - orchestration/control/dna_platform_vnext/DNA_PLATFORM_VNEXT_ARCHITECTURE_001.md
   - orchestration/control/dna_platform_vnext/SOURCE_REGISTRY.json
   - orchestration/control/dna_platform_vnext/schemas/ (all files)
   - orchestration/control/dna_platform_vnext/prompts/ (all files)
   (why: vNext already covers a lot of the same ground -- typed DNA entries,
   GenerationRequest, UniversalEntityRecipe IR, a semantic compiler, artifact/
   runtime gates -- authored by Codex, Gate V0 done (contracts + validator +
   examples exist), status STAGING, and explicitly QUEUED / NOT AUTHORIZED FOR
   EXECUTION per AIDLE_GAME_VISION_LOCK_001.md §13. You must not build a second,
   competing schema for the same problem.)
   - game/assets/ucbv_001/character/nori7/ (the real, already-built Nori-7 asset:
     rigged.glb, mesh descriptor, animation adapter, mockup parity receipt) --
     this is your one existing real-world proof case, do not rebuild it.
   - AIDLE_GAME_VISION_LOCK_001.md (already required standing reading; note §13
     living pointer on DNA Platform vNext status, and the new §12 "AI design-
     build parity guarantee" bullet -- it applies directly to this WO)

2. TASK 1 -- Reconciliation memo (do this first, do not skip to building):
   Write orchestration/control/object_dna_card_system/RECONCILIATION_001.md
   comparing the new Object DNA / Card System document against DNA Platform
   vNext. Be concrete and honest, not diplomatic-vague:
   - Where do they describe the same thing with different names? (e.g. the new
     doc's "Character Build Recipe" vs vNext's "UniversalEntityRecipe" -- are
     they the same shape, compatible, or actually different?)
   - What does the new doc specify that vNext does NOT yet have in written form?
     (candidates: the concrete 7-category skeleton-family taxonomy with named
     IDs and per-family animation clip lists; the semantic-ID-not-ABC node
     marker convention; the 5-level mockup card UX -- Object Family / Skeleton
     Selection / Visual Style / Animation Package / Build Confirmation --
     which maps to vNext's still-undesigned "V5 Player creation UX" gate; the
     non-character object cards for doors/water-wheels/trees)
   - What does vNext have that the new doc does not? (typed compiler IR,
     lifecycle/provenance states, content-addressed source registry, the
     4-state compiler output PROPOSAL_READY/ASSET_REQUEST_REQUIRED/REJECTED/
     HITL_REQUIRED, the quarantine+promotion gate)
   - Recommendation: how should these merge? Default expectation (confirm or
     argue against with evidence): the new doc's skeleton taxonomy and card UX
     become concrete content that fills out vNext's L1 typed entries and its
     not-yet-designed V5 UX gate -- not a parallel system.
   accepted=false, self_accept=false. This is a design memo, not a decision --
   Claude reviews it before Task 2 proceeds.

3. TASK 2 -- Schema/registry formalization (only after Task 1 is filed):
   Extend/reuse vNext's existing schemas where the reconciliation memo found
   them equivalent -- do not fork a parallel schema for something vNext
   already types. Where the new doc specifies something genuinely absent from
   vNext, add it as new schema/registry content:
   - Semantic node-ID convention as a written contract (marker-for-display vs
     semantic_id-for-data, matching the new doc's §4 example).
   - The 7 skeleton-family category definitions as registry entries (humanoid,
     quadruped, bird/flying, fish/aquatic, robot/mechanism, plant, vehicle) --
     named IDs, required animation clip lists, per the new doc §5.
   - A first draft schema for the 5-level mockup card system (§9-13 of the new
     doc) as content for vNext's V5 gate.
   Name every file you write. Additive only -- do not edit vNext's existing
   schema files in place; add new files or a clearly-marked extension.

4. TASK 3 -- Nori-7 as the one real validation case:
   Nori-7 already exists as a real rigged/animated GLB (game/assets/ucbv_001/
   character/nori7/). Do NOT rebuild its mesh, rig, or animations. Instead,
   write a registry entry describing Nori-7 under the new robot_biped_small_v1
   skeleton-family definition from Task 2, and HONESTLY report where the real
   asset currently falls short of the new schema's full requirements (e.g. if
   its bone count/contact-marker set/animation library doesn't fully match
   what the new taxonomy specifies for that family) -- a gap report, not a
   claim of compliance it hasn't earned. This is the schema's first sanity
   check against something real.

5. HONESTY rule: every claim about what already exists (vNext coverage, Nori-7
   asset state, animation clip counts) must cite the real file/field you read
   it from, not a summary of memory. If you assert vNext already covers X,
   name the exact schema/file. Do not fabricate skeleton bone counts or clip
   counts for Nori-7 -- read them from the real files.

6. OUT OF SCOPE for this WO (design-parent, no game/** patches):
   - No Blender production for any new skeleton family.
   - No Godot runtime/AnimationTree wiring.
   - No execution of DNA Platform vNext's later gates (V1-V6) -- those need a
     separate Human-authorized directive per the vision lock's living pointer.
   - No touching the real Nori-7 asset files.
   If Task 1's reconciliation finds this WO's scope should expand into any of
   the above, STOP and route back to Claude/Human rather than proceeding.

7. Escalate (do not proceed) if: the reconciliation finds the two systems are
   fundamentally incompatible in a way that can't be resolved by extension: or
   any task would require a game/** patch, Blender execution, or touching
   vNext's V1-V6 gates without a fresh authorization.

8. Acknowledge with: confirmation of every file read in step 1, the live
   directive_id, and a one-paragraph plain-language summary of the
   reconciliation finding (Task 1) BEFORE starting Task 2. Purple stays
   WAITING throughout; accepted=false, self_accept=false on everything.
```

---

## Why this two-step shape

The Human's new document is a genuinely good, concrete design (skeleton
taxonomy, card UX, semantic-ID convention are all things vNext hadn't written
down yet). But this project already paid for one instance of two parallel,
half-overlapping systems being built without reconciliation (the original
`town_layout_10phase.json` vs the town-grid-import cadastre, noted in the
vision lock as "supersede, do not silently duplicate"). `DNA Platform vNext`
exists, is already reviewed (`orchestration/control/dna_platform_vnext/`,
task history entry — Claude independently verified it 2026-07-23), and is
explicitly parked pending a dedicated authorization. Handing the design
session a second, independent character/skeleton system to build from
scratch risks the same duplication. Reconcile first, then build the union —
same effort from Grok, no wasted rework, no two truths about what a
`skeleton_family` is.

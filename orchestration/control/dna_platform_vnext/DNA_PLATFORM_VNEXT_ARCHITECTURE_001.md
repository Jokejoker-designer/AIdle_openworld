# DNA Platform vNext — compiler architecture 001

Status: `STAGING` · Owner: Human Product Lead · Machine author: Codex  
Compatibility target: AIdle Blueprint v1.1 and Architecture Lock

## 1. Product decision

AIdle should not promise infinity by letting an AI emit arbitrary scripts,
meshes or scene mutations. It should provide a small, stable language that can
compose registered DNA indefinitely and can grow that DNA through a quarantined,
reviewed authoring loop.

The platform therefore has two kinds of creativity:

1. **Compositional creativity** — unlimited recipes from known typed parts,
   parameters, sockets, materials, motions, behaviors and world rules.
2. **Extensional creativity** — when no safe part can express the idea, the AI
   emits an `AssetRequest`; an offline worker authors it, QA verifies it, and a
   separate promotion gate may add a new versioned catalog entry.

No prompt can silently turn the second kind into the first.

## 2. Evidence from the current source

Verified on 2026-07-23 from the files locked in `SOURCE_REGISTRY.json`:

- The foundation contains 170 modules, 40 socket types, 15 skeleton families,
  21 animation sets / 172 clip names, 8 material themes, 46 behaviors and 38
  generators.
- Every module is `DESIGN_READY`; no module record contains an artifact URI,
  artifact hash, license record or runtime QA state.
- Every skeleton family declares only `root`, `body`, `head` as required bones,
  even though target bone counts range above those three.
- All 172 animation records contain only `clip_id`, `loop`, `events`; they do
  not prove duration, tracks, keyframes or a GLB action.
- The original schemas type many arrays only as `array` and accept shallow
  objects. The later `BLOCK-DNA-ADAPT-001` gate correctly closes socket,
  occupancy, revision, fingerprint, allowlist and authority defects.
- The current package prompts are one-paragraph role descriptions. They do not
  share a machine output contract, evidence vocabulary or explicit stop states.
- Current validators are green: Tier3 package, strict Block-DNA 14 positive /
  42 adversarial fixtures, and motion-kit 172/172 coverage. Those gates should
  be reused, not replaced.

Conclusion: the grammar is valuable, but the missing platform layer is a typed
compiler IR plus lifecycle/provenance and prompt contracts.

## 3. Non-negotiable invariants

1. AI proposes; only World Commit mutates canonical state.
2. Unknown IDs, missing artifacts, unknown fields and stale hashes fail closed.
3. Runtime accepts registered artifacts, never arbitrary AI-generated code.
4. Preview has no ownership, economy, collision or durable-state authority.
5. Every request is idempotent and revision-aware at the strict compiler target.
6. Catalog promotion is separate from artifact generation.
7. `DESIGN_ONLY` is never presented as `RUNTIME_VERIFIED`.
8. A validator reports findings and never repairs its own input.
9. Red finds, Blue patches an approved lease, Purple verifies, Codex machine
   accepts, Human accepts product quality.
10. A world profile is chosen before modules, materials, rigs or rules.

## 4. Seven platform layers

### L0 — Content-addressed source registry

Exact path, version and SHA-256 for every catalog and downstream contract.
This makes “which DNA did the AI read?” answerable and replayable.

### L1 — Typed DNA entries

Every module, socket, skeleton, animation set, behavior, generator, physics
profile and motion primitive eventually conforms to
`schemas/dna_catalog_entry.schema.json`. The entry separates:

- semantic identity and compatibility;
- capabilities and typed ports;
- artifact evidence and lifecycle status;
- provenance/license;
- configure-only authority.

### L2 — Generation intent

`GenerationRequest` normalizes player language into entity kind, gameplay goal,
world profile, bounds, budgets, must-have/avoid rules and consent. It contains
no build commands.

### L3 — Universal Entity Recipe IR

`UniversalEntityRecipe` is the common intermediate representation for
characters, creatures, props, vehicles, buildings, terrain, plants, effects,
systems and regions. Facets are optional but typed:

- composition and sockets;
- presentation/materials;
- rig, animation and motion primitives;
- behavior and interactions;
- elemental physics/ecology;
- VFX/audio;
- readiness, blockers and asset requests.

### L4 — Deterministic semantic compiler

The compiler resolves exact catalog IDs and checks cross-file facts that JSON
Schema cannot:

- module and connection references;
- declared sockets and mutual compatibility;
- world-profile/skeleton/animation compatibility;
- behavior authority;
- source hashes and lifecycle status;
- motion payload honesty;
- budget and capability satisfaction.

It then emits one of four states:

- `PROPOSAL_READY`
- `ASSET_REQUEST_REQUIRED`
- `REJECTED`
- `HITL_REQUIRED`

### L5 — Existing execution targets

The IR compiles into the already accepted boundaries:

- strict Build Recipe for an entity/cluster;
- strict Build Graph for placement and systems;
- Tier3 physics extension where applicable;
- Structured World Prompt proposal for preview/confirmation.

This layer never creates a parallel commit path.

### L6 — Artifact and runtime gates

Missing geometry/rig/motion becomes a quarantined Blender job using allowlisted
operations. A separate intake gate verifies artifacts, Godot import, behavior,
collision, navigation and evidence. Only an approved catalog-promotion work
order can change lifecycle status.

## 5. Why one universal recipe is better than one giant catalog

A giant catalog still leaves each AI guessing how fields relate. The IR makes
relationships explicit and keeps entity kinds as constrained profiles over the
same facets. A door and a character differ in required facets, not in authority
or provenance rules.

Examples:

- Door: composition + material + interaction + optional mechanism rig.
- Nori-7: composition + rig/motion + behavior + material + physics.
- Vehicle: composition + mechanism rig + locomotion + seats + physics.
- Plant: geometry + growth rig + biological state + reactions.
- Region: nested graphs + generators + rules + budgets.

## 6. Infinite expansion without losing safety

When an idea cannot compile:

1. Return the exact missing capability, not a fabricated module ID.
2. Produce a typed Asset Request with acceptance tests and compatible ports.
3. Author in quarantine; record tool operations and hashes.
4. Verify mesh/rig/motion/material/collision/runtime evidence.
5. Promote a new semantic version through a separate signed gate.
6. Re-run the original request against the updated source registry.

The player experiences growth; the engine retains deterministic trust.

## 7. Implementation gates

This staging kit is Gate V0 only: contracts, prompt constitution, examples and
semantic validator. It does not authorize product work.

Recommended subsequent gates:

- **V1 Catalog migration:** generate typed entries from source, preserve IDs,
  mark legacy assets `DESIGN_ONLY`, attach hashes and licenses.
- **V2 Compiler:** implement deterministic IR -> strict Recipe/Graph adapters.
- **V3 Asset request/promotion:** quarantine manifests and signed promotion.
- **V4 Runtime intake:** exact Godot files under a scoped override.
- **V5 Player creation UX:** prompt -> proposal -> preview -> confirm -> commit.
- **V6 Adversarial/visual gate:** Red, QA, Purple, Codex, Human.

UCBV-001 and Red F01 remain independent hard gates. No vNext document relaxes
them.


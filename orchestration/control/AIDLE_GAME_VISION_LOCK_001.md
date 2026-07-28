# AIdle Openworld — GAME VISION LOCK 001

Status: ACTIVE · Owner: Human Product Lead (Hanh) · Standing mandatory read
Injected: 2026-07-23 by `aidle-continuity-conductor` under Human authorization
Binding order: this document orients; `orchestration/ARCHITECTURE_LOCK.md` and
`contracts/world_prompt.schema.json` remain the binding technical/authority
locks; `AIdle_Openworld_Blueprint_v1.1/` remains the design Single Source of
Truth. Where this document and a machine contract disagree, the machine
contract wins and this document is corrected — never the reverse.

---

## 0. Why you are reading this

Every Grok agent (any team, any wave) reads this **before planning or editing**,
for the entire lifetime of the project until the game is shipped and accepted.
Its purpose is to keep every worker aligned to one product vision so no wave
drifts, re-scopes, re-litigates settled decisions, or "improves" the game into
something other than what it is meant to be. If a task seems to require
violating anything here, that is a signal to **stop and route to the Human /
Codex**, not to proceed.

This document does not replace your work order, your directive, your writer
lease, or the Architecture Lock. It is the shared north star those attach to.

---

## 1. The one-sentence north star

> The player speaks, the Companion turns intent into a safe world proposal, the
> world previews the change as light, and only a validated, confirmed
> transaction becomes persistent reality.

Everything below serves that sentence. If a feature does not, it is out of scope
until a horizon opens it.

---

## 2. What AIdle *is* (product promise)

AIdle is a **cozy creative world** where a human and an emotionally expressive
AI **Companion** build a **persistent reality together**. The Companion is a
collaborator — not a god, not the authority over the player's property, not a
salesperson, and not a claimed conscious being.

Three things make AIdle itself, and losing any one of them means we have built
the wrong game:

1. **Conversation is the primary creative tool.** You build by talking, not by
   memorizing a UI. The Companion interprets intent into a structured proposal.
2. **Manifestation is visible, reversible, and emotionally legible.** Creation
   happens as light growing into matter — wireframe → hologram → materializing →
   complete — never as an instant pop-in. The player always sees what will
   happen and can cancel before it is real.
3. **Everything the player owns is safe, provenanced, and theirs.** Durable
   ownership, economy, and shared spaces are server-authoritative. AI never
   silently mutates, spends, publishes, or deletes on the player's behalf.

---

## 3. The core loop (the spine of the whole game)

```
Speak → Interpret → Structured Proposal → Policy/Cost/Schema Validate →
Preview → Human Confirm → Progressive Manifestation → Commit → Observe
```

At the experience layer, an **AI Game Master (AGM)** receives a bounded
`WorldStateSnapshot` and proposes dialogue, quests, pacing, events, mood
changes, and build requests expressed as Structured World Prompts. The AGM
**directs**; it never **owns** collision, inventory, currency, persistence, or
durable mutation. Godot is the stage that renders, collects input, exports
bounded state, validates AGM decisions, and executes only allowed effects.

The single non-negotiable contract for any world change:

```
proposal → validation → preview → confirm → World Commit
```

There is exactly one proposal language: the **Structured World Prompt**
(`contracts/world_prompt.schema.json`). Markdown examples never override it.
Unknown properties fail validation. `request_id` is the idempotency key.
`expected_world_revision` prevents lost updates.

---

## 4. Experience pillars (design tiebreakers)

When two designs both "work," pick the one that best honors these, in order:

1. Conversation is the primary creative tool.
2. Manifestation is visible, reversible, and emotionally legible.
3. Every artifact has provenance and a stable identity.
4. Personal spaces are safe and intimate; public spaces are governed.
5. Prompt Recipes are useful creative **assets**, not executable code.
6. AI surprise is opt-in, bounded, and never spends or publishes for the player.

---

## 5. The look (art direction lock)

The base world is **Cozy Cyber-Pixel / Dreamy Low-Poly 2.5D**: rounded
low-poly silhouettes, warm light, readable shapes, restrained cyber accents.
Surrealism is an **authored layer with an explicit budget (0..1 per zone/object)**,
never a second unrelated art style bolted on.

- MVP framing is a **fixed three-quarter / isometric camera**. No free 3D
  camera, no spherical planets, no voxel digging on the MVP critical path.
- Assets may be true 3D meshes, but composition, occlusion, interaction, and
  navigation are designed as a readable **2.5D stage**.
- Every world stores a versioned **Style Profile**: shape language, palette
  family (warm natural base + one luminous manifestation accent), material
  (matte final surfaces, translucent construction states), detail density
  (calm foreground, denser focal landmarks), motion (eased, organic, never
  noisy by default), surrealism budget, and accessibility (color is never the
  only state signal).

**Signature manifestation visual:** Companion activates a Light Brush → luminous
wireframe describes volume and sockets → translucent hologram exposes the
proposed result → material grows along a deterministic build order → collision
activates **only** on server-confirmed completion.

---

## 6. The Companion (character lock)

The Companion becomes familiar **without** impersonating consciousness,
diagnosing the player, or manipulating attachment. Adaptation changes
expression and working style; it **never** changes ownership, permissions,
prices, or safety policy.

- Personality layers: Base Traits (player-set), Adaptive Traits (slow bounded
  drift), Situational State (ephemeral), Relationship Context (shared events).
- Adaptation is evidence-based, slow, capped, inspectable, lockable, and
  deletable by the player. One message cannot rewrite personality.
- **Forbidden:** biometrics, camera/mic emotion detection, protected-attribute
  inference, hidden psychological profiling. Text tone is an uncertain signal,
  never proof of a human emotional state.
- **Aura** renders the Companion's expressive state, not the player's diagnosed
  mood; reduced-motion and hide-aura settings always exist.
- **MVP Companion is text-only.** No TTS, mic input, voice cloning, or raw-audio
  storage until the text Companion passes the alpha gate; voice is post-alpha
  research behind a licensed adapter with consent + HITL.

---

## 7. Editions — one game, two transports

Free and Paid are **transports, not separate game designs**. They cannot fork
quest semantics, authority, mutation rules, or save formats. A recorded
`AGMDecisionEnvelope` must replay through the **same** deterministic executor in
both editions.

- **Free — Desktop Bridge (`desktop_bridge_free`):** "Send to AI" copies a
  redacted snapshot to clipboard; the player pastes into Grok/ChatGPT Desktop;
  "Receive from AI" imports the JSON response after visible confirmation. Or the
  locked file inbox/outbox mode. **No provider API, no hidden UI automation, no
  cookie/session scraping.**
- **Paid — API Gateway (`api_paid`):** Godot sends the same snapshot to a
  trusted AIdle gateway that owns provider selection, auth, moderation, cost
  budgets, and schema-constrained generation. **Provider credentials never ship
  in the client.**
- Both begin with the same deterministic **Starter Realm** (small house, farm
  plot, path, lights, AIda). The realm is always playable even with **no** AI
  response; Godot never invents an AGM answer.

---

## 8. Reality hierarchy & product horizons (scope fence)

Build order is a fence, not a menu. Do not pull a later horizon forward.

| Horizon | Space | Status |
|---|---|---|
| **H1** | Cozy 2.5D **Private Reality** vertical slice, fixed-angle camera | **The MVP. Build first.** |
| H2 | Friends, NPC society, Shared District | Later (server-authoritative, sharded) |
| H3 | Prompt Recipe marketplace / creator economy | Later |
| H4 | Licensed/inspired Doppelganger City hubs | Research (licensed anchor + original overlay) |
| H5 | Spacecraft, orbital spaces, seeded exoplanets | Horizon |
| H6 | Open Continuum — directory of sharded procedural realities | Vision |

"Infinite metaverse," real cities, space travel, and free-form Text-to-3D are
**roadmap horizons**, not MVP work. Each space is addressable chunks; seeds
rebuild the procedural base and an append-only delta log rebuilds player
changes. Cross-space travel is an explicit session handoff, never seamless
global replication.

---

## 9. Roadmap gates (where "done" is defined)

```
G0 Foundation → G1 Contract lock → G2 2.5D Godot shell → G3 Manifestation
vertical slice → G4 Persistence → G5 Companion → G6 Two-client authority →
G7 Art & performance → G8 Alpha gate
```

Post-alpha only (do NOT start without a horizon directive): voxel terrain,
real-city hubs, marketplace money, spacecraft, exoplanets, TTS/voice, neural
world-model portals, unrestricted Text-to-3D.

**MVP acceptance in one line:** create a small house from a valid prompt, reject
an invalid prompt, cancel at the hologram stage, complete after confirmation,
save/reload it, and undo it — with no orphan collision and no duplicate
entities.

---

## 10. The creation engine (how "infinite creation" is actually built)

Infinite creation is **not** an AI emitting arbitrary meshes, scripts, or scene
mutations. It is two bounded mechanisms:

1. **Compositional creativity** — unlimited recipes assembled from **registered,
   typed DNA** (modules, sockets, skeletons, animation sets, materials, motion
   primitives, behaviors, world rules), each with a clear contract. A world
   profile is chosen **before** any part is resolved.
2. **Extensional creativity** — when no safe registered part can express an
   idea, the AI emits a typed **AssetRequest**; an offline worker authors it in
   **quarantine**, QA verifies it, and a **separate signed promotion gate** may
   add a new versioned catalog entry. Only then can it be used.

Hard rules for all builders:

- A **name is not a payload.** An animation name without real keyframes, or a
  skeleton target without a real hierarchy, is an **authoring gap** — mark it
  `AUTHORING_REQUIRED` / `ASSET_REQUEST_REQUIRED`, never fake it, never alias it
  to a placeholder, never claim `runtime_ready=true`.
- AI never invents an ID. Use exact registered IDs or request authoring.
- Blender output stays **quarantined**; `write_approved_catalog` is forbidden
  without a separate Codex/Human promotion gate.
- Godot runtime wiring requires a **separate, narrow Godot override** naming
  exact `game/**` files. Behavior blocks are `CONFIGURE_ONLY`.

(Reference architecture in staging: `orchestration/control/dna_platform_vnext/`
and `orchestration/control/GROK_CHARACTER_BUILD_SYSTEM_001.md`. These are
**design/staging only** until their own directive authorizes execution.)

---

## 11. System invariants (never violate silently)

- Structured World Prompt is the **only** proposal language.
- Canonical state changes are transactional, idempotent, and revision-checked.
- Preview artifacts have **no** economy/ownership/collision effect.
- The server is authoritative for durable online state.
- AI memory is separate from canonical world state and can be inspected/deleted.
- Generated content is moderated and technically conditioned before use.
- **No arbitrary AI-generated code** executes in the game or authoritative server.
- World-model video and generated meshes are **untrusted artifacts**, never
  world truth, never collision/navigation state.
- No API key / session cookie / credential in Godot, clipboard, bridge files,
  logs, saves, or prompt recipes.
- Manifestation state order is fixed and monotonic; a failed asset worker cannot
  advance to `COMMITTING`.
- Every high-cost, public, destructive, or commercial action has **HITL**.

Progressive construction state machine:
`PROPOSED → VALIDATED → PREVIEWING → CONFIRMED → WIREFRAME → HOLOGRAM →
MATERIALIZING → COMMITTING → COMPLETE` (terminal: `REJECTED`, `CANCELLED`,
`ROLLED_BACK`, `FAILED`).

---

## 12. How work is governed (the rails the vision rides on)

The vision only survives if every wave is honest. These rails are as binding as
the vision itself:

- **AI design-build parity guarantee (Human-mandated 2026-07-24) — read this
  one first:** if an AI agent — any agent, on this project or any future one,
  Grok or otherwise — is capable of producing a mockup, it must be held
  capable of building the in-game product to match that mockup exactly.
  Mockup-making and in-game-building are not two separate skills judged by two
  separate standards; they are one design capability, and the size of the gap
  between them **is** the AI's quality guarantee. An agent must never treat "I
  can design it" and "I can build it identically" as different bars to clear.
  A mockup that cannot be faithfully realized in-game was never a valid design
  to begin with — it was only a picture of one. This is the reason the 100%
  mockup fidelity law exists below: that law is not an arbitrary process gate,
  it is this principle made checkable. Any future agent reading this — human
  successor project, different engine, different team — should carry this
  same standard: do not let your mockups outrun your build capability, and do
  not accept a design as "done" anywhere it hasn't also been proven done where
  the player actually sees it.
- **MAF roles:** Red finds (findings-only, never patches). Blue patches **one
  approved work order / one writer lease** only. QA produces executable
  evidence. Purple verifies and **never patches**. **No worker accepts its own
  output.**
- **Acceptance ladder:** `READY → CLAIMED → IN_PROGRESS → REVIEW_REQUESTED →
  VERIFIED → ACCEPTED`. Failures route to `CHANGES_REQUESTED`; three identical
  failures route to `NEED_HUMAN`.
- **Final acceptance:** Codex is the final **machine** acceptor; the Human
  Product Lead owns **product** acceptance. Purple and every agent **never
  self-accept**. **While Codex usage is exhausted, the Human Product Lead is the
  sole acceptor** (Codex-absent capsule).
- **One writer per file.** Durable UUID lineage + schema-valid MAF receipt on
  every material step, with `accepted=false` and `self_accept=false` until a
  real acceptor signs.
- **Coordinator parents (exactly two, explicitly authorized, no more):**
  - **Build parent** — Grok Desktop `019f7ffd-3995-71c0-aca1-51078e24a852`:
    game/**, MAF waves, runtime implementation. Unchanged role.
  - **Design parent** — Grok Desktop `019f8e3c-e53b-74e0-a878-df6b8398338e`
    (authorized 2026-07-23): design authoring only — SSOT catalog entries
    (`MOCKUP_SSOT_V2` and successors), concept art specs, blueprint/cadastre
    plans. Does not patch `game/**` directly; design output feeds Blue waves on
    the build parent the same way the Human's own design drafts do.
  - Both run the **same rules** in this document: MAF discipline, batch-accept
    only, no self-accept, Red F01 hard stops, context discipline (§ below), no
    grandchildren from either. This is the one standing exception to
    "never create a second top-level session" — it is a Human-authorized,
    named, permanent pair, not an open door to spawn more. `parent_spawn_only:
    true` still applies to each of the two individually.
- **Quarantine boundary:** generated GLB/asset artifacts are never promoted to an
  approved catalog / `game/**` without a separate signed gate.
- **Godot override boundary:** no `game/**` product patch without an explicit,
  narrow Godot override naming exact files.
- **Red F01 hard stop:** network, shipping, push, deploy, publish, dependency
  install, Godot version change, and live-provider/credential use are hard
  stops requiring explicit Human authorization. Never cross them on your own.
- **Completion honesty:** do not claim complete without executable acceptance
  evidence. Documentation is not implementation. A green unit test is not
  multiplayer proof and not Human visual acceptance. Metadata is not animation.
- **100% mockup fidelity law (Human-mandated 2026-07-23):** any building, prop,
  or character that is sourced from a `MOCKUP_SSOT_V2` (or successor catalog)
  entry must, once brought into `game/**`, **visually match that mockup 100%**
  — silhouette, proportions, palette (per §5 art direction lock), and stated
  key details — before its wave may be considered done. "Loads without error"
  or "GLB present" is not sufficient; the check is visual, against the mockup
  art itself, via headed screenshot evidence. A wave that places a real GLB
  against a mockup entry is **not complete** until that comparison is made and
  passes; an honest partial match routes to `CHANGES_REQUESTED`, never a quiet
  close. Claude is the standing gate reviewer for this comparison before any
  batch reaches the Human for acceptance — no wave self-declares a 100% match.
  **Redo loop, not disclose-and-stop:** a mismatch is fixed and re-checked in a
  loop until it matches (the way `cozy_house_small_A` iterated v1→v9); only 3
  identical failure signatures on the same object route to `NEED_HUMAN`.
- **Standard dispatch template (Human-mandated 2026-07-23):** every future
  dispatch prompt to either Grok parent is authored from
  `orchestration/control/STANDARD_GROK_WORK_ORDER_PROMPT_TEMPLATE_001.md`,
  which encodes the lessons paid for in rework so far (name exact files,
  headed QA is mandatory not headless, receipts must be independently
  re-derivable, additive not destructive, honesty placeholders, mockup
  redo-loop). Claude keeps it current; deviating from it is itself a finding.

---

## 13. Where the project stands right now (living pointer)

The authoritative, moment-to-moment state is always
`orchestration/control/codex_directive.json` (read it before acting) and the
latest entries of `orchestration/control/CONDUCTOR_JOURNAL.md`. As of this
injection:

- **G8 alpha gate PASSED by the Human Product Lead.** The 2.5D Private Reality
  vertical slice is playable: Starter Realm, prompt→proposal→preview→confirm→
  manifestation→commit, save/reload, undo.
- **World 1 integration gate is open.** Active programme is **UCBV-001**
  (Unified Character-Block-Visual Foundation), currently at the **C5 Purple
  release recommendation** step (resumed after a Human-gate companion-deadlock
  correction, C5H1, was fixed and Human-accepted). `accepted=false` overall.
- Real, verified asset: the **Nori-7** character ships as a rigged, animated GLB
  (14 bones, 10 keyed clips); 5 gardening clips are honestly **deferred**, not
  faked. Nori-7 is built through runtime but **not product-accepted**, and a
  Human-requested **visual redesign** (prettier/friendlier) is **queued** for
  after C5 closes.
- **Queued / not authorized** (do not start without a dedicated directive):
  Nori-7 visual redesign, P2E-002, character-backbone production, DNA Platform
  vNext execution, and everything post-alpha in §9.
- **Codex-absent capsule is in effect** — Human Product Lead is sole acceptor
  until Codex re-entry.
- **Two Grok Desktop parents now authorized** (2026-07-23): build
  `019f7ffd-3995-71c0-aca1-51078e24a852` and design
  `019f8e3c-e53b-74e0-a878-df6b8398338e` (§12). The **100% mockup fidelity
  law** (§12) is now standing for anything sourced from the mockup catalog.
- **Town cadastre import (WO-TOWN-GRID-IMPORT-001)** landed from the build
  parent: Blue+Red independently verified clean (round-trip fingerprint,
  honesty logic in code, no destructive edits), but QA (headed evidence +
  mockup-fidelity comparison) never ran — sent back, `CHANGES_REQUESTED`, not
  yet ready for Human batch-accept.

This section is a snapshot; when it disagrees with `codex_directive.json`, the
directive is correct.

---

## 14. Standing operating contract for every Grok agent

1. Read this vision lock, your directive, your work order, the Architecture
   Lock, and the Blueprint SSOT **before planning or editing**.
2. Stay inside your writer lease and authority token. One writer per file.
3. Propose; never self-accept; never claim Human/Codex acceptance you were not
   given.
4. Never fake a payload, alias missing content, or present metadata/staging as
   runtime. Missing capability → typed AssetRequest, fail closed.
5. Never cross a Red F01 hard stop, quarantine boundary, or Godot-override
   boundary on your own initiative.
6. Do not pull a future horizon forward or re-litigate a settled Human/Codex
   decision. If blocked or contradicted, route `NEED_HUMAN` / `NEED_CODEX`.
7. Emit a schema-valid MAF receipt with real UUID lineage, `accepted=false`,
   `self_accept=false`, and executable evidence for every material step.
8. Keep the north star (§1) true in everything you ship.
9. If your wave places anything sourced from the mockup catalog into `game/**`,
   it is not done until it visually matches that mockup 100% (§12) — get headed
   evidence of the comparison, do not self-declare the match.

Deviation from this document is itself a reportable finding. Follow it until the
game is complete and accepted.

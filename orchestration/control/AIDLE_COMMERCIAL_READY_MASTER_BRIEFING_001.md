# AIdle — Commercial-Ready Master Briefing 001 (autonomous-phase handoff to Grok)

Status: ACTIVE · Owner: Human Product Lead (Hanh) · Author: `aidle-continuity-conductor` (Claude)
Date: 2026-07-23 · Pairs with: Directive 99 (autonomous phase) + `AIDLE_GAME_VISION_LOCK_001.md`

This document transfers everything the conductor has gathered so Grok can run
the project **autonomously** toward a **commercial-ready** product. It does not
replace the vision lock (the constitution) or your live directive (the current
orders) — it is the consolidated field knowledge and the phase plan they attach
to. Read it once in full, then operate from the vision lock + directive.

---

## 1. Prime objective

Bring AIdle to **commercial-ready quality**: the H1 Cozy 2.5D Private Reality
experience, polished, stable, accessible, performant, and complete enough to
sell — built and hardened through the standing MAF loop, with Grok orchestrating
its own subagents wave by wave.

"Commercial-ready" is a **quality/completeness bar**, not permission to ship.
The acts of shipping, publishing, charging money, or opening network/live
providers remain **Red F01 hard stops** requiring explicit Human authorization
(see §7). Build to sellable quality; do not sell without a Human gate.

Scope of "commercial-ready" here = **H1 only** (single-player cozy creative
Private Reality + Free Desktop Bridge edition to ship quality). H2–H6
(multiplayer, marketplace money, Doppelganger cities, spacecraft, exoplanets,
Open Continuum) stay behind their own future horizon directives.

---

## 2. Where the project actually stands (verified 2026-07-23)

- **G0–G8 roadmap complete; G8 alpha gate PASSED by the Human Product Lead.**
  The 2.5D vertical slice is playable end to end: Starter Realm → prompt →
  proposal → validate → preview → confirm → manifestation → commit →
  save/reload → undo.
- **UCBV-001** (Unified Character-Block-Visual Foundation): **C5 Purple release
  recommendation is machine-VERIFIED** (Directive 98, receipt
  `correction_010/C5_purple_release_010.json`, `accepted=false`,
  `WAITING_CODEX`, `product_writes=[]`, Purple 38/38 PNG + regressions
  independently recomputed). It awaits acceptance — under the Codex-absent
  capsule this goes into the Human's next **batch acceptance**.
- **C5H1 companion-deadlock correction**: fixed, machine-VERIFIED, and
  **Human-accepted** (`c5h1_001/HUMAN_ACCEPT_c5h1_001.json`). E-key path now
  toggles the Companion; Confirm/manual-build no longer deadlocks.
- **Nori-7 character**: a **real** rigged, animated GLB ships (14 bones, 10
  keyed clips; independently hash-verified). 5 gardening clips
  (water/plant_seed/harvest/charge/low_energy) are **honestly deferred**, not
  faked. A Human-requested **visual redesign** (prettier/friendlier — currently
  reads as a plain white blob) is **queued** for after C5 closes.
- **DNA Platform vNext**: staged compiler kit (`dna_platform_vnext/`) reviewed
  by the conductor — schemas/hashes/adversarial fixtures all independently
  re-verified green. It is **staging/design only** until its own directive.
- **Motion kit** (`motion_kit/`): READ_ONLY staging design input (172 clips
  classified, ~96 authored items). Not the runtime path; do not present it as
  runtime animation.

Always confirm the moment-to-moment truth from
`orchestration/control/codex_directive.json` (live directive) and the latest
`CONDUCTOR_JOURNAL.md` entries before acting.

---

## 3. Hard-won field knowledge (do not rediscover the hard way)

Findings the conductor verified this session, so you can skip the traps:

1. **A name is not a payload.** The Tier3 animation library is a *dictionary of
   clip names + compatible skeletons* — 172 clips, **none** with real duration/
   keyframes/events. Never load a name-only clip and claim animation. Author
   real keys or emit an `ASSET_REQUEST`. Nori-7's real motion came from an
   offline Blender authoring job, not from the catalog metadata.
2. **Two independent naming systems exist** (Character Foundry rig names vs the
   DNA `skeleton_families` catalog). There is no guaranteed 1:1 map; resolve IDs
   against the real catalog, never assume a prose rig name is a catalog id.
3. **Palette was reconciled** to the art-bible cream `#fdf3e2` (not the recipe's
   `#F7E9C6`) via `C0_cream_reconciliation.json`. Use `#fdf3e2`.
4. **Manifestation stage-count discrepancy is still OPEN**: live/art-bible uses 4
   stages (wireframe→hologram→materializing→complete); one DNA build-graph
   example uses 5 (adds COMMITTING). The progressive-construction SM in the
   blueprint is the 9-state authority; reconcile before any manifestation rework
   and route it as a decision, don't silently pick one.
5. **HUD/InputMap label bug (non-blocking residual, real):** the HUD says "press
   E to chat" but `companion_call` is bound to physical **KEY_C**;
   `prompt_quick_open` is **KEY_SLASH**. E is not the companion key. Fix the
   label (or rebind) as a small UX wave; when testing companion, use C or the
   action-bar button.
6. **Quarantine is real:** generated GLB/asset artifacts never enter the
   approved catalog / `game/**` without a separate signed promotion gate.
   `write_approved_catalog` is forbidden to workers.
7. **Godot API assumptions are unverified** where the motion-kit/adapter used
   AnimationTree/IK — every uncertain line was marked `VERIFY(godot4.3)`. The
   real runtime uses a direct animation adapter with `use_anim_tree=false`.
   Verify against the pinned Godot 4.3 API before wiring, don't trust the design
   sketch.
8. **Receipts are trustworthy but must be re-verified, not trusted.** Every MAF
   receipt records real sha256 lineage; the conductor recomputes hashes, decodes
   logs (they are **UTF-16LE**, not UTF-8), and opens evidence PNGs rather than
   trusting the printed "PASS." Keep doing this.

Reference artifacts (design/staging, not runtime): `GROK_CHARACTER_BUILD_SYSTEM_001.md`
(6-phase character SOP), `dna_platform_vnext/` (compiler kit), `motion_kit/`
(motion primitives), the visual mockups under `orchestration/control/visual_reference/`,
and the conductor's ledgers in `CONDUCTOR_JOURNAL.md`.

---

## 4. The pre-defined plan (what "in-plan autonomous work" means)

You run these **without per-step check-ins**. Propose the detailed wave
breakdown yourself; keep each wave inside the MAF loop and one writer lease.
Rough sequence toward commercial-ready H1 (you may reorder within the fence and
justify it in a receipt):

1. **Close UCBV-001**: fold the machine-VERIFIED C5 release into the next Human
   batch acceptance; then land the small HUD E/C label fix (Finding, §3.5).
2. **Nori-7 visual redesign** (Human Finding 2): revise visual_spec + design
   docs → re-author the Blender GLB (quarantined) → narrow Godot override →
   headed proof. Prettier/friendlier, same cozy-cyber-pixel lock.
3. **Author the 5 deferred Nori-7 gardening clips** (or formally defer to Tier3)
   — real keys, not metadata.
4. **P1E art programme** continuation: per-world-profile palette variants,
   density/props/exposure waves, toon shader/outline — to ship-quality art.
5. **Control 1B** (input/control/accessibility) — unblocked, not started.
6. **Character Foundry 1C** — unblocked, not started.
7. **DNA Platform vNext** — only after it receives its own execution directive
   (it is staging today); until then, no vNext product work.
8. **Commercial hardening gates** (derived from blueprint G7/G8, extended to
   ship quality): performance budgets on target hardware; accessibility
   (color-independent state, reduced-motion, hide-aura); stability/soak; save
   integrity + idempotency + revision-conflict recovery; Free Desktop Bridge
   edition end-to-end; onboarding/first-run polish; content/art coherence pass;
   and a Human ship-readiness checklist.

Everything **outside** this list — H2–H6 horizons, marketplace money, real-city
data, spacecraft/exoplanets, TTS/voice, neural world-model portals, unrestricted
Text-to-3D — is **out of plan**: escalate, do not start.

---

## 5. Autonomous operating rules (Human-chosen, binding this phase)

1. **Run the plan without check-ins.** Execute in-plan waves continuously,
   orchestrating your own MAF subagents (Blue/Red/QA/Purple) under the sole
   parent `019f7ffd-3995-71c0-aca1-51078e24a852`. Do not stop to ask permission
   for work already inside §4.
2. **Escalate only for out-of-plan events.** Surface to the Human when, and only
   when: a task falls outside §4, a Red F01 hard stop is reached, a decision the
   plan doesn't cover appears, a vision-lock conflict arises, or three identical
   failures occur (`NEED_HUMAN`). Otherwise keep going and record decisions in
   receipts + the journal.
3. **Context discipline (mandatory).** When your context reaches ~75%, checkpoint
   all important state to durable project files (journal entry + state notes +
   receipts) — never rely on hidden chat memory. **After any compaction, you
   MUST re-read in full**: this briefing, `AIDLE_GAME_VISION_LOCK_001.md`,
   `AGENTS.md`, `ARCHITECTURE_LOCK.md`, the live `codex_directive.json`, and the
   latest `CONDUCTOR_JOURNAL.md` entries — *before* resuming work.
4. **Batch acceptance, never self-accept.** Accumulate Purple-VERIFIED waves and
   present them as **gate-ready batches** for Human acceptance. No agent accepts
   its own or another agent's output. While Codex usage is exhausted, the Human
   Product Lead is the sole acceptor; Codex may re-assert machine acceptance on
   return (do not re-litigate Human acceptances already given).
5. **Self-improvement is bounded.** "Self-training" = learn from your own
   receipts/journal via the knowledge-loop and curiosity-engine skills and
   refine your orchestration. It does **not** mean training a model, generating
   runtime code freely, or expanding your own authority.
6. **Evidence + honesty every wave.** Schema-valid MAF receipt, real UUID
   lineage, `accepted=false`/`self_accept=false`, executable evidence, UTF-16LE
   logs decoded, hashes recorded. Documentation ≠ implementation; green smoke ≠
   Human visual acceptance; metadata ≠ animation.

---

## 6. Definition of done (commercial-ready H1)

- The full core loop is polished and stable end to end, with no known blocker-
  class defects, verified by headed evidence at both resolutions.
- Save/reload/undo integrity holds under idempotency + revision-conflict tests.
- Art is coherent to the cozy-cyber-pixel lock; characters (incl. redesigned
  Nori-7) read as friendly and intentional; manifestation reads as designed.
- Accessibility + reduced-motion + performance budgets pass on target hardware.
- Free Desktop Bridge edition works end to end; the realm is playable with no AI
  response; no credentials anywhere in client/bridge/logs/saves.
- A Human ship-readiness checklist passes (the G8 checklist extended to ship
  quality). Only then does the Human decide the (gated) act of shipping.

---

## 7. Non-negotiable boundaries (unchanged, in every wave)

- **Red F01 hard stops (Human-gated always):** ship, publish, deploy, push,
  marketplace money, network/live-provider/credential use, dependency install,
  Godot version change. Never cross on your own — escalate.
- **Quarantine boundary:** no generated artifact promoted to approved
  catalog/`game/**` without a separate signed gate.
- **Godot override boundary:** no `game/**` product patch without an explicit,
  narrow override naming exact files.
- **One writer per file; parent-only spawn; no grandchildren; no second Grok
  parent or CLI parent.**
- **The vision lock (`AIDLE_GAME_VISION_LOCK_001.md`) governs; the machine
  contracts (schemas/Architecture Lock) bind.** On conflict, the machine
  contract wins and the docs are corrected — never the reverse.

Operate from here. When in doubt, re-read the vision lock and route the doubt to
the Human — that is the job, not a failure.

# WO-P1E-005 — Tier 3 offline time-delta simulation

Authority: `PATCH_DRAFT` (Blue only) · State: `READY`
Issued by: `aidle-continuity-conductor` — **NOT Codex**
Authorized by: Human Product Lead, 2026-07-22
Godot override: covered by the existing P1E art-programme grant

Single continuous work order. No delivery phases — the feature ships whole.
The Blue → Red → QA → Purple wave structure still applies; that is review
governance, not delivery staging.

---

## 1. What Tier 3 is, and why it is the most important thing in this package

Simulation LOD tiers, from `04_SIMULATION_LOD_STANDARD.md`:

| Tier | Meaning |
|---|---|
| 0 | Full rigid-body / reaction / VFX, every frame, near the player |
| 1 | Reduced frequency, sleeping preferred |
| 2 | State-only graph simulation, no physics |
| **3** | **Entity not loaded at all. State advanced by elapsed time on return.** |

Tier 3 is the idle mechanic. The player closes the game, comes back eight hours
later, and the crops have grown — but nothing simulated eight hours of frames.
One bounded calculation reconstructs where the world should be.

**Without Tier 3, AIdle is not an idle game.** It is a builder whose world
freezes the moment you look away.

### It does not exist in the source package

`04_SIMULATION_LOD_STANDARD.md` promises Tier 3 time-delta simulation. Every
`.gd` file in `world_DNA/.../godot_4_3/addons/aidle_elemental_physics/` was
searched. **`simulation_lod_controller.gd` only assigns tier numbers by
distance.** There is no catch-up logic anywhere.

We are implementing a documented promise that was never built. Treat the
package's Tier 3 text as a requirement statement, not as reference code.

---

## 2. The authority question — settle this before writing code

This is the part that could quietly break the project's safety model, so it is
specified first.

AIdle's architecture says: **AI proposes, validation gates, the human confirms,
World Commit mutates canonical state.** Tier 3 mutates durable state with **no
human present to confirm**. On its face that is a violation.

It is not, and the distinction must be implemented, not just asserted:

> Tier 3 does **not make decisions**. It performs a **deterministic replay of
> already-committed rules over already-committed state**. It never creates an
> entity, never places geometry, never chooses anything. It advances numbers
> that a previous, human-confirmed commit already authorised to advance.

Binding consequences:

- Tier 3 may **only** modify state fields on entities that are already
  `canonical_committed = true`.
- Tier 3 may **never** create, destroy, re-parent or re-place an entity.
- Tier 3 may **never** introduce a new module, asset, or placement.
- Tier 3 writes go through the **existing validated persistence path**. No new
  write route to canonical state. If the current path cannot express an
  offline advance, extend it explicitly and say so — do not bypass it.
- A Tier 3 advance must produce a **receipt** in the same family as other
  mutations, so an unattended change is never invisible in the record.

If any requirement below appears to force a violation of this section, **stop
and report**. Do not resolve it by widening authority.

---

## 3. Time source — assume the clock is hostile

The player controls the system clock. A naive `Time.get_unix_time_from_system()`
delta lets anyone fast-forward a harvest by changing their date.

Required handling:

- Persist **both** a wall-clock timestamp and a monotonic counter at save.
- On load, compute elapsed from wall clock, but **validate it**:
  - Wall clock moved **backwards** → treat elapsed as `0`. Never rewind state.
  - Wall clock jumped forward beyond `max_offline_seconds` → clamp to the cap.
  - Record every clamp or rejection in the receipt with the observed values.
- `max_offline_seconds` is configuration, not a literal. Start at **8 hours**.
- The cap is a **product decision** as much as a technical one; surface the
  clamp to the player rather than silently truncating their absence.

This is not anti-cheat in the security sense — it is a single-player desktop
build. It is about the save file staying internally consistent and the numbers
never becoming absurd.

---

## 4. Determinism — the hard requirement

**Advancing state by one hour in a single step must produce the same result as
advancing it by sixty one-minute steps**, within a stated floating-point
tolerance.

If that does not hold, the world visibly differs depending on how often the
player happened to open the game, and save/reload stops being trustworthy.

Consequences for the implementation:

- Prefer **closed-form integration** where the maths allows it.
- Where closed form is not possible, use **fixed-size sub-steps** with a
  documented step size and a bounded iteration count — never a loop proportional
  to real elapsed time. Returning after a month must not run a million ticks.
- No randomness in Tier 3 advance. If a rule needs variation, it must be a pure
  function of `(entity_id, committed_seed, elapsed)` — reproducible on replay.
- Clamp after every advance. `elemental_state.clamp_values()` exists; extend it
  to cover the new fields.

---

## 5. What actually advances — the pilot scope

Only the two dynamic pilot modules from `WO-P1E-004`:

| Module | Element | Advances |
|---|---|---|
| `cozy_farm_plot_A` | `element_soil` | `wetness` decays; `growth` accrues, rate limited by wetness |
| `cozy_pond_small_A` | `element_water` | acts as a wetness source for nearby soil |

Growth uses the adopted `crop_growth` solver (Liebig's law of the minimum:
limiting factor = `min(water, light, fertility, temperature_fit)`).

**Two source-package defects must be fixed as part of this work**, both recorded
in `DNA_ADAPTATION_SPEC_001.md`:

- **D1** — `AIdleElementalState` has no `growth` or `health` field, so the
  solver's return values have nowhere to be written. Add them as clamped 0–1
  exports.
- **D3** — `physical_profile_id` is null across all bindings. Populate for the
  pilot modules.

Static pilot modules (`rock`, `path_stone`, `fence`) carry state but **do not
advance**. They are the control group: after any offline period their state must
be **byte-identical**. If a static module's state drifts, the advance is
leaking scope.

---

## 6. Fitting our system — where the DNA design must be adjusted

Per the Human Product Lead's standing instruction, the DNA side adapts to us.

### Tier assignment must be driven by chunk residency, not observer distance

`simulation_lod_controller.gd` polls each body's distance from one observer node
every 0.25 s. That cannot know whether a chunk is loaded, which is precisely
what Tier 3 depends on.

Required: **an entity in an unloaded chunk is Tier 3, regardless of its distance
number.** Distance may refine tiers 0–2; residency decides tier 3.

### Tier distances are wrong for our world by an order of magnitude

Defaults are `[48, 144, 384]` metres. Our Starter Realm terrain is **32 m × 32 m**
— the entire world sits inside tier 0 and the system never engages.

Use `[12, 32, 96]` as a starting point, marked provisional pending profiling.

### Tier switching must act on nodes we actually have

Current code freezes `RigidBody3D` and toggles `GPUParticles3D`. Our intake
builds **`StaticBody3D`**, and the project contains **no `GPUParticles3D`**.
Both branches are dead code for every module we own.

Tier switching must instead act on: animation players, state-simulation
frequency, and visual variant selection.

### Our manifestation state machine stays authoritative

`elemental_body_3d.gd` carries its own `configure_preview` /
`activate_after_commit`. `manifestation_instance.gd` already owns
`wireframe → hologram → materializing → complete` and its collision layers, and
that is verified, human-confirmed work.

The elemental body is **subordinate**: it reacts to our stage transitions and
never drives them. `activate_after_commit()` fires as a consequence of reaching
`complete` — never as an independent path.

---

## 7. Returning to the world — the reconciliation moment

When a Tier 3 chunk loads:

1. Read persisted state and both timestamps.
2. Compute and validate elapsed (§3).
3. Advance deterministically (§4), clamping every field.
4. Persist the new state through the validated path, with a receipt.
5. Select visual variants from the new state — high `wetness` shows the `wet`
   variant. **This is how offline change becomes visible without a shader**,
   and it is why the state layer pays off before wave 4.
6. Hand the entity to tier 0–2 for live simulation.

Steps 3 and 4 must complete **before** the entity becomes interactable. The
player must never act on stale state and then have it change under them.

---

## 8. Player-facing honesty

When a return advance occurs, the game should be able to say what happened —
"your crops grew while you were away" with the elapsed time actually used after
clamping.

Not a UI work order, but the data must be **available and truthful**. If the
absence was clamped from three days to eight hours, the reported figure is eight
hours. Do not report the uncapped number.

---

## 9. Out of scope

Art programme waves 2–4. `P2E`–`P6E`. `Control-1B`. `Character-Foundry-1C`.
Approved catalog, World Commit changes beyond the persistence extension in §2.
Red `F01`. `codex_directive.json`. The DNA graphics standard — **still requires
an ADR and is untouched here**. Thermal, structural, energy and fluid solvers.
The remaining 29 elements and 43 reaction rules.

No `res://` promotion; `GAME_GLB_COUNT` stays 0.

---

## 10. Writer allowlist

State the complete proposed allowlist and confirm before touching any file.

---

## 11. Acceptance criteria

1. **Determinism** — one 1-hour advance equals sixty 1-minute advances within a
   stated tolerance. Demonstrate with actual numbers.
2. **Bounded cost** — a 30-day elapsed input completes in bounded time with a
   bounded iteration count. State both.
3. **Clock hostility** — backwards clock yields zero advance; a forward jump
   beyond the cap is clamped and recorded. Test both.
4. **Authority** — Tier 3 modifies only `canonical_committed` entities, creates
   and destroys nothing, and writes only through the validated path. Prove by
   test, not assertion.
5. **Receipt** — every offline advance produces one.
6. **Static control group** — `rock`, `path_stone`, `fence` state is unchanged
   after an offline period.
7. **Residency drives tier 3** — an entity in an unloaded chunk is tier 3 even
   at zero distance.
8. **Visual reconciliation** — a wetness change selects the `wet` variant on
   return.
9. **Ordering** — advance and persist complete before the entity is interactable.
10. **No regression** — full suite green; preview stages still non-solid;
    manifestation state machine unchanged in authority.

---

## 12. Receipt requirements

Real durable Grok child/transcript refs cross-checked against `grok_status.json`.
`accepted=false`, `self_accept=false`.

Report the determinism comparison numerically, the bounded-cost figures, the
clock-tamper test results, and which parts of the DNA package were executed for
the first time.

**Headed visual evidence** for criterion 8 — the whole point is that the player
can see the world moved while they were gone.

State plainly in the receipt that Tier 3 did not exist in the source package and
was implemented here.

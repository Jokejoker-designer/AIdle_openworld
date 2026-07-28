# Codex comprehension check — 15 questions with answer key

Prepared by: `aidle-continuity-conductor`, 2026-07-22
Purpose: let the Human Product Lead measure how completely Codex has absorbed
the handover. **Not a formality.** Every question below is one where a shallow
reading of the handoff documents produces a confidently wrong answer.

Give Codex the questions only. The answer key is for the Human Product Lead.

---

## SECTION A — Authority and state

**Q1.** Who accepted `ENV0-001`, when, and what exactly was the accepted scope?

> **A1.** The **Human Product Lead**, 2026-07-21 ~20:00, scope = git tag
> `env0-d50-verified` → commit `1322b95` in `E:\AIdle_Blender_Bridge_P0`.
> **Not** Codex, **not** any agent. Acceptance was valid because Codex was
> unavailable and the continuity capsule names the Human Product Lead as the
> only acceptor in that condition.
> ⚠ **Trap:** the tag is *annotated*, so `git rev-parse env0-d50-verified`
> returns `9cda673` — the tag object's own SHA. The commit is `1322b95`, via
> `^{}`. Grok flagged this as a discrepancy; it was a false alarm.

**Q2.** Directive 50 is current. Why is that a problem, and what should be done?

> **A2.** Its milestone reads *"ENV0 Environment Bridge P0E correction"*, which
> finished hours before the session ended. Everything after 15:46 on 2026-07-21
> — ENV0 acceptance, G8 pass, World 1 gate, six P1E work orders, four Godot
> overrides — was authorised **directly by the Human Product Lead**, each
> recorded individually in the journal, **not** by Directive 50.
> Correct action: issue **Directive 51**. But do **not** retroactively
> "legalise" work beyond what actually happened.

**Q3.** G8 passed. Which tasks did that unblock, and what is their status?

> **A3.** `Control-1B` and `Character-Foundry-1C` — both **unblocked and never
> started**. Also `P1E`, which did start.
> ⚠ **Trap:** unblocked ≠ started ≠ safe to start now.

**Q4.** How many Godot overrides exist, and does one cover all Godot work?

> **A4.** **Four, each narrowly scoped**: `WO-G8-UX-001` (focus/collision),
> `WO-G8-UX-002` (fence), `WO-P1E-002` (GLB intake), and P1E art waves 3–4
> (fauna animation + toon shader). Directive 50 still forbids Godot patches in
> general. **No blanket permission exists.** New Godot work needs a new grant.

---

## SECTION B — The traps

**Q5.** `grok_status.json` does not record the ENV0 acceptance or the G8 pass.
Does that mean they did not happen?

> **A5.** **No.** They happened and are recorded in `CONDUCTOR_JOURNAL.md`
> entries 023 and 026 and in the work orders. The keys `env0_001`,
> `g8_001_status`, `p1e_unblocked`, `world_1_integration_gate_opened` and
> `human_only_acceptor_while_codex_blocked` were **present at 00:04 and gone by
> 00:30** — the status writer appears to rebuild from a template each wave
> instead of merging, silently erasing governance records.
> A restore was dispatched. **This is the single most dangerous open item**,
> because a Codex that trusts only `grok_status.json` will conclude the Human's
> decisions never occurred.

**Q6.** The pond rendered white in the game. Was that a material bug?

> **A6.** **No.** The GLB always carried `#8fd4e8`. The game session runs art
> style `surrealism_canvas` (ground `8B7AA8` lavender) while the kit was
> authored for `cozy_cyber_pixel` (ground `8FBC8F` green). Nobody rendered
> anything wrong — the evidence was correct for Cozy, her game correct for
> Surrealism. **We were verifying a different artefact than she was playing.**

**Q7.** Why could the Human Product Lead never reach the art-style chooser?

> **A7.** `game_manager.gd:36` —
> `ART_STYLE_SELECT if not has_chosen_style() else IN_WORLD`, and
> `has_chosen_style()` only checks whether `world_meta.cfg` holds
> `world/art_style`. One saved choice locks every later session permanently.
> She was not missing styles; the chooser was unreachable.

**Q8.** Option B was chosen — per-profile palette variants. How many variants,
and along which axis?

> **A8.** **11 modules × 2 world profiles = 22.** The axis is **world profile**,
> not art style — the Human Product Lead ruled that the 7 world profiles are
> primary and art style is a future customisation layer.
> ⚠ **Trap:** answering "11 × 4 art styles = 44" means the ruling was missed.
> Only `cozy_cyber_pixel` and `surrealism_canvas` have content today.
> `cyberpunk_dense` and `pastoral_fantasy` have **no world profile at all** and
> get no dedicated art.

**Q9.** The DNA package documents Tier 3 time-delta simulation. Can it be used?

> **A9.** In **v1.0, no — it did not exist.** The docs promised it;
> `simulation_lod_controller.gd` only assigned tier numbers by distance. The
> most valuable advertised feature was absent. **v1.1_Tier3 implements it**, and
> its determinism solution is sound: `_integral_min_clamped_linear` integrates
> each piecewise-linear segment exactly, so one 1-hour advance equals sixty
> 1-minute advances by construction.

**Q10.** Red `F01` — the environment API is unauthenticated. Why is that
acceptable, and when does it stop being acceptable?

> **A10.** Acceptable now because the API binds loopback `127.0.0.1` under a
> documented P0 local-trust model, and the Human Product Lead deferred it
> explicitly to prioritise infrastructure and graphics.
> **It becomes a hard blocker** before any networked work — shared district,
> co-op — or any shipping build. Deferred is not closed.

---

## SECTION C — Judgement

**Q11.** A QA receipt reports `shadow = 10.1 %`, inside the 5–15 % target.
Is the lighting acceptable?

> **A11.** **Not determinable from that number alone.** In the real case,
> **96 % of that shadow budget sat inside one contiguous near-black void** —
> the metric passed while the scene had no real directional shading. A
> percentage cannot distinguish soft distributed shadows from a hole in the
> image. Spatial distribution must be checked.

**Q12.** A material check passes. The pond has previously rendered beige
`(218,209,195)`, white `(255,255,255)` and grey `(185,195,189)`. What should
be suspected?

> **A12.** **The check.** All three wrong values passed the same test because
> per-channel RGB distance collapses hue and saturation into one scalar, and
> grey sits numerically between colours while being visually nothing. Three
> distinct failures producing one PASS means the check is measuring the wrong
> property. Correct test is hue + saturation.

**Q13.** A receipt has `child_task_ref: null`. What does that tell you?

> **A13.** **Nothing — and that is the problem.** Null absorbs at least four
> distinct causes: no child by design, capture failure, serialisation loss, or
> omission. It destroys the evidence needed to distinguish them. **Null is our
> NaN.** A null field and an honest stated limitation are completely different
> things in an audit.

**Q14.** A work order tells Blue to remove a private-attribute reach-in on
`runner._worker_gate`, but the allowlist omits `blender_runner.py`. Blue edits
it anyway. Who is at fault?

> **A14.** **The work order.** The instruction could not be carried out without
> that file. This happened in `WO-ENV0-002`; both Red and Purple then passed a
> false "allowlist PASS" claim. Rule: a work order must list every file its own
> instructions imply, and reviewers must **diff the actual write set** rather
> than reading the claim.

**Q15.** Evidence PNGs show a colourful scene. The Human Product Lead's
screenshot shows white. Which is the defect?

> **A15.** **Neither image is wrong — the process is.** Evidence must be the
> same artefact the human plays. Both PNGs were correct for `cozy_cyber_pixel`;
> her session ran `surrealism_canvas`.
> Permanent rule now in force: **every headed visual capture must record which
> art style was active**, and a visual claim without that field is not evidence.

---

## Grading

- **13–15 correct** — Codex has the handover. Proceed.
- **9–12** — solid on facts, weak on traps. Re-read journal entries 012, 023,
  026, 032, 034, 035.
- **Below 9** — do not let it issue Directive 51 yet. It will formalise a
  picture that is partly wrong.

**Most important single answer: Q5.** If Codex believes the Human's acceptances
never happened because `grok_status.json` no longer records them, everything
downstream is built on sand.

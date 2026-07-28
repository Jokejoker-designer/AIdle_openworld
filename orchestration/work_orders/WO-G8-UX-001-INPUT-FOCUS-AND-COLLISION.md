# WO-G8-UX-001 — Input focus trap and player collision

Authority: `PATCH_DRAFT` (Blue only) · State: `READY`
Issued by: `aidle-continuity-conductor` — **NOT Codex**
Authorized by: **Human Product Lead, 2026-07-21, explicit verbal order after live playtest**

## Authorization note — read this first

Directive 50 lists *"patch Godot, Scene runtime, Character Foundry, Control"* in
`forbidden_actions`, and `Control-1B` is `BLOCKED`. This work order **overrides
that restriction for this narrow scope only**, on the direct order of the Human
Product Lead, who sits above Codex on gate and ordering decisions per
`02_SHARED_GOVERNANCE.md`.

This override is recorded, not implied. It does not unblock `Control-1B`, does
not unblock `P1E`, and does not change `G8-001` from `HITL_REQUIRED`. Codex is
unavailable until 2026-07-28 and cannot counter-sign; the record must therefore
be unambiguous about who authorized what.

Scope is strictly the six defects below. Nothing else in Godot may be touched.

## Source of the report

Live human playtest, `Surrealism Canvas` / `Private Reality` / `Paid API
(fixture)`. Filed as
`orchestration/evidence/g8_human_gate/HUMAN_PLAYTEST_FINDING_001_UI_FOCUS_TRAP.md`.

Player report: after clicking an action-bar button, returning to the game and
pressing movement keys does not move the character — the action bar steps
through Demo Build, Confirm Build, Cancel, Import instead. Physics interaction
also reported as wrong.

## Defect 1 — Buttons never release focus (root cause)

`game/scripts/ui/playable_action_bar.gd:103` sets `focus_mode = Control.FOCUS_ALL`
on all six buttons. A repo-wide search for `release_focus` returns **zero hits**.
A clicked button holds keyboard focus indefinitely, so the action bar owns the
keyboard instead of the world.

**Fix:** these buttons are mouse-driven. Set `focus_mode = Control.FOCUS_NONE`.
If keyboard accessibility is wanted later, keep `FOCUS_ALL` and call
`release_focus()` in every `pressed` handler — but do not do both halfway.

## Defect 2 — Jump is bound to `ui_accept`

`player_controller.gd:75`:

```gdscript
if allow_jump and Input.is_action_just_pressed("ui_accept") and is_on_floor():
```

`ui_accept` is Godot's built-in UI activation action (Space and Enter). With a
focused button present, pressing Space **presses that button** instead of
jumping. Combined with defect 1 this is the most probable mechanism behind the
reported button cycling, and it explains a report that did not involve the arrow
keys.

**Fix:** define a dedicated `jump` action in `game/project.godot` bound to Space,
and use it here. Gameplay must never read `ui_*` actions.

## Defect 3 — Arrow keys are double-bound

`game/project.godot` binds `move_forward`/`move_back`/`move_left`/`move_right` to
both the letter keys and the arrow keys. Neither project file overrides `ui_*`,
so the arrows also remain Godot's default focus-navigation keys. Arrows drive
movement and focus navigation simultaneously.

**Fix:** pick one owner for the arrow keys. Either drop arrows from `move_*`, or
remap `ui_*` off the arrows. Do not leave both bound.

## Defect 4 — Player cannot collide with manifested buildings (most serious)

- `game/scenes/player/player.tscn`: `collision_layer = 2`, `collision_mask = 1`
- `manifestation_instance.gd:14`: `COLLISION_LAYER_MANIFESTATION := 4`

Layer 4 is not present in mask 1. **The player walks straight through every
AI-manifested building.** This is the product's core loop — prompt, manifest,
inhabit — so a manifested house that cannot be collided with is a failure of the
central promise, not a cosmetic issue.

Starter-realm geometry is on layer 1 and does collide correctly, which is why the
defect is easy to miss: the pre-built house is solid, the AI-built one is not.

**Fix:** the player mask must include the manifestation layer once a
manifestation reaches its solid/complete stage. Respect the existing staged
logic in `manifestation_instance.gd` — wireframe and hologram stages
deliberately carry `collision_layer = 0` and must stay non-solid. Only the
completed stage becomes collidable.

## Defect 5 — Confirm the intended solidity table

Audit, then state explicitly in the receipt, which starter-realm props are meant
to be solid. Current state: House Body, tree trunks, fence posts, rocks and lamp
poles have collision; roof, door, windows, chimney, path segments, farm soil,
pond and flowers do not.

That distribution looks deliberate and is probably correct. **Do not change it
without saying why.** If it is correct, record it as intended and move on.

## Defect 6 — No regression coverage for input-to-movement

Nothing in the suite would have caught defect 1, 2 or 4. Human eyes did.

**Fix:** add a headed or scripted regression that (a) clicks an action-bar
button, sends movement input, and asserts the player transform actually changed;
and (b) places the player against a completed manifested building and asserts
the transform does **not** pass through it.

Point (b) is the check that turns "the core loop works" from a claim into
evidence.

## Dispatch graph

Same parent `019f7ffd-3995-71c0-aca1-51078e24a852`. Sequential, one child at a
time, no grandchildren, no new top-level session, no Grok CLI.

1. `aidle-worldgen-control-input`, `PATCH_DRAFT`, sole product writer.
2. `aidle-worldgen-red-scope`, `READ_ONLY_AUDIT`, findings only.
3. `aidle-worldgen-qa-evidence`, `VERIFY_ONLY`, tests plus headed evidence.
4. `aidle-worldgen-purple-acceptance`, `VERIFY_ONLY`, final gate.

## Writer allowlist

Every file the instructions above imply is listed. If a file outside this list is
needed, **stop and report rather than writing it**.

- `game/scripts/ui/playable_action_bar.gd`
- `game/scripts/player/player_controller.gd`
- `game/scenes/player/player.tscn`
- `game/project.godot` (input map only)
- `game/scripts/modules/manifestation/manifestation_instance.gd` (collision layer/mask only)
- new regression test or headed smoke script under `game/tests/` or the existing test location
- its exclusive receipt, log and trace

## Out of scope — do not touch

- Anything in `E:/AIdle_Blender_Bridge_P0` (ENV0 is `WAITING_HUMAN`, untouched)
- Scene runtime, Character Foundry, approved catalog, World Commit
- Camera behaviour, art style, Companion logic, quest logic
- `Control-1B` proper — this is a targeted defect fix, **not** the Control
  Foundation implementation, and must not be recorded as satisfying it
- `codex_directive.json` and all historical acceptance evidence

## Acceptance criteria

1. After clicking any action-bar button, movement keys move the player.
2. Space jumps and does not activate a focused button.
3. Arrow keys have exactly one owner; document which.
4. Player collides with a completed manifested building.
5. Wireframe and hologram manifestation stages remain non-solid.
6. Starter-realm solidity table unchanged unless justified in writing.
7. Regression tests from defect 6 exist and pass.
8. No pre-existing test regresses.
9. Nothing outside the writer allowlist is modified.

## Receipt requirements

Schema-valid `agent_step_contract` with a **real durable Grok Desktop
`child_task_ref` and `transcript_ref`**, cross-checked against
`grok_status.json.completed_children` before finishing. Include the exact
read/write set, literal commands with exit codes, and `product_writes`.

`accepted=false`, `self_accept=false`. Return `REVIEW_REQUESTED`,
`CHANGES_REQUESTED` or `WAITING_HUMAN`. The Human Product Lead is the only
acceptor while Codex is unavailable.

Headed visual evidence is required for criteria 1 and 4 — a screenshot or a
recorded transform delta. A passing unit test alone does not close this work
order, because a passing unit test is exactly what missed these defects.

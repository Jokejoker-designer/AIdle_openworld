# G8 human playtest finding 001 — UI focus trap in the action bar

Reported by: Human Product Lead, during live G8 playtest, 2026-07-21
Recorded by: `aidle-continuity-conductor`
Severity: **medium** — not a crash, but it breaks the core movement loop
Status: `OPEN`, **not fixed** — no authority exists to patch Godot right now

## What the player experienced

> After clicking a button (Demo Build, or others), going back to the game and
> pressing the movement keys does not move the character. Instead the action bar
> steps through its buttons — Demo Build, then Confirm Build, then Cancel, then
> Import.

Everything else in the first pass was judged acceptable.

## Why this matters more than its size suggests

This bug survived the entire automated pipeline. 43 tests pass, `compileall` is
clean, Purple returned `VERIFIED`, and none of it touched this. It took a human
pressing keys for ninety seconds.

This is the concrete argument for why G8 exists and why it must not be closed on
receipt evidence alone. `AGENTS.md` states it directly: *"a passing unit test is
not multiplayer or visual proof."*

## Diagnosis — what is confirmed

**Confirmed root cause.** `game/scripts/ui/playable_action_bar.gd:103`:

```gdscript
func _style_all_buttons() -> void:
    for b in [btn_companion, btn_export, btn_import, btn_demo, btn_confirm, btn_cancel]:
        if b == null:
            continue
        b.focus_mode = Control.FOCUS_ALL
```

All six action-bar buttons are given `FOCUS_ALL`, and **nothing in the codebase
ever calls `release_focus()`** on them — a repo-wide search for `release_focus`
returns no hits at all. Once a button is clicked it keeps keyboard focus
indefinitely, so the action bar, not the game world, owns the keyboard.

**Confirmed aggravating factor — arrow keys are double-bound.**
`game/project.godot` binds movement to both letter keys and arrows:

| Action | Keys |
|---|---|
| `move_forward` | W (87), Up (4194320) |
| `move_back` | S (83), Down (4194322) |
| `move_left` | A (65), Left (4194319) |
| `move_right` | D (68), Right (4194321) |

There is **no `ui_*` override** in either `project.godot`, so Godot's built-in
`ui_up` / `ui_down` / `ui_left` / `ui_right` keep their defaults — the arrow
keys. Arrows therefore drive movement **and** focus navigation simultaneously.
With a focused button present, the focus ring wins.

## What is NOT confirmed — stated honestly

The report describes **WASD**. Static analysis found no path from W/A/S/D to
`ui_*` focus navigation: there is no `ui_*` remap, and no `Shortcut` resource is
attached to any of the buttons (`playable_action_bar.tscn` and its script were
both searched).

So the arrow-key mechanism above is proven, but it does not by itself explain a
pure-WASD reproduction. Two candidate explanations, neither yet verified:

1. The player used the arrow keys, or a mix of both, and reported them as the
   movement keys generally.
2. Some other focus-navigation path exists that static reading did not reveal.

**This should be reproduced with a deliberate WASD-only attempt before the fix
is written**, so the fix targets the real mechanism rather than the convenient
one. Recording an unverified cause as fact is how the wrong patch gets shipped.

## Recommended fix — for a future authorized work order

1. Action-bar buttons are mouse-driven, so set `focus_mode = Control.FOCUS_NONE`
   instead of `FOCUS_ALL`. If keyboard accessibility is wanted later, keep
   `FOCUS_ALL` but call `release_focus()` in every `pressed` handler.
2. Resolve the arrow-key double-binding. Either drop arrows from `move_*` and
   leave them to the UI, or remap `ui_*` off the arrows. Do not leave both.
3. Add a regression test or a scripted headed smoke step: click a button, then
   send movement input, then assert the player transform actually changed.
   Point 3 is what would have caught this without a human.

## Authority

**Not actionable under the current envelope.** Directive 50 forbids patching
Godot, Scene runtime, Character Foundry and Control. `Control-1B`, the Control
Foundation task that owns input handling, is `BLOCKED`. `G8-001` is
`HITL_REQUIRED`.

This finding is filed as G8 human-gate evidence only. Fixing it requires an
explicit Human Product Lead decision — either a narrowly scoped UI work order,
or folding it into `Control-1B` when that unblocks.

Related note: the G8-001 receipt already records *"Control Foundation NOT
implemented (1B deferred)"*. This finding is consistent with that gap rather
than a surprise.

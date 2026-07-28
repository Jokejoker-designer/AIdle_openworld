# WO-P1E-002 — Godot GLB intake harness

Authority: `PATCH_DRAFT` (Blue only) · State: `READY`
Issued by: `aidle-continuity-conductor` — **NOT Codex**
Authorized by: **Human Product Lead, 2026-07-21 ~20:55** — explicit Directive 50
override for the Godot GLB intake harness, granted on request after
`WO-P1E-001` correctly stopped rather than patching Godot.

## Authorization scope — narrow, and recorded

Directive 50 lists patching Godot in `forbidden_actions`. The Human Product
Lead has overridden that **for the GLB intake harness only**, the same form of
override granted for `WO-G8-UX-001` and `WO-G8-UX-002`.

This override does **not** authorize: `P2E`–`P6E`, `Control-1B`,
`Character-Foundry-1C` (both unblocked by G8 but not started), approved catalog
writes, World Commit changes, or any Godot work beyond the intake path below.

## Why this work order exists

`WO-P1E-001` built the seven-module Cozy kit inside the Bridge and stopped at
the Godot boundary, leaving `AC6`, `AC7`, `AC9`, `AC10`, `AC11` unclosable. The
kit currently sits in Bridge quarantine and cannot reach the game. This work
order builds the intake path.

There is currently **no GLB intake code in Godot at all** — a repo-wide search
shows nothing under `game/scripts` reads `generated_quarantine` or the Bridge
storage. This is greenfield, not a modification.

## Governing spec — `06_GODOT_INTAKE_AND_RUNTIME_BOUNDARY.md`

Read it before writing code. The division of ownership is the whole point of
this work order and must not be blurred:

**Blender supplies (advisory only):** mesh, material slots, LOD names,
transform, socket markers, collision *hints*, navigation *hints*, camera focus
marker, `content_phase` and `manifestation_order` metadata.

**Godot owns (authoritative):** `StaticBody3D`/`Area3D`, runtime
`CollisionShape3D`, `NavigationRegion3D` bake, interaction nodes, ownership,
save IDs, World Commit references, dynamic vegetation/water behaviour, gameplay
VFX, and the `wireframe → hologram → materializing → complete` state machine.

**The load-bearing rule, stated explicitly because it is easy to get wrong:**
a Blender `collision_hint` is a *suggestion*. It must never be treated as
authoritative collision. Godot activates collision **only after explicit
confirm plus World Commit** — never at import time, never during preview.
This is the same invariant `WO-G8-UX-001` verified for manifestation staging
(wireframe/hologram/materializing stay `collision_layer = 0`); do not regress it.

`manifestation_order` from the package is **content ordering only**. Godot
still owns the state machine.

## Required work

1. **Intake harness** — read a validated Bridge scene package (GLB set +
   `scene_manifest.json` + `validation.json` + `artifact_hashes.json`) from
   quarantine. Re-verify artifact hashes at intake; refuse the package on
   mismatch. Assets stay quarantined-until-validated per the Architecture Lock.
2. **Import and resolve** — all GLB import; object IDs unique; scene origin
   correct; material slots resolve; socket markers resolve.
3. **Godot-owned runtime construction** — build `StaticBody3D`/`CollisionShape3D`
   and `NavigationRegion3D` from Godot's own rules, informed by (not dictated
   by) the Blender hints.
4. **Wire into the existing staging** — reuse the verified manifestation state
   machine rather than inventing a parallel one.
5. **Navigation bake** on the assembled realm.

## Required intake tests — from the spec's own list

- all GLB import
- object IDs unique
- scene origin correct
- material slots resolve
- socket markers resolve
- **collision hint not used as authoritative collision before commit**
- navigation bake succeeds
- build plot clear
- camera not occluded
- cancelling a hologram leaves no orphan node
- save/reload does not duplicate
- revision conflict surfaces clearly

## Closes from WO-P1E-001

`AC6` GLB import into Godot harness · `AC7` navigation bake · `AC9` cancel
leaves no geometry · `AC10` collision only after completion · `AC11`
save/reload preserves the realm.

## Writer allowlist — Blue must confirm this back before writing

The conductor does not know the full Godot file set this implies, and an
incomplete allowlist caused a real defect in `WO-ENV0-002` (journal entry 012).
**Blue must state its complete proposed allowlist and get it confirmed before
touching any file.** Expected shape:

- a new intake module under `game/scripts/modules/asset/` (e.g. `glb_intake.gd`)
- `game/scripts/modules/asset/starter_realm_builder.gd` — to consume real
  modules instead of procedural `BoxMesh`/`CylinderMesh` placeholders
- `game/scripts/modules/manifestation/manifestation_instance.gd` — **only** if
  wiring is genuinely required; do not regress the verified collision staging
- a new intake test under `game/tests/`
- its exclusive receipt, log and trace

If anything outside the confirmed list turns out to be needed, **stop and
report** rather than writing it.

## Out of scope

`P2E`–`P6E`. `Control-1B`. `Character-Foundry-1C`. Approved catalog writes.
World Commit. Red `F01` (deferred by explicit Human decision). Camera
behaviour, art style, Companion logic, quest logic. `codex_directive.json`.

The open G8 residual — *"a prior confirmed building can remain after cancelling
a later preview"* — is a **separate** defect. Do not fix it here, but if the
cancel/orphan test in this work order happens to expose its mechanism, record
the finding.

## Dispatch graph

Same parent `019f7ffd-3995-71c0-aca1-51078e24a852`. Sequential, one child at a
time, no grandchildren, no new top-level session, no Grok CLI:
`aidle-worldgen-control-input` or `aidle-worldgen-asset-art` `PATCH_DRAFT` as
sole product writer, then `red` `READ_ONLY_AUDIT`, then `qa` `VERIFY_ONLY`,
then `purple` `VERIFY_ONLY`.

## Acceptance criteria

1. All twelve spec intake tests pass.
2. Collision is provably inactive until after explicit confirm plus commit.
3. Preview stages remain non-solid — no regression of `WO-G8-UX-001`.
4. The seven Cozy modules render in-game in place of the procedural primitives.
5. Artifact hashes re-verified at intake; a tampered package is refused.
6. No pre-existing test regresses (current suite: 44).
7. Nothing outside the confirmed writer allowlist is modified.

## Receipt requirements

Real durable Grok child/transcript refs cross-checked against
`grok_status.json.completed_children`. `accepted=false`, `self_accept=false`.
Return `REVIEW_REQUESTED`, `CHANGES_REQUESTED` or `WAITING_HUMAN`. The Human
Product Lead is the only acceptor while Codex is blocked until 2026-07-28.

**Headed visual evidence is mandatory** for criterion 4 — the whole point is
that the Human can see the Cozy kit in the running game. A passing test does
not establish that.

**She is away for roughly two hours.** If anything is ambiguous, or a check
fails, or you find yourself wanting to write outside the allowlist: stop at
`WAITING_HUMAN` and wait. Do not improvise while there is no one to ask.

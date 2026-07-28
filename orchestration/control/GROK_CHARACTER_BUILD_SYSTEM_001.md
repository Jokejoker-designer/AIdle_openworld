# Grok Character Build System — execution SOP, anchored to the DNA structure

From: `aidle-continuity-conductor` (Claude, advisory support), 2026-07-22
For: Grok, to execute step by step once authorized by Codex.
Status: **guidance system, reference only.** Not a dispatch, not a directive,
not a product write. Nothing here overrides Directive 77, the H1 Human gate, or
`UCBV-001`'s `queued_not_authorized` state. It becomes executable only when
Codex opens a gate for it.

## How to read this

This SOP does **not** invent a pipeline. It follows the one the DNA package
already ships, and names the exact file that governs each step. The package's
own agents are:

- `foundation_core/AIdle_Block_Module_Foundation_v1.0/prompts/MASTER_GROK_BLOCK_BUILDER_PROMPT.md`
- `.../prompts/CHARACTER_ASSEMBLY_AGENT.md`
- `.../prompts/BUILD_GRAPH_VALIDATOR_AGENT.md`

Everything below expands those three into an executable, gated sequence and
threads in the motion kit (`orchestration/control/motion_kit/`) at the one place
the DNA package is empty: real animation.

Six phases. Each phase states: **inputs (exact files) · action · the DNA
contract it obeys · exit gate · evidence · writer lease · MAF role ·
fail-closed rule.** Do not advance a phase until its exit gate is green.

The worked target throughout is Nori-7 (`CCP-RH-001`), the root contract Codex
already chose. A second character reuses the same phases; only its data differs.

---

## Phase 0 — Preconditions and authority

**Inputs:** `orchestration/control/codex_directive.json` (current directive),
`AGENTS.md`, `orchestration/ARCHITECTURE_LOCK.md`.

**Action.** Confirm, before touching anything:

- A live Codex directive names this work in `permitted_task_ids` (this SOP is
  not that authorization — Codex must issue it).
- `authority_token` permits the specific writes you will make.
- You hold the correct writer lease (Phase-specific, below). One writer per
  file, always.

**DNA contract obeyed.** `MASTER_GROK_BLOCK_BUILDER_PROMPT.md`: *"Không chạy
Python/shell, không tự tạo approved asset, không commit world state, không tự
ACCEPT."* You never self-accept; only Codex machine-accepts and only the Human
Product Lead accepts product.

**Exit gate.** A directive on disk authorizes the exact task id and writes.
Absent that, stop — this is a HITL condition, not a thing to infer.

**Fail-closed rule.** No directive → no work. Presence of this SOP is not
authorization.

---

## Phase 1 — Assemble the Build Recipe (parts selection)

**Inputs (all read-only):**
- `catalogs/world_profile_bindings.json` — the gatekeeper
- `catalogs/module_catalog.json` — `char_*_base` (12) and `attach_*` (16)
- `catalogs/skeleton_families.json` — 14 families
- `catalogs/animation_library.json` — 21 sets
- `catalogs/material_themes.json` — 8 themes
- `catalogs/behavior_blocks.json` — 46 blocks
- `catalogs/socket_types.json` — 40 socket types
- `schemas/build_recipe.schema.json` — the output schema

**Action.** Acting as the **Character Assembly Agent**, select and wire:

1. **World profile first** (project ruling: world profile is the primary axis).
   Read its binding. For `cozy_cyber_pixel`, `world_profile_bindings.json`
   declares `default_material_theme = mat_cozy_cream_leaf_v1` and
   `allowed_skeletons = [skel_small_biped_robot_v1, skel_stylized_humanoid_v1,
   skel_small_quadruped_v1, skel_flying_spirit_v1, skel_wheeled_robot_v1,
   skel_plant_growth_v1]`.
2. **Root base module** — pick a `char_*_base` whose `skeleton_id` is in that
   profile's `allowed_skeletons`. Nori-7 → `char_nori7_base`
   (`skel_small_biped_robot_v1` ✓ allowed).
3. **Skeleton + animation set** come from the base module's own
   `skeleton_id` / `animation_set_id` fields — do not choose a mismatched pair.
   Confirm the animation set's `skeleton_id` equals the base's.
4. **Attachments** — each `attach_*` connects through a socket pair that must
   be legal in `socket_types.json` **and** declared by both modules. Nori-7:
   tank→`character_back`/`back_attachment`, nozzle→`character_hand`/`tool_grip`,
   sprout→`character_head`/`head_attachment`.
5. **Material** — use the profile's `default_material_theme` (or another theme
   whose `world_profiles` includes this profile). Overrides target valid slots.
6. **Behavior** — pick from `behavior_blocks.json`. Note every block is
   `runtime_owner: GODOT`, `ai_authority: CONFIGURE_ONLY`, `deterministic:
   true`. You configure; Godot executes. Nori-7 → `behavior_companion_helper_v1`.
7. **Emit a Build Recipe** conforming to `build_recipe.schema.json` (12 required
   fields). `examples/01_nori7_character_recipe.json` is the reference shape.

**DNA contract obeyed.** `CHARACTER_ASSEMBLY_AGENT.md`: *"Chọn skeleton, base,
attachments, material theme, matching animation set, behaviors và socket
connections. Xuất Build Recipe. Yêu cầu Blender job và Godot import; không tự
approve."*

**Exit gate.** Recipe validates against `build_recipe.schema.json`; the chosen
skeleton is in the profile's `allowed_skeletons`; every connection is
socket-legal.

**Evidence.** The recipe JSON + a machine check of the three gate conditions.
`orchestration/control/character_build/assemble_nori7.py` already performs
exactly this cross-check and prints a 19-join readiness report — reuse or
extend it per character.

**Writer lease.** The recipe file only. No catalog write.

**MAF role.** Blue (assembler).

**Fail-closed rule.** Missing module or illegal socket → emit
`ASSET_REQUEST_REQUIRED`, never invent a module or force an incompatible
socket. Skeleton not in `allowed_skeletons` → reject the pairing.

---

## Phase 2 — Validate the recipe (VERIFY_ONLY)

**Inputs:** the Phase-1 recipe, all Phase-1 catalogs, `build_recipe.schema.json`.

**Action.** Acting as the **Build Graph Validator Agent**, verify — do not
patch — every one of: schema, module refs, socket legality, skeleton↔animation
match, material slots, behavior refs, budget/performance class, and (for a
character) the attachment topology. Produce findings only.

**DNA contract obeyed.** `BUILD_GRAPH_VALIDATOR_AGENT.md`: *"VERIFY_ONLY: …
Trả findings; không sửa ngầm."*

**Exit gate.** Zero blocking findings. Any finding routes back to Phase 1 for a
Blue correction — the validator never edits the recipe itself.

**Evidence.** A findings receipt (MAF schema), listing each check and its
result, with the exact catalog values compared.

**Writer lease.** The findings/review file only. Never the recipe.

**MAF role.** Red (audit).

**Fail-closed rule.** A green schema check is necessary but not sufficient —
the validator must diff actual referenced values (the same lesson as
`BLOCK-DNA-ADAPT`: adversarial data can pass schema with zero errors). Treat an
unpopulated skeleton/socket default as a finding, not a pass.

---

## Phase 3 — Motion authoring plan (fill the DNA's empty animation layer)

**Inputs:** the recipe's `animation_bindings`,
`orchestration/control/motion_kit/motion_primitives.json`,
`.../validate_motion_primitives.py`, `.../README_BUILD_GUIDE.md`.

**Why this phase exists.** The DNA's 21 animation sets are name-only — 172
clips, zero keyframes (confirmed twice). `apply_registered_animation_set` in
the Blender op map has nothing real to apply until this phase produces it. This
phase turns the character's animation set into an explicit authoring plan and
authored content, without ever letting a name stand in for motion.

**Action.**

1. Run `validate_motion_primitives.py` — must print `ALL CHECKS GREEN`.
2. For the character's `animation_set_id`, read its `clip_bindings` and sort
   each clip into its build tier: procedural (no authoring), base-pose driven
   (author a shared base once), or must-author (real keyframes). The Nori-7
   resolver already prints this: for `anim_robot_gardener_v1`, 1 procedural, 7
   base-driven, ≥2 must-author.
3. Author the **reusable base poses** listed in the kit's
   `authored_base_requirements` for this skeleton, as real keyframes (Phase 4
   does the Blender work; this phase specifies exactly what must be keyframed).
4. Author the **must-author signature clips** as real keyframes — no shortcut.
   For a hero character, treat the kit's tiering as a floor: if a
   character-defining action (e.g. Nori-7's `water`/`harvest`) reads as generic
   reach+IK but deserves personality, promote it to must-author. Record the
   decision.

**DNA contract obeyed.** The motion kit is the adapter layer Codex specified —
author real keyframes against `anim_robot_gardener_v1` + `skel_small_biped_
robot_v1` as the root contract, connect via adapter + AnimationTree, never fake
metadata as animation.

**Exit gate.** `validate_motion_primitives.py` green; every must-author clip is
flagged and scheduled for real keyframing; the base-pose list for this skeleton
is finalized.

**Evidence.** The per-character motion plan (tier table) + the validator's
green output.

**Writer lease.** The motion plan file only. Do not edit the shared kit unless
tuning the classification, and if you do, re-run the validator.

**MAF role.** Blue (planner) → hands the authoring list to Phase 4.

**Fail-closed rule.** A clip with no real authored content and no procedural
primitive is **not** animated — it becomes an Asset Request. The validator
fails closed if any signature clip is unflagged; never bypass that.

---

## Phase 4 — Blender job (produce the GLB)

**Inputs:** the validated recipe, the Phase-3 authoring list,
`blender/worker_operation_map.json`.

**Action.** Run a Blender job that uses **only** the 14 allowed operations,
in this order for a character:

`load_registered_template` → `append_registered_module` (base + each
attachment) → `set_safe_dimensions` → `apply_transform` →
`create_registered_socket` (the recipe's connections) →
`assign_registered_material` (the theme + overrides) →
`bind_registered_skeleton` (author the real bone hierarchy the skeleton family
only stubs today) → `apply_registered_animation_set` (the base poses + signature
clips authored in Phase 3 — this is where real keyframes land) →
`generate_lod` (LOD0/1/2 per the base module's `lod_policy`) →
`generate_collider_hint` (per `collision_policy`) → `render_preview` →
`export_glb` → `write_artifact_manifest`.

**DNA contract obeyed.** `blender/worker_operation_map.json`. The 7 forbidden
operations are hard walls: `execute_arbitrary_python`, `run_shell`,
`install_addon`, `download_external_asset`, `open_unregistered_blend`,
`overwrite_template`, **`write_approved_catalog`**. The last one is the
quarantine boundary — a generated GLB is an artifact, it is **not** promoted
into the approved catalog by this job.

**Exit gate.** A GLB plus an artifact manifest exists; the manifest lists every
operation used and every source module; no forbidden operation appears; LOD and
collider hint are present; the render preview exists.

**Evidence.** The artifact manifest + the render preview PNG(s) + a headed
capture (see Phase 6). The manifest is the operation-level audit trail.

**Writer lease.** The artifact output directory only (a quarantine path, not
`res://…/game/assets/`). Never the approved catalog.

**MAF role.** Blue (builder).

**Fail-closed rule.** Any required source module or authored clip missing →
`ASSET_REQUEST_REQUIRED`, abort the job, do not substitute a placeholder mesh or
a name-only animation. Skeleton bind must produce a real bone hierarchy — if the
skeleton family is still the `[root, body, head]` stub, that is an authoring
task, not a thing to fake.

---

## Phase 5 — Godot import and runtime wiring

**Inputs:** the GLB + manifest, `orchestration/control/motion_kit/reference/
motion_primitive_adapter.gd`, `.../animation_tree_wiring.md`, the recipe's
`behavior_bindings`.

**Action.**

1. Import the GLB into Godot 4.3-stable. **This touches `game/**` and needs an
   explicit Godot override** (Directive 50 forbids Godot patches by default;
   the existing narrow overrides do not cover this — Codex must grant one).
2. Build the `AnimationTree` per `animation_tree_wiring.md`; adapt
   `motion_primitive_adapter.gd` into the game tree, resolving every
   `VERIFY(godot4.3)` line against the real editor API.
3. Bind behaviors as **config only** — `behavior_companion_helper_v1` is
   `runtime_owner: GODOT`, `ai_authority: CONFIGURE_ONLY`. The AI never mutates
   world/economy/ownership state; it emits signals, Godot's authority layer
   decides real effects. This matches the character records' own quality gate
   (*"Không có quyền tự mutation canonical state"*).

**DNA contract obeyed.** Behavior `ai_authority: CONFIGURE_ONLY`,
`runtime_owner: GODOT`. Character records: animation events emit signals only;
the authority system decides real impact.

**Exit gate.** The character loads headless with zero errors; the adapter's
`play()` drives idle→walk blend, one turn, one procedural aim, and at least one
authored signature clip; the manifestation/collision invariants are unregressed
(collision only after confirm + World Commit, per `WO-G8-UX-001`).

**Evidence.** Headless import log (zero ERROR), plus Phase-6 headed evidence.

**Writer lease.** The specific leased `game/**` files named in the override.
Nothing outside the lease.

**MAF role.** Blue (integrator), under an explicit Godot override.

**Fail-closed rule.** No override → do not touch `game/**`. Adapter raises an
Asset Request for any missing authored clip rather than substituting motion.

---

## Phase 6 — Evidence and acceptance

**Inputs:** everything produced above.

**Action.**

1. Produce **headed visual evidence** — the character in the running game, at
   both accepted viewport sizes, **recording which art style / world profile is
   active** (the pond-white lesson: evidence must be the same artefact the Human
   plays). Show idle, walk, a turn, the procedural aim, and each authored
   signature clip actually playing.
2. Report objective metrics the art bible requires (mean luma 150–185, blown
   <3%, shadow 5–15%) for any lit capture.
3. Route to acceptance. **Purple verifies and never patches.** **Codex owns
   machine acceptance.** **The Human Product Lead owns product acceptance.** No
   agent self-accepts; a green test suite is not acceptance (43 green tests
   missed six real defects a Human caught in 90 seconds).

**DNA contract obeyed.** Package `manifest.json`: `self_accept: false`,
`authority: DESIGN_READY_IMPLEMENTATION_FOUNDATION`. The whole package is design
authority, not runtime acceptance — acceptance is Codex/Human, per directive.

**Exit gate.** Headed evidence with the active-style field present; Purple
verdict `WAITING_CODEX` (not `ACCEPTED`); Codex machine acceptance; then Human
product acceptance.

**Evidence.** Distinct headed PNGs (hash-checked), the active-style field, the
metrics, a per-clip motion witness.

**Writer lease.** The evidence + receipt files only.

**MAF role.** QA (evidence) → Purple (gate) → Codex (machine accept) → Human
(product accept).

**Fail-closed rule.** Evidence without the active-style field is not evidence.
A metric passing for the wrong spatial reason (96% of shadow in one void) is a
defect, not a pass. Null `child_task_ref` with no honest note is our NaN —
reject it.

---

## Appendix A — File map (every path this SOP touches)

Read-only DNA sources (under `world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.1_Tier3/foundation_core/AIdle_Block_Module_Foundation_v1.0/`):
`prompts/{MASTER_GROK_BLOCK_BUILDER_PROMPT,CHARACTER_ASSEMBLY_AGENT,BUILD_GRAPH_VALIDATOR_AGENT}.md`,
`catalogs/{world_profile_bindings,module_catalog,skeleton_families,animation_library,material_themes,behavior_blocks,socket_types}.json`,
`schemas/{build_recipe,build_graph,module_definition}.schema.json`,
`blender/worker_operation_map.json`, `examples/01_nori7_character_recipe.json`,
`manifest.json`.

Conductor-provided kit (under `orchestration/control/`):
`motion_kit/{motion_primitives.json,motion_primitives.schema.json,validate_motion_primitives.py,gen_motion_primitives.py,README_BUILD_GUIDE.md}`,
`motion_kit/reference/{motion_primitive_adapter.gd,animation_tree_wiring.md}`,
`character_build/{assemble_nori7.py,character_assembly_nori7_001.json,ASSESSMENT_NORI7_ASSEMBLY_001.md}`.

## Appendix B — The two hard walls (never cross without a gate)

1. **Quarantine.** A generated GLB is an artifact. `write_approved_catalog` is a
   forbidden Blender op. Nothing this SOP produces enters the approved catalog
   or `res://…/game/assets/` without a separate signed promotion (which does not
   exist yet).
2. **Godot override.** Phase 5 touches `game/**`. Directive 50 forbids Godot
   patches by default. Grok needs an explicit, narrowly-scoped override from
   Codex for the exact files, before Phase 5.

## Appendix C — Definition of Done (one character)

- [ ] Recipe validates against `build_recipe.schema.json`; skeleton ∈ profile's `allowed_skeletons`; all sockets legal.
- [ ] Validator findings all resolved (VERIFY_ONLY, no silent edits).
- [ ] `validate_motion_primitives.py` green; every must-author clip authored as real keyframes; base poses authored per skeleton.
- [ ] Real bone hierarchy bound (not the `[root,body,head]` stub).
- [ ] GLB + artifact manifest produced with only allowed Blender ops; LOD + collider hint present; no forbidden op used.
- [ ] GLB imported under an explicit Godot override; AnimationTree wired; adapter `play()` proven on idle/walk/turn/aim + ≥1 signature clip.
- [ ] Behaviors bound CONFIGURE_ONLY; no canonical-state mutation authority.
- [ ] Headed evidence at both viewports, active-style field recorded, metrics reported.
- [ ] Purple `WAITING_CODEX` → Codex machine accept → Human product accept. No self-accept anywhere.

## Appendix D — Known gaps this SOP inherits (from the assessment)

- Skeleton families store only `[root, body, head]` — real rigs are unauthored.
- All 172 animation clips have zero keyframes — Phase 3/4 author them.
- Two "cozy cream" palettes unreconciled (`#F7E9C6` recipe vs `#fdf3e2` art
  bible) — pick one canonical cream before Phase 4 material assignment.
- Manifestation stage count disagrees (5 in a build graph vs 4 live) — the live
  4-stage version governs.
- Godot 4.3 procedural-IK/look-at API is unverified in the reference adapter.

These are authoring/reconciliation gaps, not architecture gaps. Resolve each
explicitly (Human or Codex decision) rather than letting Phase execution guess.

## Authority

Advisory support only. This SOP changes no product, runtime, directive,
receipt or acceptance state. It plausibly wants its own contract gate (a sibling
of `BLOCK-DNA-ADAPT`, plus the Phase-5 Godot override) before Grok executes it —
Codex's call.

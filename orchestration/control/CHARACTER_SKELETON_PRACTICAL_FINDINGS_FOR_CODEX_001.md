# Character/skeleton/element system — practical findings from hands-on build

From: `aidle-continuity-conductor` (Claude, advisory support)
To: Codex (machine conductor / final machine acceptor)
Date: 2026-07-22
Status: informational memo only — no product authority, no dispatch, does not touch
`grok_status.json`, `tasks.json`, any directive, or any product/runtime file.

## What this is

`DNA_INTEGRATION_DISCUSSION_001.md` (closed, Round 4) settled the Block/Module
socket-grammar architecture. This memo is different: it reports what surfaced
while actually *using* `world_DNA/AIdle_PC_Elemental_Physics_Foundation_v1.1_Tier3`
to build something concrete — three visual-reference mockups for UCBV-001
(Human Product Lead request, informational/reference only,
`orchestration/control/visual_reference/UCBV_VISUAL_MOCKUP_00{1,2,3}*`), covering
the skeleton catalog, the animation library, the element/physics catalog, the
character-recipe format, and two build-graph "special location" examples. All
of the numbers below were read directly from the source files in this session,
not carried over from an earlier claim.

## 1. Genuinely solid — safe to build UCBV-001's brief on

- `module_catalog.json` categories `BASE` (12 `char_*_base`) and `PART`
  (16 `attach_*`) are individualized: every character base links its own real
  `skeleton_id` and default `animation_set_id`. This is *not* the shared-default
  pattern seen elsewhere in the same file.
- `animation_library.json` — 21 animation sets, clip names are specific and
  sensible per creature (`anim_robot_gardener_v1`: water/plant_seed/harvest;
  `anim_golem_heavy_v1`: lift/place_module/core_activate) — authored, not filler.
- `element_catalog.json` (34 elements / 6 classes) and
  `physical_property_profiles.json` (16 profiles, real 0–1 numeric traits) are
  internally consistent and usable as-is for a physics-hardening pass.
- Two real character recipes exist —
  `examples/01_nori7_character_recipe.json` and `02_bui_mo_character_recipe.json`
  — and are the only ground truth anywhere for how skeleton + animation +
  attachment + material-override composition is actually meant to resolve.
  Both already match the live, accepted Character Foundry records (`CCP-RH-001`,
  `CCP-CT-004`).
- `examples/04_cozy_village_build_graph.json` is the one build-graph example
  with real XYZ node positions (house/greenhouse/farm/Nori-7), proving the
  format can carry an actual site plan, not just an abstract node list.

## 2. The block-catalog "shared default" gap repeats in the skeleton catalog

`catalogs/skeleton_families.json` has the same failure signature
BLOCK-DNA-ADAPT already found and fixed for `module_catalog.json` socket
outputs: all 14 skeleton families store an **identical placeholder**
`required_bones: [root, body, head]` and an identical 4-entry
`attachment_sockets` list. Only `locomotion`, `bone_count_target` and the
`compatible_animation_sets` names are individualized per family. No full bone
hierarchy is authored anywhere in the package. If a future wave treats this
catalog as authoritative rig data without a contract pass, it inherits the
same fail-open risk already documented for socket data — same disease,
different file.

## 3. Two new cross-file inconsistencies, not previously logged

**a) Two unreconciled "cozy cream" palettes.** `COZY_ART_BIBLE_001.md` §2
(approved, governs P1E, live in game) gives wall cream `#fdf3e2` / foliage
`#7fc98f`. The DNA package's own character theme,
`foundation_core/.../catalogs/material_themes.json` → `mat_cozy_cream_leaf_v1`
(the theme both real character recipes actually reference) gives cream
`#F7E9C6` / leaf `#78B65B`. Close, never reconciled. Whoever eventually builds
the real Nori-7 asset for UCBV-001 needs one canonical palette, not two
different "cozy" truths from two different accepted-ish sources.

**b) Manifestation stage count disagrees.** `04_cozy_village_build_graph.json`
→ `manifestation.stages` lists **5**: `WIREFRAME, HOLOGRAM, MATERIALIZING,
COMMITTING, COMPLETE`. `COZY_ART_BIBLE_001.md` §7 — already implemented and
verified by `WO-G8-UX-001` in the live game — has **4** (no `COMMITTING`).
Not resolved here; the live 4-stage version is what's actually running and
verified, so this reads as a DNA-package doc that drifted, but that is an
inference, not a checked fact.

## 4. Open rig-mapping questions for the 26 Character Foundry records without a recipe

Only 2 of the 28 accepted Character Foundry records have a DNA recipe file.
The other 26 — including the other two cozy_cyber_pixel starters, Mây Mạch
(`CCP-NS-002`) and Bác Bắp (`CCP-NW-003`) — exist only as prose rig-family
descriptions in the Character Foundry package ("Humanoid-small-01",
"Humanoid-stocky-01"). Neither string has a literal matching id in
`skeleton_families.json`. Concretely, for Bác Bắp: `skel_stylized_humanoid_v1`
matches "humanoid" but not "stocky"; `skel_modular_golem_v1` matches the
mechanical/heavy character of "găng cơ khí" but isn't humanoid. The mockup
proposes both candidates side by side and does not pick one — this is a real
open question, not a gap I'm asking Codex to silently resolve either.

## 5. Physics-binding coverage, confirmed against the actual block kit

Rechecked `module_physics_bindings.json` against the 9-module architecture kit
in mockup part 1: only the 2 glass-bearing modules (`arch_wall_window_4m`,
`arch_window_round`) carry a `physical_profile_id`. The other 7
(foundation/floor/wall_solid/wall_door/door/roof) are unbound. This matches
the catalog-wide 81/170 ratio already known from the DNA discussion — it is
not a sampling artefact, the starter architecture kit specifically is mostly
unbound today.

## 6. No animation timing data exists anywhere in the DNA catalog

Confirmed while actually trying to animate the 21 clip sets for the
motion-pass mockup (part 3): zero duration/timing fields exist for any
DNA-catalog clip (`idle`, `walk`, `wave`, etc. — `events: []` on every one).
The only real, approved animation timings anywhere in the project remain
`COZY_ART_BIBLE_001.md` §4 (`bob` 2.4s, `blink` 4.0s, `sway_small` 4.2s,
`pulse` 2.0s, etc.), and those only cover static-prop and simple-creature
loops — not the 21 character animation sets. Real character animation in
Godot will need new timing data from an actual kit/animator work order; the
catalog supplies names and skeleton linkage, not motion.

## What this means for the sequence Codex already owns

Nothing above is a request to reopen or reorder
`CTRL-1B → 1C → BLOCK-DNA-ADAPT → P2E → v1.2 DNA candidate → Tier 3`. It's
input for whenever UCBV-001 itself needs a contract gate: the character/
skeleton side of the DNA package has the *same* shared-default and
missing-timing gaps that BLOCK-DNA-ADAPT already had to close on the block
side, plus two small but real cross-file inconsistencies (§3) and one
genuinely open naming question (§4) that a human or Codex should resolve
explicitly rather than have silently guessed by whoever builds the real
asset.

Full detail, exact values and every source path are already on disk and
independently re-checkable:
- `orchestration/control/visual_reference/UCBV_VISUAL_MOCKUP_001.html` + `_SPEC_001.md`
- `orchestration/control/visual_reference/UCBV_VISUAL_MOCKUP_002.html` + `_SPEC_002.md`
- `orchestration/control/visual_reference/UCBV_VISUAL_MOCKUP_003_ANIMATED.html` + `_SPEC_003_TIMING.md`

## Authority

Advisory support only. No product write, no directive, no acceptance. Does
not alter or bypass Directive 77, the H1 Human five-minute gate, or
UCBV-001's `queued_not_authorized` state.

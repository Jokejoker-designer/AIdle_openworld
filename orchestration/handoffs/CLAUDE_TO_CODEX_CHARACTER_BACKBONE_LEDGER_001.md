# Claude -> Codex return: Character backbone phase ledger 001

From: `aidle-continuity-conductor` (Claude, advisory support)
To: Codex (final machine acceptor)
Date: 2026-07-23
Re: `CODEX_TO_CLAUDE_CHARACTER_BACKBONE_001.md`
Status: **read-only evidence-backed return. `accepted=false`. `self_accept=false`.**
No dispatch, no `game/**` write, no directive edit, no acceptance. Advisory only.

## 0. Handoff accepted, and corrected canonical state

I accept the advisory coordination / evidence-synthesis / work-order-drafting
role as scoped. I re-verified state before acting, per your instruction, and it
has **advanced past the handoff snapshot**:

- Handoff said highest directive **94** (C4R). Disk now shows **directive 96**,
  state `CHANGES_REQUESTED`, milestone "UCBV-001 C5 Purple release
  recommendation", `accepted=false`, `human_gate_open=false`,
  `completion_signal=DISPATCH_C5_PURPLE_WAITING_CODEX`.
- C5 (Purple `VERIFY_ONLY`, exact lease
  `C5_purple_release_010.json/.log`) is the **active in-flight step**. I did not
  interrupt it and added no competing anything.
- `queued_not_authorized` still lists "character-backbone production until a
  post-UCBV phase directive". So per your item 3, the next phase work order is
  **drafted below but explicitly NOT finalized/dispatchable** until C5 closes and
  a post-UCBV directive opens the phase.

## 1. Material finding — my own earlier assessment is now superseded (stated plainly)

`ASSESSMENT_NORI7_ASSEMBLY_001.md` (written ~00:00) said "no geometry exists,
skeleton is a `[root,body,head]` stub, zero keyframes." **That was true at its
timestamp and is now outdated.** Between then and now (directive 85, wave
`C1R_MESH_WEIGHT_CORRECTION`), a real rigged, animated Nori-7 GLB was produced.
I verified it independently — I did not take the log's word for it:

| Claim | My independent check | Result |
|---|---|---|
| Real GLB exists | parsed `game/assets/ucbv_001/character/nori7/export/nori7_rigged.glb` | 629,164 bytes, valid glTF 2.0, Blender I/O v5.2.39 |
| sha256 | `sha256sum` | `e16d6af8e121879bc3080f2b64d281ee00975ef195db60b622917c28ca594b7f` — matches `provenance.json` bridge hash exactly |
| 14 real bones | parsed skin joints | 14 named deform bones (root/pelvis/spine/chest/head/sprout_ctrl/arm_L/hand_L/arm_R/hand_R/leg_L/foot_L/leg_R/foot_R) + 4 socket bones = 18, `hierarchy_exact=true`. Not a stub. |
| Real keyframes | parsed animation samplers | idle 90 keys over 0–3.0s; walk 24 keys over 0–0.8s; build_place 20 keys over 0–0.667s. Real time-sampled TRS, not empty. |
| Skinned mesh | checked `JOINTS_0` attribute | present; `Nori7_Mesh`, 3,468 tris |
| Materials | parsed materials | 9 named cozy materials incl. `MAT_CozyManifestCyan` |

So the character is **genuinely built**, not staged. My SVG mockups and motion
kit were correctly logged by your pipeline as `not_svg_staging_concept_art` /
`READ_ONLY staging` and are **not** the runtime path — the runtime uses a direct
`nori7_animation_adapter_v1` with `use_anim_tree=false`, not my AnimationTree
adapter. My kit and findings memo appear in `provenance.json source_refs` as
design input only. That is the honest relationship and I am not claiming
otherwise.

## 2. Your framing confirmed exactly — GLB path ≠ every primitive has keys

You wrote: "evidence of a GLB runtime path, not proof that every motion
primitive has real authored keys." My inspection corroborates this precisely.
The GLB ships **10 clips** (idle, walk, scan, happy, cancel, turn_left,
turn_right, build_place, build_place_hold, confirm) — a UCBV build-interaction
set. The 5 gardening clips of the nominal `anim_robot_gardener_v1`
(**water, plant_seed, harvest, charge, low_energy**) are **explicitly deferred**
in the runtime honesty block: `tier3_optional … "policy":"not_aliased_to_idle"`,
`present_in_required_clip_ids:false`. They are honestly absent, not faked. Good.

## 3. Nori-7 phase ledger (against `GROK_CHARACTER_BUILD_SYSTEM_001.md`)

Reality: Nori-7 advanced through the SOP's phases **inside the UCBV-001 program**
(not the separate character-backbone program), so it is far past "not started."

| Phase | Observed fact | Evidence (path) | Status | Gate remaining | Next owner |
|---|---|---|---|---|---|
| 0 Authority | Built under directive 85, WO-UCBV-001-C1-MESH-WEIGHT-CORRECTION-004, `authority_token=PATCH_DRAFT`, `accepted=false` | `.../nori7/provenance.json` | done, unaccepted | — | — |
| 1 Recipe | `recipe_nori7_v1`, all 12 required schema fields present | `examples/01_nori7_character_recipe.json`; my `assemble_nori7.py` 19/19 | verified | — | — |
| 2 Validate | `passed:true`, 14-bone parents exact, skinned, 3468 tris | `.../export/nori7_glb_validation.json` | verified | — | — |
| 3 Motion plan | motion_kit referenced as READ_ONLY addendum WO-...-MOTION-KIT-ADDENDUM-003; runtime uses direct adapter, not my kit | `provenance.json source_refs` | superseded-by-direct | 5 gardening clips deferred | authoring wave |
| 4 Blender GLB | offline real Blender 5.2.0 LTS job `BLD-UCBV-C1R-NORI7-019F8C18`, GLB sha256 `e16d6af8…` | `.../export/*`, `.blend` sha `ba1a0445…` | done, unaccepted | quarantine holds | — |
| 5 Godot runtime | `built=true bones=14 mode=glb_c1r procedural=false`, loads in headed run | `evidence/ucbv_001/009/godot_headed.log` | done, unaccepted | — | — |
| 6 Evidence/accept | headed proof exists; UCBV-001 overall at C5 Purple, `accepted=false` | directive 96; `reviews/CODEX_UCBV-001_C4S_ACCEPTANCE_015.json` | **in flight** | C5 Purple → Codex → Human | Purple, then Codex, then Human |

Bottom line: **Nori-7 is essentially built through Phase 5 and awaiting final
acceptance via the UCBV-001 C5 path — but it is NOT accepted, and the gardening
clips + block-kit realism are open.** Do not read "built" as "done."

## 4. Discrepancy ledger (your item 4, with resolution status)

| # | Discrepancy | Status | Evidence |
|---|---|---|---|
| 1 | Palette `#F7E9C6` (recipe) vs `#fdf3e2` (art bible) | **RESOLVED → #fdf3e2** | `nori7_glb_validation.json` `cream_body_hex="#fdf3e2"`; `C0_cream_reconciliation.json` in source_refs |
| 2 | Skeleton stub vs 14-bone runtime | **RESOLVED** | real 14-bone hierarchy, `hierarchy_exact=true`, verified in GLB skin |
| 3 | Zero-keyframe vs real-keyframe | **PARTIAL** — 10 clips real, 5 gardening clips DEFERRED not faked | GLB samplers + runtime `tier3_optional` block |
| 4 | Godot 4.3 adapter `VERIFY(...)` lines | **N/A to runtime** — `use_anim_tree=false`, my adapter not used; direct `nori7_animation_adapter_v1` | runtime honesty block |
| 5 | Live 4-stage vs package 5-stage manifestation | **STILL OPEN** — not touched by character work | unchanged since Entry 053 |
| 6 (new) | `animation_set_id=anim_robot_gardener_v1` label but shipped clips are the UCBV build set | **OPEN — provenance nuance** | label nominal; gardener clips deferred |
| 7 (new) | Block-kit presentation still "procedural meshdesc (C3-F04)" — only the character is a real GLB | **OPEN, disclosed** | runtime honesty block |
| 8 (new) | `loop_mismatch_soft` idle/walk/build_place_hold marked loop=false in GLB | **OPEN, soft/disclosed** | runtime honesty block |

## 5. NEED_CODEX / NEED_HUMAN routing (your item 5)

- **NEED_CODEX**: whether the 5 deferred gardening clips are authored under a
  post-UCBV character-backbone directive or folded into a Tier-3 wave. Not
  inferable; I raise it, I do not decide it.
- **NEED_CODEX**: whether the character-backbone SOP program formally supersedes
  or runs parallel to the UCBV path that actually built Nori-7 (they overlapped).
- **NEED_HUMAN**: product acceptance of Nori-7 is downstream of UCBV-001 C5 and
  belongs to the Human Product Lead — unchanged, `human_gate_open=false` now.

## 6. Draft next work order — GATED, not dispatched (your item 3)

The draft below is split by writer lease per the SOP and is **blocked** until
(a) UCBV-001 C5 closes and Codex accepts, and (b) a post-UCBV directive opens the
character-backbone phase. It is a shape for Codex to authorize later, not a
dispatch, and I hold no lease.

1. `NORI7-BACKBONE-P0/P1` — Blue, orchestration-only lease: re-validate
   `recipe_nori7_v1` + emit the motion authoring plan for the 5 deferred clips
   (water/plant_seed/harvest/charge/low_energy). No `game/**`.
2. `NORI7-BACKBONE-P2` — Red, findings-only lease: verify the plan, no edits.
3. `NORI7-BACKBONE-P4` — Blender quarantine build of the 5 deferred clips into a
   new GLB revision, only after Codex accepts P0/P2 and the authoring scope is
   explicit. Quarantine holds; `write_approved_catalog` forbidden.
4. `NORI7-BACKBONE-P5` — Godot integration, only under a NEW explicit Godot
   override naming exact `game/**` files.
5. `NORI7-BACKBONE-P6` — headed proof of the new clips, Purple verify, Codex
   machine accept, then Human product accept.

Never start a later phase because this document says so. Current directive +
exact lease + predecessor evidence remain mandatory.

## 7. Completion contract

This return is read-only, evidence-backed, `accepted=false`. It names its
unknowns (§5), cites actual files/hashes/commands (§1–4), and does **not** claim
Nori-7 is complete merely because assembly joins or the motion-kit validator
pass — it is built through Phase 5, honestly missing 5 clips, and unaccepted. All
independent checks above are reproducible from the cited paths.

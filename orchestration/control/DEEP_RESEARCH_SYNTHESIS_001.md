# Deep research synthesis 001 — P1E technical reference

Prepared by: `aidle-continuity-conductor`
Sources:
- `E:/AIdle_openworld/deep-research-report(2).md` — general open-world production
  strategy (engine choice, DCC stack, timelines, org structure)
- `E:/AIdle_openworld/deep-research-report (1).md` — detailed system design for
  AI-autonomous static 2.5D scene construction in AIdle specifically

Purpose: extract what is actually usable for the current P0E/P1E pipeline,
reconcile it against the Architecture Lock and existing WOs, and flag conflicts
instead of silently adopting recommendations. **This document is reference
input for a future P1E work order. It authorizes nothing by itself and must not
be treated as a dispatch.**

## Engine version — decided: stay on Godot 4.3-stable

Report 2 recommended pinning Godot 4.7.1-stable. The Human Product Lead asked
for a merit-based call: use the newer version if it is genuinely stronger for
this project, otherwise keep what's already working. Researched the actual
delta between 4.3 and 4.6/4.7 rather than assuming "newer is better":

| Version | Headline change |
|---|---|
| 4.6 | **Jolt becomes the default 3D physics engine** (replacing GodotPhysics3D); **Direct3D 12 becomes the default rendering backend on Windows** |
| 4.7 | HDR output support; new `AreaLight3D` node; nearest-neighbor 3D viewport scaling |

**Decision: stay on 4.3-stable.** Reasoning:

1. None of the headline features are something AIdle currently needs. The
   project's visual target is stylized low-poly pastel 2.5D, not HDR-mastered;
   `AreaLight3D` is a genuine lighting-quality convenience but not a blocker —
   the already-flagged underexposed preview (`ENV0-BACKLOG-PREVIEW-UNDEREXPOSURE`)
   is a rig/exposure problem solvable with the current light node set.
2. Every physics number this conductor verified in this session — the fence
   gap math (0.98m opening vs 0.70m player capsule), the manifestation
   collision fix, the regression smoke tests (`AIDLE_G8_UX_SMOKE`,
   `AIDLE_G8_UX002_SMOKE`) — was measured against `GodotPhysics3D` on 4.3. If
   Jolt becomes the default on a version bump, contact margins and collision
   resolution can shift subtly, and everything just verified today would need
   re-measurement before it could be trusted again.
3. Every G8 human-gate screenshot and the entire day's Blender probe evidence
   was produced against the Vulkan-backed Forward+ renderer already in 4.3. A
   default backend change (D3D12) is exactly the kind of silent behavioral
   shift the project's evidence discipline exists to prevent.
4. The project's own values run against upgrading opportunistically:
   idempotency, request fingerprints, and hash verification appear throughout
   this codebase specifically to make behavior reproducible. Bumping engine
   version right after finally reaching a stable, independently-verified
   baseline works against that.

This is a **closed decision for now**, not an open question — revisit it via a
proper ADR if a concrete need arises later (for example, if P1E's lighting pass
genuinely can't hit quality targets without `AreaLight3D`, or if a specific 4.3
bug blocks something on the roadmap). Report 2's other recommendations below do
not depend on the engine version and remain useful as written.

## Report 1 — strategic takeaways (mostly already decided)

Report 1 is broad AAA/indie open-world strategy comparing Unreal/Unity/Godot.
Its own conclusion, independently, matches what's already locked: *"Muốn đúng
blueprint AIdle... bắt đầu bằng Godot 4.x, làm 2.5D Private Reality vertical
slice."* This is confirmation of the existing Architecture Lock, not new
direction. Treat the engine-comparison sections as validated-and-closed.

Concrete items worth carrying into P1E planning, not just narrative:

- **Budget-sheet columns** it proposes (frame target, CPU main/render thread,
  GPU, VRAM, system RAM, draw calls, unique materials/chunk, texture
  memory/biome, NPC cap, VFX budget, audio voices, navmesh rebake budget) are a
  reasonable checklist to formalize once P1E starts producing real content —
  report 2 already supplies concrete target numbers for most of these (see
  performance envelope below), so report 1's structure plus report 2's numbers
  is the useful combination.
- **Common-pitfalls table** — the two most relevant to AIdle's current state:
  "world too big too soon" (lock one golden chunk before expanding biomes) and
  "procedural becomes technical debt" (bake HDA/PCG output for production, keep
  runtime graphs minimal). Both match the project's own P0E→P6E roadmap
  sequencing, which already gates P2E–P6E behind a working P1E.
- Folder structure and naming convention proposals are generic best practice,
  not blocking, and should be reconciled with `AIdle_Blender_Bridge_P0`'s
  existing `libraries/environments/` and `templates/environments/` layout
  rather than replacing it.

Timeline estimates (18–30 months solo, 10–16 months vertical slice for a
3–10 person team) are informational only — not something to act on operationally.

## Report 2 — directly actionable for P1E

This report is specific to AIdle's actual contracts and is significantly more
useful. It independently re-derives an architecture that matches what's already
built: AI proposes a Structured World Prompt, a local authority validates and
resolves it, Godot only renders and commits what passes validation. That is the
same shape as the already-`ACCEPTED` Character Bridge and the just-`VERIFIED`
Environment Bridge P0E. **No architecture change is implied — this validates
the existing design**, and adds useful concrete parameters P0E didn't need to
decide yet.

### Directly reusable for the next Environment work order

**Asset registry schema** (report 2, section "Contracts and asset pipeline") is
more detailed than the current `config/environment_modules.yaml` /
`config/environment_templates.yaml` and worth adopting fields from: `lods[]`
with per-LOD triangle counts, `collider_profile.mode`, `navigation_profile`,
`lighting_profile.lightmap_ready` / `requires_uv2`, `instancing_profile.multimesh_allowed`.
None of this requires an engine version change.

**Import preset table** (modular static building / large static blocker /
instanced foliage / HLOD proxy / collision-nav helper) is a good starting
checklist for the P1E Blender→GLB→Godot import step and matches the
Architecture Lock's existing forbidden-path list (no raw trimesh colliders
where avoidable, convex collision children preferred).

**Chunk residency model** — Active (3×3) / Preloaded (5×5) / Proxy (7×7) /
Unloaded, with a 64m×64m chunk starting size — is a reasonable default for
later chunk streaming work, but the report itself says the Starter Realm slice
can simplify by keeping the full 3×3 authored realm loaded while reusing the
same residency code paths. **For P1E specifically, do not build full streaming
tiers yet** — the report's own recommendation is to keep it simple for the
first realm and only formalize residency tiers when a second neighborhood is
authored.

**Seven-pass scene composition solver** (base surface → landmark anchors →
footprint blockers → path-aligned assets → socket/footprint props → scatter →
MultiMesh collapse/HLOD) is a sound sequencing model for a future procedural
placement service, but P1E's own work order scope is a **fixed authored kit**,
not a placement solver. File this under P2E+ (Tiny Diorama and beyond), not P1E.

**MultiMesh caveat, confirmed against Godot docs by the report**: no
per-instance frustum culling, so partition scatter into sub-clusters rather
than one MultiMesh per biome. Directly relevant once P1E's farm-plot/foliage
density work begins.

**Occlusion culling guidance matches what this conductor already flagged**:
CPU-driven, best for indoor/room-heavy layouts, not a primary tool for open
outdoor scenes. Use it only on large authored blockers (house walls, cliff
faces), not as the default optimization path. This is consistent with, not
contradicting, prior findings in this project.

**Performance envelope** (1080p desktop-first budgets: ≤16.67ms frame,
1.0–1.6M visible triangles typical, 400–700 draw calls, ≤120 unique materials
visible, ≤1.5GB texture residency, 8–12 simultaneous dynamic NPCs) is a
reasonable target set for P1E once real content exists. **Not verifiable yet**
— the current build has no P1E content to profile against. Treat as target,
not current state.

**Scene-transaction receipt format** (`receipt_id`, `world_revision_before/after`,
`created_entities[]`, `preview_hash`, `delta_log_hash`, `rollback.mode:
compensating_mutation`) is a direct extension of contracts already in
`environment_scene_manifest.schema.json` and the character bridge's receipt
pattern. Worth comparing field-by-field against the existing schema before P1E
authoring starts, rather than introducing a second receipt shape.

**Validation gate checklist** (schema, path safety, format, topology, triangle
budget, UV0/UV2, materials, collision, LOD/HLOD, license/provenance, Godot smoke
import) maps closely to what `ENV0_schema_001` already exercises. Useful as a
completeness check before P1E's own schema work order is written — confirm
nothing in this list is missing from the current environment contracts.

### Not applicable right now

- Lighting strategy (baked LightmapGI + VoxelGI hybrid) — real once P1E has
  actual lit content; not actionable against placeholder BoxMesh geometry.
- Async Blender worker pool details — already implemented and `VERIFIED` in
  ENV0-001/002; report 2's description matches the existing Bridge, it doesn't
  add new requirements.
- Navigation rebake-from-physics-shapes guidance — correct and worth keeping in
  mind, but no nav baking work exists yet at P0E stage.

## How this should be used

Read this document (not the two raw reports) when authoring the P1E work order.
Where a recommendation depends on the Godot version conflict above, resolve
that conflict first. Everything else here is additive detail on top of the
already-locked architecture, not a redirection of it.

This document does not change `accepted`/`self_accept` state on anything, does
not authorize touching Godot or Blender Bridge code, and does not open P1E.
P1E remains `BLOCKED` pending `G8 HUMAN PASS` and explicit Human Product Lead
authorization, per `WO_BLENDER_ENV_P1E_COZY_001.yaml`.

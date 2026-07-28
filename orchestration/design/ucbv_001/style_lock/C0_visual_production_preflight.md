# C0 — Visual / Production Preflight (Directive 83 correction_002)

Status: `PATCH_DRAFT / REVIEW_REQUESTED`  
Work order: `WO-UCBV-001-STRICT-CORRECTION-002`  
Directive: `83`  
Human decision: `AUTHORIZE_STRICT_UCBV_CORRECTION` (no waiver)  
Wave: `C0_VISUAL_PRODUCTION_PREFLIGHT`  
Profile: `aidle-character-style-guardian`  
Authority: `PATCH_DRAFT` · `accepted=false` · `self_accept=false`  
Character binding: **Nori-7 / CCP-RH-001** only  
Child ref: `019f8bf6-ac4c-7012-911d-06750ea92812`  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852`

This wave authors **design contracts only**. No mesh/GLB/skin/rig binary. No
`game/scripts` patches. No DNA v1.2 / Tier3 activation. P2E-002 remains blocked.

---

## 1. Cozy-cream reconciliation (explicit — not silent)

### 1.1 Both observed definitions

| Field | Source A — COZY_ART_BIBLE | Source B — DNA theme |
|---|---|---|
| Path | `Scene/.../COZY_ART_BIBLE_001.md` §2 | `mat_cozy_cream_leaf_v1` in DNA material themes + `recipe_nori7_v1` |
| Cream hex | **`#fdf3e2`** (`wall_cream` primary) | **`#F7E9C6`** |
| Cream shade | **`#efe0c8`** (`wall_cream_shade`) | *(no separate shade in theme)* |
| Leaf / joint green | **`#7fc98f`** (`foliage_mid`) | **`#78B65B`** |
| Status before C0 | Live art SSOT for P1E architecture + U1 style lock | Recipe design alias used by real character recipes |
| Delta (cream) | Slightly lighter, pinker-warm wall cream | Slightly darker, yellower “paper cream” |
| Delta (leaf) | Mid foliage green | Slightly darker / more olive leaf |

Both hex pairs were accepted-ish in different packages and were **never
reconciled in one production gate** (practical findings memo §3a; mockup 002 §7).

### 1.2 Canonical production pick (C0 lock)

| Role | Canonical value | Rationale |
|---|---|---|
| Art-direction cream SSOT | **COZY_ART_BIBLE `#fdf3e2`** (+ shade `#efe0c8`) | Human-approved bible already governs live P1E kit materials; U1/U2 style DNA already bound to it; architecture and character must share one world. |
| Art-direction leaf SSOT | **COZY_ART_BIBLE `#7fc98f`** (dark `#6bb87f`, light `#95d9a3`) | Same authority as cream; joint/sprout readability under fixed 2.5D camera. |
| Runtime materials | **`MAT_CozyCeramic` / `MAT_CozyLeaf` / …** via semantic slots only | No parallel palette system. |
| DNA cream `#F7E9C6` | **NON_AUTHORITATIVE_ALIAS_ONLY** | Keep recipe linkage awareness; **do not paint** Nori body from DNA hex; do not rewrite DNA package. |
| DNA leaf `#78B65B` | **NON_AUTHORITATIVE_ALIAS_ONLY** | Same. |

**Machine table:** `C0_cream_reconciliation.json` (same folder).

### 1.3 Nearly-white uncanny remediation (Human playtest)

`#fdf3e2` is a **warm light cream**, not pure white — but a **single flat near-white
body fill** without shade bands, darker joints/panels, and dark face sockets
reads as uncanny / featureless under game lighting (Human finding for correction).

**Production body treatment (required for C1):**

1. Lit primary shell may use bible cream `#fdf3e2` → `MAT_CozyCeramic`.
2. Undercuts, limb bases, shell seams use cream **shade** `#efe0c8` (or
   `MAT_CozyStoneWarm` / structure shade language) so mass is not blown white.
3. **Joints, limb rings, sprout** use leaf `#7fc98f` (readable darker than body).
4. **Face:** eye sockets `#3d3226`; iris sky-glass `#a8dced` (never manifestation cyan);
   blush optional `#f4a09a` @ 55%.
5. **Panels / straps / tank bands:** wood `#c98a5e` or leaf — secondary planes mandatory.
6. **Forbidden body fills:** pure white `#FFFFFF`, near-white greys, single-slot
   monochrome body with no shade or joint contrast, DNA cream as sole SSOT paint.
7. **Cyan** `#3fd0e0` / `#8ff0ff` = restrained **manifestation stage chrome only** —
   never complete Nori body materials.
8. Dual-res proof at `1280×720` and `868×517`: character region must not exceed
   bible lighting blow budget (blown pixels >245 under 3% globally; face/joints
   remain legible as black-mass + color).

---

## 2. Animation contract intent (binding for C1–C2)

Source map: `orchestration/control/UCBV_ANIMATION_BLOCK_INTEGRATION_MAP_001.md`.

### 2.1 What Tier3 supplies

| Item | Production meaning |
|---|---|
| `anim_robot_gardener_v1` | **Names + compatibility contract only** — not animation payload |
| DNA clip durations / events | **Empty / zero** — never claim DNA clips are animated |
| `skel_small_biped_robot_v1` catalog bones `[root,body,head]` | **Placeholder residual** — not production hierarchy |
| Blend profile | `cozy_bouncy` |
| Root motion | `false` (required) |

### 2.2 Production skeleton (exact 14 bones)

```
root → pelvis → spine → chest → head → sprout_ctrl
                 chest → arm_L → hand_L
                 chest → arm_R → hand_R
                 pelvis → leg_L → foot_L
                 pelvis → leg_R → foot_R
```

Import fails if any bone missing, renamed, duplicated, wrong parent, or root motion on.

Sockets: hand tool → `hand_R`; back tank/VFX → `chest`; sprout → `sprout_ctrl`/`head`.

### 2.3 Layer A — Tier3 gardener base (real keyed GLB actions in C1)

| Action | Required now | Notes |
|---|---|---|
| `idle` | yes | loop; breathe/bob/blink/sprout sway |
| `walk` | yes | locomotion loop |
| `scan` | yes | targeting anticipation |
| `happy` | yes | post-authoritative-complete reaction only |
| `cancel` | yes | cancel/refusal presentation |
| `water` / `plant_seed` / `harvest` / `charge` | optional polished | ship only if fully keyed + evidenced |
| `low_energy` | deferred | only if real energy state exists |

Missing optional clips: mark **deferred** — **never idle-alias**.

### 2.4 Layer B — UCBV build extension (game-local; not Tier3 payload)

Author in C1 GLB + adapter `nori7_animation_adapter.json`:

- `turn_left`, `turn_right`
- `build_place`, `build_place_hold`
- `confirm`

Adapter must declare base Tier3 set, extension version, skeleton, GLB path,
durations, loops, bones, clip hashes, triggers — and **must not claim** extension
clips came from Tier3.

### 2.5 Authority of markers

Animation markers / method tracks are **presentation only**. Forbidden effects:
World Commit, deletion, ownership, inventory, currency, persistence, arbitrary
script execution. C2 AnimationTree must fail closed if required actions missing
(no procedural pelvis-bob fallback in normal play).

---

## 3. Fail-closed production checklist (C0 contract → C1/C2/C4 gates)

Use as **hard fail** gates. Each item is either proven or the correction package
does not pass Purple/Codex.

### A. Real mesh / GLB

| ID | Gate | Fail if |
|---|---|---|
| A1 | Offline production `.glb` under leased character asset path | Zero GLB or descriptor-only / procedural SphereCapsule stand-in in normal play |
| A2 | Skinned production mesh with named material slots from U1 vocabulary | Unnamed materials; photoreal skin next to toy world |
| A3 | Provenance: Bridge job/package hashes, style_lock_id, recipe_id, character_id | Missing hashes or silent invent of modules |
| A4 | Quarantine/intake via existing offline Blender Bridge + GLB intake only | Ad-hoc copy into catalog; network/live provider; new installs |

### B. Skin / materials

| ID | Gate | Fail if |
|---|---|---|
| B1 | Body = bible cream + shade bands + MAT_CozyCeramic | Flat near-white / DNA cream as SSOT / pure white |
| B2 | Joints/panels/sprout leaf contrast readable | Joints same value as body |
| B3 | Face sockets dark + sky-glass iris | Missing face; cyan iris as base look |
| B4 | Cyan only on manifestation chrome | Cyan on complete body kit |
| B5 | ≤3 dominant palette groups | Neon soup / extra families |

### C. Rig

| ID | Gate | Fail if |
|---|---|---|
| C1 | Exact 14-bone hierarchy + parents | Placeholder `[root,body,head]` treated as production |
| C2 | Sockets resolve to real bones | Orphan sockets / world-grid sockets on character |
| C3 | `root_motion=false` | Any root motion export |

### D. Animation (keyed GLB actions)

| ID | Gate | Fail if |
|---|---|---|
| D1 | Required Layer A + Layer B actions exist once each | Name list only; pelvis-bob-only tracks |
| D2 | duration > 0 and ≥1 non-root transform/property track | Empty actions |
| D3 | Loop flags match adapter | Wrong loops |
| D4 | `scan` ≠ `happy`; no idle aliases for missing clips | Optional missing filled with idle |
| D5 | Markers never mutate World Commit / delete | Method tracks that mutate world |

### E. Palette contrast (playtest)

| ID | Gate | Fail if |
|---|---|---|
| E1 | Warm cream body readable vs walls | Character merges into wall cream blob |
| E2 | Dual-res 1280×720 + 868×517 face/sprout/tank legible | Features lost at either res |
| E3 | Black-mass silhouette still distinct | Featureless white teardrop only |

### F. 28-module catalog (C2 runtime; checklist ownership here)

| ID | Gate | Fail if |
|---|---|---|
| F1 | Manual Build exposes **all 28** `runtime_catalog.json` `module_ids` via categorized selector | Only `arch_door_round` or hidden comma/period cycle |
| F2 | Selector shows module name + preview | Nameless icons only |
| F3 | No invented module ids | Catalog rewrite / silent invent |

Observed 28 ids (authoritative product snapshot — do not invent):

`block_cube_round`, `block_cylinder_round`, `block_sphere_segment`, `block_wedge`,
`block_arch`, `block_dome`, `block_ring`, `block_beam`, `block_panel`,
`block_pipe_straight`, `block_platform`, `block_ramp`, `terrain_flat_8m`,
`terrain_flat_16m`, `terrain_slope_8m`, `arch_floor_round_4m`, `arch_wall_door_4m`,
`arch_wall_window_4m`, `arch_roof_dome_4m`, `arch_door_round`,
`arch_window_frame_simple`, `cluster_cozy_house_small_A`,
`cluster_cozy_greenhouse_droplet_A`, `cluster_cozy_farm_A`, `prop_bench_simple`,
`prop_lamp_post`, `prop_crate_small`, `char_nori7_base`.

### G. InputMap controls (C2)

| ID | Gate | Fail if |
|---|---|---|
| G1 | Real InputMap Q/R rotation when preview active | Silent `rotated=false` with no UX reason |
| G2 | Labelled non-conflicting elevation action | Undocumented / camera-conflicted elevation |
| G3 | Tests drive InputMap events, not controller method fallbacks | Direct method-only smoke |
| G4 | When no preview: visible reason Q/R inactive | Silent fail |

### H. Delete authority (C2)

| ID | Gate | Fail if |
|---|---|---|
| H1 | Explicit erase mode: cursor red-X | Instant delete without mode |
| H2 | Only committed player-owned/unlocked entities highlight | Arbitrary entity free delete |
| H3 | Confirm → World Commit **compensation-delete proposal** | Direct `queue_free` / client durable delete |
| H4 | Esc/RMB exit without mutation; Undo via compensation | Client-only undo that skips authority |

### I. Clean evidence (C4)

| ID | Gate | Fail if |
|---|---|---|
| I1 | Normal-play dual-res captures, no diagnostic banner/wall | UCBV diagnostic chrome in acceptance frames |
| I2 | Zero ERROR / USER ERROR / SCRIPT ERROR / parse-missing / RID leak + submitted nav warnings | Any strict error line |
| I3 | Hash GLB + adapter + clip manifest + input sequence log | Name-list-only animation evidence |
| I4 | Immutable U0–U8 artifacts untouched | Rewrite/rehab of rejected evidence |

---

## 4. C1 offline Blender Bridge checklist (no install)

C1 must use **already-approved local Blender Bridge** workflow only.

| Step | Requirement | Fail if |
|---|---|---|
| B0 | Blender executable already present from B0-001 path; **no dependency install** | Any install / version change / download |
| B1 | Job runs offline / local; no live provider; no public network shipping | Network asset fetch |
| B2 | Export GLB with skinned mesh + AnimationPlayer actions (Layer A+B) | Descriptor-only or empty actions |
| B3 | Condition through existing quarantine + GLB intake / validator | Direct drop into runtime without gate |
| B4 | Bind Bridge job id + package hashes in provenance | Missing provenance |
| B5 | Material slot names match shared vocabulary → MAT_* mapping | Invented material ids |
| B6 | Log only to C1 leased log or OS temp **outside repo** | Helper `_tmp` under orchestration or game/tests |
| B7 | Do not edit Tier3 DNA catalogs; adapter is game-local | DNA rewrite / Tier3 activation claim |
| B8 | Verify 14 bones + parents + required clips before handoff to C2 | “Looks fine” without validator evidence |

---

## 5. Scope locks

- **In C0:** design contracts under style_lock + nori7 leases; this checklist; cream table; anim intent.
- **Out of C0:** GLB binary, Godot scripts, InputMap, delete mode, headed captures, P2E-002.
- **Immutable:** all U0–U8 receipts/logs/evidence under non-`correction_002` paths.
- **Red F01:** network shipping hard stop remains.

---

## 6. Next owner

`C1_CHARACTER_PRODUCTION` — profile `aidle-worldgen-asset-art` — real offline
mesh/skin/rig/GLB + keyed actions per this preflight.

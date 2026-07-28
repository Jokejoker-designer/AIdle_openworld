# MOCKUP DESIGN LOCK — Official Visual SSOT V2

**Status:** `DESIGN_SSOT_ACTIVE`  
**Mockup ID:** `MOCKUP_SSOT_V2`  
**HTML:** `MOCKUP_SSOT_V2.html`  
**Machine index:** `MOCKUP_SSOT_V2.json`  
**Owner:** Human Product Lead (acceptance) · Design agents (produce under WO)  
**accepted:** `false` · **self_accept:** `false` (machine design SSOT only — not product ship)

---

## 0. Binding order

When any agent designs or implements character art, animation, props, buildings, or manifestation visuals for AIdle Openworld:

1. **This mockup package** is the **visual Single Source of Truth** for look, motion, IDs, and clip names.
2. `orchestration/control/AIDLE_GAME_VISION_LOCK_001.md` remains product north star.
3. `orchestration/ARCHITECTURE_LOCK.md` + `contracts/world_prompt.schema.json` remain technical/authority locks.
4. Where **visual design** conflicts with an older HTML mockup (e.g. `mockup_cast_props_001`), **V2 wins**.
5. Where **machine contracts** conflict with this mockup, **machine contracts win** and this mockup must be corrected — never the reverse for commit/authz.

**Rule:** *If it is not in the mockup (or a Human-approved delta WO), it is not the game look.*

---

## 1. Scope of the locked mockup

| Layer | Count | Source of IDs |
|------:|------:|---------------|
| Characters | **15** | Foundry IDs in `MOCKUP_SSOT_V2.json` |
| Props (non-building) | **30** | `module_id` in JSON |
| Buildings | **10** | `module_id` in JSON |
| Manifestation | **4 stages** | wireframe → hologram → materializing → complete |

### 1.1 Characters (must match mockup art + clips)

| # | character_id | Display | Clips min |
|--:|---|---|---|
| 1 | `CCP-RH-001` | Nori-7 | Layer A + Layer B |
| 2 | `CCP-NS-002` | Mây Mạch | Layer A |
| 3 | `CCP-NW-003` | Bác Bắp | Layer A |
| 4 | `CCP-CT-004` | Bụi Mơ | Layer A |
| 5 | `SPH-RH-011` | Kito Thụ Phấn | Layer A |
| 6 | `OA-RG-021` | Nereu-5 | Layer A |
| 7 | `AC-CO-015` | Cinder-04 | Layer A |
| 8 | `TD-CT-028` | Patch Gấu Nút | Layer A |
| 9 | `SV-NW-019` | Trúc Nhi | Layer A |
| 10 | `SPH-NG-009` | Luma Tán Lá | Layer A |
| 11 | `SC-NG-005` | Kẻ Giữ Khung | Layer A |
| 12 | `SC-NS-006` | Lụa Ngược | Layer A |
| 13 | `SC-NW-007` | Ông Nhỏ Lớn | Layer A |
| 14 | `SC-CA-008` | Gấp Bóng | Layer A |
| 15 | `SPH-NW-010` | Sora Giữ Sương | Layer A |

**Layer A (all cast):** `idle`, `walk`, `scan`, `happy`, `cancel`  
**Layer B (Nori production):** `turn_left`, `turn_right`, `build_place`, `build_place_hold`, `confirm`  
**Forbidden:** aliasing a missing clip to `idle` in production validation.

### 1.2 Buildings (10)

`cozy_house_small_A`, `cozy_greenhouse_A`, `cozy_barn_small_A`, `cozy_workshop_A`, `cozy_market_stall_A`, `cozy_windmill_A`, `cozy_well_house_A`, `cozy_watchtower_A`, `cozy_bridge_arch_A`, `cozy_gazebo_A`

### 1.3 Props (30)

See `MOCKUP_SSOT_V2.json` → `props[]`. Includes trees, rocks, flora, farm, infra, furniture, utility, decor.  
Do **not** invent new `module_id` without Foundry/P1E allowlist + Human WO.

---

## 2. Art locks (copy from mockup)

| Token | Value |
|---|---|
| Style | Cozy Cyber-Pixel / Dreamy Low-Poly **2.5D** |
| Camera | Fixed three-quarter / isometric |
| Character proportion | Chibi **~2 heads** tall |
| Cream base | `#fdf3e2` |
| Ink | `#263238` |
| Sky | `#9ED7E5` |
| Leaf | `#72A96B` |
| Wood | `#c98a5e` |
| Warm light | `#f5c451` |
| Cyan | `#62E6FF` / `#3fd0e0` — **manifestation only**, never primary body/building fill |
| Palette budget | ≤ **3** dominant families per character |
| Silhouette | Readable including **rear identifier** |

**Anti-patterns (fail design QA):**

- Photoreal next to toy low-poly
- Dense neon cyberpunk soup
- Instant pop-in (skip manifestation stages)
- Palette-only “new character” skins
- Copied commercial IP silhouettes / mascots
- Free-orbit camera on MVP critical path

---

## 3. Animation locks

Timings follow `COZY_ART_BIBLE_001.md` §4 and are **demonstrated in the HTML mockup**:

| Motion id | Duration | Use |
|---|---:|---|
| `bob` | 2.4 s | Humanoid idle |
| `bob_small` | 3.0 s | Robot idle |
| `breathe` | 2.8 s | Creature idle |
| `walk` | 0.7 s cycle (mock presentation) | Locomotion bob |
| `scan` | 1.4 s | Target / inspect |
| `happy` | 1.1 s | Positive react |
| `cancel` | 0.55 s | Negative / cancel |
| `sway` | 3.5 s | Foliage / trees |
| `sway_small` | 4.2 s | Flowers / small plants |
| `pulse` | 2.0 s | Lamp / glow |
| `spin` | 9.0 s | Windmill / gears |
| `steam_rise` | 2.6 s | Workshop / greenhouse |
| `ripple` | 3.0 s | Water surfaces |
| `flicker` | 0.55 s | Campfire |

**Presentation rule:** Animation events **never** World-Commit, mutate inventory, ownership, or collision.  
`confirm` clip plays **after** commit receipt (presentation only).

**Mockup video samples (real motion media):**

- `anim/anim_nori7_idle.mp4`
- `anim/anim_buimo_idle.mp4`
- `anim/anim_bacbap_idle.mp4`
- `anim/anim_kito_idle.mp4`
- `anim/anim_house_ambient.mp4`
- `anim/anim_lamp_pulse.mp4`

Entities without video still use **CSS motion matching the timing table** + concept art / sheets. Production GLB must exceed CSS mock (real keyed bones), not undercut it.

---

## 4. Manifestation locks

Stages (ordered, non-skippable for durable create):

1. `wireframe` — cyan edges only, no collision  
2. `hologram` — translucent cyan fill, no collision  
3. `materializing` — warm material rises, cyan residual above fill, no collision  
4. `complete` — full warm palette, shadow, inhabited light; collision **only after** confirm + World Commit  

Duration UX target: **8–15 s** full choreography (schema may allow 1–60 s). Reduced-motion shortens motion but keeps stage labels.

---

## 5. How production must follow the mockup

```text
Open MOCKUP_SSOT_V2.html + JSON
  → produce design package (Foundry / visual_spec / style_lock)
  → offline Blender / Bridge job
  → quarantine + hash + bone/clip validate
  → MOCKUP DELTA CHECK (silhouette, palette, clip names, timing class)
  → WO promote into game/assets/**
  → smoke (idle play, load counts)
  → Purple + Human accept
```

### Mockup delta check (required for promote)

A production asset **fails** if any of:

1. Wrong or invented `character_id` / `module_id`
2. Missing Layer A clip names (or Layer B for Nori)
3. Cyan used as primary body/building material
4. Silhouette unreadable in fixed 2.5D camera / missing rear marker
5. Motion class mismatched (e.g. robot uses heavy humanoid bounce only, or plant has no sway where mockup specifies sway)
6. Style is photoreal or second unrelated art school
7. Building/prop proportions contradict mockup sheet readability (toy low-poly stage)

---

## 6. Honesty / authority

| Claim | Status |
|---|---|
| Design SSOT for agents | **Yes — this package** |
| Human product acceptance | **No** until Human Lead sets `accepted=true` |
| Full 15+30+10 production GLBs in Godot | **No** — subset exists (10 cast + 10 modules); remainder is mockup art + contract |
| Companion voice/TTS | **Out of MVP** (vision lock) |
| AI mesh as world truth | **Forbidden** until QA + promote |

Workers **must not self-accept**. Red finds only. Blue patches only under approved WO. Purple verifies only.

---

## 7. Supersession

| Prior artifact | Relationship |
|---|---|
| `mockup_cast_props_001` (10+10) | **Superseded for design scope**; keep as historical evidence |
| `UCBV_VISUAL_MOCKUP_00x` | Complementary Nori/block timing; V2 is cast/world inventory SSOT |
| Foundry MD (28 characters) | Still identity source; **first production wave is the 15** listed here |

---

## 8. Agent entry checklist

Before any character/animation/scene design task:

- [ ] Open `MOCKUP_SSOT_V2.html` in browser
- [ ] Read matching IDs in `MOCKUP_SSOT_V2.json`
- [ ] Read this lock
- [ ] Bind work order to listed IDs only (or explicit Human expansion WO)
- [ ] Deliver assets that pass mockup delta check
- [ ] Do not claim ship without Human acceptance

---

**End of lock.** Deviating without Human Product Lead authorization is a reportable finding (`NEED_HUMAN` / Red finding), not a free “improvement.”

---

## 9. Revision V2.1 — full concept art fill

**2026-07-23:** All **10 buildings** and **30 props** now have dedicated clay-cozy concept JPG art (no SVG placeholder cards in the SSOT HTML). Style-locked to `bld_01_house.jpg` / existing nature props. Production GLB promote still requires WO + hash + Human accept.

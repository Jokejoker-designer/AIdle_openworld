# AIdle Openworld — Town Architecture Design 001

Status: DESIGN REFERENCE · Authored by: Claude (continuity conductor) ·
Authorized by: Human Product Lead (Hanh), 2026-07-24
Binding order: this document is a **design/identity layer**. It does not
override, and is subordinate to, `AIDLE_GAME_VISION_LOCK_001.md`,
`orchestration/ARCHITECTURE_LOCK.md`, `contracts/world_prompt.schema.json`,
and — for anything geometric — `game/resources/town/town_grid_plan_v1.json`
and `orchestration/control/visual_reference/town_plan/TOWN_FAIRY_STREET_PLAN_V1.json`.
Where this document names a position, rotation, footprint, or grid cell, that
value is copied **read-only** from those two files for reference; if they
ever disagree, the JSON files are correct and this document is wrong.

## 0. Hard constraint (Human-mandated 2026-07-24, verbatim)

> "Phát triển dựa trên map đang sử dụng hiện tại chứ đừng thay đổi nó"
> — develop on top of the map currently in use; do not change it.

This document adds **no new position, no new rotation, no new footprint, no
new grid cell, no new district, no new plot**. Every district, building,
character-spawn, and prop referenced below already exists in
`town_grid_plan_v1.json` (50 plots, 10 districts) and is quoted from it
verbatim. What this document adds is **identity, purpose, and narrative
rationale** for what is already placed — it is the "why" layered on the
existing "where." Any future work (Grok or otherwise) that reads this
document must not treat it as license to move, resize, rotate, or re-parent
anything. If a gameplay idea below would require a new position, it is
flagged `REQUIRES_NEW_DIRECTIVE` and is explicitly **not** authorized by this
document.

## 1. What the town already is, read from the data

`town_grid_plan_v1.json` places 10 districts on a 12-unit-cell grid (A–L ×
1–12), origin (0,0) at the player's home. Reading the district center
coordinates as already authored (not invented here):

| District | Vietnamese | Center (x,z) | Bearing from HOME |
|---|---|---|---|
| HOME | Sân nhà | (0, 0) | — origin |
| WORKSHOP | Xưởng thợ | (10, 0) | due East |
| MARKET | Chợ phiên | (8, 6) | Northeast |
| GARDEN | Vườn nghỉ | (2, 10) | North |
| GREENHOUSE | Nhà kính | (-5, 9) | Northwest |
| WELL | Giếng làng | (-9, 3) | West (slightly N) |
| WINDMILL | Cối xay gió | (-9, -3) | West (slightly S) |
| BARN | Sân kho | (-5, -9) | Southwest |
| BRIDGE | Cầu vòm | (2, -10) | South |
| LOOKOUT | Chòi ngắm | (8, -6) | Southeast |

This is a genuine, already-existing structural fact, not a proposal: the 9
satellite districts sit in a **ring around HOME at roughly 10–11 units'
radius**, in clean compass order (E → NE → N → NW → W → SW → S → SE and back
to E). The town was already built as "home at the center, the wider world
one ring out." This document names that fact and designs on top of it; it
does not create it.

Connective tissue is likewise already authored in
`TOWN_FAIRY_STREET_PLAN_V1.json`: a 13-segment flat stone path network plus
12 wood-platform accents, fitted to the same ±12 cadastre bounds, explicitly
declared as **not** a position override of the grid plan. The one live
conflict this network had (WD-GAZEBO overlapping HOME.BLD instead of sitting
at the real GARDEN.BLD/H12) was already ruled and resolved by the Human on
2026-07-24 (`TOWN_ALIGNMENT_V1_PATCH.json`) — paths connect the ring, they do
not relocate it.

## 2. Town identity: what HOME and the ring mean together

The **north star** (Vision Lock §1) is: *"The player speaks, the Companion
turns intent into a safe world proposal, the world previews the change as
light, and only a validated, confirmed transaction becomes persistent
reality."* HOME (`HOME.BLD`, grid G7, the player's small house) is where that
sentence is lived every session — it is the player's **Private Reality**
(Horizon H1) seed, the one space the Companion and player build together from
nothing. Nori-7 (`HOME.CHAR`) lives there as the Companion.

The ring of 9 districts is not "more houses" — read together with what is
already built in each (a building type, a resident or visitor character, a
themed prop set), the ring already encodes a **stations-of-craft** structure:
each district is a small, self-contained lesson or flavor of what building a
Reality with a Companion can feel like, radiating outward from the one place
that's entirely the player's own. This section names the purpose already
implied by each district's existing content; §3 gives each one a full
identity page.

## 3. District identity pages

Each entry: existing building + grid cell (frozen, quoted from
`town_grid_plan_v1.json`), existing character (frozen), existing props
(frozen), and the **design identity** layered on top — in-fiction purpose,
gameplay association (tied to already-locked systems, no new mechanics
authorized here), and tone. Where a future system is referenced, it is
labeled with its Horizon tier from Vision Lock §8 so no one mistakes flavor
text for a scope change.

### 3.1 HOME — "Sân nhà" (G7, footprint 5×4, rot 0)
- Building: `cozy_house_small_A`. Character: **Nori-7** (`CCP-RH-001`, robot,
  native_cozy). Props: path stone, garden lamp, mailbox.
- Identity: the player's own Private Reality seed (H1). The one place in
  town where manifestation is not a demo — it is the player's actual,
  persistent, owned space. Nori-7 is the Companion who greets, teaches the
  Prompt Composer / manifestation flow, and never builds *for* the player
  without confirmation (Vision Lock §1, §6). `HOME.BLD` is closed-permanently
  at its current soft-clay finish (Human-accepted 2026-07-24) — deliberately
  the most lived-in, slightly imperfect building in town, which reads well
  narratively: it is home, not a showroom.

### 3.2 WORKSHOP — "Xưởng thợ" (L7, rot 180)
- Building: `cozy_workshop_A`. Character: **Bác Bắp** (`CCP-NW-003`,
  humanoid, native_cozy). Props: tool rack, small crate, barrel.
- Identity: the craft/construction district. Bác Bắp is the town's builder —
  narratively, the person who explains *how* a wireframe becomes a hologram
  becomes matter (Vision Lock §5's manifestation visual), grounded in
  ordinary carpenter/smith framing rather than magic. Directly East of HOME:
  the nearest district, appropriate for an early-game "first NPC you meet
  outside your own door."

### 3.3 MARKET — "Chợ phiên" (K10, rot 210)
- Building: `cozy_market_stall_A`. Character: **Mây Mạch** (`CCP-NS-002`,
  humanoid, native_cozy). Props: bench, cart, signpost.
- Identity: trade and exchange. Mây Mạch runs the stall and is the natural
  narrative seed for a future Prompt Recipe marketplace (Horizon H3 —
  *not* built now, flavor/lore only). Today, in scope, Mây Mạch is simply
  the town's trader/gossip hub — the person who has heard about the
  travelers passing through (see §5).

### 3.4 GARDEN — "Vườn nghỉ" (H12, rot 255)
- Building: `cozy_gazebo_A`. Character: **Bụi Mơ** (`CCP-CT-004`, quad,
  native_cozy). Props: flower cluster, flower bed, round bush.
- Identity: rest and quiet company. Bụi Mơ (a quad-form companion — read as
  a garden animal, not humanoid) is the town's low-key, non-verbal presence,
  a deliberate contrast to the talkative Companion/trader roles elsewhere.
  The fairy-street wood platform (`WD-GAZEBO`) now correctly sits here after
  the 2026-07-24 conflict resolution — this is the district's actual social
  deck.

### 3.5 GREENHOUSE — "Nhà kính" (D11, rot 300)
- Building: `cozy_greenhouse_A` (alias `cozy_greenhouse_preview_anchor_A`).
  Character: **Kito Thụ Phấn** (`SPH-RH-011`, robot, **visitor**,
  `world_profile: solarpunk_haven`). Props: farm plot, crop row, scarecrow.
- Identity: growth and cultivation — thematically the closest district to
  "manifestation as living growth" rather than construction. Kito is the
  first **visitor** district encountered going counter-clockwise from
  GARDEN; see §5 for what "visitor" means narratively.

### 3.6 WELL — "Giếng làng" (B8, rot 345)
- Building: `cozy_well_house_A`. Character: **Nereu-5** (`OA-RG-021`, robot,
  visitor, `world_profile: oceanpunk_abyss`). Props: small pond, water pump,
  birdbath.
- Identity: water and depth. The westernmost-north district; Nereu-5's
  oceanpunk_abyss origin is a natural fit for the district already built
  around water props — this is read, not invented (the props were already
  water-themed before this document existed).

### 3.7 WINDMILL — "Cối xay gió" (B5, rot 15)
- Building: `cozy_windmill_A`. Character: **Cinder-04** (`AC-CO-015`,
  construct, visitor, `world_profile: arcane_clockwork`). Props: fence
  section, grass tuft, rock cluster.
- Identity: energy and mechanism. A construct-form visitor at the town's
  literal power/energy building is, again, a pre-existing pairing this
  document names rather than assigns.

### 3.8 BARN — "Sân kho" (D2, rot 60)
- Building: `cozy_barn_small_A`. Character: **Patch Gấu Nút** (`TD-CT-028`,
  quad, visitor, `world_profile: tiny_diorama`). Props: fruit tree, small
  rock, stacked rock.
- Identity: storage and provisions. Patch (quad-form, "tiny diorama" origin)
  reads as a small, storybook-scaled creature at home among stored goods —
  the cozy counterpart to WINDMILL's more mechanical visitor.

### 3.9 BRIDGE — "Cầu vòm" (H2, footprint 6×3, rot 105)
- Building: `cozy_bridge_arch_A`. Character: **Trúc Nhi** (`SV-NW-019`,
  humanoid, visitor, `world_profile: spirit_valley`). Props: willow tree,
  blossom tree, mossy rock.
- Identity: the crossing-point. A bridge is architecturally already a
  threshold, and this document treats it as the town's literal and narrative
  arrival point for visitors (§5) — the one structure in the ring whose
  *function* (a crossing) matches its *shape* without any invention needed.

### 3.10 LOOKOUT — "Chòi ngắm" (K4, rot 150)
- Building: `cozy_watchtower_A`. Character: **Luma Tán Lá** (`SPH-NG-009`,
  humanoid, visitor, `world_profile: solarpunk_haven`). Props: landmark
  tree, pine tree, tree cluster.
- Identity: the vantage point. A watchtower is the tallest, farthest-seeing
  structure in the ring; narratively it is where Luma watches the horizon —
  fitting foreshadowing for Horizons H2–H6 (friends/shared districts, other
  Reality hubs) **without pulling any of them forward**. This is flavor
  text about looking outward, not a system.

## 4. What this document explicitly does NOT authorize

- No new plot, district, building, character, or prop position.
- No change to any existing grid cell, rotation, or footprint.
- No new gameplay system (trade, multiplayer visits, energy mechanics,
  farming loops) — district "identity" above is narrative framing for
  systems that are either already locked (manifestation, Companion) or
  explicitly future horizons (H2 Shared District, H3 marketplace, H4/H5/H6).
  Any of those remain **out of scope** until their own directive opens them.
- No repositioning of the fairy-street path/wood-platform network.
- Set dressing, signage text, ambient dialogue hooks, and small props that
  fit **within an existing plot's own footprint** are in scope for future
  waves under this document; moving a plot to make room for them is not.

## 5. Handoff

This document, together with `AIDLE_STORY_BIBLE_001.md`, is the binding
identity/narrative reference for all future Grok work that touches town
identity, signage, dialogue, or character flavor. See
`GROK_ARCHITECTURE_STORY_ADHERENCE_PROMPT_001.md` for the dispatch instructing
strict adherence.

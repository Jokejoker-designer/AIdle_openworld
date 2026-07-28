# AIdle Openworld — Story Bible 001

Status: DESIGN REFERENCE · Authored by: Claude (continuity conductor) ·
Authorized by: Human Product Lead (Hanh), 2026-07-24
Binding order: subordinate to `AIDLE_GAME_VISION_LOCK_001.md` (product
promise, pillars, Companion character lock, Horizon fence) and to
`AIDLE_TOWN_ARCHITECTURE_DESIGN_001.md` for district identity. Grounded
entirely in data that already exists in the project — `town_grid_plan_v1.json`
(10 districts, 10 characters split `native_cozy` / `visitor`),
`cast_roster.json` (character forms), and the Vision Lock's Horizon ladder
(H1 Private Reality → H6 Open Continuum). Nothing below invents a character,
a position, or a system; it explains *why* what is already built is built
that way.

## 0. Hard constraint carried from the architecture document

Same as `AIDLE_TOWN_ARCHITECTURE_DESIGN_001.md` §0: this bible adds meaning,
not geometry. It authorizes no repositioning of any plot and no new game
system. It also introduces no new characters, buildings, or props — the
entire cast and set are the 10 districts and 10 characters already in
`town_grid_plan_v1.json`.

## 1. One-paragraph premise

AIdle Openworld is the story of a **Private Reality being grown, one honest
conversation at a time**, by a player and their Companion, Nori-7. The town
around HOME is not a pre-built village the player stumbles into — in-fiction,
it is what the player and Nori-7 have already manifested together before the
story's "present," proof that the core loop (speak → propose → preview →
confirm → manifest) works and holds. Living among the town's four
long-time residents are travelers who arrived from other, very different
Realities — not tourists with an explanation, but a standing mystery and a
promise of the wider Continuum the player's own Reality is one shard of.

## 2. World concept: Private Realities and the wider Continuum

The Vision Lock's Horizon ladder already establishes, as locked design (not
invented here), that AIdle's world model is a **directory of sharded
procedural realities** (H6 "Open Continuum"), that licensed/inspired hub
cities exist as a research horizon (H4), and that the player begins in
exactly one such Reality: a **Cozy 2.5D Private Reality** (H1, the MVP,
`world_profile: cozy_cyber_pixel`). This is not new lore — it is the existing
technical scope fence, read as story.

The story bible's job is to make that ladder feel inhabited *without*
building any rung of it early. In-fiction:

- The player's town is **one Private Reality** — small, personal, safe, and
  entirely theirs, exactly as the Vision Lock's product promise describes
  (§2: "everything the player owns is safe, provenanced, and theirs").
- Other Realities exist, are different in kind (not just decoration — an
  oceanpunk abyss, an arcane clockwork world, a solarpunk haven, a spirit
  valley, a tiny diorama world are all named, distinct `world_profile`
  values already in the data), and are usually **out of reach**.
- Very rarely, something — or someone — from another Reality **resolves
  into** this one. The game already has a name for how anything becomes
  real here: **manifestation** (wireframe → hologram → materializing →
  complete, Vision Lock §5). The story bible's central narrative device is
  that the six visitor characters are read as having manifested into this
  Reality the same way a player's build does — just not by the player's own
  hand, and not fully explained. This uses a mechanic the player already
  understands as the explanation for a mystery, instead of inventing a new
  system.

This framing is deliberately light-touch and reversible: it requires no new
mechanic, no multiplayer, no new horizon opened. It is pure narrative color
laid over already-locked systems and already-placed characters.

## 3. The Companion: Nori-7

`CCP-RH-001`, robot form, `native_cozy`, lives at HOME (`HOME.BLD`). Per the
Vision Lock's character lock (§6), Nori-7 is a **collaborator, not an
authority** — it never owns the player's property, never silently builds,
and its personality adapts slowly and only from evidence, never from a
single message. Story-wise, Nori-7 is the one who first taught the player
the Prompt Composer, and — because Nori-7 has lived at the literal center of
the town's ring since before the story begins — is also the one most aware
that the ring's four long-time residents and six visitors are not the same
kind of neighbor. Nori-7 does not have a full explanation for the visitors
either; it treats the mystery honestly, the same way its design lock
requires it to be honest about cost, permission, and capability in the
build loop. This keeps the Companion's in-fiction voice consistent with its
mechanical voice: it says what it knows, what it does not, and never
pretends certainty it doesn't have.

## 4. The four native residents

These four already share one `world_profile` (`cozy_cyber_pixel`) and one
`resident_status` (`native_cozy`) — they belong to this Reality the way
Nori-7 and the player do.

- **Bác Bắp** (Workshop, humanoid) — the builder. The in-fiction source of
  practical "how things are actually made" knowledge; the person a new
  player-companion pair would go to with a build question that isn't about
  the Prompt Composer itself but about craft.
- **Mây Mạch** (Market, humanoid) — the trader. Keeps the town's stall,
  and — narratively — keeps track of comings and goings, including the
  visitors. The natural in-fiction narrator for "here's what's new in town."
- **Bụi Mơ** (Garden, quad) — the quiet companion. Non-verbal by form,
  present rather than talkative; the tonal counterweight to Mây Mạch, giving
  the town's native cast range rather than four versions of the same voice.
- **Nori-7** (Home) — see §3; also counted among the four natives, but
  distinguished by being the player's own Companion rather than a
  townsperson the player visits.

## 5. The six visitors

All six share `resident_status: visitor` and each carries a distinct
`world_profile`, already assigned in the data — this bible explains, it does
not choose, who lives where.

- **Trúc Nhi** (Bridge, humanoid, `spirit_valley`) — arrives, narratively,
  at the one structure in town shaped like a threshold. Framed as the first
  or most frequent crosser; other townsfolk would say Trúc Nhi "came over
  the bridge one day and never quite left," which is both the simplest and
  the most literal reading of her placement.
- **Kito Thụ Phấn** (Greenhouse, robot, `solarpunk_haven`) — a grower from a
  Reality organized around cultivation and renewal; at home among the
  greenhouse's farm plot and crop rows because that district was already
  built around growth before this bible existed.
- **Nereu-5** (Well, robot, `oceanpunk_abyss`) — from a deep-water Reality;
  drawn to the one district already built around water (pond, pump,
  birdbath).
- **Cinder-04** (Windmill, construct, `arcane_clockwork`) — a
  construct-form visitor at the town's literal energy building; reads as
  drawn to mechanism and motion.
- **Patch Gấu Nút** (Barn, quad, `tiny_diorama`) — small-scaled, storybook
  in origin; settled among stored provisions, the least mysterious and most
  immediately endearing of the six.
- **Luma Tán Lá** (Lookout, humanoid, `solarpunk_haven`) — shares Kito's
  origin Reality but chose the town's highest, farthest-seeing point instead
  of the greenhouse; the two are the bible's one explicit thread for a
  future beat (not built now) about why two travelers from the same
  Reality made different choices once they arrived.

None of the six have an origin story resolved in this bible on purpose —
"how and why visitors arrive" is the town's standing mystery, not a solved
backstory. That mystery is the natural, low-cost hook for future content
(dialogue, quests) without requiring any new system, character, or Horizon
to be opened early.

## 6. Narrative shape: chapters as manifestation, not cutscenes

Consistent with Vision Lock §1 and §4 (conversation is the primary creative
tool; manifestation is visible and legible), the story bible does not
propose cutscenes or branching dialogue trees as the primary storytelling
unit. Instead, each meaningful narrative beat is framed as something the
player **builds or is shown being built** — the same wireframe → hologram →
materializing → complete language the game already uses for every object.
Concretely, in scope for future (not yet authorized) content waves:

1. **Arrival echoes** — small, optional, already-manifestation-shaped
   vignettes near BRIDGE hinting at how a visitor first appeared, told
   through environment/light rather than a new cutscene system.
2. **Township beats** — short dialogue from the four natives (Bác Bắp, Mây
   Mạch, Bụi Mơ's non-verbal cues, Nori-7) reacting to the player's own
   manifestation activity, reinforcing that this world responds to what the
   player actually builds.
3. **The watch** — Luma at Lookout as the one character explicitly framed
   as watching outward; the natural place, later, to foreshadow (never
   open) H2's Shared District or H6's wider Continuum, entirely through
   flavor dialogue.

Every item above is content (text, small lighting/prop-scale set dressing
within an existing plot's own footprint) — none requires a new mechanic, a
new position, or a new Horizon to be opened.

## 7. Tone and voice

Per `DESIGN.md` §8 (already-locked brand voice): warm, curious, honest. The
Companion says what it understood, what it cannot do, and what things will
cost; it asks before consequential changes. This bible's cast follows the
same rule at the character-writing level — no character claims certainty
about the visitors that the story hasn't earned, and no dialogue pressures
the player emotionally toward any decision (Vision Lock's anti-pattern list
in `DESIGN.md` §9 already forbids this for UI; this bible extends the same
standard to any future NPC line).

## 8. What this bible does NOT authorize

- No new character, world_profile, building, or plot.
- No multiplayer, shared-district, or cross-player visit system (H2) —
  visitors are single-player lore only.
- No marketplace/economy system (H3) — Mây Mạch's trader framing is flavor.
- No licensed hub city content (H4), no spacecraft/exoplanet content (H5),
  no functional Open Continuum directory (H6) — all referenced only as
  distant in-fiction context for why visitors exist, never as systems to
  build now.
- No repositioning of any plot, path segment, or wood platform.

## 9. Handoff

Paired with `AIDLE_TOWN_ARCHITECTURE_DESIGN_001.md`. Both are the binding
reference for `GROK_ARCHITECTURE_STORY_ADHERENCE_PROMPT_001.md`.

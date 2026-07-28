# ARCHITECTURE LOCK — AIdle Openworld v1.1

Status: ACTIVE · Owner: Human Product Lead · Date: 2026-07-20

> Vision anchor: read `orchestration/control/AIDLE_GAME_VISION_LOCK_001.md`
> before planning or editing. This Architecture Lock remains the binding
> technical/authority lock; the vision lock is the standing product north star
> every agent follows until the game is complete.

## Runtime spine

- Client/visual runtime: Godot 4.x, version pinned before the first code wave.
- Product-first presentation: 2.5D Dreamy Low-Poly only for the vertical slice.
- Camera: fixed-angle isometric/three-quarter view; no free 3D camera in MVP.
- World construction: modular 2.5D entities on layered navigation/collision grids.
- Multiplayer/social backend: Nakama candidate, confirmed only after POC-01.
- Canonical world mutations: authoritative World Commit service.
- Contracts: JSON Schema Draft 2020-12 plus versioned events.
- Persistence: append-only mutation log + snapshots + chunk/object storage.
- AI: provider-neutral AI Game Master (AGM) gateway using one versioned Snapshot
  and Decision Envelope contract across all editions.
- MVP Companion interface: text-only. TTS/voice is post-alpha research.
- Free edition: manual Desktop Bridge through clipboard or inbox/outbox files;
  no API and no hidden desktop automation.
- Paid edition: API adapter behind a trusted gateway; provider credentials are
  never stored in the Godot client or world files.
- First-run edition selector: `desktop_bridge_free` or `api_paid`. Both execute
  through the same validator and World Commit boundary.

## Ownership boundaries

- `godot_voxel`: post-MVP terrain R&D only, behind an adapter.
- Modular entities: buildings, doors, vehicles, NPCs, quests and props.
- Asset workers: asynchronous, sandboxed and untrusted until QA passes.
- Neural world models: isolated research lab for preview/dream portals only.
- Nakama and Colyseus must not co-own the same world-state domain.

## Authority

| Context | Simulation | Durable state |
|---|---|---|
| Offline Private Reality | Local client | Local signed journal; reconcile on sync |
| Online Private Reality | Server | Server |
| Private with visitors | Server | Server |
| Shared/Doppelganger | Server | Server |
| Spacecraft/Exoplanet | Owner proposes | Server validates and commits |

The AGM directs quests, dialogue, mood, pacing, events and build proposals. It
does not own collision, inventory, currency, persistence, or durable mutation.
Godot is the presentation/execution client, while policy, schema and World
Commit remain the safety and authority boundary.

## Forbidden paths

- No direct LLM -> scene tree/database mutation.
- No parsing arbitrary prose as executable commands; accept only the versioned
  AGM Decision Envelope.
- No API key, session cookie, Desktop AI credential, or auth token in Godot,
  clipboard snapshots, bridge files, logs, saves or prompt recipes.
- No client-authoritative inventory, ownership, currency or marketplace state.
- No arbitrary generated scripts or shaders in authoritative runtime.
- No Matrix/Oasis video state treated as collision/navigation/world state.
- No real-city branding/data import without source and license record.
- No blockchain dependency in MVP.
- No free-form 3D world, spherical planets or voxel digging on the MVP critical path.
- No TTS model, voice cloning or raw-audio pipeline on the MVP critical path.

Do not translate product, security or UX recommendations into a deprecated or
parallel stack. Propose an ADR if this lock must change; do not silently diverge.

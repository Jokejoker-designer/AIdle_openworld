# Agent Integration Guide – AIdle Openworld (Agent-Core base)

**Core version:** `0.1.0-core`  
**Blueprint:** Master Blueprint v1.0  
**Project root:** `E:\AIdle_openworld\game`

This document is the contract for **Agent-Voxel, Companion, Executor, Network, Schema, Asset, Persist** to attach without breaking Core hierarchy.

---

## 1. Reality Hierarchy (LOCKED)

Do **not** rename or re-parent these nodes under `WorldRoot`:

```
WorldRoot
├── PrivateReality          # client-authoritative
│   └── ManifestationHost   # Agent-Voxel spawns progressive builds HERE
├── SharedDistricts         # server-authoritative
│   └── ManifestationHost
├── DoppelgangerCities      # server + community hub
│   └── ManifestationHost
├── Orbital                 # owner-authoritative (spacecraft)
│   └── ManifestationHost
├── Exoplanets              # owner / shared
│   └── ManifestationHost
├── ModuleMounts
│   ├── VoxelMount
│   ├── CompanionMount
│   ├── ExecutorMount
│   ├── NetworkMount
│   ├── SchemaMount
│   ├── AssetMount
│   └── PersistMount
└── Systems                 # lighting, ground, environment (Core)
```

Access helpers:

```gdscript
var world := GameManager.world_root as WorldRoot
var host := world.get_manifestation_host("private_reality")
var space := world.get_space_node("shared_district")
```

---

## 2. Autoloads (always available)

| Autoload | Role |
|----------|------|
| `EventBus` | Common Contracts events |
| `SettingsManager` | Audio/graphics/debug prefs → `user://settings.cfg` |
| `ArtStyleManager` | Active art style + `user://world_meta.cfg` |
| `ProvenanceLogger` | Append-only provenance log |
| `ModuleRegistry` | Register modules + mounts |
| `GameManager` | Session, pause, player/world refs |

**Art style hard rule:** before generating any visual content:

```gdscript
var style: Dictionary = ArtStyleManager.query_art_style_for_generation()
# style.id, style.palette, style.geometry_bias, ...
```

---

## 3. How to register a module (any Agent)

```gdscript
# In your module root script _ready():
extends Node

func _ready() -> void:
    ModuleRegistry.attach_to_mount(AIdleConstants.MODULE_VOXEL, self)
    ModuleRegistry.register_module(AIdleConstants.MODULE_VOXEL, self)
```

Module IDs (from `AIdleConstants`):

- `voxel` · `companion` · `executor` · `network` · `schema` · `asset` · `persist`

Core ships **stubs** so mounts are never “undefined”. Your real module **replaces** the stub by registering the same id.

Validate your surface against Core interfaces:

```gdscript
var missing := IVoxelModule.validate(self)
assert(missing.is_empty(), "Missing voxel API: %s" % missing)
```

Interface reference scripts live in:

`res://scripts/modules/interfaces/`

---

## 4. Per-agent attach notes

### Agent-Schema
- Parent under `SchemaMount`.
- Implement `validate_prompt(data) -> {ok, errors, normalized}` and `get_schema_version()`.
- Executor depends on you; finish before production Executor flow.

### Agent-Voxel
- Parent under `VoxelMount`.
- Spawn progressive meshes under `WorldRoot.get_manifestation_host(space_id)`.
- API: `start_manifestation` / `update_construction_progress` / `finalize_manifestation` / `cancel_manifestation`.
- **Never** instant-spawn solids. Stages: wireframe → hologram → materializing → complete.
- Emit `EventBus.manifestation_*` signals with `prompt_id` + provenance.

### Agent-Companion
- Parent under `CompanionMount`.
- Follow player; Mood Aura; Manifestation Device VFX hooks.
- World changes: **only** via Executor (`submit_prompt`), never Voxel directly.
- Emit `emotional_state_changed`, `random_alchemist_gift`.

### Agent-Executor
- Parent under `ExecutorMount`.
- Pipeline: validate (Schema) → Voxel (+ Asset) → Provenance + events.
- Respect `RealitySpace.authority`.

### Agent-Network
- Parent under `NetworkMount`.
- Sync manifestation progress + aura; honor authority model.
- Listen to `EventBus` rather than polling modules.

### Agent-Asset
- Parent under `AssetMount`.
- Query `ArtStyleManager` for palette/materials.

### Agent-Persist
- Parent under `PersistMount`.
- Listen `manifestation_completed` / visit events; never mutate provenance after commit.

---

## 5. EventBus checklist (Common Contracts)

| Signal | Emit when |
|--------|-----------|
| `manifestation_started` | Build begins |
| `manifestation_progress_updated` | progress 0..1 + stage |
| `manifestation_completed` | progress = 1 + collision on |
| `manifestation_cancelled` | abort / timeout |
| `random_alchemist_gift` | Companion gift |
| `emotional_state_changed` | Mood / aura change |
| `player_entered_space` | Zone transition |
| `visit_requested` / `visit_accepted` | Social visit flow |
| `art_style_changed` | Style switch (rare after boot) |

---

## 6. Recommended code layout for other agents

```
res://
  modules/
    voxel/          # Agent-Voxel
    companion/      # Agent-Companion
    executor/
    network/
    schema/
    asset/
    persist/
```

Keep Core folders (`autoload/`, `scenes/world/`, `scripts/core/`) stable. Add under `modules/` or your agent folder; register at runtime.

---

## 7. Do / Don’t

**Do**
- Use Structured World Prompt as the only world-mutation contract.
- Query art style before generation.
- Attach under ModuleMounts + ManifestationHost.
- Log provenance via `ProvenanceLogger` / EventBus completed.

**Don’t**
- Rename WorldRoot hierarchy nodes.
- Call Voxel from Companion.
- Skip progressive construction stages.
- Delete or rewrite committed provenance.

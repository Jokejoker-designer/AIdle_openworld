# System Architecture

Current pins: Blender `5.2.0 LTS` at `E:/blender.exe`; Bridge root
`E:/AIdle_Blender_Bridge_P0`; Godot `4.3-stable`.

```text
Grok World Genesis Orchestrator
        │
        ├── World Concept Agent
        ├── Environment Layout Agent
        ├── Architecture Kit Agent
        ├── Nature/Biome Agent
        ├── Lighting Agent
        ├── Technical Optimization Agent
        └── QA/Review Agents
        │
        ▼
AIdle Blender Bridge API
        │
        ├── Environment Schema Validator
        ├── World Style Profile Registry
        ├── Module Registry
        ├── Material Registry
        ├── Scene Template Registry
        ├── Operation Allowlist
        ├── Job/Lease Manager
        └── Resource Policy
        │
        ▼
Blender Environment Worker
        │
        ├── Terrain Builder
        ├── Modular Architecture Assembler
        ├── Nature Scatter Builder
        ├── Landmark Builder
        ├── Lighting/Camera Preview Builder
        ├── LOD/HLOD Generator
        ├── Collision Hint Generator
        ├── Exporter
        └── Validator
        │
        ▼
Generated Quarantine
        │
        ├── GLB modules
        ├── Scene manifest
        ├── Preview renders
        ├── Metrics
        ├── Logs/hashes
        └── Provenance
        │
        ▼
Godot Intake Harness
        │
        ├── Import
        ├── Instantiate chunks
        ├── Bake navigation
        ├── Apply runtime collision
        ├── Test camera/occlusion
        ├── Test manifestation stages
        └── Save/reload regression
```

## Components

### Environment Gateway

Mở rộng FastAPI P0 với:

```text
GET  /v1/environment/templates
GET  /v1/environment/modules
GET  /v1/environment/world-profiles
POST /v1/environment/jobs
GET  /v1/environment/jobs/{job_id}
POST /v1/environment/jobs/{job_id}/cancel
POST /v1/environment/jobs/{job_id}/validate
POST /v1/environment/jobs/{job_id}/render
GET  /v1/environment/jobs/{job_id}/artifacts
```

Không tạo endpoint thực thi Python hoặc shell.

### Blender Worker profiles

```text
environment_module_worker
starter_realm_assembler
world_seed_diorama_worker
terrain_chunk_worker
preview_render_worker
```

P0E chỉ cần `starter_realm_probe_worker`.

## Shared Bridge authority

Environment jobs extend the existing Character Bridge rather than creating a
parallel authority plane. Both job types share configuration, path policy,
job store, lifecycle receipts, quarantine and the global `max_active_jobs = 1`
lease. They use separate request models, services and Blender entrypoints to
reduce blast radius.

The public request never carries an absolute output directory. The service
creates an internal spec containing the server-owned quarantine path and then
invokes Blender. A direct CLI run is useful for command-contract diagnosis but
does not prove the API lifecycle.

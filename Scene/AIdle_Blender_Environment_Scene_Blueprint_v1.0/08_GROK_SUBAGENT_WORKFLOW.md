# Grok Subagent Workflow for Exterior Scenes

## Installed routing profiles

Conceptual roles must route through installed profiles. P0E uses at most five
real Desktop children:

1. `schema` — contract/fixture review or an explicitly leased schema patch.
2. `aidle-worldgen-asset-art` — sole Blue product writer for Environment Bridge.
3. `aidle-worldgen-red-scope` — READ_ONLY_AUDIT findings only.
4. `aidle-worldgen-qa-evidence` — VERIFY_ONLY tests/evidence only.
5. `aidle-worldgen-purple-acceptance` — VERIFY_ONLY release gate, never patches.

Every child binds its TrustLayer character, UI character, authority token and
fully loaded skills from the project registries. Each significant step emits a
schema-valid `agent_step_contract` receipt with transcript refs, file lease,
commands/exits, hashes, trace/handoff and `self_accept=false`.

## Order

```text
WORK_ORDER
→ STYLE_LOCK
→ LAYOUT_GRAPH
→ TERRAIN_RECIPE
→ MODULE_PLAN
→ NATURE_PLAN
→ LIGHTING_PREVIEW_PLAN
→ ENVIRONMENT_BUILD_SPEC
→ BLENDER_JOB
→ QUARANTINE
→ GODOT_INTAKE
→ RED
→ REWORK
→ PURPLE
→ CODEX/HUMAN
```

## Parent authority

Parent Orchestrator:

- không patch product file
- giữ file lease
- tối đa 5 child
- không cho child spawn grandchild
- không tự ACCEPT
- không impersonate Codex hoặc Human Product Lead
- khi continuity active, chỉ tạo work order trong operating envelope hiện hành

## Blender Production Agent

Chỉ được gọi:

- inspect environment template
- inspect module registry
- create environment job
- get job status
- render preview
- validate environment package

Không được gọi shell/Python.

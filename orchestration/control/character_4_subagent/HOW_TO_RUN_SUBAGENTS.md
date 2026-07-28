# How to run the 4 subagents (mockup-matching Blender characters)

## Mental model

```
Mockup SSOT → character_spec → Orchestrator workspace
     → S1 head clay  ||  S2 body clay
     → S4 primary camera QA
     → FORM_LOCKED
     → S3 tech (rig/clips/GLB quarantine)
     → S4 tech QA
     → HUMAN_REVIEW → (Human only) ACCEPTED → promote game/**
```

## 1. Init a character job

```powershell
python orchestration/control/character_4_subagent/scripts/build_spec_from_mockup_ssot.py `
  --character-id CCP-RH-001 `
  --out orchestration/control/character_4_subagent/specs/nori7_character_spec.json

python orchestration/control/character_4_subagent/scripts/orchestrator_aidle.py init `
  --character-id CCP-RH-001 `
  --spec orchestration/control/character_4_subagent/specs/nori7_character_spec.json
```

Any MOCKUP_SSOT character id works (e.g. `CCP-NS-002` for Mây Mạch) — generate a new out path.

## 2. Advance + dispatch

```powershell
python .../orchestrator_aidle.py advance --character-id CCP-RH-001 --to CLAY_HEAD_BODY
python .../orchestrator_aidle.py dispatch --character-id CCP-RH-001 --agent S1
python .../orchestrator_aidle.py dispatch --character-id CCP-RH-001 --agent S2
```

Open:

- `run/CCP-RH-001/dispatch/S1_CLAY_HEAD_BODY_BRIEF.md`
- `run/CCP-RH-001/dispatch/S2_CLAY_HEAD_BODY_BRIEF.md`

Paste brief + upstream prompt into a **scoped subagent** (or human Blender session).

### Grok subagent tips

| Agent | capability | isolation | Tools |
|-------|------------|-----------|--------|
| S1 | read-write | worktree optional | Blender MCP write only S1 blend |
| S2 | read-write | worktree optional | Blender MCP write only S2 blend |
| S3 | read-write + execute | none | Blender + offline author scripts |
| S4 | read-only | none | Blender screenshot/info only |

## 3. Blender MCP (live)

Connected server tools (mapped in `blender_mcp_tool_map.json`):

- S1/S2/S3: `blender__execute_blender_code` **only** inside owned collection
- S4: `get_scene_info`, `get_viewport_screenshot` only

Before sculpting:

1. Import mockup as reference image empties at locked camera.
2. Create collections `S1_HEAD_HAIR_FACE` / `S2_BODY_CLOTHES` per contract.
3. Clay grey materials only until FORM_LOCKED.

## 4. Primary camera QA

After S1/S2 save previews to `evidence/primary_camera.png`:

```powershell
python .../orchestrator_aidle.py gate --character-id CCP-RH-001 --gate PRIMARY_CAMERA_QA
```

Pass → `advance --to FORM_LOCKED`  
Fail → change requests to owner in `qa/`.

## 5. Technical integration (S3)

```powershell
python .../orchestrator_aidle.py advance --character-id CCP-RH-001 --to TECH_INTEGRATION
python .../orchestrator_aidle.py dispatch --character-id CCP-RH-001 --agent S3
```

S3 may use offline scripts under `character_build/` (e.g. Nori full anim rekey) **after** form lock — never as a substitute for silhouette match.

Export only to:

- workspace `release/` or
- `E:/AIdle_Blender_Bridge_P0/storage/generated_quarantine/<JOB>/`

## 6. Never auto-promote

`advance --to ACCEPTED` is **blocked** in orchestrator.  
Human Product Lead only → then copy quarantine GLB into `game/assets/...` under a Build WO.

## Pilot status (Nori-7)

| Item | Path / state |
|------|----------------|
| Spec | `specs/nori7_character_spec.json` (15 clips, 14 bones) |
| Workspace | `run/CCP-RH-001/` |
| State | `CLAY_HEAD_BODY` (after advance) |
| Refs staged | `run/CCP-RH-001/references/char_01_nori7*.jpg` |

# AIdle · 4-Subagent Blender Character System (integration)

**Upstream (source kit):**  
`E:\agents\AIdle_4_Subagent_Blender_Character_System\aidle_character_4_subagents\`

**Purpose:** When building a character in Blender, route work through **Orchestrator + S1–S4** so the result tracks **MOCKUP_SSOT_V2** (CAMERA_LOCKED_MATCH), not free-form “one agent edits one giant blend”.

## Goals (honest)

| Goal | Meaning |
|------|---------|
| `CAMERA_LOCKED_MATCH` | Near-indistinguishable on mockup primary camera |
| `STYLE_LOCK_MATCH` | Silhouette, proportions, palette, form language |
| `TECHNICAL_VALID` | Topology, 14-bone robot / family rig, exact clip names, GLB |
| `HUMAN_ACCEPTED` | Only Human sets `accepted=true` |

Do **not** claim full 3D geometry fidelity for angles absent from a 2D mockup.

## Agents

| Agent | Owns | Does not |
|-------|------|----------|
| **Orchestrator** | `spec/character_spec.json`, state machine, release promote | Sculpt |
| **S1** | Head / face / hair / eyes (`work/S1_*.blend`) | Body |
| **S2** | Body / clothes / limbs (`work/S2_*.blend`) | Head |
| **S3** | Append locked collections → retopo / UV / mat / rig / clips / GLB | Silhouette redesign |
| **S4** | Read-only QA + change requests | Mesh patch, self-accept |

## Bindings into AIdle Openworld

| AIdle source | Role |
|--------------|------|
| `orchestration/control/visual_reference/mockup_ssot_v2/` | Mockup SSOT (images + JSON) |
| `game/assets/ucbv_001/character/nori7/` | Production Nori-7 proof case |
| `orchestration/control/object_dna_card_system/` | Skeleton family + clip packages |
| `orchestration/control/character_build/author_*.py` | Offline Blender author jobs (S3-adjacent) |
| Blender MCP (`blender__*`) | Live scene tools for S1–S4 (scoped) |

## Quick start — Nori-7 pilot

```powershell
# 1) Build / refresh character_spec from MOCKUP_SSOT_V2
python E:\AIdle_openworld\orchestration\control\character_4_subagent\scripts\build_spec_from_mockup_ssot.py `
  --character-id CCP-RH-001 `
  --out E:\AIdle_openworld\orchestration\control\character_4_subagent\specs\nori7_character_spec.json

# 2) Init workspace + job state
python E:\AIdle_openworld\orchestration\control\character_4_subagent\scripts\orchestrator_aidle.py init `
  --character-id CCP-RH-001 `
  --spec E:\AIdle_openworld\orchestration\control\character_4_subagent\specs\nori7_character_spec.json

# 3) Print dispatch packets (paste into subagent / MCP session)
python E:\AIdle_openworld\orchestration\control\character_4_subagent\scripts\orchestrator_aidle.py dispatch `
  --character-id CCP-RH-001 --agent S1

# 4) After S1/S2 clay: run S4 primary gate (file/metrics scaffold)
python E:\AIdle_openworld\orchestration\control\character_4_subagent\scripts\orchestrator_aidle.py gate `
  --character-id CCP-RH-001 --gate PRIMARY_CAMERA_QA
```

## State machine

`INTAKE → SPEC_LOCKED → CLAY_HEAD_BODY → PRIMARY_CAMERA_QA → FORM_LOCKED →
TECH_INTEGRATION → TECH_QA → HUMAN_REVIEW → ACCEPTED`

Fails → `CHANGES_REQUESTED` → owner agent only.

## One writer rule

See upstream `README.md` + `blender/BLENDER_COLLECTION_CONTRACT.md`.  
This integration **does not** allow S1 to open S2 blends for write.

## Status

| Item | Status |
|------|--------|
| Contracts / prompts / state machine | Integrated from upstream |
| Spec builder (MOCKUP_SSOT) | Implemented |
| Orchestrator workspace + dispatch packets | Implemented |
| Live multi-agent MCP sculpt loop | **Human-supervised** (dispatch packets + Blender MCP) |
| Auto-promote to `game/**` | **Forbidden** without Human accept |

`accepted=false` · `self_accept=false` on all machine outputs.

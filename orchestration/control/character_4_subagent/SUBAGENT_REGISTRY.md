# Subagent registry — Character 4-crew (Blender mockup match)

| ID | Role | TrustLayer analogue | Write path |
|----|------|---------------------|------------|
| ORCH | Orchestrator | Conductor | `spec/character_spec.json`, job state |
| S1 | Head/Hair/Face | Blue (scoped) | `work/S1_head_hair_face.blend` |
| S2 | Body/Clothes | Blue (scoped) | `work/S2_body_clothes.blend` |
| S3 | Tech integration | Blue (export) | `work/S3_character_integration.blend` + quarantine |
| S4 | Visual QA | Purple (no patch) | `qa/qa_report.json` only |

## Source kit

`E:\agents\AIdle_4_Subagent_Blender_Character_System\aidle_character_4_subagents`

## Integration

`E:\AIdle_openworld\orchestration\control\character_4_subagent`

## Rules

- Red/Purple never patch mesh.
- No self-accept.
- Mockup SSOT is design truth; runtime promote is separate Build WO.

# Dispatch S4 — CCP-RH-001

**State:** `SPEC_LOCKED`  
**Write only:** `E:\AIdle_openworld\orchestration\control\character_4_subagent\run\CCP-RH-001\qa\qa_report.json`  
**Prompt:** `E:\agents\AIdle_4_Subagent_Blender_Character_System\aidle_character_4_subagents\prompts\S4_VISUAL_QA.md`

## Hard rules
- One writer; no self-accept; no game/** promote
- Match mockup primary camera (CAMERA_LOCKED_MATCH)
- Clips exact: ['idle', 'walk', 'scan', 'happy', 'cancel', 'turn_left', 'turn_right', 'build_place', 'build_place_hold', 'confirm', 'water', 'plant_seed', 'harvest', 'charge', 'low_energy']
- Skeleton family: robot_biped_small_v1

## MCP tools allowed
```json
{
  "allowed_mcp": [
    "blender__get_scene_info",
    "blender__get_object_info",
    "blender__get_viewport_screenshot"
  ],
  "forbidden_mcp": [
    "blender__execute_blender_code"
  ],
  "notes": "Read-only. Prefer offline render + metrics scripts. Verdict max: PASS_FOR_HUMAN_REVIEW."
}
```

## Upstream prompt (open full file)
E:\agents\AIdle_4_Subagent_Blender_Character_System\aidle_character_4_subagents\prompts\S4_VISUAL_QA.md

## Spec
E:\AIdle_openworld\orchestration\control\character_4_subagent\run\CCP-RH-001\spec\character_spec.json

## References
E:\AIdle_openworld\orchestration\control\character_4_subagent\run\CCP-RH-001\references

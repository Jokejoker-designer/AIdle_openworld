# Dispatch S2 — CCP-RH-001

**State:** `CLAY_HEAD_BODY`  
**Write only:** `E:\AIdle_openworld\orchestration\control\character_4_subagent\run\CCP-RH-001\work\S2_body_clothes.blend`  
**Prompt:** `E:\agents\AIdle_4_Subagent_Blender_Character_System\aidle_character_4_subagents\prompts\S2_BODY_CLOTHES.md`

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
    "blender__get_viewport_screenshot",
    "blender__execute_blender_code"
  ],
  "code_scope": "Only collections under S2_BODY_CLOTHES; save only work/S2_body_clothes.blend",
  "forbidden": [
    "edit S1 collections",
    "export release GLB",
    "self_accept"
  ]
}
```

## Upstream prompt (open full file)
E:\agents\AIdle_4_Subagent_Blender_Character_System\aidle_character_4_subagents\prompts\S2_BODY_CLOTHES.md

## Spec
E:\AIdle_openworld\orchestration\control\character_4_subagent\run\CCP-RH-001\spec\character_spec.json

## References
E:\AIdle_openworld\orchestration\control\character_4_subagent\run\CCP-RH-001\references

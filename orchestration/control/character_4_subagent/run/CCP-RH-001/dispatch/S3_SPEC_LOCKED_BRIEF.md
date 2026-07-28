# Dispatch S3 — CCP-RH-001

**State:** `SPEC_LOCKED`  
**Write only:** `E:\AIdle_openworld\orchestration\control\character_4_subagent\run\CCP-RH-001\work\S3_character_integration.blend`  
**Prompt:** `E:\agents\AIdle_4_Subagent_Blender_Character_System\aidle_character_4_subagents\prompts\S3_TECH_INTEGRATION.md`

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
  "code_scope": "Append approved collections; rig/anim/export to quarantine only",
  "offline_scripts": [
    "E:/AIdle_openworld/orchestration/control/character_build/author_nori7_gardener_clips_v1.py",
    "E:/AIdle_openworld/orchestration/control/character_build/author_nori7_mockup_parity_v1.py"
  ],
  "forbidden": [
    "sculpt silhouette after FORM_LOCKED without change request",
    "promote to game/** without Human"
  ]
}
```

## Upstream prompt (open full file)
E:\agents\AIdle_4_Subagent_Blender_Character_System\aidle_character_4_subagents\prompts\S3_TECH_INTEGRATION.md

## Spec
E:\AIdle_openworld\orchestration\control\character_4_subagent\run\CCP-RH-001\spec\character_spec.json

## References
E:\AIdle_openworld\orchestration\control\character_4_subagent\run\CCP-RH-001\references

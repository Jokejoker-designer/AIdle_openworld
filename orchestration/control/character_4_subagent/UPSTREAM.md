# Upstream pointer

| Field | Value |
|-------|--------|
| Kit root | `E:\agents\AIdle_4_Subagent_Blender_Character_System\aidle_character_4_subagents` |
| Integrated | 2026-07-24 / 2026-07-25 |
| Integration root | `E:\AIdle_openworld\orchestration\control\character_4_subagent` |

## Copy vs reference

| Asset | Policy |
|-------|--------|
| Schemas, example templates | **Referenced** (paths in `aidle_bridge.json`) |
| Prompts | **Referenced** + thin AIdle wrapper notes in `prompts/` |
| Orchestrator | **AIdle implementation** `scripts/orchestrator_aidle.py` (does not replace upstream skeleton; extends it) |
| State machine | Loaded from upstream `workflow/state_machine.json` |

If upstream kit moves, update `aidle_bridge.json` only.

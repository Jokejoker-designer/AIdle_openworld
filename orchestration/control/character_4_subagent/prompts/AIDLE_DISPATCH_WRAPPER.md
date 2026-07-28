# AIdle dispatch wrapper (read with upstream agent prompt)

You are running inside **AIdle Openworld** character reconstruction.

## Always load first
1. Workspace `spec/character_spec.json` (MOCKUP_SSOT bound)
2. Upstream role prompt (S1/S2/S3/S4 or Orchestrator)
3. `spec/BLENDER_COLLECTION_CONTRACT.md`
4. `AIDLE_GAME_VISION_LOCK_001.md` §12 mockup fidelity law

## Success criteria
- `CAMERA_LOCKED_MATCH` on primary mockup camera
- Exact animation clip names from `character_spec.clips`
- Skeleton family / bone budget from spec (`technical_budget`)
- `self_accept=false` · never `accepted=true`

## Blender MCP
Use only tools listed in your dispatch packet `mcp.allowed_mcp`.  
S4: **no** `blender__execute_blender_code`.

## Write path
Only the path in dispatch `write_path_only`.

## Handoff
Emit agent receipt JSON under workspace `qa/` or next to owned blend, with artifact hashes.

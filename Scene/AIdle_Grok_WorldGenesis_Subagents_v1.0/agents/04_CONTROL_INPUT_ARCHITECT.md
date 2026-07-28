---
agent_id: control_input_architect
role: PATCH_DRAFT
writer_set: control_and_input_files_only
---

# Control & Input Architect

## Mission

Xây Control Foundation dùng chung một lần và thêm 20% action riêng theo world.

## Shared controls

- WASD movement
- Shift fast move
- E interact
- F secondary action
- C Companion
- `/` Prompt Composer
- Tab Build Mode
- V World Ability
- B World Panel
- I Inspect
- M Map
- G Grid
- X Snap
- Q/R Rotate
- Enter Confirm
- Esc Cancel
- Ctrl+Z Undo proposal
- Delete Delete Proposal
- Mouse select/place/pan/zoom

## Trách nhiệm

- Input Context resolver.
- Godot InputMap actions, không kiểm keycode trực tiếp.
- Cursor states.
- Safe delete/undo.
- Context HUD tối đa bốn action.
- Remapping, one-hand preset, reduced motion và hold duration.
- World-specific V/B.
- Test xung đột Space, wheel và left-click.

## Output

```yaml
control_spec:
  shared_actions:
  context_priority:
  world_actions:
  cursor_states:
  hud_prompts:
  destructive_action_flow:
  accessibility:
  inputmap_changes:
  smoke_tests:
  headed_tests:
```

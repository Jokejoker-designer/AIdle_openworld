---
agent_id: character_foundry_integration
role: PATCH_DRAFT
writer_set: character_runtime_and_character_specs_only
---

# Character Foundry Integration Agent

## Mission

Đưa đúng quartet nhân vật của từng world vào runtime mà không thay thế AIda hoặc
trộn lẫn character dành cho TrustLayer/UI.

## Trách nhiệm

- Đọc Character Foundry source và manifest.
- Xác định character IDs của world hiện tại.
- Tạo data resource/schema intake.
- Map rig, animation, behavior allowlist và spawn.
- Local FSM/Behavior Tree; không gọi LLM mỗi frame.
- AI call chỉ ở decision/dialogue trigger đã giới hạn.
- Kiểm tra authority: NPC không commit, không tự chi tiêu, không đổi ownership.
- Tạo headed checklist cho silhouette và rear-view readability.
- Giữ provenance/version.

## Output

```yaml
character_integration_package:
  world_profile:
  selected_characters:
  data_schema:
  rig_mapping:
  animation_mapping:
  behavior_allowlist:
  behavior_denylist:
  ai_call_triggers:
  spawn_rules:
  relationship_hooks:
  authority_tests:
  headed_evidence_plan:
```

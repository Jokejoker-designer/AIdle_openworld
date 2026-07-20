# AIdle Openworld – Structured World Prompt Schema

**Phiên bản Schema:** 1.0  
**Trạng thái:** Khóa cứng – Hợp đồng duy nhất giữa tất cả Agent

---

## Mục đích

Structured World Prompt là **ngôn ngữ trung gian duy nhất** giữa ý định của người chơi / Companion và hệ thống thực thi thế giới. Không Agent nào được phép tạo thay đổi thế giới mà không đi qua schema này.

---

## Schema chính (JSON Schema rút gọn – phiên bản đầy đủ nằm trong code Validator)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "AIdleStructuredWorldPrompt",
  "type": "object",
  "required": ["prompt_id", "schema_version", "intent", "target_space", "art_style", "manifestation", "provenance"],
  "properties": {
    "prompt_id": { "type": "string", "format": "uuid" },
    "schema_version": { "type": "string", "const": "1.0" },
    "intent": {
      "type": "object",
      "required": ["natural_language", "parsed_goal"],
      "properties": {
        "natural_language": { "type": "string" },
        "parsed_goal": { "type": "string" },
        "tags": { "type": "array", "items": { "type": "string" } }
      }
    },
    "target_space": {
      "type": "string",
      "enum": ["private_reality", "shared_district", "doppelganger_city", "spacecraft", "exoplanet", "open_continuum"]
    },
    "art_style": {
      "type": "string",
      "enum": ["cozy_cyber_pixel", "surrealism_canvas", "cyberpunk_dense", "pastoral_fantasy", "custom"]
    },
    "geometry": {
      "type": "object",
      "properties": {
        "type": { "type": "string", "enum": ["voxel_structure", "modular_prefab", "terrain_mod", "prop", "creature"] },
        "bounding_box": { "type": "object" },
        "voxel_data_ref": { "type": "string" },
        "prefab_id": { "type": "string" }
      }
    },
    "manifestation": {
      "type": "object",
      "required": ["stages", "estimated_duration_seconds"],
      "properties": {
        "stages": {
          "type": "array",
          "items": { "type": "string", "enum": ["wireframe", "hologram", "materializing", "complete"] }
        },
        "construction_progress": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "estimated_duration_seconds": { "type": "number" }
      }
    },
    "behaviors": { "type": "array", "items": { "type": "object" } },
    "interactions": { "type": "array", "items": { "type": "object" } },
    "provenance": {
      "type": "object",
      "required": ["requested_by", "generated_by", "timestamp", "source_type"],
      "properties": {
        "requested_by": { "type": "string" },
        "generated_by": { "type": "string" },
        "companion_id": { "type": "string" },
        "source_type": { "type": "string", "enum": ["player_request", "companion_enrichment", "random_alchemist", "system"] },
        "timestamp": { "type": "string", "format": "date-time" },
        "parent_prompt_id": { "type": "string" }
      }
    },
    "emotional_context": {
      "type": "object",
      "properties": {
        "companion_mood": { "type": "string" },
        "player_sentiment": { "type": "string" }
      }
    }
  }
}
```

---

## Các quy tắc quan trọng

1. `art_style` phải khớp với Art Style đang active của không gian.
2. `manifestation.stages` phải luôn bắt đầu từ `wireframe`.
3. `provenance.source_type = "random_alchemist"` chỉ được phép khi Companion kích hoạt Random Alchemist.
4. Mọi Prompt phải có `prompt_id` duy nhất (UUID).
5. Validator phải từ chối Prompt thiếu required fields hoặc có giá trị ngoài enum.

---

## Ví dụ tối thiểu hợp lệ

```json
{
  "prompt_id": "550e8400-e29b-41d4-a716-446655440000",
  "schema_version": "1.0",
  "intent": {
    "natural_language": "Xây cho tôi một ngôi nhà gỗ nhỏ kiểu Stardew với mái rêu và đèn lồng ấm",
    "parsed_goal": "create_cozy_wooden_house",
    "tags": ["house", "cozy", "farm"]
  },
  "target_space": "private_reality",
  "art_style": "cozy_cyber_pixel",
  "geometry": {
    "type": "voxel_structure",
    "bounding_box": {"x": 8, "y": 6, "z": 8}
  },
  "manifestation": {
    "stages": ["wireframe", "hologram", "materializing", "complete"],
    "construction_progress": 0.0,
    "estimated_duration_seconds": 12
  },
  "provenance": {
    "requested_by": "player_123",
    "generated_by": "companion_456",
    "source_type": "player_request",
    "timestamp": "2026-07-20T14:30:00Z"
  }
}
```

---

**Agent-Schema chịu trách nhiệm cung cấp bản JSON Schema đầy đủ + Validator code + bộ test cases.**

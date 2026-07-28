# Character Specification Schema

```yaml
character_id: string
display_name: string
world_profile: enum
character_class: enum
species_form: string
gameplay_role: string
narrative_role: string
size_class: [TINY, SMALL, PLAYER_SCALE, TALL, LARGE, LANDMARK]
silhouette_family: string
shape_language: string
primary_palette: [string]
secondary_palette: [string]
material_family: [string]
face_language: string
costume_body_details: string
signature_prop: string
locomotion: string
idle_behavior: string
interaction_behavior: string
personality_traits: [string]
dialogue_style: string
world_ability: string
player_benefit: string
limitation: string
spawn_location: string
relationship_hooks: [string]
animation_set: [string]
vfx_aura: string
audio_identity: string
rig_family: string
lod_class: string
behavior_allowlist: [string]
behavior_denylist: [string]
provenance:
  creator: string
  source_prompt_id: string
  version: string
  reviewer: string
```

## Character Class

- `COMPANION`
- `NPC_GUIDE`
- `NPC_WORKER`
- `NPC_SOCIAL`
- `NPC_QUEST`
- `CREATURE_TAMEABLE`
- `CREATURE_AMBIENT`
- `ROBOT_HELPER`
- `SPIRIT_ENTITY`
- `CONSTRUCT`

## Quy tắc

1. Một nhân vật mới phải có gameplay role thật.
2. Ability luôn đi cùng limitation.
3. AI behavior chỉ được gọi action allowlisted.
4. Nhân vật không được commit world mutation.
5. Một biến thể chỉ đổi màu được xem là skin, không phải character mới.
6. Silhouette, prop, movement và idle không được cùng lúc trùng với một nhân vật hiện có.

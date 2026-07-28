# Master Prompt Template — Tạo nhân vật AIdle mới

```text
Generate one original character for the AIdle Character Foundry.

WORLD:
[WORLD_NAME]

WORLD VISUAL RULES:
[WORLD_STYLE_RULES]

CHARACTER PARAMETERS:
- Character class: [CLASS]
- Gameplay role: [ROLE]
- Narrative role: [NARRATIVE_ROLE]
- Species/form: [FORM]
- Size class: [SIZE]
- Silhouette family: [SILHOUETTE]
- Shape language: [SHAPE_LANGUAGE]
- Movement type: [MOVEMENT]
- Personality triad: [TRAIT_1], [TRAIT_2], [TRAIT_3]
- Limitation: [LIMITATION]
- Signature prop: [PROP]
- World ability: [ABILITY]
- Main material: [MATERIAL]
- Main colors: [COLORS]
- Spawn location: [SPAWN]
- Relationship hook: [RELATIONSHIP]

REQUIREMENTS:
1. Create a unique readable silhouette for a fixed three-quarter isometric camera.
2. Include one recognizable feature visible from behind.
3. Use no more than three dominant color families.
4. Connect the visual design to the gameplay role.
5. Give the character one useful ability and one meaningful limitation.
6. Do not copy existing game, film, animation or toy characters.
7. Do not use photorealism or dense surface detail.
8. Provide front, side, back and three-quarter views.
9. Provide idle, locomotion, interaction, refusal and signature animation descriptions.
10. Provide dialogue style without unrestricted AI agency.
11. State the reusable rig family or explain why a new rig is required.
12. AI behavior must be allowlisted and cannot mutate canonical world state directly.

OUTPUT:
- Character ID proposal
- Character name
- One-sentence hook
- Visual description
- Silhouette description
- Rear-view readability feature
- Personality
- Dialogue style
- Gameplay role
- Ability
- Limitation
- Spawn location
- Relationship hook
- Animation list
- Audio identity
- Production prompt
- Negative prompt additions
- Reusable rig family
- Behavior allowlist
- Behavior denylist
- Quality gate checklist
```

## Công thức nhân rộng

`WORLD + CLASS + ROLE + SILHOUETTE + SIZE + MATERIAL + PROP + MOVEMENT + PERSONALITY TRIAD + ABILITY + LIMITATION`

## Ma trận chống trùng

Trước khi chấp nhận nhân vật mới, so sánh:

- silhouette
- head feature
- signature prop
- movement
- color grouping
- gameplay role
- personality triad
- world ability
- idle animation
- rig family

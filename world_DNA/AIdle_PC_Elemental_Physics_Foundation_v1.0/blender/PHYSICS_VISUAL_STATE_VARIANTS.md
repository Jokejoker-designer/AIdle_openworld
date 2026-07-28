# Physics Visual State Variants

Use fixed intact/damaged/broken/wet/frozen/burning/corroded/restored variants.
Godot selects variants from deterministic state. High-end debris/particles are
noncanonical presentation.

## World-profile visual variants (WO-P1E-006 extension)

**Same mechanism, additional selector.** Do not invent a parallel STYLE_VARIANTS
system.

| Selector | Selects |
|----------|---------|
| Physics **state** | wet / frozen / restored / … mesh-material variant |
| **World profile** | `cozy_cyber_pixel` / `surrealism_canvas` (content axis) |

Runtime catalog (AIdle Openworld):
`game/resources/world_profiles/state_visual_variants.json`

- Active art style maps to nearest world profile (`art_style_to_world_profile`).
- `cozy_cyber_pixel` variant mode = **identity_register** (current kit materials;
  no re-author).
- `surrealism_canvas` = material table (purple accent, readable; not void wash).
- Profiles without kits (P2E–P6E) fall back to cozy identity until content lands.
- Art styles without world profiles (`cyberpunk_dense`, `pastoral_fantasy`) use
  nearest profile presentation mapping only — no dedicated art.

Godot applies via `world_profile_variant_selector.gd` after GLB intake attach.

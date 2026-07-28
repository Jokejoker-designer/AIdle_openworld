# Headed visual evidence QA (permanent)

**Status:** ACTIVE · 2026-07-22  
**Trigger:** P1E-004 live vs evidence discrepancy (style mismatch).  
**Rule:** A visual claim without `art_style_id_active` is **incomplete**.

## Required fields on every headed / visual claim

| Field | Required | Description |
|-------|----------|-------------|
| `art_style_id_active` | **YES** | Exact style id at capture (`cozy_cyber_pixel`, `surrealism_canvas`, …). Use `unknown` only if honestly undeterminable. Use `n/a_blender_eevee` for Bridge package previews (no ArtStyleManager). |
| `capture_source` | **YES** | `godot_headed` \| `godot_headless_viewport` \| `blender_eevee` \| `unknown` |
| `package_job_id` | When realm is GLB-built | e.g. `BLD-…` or `procedural` |
| `world_profile` | When known | e.g. `cozy_cyber_pixel` package profile |
| `live_parity` | **YES** | `true` only if same build + same style the human will run; else `false` with reason |

## Incomplete receipt rule

Any receipt that asserts visual PASS/FAIL (pond colour, exposure charm, “kit looks right”, density aesthetics) **without** `art_style_id_active` is **incomplete** and must not be used as live-game proof.

## Capture implementation

- Godot headed harness (`game/scripts/core/headed_visual_smoke.gd`) must write `art_style_id_active` on every capture entry in the evidence manifest.
- Prefer a sidecar `*.visual_claim_meta.json` next to PNG when not using the harness.
- Blender package PNGs must state `capture_source=blender_eevee` and `art_style_id_active=n/a_blender_eevee` plus intended `world_profile` / kit style.

## Product note

Cozy kit + `COZY_ART_BIBLE_001` hexes are authored for **cozy_cyber_pixel**. Evidence captured under that style does not prove the live game under **surrealism_canvas** (or any other saved world_meta style).

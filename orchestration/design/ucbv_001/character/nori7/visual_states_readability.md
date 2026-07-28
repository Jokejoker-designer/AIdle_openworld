# Nori-7 Visual States & Dual-Resolution Readability — U2

Identity: **Nori-7 / CCP-RH-001**  
Style lock: `ucbv_001_style_lock_v1`  
Viewports: **1280×720** and **868×517**  
Authority: `PATCH_DRAFT` · Accepted: `false`

## 1. Purpose

Define how Nori-7 remains readable in **idle** and **build-interaction** contexts
without inventing U4 animation timings or a parallel state system. Color never
carries critical meaning alone.

## 2. Character readable visual states (minimum)

Aligned with U1 `character_readable_visual_states_min` and Foundry quality gate:

| State id | Pose / mass cues | Face / sprout | Non-color signals |
|---|---|---|---|
| `idle_happy` | Neutral plant; nozzle stowed; soft bob allowed later | Soft open eyes; sprout upright | Optional warm micro-emissive blink (not cyan) |
| `active_build` | Weight shift; nozzle extended toward build/plant point; arm forward | Eyes slightly wider / scan | Selection outline on target object + Nori focus ring if selected |
| `caution_needs_confirm` | Half-step hold; nozzle partial; body lean back ~5° | Eyes narrower; sprout tilt away from hazard | **Icon + label** “needs confirm”; dashed outline pattern |
| `low_energy_rest` | Lower center of mass; optional sit-charge silhouette later | Eyes half-lid; sprout droop ~15–25° | Dimmer (opacity) **and** rest icon — not color-only |

Full 12-clip Foundry set remains **U4** ownership (`anim_robot_gardener_v1`).

## 3. Build interaction encoding (world objects + character)

World build states reuse live/P2E language (not reinvented):

`preview` → `valid` → `invalid` → `selected` → `materializing` → `complete`

| Interaction beat | Character visual | World object visual | Shared rule |
|---|---|---|---|
| Approach / idle near kit | `idle_happy` | complete architecture full warm palette | Character cream ≠ wall cream value |
| Companion proposal (text) | idle or slight look-to-UI | no mutation | Text-only Companion; no identity swap |
| Preview placement | `active_build` aiming | translucent preview + outline | Preview glass/marker mats only on object |
| Valid snap | `active_build` confident plant | solid-edge valid pattern | Outline pattern + icon, not green-only |
| Invalid surface | `caution_needs_confirm` | invalid pattern (e.g. dashed/hash) | Label + pattern required |
| Confirm pending | `caution_needs_confirm` | hold preview | Player confirm required |
| Manifestation | watch / modest bob | **4 stages only** | wireframe → hologram → materializing → complete |
| Complete | `idle_happy` or react positive (U4) | full materials + shadow | Collision only after confirm + World Commit |

### Manifestation stage chrome (locked 4)

| Stage | Object look | Character duty |
|---|---|---|
| wireframe | Cyan edges `#3fd0e0`, pulse, dashed centre | Do **not** recolor Nori body cyan |
| hologram | 22–30% fill, scan line | Keep ceramic palette; optional look-at |
| materializing | Bottom-up real materials; cyan above fill | Remain complete character; may point nozzle |
| complete | Full warm palette | Resume idle/happy |

Cyan is **manifestation language only**, never complete base-kit character paint.

## 4. Dual-resolution layout budgets

### 4.1 1280×720 (primary H1)

| Budget | Rule |
|---|---|
| Character height in mid-play | ~10–18% viewport height when near build focus |
| Minimum readable | ≥10% for interactive focus; if smaller, use LOD2 + sprout tip |
| Chrome | No overlapping diagnostic walls; Companion text separate |
| Silhouette edge | Dark soft contact shadow under pads; cream vs ground contrast |
| Face | Eyes must resolve (socket + iris) at mid distance; specular optional at far |

### 4.2 868×517 (secondary H1)

| Budget | Rule |
|---|---|
| Same composition scaled | Prefer fewer simultaneous chrome callouts |
| Character | Prefer slightly larger relative framing if UI denser — never clip sprout/tank |
| Thin features | No hairline meshes; nozzle stowed mass must stay ≥ ~3–4 px equivalent at this res when mid-frame |
| Text | Stage/state labels remain machine strings; UI type not redesigned here |

### Shared dual-res fail conditions

- Sprout or tank clipped by UI safe margins  
- Eyes lost → face reads as blank cream blob at mid distance  
- Invalid/valid distinguished only by hue  
- Character standing inside overlapping panels  
- Free-orbit framing in MVP art proofs  

## 5. Ambient motion references (not U4 clip table)

From COZY_ART_BIBLE / mockup reuse — **reference only**:

| Loop | Typical use | Duration cue |
|---|---|---|
| bob / bob_small | Idle body | ~2.4 s / ~3.0 s robot-ish |
| blink | Eyes | ~4.0 s; scaleY snap near end |
| sway | Sprout organic | ~3.6 s ± small angle |
| pulse | Manifestation wireframe edges | ~2.0 s |

`reduced_motion_supported`: replace continuous pulse/scan with **static stage chrome + opacity steps**; preserve stage order and labels.

## 6. Accessibility checklist

- [x] Critical state = outline / pattern / icon / label (color optional reinforce)
- [x] Eye socket `#3d3226` on cream for face contrast
- [x] ≤3 dominant palette groups on character
- [x] Rear features mandatory
- [x] Reduced-motion path defined
- [x] Dual viewports named with concrete budgets
- [x] No emotional coercion toward World Commit

## 7. Concept-art state icons (sheet)

Four small icons under turnaround sheet:

1. Idle happy — upright sprout, stowed nozzle  
2. Active build — extended nozzle, lean-in  
3. Caution needs-confirm — lean-back, dashed ring  
4. Low energy — drooped sprout, half-lid eyes  

These are static reference glyphs, not the full animation set.

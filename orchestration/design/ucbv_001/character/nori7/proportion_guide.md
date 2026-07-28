# Nori-7 Proportion Guide — U2

Identity: **Nori-7 / CCP-RH-001**  
Style lock: `ucbv_001_style_lock_v1`  
Silhouette family: `ucbv_cozy_rounded_readable_v1`  
Proportion system: **2 heads tall (chibi)**  
Authority: `PATCH_DRAFT` · Accepted: `false`

## 1. Head-unit system

| Symbol | Meaning |
|---|---|
| HU | Head Unit = vertical span of fused upper head/body bulb |
| Ground | Y=0 at foot-pad contact plane |
| Up | +Y |
| Forward | +Z toward face (side view) |
| Right | +X |

**Base standing height** (ground → top of ceramic body, excluding sprout) = **2.0 HU**.  
**Sprout tip** ≈ **2.40 HU** (±0.05).  
**Head radius** ≈ **0.50 HU** (diameter ≈ 1.0 HU) — matches U1 “head radius ≈ half body height” when body mass height ≈ 1.0 HU below apex of head sphere portion.

## 2. Vertical stack (front elevation)

| Band | Y range (HU) | Contents |
|---|---|---|
| Sprout | 2.00 – 2.40 | Mechanical stem + 1–2 leaf lobes |
| Head / upper teardrop | 1.00 – 2.00 | Face plane, eyes, sprout root socket |
| Mid body / lower teardrop | 0.45 – 1.00 | Arm roots, tank mid attach |
| Pelvis taper | 0.30 – 0.45 | Soft crotch split start |
| Legs | 0.00 – 0.35 | Short biped; foot pads 0.00 – 0.06 |

> Note: teardrop is continuous — bands are guide rails, not hard mesh cuts.

## 3. Width / depth budget

| Measure | Target (HU) | Notes |
|---|---|---|
| Max body width (front) | 1.00 – 1.10 | At ~Y=1.35 |
| Pelvis width | 0.50 – 0.60 | Above legs |
| Foot pad width each | 0.22 – 0.28 | Stable plant |
| Stance outer foot span | 0.55 – 0.70 | Not wide humanoid |
| Max body depth (side, no tank) | 0.85 – 0.95 | |
| Tank depth add | +0.35 – 0.40 | Behind back plane |
| Tank height | 0.55 – 0.65 | Centered mid-back |
| Tank width | 0.50 – 0.60 | |
| Eye height each | 0.20 – 0.24 | Large readable |
| Arm length (shoulder→wrist) | 0.45 – 0.55 | Short, chunky |
| Nozzle extended length | 0.40 – 0.55 | Action only |

## 4. Face proportion (front)

| Element | Placement |
|---|---|
| Eye line | ~Y = 1.45 – 1.55 |
| Eye outer span | Within 70% of head width |
| Specular | Up-left of each iris (~10 o'clock) |
| Blush | Below outer third of each eye; low opacity |
| Mouth | Optional soft line or none — expression via eyes/sprout preferred |

## 5. Bevel / roundness vs architecture

| | Character (Nori-7) | Block architecture (U3) |
|---|---|---|
| Outer corner | Higher readable roundness on primary mass | Soft bevel ~3–6% of local face |
| Joint language | Organic robot rings; **not** world-grid snap cubes | Grid-aligned modules with soft corners |
| Scale next to wall | Body cream slightly lighter than wall cream | Wall `#fdf3e2` family |

## 6. Scale against construction kit (nominal)

No meter CAD in catalog; `_4m` labels are nominal grid units. Use **relative screen mass** for H1 proofs:

| Context | Character screen height target |
|---|---|
| Near door of small house cluster | ~12–18% of viewport height |
| Mid garden path | ~10–15% (Foundry min readability) |
| Far ambient | may drop to billboard LOD2; sprout tip must remain |

Relative to a nominal wall module face height (1 grid tall in kit language):

- Nori-7 total height ≈ **0.45–0.55** of one wall module height (chibi helper, not adult human)

This is an art-direction ratio for mock composition, not physics collision truth.

## 7. Rig binding notes (informational — U4 owns bones)

Label skeleton: `skel_small_biped_robot_v1` / Foundry `Biped-small-robot-01`.

Suggested major joints for later hierarchy (not authored as production bones here):

1. root / pelvis  
2. spine_or_body (single or dual)  
3. head (may be body-fused with head_aim bone)  
4. leg_L / leg_R (+ optional foot)  
5. arm_L / arm_R  
6. aux: sprout, nozzle, tank (follow sockets)

Do **not** treat shared placeholder bones as production truth.

## 8. Proportion sheet panels

1. Front with 2-head grid boxes  
2. Side with depth callouts (body + tank)  
3. Back with sprout + tank dimensions  
4. Overlay on three-quarter  
5. Mini scale bar next to simplified wall/door glyph (not a real U3 mesh)

SVG: `sheets/nori7_proportion_grid.svg`.

## 9. Fail conditions

- Adult 6–8 head fashion proportions  
- Long thin limbs  
- Separate human neck  
- Tank smaller than rear-read budget  
- Sprout tip cut off in 15% screen-height test  
- Character joints snapping to world construction grid

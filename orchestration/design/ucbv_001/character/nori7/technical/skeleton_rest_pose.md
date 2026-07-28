# Skeleton rest pose notes — skel_small_biped_robot_v1

Production hierarchy for Nori-7. Units: meters. Y-up. Face +Z.

## Bone table

| # | Bone | Parent | Rest pos (m) | Role |
|--:|---|---|---|---|
| 0 | root | — | (0, 0, 0) | ground anchor |
| 1 | pelvis | root | (0, 0.22, 0) | hips / COM |
| 2 | spine | pelvis | (0, 0.18, 0.02) | lower mass |
| 3 | chest | spine | (0, 0.28, 0.03) | arms + tank |
| 4 | head | chest | (0, 0.32, 0.04) | face aim |
| 5 | arm_L | chest | (−0.28, 0.08, 0.02) | upper arm L |
| 6 | hand_L | arm_L | (−0.16, −0.10, 0.04) | hand L |
| 7 | arm_R | chest | (0.28, 0.08, 0.02) | upper arm R |
| 8 | hand_R | arm_R | (0.16, −0.10, 0.04) | tool hand |
| 9 | leg_L | pelvis | (−0.12, −0.02, 0) | leg L |
| 10 | foot_L | leg_L | (0, −0.14, 0.02) | pad L |
| 11 | leg_R | pelvis | (0.12, −0.02, 0) | leg R |
| 12 | foot_R | leg_R | (0, −0.14, 0.02) | pad R |
| 13 | sprout_ctrl | head | (0, 0.22, −0.02) | sprout sway |

Machine-readable:  
`game/assets/ucbv_001/character/nori7/skeleton/skel_small_biped_robot_v1.hierarchy.json`

## DNA placeholder mapping

| DNA placeholder | Production expansion |
|---|---|
| root | root |
| body | pelvis + spine + chest |
| head | head + sprout_ctrl |

Do not export only the three placeholder names as the live Skeleton3D.

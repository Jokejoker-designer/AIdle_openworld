# UCBV Visual Mockup 003 — animation timing provenance

Status: `REFERENCE — vector mockup, not final art, not a dispatch`
Companion to: `UCBV_VISUAL_MOCKUP_003_ANIMATED.html`
Extends: parts 1 and 2 (this pass adds motion only — no new ids, colours or decisions)
Prepared by: `aidle-continuity-conductor` (Claude, advisory support), 2026-07-22

Pure CSS `@keyframes`, no JavaScript. Open the HTML file in a browser to see it move —
static exports (PDF, screenshot, PNG) cannot show motion.

| Motion | Element(s) | Duration | Provenance |
|---|---|---|---|
| Idle bob | all 4 characters | 2.4 s, Y 0→−3→0 | **Real** — `COZY_ART_BIBLE_001.md` §4 "bob" |
| Blink | Nori-7 eyes | 4.0 s, scaleY snap to 0.1 at ~95% | **Real** — art bible §4 "blink" |
| Sprout sway | Nori-7 head ornament | 3.6 s, rotate ±2.5° | **Real** — art bible §4 "sway" (nearest organic-wobble entry; sprout isn't foliage but reuses the same motion family) |
| Flower sway_small | village scene, 3 stems | 4.2 s, staggered 0/0.5/1.1 s | **Real** — art bible §4 "sway_small" + explicit 0–1.5s stagger instruction |
| Tree foliage sway | village scene | 3.5 s | **Real** — art bible §4 "sway", within its stated 3.4–3.6s range |
| Garden lamp / door light pulse | village scene, manifestation stage 4 | 2.0 s | **Real** — art bible §4 "pulse" |
| Chimney steam | village scene | 2.6 s, staggered 0/0.9/1.7 s | **Real** — art bible §4 "steam_rise" |
| Wireframe pulse | manifestation stage 1 | 2.0 s | **Real** — art bible §7 explicitly assigns "pulse" to stage 1, and §4 gives pulse = 2.0s |
| Nozzle drip | Nori-7 hero | 1.8 s | **Illustrative** — the `water` clip exists in `anim_robot_gardener_v1` but no source file gives it a duration |
| Hologram scan line | manifestation stage 2 | 2.4 s | **Illustrative** — art bible §7 names "horizontal scan line", gives no duration |
| Materializing rise + sparks | manifestation stage 3 | 3.2 s / 1.6 s | **Illustrative** — §7 names "rising bottom-up" and "rising spark particles", gives no duration |

Nothing here changes an approved value. Where the art bible states an exact number, this
sheet uses it exactly. Where a source file only names an effect with no duration, the pacing
is a demo choice and is labelled illustrative so it is never mistaken for something Codex or
the Human Product Lead approved.

Scope unchanged from parts 1–2: visual reference only, step 2 of the UCBV sequencing lock.
`UCBV-001` remains `queued_not_authorized` per Directive 77 until Human PASS on the H1
five-minute gate and a new monotonic Codex directive.

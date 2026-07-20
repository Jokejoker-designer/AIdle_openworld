# G8-001 Human Acceptance Checklist — Local Godot 2.5D Alpha

**Purpose:** Manual headed verification after machine gate `PASS_FOR_HUMAN_REVIEW`.  
**Not automated.** Headless PASS does **not** complete this list.  
**Authority:** Human Product Lead (final alpha). Codex owns machine ACCEPT; Human owns play/presentation ACCEPT.

## Preconditions

- [ ] Godot **4.3** available (`tools/Godot_v4.3-stable_win64.exe` or system install)
- [ ] Project path: `E:\AIdle_openworld\game` (or workspace equivalent)
- [ ] No live API keys required for this checklist (Free path / fixture Paid path only)
- [ ] Machine package reviewed: `G8-001_ALPHA_EVIDENCE_REPORT.md` + matrix log green

## Launch

```text
# From repo root
tools\Godot_v4.3-stable_win64.exe --path game
```

- [ ] Project opens without SCRIPT / Parse / Compile errors in debugger
- [ ] Main scene boots into Private Reality (or boot → main flow completes)

---

## 1. Presentation (2.5D shell)

- [ ] Camera is **fixed-angle isometric / three-quarter** (not free-orbit FPS)
- [ ] Pitch does not free-look with mouse as FPS
- [ ] Ground plane / world readable; no black void only
- [ ] Art style loads (`cozy_cyber_pixel` or selected style) without missing-resource spam
- [ ] UI chrome readable (HUD / prompt entry if present)

**Fail if:** free 3D orbit camera, or project unplayable due to script errors.

---

## 2. Movement

- [ ] Player (`CharacterBody3D`) moves on **XZ** ground plane
- [ ] Movement feels grounded (not flying/noclip by default)
- [ ] Collision with ground works; character does not fall infinitely
- [ ] Camera follows or frames player acceptably for 2.5D play

**Fail if:** no locomotion, broken controller, or camera loses player permanently.

---

## 3. Prompt flow (onboarding / house)

- [ ] Can enter or trigger a **world prompt** path toward starter house
- [ ] Flow shows progressive construction stages (not instant silent world write)
- [ ] Explicit **confirm** step required before durable commit semantics (or clear handoff)
- [ ] Cancel / back path does not leave broken half-state without recovery

**Fail if:** prompt instantly mutates world with no preview/confirm; or flow hard-crashes.

---

## 4. Companion (text-only)

- [ ] Companion dialogue appears as **text** (chat/log/panel)
- [ ] Companion is useful for guidance/personality — not silent forever
- [ ] No requirement for microphone / STT / TTS to use Companion
- [ ] Companion **cannot** silently commit world mutations (no hidden “build now” world write without confirm path)

**Fail if:** voice stack required; or Companion tools commit world without confirm pipeline.

---

## 5. Manifestation stages

Observe build presentation for a structure (e.g. cozy house):

- [ ] Stage order visible: **wireframe → hologram → materializing → complete** (or equivalent progressive stages)
- [ ] Stages progress forward; no reverse-stage glitch under normal use
- [ ] At **complete**, presentation looks solid / finished enough for alpha demo

**Fail if:** stages skipped into a broken final mesh only, or reverse ordering under normal flow.

---

## 6. Manifestation cancel

- [ ] Cancel mid-manifestation returns to a safe state
- [ ] After cancel: no stuck solid collision ghost blocking movement
- [ ] After cancel: no orphan “half house” that acts as permanent blocker without cleanup path
- [ ] Re-start build after cancel still works

**Fail if:** cancel leaves permanent invisible walls or unremovable debris.

---

## 7. Save / reload (Private Reality)

- [ ] Save (or auto journal path) succeeds without crash
- [ ] Reload restores player-relevant state and built content consistent with last confirmed commit
- [ ] Reload does not require re-install or wiping user data unexpectedly
- [ ] Tamper is not required to test — happy path only for humans

**Fail if:** reload loses confirmed builds, or save corrupts session.

---

## 8. Edition choice (Free vs Paid)

- [ ] Can view or switch **edition** selection (Free Desktop Bridge / Paid API posture)
- [ ] Free path does **not** demand network or API key
- [ ] Paid path does **not** store raw `api_key` / `client_secret` in client settings (refuse/block expected)
- [ ] Same AGM contract language / UX framing for both (parity of “snapshot → decision → validate → confirm”)

**Fail if:** Free requires secrets; or Paid stores live secrets in plain client settings.

---

## Honesty gates (check boxes = understanding)

- [ ] I understand headless matrix PASS ≠ commercial alpha ship
- [ ] I understand G5 is **fixture/local** unless separately HITL’d for live provider
- [ ] I understand G6 is **local in-process POC**, not production multiplayer
- [ ] I will not claim “live AI multiplayer open world” from this checklist alone

---

## Sign-off

| Role | Name | Date | Result |
|---|---|---|---|
| Human Product Lead | | | PASS / FAIL / PASS_WITH_NOTES |
| Notes | | | |

**If FAIL:** open correction directive with evidence (screenshot + repro). Do not self-patch under G8-001.  
**If PASS:** Codex may record machine+human joint ACCEPT under a subsequent directive / control update — parent Grok does not self-ACCEPT.

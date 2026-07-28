# G8-001 UI Brief (U0 · schema · REPORT_ONLY)

**Characters:** TrustLayer `devil-advocate` · UI `ui-brief-writer`  
**Skills:** `od-design-brief` (full), `od-reference-design-contract` (full)  
**Binding truth:** `DESIGN.md`, `design-contract.md`, Dir21 screenshots  

## Problem (observed)

1. **Surrealism Canvas / purple field dominates** first headed captures — violates Cozy Cyber-Pixel default in DESIGN.md.
2. **Debug/session schema text** (Snapshot, Session, rev, personality rev) is player-facing.
3. **868×517 / 1280×720**: bottom action bar + companion + HUD hints **overlap**; long labels clip.
4. **Wireframe** reads as a solid gray box; stages not object-distinct enough.
5. **Bridge/Companion** share the same dark panel language; Bridge not labeled as *manual*.
6. **Confirm/Cancel** look active when disabled (low contrast distinction).

## Goals (falsifiable)

| ID | Criterion |
|---|---|
| B1 | Default headed view = Cozy Cyber-Pixel (warm ground `#C9B98A`, dawn sky `#9ED7E5`) unless player explicitly chose another style this session |
| B2 | Player HUD: art/space/edition + short control hints only; snapshot/session/schema text only when F3 debug on |
| B3 | At 1280×720 and 868×517: no control overlap covering player; action bar single row compact; companion above bar |
| B4 | Companion panel: turns, input, proposal status, privacy/history — text-only; no raw rev dumps |
| B5 | Bridge buttons labeled manual send/import; no credential affordance |
| B6 | Demo flow states: idle / previewing / confirmable / cancelled — buttons geometry-stable, disabled look disabled |
| B7 | Manifested object changes wireframe→hologram→materializing→complete on the mesh; banner is secondary |
| B8 | Cancel leaves no solid collision ghost |

## Anti-patterns (DESIGN.md)

No neon soup, no arbitrary purple as base, no tiny fonts, no full-screen prompt editor, no instant pop-in.

## Out of scope

Voice, live LLM, production multiplayer, new dependency, redesign from scratch.

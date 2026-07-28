# WO-C5H1-UX-002 — Mid-build companion_call + restore build context

Directive: **99** · Residuals: **R-C5H1-02**, **R-C5H1-03**
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852`
Authority: `PATCH_DRAFT` · TIER 1 · Human commercial-grade continue (2026-07-23)
Status: OPEN · `accepted=false` · no self-accept

## Scope

1. **R-C5H1-02:** Add `companion_call` to build context allow-list (parity with
   `prompt_quick_open` already allowed in build).
2. **R-C5H1-03:** When Companion opens from build, close returns to **build**
   (not exploration) if build mode / preview still active.

## Exact product write lease

- `game/scripts/input/control_action_catalog.gd`
- `game/scripts/main/main.gd`

## Forbidden

Confirm-gate change, InputMap rebind of unrelated actions, catalog/GLB, TIER3.

## Acceptance

- From build, KEY_C opens Companion (router allows companion_call).
- Close Companion while still mid-build → primary context **build**, locomotion
  appropriate for build, preview not force-cancelled by close alone.
- Existing C5H1 smoke still PASS; no new ERROR.

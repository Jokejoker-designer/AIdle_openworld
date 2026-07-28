# WO-COMMERCIAL-CTRL-1B-POLISH-001

Directive: **99** · TIER2 authorized by Human commercial-grade continue  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852`  
Profiles: **`aidle-worldgen-control-input`** (Blue) · `support-control-a11y` / QA for verify  
Authority: PATCH_DRAFT · `accepted=false`

## Goal

Close residual Control 1B commercial polish: a11y completeness, reduced-motion /
non-color state, binding discovery, any residual after R-C5H1-01/02/03.

## Exact product lease (must name before write)

Default audit-first. If patching, only these candidates (confirm in receipt which were written):

- `game/scripts/input/control_action_catalog.gd`
- `game/scripts/input/control_binding_manager.gd`
- `game/autoload/control_context_router.gd`
- `game/autoload/control_accessibility_settings.gd`
- `game/scripts/ui/context_action_hud.gd`
- `game/tests/control_1b_*.gd`

**Forbidden:** Confirm-gate change, World Commit authority, TIER3, network.

## Required

1. Run all `control_1b_*` smokes; decode logs.
2. Audit reduced_motion / hide-aura / color-independent state in code + settings.
3. Patch only proven gaps under named lease.
4. Re-run smokes; MAF receipt + evidence.

## Receipt path

`orchestration/receipts/commercial_ctrl_1b_001/**`

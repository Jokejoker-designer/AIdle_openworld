# WO-C5H1-UX-001 — HUD companion label: press E → KEY_C

Directive: **99** · Task: `C5H1-UX-RESIDUALS` · Residual: **R-C5H1-01**
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852`
Authority: `PATCH_DRAFT` · TIER 1 autonomous · narrow Godot override
Status: OPEN for Blue under sole parent · `accepted=false` · no self-accept

## Why

Human residual R-C5H1-01: HUD says "press E to chat" but `companion_call` is
bound to physical **KEY_C** (`control_binding_manager.gd`). E is `interact` /
`interact_primary`. Mislabel confuses playtesters.

## Exact write lease (one writer)

**Product:**
- `game/scripts/modules/g3_ui/starter_realm_panel.gd` only

**Orchestration (receipts/logs/evidence):**
- `orchestration/receipts/c5h1_ux_001/**`
- `orchestration/logs/c5h1_ux_001/**`
- `orchestration/evidence/c5h1_ux_001/**`

**Forbidden:** Confirm-gate change, InputMap rebind (label only this wave),
any other `game/**` file, catalog, GLB, directive rewrite.

## Required change

1. Default companion placeholder strings:
   - `"Companion: press E to chat"` → `"Companion: press C to chat"`
   - `"Companion: press E to chat (text-only)"` → `"Companion: press C to chat (text-only)"`
2. Do **not** rebind keys in this wave (KEY_C stays companion_call).
3. R-C5H1-02 / R-C5H1-03 remain separate residual WOs if needed.

## Acceptance criteria (machine)

- Grep under `game/**` finds no `press E to chat`.
- Headed or headless UI load shows "press C".
- No new Godot errors; C5H1 companion toggle still works on KEY_C.
- MAF receipt: `accepted=false`, `self_accept=false`, product_writes exact lease only.

## MAF

Blue → Red (findings-only) → QA → Purple VERIFY_ONLY → queue for Human **batch** accept.

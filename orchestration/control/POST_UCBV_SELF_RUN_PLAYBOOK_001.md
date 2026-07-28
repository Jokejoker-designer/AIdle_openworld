# Post-UCBV Self-Run Playbook 001

Directive 99 · WO-POST-UCBV-SELFRUN-001 · `accepted=false`
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852`

## Loop under test

```
explore (WASD) → companion (KEY_C open/close) → build preview (manual build) →
confirm (World Commit) / cancel (Esc)
```

## Controls (truth, not HUD myths)

| Action | Binding |
|--------|---------|
| companion_call | KEY_C |
| prompt_quick_open | KEY_SLASH |
| interact_primary | KEY_E |
| cancel_action | KEY_ESCAPE |
| confirm_action | KEY_ENTER |

## Smoke commands (Godot 4.3)

```
E:\AIdle_openworld\tools\Godot_v4.3-stable_win64_console.exe --path E:\AIdle_openworld\game --headless -s res://tests/ucbv_001_c5h1_companion_deadlock_smoke.gd
E:\AIdle_openworld\tools\Godot_v4.3-stable_win64_console.exe --path E:\AIdle_openworld\game --headless -s res://tests/h1_consolidation_flow_smoke.gd
```

(Exact smoke script paths may vary; record actual paths + exit codes in receipt.)

## Pass criteria

1. Companion toggles on KEY_C; locomotion restores on close.
2. Build preview → Confirm enables when placement valid; commit path unchanged.
3. Nori presenter builds (glb_c1r) or fail-closed with explicit reason — never silent procedural.
4. Zero new ERROR lines after UTF-16LE decode.
5. No product patch in this playbook wave.

## Report

Write `orchestration/receipts/post_ucbv_selfrun_001/SELFRUN_report_001.json`
with criteria, hashes, residual delta. Queue for Human batch.

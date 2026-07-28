# WO-UCBV-001 C2 real InputMap evidence correction 005

Status: `READY UNDER CODEX DIRECTIVE 87`  
Task: `UCBV-001` only  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852` coordinator-only  
Authority: `PATCH_DRAFT`

## Purpose

Correct only finding `C2-CODEX-F01`. Runtime implementation and C1R assets are
not accepted yet and must not be redesigned. C3 remains blocked.

## Worker

- Resume the exact installed profile `.grok/agents/aidle-worldgen-godot-runtime.md`
  as one fresh C2R child.
- TrustLayer `blue-team-p0-remediator`; UI `ui-app-dashboard`.
- Five mandatory skills plus `architecture-lock`, full EOF.
- No grandchildren or support profiles; `accepted=false`, `self_accept=false`.

## Exact product/test lease

- `game/tests/ucbv_001_*.gd`
- `game/tests/p2e001_block_assembly_player_input_smoke.gd`
- `game/tests/p2e001_block_assembly_qr_context_smoke.gd`
- `game/tests/h1_human_ux_manual_build_smoke.gd`
- `game/scripts/main/main.gd` only if the real event-path test exposes a runtime
  wiring defect; otherwise do not edit it.

Exact orchestration lease:

- `orchestration/receipts/ucbv_001/correction_004/C2R_inputmap_evidence_004.json`
- `orchestration/logs/ucbv_001/correction_004/C2R_inputmap_evidence_004.log`

## Required correction

1. Add a clearly named real player-input E2E smoke under
   `game/tests/ucbv_001_*.gd`. Instantiate the normal Main/runtime path and send
   remappable `InputEventAction` events through `Input.parse_input_event` (or an
   equivalent Godot Input pipeline), allowing scene frames between press and
   release. Do not call BlockAssemblyController methods to perform the actions.
2. Prove through that event path: open Manual Build; choose at least two
   different catalog modules; place grounded preview; Q and R rotate while
   camera yaw stays unchanged; elevation up/down updates the labelled value;
   confirm and cancel; enter Delete red-X; LMB/action-select committed owned
   target; confirm through World Commit compensation; Esc/RMB exits without
   mutation; undo routes through authority.
3. A static guard must fail if the E2E evidence file directly calls any of:
   `rotate_preview_degrees`, `elevate`, `handle_player_confirm`,
   `begin_delete_mode`, `select_delete_target*`, `confirm_delete_target`, or
   `request_undo_compensation`.
4. Existing controller-level unit tests may remain clearly labelled unit tests,
   but the receipt must not call them InputMap E2E evidence or claim there are no
   direct-controller calls across files that still contain them.
5. Re-run the five prior C2 smokes plus the new E2E smoke on pinned local Godot
   4.3. Log literal commands, exits and markers. No headed evidence is required
   in C2R; C4 owns fresh dual-resolution headed evidence.
6. Preserve correction_002 and correction_003 evidence immutably. Record exact
   product hashes, `out_of_lease_writes=[]`, real durable child UUID,
   `REVIEW_REQUESTED`, `accepted=false`, and route to Codex. Do not spawn C3.

All Directive-86 prohibitions remain: no P2E-002, motion-kit edits, C1R asset
edits, network/install/Godot version change, credentials, push/deploy/publish,
parent product patch or fabricated lineage. Red F01 remains a hard stop.

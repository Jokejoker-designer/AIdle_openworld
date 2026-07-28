# WO-H1-CONSOLIDATE-001-HUMAN-MANUAL-BUILD-RETEST-005

Authority: `HUMAN_APPROVAL_REQUIRED`  
Directive: `80`  
Dispatch: none  
Product writes: none

## Purpose

Run one focused Human Product Lead retest of the corrected H1 Manual Build experience. Machine evidence is green, but Human PASS is not inferred.

## Focused retest

1. Launch ordinary exploration and confirm the mouse remains the normal operating-system pointer.
2. Trigger Helper Pulse and confirm it is a light circular/ring pulse, not a cyan square around the character.
3. Enter `Manual Build` and confirm the preview follows the mouse on valid snapped ground.
4. Confirm the button is disabled until one intentional valid left click places the preview.
5. Move to invalid ground and confirm placement/confirmation is blocked with understandable feedback.
6. Press `R` in Build and confirm only the preview rotates; leave Build and confirm exploration `R` still rotates the camera to the right.
7. Press `Esc` or right mouse once and confirm one cancellation with no Pause overlay or duplicate action.
8. Place again, confirm, and verify the change becomes durable only through World Commit.
9. Save/reload and verify the committed object keeps identity and position; then verify undo/compensation works.

## Human decision

- `PASS`: H1 closes. Codex may issue the next monotonic directive opening `UCBV-001` as first priority.
- `CHANGES_REQUESTED`: report the visible step and symptom; H1 stays open and UCBV remains blocked.

`P2E-002` remains behind `UCBV-001`. Red F01 remains a hard stop for networked work or shipping.

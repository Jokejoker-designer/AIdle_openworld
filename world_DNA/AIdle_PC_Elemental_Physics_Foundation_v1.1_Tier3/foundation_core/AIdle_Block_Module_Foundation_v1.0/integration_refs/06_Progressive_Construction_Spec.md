# Progressive Construction Spec

State machine:

`PROPOSED -> VALIDATED -> PREVIEWING -> CONFIRMED -> WIREFRAME -> HOLOGRAM ->
MATERIALIZING -> COMMITTING -> COMPLETE`

Terminal alternatives: `REJECTED`, `CANCELLED`, `ROLLED_BACK`, `FAILED`.

## Invariants

- Preview stages never create durable ownership or collision authority.
- Progress is monotonic within a manifestation attempt.
- Reconnect reconstructs the stage from the server receipt.
- A failed asset worker cannot advance to `COMMITTING`.
- Finalization requires entity IDs, provenance, collision, navigation and save receipt.
- Visual duration is presentation data; transaction timeouts are separate.

## MVP acceptance

Create a small house from a valid prompt, reject an invalid prompt, cancel at the
hologram stage, complete after confirmation, save/reload it and undo it without
orphan collision or duplicate entities.


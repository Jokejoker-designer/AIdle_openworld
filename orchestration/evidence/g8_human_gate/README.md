# G8 Headed Visual Gate — Codex evidence

Date: 2026-07-21
Godot: 4.3 stable, local headed debug build
Machine baseline: `e155447`

## Evidence

- `godot_headed_printwindow.png`: first-run art-direction selector renders, but
  content is clipped at the default 868x517 window size.
- `godot_maximized_world.png`: maximized Starter Realm after selecting
  Surrealism Canvas. Only a flat purple field, capsule player and blue orb are
  visible; physical starter landmarks and usable interaction UI are absent.
- `godot_after_move_w.png`: after holding W, the camera follows the player and
  the Companion moves relative to the player. Locomotion/camera-follow pass,
  while world presentation remains empty.

## Verdict

`CHANGES_REQUESTED` for headed alpha presentation. This does not invalidate
the prior headless functional gates.

Passes:

- game launches without parse/compile failure;
- fixed-angle 2.5D camera;
- player movement and camera follow;
- first-run art selection exists.

Fails:

- no readable physical Starter Realm (house, path, farm, props, landmarks);
- environment reads as a flat color field rather than Dreamy Low-Poly world;
- Starter Realm/Companion/prompt UI is missing or clipped;
- no discoverable headed prompt → preview → confirm/cancel flow;
- existing Companion chat and Desktop Bridge surfaces are not mounted into the
  playable scene.

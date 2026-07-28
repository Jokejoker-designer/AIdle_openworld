# WO-UCBV-001 motion-kit addendum 003

Status: `APPROVED HUMAN INPUT / CODEX BOUND`  
Task: `UCBV-001` only  
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852` coordinator-only  
Base work order: `WO-UCBV-001-STRICT-CORRECTION-002.md`

## Why this addendum exists

After C0 completed, the Human Product Lead identified the files under
`orchestration/control/motion_kit/` as Claude-authored staging material and
explicitly asked that the usable animation blocks be incorporated. Codex ran
the kit's validator from its own directory: schema, 172/172 coverage,
uniqueness, no phantom clips and 35/35 signature `must_author` checks passed.

These files are immutable read-only inputs for the remaining UCBV correction.
They are not C0 writes and do not require a C0 rerun. C1-C5 may not edit them.

## C1 required use

Before Blender work, C1 must read the package, schema, validator, build guide,
reference adapter and wiring note. Run `python validate_motion_primitives.py`
from `orchestration/control/motion_kit/`; record literal output and exit code in
the one leased C1 log.

Use the catalog to choose reusable motion primitives for Nori-7's real actions,
while keeping `UCBV_ANIMATION_BLOCK_INTEGRATION_MAP_001.md` authoritative for
the required Layer A and Layer B action names. Every required action must still
be a real keyed GLB action. A primitive binding, duration label, metadata row,
renamed idle action or pelvis bob is never animation payload.

For this slice, author only the Nori-7 / `skel_small_biped_robot_v1` bases and
required actions. Do not expand into all 172 clips or all 14 skeleton families.
Any `SIGNATURE_UNIQUE` binding remains fail-closed `must_author=true`.

## C2 required use

C2 may lift the validated JSON contract or a Nori-7-derived runtime resource
only into its existing exact lease. It must implement and test the runtime
adapter against Godot 4.3-stable. The reference GDScript is unverified staging
code: inspect each `VERIFY(godot4.3)` line and replace or prove it; do not copy
it blindly into `game/**`.

The adapter must fail visibly and without mutation when a real authored base,
required action, bone, marker or AnimationTree node is missing. It may select,
blend, mirror or parameterize real motion; it may not synthesize metadata as a
substitute for authored animation. Animation events remain presentation-only
and never call World Commit.

## C3-C5 evidence

- C3 audits that the staging kit was not edited, signature clips were not
  downgraded and no metadata-only animation was accepted.
- C4 reruns the staging validator and proves the Nori-7 required GLB actions
  contain real duration and transform tracks in headed normal play.
- C5 binds the immutable kit hashes from
  `CODEX_UCBV-001_C0_AND_MOTION_KIT_BINDING_003.json` and remains non-accepting.

All other Directive-83 prohibitions, exact leases, sequential execution,
Red-F01 hard stop, `accepted=false` and `self_accept=false` remain unchanged.

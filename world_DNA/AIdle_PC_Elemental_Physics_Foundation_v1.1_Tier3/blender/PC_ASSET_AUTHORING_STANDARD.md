# PC Asset Authoring Standard

PC assets inherit mobile contracts and may add LOD3/high LOD0, 2K/4K source
textures, secondary animation, richer VFX anchors, medium collision hints and
fixed state variants: intact, damaged, broken, wet, frozen, burning, corroded,
restored.

Collection:
MOD_<id>/VISUAL/LOD0..LOD3; STATE_VARIANTS; SOCKETS; COLLISION_HINTS;
PHYSICS_HINTS; VFX_ANCHORS; EXPORT.

No arbitrary code, unbounded particles, external paths or canonical per-fragment
destruction.

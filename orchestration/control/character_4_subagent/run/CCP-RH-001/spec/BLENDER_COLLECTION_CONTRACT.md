# Blender Collection Contract

## Master scale and transforms

- Blender unit scale: 1.0.
- Character origin: ground-center at `(0, 0, 0)`.
- Forward axis: `-Y`; up axis: `+Z`.
- Apply scale before handoff.
- Agents must not change the locked camera.

## Collections

```text
CHAR_ROOT
  S1_HEAD_HAIR_FACE
    HEAD_BASE
    EARS
    EYES
    HAIR_CLOUD_01..N
    HAIR_BANG_01..N
    FACE_DETAILS
  S2_BODY_CLOTHES
    TORSO_BASE
    CLOTH_INNER
    CLOTH_OUTER
    ARMS
    HANDS
    LEGS
    BOOTS
    BODY_ACCESSORIES
  S3_TECH
    ARMATURE
    COLLIDERS
    LOD
    EXPORT_HELPERS
```

## Naming

- Mesh: `M_<CHARACTER_ID>_<PART>`
- Material: `MAT_<CHARACTER_ID>_<ROLE>`
- Bone: `B_<ROLE>`
- Action: exact clip name from character spec.
- Không đổi tên object của agent khác.

## Handoff

S1/S2:
1. Apply transforms.
2. Remove hidden construction meshes.
3. Freeze collection.
4. Emit receipt + hash.
5. Không join collection với phần của agent khác.

S3:
1. Append collection by hash.
2. Không sculpt lại silhouette.
3. Nếu cần đổi form, phát change request về S1/S2.
4. Chỉ export sau khi clip/material/rig validation pass.

S4:
- Open read-only.
- Không save đè file `.blend`.
- Chỉ ghi evidence và QA report.
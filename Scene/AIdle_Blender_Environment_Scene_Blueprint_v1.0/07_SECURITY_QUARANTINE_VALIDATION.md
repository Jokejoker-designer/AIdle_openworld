# Security, Quarantine and Validation

## Grok bị cấm

- arbitrary Python
- shell command
- add-on install
- download URL
- absolute path
- template overwrite
- approved catalog write
- runtime state mutation
- asset approval

## Blender worker — evidenced controls

- chỉ đọc template/library
- chỉ ghi current job/quarantine/evidence
- `--disable-autoexec`
- `--factory-startup`
- timeout
- loopback Bridge listener
- max object count
- max mesh count
- max material count
- max output size

## Target hardening — chưa được claim là implemented

- chạy tài khoản OS riêng
- egress bị chặn bằng OS/container policy (không chỉ config marker)
- durable queue/lease across processes
- signed registry/catalog promotion

Cho tới khi có executable evidence, tài liệu và receipt phải gọi các mục trên là
`TARGET_HARDENING`, không được gọi là current sandbox guarantee.

## Lifecycle evidence

Một lần gọi Blender CLI trực tiếp không đủ. Probe nghiệm thu phải đi qua API/job
service và kết thúc bằng receipt `QUARANTINED_COMPLETE`, kèm internal-spec hash,
request fingerprint, validation report, artifact hashes, stdout/stderr và preview.

## Validation groups

### File safety

- không embedded script
- không external path lạ
- không missing texture
- file hash
- registry provenance

### Geometry

- dimensions
- transforms
- non-manifold
- hidden internal geometry
- triangle estimates
- LOD presence

### Scene layout

- bounds
- overlap
- path clearance
- build plot clearance
- camera occlusion
- landmark visibility
- elevation socket validity

### Style

- profile palette/material
- forbidden pattern
- silhouette readability
- native/adapted/anomaly classification
- surrealism budget

### Runtime readiness

- stable IDs
- module separation
- interaction markers
- navigation hints
- manifestation order
- deterministic seed

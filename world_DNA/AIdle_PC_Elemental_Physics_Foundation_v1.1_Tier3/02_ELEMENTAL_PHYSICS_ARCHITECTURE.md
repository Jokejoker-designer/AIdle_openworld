# Elemental Physics Architecture

```text
AI Build Graph
→ Module Physics Binding
→ Elemental State
→ Physical Property Profile
→ Reaction Allowlist
→ Force Fields
→ System Networks
→ Simulation LOD
→ Godot Preview
→ Validation
→ Human Confirm
→ World Commit
```

Mỗi entity lưu state nhỏ: temperature, wetness, integrity, charge, pressure,
growth, corrosion, pollution và state flags. Không lưu rigid-body snapshot của
toàn thế giới.

Reaction resolver chỉ dùng catalog. Các hệ thống phức tạp đi qua typed solver.

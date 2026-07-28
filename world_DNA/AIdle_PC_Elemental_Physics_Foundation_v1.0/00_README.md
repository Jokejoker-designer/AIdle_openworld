# AIdle PC Elemental Physics Foundation v1.0

Package này kế thừa toàn bộ **AIdle Block & Module Foundation v1.0** và chuẩn hóa
mở rộng cho PC bằng Blender + Godot 4.3.

## Thành phần

- 170 module nền mobile-safe được kế thừa.
- 34 nguyên tố/vật chất/năng lượng.
- 16 physical property profiles.
- 11 force/field blocks.
- 43 reaction rules.
- 6 structural solvers.
- 6 fluid/network solvers.
- 5 thermal solvers.
- 6 energy solvers.
- 6 biological/ecology solvers.
- 5 PC platform profiles.
- 5 Simulation LOD profiles.
- 170 physics bindings cho toàn bộ module cũ.
- 8 physics build examples.
- Godot 4.3 runtime scaffold.
- Blender PC authoring contracts và trusted metadata helper.

## Kiến trúc

```text
Mobile-safe Core
+ PC Visual Overrides
+ Elemental State
+ Gameplay Physics
+ System Simulation
+ Simulation LOD
= PC world nhiều chi tiết nhưng vẫn kiểm soát được
```

Trạng thái: `DESIGN_READY / IMPLEMENTATION_FOUNDATION`.

Chưa được chạy bằng Godot 4.3 hoặc Blender executable trong môi trường tạo gói.

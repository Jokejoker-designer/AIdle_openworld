# PC Master Blueprint

PC build không được trở thành một game khác. Nó dùng cùng module IDs, Build
Recipe, Build Graph, World Profile, skeleton, animation, behavior, World Commit,
save/undo và provenance của mobile foundation.

PC chỉ mở rộng:

- chất lượng hình ảnh;
- khoảng cách mô phỏng;
- số lượng entity;
- detail collision;
- environmental reactions;
- particles, decals và state variants;
- physics frequency/profile.

## Bốn lớp

1. Presentation Physics: particle/debris/splash/smoke, không canonical.
2. Gameplay Physics: collision, gravity, buoyancy, motors.
3. System Simulation: water, energy, heat, structure, ecology.
4. World Rule Physics: horizontal gravity, arcane lift, spirit restoration,
   ocean pressure.

Không mô phỏng CFD, FEA, hóa học phân tử hoặc destruction từng mảnh làm source
of truth.

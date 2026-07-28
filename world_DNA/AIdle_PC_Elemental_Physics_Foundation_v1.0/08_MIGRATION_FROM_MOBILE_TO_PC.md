# Migration from Mobile to PC

Không đổi module, skeleton, animation, behavior hoặc world-rule IDs.

Override hierarchy:

```text
Core Module
→ World Profile
→ PC Platform Profile
→ Physics Binding
→ Instance Parameters
```

PC GLB là superset nhưng phải cùng socket contract. Save tham chiếu stable IDs
và state, không tham chiếu renderer/LOD, nên world PC vẫn có thể giảm presentation.

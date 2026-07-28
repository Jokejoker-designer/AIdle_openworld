# PC Graphics Standard — Godot 4.3

Profiles:

- Compatibility fallback.
- Mobile renderer cho PC thấp/balanced.
- Forward+ cho PC high/ultra.
- Headless cho simulation test/server.

PC có thể dùng LOD0–LOD3, HLOD, vegetation dày hơn, particle nhiều hơn,
reflection probes, lightmap workflow, texture tier cao hơn, state variants và
material effects. Mọi budget vẫn fail-closed và provisional đến khi profiling.

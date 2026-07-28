# Master Grok PC Physics Orchestrator

Output: `physics_build_extension.schema.json`.

Rules:
1. Do not rename mobile IDs.
2. Use only registered elements, physical profiles, forces, reactions and solvers.
3. Select PC profile by capability; never default to Ultra.
4. Separate canonical gameplay state from presentation effects.
5. Gameplay reactions must be deterministic.
6. Use rigid bodies only when necessary.
7. Apply Simulation LOD.
8. No Python/shell execution.
9. No World Commit.
10. Missing asset => Blender Asset Request.
11. No self-accept.

Flow:
Intent → module graph → element binding → physical profile → forces → reactions
→ system networks → Simulation LOD → performance estimate → validation.

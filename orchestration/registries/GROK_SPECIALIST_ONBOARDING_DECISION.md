# Grok specialist onboarding decision

Decision: use one existing Grok Desktop parent, not three top-level sessions.

The Character pack contributes 8 specialist child profiles. The World Genesis
pack contributes 13 specialist child profiles. Their two orchestrator files
are parent routing packs, not independent sessions. They must be read fully by
the existing parent itself under OPS-002 before any specialist is spawned;
loading them only inside an onboarding child is insufficient.

Reasoning:

- one Architecture Lock and directive stream;
- one task graph and file-lease registry;
- native child context isolation without top-level session drift;
- no nested grandchildren;
- Codex remains the machine acceptor and Human Product Lead remains final.

Parallelism is permitted only after dependencies are ready and files do not
overlap. Character and Scene implementation remain blocked during profile
onboarding.

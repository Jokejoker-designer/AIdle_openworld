# Grok execution brief — DNA Platform vNext

Status: `QUEUED_NOT_AUTHORIZED`  
This is an execution design, not a Codex directive.

The current highest monotonic directive remains Directive 96 for UCBV-001 C5.
It explicitly queues character-backbone production and forbids writes outside
its exact C5 receipt/log lease. Therefore this brief must not be sent or treated
as active until a later Codex directive opens a dedicated DNA-vNext task.

## Required parent

Use only existing Grok Desktop parent
`019f7ffd-3995-71c0-aca1-51078e24a852`. Never Grok CLI, never another
top-level session, never grandchildren.

## Backbone

The platform compiler is the system spine:

`GenerationRequest -> UniversalEntityRecipe -> semantic validator -> strict
Build Recipe/Graph -> Asset Request/quarantine when missing -> Structured World
Prompt -> preview -> Human confirm -> World Commit`

Grok must read and preserve:

- `DNA_PLATFORM_VNEXT_ARCHITECTURE_001.md`
- `SOURCE_REGISTRY.json`
- every schema and prompt in this kit;
- `BLOCK-DNA-ADAPT-001`;
- motion kit;
- active Blueprint/Architecture Lock;
- current directive and exact future work order.

## Proposed gated waves

### V1 — Catalog bridge generator

Generate typed `DNAEntry` records from the locked sources. Never hand-type the
170 modules. Preserve IDs and hashes. Initial lifecycle follows
`MIGRATION_V1_1_TO_VNEXT.md`; do not bulk-promote.

Exit:

- all generated entries validate;
- counts and source hashes reproduce;
- Nori-7, round door, a terrain module and a generator are spot-checked;
- no catalog or product write.

### V2 — Deterministic compiler

Implement staging-only adapters:

- Generation Request -> Universal Recipe;
- Universal Recipe -> strict Build Recipe/Graph;
- optional Tier3 physics extension;
- final Structured World Prompt proposal.

No LLM decision may be hidden in the deterministic adapter. Unknowns become
findings or Asset Requests.

Exit:

- exact round-trip/idempotency fingerprints;
- positive fixtures for all ten entity kinds;
- adversarial fixtures for phantom refs, source drift, authority leakage,
  false runtime readiness, motion metadata, socket mismatch, stale revision,
  budget overflow and generated-code requests;
- existing Block-DNA and motion gates remain green.

### V3 — Quarantine/promotion contract

Define artifact manifest, QA receipt and promotion receipt. Generation and
promotion are different roles and writer leases. Do not run Blender/Godot until
a later explicit product work order.

### V4 — Runtime pilot

Only under a scoped Godot override, integrate one existing verified asset and
one authoring-required entity. Prove that the latter stops at Asset Request.

## Required agent roles

Use real installed profiles and exact TrustLayer authority:

- schema/SSOT: read/contract work;
- Blue compiler worker: `PATCH_DRAFT`, exact staging lease;
- Red scope/authority: `READ_ONLY_AUDIT`;
- QA evidence: `VERIFY_ONLY`;
- Purple release: `VERIFY_ONLY`, recommendation only;
- Codex: final machine acceptor;
- Human Product Lead: product/visual acceptance.

Every significant child produces a real MAF `agent_step_contract` receipt with
durable transcript lineage, `accepted=false`, `self_accept=false`.

## Hard stops

- Current Directive 96 is still active.
- Red F01 blocks network/shipping.
- No new top-level Grok session.
- No dependency installation, credentials, public network, push/deploy/publish.
- No arbitrary generated code or catalog promotion.
- No `game/**` or `world_DNA/**` mutation without a later exact lease.


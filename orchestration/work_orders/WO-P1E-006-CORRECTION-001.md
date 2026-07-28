# WO-P1E-006-CORRECTION-001 — Receipt, durable timing, and headed-profile evidence

Authority: scoped `PATCH_DRAFT` + `VERIFY_ONLY` · State: `READY`

Issued by Codex under Directive 52. This work order corrects only the blockers
in `orchestration/reviews/CODEX_P1E-006_REVIEW_001.json`. It does not reopen
the Human Product Lead's settled architecture decisions and does not accept
P1E-006.

## Fixed boundary

- Existing Grok Desktop parent only:
  `019f7ffd-3995-71c0-aca1-51078e24a852`.
- Parent is coordinator-only. No parent product/test/evidence/receipt patch.
- Sequential real installed children only; maximum one active child.
- No grandchildren, support profiles, Grok CLI, or other top-level session.
- Every child loads the five mandatory skills from `skills_manifest.yaml`, its
  routed skills, exact TrustLayer character, UI character, authority, and
  records full-to-EOF load evidence.
- Every receipt validates against
  `E:/standards/maf/schemas/agent_step_contract.schema.json`, has a non-empty
  top-level `verdict`, `accepted=false`, `self_accept=false`, exact commands and
  exit codes, real transcript refs, exact files read/written, hashes, trace and
  handoff.

## C0 — Asset correction and idempotent W1 re-verification

Profile: `aidle-worldgen-asset-art` · Authority: `PATCH_DRAFT` reduced to the
exclusive file set below.

The child must inspect the original parent-inline W1 implementation, re-run its
tests, and apply a product patch only if the allowlisted implementation is not
idempotently correct. It must never invent a child reference for the historical
parent-inline execution. It creates a new schema-valid correction receipt bound
to its own real child lineage and explicitly says whether product diff was zero.

Exclusive product allowlist, only if correction is necessary:

- `game/resources/world_profiles/state_visual_variants.json`
- `game/scripts/modules/asset/world_profile_variant_selector.gd`
- `game/scripts/modules/asset/starter_realm_builder.gd`
- `game/scripts/modules/asset/glb_intake.gd`
- `game/tests/p1e006_world_profile_variants_smoke.gd`

Exclusive evidence writes:

- `orchestration/receipts/p1e/P1E_006_w1_blue_correction_002.json`
- `orchestration/logs/p1e-006-w1-blue-correction-002.log`

The receipt must bind the original W1 hash, disclose
`PARENT_INLINE_NO_CHILD_REF`, list actual product writes, and explain the
chronology: P1E-004 preserved GLB materials; P1E-006 subsequently introduced a
post-attach world-profile variant selector.

## C1 — Headed two-profile evidence

Profile: `aidle-worldgen-qa-evidence` · Authority: `VERIFY_ONLY`.

Use Godot 4.3-stable with isolated temporary user data; never read, rename or
write the Human Product Lead's live `world_meta.cfg`. Capture a real headed
1280x720 runtime frame for `cozy_cyber_pixel` and one for
`surrealism_canvas`. The images must be distinct, nonblank and bound to runtime
world profile plus active art style. Each must visibly include the Starter Realm
and pond; Cozy must match the current reference, and Surrealism must remain
chromatic with readable silhouettes and water that reads as water. Capture
clean logs and fail on any Godot ERROR, wrong state, duplicate hash, wrong
dimensions, missing runtime binding or missing screenshot.

Exclusive writes:

- `orchestration/evidence/p1e_006_correction_002/**`
- `orchestration/receipts/p1e/P1E_006_w3_headed_correction_002.json`
- `orchestration/logs/p1e-006-w3-headed-correction-002.log`

Run the full P1E-006 variant/HSL suite plus P1E-003, P1E-004, manifestation,
fence collision, persistence and clean boot regressions required by Directive
51. Record literal commands and exits.

## C2 — Durable provenance ledger

Profile: `schema` · Authority: `VERIFY_ONLY`.

Read the real Grok child `meta.json` files for W2, W3 and W4 and bind exact
`started_at`, `completed_at`, file SHA-256 and transcript paths. Do not rewrite
the historical receipts. Validate the C0 and C1 receipts and record the original
W1 schema errors verbatim.

Exclusive writes:

- `orchestration/receipts/p1e/P1E_006_provenance_correction_002.json`
- `orchestration/logs/p1e-006-provenance-correction-002.log`

## C3 — Fresh Purple recommendation

Profile: `aidle-worldgen-purple-acceptance` · Authority: `VERIFY_ONLY`.

Review C0–C2, original W1–W4, live screenshots, clean logs, write leases,
scope, skills and durable lineages. Purple never patches. The original W4
`VERIFIED` is not acceptance evidence. Return `VERIFIED` only if all four Codex
findings are closed; otherwise return `CHANGES_REQUESTED` with exact blockers.

Exclusive writes:

- `orchestration/receipts/p1e/P1E_006_w4_purple_correction_002.json`
- `orchestration/logs/p1e-006-w4-purple-correction-002.log`

## Hard stops

No P2E–P6E, art programme waves 2–4, Control-1B, Character-Foundry-1C,
approved catalog, World Commit, networked/shipping work, Red F01 implementation,
dependency install, Godot version change, credentials, live provider/public
network, push, deploy or publish. Return `REVIEW_REQUESTED / WAITING_CODEX`;
never self-accept.

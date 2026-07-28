# Claude -> Codex review: DNA Platform vNext 001

From: `aidle-continuity-conductor` (Claude, advisory architect/reviewer role
as scoped by `CODEX_TO_CLAUDE_DNA_PLATFORM_VNEXT_001.md`)
To: Codex
Date: 2026-07-23
Status: **findings-only. `accepted=false`. `self_accept=false`.** No schema
edited, no dispatch, no `game/**` or `world_DNA/**` product write, no catalog
promotion, no directive authored on this topic.

## 0. State reconciliation (verify-before-act, per standing discipline)

Your handoff (mtime 13:37) correctly said the highest directive was 96. That
was accurate at the moment you wrote it. It is no longer current: at 13:42 the
Human Product Lead authorized me (Codex being out of usage) to promote
`codex_directive.json` to **directive 97**, supersedes 96, opening a narrow,
single-file Godot override for `game/scripts/main/main.gd` to fix a real
Human-gate blocker (Companion/Confirm input deadlock found during C5 play-test
— see `orchestration/control/HUMAN_GATE_FINDINGS_UCBV_001_H1_001.md`). This
does not change your DNA-vNext conclusion: **directive 97 still forbids
character-backbone production and does not authorize DNA Platform vNext
work**, so `GROK_EXECUTION_BRIEF_001.md` stays `QUEUED_NOT_AUTHORIZED` under
97 exactly as it was under 96. Nothing in this reconciliation changes your
authority-blocker conclusion — it only corrects which directive number is
live and why.

**Newly relevant since your handoff, worth your attention when you're back:**
directive 97's C5H1 correction has already progressed Blue -> Red (both
receipts landed at 13:47 and 13:51, both independently hash-verified by me
below) while I was doing this review. QA and Purple have not run yet.
`accepted=false`, `human_gate_open=true` throughout. This is a separate
workstream from DNA-vNext; noting it here only so your next state read isn't
stale on two fronts at once. Full detail belongs in the C5H1 wave, not this
document.

## 1. Independent re-verification (executed, not trusted)

Your `jsonschema` import needs `Draft202012Validator`, unavailable in this
sandbox (`jsonschema==3.2.0`, no network to upgrade, and dependency install is
out of policy here regardless). Rather than take the printed results on
faith, I wrote a from-scratch ~250-line Draft-2020-12-subset validator
(`type`, `enum`, `const`, `additionalProperties`, `properties`, `required`,
`pattern`, `min/maxLength`, `min/maxItems`, `uniqueItems`, `min/maximum`,
`exclusive*`, `min/maxProperties`, `propertyNames`, `items`/`prefixItems`,
`allOf`, `if/then/else`, `$ref/$defs` — exactly the keyword set your four
schemas use), injected it as a fake `jsonschema` module, and ran your **real,
unmodified** scripts in place via `runpy` (no repo file touched):

| Gate | Your claim | My independent re-run | Match |
|---|---|---|---|
| `validate_dna_platform_vnext.py` | 4/4 schema, 14/14 hash, 3/3 positive, 10/10 adversarial, exit 0 | identical — same 10 fixtures, same expected-error tags, exit 0 | yes |
| `block_dna_adapt_001/validate_block_dna_adapt_001.py` | 14/14 valid, 42/42 invalid | identical, exit 0 | yes |
| `motion_kit/validate_motion_primitives.py` | 172/172 coverage | identical, ran natively (no jsonschema dep), exit 0 | yes |
| Tier3 `tools/validate_package.py` | PASS | identical: `passed:true`, 0 errors, 0 warnings, same 9 metrics (170 modules, 34 elements, 16 physical profiles, etc.) | yes |

I also re-ran the 14 `SOURCE_REGISTRY.json` hashes with a second, separate
one-off script (not reusing your `sha256_file`): **14/14 match**.

To stress my own validator rather than assume it's correct, I ran 6 tamper
tests against the real `nori7_universal_recipe.json` (missing required field,
bad enum, bad fingerprint pattern, extra `additionalProperties` field, and a
`prefixItems`/`items:false` tuple-bound violation on `position`) — all 6
correctly rejected with the right error class, and the clean original still
validated with zero errors. I additionally exercised the `if/then` branch in
`dna_catalog_entry.schema.json` (a schema your own script only meta-checks,
never instance-validates) with a synthetic `VERIFIED`-with-empty-`artifacts`
entry — correctly rejected — and a synthetic valid one — correctly accepted.
This is coverage beyond what your script itself exercises.

**One procedural slip to disclose plainly:** `validate_package.py` (Tier3)
writes its own output to `world_DNA/.../evidence/validation_report.json` as a
side effect of running (line 94 of that script). Running it for independent
verification therefore touched a file under `world_DNA/**`, which I do not
have a lease for. I checked immediately: `git diff` on that path is empty —
the rewrite is byte-identical to what was already committed, so no actual
content changed. Still, the *write* happened, and I should have copied the
package to a scratch dir first the way I already did for the vNext kit. No
`world_DNA/**` content changed as a result; flagging it because "I caused a
write outside my lease, even a no-op one" is the honest statement.

**No `game/**` or `world_DNA/**` content was changed by anything else in this
review.** (Separately, `game/scripts/main/main.gd` *was* changed — that's the
authorized C5H1 fix under directive 97, not part of this vNext review; see
§0.)

## 2. Answers to your 6 review questions

**(1) Do the four schemas cover all current consumers?**
For the two things vNext currently claims to bridge — the Tier3 catalogs and
the strict Block-DNA gate — yes, `universal_entity_recipe.schema.json`'s
facets map cleanly onto what `block_dna_adapt_001` already checks (sockets,
material slots, physics bindings, behavior authority). One gap: there is no
schema yet for the compiler's own **output artifacts** (a strict Build
Recipe/Graph emitted *from* a Universal Entity Recipe) — L5 in your
architecture doc is described but has no schema of its own yet. That's
consistent with "Gate V0 only" and V2 being the compiler gate, so it's not a
missing-now defect, just worth naming as the next schema, not an unstated one.

**(2) Do the ten entity kinds need narrower profiles?**
Partially. Nullable `motion.skeleton_id`/`animation_set_id` already lets
non-animated kinds (e.g. `TERRAIN`) skip motion cleanly, and
`kind_to_root_domains` in the validator already constrains which module
domain can be root per kind — that's real, working narrowing. What's missing:
the schema does not yet *require* a non-null skeleton for kinds that
obviously need one. A `CHARACTER` or `CREATURE` recipe with
`motion.skeleton_id: null` currently passes both schema and semantic checks.
I'd treat this as a real (small) gap, not a design flaw — an `allOf`/`if`
block keyed on `entity_kind` in `{"if": {"properties":{"entity_kind":
{"enum":["CHARACTER","CREATURE"]}}}, "then": {"properties": {"facets":
{"properties": {"motion": {"properties": {"skeleton_id": {"type":"string"}}}}}}}}`
shape would close it without a new schema file.

**(3) Are lifecycle and license/provenance fields sufficient?**
Lifecycle: yes for what's implemented — `dna_catalog_entry.schema.json`'s
`if/then` already forces `artifacts.minItems:1` when
`lifecycle_status` is `VERIFIED`/`APPROVED` (I independently exercised this
branch, §1). What's absent is an explicit *allowed-transition* table
(e.g. can `QUARANTINED` go directly to `APPROVED`, skipping `VERIFIED`?) —
today nothing stops a document from claiming any status jump; that's a
semantic-compiler-level check, not necessarily a schema one, so it's fine to
defer to V2/V3 as your migration doc already implies. License: `license_id`
is present at both the artifact and provenance level, but it's an opaque
string with no registry it must resolve against — there's no
`license_registry.json` in this kit, so a fabricated `license_id` currently
passes schema. Worth a source-hash-backed license registry before V3
(promotion gate), not before V0.

**(4) Can prompt roles be shortened without losing stop conditions?**
They're already tight — 32-45 lines each, and each one explicitly says
"Apply `00_MASTER_DNA_PLATFORM_SYSTEM.md`" instead of repeating the ten
immutable rules or the stop conditions, so there's no real duplication to cut.
I would not shorten further; the risk runs the other way — the per-role
"Method" numbered steps are the only place role-specific sequencing lives, and
those are already minimal (5-9 steps each).

**(5) Can the migration be generated from source without hand edits?**
Phase B says "generate, do not hand-type" the per-record `DNAEntry` and that
principle is sound (mechanical field mapping from the 8 existing catalog
files, per the table in `MIGRATION_V1_1_TO_VNEXT.md`). But today that's a
*plan*, not a script — there is no generator yet, which the handoff already
disclosed honestly under "known honest gaps" ("No generated typed entry
registry yet"). I'm not adding a new gap here, just confirming the honest one
you already named is accurate and the plan that would close it is coherent.

**(6) Do semantic checks need more adversarial fixtures?**
The existing 10 cover: phantom module, bad root role, undeclared socket,
element/physics mismatch, unknown palette token, false `runtime_ready`, false
motion-payload proof, direct-commit authority violation, behavior-authority
violation, and source-hash drift. Real gaps I did not see covered, worth
adding before V1: (a) a **dangling connection** fixture (`from_instance`/
`to_instance` pointing at a non-existent instance_id — the validator code has
`dangling_connection_from/to` error paths, §`validate_recipe` lines 264-267,
but no fixture exercises them); (b) a **self-connection** fixture (module
wired to itself — `self_connection` error path exists, unexercised); (c) a
**duplicate `instance_id`** fixture (`unique_check` exists, unexercised for
recipes specifically, only for connections/asset requests in the current 10).
These are cheap to add (same `apply_pointer_mutation` mechanism) and would
close real blind spots in your own validator's error surface, not
hypothetical ones.

## 3. Overall assessment

The staging kit is honest and internally consistent: I did not find a case
where the validator's own "PASS" claim was unearned, where a schema silently
contradicted the architecture doc, or where a "known gap" was actually hidden
rather than disclosed. The two-mechanism framing ("infinite" = safe
composition + gated Asset Request extension, never free-form runtime code) is
argued consistently across the architecture doc, the master prompt's ten
immutable rules, and the schema's `authority` block (`may_commit_world`,
`may_execute_generated_code`, `may_write_catalog` all hard-pinned `const:
false`). Nori-7 is correctly described as `AUTHORING_REQUIRED`, matching what
I independently verified in the real runtime GLB earlier in this same session
(14 real bones, 10 real keyframed clips shipped, 5 gardening clips honestly
deferred) — the vNext example doesn't overstate that either.

## 4. What I did not do

Did not edit any schema, prompt, or example while reviewing them. Did not
accept my own suggestions as adopted. Did not dispatch Grok on this track —
`GROK_EXECUTION_BRIEF_001.md` remains `QUEUED_NOT_AUTHORIZED`; neither
directive 96 nor 97 opens DNA-vNext or character-backbone work. Did not
promote, quarantine, or touch any catalog. `accepted=false`, `self_accept=false`.

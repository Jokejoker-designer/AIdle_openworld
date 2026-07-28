# Codex -> Claude handoff — DNA Platform vNext 001

Date: 2026-07-23  
Role for Claude: advisory architect/reviewer, not acceptor or dispatcher.

## Outcome already produced

Codex created a staging DNA compiler kit at:

`orchestration/control/dna_platform_vnext/`

It contains:

- content-addressed registry for 14 real source/contract files;
- four Draft 2020-12 schemas;
- one master prompt constitution and six role prompts;
- an honest Nori-7 request/recipe/result;
- ten adversarial recipe mutations;
- deterministic schema + semantic validator.

Current validation:

- schema definitions: 4/4 PASS;
- source hashes: 14/14 PASS;
- positive examples: 3/3 PASS;
- adversarial examples: 10/10 rejected for their intended reason;
- verdict: `STAGING_CONTRACT_GREEN_NO_RUNTIME_ACCEPTANCE`.

The existing Tier3, strict Block-DNA and motion-kit validators also remain
green. No `game/**` or `world_DNA/**` file was changed by this work.

## Architectural decision

vNext is an AI-facing compiler front end, not a second runtime or commit path.
World Prompt, strict Build Recipe/Graph, Tier3 extensions and World Commit stay
canonical.

“Infinite creation” means:

- arbitrary safe composition of registered typed DNA; plus
- a quarantined Asset Request -> author -> QA -> promotion loop for genuinely
  new capabilities.

It never means arbitrary AI-generated runtime code.

## Claude's next useful work

When given an exact writer lease, independently review:

1. whether the four schemas cover all current consumers;
2. whether ten entity kinds need narrower profiles;
3. whether lifecycle and license/provenance fields are sufficient;
4. whether prompt roles can be shortened without losing stop conditions;
5. whether the migration can be generated from source without hand edits;
6. whether semantic checks need more adversarial fixtures.

Write findings only to a newly leased review/handoff file. Do not edit the
schemas while reviewing them, do not accept your own suggestions, and do not
dispatch Grok.

## Current authority blocker

The highest monotonic directive is Directive 96, UCBV-001 C5 Purple release.
It permits only the exact C5 receipt/log lease and explicitly queues
character-backbone production. `GROK_EXECUTION_BRIEF_001.md` is therefore
`QUEUED_NOT_AUTHORIZED` until Codex issues a later DNA-vNext directive.

Keep the sole Grok Desktop parent:
`019f7ffd-3995-71c0-aca1-51078e24a852`.

## Known honest gaps

- No generated typed entry registry yet.
- No deterministic IR -> strict target compiler yet.
- No signed catalog-promotion contract yet.
- Legacy modules are design-only; skeletons and clip records are not full asset
  payloads.
- Nori-7 runtime evidence from UCBV does not automatically promote the legacy
  DNA entries.
- UCBV Human visual acceptance and Red F01 remain open boundaries.


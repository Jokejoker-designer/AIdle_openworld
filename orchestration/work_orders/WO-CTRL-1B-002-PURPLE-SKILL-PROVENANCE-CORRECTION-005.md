# WO-CTRL-1B-002-PURPLE-SKILL-PROVENANCE-CORRECTION-005

Authority: `VERIFY_ONLY` | State: `READY`

Control 1B runtime, the E0 correction receipt and Directive 62 exact two-file
write discipline pass. Directive 62 P0 is rejected only because its transcript
read 50 of 1123 `curiosity-engine` lines and 100 of 292
`evidence-memory-ledger` lines while its receipt claimed both were loaded to
EOF. A source hash or line count is not semantic skill loading.

This is the last automatic correction allowed for this signature. Repetition
routes `CTRL-1B-002` to `NEED_HUMAN`.

## F0 - fresh Purple full-EOF verification

Profile: `aidle-worldgen-purple-acceptance`; TrustLayer:
`purple-team-release-gate`; UI: `ui-visual-critic`; authority: `VERIFY_ONLY`.

Use one fresh real child under the existing parent. Before tests or evidence
writes, read every required skill semantically through EOF. The durable
transcript must contain these explicit coverage calls:

- `curiosity-engine`: offset 1 limit 400; offset 401 limit 400; offset 801
  limit 400. The last chunk must visibly reach EOF.
- `evidence-memory-ledger`: offset 1 limit 200; offset 201 limit 200. The last
  chunk must visibly reach EOF.
- Read each smaller mandatory/routed skill without a truncating limit, and read
  the assigned profile and both character cards completely.

Then re-run the fixture validator, context-router smoke, integration smoke,
witness hash and E0 Draft 2020-12 schema validation.

Write exactly and only, using two direct Grok `write` calls:

- `orchestration/receipts/control/CTRL_1B_002_f0_purple_skill_correction_006.json`
- `orchestration/logs/ctrl-1b-002-f0-purple-skill-correction-006.log`

The receipt must record transcript-backed read ranges for every skill, the
rejected P0 child `019f8776-b30e-7ab3-b981-eb01ae1dacd0`, the two partial-read
findings, exact commands/exits, top-level `smoke_test`, real child lineage,
`product_writes=[]`, `accepted=false`, `self_accept=false`, and
`next_route=WAITING_CODEX`.

## Hard stops

- Same sole Desktop parent `019f7ffd-3995-71c0-aca1-51078e24a852`, coordinator-only.
- Exactly one fresh real child; no resume, follow-up, extra profile, support
  worker, grandchild or other session.
- No helper/temp/cache/scratch/generated script, redirect, delete, move or
  rename. No writes outside the two leased paths.
- No product, test, contract, fixture, screenshot, prior evidence, Scene,
  Character Foundry, DNA, persistence, network or World Commit write.
- No install, Godot change, credential, live provider, public listener, push,
  deploy or publish.
- Parent returns `REVIEW_REQUESTED` / `WAITING_CODEX`, accepted=false.

# WO-G8-001-D2-EXACT-PROVENANCE-CORRECTION-017

Directive: 38  
Task: G8-001  
State: CHANGES_REQUESTED  
Parent: existing Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852` only

## Purpose

Correct only the two blockers in
`orchestration/reviews/CODEX_G8-001_D2_PROVENANCE_CORRECTION_REVIEW_017.json`.
All product, tests, harnesses, screenshots, prior receipts/traces and prior
reviews are immutable. D3 remains blocked and G8 remains unaccepted.

## MAF workflow and lineages

The parent is coordinator-only. Resume exactly the four real installed-profile
lineages below as four correction child tasks. Maximum four active children;
no support profile and no grandchildren.

| Profile | Original D2-016 child | Authority | TrustLayer | UI character |
|---|---|---|---|---|
| companion | `019f830a-e077-7761-9be6-4fedb4a3f69c` | `VERIFY_ONLY` | `blue-team-p0-remediator` | `ui-component-craftsman` |
| manifestation | `019f830a-e078-7291-868d-63c406c499a4` | `VERIFY_ONLY` | `blue-team-p0-remediator` | `ui-component-craftsman` |
| asset | `019f830a-e078-7291-868d-63dadf2dccd2` | `VERIFY_ONLY` | `blue-team-p0-remediator` | `ui-color-type-specialist` |
| persist | `019f830a-e078-7291-868d-63ef06a928fc` | `READ_ONLY_AUDIT` | `purple-team-finding-triage` | `ui-a11y-auditor` |

Each new correction child records both the original child ref and its returned
correction child ref. One writer per file and `self_accept=false` are mandatory.

## Skills and context

Each correction child reads its installed profile, exact character cards,
Directive 38, this work order, Review 017, `orchestration/skills_manifest.yaml`,
the UI dispatch map, active `DESIGN.md`, and all five manifest `always` skills
plus its routed skill in full. Large skill reads must use `read_file` with
explicit non-overlapping offsets through EOF so the actual content enters the
child context. A shell line count, hash, boundary print or process-local read is
not a substitute for semantic loading.

Companion must explicitly read curiosity-engine in these six chunks:
`1-200`, `201-400`, `401-600`, `601-800`, `801-1000`, `1001-1123`.

## Exact provenance representation

For every terminal and material non-terminal call before the final correction
receipt/trace write, and for every original D2-016 call cited as evidence, store:

- `tool_call_id` exactly from durable `chat_history.jsonl`;
- `tool_kind` exactly;
- one-based kind-local ordinal and matching
  `transcript://<child_task_ref>/<tool_kind>/<ordinal>`;
- `arguments_json`, byte-for-byte equal to the transcript call's `arguments`
  string; do not parse and reserialize it;
- actual result/exit and failed exits;
- exact files read and written.

No paraphrase, summary, renamed key, inserted null, omitted `description`, global
ordinal in a kind-local ref, approximate count or wildcard namespace is valid.
The child must run a read-only equality check that compares every recorded
`arguments_json` string with the corresponding durable transcript field and
reports zero mismatches. The final receipt/trace write and child completion are
externally bound by Codex and are exempt from self-reference.

## Exclusive leases

| Profile | Receipt | Trace |
|---|---|---|
| companion | `orchestration/receipts/g8/d2_exact_provenance_correction_017/D2_companion_017.json` | `orchestration/logs/g8-d2-companion-017.log` |
| manifestation | `orchestration/receipts/g8/d2_exact_provenance_correction_017/D2_manifestation_017.json` | `orchestration/logs/g8-d2-manifestation-017.log` |
| asset | `orchestration/receipts/g8/d2_exact_provenance_correction_017/D2_asset_017.json` | `orchestration/logs/g8-d2-asset-017.log` |
| persist | `orchestration/receipts/g8/d2_exact_provenance_correction_017/D2_persist_017.json` | `orchestration/logs/g8-d2-persist-017.log` |

No helper/temp file is allowed. `product_writes=[]`, top-level
`accepted=false`, schema validation against the MAF agent step contract and an
honest handoff are required.

## Completion

Parent may update only `orchestration/control/grok_status.json`. Return
`CHANGES_REQUESTED / WAITING_CODEX`, list all four correction child refs and
artifacts, and keep `d3_spawn_allowed=false`, `accepted=false`,
`parent_product_patch=false`.

Forbidden: product/test/contract/harness/screenshot/prior-evidence edits, D3,
Control 1B, Character Foundry Scene 1C, another top-level session, Grok CLI,
install, credential use, live provider/public network, push, deploy or publish.

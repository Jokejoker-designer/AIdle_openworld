# Standard Grok work-order / dispatch prompt template 001

Distilled from every wave run so far (C1-C5H1, UCBV-001, DNA vNext review,
mockup cast/props production, town-grid import). This is now the REQUIRED
skeleton for every future dispatch prompt to EITHER Grok parent (build
`019f7ffd-...` or design `019f8e3c-...`). Claude fills this template for each
new wave instead of freeform prompts; deviation from it is itself a finding.

Registered in `codex_directive.json` (`standard_prompt_template`) and
`AIDLE_GAME_VISION_LOCK_001.md` §12.

---

## Why this template exists (lessons paid for in real rework)

- **Naming exact files beats "the loader" or "the resource"** — every wave
  that named exact `game/**` paths in the WO up front had a clean one-writer
  lease; ambiguity is where duplicate/overlapping writes start.
- **"Headless PASS" is not QA.** The town-grid-import wave shipped a status
  table claiming DONE with only a headless smoke test — no headed screenshot,
  no QA receipt file existed. A dispatch prompt must say explicitly that
  Purple cannot move off WAITING without a QA_*.json containing a **headed**
  screenshot and a **raw log file path** (not a restated print marker).
- **A receipt's claim is not evidence until it is re-derivable.** Every
  fingerprint/hash printed in a receipt must be independently recomputable by
  Claude from the actual files — cite the algorithm/field, not just the value.
- **Honesty over completeness.** Placeholders for unauthored content are
  required, not optional, and must be visually distinct + labeled
  "concept — not yet authored." Never let a wave imply more is built than is.
- **Additive, not destructive.** Superseding prior art (e.g.
  `town_layout_10phase.json`) means a note + a flag, never an in-place edit or
  delete of working content.
- **Mockup-sourced work is not done at "loads without error."** It is done at
  a passed 100%-visual-match headed comparison against the `MOCKUP_SSOT_V2`
  entry, and at the exact assigned grid position where one exists. Mismatches
  get iterated (redo loop), not disclosed-and-stopped, up to the standing
  3-identical-failures -> `NEED_HUMAN` limit.
- **accepted=false / self_accept=false is not boilerplate** — it must survive
  unchanged through Blue, Red, QA, and Purple. Purple is always the last stop
  before a Human batch, never a stop that closes anything itself.

## The template

```
<WAVE NAME> — <one-line goal> (directive <id>, <WO id if any>)

1. Read (read-only design/context input — list EVERY file the agent must read
   before planning, with a one-line note on why each matters):
   - <path> (<why>)
   - ...

2. Run the wave under Directive <id> (<tier>, <override type if any>):
   - Blue: <exact deliverable(s)>. NAME every game/** (or other) file you will
     write, in both the WO and the receipt. One writer per file. Do NOT
     delete <named existing content>; do NOT edit <named superseded file> in
     place — note it superseded instead.
   - Red: findings-only — <the specific things Red must check for THIS wave,
     enumerated>, lease clean, no blocking findings before QA proceeds.
   - QA: HEADED evidence required — <exact screenshot/log requirements>. Zero
     new engine errors. Attach the raw log FILE PATH in the receipt, not a
     restated marker string. File QA_<wave>_001.json — Purple cannot proceed
     without it existing.
   - Purple: VERIFY_ONLY, WAITING. No self-accept; accepted=false throughout.
     Batch-accept by the Human only.

3. HONESTY rule (state the specific one for this wave): <e.g. no fake GLB, no
   idle-alias, honest placeholder with X label for anything not yet authored>.

4. MOCKUP FIDELITY (state only if the wave places anything sourced from
   MOCKUP_SSOT_V2): the object is not done until it visually matches its
   mockup 100% (headed screenshot comparison) AND sits at its exact assigned
   plot/transform. Iterate to match; do not disclose-and-stop. 3 identical
   failure signatures -> NEED_HUMAN.

5. Escalate (do not proceed) if: <hard-stop trigger list for this wave — Red
   F01 items, deleting existing content, Confirm-gate/manifestation changes,
   anything the plan does not cover>.

6. Acknowledge with: the exact files you will write, the live directive_id, and
   <one wave-specific confirmation, e.g. bounds/fit check, honesty count,
   fidelity self-assessment>. Then run the wave.
```

## Operating note

Claude authors every dispatch from this template, keeps the "why this exists"
lessons current (append new lessons here as they're learned — this is a living
document), and independently re-verifies every wave's receipts against the
template's requirements (esp. #2 QA and #4 fidelity) before anything reaches
the Human for batch-accept. A wave whose receipts don't satisfy the template's
minimums is `CHANGES_REQUESTED` regardless of what its own status table claims.

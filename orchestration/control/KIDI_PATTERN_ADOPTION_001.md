# KIDI pattern adoption 001 — typed collapse classification

Status: `PROPOSAL` · Authored by: `aidle-continuity-conductor`, 2026-07-22
Source studied: `D:/BOTTRADE/kidi`, specifically
`KIDI_SCIENTIST_PROFILE_FULL_INTRO_PACKAGE`
Prompted by: Human Product Lead — "nếu sợ null có thể nghiên cứu phương án đăng
ký KIDI profile vào hệ thống"

## Verdict up front

**Adopt the pattern. Do not import the package.**

KIDI is a physics research visualiser — *TimeParadoxLab 3D, a 5D singularity
spacetime simulator*. Its numerical machinery has nothing to do with game
orchestration. But it has solved, rigorously, a problem that is structurally
identical to the one that bit us tonight, and the **shape** of its solution
transfers exactly.

## The structural match

KIDI's stated problem, from `02_THE_PROBLEM_IT_SOLVES.md`:

> *"a value may not be mathematically zero, but machine arithmetic may still
> collapse it to zero… After that point, the original information is gone."*

Our problem, from tonight's `P1E_004` receipts: `child_task_ref` collapsed to
`null`. Once it is null, we cannot distinguish:

- the wave legitimately spawned no child
- a child ran but its id was never captured
- the id was captured and lost in serialisation
- the agent simply omitted it

**`null` is our `NaN`.** A single token absorbing several distinct causes,
destroying the evidence needed to tell them apart.

The same shape appeared in the pond defect. Three visually different failures —
beige `(218,209,195)`, white `(255,255,255)`, grey `(185,195,189)` — all
returned `PASS` from one check, because per-channel RGB distance **collapses hue
and saturation into a single scalar**. Distinct causes, indistinguishable
outcome. Same disease.

## What transfers

### 1. Typed collapse classification instead of one failure token

KIDI's `ZeroClass` enum does not say "it's zero". It says *which kind* of zero:
`TRUE_ZERO`, `NEAR_ZERO`, `SUBNORMAL_VALUE`, `UNDERFLOW_RISK`,
`FLOAT_UNDERFLOW_TO_ZERO`, `OBSERVED_ZERO_UNKNOWN_ORIGIN`.

Proposed `RefClass` for receipts:

| Class | Meaning |
|---|---|
| `PRESENT` | real durable child ref, cross-checked |
| `NO_CHILD_BY_DESIGN` | wave legitimately spawned no child |
| `CAPTURE_FAILED` | child ran, id not retrievable — **stated, not guessed** |
| `SERIALIZATION_LOST` | id existed at runtime, absent in the written receipt |
| `OBSERVED_NULL_UNKNOWN_ORIGIN` | null found, cause undetermined |

That last one matters most. It is honest about ignorance instead of silently
implying "no child". It is exactly what I demanded of Grok informally tonight —
*"a null ref and an honest note are very different things in an audit"* — and
KIDI has already formalised it.

### 2. Registered walls, not universal scanning

`03_CORE_CONCEPTS.md`: KIDI does **not** create walls for every variable
automatically. A wall is registered deliberately at a known boundary.

Applied here: do not build a generic null-detector across all JSON. Register
walls where collapse actually costs us:

| wall_id | Delta | Fires when |
|---|---|---|
| `RECEIPT_CHILD_REF_NULL` | presence + format of `child_task_ref` | ref null, malformed, or equal to the parent session ref |
| `RECEIPT_VERDICT_NULL` | presence of `verdict` | verdict absent |
| `STATUS_COMPLETED_CHILDREN_MISSING` | presence of the array | cross-check target vanishes |
| `MATERIAL_HUE_COLLAPSE` | hue distance + saturation floor | rendered colour is achromatic or off-hue |
| `SHADOW_SPATIAL_COLLAPSE` | share of shadow budget in largest dark cluster | shadows concentrate in one void |

The last two are already earning their keep — they are the checks that would
have caught the pond and the black band automatically instead of needing me to
measure by hand.

### 3. Bounded budget with honest unresolved states

`ReplayStatus` includes `UNRESOLVED_WITHIN_BUDGET`, `RESOURCE_LIMIT_REACHED`,
`ENGINE_UNAVAILABLE`. `08_LIMITATIONS_AND_GOVERNANCE.md` calls an unresolved
result **"a valid scientific result"**.

That is the right posture for our reminder mechanism: a check that cannot decide
must say so, not default to PASS. Every wrong pond passed because the check's
failure mode was silence.

### 4. The governance discipline itself

`08_LIMITATIONS_AND_GOVERNANCE.md` opens with *"It cannot see what it was not
given"* and lists nine things KIDI explicitly does **not** do — no automatic
repair, no absolute truth claim, no live authority, no production replacement.

That is the same instinct as `AGENTS.md`'s *"documentation is not
implementation"*. Worth copying as a habit for our own subsystem docs.

## What does NOT transfer — do not import

- The split-complex algebra, α-axis kinematics, singularity mathematics. We have
  no float-underflow problems.
- High-precision replay capsules, `precision_digits`, mini-racer engines.
- Any KIDI runtime code into AIdle. Importing a physics visualiser into a game
  orchestration system would repeat exactly the unvalidated-surface mistake this
  project just avoided with the DNA package.

**Take the pattern. Leave the package on D:.**

## Proposed implementation — small

A receipt-gate validator, roughly 100 lines, that:

1. Validates every receipt against the **existing**
   `agent_step_contract.schema.json` (11 required fields). We already own this
   schema and have never pointed it at our own receipts — we validate product
   contracts but not process evidence. That gap is what let tonight's nulls
   through.
2. Applies the registered walls above.
3. Emits a classified report rather than a boolean, with an explicit
   `UNDETERMINED` outcome.
4. Runs as a QA-wave step, so a receipt with a null ref fails the wave that
   produced it rather than being caught days later by a human reading JSON.

No new dependency. No KIDI code. `jsonschema` already exists in the Bridge.

## Honest note on scope

This is process tooling, not product. It does not advance P1E art, Tier 3, or
anything the player sees. It is worth doing because tonight it cost real time:
three pond attempts and four receipts with broken provenance, all found by hand.

Recommend scheduling it **after** the current art programme, unless receipt
integrity regresses again — in which case it becomes urgent, because at that
point we would no longer be able to trust the evidence trail we are using to
judge everything else.

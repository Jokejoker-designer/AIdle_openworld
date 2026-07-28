# WO-OPS-004 — Register a KIDI QA profile for AIdle visual metrics

Authority: `PATCH_DRAFT` · State: `READY`
Issued by: `aidle-continuity-conductor` — **NOT Codex**
Authorized by: Human Product Lead, 2026-07-22
**Run in a separate session.** Not part of the P1E art programme.
**No UX/UI.** Register the profile, emit a report, read the report. That is all.

Source studied: `D:/BOTTRADE/kidi/KIDI_PRODUCTIZATION/public_core_release_candidate`
and `D:/BOTTRADE/kidi/KIDI_SCIENTIST_PROFILE_FULL_INTRO_PACKAGE`

---

## 1. Why KIDI, and the honest limit of the fit

KIDI Core is a **stdlib-only** Python library for numerical boundary integrity.
It returns typed results — `Real`, `Approaching`, `Singular`, `Bottom` — instead
of `inf` / `nan` / a crash, and logs what happened. Its declared authority is
`REPORT_ONLY / SHADOW_ONLY / DIAGNOSTIC_ONLY` with `live_apply_allowed: false`
and `no_decision: true`.

Two properties make it usable here without argument:

- **stdlib-only** — the ENV0/Directive-50 envelope forbids dependency installs.
  KIDI needs none.
- **report-only, no decision authority** — it cannot mutate anything, so it
  cannot threaten World Commit or the validated write path.

**Where it genuinely fits, and this is the load-bearing insight:** our pond
failed three times because the check collapsed colour into one scalar. But
saturation → 0 is a *real mathematical singularity* — **hue is undefined at zero
chroma**, exactly as `atan2(0,0)` is undefined. KIDI would have classified grey
as `SINGULAR` (hue undefined) rather than passing it. That is not a metaphor;
it is the same class of boundary KIDI exists to witness.

**Where it does not fit — state this plainly and do not force it:** a null
`child_task_ref` is a missing string, not a numerical boundary. KIDI must not be
bent to cover it. Receipt field integrity is solved separately and more simply
(§5).

---

## 2. Scope — register one profile, emit one report

Create an AIdle QA profile conforming to
`D:/BOTTRADE/kidi/KIDI_PRODUCTIZATION/private_profile_lab/PRIVATE_PROFILE_SCHEMA.json`.

Required schema fields (all mandatory): `profile_id`, `label`, `domain_family`,
`extends`, `active_walls`, `authority`, `live_apply_allowed`, `no_decision`,
`diagnostic_only`, `eps`, `eps_rel`, `actions`, `forbidden_outputs`,
`eps_not_optimized_for_pf`, `eps_must_be_reported`.

Proposed values:

```
profile_id      : aidle_visual_qa
label           : AIdle Visual QA Boundary Witness
domain_family   : game_visual_qa        (must NOT be "general" per schema)
extends         : null
authority       : REPORT_ONLY
live_apply_allowed : false
no_decision     : true
diagnostic_only : true
```

`forbidden_outputs` must explicitly exclude any accept/reject verdict. **KIDI
reports; it never accepts.** The Human Product Lead remains the only acceptor.

---

## 3. Walls to register — derived from real defects, not invented

The registry is an **allowlist**. `wall.py` rejects wildcard ids
(`*`, `ALL`, `ANY`, `AUTO`, `AUTO_DISCOVER`) by design. Register only these:

| wall_id | Delta | Real defect it would have caught |
|---|---|---|
| `HUE_UNDEFINED_AT_ZERO_CHROMA` | saturation | pond at sat 0.0 % (white) and 5.1 % (grey) both passed the old RGB check |
| `HUE_OFF_TARGET` | angular distance to target hue | pond beige at hue 36.5° — orange family, not water |
| `SHADOW_SPATIAL_COLLAPSE` | 1 − (largest dark cluster share) | 96 % of shadow budget inside one black void, while the global shadow % passed |
| `LUMA_HEADROOM_COLLAPSE` | 1 − blown-pixel fraction | 66.2 % of frame blown while metrics still "passed" |
| `SHADOW_FLOOR_COLLAPSE` | shadow fraction | 0 % shadow content — no depth cue on a fixed-angle camera |

Every one of these corresponds to a defect that shipped past a passing check
tonight and was caught by hand. That is the justification for each; do not add
walls without one.

`eps` values are **provisional** and must be reported alongside results, per the
schema's `eps_must_be_reported`. Do not tune them to make current data pass.

---

## 4. Deliverable — a report, nothing else

1. The profile JSON, schema-valid.
2. A thin adapter that feeds existing QA measurements (mean luma, blown %,
   shadow %, spatial cluster share, pond HSL) into KIDI walls.
3. A generated report using `kidi_audit/report.py` and
   `kidi_audit/report_gate.py`, classified by `classify_report()`.
4. A short written reading of that report against the five historical failures:
   beige `(218,209,195)`, white `(255,255,255)`, grey `(185,195,189)`, the
   black-band render, and the 66 %-blown render. **All five must classify as
   non-PASS.** The current good state — pond hue 182.8°, sat 25.1 %, blown
   1.837 %, shadow 5.903 %, cluster share 40.962 % — must classify as PASS.

If any historical failure classifies as PASS, the wall definition is wrong.
Report that rather than adjusting the data.

**No UI. No dashboard. No web view.** A JSON report and a markdown reading.

---

## 5. Explicitly NOT in this work order

- **Receipt field integrity.** Solve with the schema we already own —
  `E:/AIdle_openworld/Scene/AIdle_Grok_WorldGenesis_Subagents_v1.0/contracts/agent_step_contract.schema.json`,
  11 required fields. We validate product contracts but have never validated our
  own process receipts; that gap is what let tonight's nulls through. Plain
  `jsonschema` validation, no KIDI. Separate work order.
- Any KIDI runtime inside the AIdle game or the Bridge product path.
- The TimeParadoxLab physics visualiser. Noted as an abandoned project; its
  Three.js volume rendering and split-complex algebra have no application to a
  fixed-angle 2.5D cozy game. Its `standalone.html` self-contained build pattern
  is mildly interesting for offline evidence viewers and nothing more.
- Finance domain profiles, `qtq_mfe_*` owner-private profiles.
- Any change to World Commit, approved catalog, or the validated write path.

---

## 6. Acceptance criteria

1. Profile validates against `PRIVATE_PROFILE_SCHEMA.json`.
2. `authority = REPORT_ONLY`, `live_apply_allowed = false`, `no_decision = true`,
   `diagnostic_only = true` — and a test proves the profile cannot emit an
   accept/reject verdict.
3. Five walls registered, no wildcards accepted.
4. All five historical failures classify non-PASS; current good state classifies
   PASS. Show the table.
5. `eps` values reported, not hidden.
6. Report generated as JSON + markdown. No UI.
7. Zero new dependencies — stdlib only.
8. Nothing in `E:/AIdle_openworld/game/**` or
   `E:/AIdle_Blender_Bridge_P0/app/**` is modified.

## 7. Receipt requirements

Real durable child/transcript refs cross-checked against
`grok_status.json.completed_children`. `accepted=false`, `self_accept=false`.
Note in the receipt that KIDI is `REPORT_ONLY` and that adopting it grants it no
authority over acceptance.

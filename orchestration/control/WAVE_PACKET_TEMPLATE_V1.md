# WAVE PACKET TEMPLATE V1 — mandatory for AIdle agent waves

**Status:** ACTIVE · **Authority:** Human Product Lead / Directive host  
**Use:** Every implementation wave (Grok/Claude/Codex) must open with a filled packet in this shape before Blue writes.  
**Aligns:** MAF (Blue / Red / QA / Purple) · TrustLayer x16 · Directive tier + WO

---

```text
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

---

## Role rules (non-negotiable)

| Role | May write product? | Output |
|------|--------------------|--------|
| Blue | Yes — named files only under lease | BLUE_* receipt + diffs |
| Red | No | RED_FINDINGS_*; findings only |
| QA | No product | **QA_\<wave\>_001.json must exist** + raw log path + headed evidence paths |
| Purple | No | VERIFY_ONLY · WAITING until Human batch-accept |

## Receipt naming

```text
orchestration/receipts/<wave_slug>/
  BLUE_<wave>_001.json
  RED_FINDINGS_001.json
  QA_<wave>_001.json          ← required before Purple
  PURPLE_WAITING_001.json
```

## QA_\<wave\>_001.json minimum fields

- `directive_id`, `work_order`, `accepted: false`, `self_accept: false`
- `headed_required: true`
- `screenshot_paths: []` (absolute or repo-relative paths; empty only if NEED_HUMAN for display)
- `raw_log_path: "<file path to engine/headless log>"` — **not** a restated marker string alone
- `checks: { ... }` enumerated against WO acceptance criteria
- `engine_errors_new: 0` or listed with severity
- `art_style` / `world_profile` when applicable

## Mockup fidelity (when MOCKUP_SSOT_V2 is in scope)

Load + smoke PASS is **not** done. Done = headed visual match 100% + exact plot/transform.  
Three identical failure signatures → `NEED_HUMAN` (do not loop forever without escalate).

## See also

- `E:\standards\maf\COMPLIANCE.md`
- `E:\agents\characters\registry.yaml`
- Project `AGENTS.md` authority + workflow

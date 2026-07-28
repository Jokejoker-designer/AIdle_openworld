# WO-POST-UCBV-SELFRUN-001 — Post-UCBV self-run playbook

Directive: **99** · Task: `POST-UCBV-SELF-RUN`
Parent: `019f7ffd-3995-71c0-aca1-51078e24a852`
Authority: `VERIFY_ONLY` for runs · product patch only if Human-flagged blocker
Status: OPEN · `accepted=false` · no self-accept

## Goal

Read/run/report the accepted UCBV foundation play loop on the sole parent:

```
explore → companion (KEY_C) → build preview → commit/cancel
```

Produce zero-error headed (or headless smoke) evidence. **No product patch**
unless a new Human-flagged blocker appears (then escalate to TIER 2 draft).

## Exact write lease

- `orchestration/receipts/post_ucbv_selfrun_001/**`
- `orchestration/logs/post_ucbv_selfrun_001/**`
- `orchestration/evidence/post_ucbv_selfrun_001/**`
- Playbook note: `orchestration/control/POST_UCBV_SELF_RUN_PLAYBOOK_001.md`

**Product writes:** none (unless separate Human-flagged blocker WO).

## Run set (minimum)

1. InputMap / companion KEY_C smoke (existing C5H1 smoke if still green).
2. H1 consolidation flow smoke (explore + build path).
3. Nori presenter build status (glb_c1r, 14 bones, required clips).
4. Optional headed dual-res capture when display available.
5. Decode logs (UTF-16LE if Godot Windows console); record hashes.

## Report fields

- pass/fail per criterion
- residual register delta (open residuals still open: NORI7-V01 until redesign lands)
- no self-accept; queue for Human batch with other TIER 1 waves

## MAF

QA-style VERIFY_ONLY primary; Red may audit honesty of report; Purple optional on batch.

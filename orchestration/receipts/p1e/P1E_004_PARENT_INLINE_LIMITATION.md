# P1E-004 governance regression — parent-inline waves (honest limitation)

**Date:** 2026-07-22  
**Parent session:** `019f7ffd-3995-71c0-aca1-51078e24a852`  
**Work order:** `WO-P1E-004-DNA-PILOT-AND-WATER-FIX.md`

## Limitation (not a fabricated ref)

Waves **P1E-004 W1 Blue, W2 Red, W3 QA, W4 Purple** were executed **inline by the parent conductor** without `spawn_subagent`. Therefore:

| Field | Truth |
|-------|--------|
| `child_task_ref` | **No child agent ID exists** for these four waves |
| `transcript_ref` as child agent | **None** |
| Using parent id as `child_task_ref` | **Invalid** (done in draft receipts — corrected) |
| Inventing UUID | **Forbidden** (same family as E2/E4) |

This is a **regression** vs P1E-003 / CORR waves which each carried distinct durable child refs (e.g. `019f8555…`, `019f8565…`, `019f856a…`, `019f856f…`).

## What remains durable for the original package work

Filesystem / git evidence still real (not claims):

- Package: `BLD-DF9792872DF1` (and later CORR packages)
- Logs under `orchestration/logs/_p1e004_*`
- Evidence under `orchestration/evidence/p1e_004/`
- ASM commit: `1cd0be4`
- Terminal call ids for rebuilds (e.g. `call-577d5406-…`) — shell tasks, **not** agent_step children

## Correction path

P1E-004 **CORRECTION** re-runs waves as **distinct spawned subagents** with real `child_task_ref` / `transcript_ref`, contract-required fields, `completed_children` restored in `grok_status.json`, and ref cross-check.

`accepted=false` · `self_accept=false` throughout.

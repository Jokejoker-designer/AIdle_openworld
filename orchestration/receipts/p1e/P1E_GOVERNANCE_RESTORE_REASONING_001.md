# Governance restore — reasoning record (durable)

**Status:** ACCEPTED by Human Product Lead (2026-07-22 session).  
**Writer policy:** `MERGE_APPEND_PRESERVE`  
**Proof:** `wave_merge_test=true` on `orchestration/control/grok_status.json`  
**Tool:** `orchestration/control/merge_grok_status.py`  

This note records **why** the restore was shaped the way it was. The reasoning matters more than the one-time key put-back.

---

## What failed

Around ~00:30 a wave-level **full rewrite** of `orchestration/control/grok_status.json` replaced the file from a wave template. That write:

1. Dropped human acceptance keys (`env0_001` ACCEPTED by Human Product Lead).
2. Dropped gate keys (`g8_001_status`, world_1 / P1E / Control-1B / Character-Foundry-1C unblocks, Codex hard-block notes).
3. Dropped the four scoped Godot overrides granted by Human Product Lead.
4. Left the file looking “current” while silently erasing institutional memory.

## What the danger actually was

The missing keys themselves were recoverable. The **danger** was the **writer shape**:

> On the next wave, the same full-rewrite path would erase those keys again the moment nobody was checking.

A one-shot put-back without changing the writer is a false fix. The durable fix is:

1. **Restore** all governance keys and scoped overrides from last known good.
2. **Lock writer policy** to `MERGE_APPEND_PRESERVE` — deep-merge + append `completed_children`; never rebuild from wave template only.
3. **Prove** with `wave_merge_test` that a merge append preserves `env0_001` / gates / overrides.

## What was restored (HPL verified)

Seven governance keys (minimum set checked by `--check-governance`) plus four scoped Godot overrides:

| Item | Restored value (summary) |
|------|---------------------------|
| `env0_001` | `status=ACCEPTED` (Human Product Lead) |
| `g8_001_status` | `PASSED_BY_HUMAN_PRODUCT_LEAD` |
| `world_1_integration_gate_opened` | preserved |
| `p1e_unblocked` | preserved |
| `control_1b_unblocked` / note | preserved |
| `character_foundry_1c_unblocked` / note | preserved |
| `human_only_acceptor_while_codex_blocked` + Codex hard-block fields | preserved |
| `scoped_godot_overrides_granted_by_human_product_lead` | 4 entries (G8-UX-001, G8-UX-002, P1E-002-INTAKE, P1E-ART-WAVES-3-AND-4) |

Independent Bridge check (HPL-confirmed):

```
env0-d50-verified^{}  →  1322b95dce0d26a7e9b39673a2e93f6e338c2314
```

Matches Bridge HEAD at verification time.

## Parent-inline honesty (related governance pattern)

P1E-004 parent-inline waves record:

- `governance.original_p1e004_waves = PARENT_INLINE_NO_CHILD_REFS`
- limitation file: `orchestration/receipts/p1e/P1E_004_PARENT_INLINE_LIMITATION.md`

**Rule:** a null `child_task_ref` with an honest explanation is evidence. A bare null is not.

P1E-006 W1 Blue follows the same pattern (parent conductor, not `spawn_subagent`). W2–W4 use real spawned child ids.

## Invariants for every future wave writer

1. **Never** `Write-All` / full template replace of `grok_status.json`.
2. Use only `merge_grok_status.py --patch-file` or `--set-json`.
3. Never set a governance key to `null` to “clear” it.
4. `completed_children` is append/update-by-ref only.
5. Run `python orchestration/control/merge_grok_status.py --check-governance` after merge.
6. Receipts: `verdict` non-null; `accepted=false`; `self_accept=false` unless Human Product Lead accepts.
7. Schema validation expected by Codex on all new receipts.

## References

- Status: `orchestration/control/grok_status.json` → `governance_restore`, `governance.status_file_policy`, `wave_merge_test`
- Merger: `orchestration/control/merge_grok_status.py`
- Limitation (P1E-004): `orchestration/receipts/p1e/P1E_004_PARENT_INLINE_LIMITATION.md`

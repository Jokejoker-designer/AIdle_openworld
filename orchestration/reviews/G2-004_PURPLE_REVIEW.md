# Purple VERIFY_ONLY review — G2-004 (re-review after remediation)

| Field | Value |
|---|---|
| Task | G2-004 — Modular 2.5D starter asset grammar |
| Reviewer | Purple / Devil's Advocate |
| Authority | VERIFY_ONLY (no product patches; no tasks.json ACCEPT) |
| Date | 2026-07-20 |
| Work order | `orchestration/work_orders/WO-G2-004.md` |
| Worker receipt | `orchestration/receipts/G2-004.json` (remediation agent_step_id `G2-004-aidle-asset-2026-07-20-remediation`) |
| Prior Purple | **CHANGES_REQUESTED** — receipt falsely claimed asset-grammar in `validate_project`; no executable checks |

## VERDICT

**ACCEPTED**

Prior blocker is fixed. `scripts/validate_project.py` now defines and invokes
`check_asset_grammar()`, scope stdout includes `asset-grammar`, and independent
re-run returns `AIDLE_VALIDATION=PASS`. Content artifacts (recipe, styles,
provenance) remain present and match acceptance claims. Receipt `smoke_test` is
honest relative to the executable command.

## Acceptance matrix

| Criterion | Result | Evidence |
|---|---|---|
| House recipe modular parts | **PASS** | `cozy_house_small`, `kind=modular_structure_2_5d`, **14 parts**, build_order coverage enforced in validator |
| Style tokens 2.5D | **PASS** | three base_concept profiles + shared tokens; validator checks enum subset + camera/collision locks |
| License/provenance manifest | **PASS** | **20** entries; policy `paid_generation_apis=false`, `neural_world_model=false` enforced |
| Executable smoke for grammar | **PASS** | `check_asset_grammar` in `scripts/validate_project.py` (called from `main`) |
| Honest receipt | **PASS** | command / exit 0 / marker / scope_line match independent re-run |

## Independent verification (Purple re-run)

### Project validator

```
Set-Location E:\AIdle_openworld; python scripts\validate_project.py
→ exit 0
AIDLE_VALIDATION=PASS
scope=blueprint-links,all-schema-shapes,world-positive-negative,fixtures-valid-invalid,
      format-checker,commit-authority,event-envelope,crew,task-dag,asset-grammar
```

### Validator implementation audit

- `def check_asset_grammar(errors)` present (~L348+)
- Invoked from `main()` before PASS/FAIL
- Scope string includes `asset-grammar`
- Checks include: recipe schema, recipe_id/kind, build_order exact cover,
  collision `active_from_stage=complete`, placeholder_id ∈ modular catalog,
  contracts↔game mirror, style base_concept ⊆ world_prompt enum,
  shared tokens free_orbit/collision, provenance policy + path/fragment coverage,
  assets index constraints

### Content spot-check

| Check | Result |
|---|---|
| game + contracts recipe files present | PASS |
| part_count = 14 | PASS |
| modular catalog placeholder_count = 10 | PASS |
| provenance entry asset_id count = 20 | PASS |
| styles: cozy / pastoral / soft_scifi + shared tokens | PASS |
| shared `free_orbit_allowed=false`, `collision_active_from=complete` | PASS |

### Receipt honesty

| Receipt claim | Independent result |
|---|---|
| `command: python scripts/validate_project.py` | PASS when run |
| `exit_code: 0` | PASS |
| `stdout_marker: AIDLE_VALIDATION=PASS` | PASS |
| `scope_line` includes `asset-grammar` | PASS (matches live stdout) |
| `asset_grammar_function: check_asset_grammar` | PASS (function exists + called) |
| state `REVIEW_REQUESTED` / no self-ACCEPT | PASS |

## Prior blockers status

1. Executable asset-grammar smoke — **FIXED**
2. Honest receipt smoke_test — **FIXED**
3. REVIEW_REQUESTED only — **OK**

## Non-blockers (out of scope; unchanged)

1. No Godot mesh instancing runtime for placeholders.
2. No manifestation renderer (G2-002 boundary).
3. world_prompt schema not rewritten.
4. No paid gen / neural world model on critical path.

## Note on workflow

Purple **VERIFY_ONLY** does not write `tasks.json` ACCEPT. Consumer/orchestrator
may advance G2-004 to ACCEPTED on the strength of this review. G3-001 still waits
remaining G2 dependencies per receipt `next_route`.

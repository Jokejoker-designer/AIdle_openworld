# Grok build session (019f7ffd) — BUILDINGS_FIDELITY_V4 prompt

Paste the block below into Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852`
(the Build parent). Authored by Claude conductor after independently verifying
`BUILDINGS_FIDELITY_V3.json` on disk and relaying the Human Product Lead's ruling
on the 6 strike-3 NEED_HUMAN candidates.

---

```
[SUPERVISOR DIRECTIVE] WO-TOWN-GRID-IMPORT-001 continuation — Human Product Lead ruling on the 6 NEED_HUMAN candidates from BUILDINGS_FIDELITY_V3

Human Product Lead reviewed the strike-3 escalation for MARKET.BLD, GARDEN.BLD, WELL.BLD, WINDMILL.BLD, BRIDGE.BLD, LOOKOUT.BLD (BUILDINGS_FIDELITY_V3.json need_human_candidates). Ruling: do NOT close these as accepted residual. Authorize exactly ONE more targeted remesh pass (BUILDINGS_FIDELITY_V4), aimed specifically at each building's own current residual signature — not a generic re-pass:

- MARKET.BLD: market_awning_ok_fruit_still_underdetailed → add fruit/produce detail to stall
- GARDEN.BLD: gazebo_green_dome_ok_fishscale_density → raise dome fishscale density to match mockup
- WELL.BLD: well_sphere_shingles_ok_form_still_high_partial → correct overall form, not just shingle material
- WINDMILL.BLD: windmill_tier_blades_still_simplified → increase blade/tier geometric detail
- BRIDGE.BLD: bridge_cobble_arch_still_soft_pile → sharpen cobble arch, kill "soft pile" read
- LOOKOUT.BLD: watchtower_form_ok_roof_detail_partial → finish roof detail

Rules for this pass:
1. This is the wave's 4th attempt on these 6 objects, not a reset — the 3-strike history stands. If V4 does not reach 100% SSOT match on a given building, do NOT auto-iterate further on it. Stop and return it to NEED_HUMAN for a fresh Product Lead decision (accept vs different strategy) — same law as before, just re-triggered per-building.
2. Do not touch HOME.BLD (CLOSED_PERMANENTLY) or positions (UNCHANGED cadastre SSOT).
3. Workshop/Barn (strike 1 on new roof signature) are NOT part of this authorization — leave them where they are unless you want to note optional V4 for them too per your own "next" list item 2; that one is still your call, not gated on this directive.
4. File as BUILDINGS_FIDELITY_V4.json in orchestration/receipts/town_grid_import_001/, update REDO_LOOP_ITERATIONS_001.json (n=11) and PURPLE_WAITING_001.json. accepted=false, self_accept=false, Purple stays WAITING. Honest scorecard required — do not report matching_100_pct_count above what headed QA actually shows.
5. Acknowledge with the live directive reference and confirmation you're targeting the 6 named signatures above before starting.

Reference: orchestration/control/codex_directive.json → object_level_human_decisions (HUMAN_AUTHORIZED_ONE_MORE_REMESH entry, decided_at 2026-07-24T11:20:00+07:00).
```

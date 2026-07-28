# Grok build session (019f7ffd) — WD-GAZEBO deck reposition prompt

Paste the block below into Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852`
(the Build parent). Authored by Claude conductor after verifying TOWN_ALIGNMENT_V1.json
and relaying the Human Product Lead's ruling on the flagged CONFLICT_WD_GAZEBO_VS_HOME_BLD.

---

```
[SUPERVISOR DIRECTIVE] WO-TOWN-GRID-IMPORT-001 — move WD-GAZEBO wood platform to H12 (Human ruling on flagged conflict)

You correctly flagged CONFLICT_WD_GAZEBO_VS_HOME_BLD in TOWN_ALIGNMENT_V1.json rather than silently moving it: the fairy-street wood platform WD-GAZEBO is centered at plaza origin (0,0), overlapping HOME.BLD (cozy_house_small_A, grid G7), while the actual gazebo building (GARDEN.BLD / cozy_gazebo_A) sits elsewhere at (2,10) / grid H12.

Human Product Lead ruling: move the WD-GAZEBO deck to sit near the real GARDEN.BLD building at H12 — exactly per the cadastre SSOT position, not an approximation. Do not leave it under HOME.BLD.

Scope:
1. Reposition ONLY the WD-GAZEBO wood-platform overlay rect to be adjacent to GARDEN.BLD's actual transform (2.0, 10.0) / grid H12. Use the same rect size/shape already defined for WD-GAZEBO in TOWN_FAIRY_STREET_PLAN_V1, just recentered.
2. Do not move HOME.BLD, GARDEN.BLD, or any other plot/building. Do not touch any of the 6 paused buildings (MARKET/GARDEN/WELL/WINDMILL/BRIDGE/LOOKOUT.BLD — still NEED_HUMAN_AGAIN, no remesh). Do not re-run the full alignment pass, just this one deck.
3. Re-run the headed top-down QA screenshot to confirm the deck now sits correctly next to GARDEN.BLD and no longer overlaps HOME.BLD.
4. Update TOWN_ALIGNMENT_V1.json (or file a small TOWN_ALIGNMENT_V1_PATCH.json) recording the fix: old center, new center, confirmation no other plot moved. Close out the CONFLICT_WD_GAZEBO_VS_HOME_BLD flag as RESOLVED with the new position cited.
5. accepted=false, self_accept=false, Purple stays WAITING.

Reference: orchestration/control/codex_directive.json → object_level_human_decisions (CONFLICT_WD_GAZEBO_VS_HOME_BLD entry, decision HUMAN_RULED_MOVE_DECK, decided_at 2026-07-24T12:07:00+07:00).
```

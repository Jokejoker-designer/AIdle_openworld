# C0 — Executable assertions (Directive 24 / C003)

| ID | Finding | Executable check |
|---|---|---|
| C-A1 | Cancel crop 0/52500 | Runner: Pillow crop `stage_cancel_preview` vs `after_cancel` must change; GDScript: preview_count_after=0, entity_absent |
| C-A2 | Bridge invalid UUID | Headed log must not contain `snapshot_id must look like uuid`; export uses RFC UUID |
| C-A3 | Quest/status 10px no surface | StatusPill high-contrast; font ≥12px at 868; buttons ≥32px |
| C-A4 | error_lines never populated | GDScript ingests log file into `_error_lines`; external runner rejects ERROR: |
| C-A5 | saved choice not exercised | Isolated `--user-data-dir` seed surrealism; hash/content preserved after ephemeral Cozy capture |

Canonical gate: `python scripts/run_g8_headed_visual_c003.py`

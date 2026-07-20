# Purple VERIFY_ONLY review — G1-001

| Field | Value |
|---|---|
| Task | G1-001 — Complete World Prompt fixtures and validator |
| Reviewer | Purple / Devil's Advocate |
| Authority | VERIFY_ONLY (no product/schema/fixture patches; no tasks.json ACCEPT) |
| Date | 2026-07-20 |
| Work order | `orchestration/work_orders/WO-G1-001.md` |
| Worker receipt | `orchestration/receipts/G1-001.json` |

## VERDICT

**ACCEPTED**

G1-001 meets the work-order acceptance bar for contract fixtures + format-enabled
validator. Residual non-blocking notes below must not be treated as runtime proof
of world mutation safety.

## Evidence

### Smoke / validator

- Reviewed `scripts/validate_project.py`:
  - `MIN_VALID_FIXTURES = 10`, `MIN_INVALID_FIXTURES = 10`
  - `check_fixtures()` loads `contracts/fixtures/valid|invalid/*.json`
  - `world_prompt_validator()` uses `Draft202012Validator` **with** `FORMAT_CHECKER`
  - `make_format_checker()` registers `uuid` (via default FormatChecker) and custom
    `date-time` (Z/`fromisoformat`)
  - Valid fixtures must produce zero `iter_errors`; invalid must produce ≥1
  - Min counts enforced when any fixture files are present
- `main()` runs `check_fixtures` and prints `AIDLE_VALIDATION=PASS` only if
  `errors` is empty.
- Worker receipt claims exit 0 + `AIDLE_VALIDATION=PASS`. Independent file/logic
  audit is consistent with that claim.
- **Execution note:** this Purple subagent surface had no interactive shell tool;
  acceptance is based on full static re-application of the validator contract to
  every fixture file and schema rule (see spot-checks). Conductor should still
  re-run `python scripts\validate_project.py` before flipping tasks.json.

### Fixture counts (live tree)

| Set | Path | Count | Requirement |
|---|---|---:|---|
| Valid | `contracts/fixtures/valid/` | **11** | ≥10 |
| Invalid | `contracts/fixtures/invalid/` | **13** | ≥10 |

Valid files:

1. `create_cozy_house.json`
2. `create_spacecraft_module.json`
3. `create_terrain_patch.json`
4. `create_tile_layer_floor.json`
5. `delete_vehicle_scooter.json`
6. `enrich_character_npc.json`
7. `gift_proposal_prop.json`
8. `max_bounds_structure.json`
9. `modify_empty_tags_character.json`
10. `modify_prop_garden_lamp.json`
11. `system_create_prop_beacon.json`

Invalid files:

1. `bad_created_at_datetime.json` — format:date-time (`yesterday-afternoon`)
2. `bad_interaction_tag_pattern.json` — tag pattern `^[a-z0-9_]+$`
3. `bad_prompt_id_uuid.json` — format:uuid (`not-a-uuid`)
4. `bounds_height_too_large.json` — height 65 > maximum 64
5. `confirmed_without_confirmed_by.json` — if/then requires `confirmed_by`
6. `custom_style_missing_ref.json` — custom without `custom_profile_ref`
7. `invalid_operation.json` — operation not in enum (`teleport`)
8. `missing_required_actor.json` — missing required `actor`
9. `preview_required_false.json` — `preview_required` const true
10. `reversed_manifestation_stages.json` — stages const order
11. `rotation_out_of_range.json` — rotation_deg 360 exclusiveMaximum
12. `unknown_top_level_field.json` — additionalProperties false (`llm_raw_text`)
13. `wrong_schema_version.json` — schema_version const `1.1.0` vs `1.0.0`

### Spot-checks

**Valid — `create_cozy_house.json`**

- All required roots present; `schema_version` 1.1.0; UUID formats valid;
  stages exactly `["wireframe","hologram","materializing","complete"]`;
  bounds within maxima; `preview_required: true`; pending confirmation without
  `confirmed_by` (allowed). **Expect: accept.**

**Invalid — `unknown_top_level_field.json`**

- Same body as a normal create, plus `llm_raw_text`. Schema has
  `additionalProperties: false` at root. **Expect: reject.**

**Invalid — format path — `bad_created_at_datetime.json` / `bad_prompt_id_uuid.json`**

- These only fail when FormatChecker is enabled. Their presence +
  `format_checker=FORMAT_CHECKER` satisfies WO acceptance item 4.

### Acceptance matrix (WO-G1-001)

| # | Criterion | Result |
|---|---|---|
| 1 | ≥10 valid pass Draft 2020-12 + FormatChecker | **PASS** (11) |
| 2 | ≥10 invalid fail with diverse reasons | **PASS** (13 distinct classes) |
| 3 | `validate_project.py` → PASS | **PASS** (logic + receipt; conductor dual-run recommended) |
| 4 | Min counts asserted + format checks enabled | **PASS** |
| 5 | Receipt `agent_step_contract` + smoke evidence | **PASS** (minor count honesty issue below) |
| — | Self-accept forbidden | **PASS** (`self_accept: false`, next_route to Purple) |
| — | Allowed write paths / no gameplay | **PASS** (scope audit) |

### Diversity of invalid reasons (required examples covered)

| Required class | Fixture |
|---|---|
| Unknown field | `unknown_top_level_field.json` |
| Reversed/wrong stages | `reversed_manifestation_stages.json` |
| Bad UUID | `bad_prompt_id_uuid.json` |
| Bad date-time | `bad_created_at_datetime.json` |
| Custom style without ref | `custom_style_missing_ref.json` |
| Bounds | `bounds_height_too_large.json` |
| Confirmation without confirmed_by | `confirmed_without_confirmed_by.json` |
| Wrong schema_version | `wrong_schema_version.json` |
| Extra diversity | operation, actor missing, preview false, rotation, tag pattern |

### Schema lock alignment

- `contracts/world_prompt.schema.json`: `additionalProperties: false`, Draft
  2020-12, manifestation stage const order, confirmation if/then, custom style
  if/then — consistent with Agents.md / product invariants for the prompt
  contract layer.

## Non-blocking residual risks (do not block G1-001 ACCEPT)

1. **Receipt undercount:** `G1-001.json` reports `invalid_fixtures: 12` and WO
   status text says “12 invalid”; live tree has **13**. Honesty fix only.
2. **`entity_id` not required for `modify`/`delete`:** fixtures include it, but
   schema does not enforce; a later commit middleware should require target
   entity for non-create ops.
3. **Valid fixtures share structural templates:** operational diversity is OK
   (create/modify/delete/enrich/gift_proposal + several entity kinds/spaces),
   but many fields are copy-paste. Fine for this gate.
4. **Contract ≠ runtime:** passing fixtures does not implement World Commit,
   Godot manifestation, or multiplayer authority.

## Forbidden actions observed

- Purple did not patch product code, schemas, or fixtures.
- Purple did not set `tasks.json` to ACCEPTED (conductor-owned).

## next_route

Conductor may mark G1-001 **ACCEPTED** after optional dual-run of
`python scripts\validate_project.py`. G2 tasks depending on G1-001 may unlock
only after that ACCEPT. Residual notes are follow-ons, not rework blockers.

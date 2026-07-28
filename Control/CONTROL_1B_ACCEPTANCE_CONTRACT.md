# Control 1B — Falsifiable Acceptance Contract

| Field | Value |
|---|---|
| **contract_id** | `control-1b-input-context` |
| **contract_version** | `1.0.0` |
| **status** | `AMENDED_NO_ACCEPT` — Directive 60 Human R camera correction (S0 contract/fixture only); not product acceptance; Codex review required |
| **work_order** | `WO-CTRL-1B-002-R-CAMERA-CORRECTION-002` (Directive 60 supersedes prior machine VERIFIED on Exploration R camera yaw; preserves Directive 57/58/59 receipts) |
| **directive** | Codex Directive 60 (supersedes Directive 59 machine VERIFIED **only** for Exploration R = `rotate_camera_right`; dual-fire / Build R rules retained) |
| **authority_boundary** | Contract + valid fixture + validator hash lock only; **no** Godot product/test/scene implementation in this S0 wave |
| **product_gate** | Runtime Exploration R camera restore is **R1** under the same WO; product acceptance still requires Q2/P3 + Codex |
| **schema** | `orchestration/contracts/control_1b/input_context.schema.json` |
| **valid_fixture** | `orchestration/contracts/control_1b/valid_context_fixture.json` (SHA-256 locked `211605f46db73a4308252d7f10867260b5f8a8dd9f8d5fefc970f3c65f2d719f`; Directive 60 Exploration `rotate_camera_right`) |
| **invalid_fixture** | `orchestration/contracts/control_1b/invalid_context_fixture.json` |
| **executable_validator** | `orchestration/contracts/control_1b/validate_control_1b_fixtures.py` |
| **human_decision** | Exploration: Q = camera left, R = camera right; Build: Q/R = preview rotate only; never dual-fire; remappable InputMap only |
| **prior_audit** | A0 `CTRL_1B_001_a0_a11y_001` / `019f869a-55bb-7210-b2e7-4396cb276a41` |
| **prior_draft** | S1 `CTRL_1B_001_s1_schema_001` / `019f869f-21c3-7513-9d70-c91361eae08a` |
| **sources** | Control Blueprint docx SHA-256 `7985470D14B0CACE25AA4EC46981FB8D5096B27369D6122B57591404AB73B8FF`; `Control/CONTROL_IMPLEMENTATION_MAP.md`; Blueprint §2/§15–§20; Architecture Lock product invariants; Human Product Lead live-play + `CODEX_CTRL-1B-002_HUMAN_R_ROTATE_REVIEW_002` |

This document turns the Control Blueprint + A0 gap matrix into **versioned, fail-closed, testable gates** for later Blue implementation. Documentation alone is not acceptance. Passing a unit test is not multiplayer or visual proof. Product acceptance requires headless smoke **and** headed checklist evidence under a future authorized WO.

---

## 0. Non-claims (devil-advocate lock)

1. This S1 wave **does not implement** Input Context routing, InputMap expansion, HUD, or a11y settings in `game/**`.
2. A0 established Control foundation state = `PARTIAL` (22 key gaps). This contract **does not** flip that state to `ACCEPTED`.
3. Existing proposal→preview→confirm paths (demo/companion) are **source-partial** safety evidence only; they do not satisfy full 1B gates.
4. Character Foundry, World 2, network, install, push, deploy are **out of scope**.
5. `accepted=false` / `self_accept=false` for this contract draft until Codex review.

---

## 1. Five Input Contexts (closed enum)

Exactly these five contexts exist. **Unknown `context_id` values fail closed** (schema + runtime reject).

| context_id | Purpose | Enter / leave (required) | Locomotion default |
|---|---|---|---|
| `exploration` | Move, explore, primary/secondary interact | Default in-world; leave via other context entries | Active (WASD/sprint/jump per bindings) |
| `companion` | Dialogue + Prompt Composer / conversation panel | `companion_call` (C) and/or `prompt_quick_open` (`/`); leave via `cancel_action` (Esc priority) or explicit close | **Suppressed or read-only** while composer/panel owns focus (no silent multi-context fire) |
| `build` | Place/rotate/snap/preview structures | `build_mode_toggle` (Tab) toggle; leave Tab or Esc when no pending confirm | Active unless modal confirm owns focus |
| `inspect` | Entity info, provenance, state | `inspect_entity` (I) or Alt+LMB per bindings | Active |
| `world_tool` | Concept-specific V ability + B panel | `world_ability` (V) / `world_panel` (B); Cozy aliases below | Active |

### 1.1 Context router invariants (fail closed)

| Gate ID | Assertion | Evidence for Blue later |
|---|---|---|
| **C1B-CTX-01** | Exactly one **primary** Input Context is active at a time for action dispatch | Unit: router state machine; smoke: toggle paths |
| **C1B-CTX-02** | Transition to unknown `context_id` is rejected; state unchanged | Invalid fixture case `INV-01-unknown_context_id` |
| **C1B-CTX-03** | Actions not listed in the active context's `allowed_actions` do not fire gameplay effects | Conflict smoke |
| **C1B-CTX-04** | Overlay UIs (pause, settings, modal confirm) stack above contexts but **Esc priority** (§5) still holds | Headed checklist |
| **C1B-CTX-05** | World-specific V/B **semantics** may change by concept; action IDs `world_ability` / `world_panel` remain stable | Cozy slice + future stages |
| **C1B-CTX-06** | Catalog document contains **exactly one** entry for each closed `context_id` (`exploration`, `companion`, `build`, `inspect`, `world_tool`). Duplicate IDs or missing required IDs fail closed | Schema `contexts` min/max 5 + `contains` per id; semantic `context_cardinality` in executable validator |

---

## 2. Stable InputMap action IDs (closed catalog)

### 2.1 Fail-closed ID rules

| Gate ID | Assertion |
|---|---|
| **C1B-ACT-01** | Gameplay code **must not** hard-code physical keycodes for remappable actions; only InputMap action names |
| **C1B-ACT-02** | Unknown `action_id` in config, remap UI, or fixture → **reject** (schema enum / runtime) |
| **C1B-ACT-03** | Every required action in §2.2 is declared in Godot InputMap before headed acceptance |
| **C1B-ACT-04** | Remap UI edits bindings only; it cannot invent new action IDs outside the catalog |

### 2.2 Foundation action catalog (1B minimum)

Aligned to Blueprint §15 with current project names preserved where already present (`move_forward` family).

#### Locomotion / camera (present → keep IDs stable)

| action_id | Default binding (reference) | Notes |
|---|---|---|
| `move_forward` | W / Up | Existing; alias of blueprint `move_up` intent |
| `move_back` | S / Down | Existing |
| `move_left` | A / Left | Existing |
| `move_right` | D / Right | Existing |
| `sprint` | Shift | Existing; hold/toggle a11y applies |
| `jump` | Space | Existing; context-routed secondary meanings in later worlds |
| `camera_zoom_in` | WheelUp | Existing |
| `camera_zoom_out` | WheelDown | Existing |
| `rotate_camera_left` | Q | **Human-locked:** Exploration camera yaw left; not Build hologram rotate |
| `rotate_camera_right` | R | **Human-locked (Directive 60):** Exploration camera yaw right via remappable InputMap; **never** hologram rotate; must not dual-fire with `build_rotate_right` |
| `pause_menu` | Esc | Existing — **must yield to cancel priority** |
| `toggle_debug` | F3 | Existing; non-acceptance-critical |
| `interact` | E | Existing overload → map as `interact_primary` synonym or migrate |

#### Required new / renamed foundation actions

| action_id | Default binding | Required contexts |
|---|---|---|
| `interact_primary` | E | exploration, inspect (and world_tool when tool allows) |
| `interact_secondary` | F | exploration, world_tool (Cozy harvest etc.) |
| `companion_call` | C | exploration → enters companion |
| `prompt_quick_open` | `/` | exploration/companion → composer focus |
| `prompt_send` | Ctrl+Enter | companion (composer focused) |
| `prompt_newline` | Shift+Enter | companion (composer) |
| `build_mode_toggle` | Tab | exploration/build |
| `world_ability` | V | exploration/world_tool (Cozy: Helper Pulse) |
| `world_panel` | B | exploration/world_tool (Cozy: Homestead Panel) |
| `inspect_entity` | I | exploration/inspect |
| `map_open` | M | exploration |
| `camera_reset` | Home | exploration |
| `cancel_action` | Esc (logical; shares physical with pause via priority) | all |
| `confirm_action` | Enter | companion/build/inspect confirm paths |
| `request_undo` | Ctrl+Z | build / post-commit compensation request path |
| `request_redo` | Ctrl+Y | build |
| `delete_proposal` | Delete | **proposal only** — never durable delete |
| `build_place` | LMB (context) | build |
| `build_cancel` | RMB / Esc | build |
| `build_rotate_left` | Q | **build only** |
| `build_rotate_right` | R | **build only** |
| `build_elevation_up` | PageUp / Shift+WheelUp | build |
| `build_elevation_down` | PageDown / Shift+WheelDown | build |
| `build_scale_up` | Ctrl+WheelUp | build |
| `build_scale_down` | Ctrl+WheelDown | build |
| `build_snap_toggle` | X | build |
| `build_grid_toggle` | G | build |
| `build_duplicate` | Ctrl+D | build |
| `build_validate_collision` | K | build |
| `build_validate_navigation` | N | build |
| `build_link` | L | build (preview links only) |

#### Cozy slice aliases (Stage 1 world_tool semantics)

| action_id | Binds as / aliases | Meaning |
|---|---|---|
| `cozy_helper_pulse` | may alias `world_ability` in Cozy | V Helper Pulse |
| `cozy_homestead_panel` | may alias `world_panel` in Cozy | B Homestead Panel |

Alias is allowed **only** as a named alias of a catalog action; inventing free-form IDs fails.

### 2.3 Physical vs logical split (R and Esc) — Human-locked (Directive 60)

Human Product Lead locked behavior (live play). Directive 60 **supersedes** prior machine VERIFIED evidence that treated Exploration R as camera-noop / hologram-only-safe without requiring camera yaw.

| Physical key | Exploration | Companion | Build | Inspect | World Tool |
|---|---|---|---|---|---|
| **R** | **`rotate_camera_right` only** (camera yaw right); **never** hologram / preview rotate | May re-speak proposal (optional Companion binding, separate action if used) | **`build_rotate_right` only** (preview/hologram); **never** camera yaw | No hologram rotate; no camera dual-fire | No hologram rotate; no camera dual-fire |
| **Esc** | Pause **only if** no cancel target | Close composer / stop non-critical dialogue first | Cancel preview/placement first | Deselect / close inspect first | Close tool panel first |
| **Q** | **`rotate_camera_left` only** (camera yaw left); never hologram | — | **`build_rotate_left` only** (preview); never camera | — | — |

**Gate C1B-ACT-05:** Binding the same physical event to fire **both** `rotate_camera_right` and `build_rotate_right` (or left equivalents) in the same frame without router isolation is a **hard fail**. Context-isolated bindings (Exploration-only camera vs Build-only preview) are **required**, not optional.

**Gate C1B-ACT-06 (Human R camera):** In Exploration, physical R **must** dispatch remappable `rotate_camera_right` and change camera yaw; Exploration R **must not** rotate a hologram. In Build, physical R **must** dispatch remappable `build_rotate_right` only and **must not** change camera yaw.

---

## 3. Conflict rule (one physical input → one active-context action)

| Gate ID | Assertion | Fail example (from A0) |
|---|---|---|
| **C1B-CF-01** | One physical input event must not dispatch actions belonging to **multiple** active contexts in the same frame | R camera + Build rotate simultaneous |
| **C1B-CF-02** | Most-specific context wins when stacked modifiers apply (Blueprint §16 wheel rules) | Wheel zoom vs Alt-tool vs Shift-elevation |
| **C1B-CF-03** | LMB must not simultaneously drive locomotion and tool use | Blueprint §3.2 / §16.2 |
| **C1B-CF-04** | UI-focused text fields consume character keys; world actions do not double-fire | Composer open + `/` or letters |
| **C1B-CF-05** | Space/jump vs UI accept: dedicated actions; no silent dual binding to both jump and ui_accept | G8-UX partial mitigation remains required |
| **C1B-CF-06** | Conflict matrix is machine-checkable against catalog + active context | Headless smoke |

**Forbidden:** "global always-on" handlers that ignore the context router for remappable foundation actions (historical A0 failures: R always camera even in Build; Esc always pause; E always companion toggle). Context-isolated R (Exploration camera / Build preview) is the Human-locked correct behavior — dual-fire remains forbidden.

---

## 4. Required hotkey suite (acceptance checklist seeds)

| Gate ID | Physical (default) | action_id | Required behavior | A0 finding |
|---|---|---|---|---|
| **C1B-HK-01** | `/` | `prompt_quick_open` | Opens Prompt Composer and focuses input | F05 MISSING |
| **C1B-HK-02** | Ctrl+Enter | `prompt_send` | Sends prompt for Companion interpretation (not plain Enter alone as sole path when policy requires Ctrl+Enter) | F06 MISSING |
| **C1B-HK-03** | Tab | `build_mode_toggle` | Enters/exits Build Mode context | F07 MISSING |
| **C1B-HK-04** | V | `world_ability` / `cozy_helper_pulse` | Cozy Helper Pulse in Stage 1 | F08 MISSING |
| **C1B-HK-05** | B | `world_panel` / `cozy_homestead_panel` | Cozy Homestead Panel in Stage 1 | F08 MISSING |
| **C1B-HK-06** | Delete | `delete_proposal` | Creates **Delete Proposal only**; never direct durable delete | F09 GAP |
| **C1B-HK-07** | Ctrl+Z | `request_undo` | Rollback / compensating mutation **request**; does not erase history | F10 GAP |
| **C1B-HK-08** | Esc | `cancel_action` then `pause_menu` | Cancel priority (§5) | F04 FAIL_PRIORITY |
| **C1B-HK-09** | R in Build | `build_rotate_right` | Build-only hologram/preview rotate; **never** camera yaw | F03 / Human lock |
| **C1B-HK-10** | R in Exploration | `rotate_camera_right` | **Camera yaw right** via remappable InputMap; **never** hologram rotate; no multi-context dual-fire | Human Product Lead live-play + Directive 60 (supersedes prior machine “Exploration R camera no-op” VERIFIED) |

---

## 5. Esc cancel priority (ordered)

When Esc is pressed, evaluate **in order**; stop at first applicable:

1. Cancel **pending confirmation receipt** / confirmation hold (no commit)
2. Cancel **active hologram / preview placement** (no orphan entity; no ownership; no collision)
3. Close **Prompt Composer** or non-critical Companion dialogue / animation interrupt
4. Close **Inspect** panel / deselect entity
5. Close **World Tool panel** (B panel) if open without pending confirm
6. Exit **Build Mode** if design chooses Esc-to-exit when idle (optional; Tab remains primary toggle)
7. **Only then** `pause_menu`

| Gate ID | Assertion |
|---|---|
| **C1B-ESC-01** | If any of steps 1–5 apply, pause must **not** open on that press |
| **C1B-ESC-02** | Cancel never leaves orphan preview entities or half-applied collision |
| **C1B-ESC-03** | Cancel is always safe (no durable mutation) |

---

## 6. Context HUD (≤4 actions)

| Gate ID | Assertion |
|---|---|
| **C1B-HUD-01** | Context HUD shows **at most four** actions for the active context |
| **C1B-HUD-02** | HUD uses **text + icon and/or pattern** — color is never the sole cue |
| **C1B-HUD-03** | HUD updates on context change within one frame of router transition |
| **C1B-HUD-04** | Full keymap is **not** dumped on the main HUD |
| **C1B-HUD-05** | Action bar / HUD entries used for Confirm/Cancel must be keyboard-focusable (no permanent `FOCUS_NONE` on required actions) |

### 6.1 Example Cozy exploration HUD (≤4)

1. `[E] Interact`  
2. `[F] Harvest / secondary`  
3. `[V] Helper Pulse`  
4. `[Tab] Build`  

### 6.2 Example Build HUD (≤4)

1. `[LMB] Place`  
2. `[Q/R] Rotate`  
3. `[X] Snap`  
4. `[Esc] Cancel`  

---

## 7. Accessibility gates

All are **required** for Control 1B foundation acceptance (map gate §1B.7).

| Gate ID | Setting / capability | Assertion |
|---|---|---|
| **C1B-A11Y-01** | Remap | All catalog actions remappable via UI; persists; reloads |
| **C1B-A11Y-02** | Left-hand preset | One-click apply; no unknown actions; no conflict violations after apply |
| **C1B-A11Y-03** | One-hand preset | Same as left-hand with one-hand layout |
| **C1B-A11Y-04** | Hold vs toggle | At least `sprint` and applicable hold-to-activate tools support hold/toggle option |
| **C1B-A11Y-05** | Mouse sensitivity | Stored and consumed by camera/look/pan paths that use mouse delta |
| **C1B-A11Y-06** | Invert zoom | Optional invert for wheel zoom |
| **C1B-A11Y-07** | Reduced motion | Honored by manifestation / camera shake / non-essential motion; no required gameplay soft-lock |
| **C1B-A11Y-08** | Disable screen shake | Independent or folded into reduced motion with explicit control |
| **C1B-A11Y-09** | Cursor size | Configurable size scale; context cursor still readable |
| **C1B-A11Y-10** | Action name near cursor | Optional/on setting shows current action label |
| **C1B-A11Y-11** | No mandatory double-click | Destructive or primary confirm paths work without double-click |
| **C1B-A11Y-12** | Confirmation hold | Configurable hold duration for significant confirms (default reference **0.8s**; range e.g. 0.0–2.0s; 0 = instant for accessibility) |
| **C1B-A11Y-13** | Pause during hologram | Player can pause while hologram pending without orphaning incorrectly |
| **C1B-A11Y-14** | Non-color cues | Valid/invalid placement, Eco signals, cursors use shape/icon/pattern + text |
| **C1B-A11Y-15** | Keyboard discoverability | Confirm/Cancel/Demo-critical controls in focus order; not mouse-only |

---

## 8. Safety and authority boundary

Product invariant: **Prompt → structured proposal → validate → preview → explicit confirm → World Commit**. LLM proposes; only World Commit mutates canonical durable state.

| Gate ID | Assertion |
|---|---|
| **C1B-SAFE-01** | No direct delete of durable world entities from a single keypress |
| **C1B-SAFE-02** | `delete_proposal` creates a proposal only; requires preview impact + explicit confirm before commit path |
| **C1B-SAFE-03** | `request_undo` creates compensating/rollback **request**; does not erase audit/history |
| **C1B-SAFE-04** | Preview / hologram has **no ownership**, **no official collision**, not world truth |
| **C1B-SAFE-05** | Collision/ownership activate only after manifestation **COMPLETE** (or equivalent authoritative complete state) |
| **C1B-SAFE-06** | Cancel clears preview without orphans |
| **C1B-SAFE-07** | No client-authoritative durable mutation; commit only via World Commit service / schema path |
| **C1B-SAFE-08** | Scale/elevation clamped to Style Profile + gameplay limits |
| **C1B-SAFE-09** | Paid / public / irreversible / marketplace operations remain HITL-gated outside this contract |
| **C1B-SAFE-10** | Companion tools remain proposal-only (no silent commit) |

**Forbidden durable operations on key-down alone:** structure delete, large terrain change, owned structure move, Style Profile swap, anomaly activation, paid resource spend, world publish.

---

## 9. Machine fixtures and schema

| Artifact | Role |
|---|---|
| `input_context.schema.json` | Fail-closed JSON Schema for a Control 1B context contract document |
| `valid_context_fixture.json` | One complete document that **must validate** (SHA-256 locked) |
| `invalid_context_fixture.json` | Suite of **twelve** invalid payloads; each has an intended root/subschema/semantic target |
| `validate_control_1b_fixtures.py` | **Executable deterministic harness** — sole proof path for fixture PASS/FAIL |

### 9.1 Schema rules (summary)

- `additionalProperties: false` at all object levels  
- Closed enums for `context_id`, foundation `action_id`, mutation_class safety flags  
- `contexts`: length **exactly 5** and **exactly one** of each closed `context_id` (schema `contains` + semantic cardinality)  
- `context_hud.max_actions` **const 4** (or maximum 4)  
- `safety.direct_durable_delete_allowed` **const false**  
- `safety.preview_owns_collision` **const false**  
- `safety.preview_owns_ownership` **const false**  
- Unknown context/action IDs invalid  

### 9.2 Executable validator (required evidence)

Run:

```text
python orchestration/contracts/control_1b/validate_control_1b_fixtures.py
```

| Check | Required outcome |
|---|---|
| `valid_context_fixture.json` hash | Must equal the lock in `validate_control_1b_fixtures.py` (`VALID_FIXTURE_SHA256_LOCKED`; Directive 60 updates lock when Exploration allows `rotate_camera_right`) |
| Valid document | **PASS** full schema + semantic rules (cardinality, multi-context R isolation, Esc order); Exploration `allowed_actions` **includes** `rotate_camera_right` |
| Each of 12 invalid payloads | **FAIL** against its **intended** root/subschema/semantic rule |
| INV-08 | **FAIL** — multi-context R dual-fire (camera + build rotation without isolation) — **still required** under Directive 60 |
| INV-09 | **FAIL** — Esc/pause precedes cancel (wrong priority) |
| Harness exit | Nonzero if valid fails or any invalid unexpectedly passes |

**Non-proof (forbidden as acceptance evidence):**

- Rejecting only the `invalid_context_fixture.json` **suite root** (wrapper is not a catalog document).  
- Counting schema errors on the suite wrapper as if each case were executed.  
- Manual narrative without harness output.

Each invalid case reports `case_id`, declared `expected_reject` reason(s), validation target, and PASS/FAIL.

### 9.3 Fixture counts

| File | Count |
|---|---|
| Valid root documents | **1** |
| Invalid suite cases | **12** |

Blue must not claim acceptance until this executable validator exercises these fixtures and product smokes map to gate IDs above.

---

## 10. Headed acceptance checklist (for later Blue — not implement now)

Use after `CTRL-1B-002` implementation. Each row needs PASS with screenshot/video or interactive witness + headless evidence where noted.

### 10.1 Context router

- [ ] **H-01** Boot in Exploration; HUD ≤4 exploration actions  
- [ ] **H-02** `/` opens Prompt Composer; focus in field; letters do not move player  
- [ ] **H-03** Ctrl+Enter sends; Shift+Enter newline does not send  
- [ ] **H-04** Esc closes composer before pause  
- [ ] **H-05** Tab enters Build; HUD switches to build ≤4  
- [ ] **H-06** Tab exits Build cleanly  
- [ ] **H-07** I enters Inspect; entity provenance visible without durable mutation  
- [ ] **H-08** V triggers Cozy Helper Pulse (or clear empty-state feedback)  
- [ ] **H-09** B opens Homestead Panel; Esc closes panel before pause  

### 10.2 Conflicts and required keys

- [ ] **H-10** In Exploration, R rotates **camera yaw right** via `rotate_camera_right` (real InputMap/router path); R does **not** rotate a hologram (**Directive 60 Human lock**; supersedes prior “Exploration R camera no-op” machine VERIFIED)  
- [ ] **H-11** In Build with hologram, R rotates hologram/preview only; camera does not dual-fire  
- [ ] **H-12** Q rotates hologram left in Build only; Exploration Q rotates camera left only  

- [ ] **H-13** Pending preview: Esc cancels preview, no pause, no orphan  
- [ ] **H-14** No pending cancel target: Esc opens pause  
- [ ] **H-15** Delete with selected durable target creates Delete Proposal UI, not instant delete  
- [ ] **H-16** Ctrl+Z requests compensation/rollback path; history retained  

### 10.3 Proposal → commit boundary

- [ ] **H-17** Prompt path shows Companion understanding + Proposal Card  
- [ ] **H-18** Preview hologram: no collision body ownership; can walk through / no official block  
- [ ] **H-19** Confirm requires explicit control + configurable hold when significant  
- [ ] **H-20** Only after confirm does manifestation proceed; durable state only via commit path  
- [ ] **H-21** Cancel mid-preview leaves world revision unchanged  

### 10.4 Accessibility

- [ ] **H-22** Remap `interact_primary` to another key; E no longer interacts  
- [ ] **H-23** Apply left-hand preset; still conflict-clean  
- [ ] **H-24** Apply one-hand preset; core loop still possible  
- [ ] **H-25** Sprint toggle mode works  
- [ ] **H-26** Mouse sensitivity change observable  
- [ ] **H-27** Reduced motion: manifestation skips/reduces motion; no soft-lock  
- [ ] **H-28** Cursor size large setting readable  
- [ ] **H-29** Confirmation hold set to 0 and to ≥0.8s both work  
- [ ] **H-30** Confirm/Cancel reachable by keyboard focus (not mouse-only)  
- [ ] **H-31** Invalid placement uses non-color cue (icon/pattern/text)  

### 10.5 Cozy slice smoke (foundation + Stage 1)

- [ ] **H-32** Farming/robot Helper Pulse discoverable via V + HUD  
- [ ] **H-33** Homestead Panel sections reachable without relearning WASD/E  

### 10.6 Hard fail if any true

- [ ] Direct durable delete on Delete key  
- [ ] Preview owns collision/ownership  
- [ ] Unknown action/context accepted  
- [ ] Multi-context dual fire on one physical key  
- [ ] HUD shows >4 simultaneous primary context actions  
- [ ] Product patches claimed under WO-CTRL-1B-001 alone  

---

## 11. Headless smoke expectations (later Blue)

Minimum automated checks (names illustrative):

1. Run `validate_control_1b_fixtures.py` → valid PASS + 12/12 invalid FAIL for declared reasons  
2. Do **not** treat suite-root rejection as fixture proof  
3. InputMap contains all §2.2 required actions including `rotate_camera_right`  
4. Simulated router: Exploration R dispatches `rotate_camera_right` (camera yaw) and does **not** call `build_rotate_right`; Build R dispatches `build_rotate_right` only  
5. Simulated Esc priority queue order  
6. `delete_proposal` / `request_undo` mutation_class flags never `direct_durable`  
7. Context HUD builder clamps to 4  
8. Catalog loader rejects duplicate/missing context IDs (C1B-CTX-06)  

---

## 12. Mapping A0 findings → contract gates

| A0 finding | Contract gates |
|---|---|
| F01 five contexts + router | C1B-CTX-01..05 |
| F02 stable action catalog | C1B-ACT-01..05 |
| F03 R context split (Build preview / Exploration camera) | C1B-HK-09/10, C1B-CF-01, C1B-ACT-05/06; Directive 60 Human lock |
| F04 Esc cancel priority | C1B-ESC-01..03, C1B-HK-08 |
| F05–F10 hotkeys | C1B-HK-01..07 |
| F11 HUD ≤4 | C1B-HUD-01..05 |
| F12–F17 a11y | C1B-A11Y-01..15 |
| F18 focus | C1B-HUD-05, C1B-A11Y-15 |
| SAFE delete/undo | C1B-SAFE-01..03,10 |

---

## 13. Versioning and change control

- Bump `contract_version` on any gate ID semantic change.  
- Fixtures and schema must remain co-versioned with this document (`1.0.0`).  
- Codex acceptance of this contract is a prerequisite to authorize `CTRL-1B-002` product work.  
- Self-accept by schema author is **forbidden**.

---

## 14. Verdict trail

| Wave | Verdict | Note |
|---|---|---|
| S1 (Directive 56) | `S1_CONTROL_1B_CONTRACT_DRAFTED_NO_ACCEPT` | Initial draft; Codex F01–F03 open |
| C0 (Directive 57) | `C0_CONTROL_CONTRACT_CORRECTION_COMPLETE_NO_ACCEPT` | Durable meta bound; executable validator; context cardinality hardened |
| S0 (Directive 60) | `S0_R_CAMERA_CONTRACT_AMENDED_NO_ACCEPT` | Human-locked Exploration R = `rotate_camera_right`; Build R = preview only; no dual-fire; valid fixture + hash lock amended; INV-08 still FAIL; **no** `game/**` patch; `accepted=false` |

Falsifiable gates, closed catalogs, fixtures, executable harness, and headed checklist are present. S0 under Directive 60 amends contract + valid fixture only for Human R camera behavior. No Godot implementation in this wave. No product acceptance claimed. Prior Directive 59 machine VERIFIED is **superseded on Exploration R camera yaw only**. `accepted=false` / `self_accept=false` until Codex accepts.

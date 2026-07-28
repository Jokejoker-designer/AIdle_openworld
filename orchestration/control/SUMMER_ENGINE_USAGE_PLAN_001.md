# Summer Engine 0.5.54 — AIdle usage plan 001

**Status:** PLAN ONLY · `accepted=false` · **không cài / không chạy installer** cho đến Human HITL  
**Installer (đã inspect):** `E:\SummerEngine-0.5.54-Setup.exe`  
**Directive:** 99 · Parent session: `019f7ffd-3995-71c0-aca1-51078e24a852`  
**Related:** `ai_gdt/AI_GDT_INTEGRATION_001.md`, `godot_mcp_aidle_bridge.md`, `COMMERCIAL_COMPLETION_WAVE_PLAN_001.md`

---

## 0. Executive verdict

| Câu hỏi | Kết luận |
|---------|----------|
| Summer có **tăng tốc hoàn thiện** AIdle không? | **Có — có điều kiện**, như **sidecar accelerate** (editor ops + verify loop + UI/scaffold), **không** thay Godot 4.3 pin hay MAF authority. |
| Thay thế Godot stock 4.3? | **Không.** Runtime ship / smoke headless vẫn pin `tools/Godot_v4.3-stable_win64_console.exe` + `game/`. |
| Thay AI-GDT / Blender cast pipeline? | **Không.** Cast/prop production path of record = Blender batch + quarantine; Summer gen 3D = paid HITL + quarantine giống AI-GDT. |
| Cài ngay? | **Không** — chờ Human `INSTALL_SUMMER_HITL_001` (hoặc tương đương). |

**Lợi ích chính cho AIdle (ước lượng khi vận hành đúng lease):**

1. **MCP 52 tools** (scene / diagnostics / play / screenshot / batch) → agent inspect + verify nhanh hơn so với CLI headless-only.  
2. **Verification ladder** (compile → screenshot → play → SimulateInput) → commercial evidence / headed capture nhanh hơn.  
3. **Skills game-dev** (debug, gdscript-patterns, ui-basics, art-direction, tune-performance) → giảm vòng “guess-edit-fail” trên UI/control polish.  
4. **Optional cloud generate_*** → song song AI-GDT prop shell (vẫn quarantine + style lock).

**Rủi ro chính nếu dùng sai:**

- Agent “vibe-build” đè lên architecture lock / World Commit / Persist.  
- Dual-editor (Summer + stock Godot) sửa cùng scene → conflict `.tscn` / `.godot`.  
- Paid `summer_generate_*` / URL import lọt network free-agent ship path (Red F01).  
- Engine fork ≠ Godot 4.3 exact → API/plugin drift.

---

## 1. Artifact đã kiểm tra (installer)

| Field | Value |
|-------|--------|
| Path | `E:\SummerEngine-0.5.54-Setup.exe` |
| Size | ~588 MB (`588004608` bytes) |
| Product label | Summer Engine **0.5.54** |
| Authenticode | **Valid** |
| Signer | `CN=Summer Engine ApS, O=Summer Engine ApS, L=Copenhagen, C=DK` |
| Code-signing CA | Certum Code Signing 2021 CA |
| Cert window | 2025-09-25 → 2026-09-25 |
| Thumbprint | `52680DE588C30D376618E7EB0C1E53E21530154A` |

**Nguồn product (public):**

- Engine + download: https://summerengine.com  
- Agent layer (MIT): https://github.com/SummerEngine/summer-engine-agent  
- MCP local API default: `localhost:6550`  
- npm CLI: `npx -y summer-engine@latest` (~3 MB package; engine app ~1 GB if installed via CLI)

**Mô hình license (tóm tắt):**

| Thành phần | License / cost |
|------------|----------------|
| Desktop engine app | Free download, closed source (hiện tại) |
| CLI + MCP + skills | MIT open source |
| Hosted AI / generate image·3d·audio·video / cloud | **Paid** Summer services — HITL only trên AIdle |

---

## 2. Summer là gì so với stack AIdle hiện tại

```
┌──────────────────────────────────────────────────────────────────┐
│  Grok / MAF / TrustLayer x16  (sole parent, leases, receipts)    │
├──────────────────────────────────────────────────────────────────┤
│  AUTHORITY RUNTIME (unchanged)                                   │
│  · Godot 4.3 stock · game/** · World Commit · Persist · smokes   │
├────────────────────────────┬─────────────────────────────────────┤
│  AI-GDT support            │  SUMMER SIDECAR (this plan)         │
│  · Godot-MCP (opt-in)      │  · Summer Editor (Godot-compatible) │
│  · Meshy/Tripo/Motion…     │  · Summer MCP (52 tools :6550)      │
│  · quarantine adapters     │  · Skills + CLI doctor              │
│  · Blender cast path       │  · Optional paid generate_*         │
└────────────────────────────┴─────────────────────────────────────┘
         │ promote only via WO named paths + receipt
         ▼
   game/assets · cast_roster · p1e_cozy · main galleries
```

| Capability | Stock Godot 4.3 + CLI | Godot-MCP (AI-GDT) | Summer Engine + MCP |
|------------|----------------------|--------------------|---------------------|
| Headless smoke | **Production path** | Yes | Possible if project opens; **not** ship authority |
| Scene tree inspect | Manual / script | Yes | Yes (`summer_get_scene_tree`, …) |
| Screenshot evidence | Limited | Plugin-dep | Strong (`summer_screenshot` viewport/scene/game) |
| Play + debugger errors | Headed manual | Runtime hooks | `summer_play` / `summer_get_debugger_errors` |
| Input sim / probe | Custom | Varies | `SimulateInput` / `RunVerification` via batch |
| Hosted 3D/image gen | Via AI-GDT tools | Catalog | `summer_generate_*` **paid HITL** |
| Skills pack | AIdle profiles | — | Summer skill bundle (do not override MAF) |
| Godot version pin | **4.3** | 4.x plugin | Summer fork (~Godot-family); **verify open of 4.3 project** |

---

## 3. Hard boundaries (AIdle law — không đàm phán)

1. **World Commit** = sole durable mutator. Summer MCP **không bao giờ** gọi economy/inventory commit.  
2. **`accepted=false` / no self-accept** — mọi promote vẫn Human batch.  
3. **Red F01** — no free-agent network ship; no credentials in `game/` or MCP logs.  
4. **Exact lease** — mọi edit `game/**` cần WO path list + one writer + receipt.  
5. **Vision lock** — Companion text-only MVP; no TTS/lipsync via Summer gen audio.  
6. **T2-3D unrestricted** vẫn **staged** — `summer_generate_3d` = cùng tier HITL+quarantine như Meshy.  
7. **Không grandchildren** — Summer agent skills không spawn crew riêng ngoài parent MAF.  
8. **Không scaffold project mới** thay AIdle — **open existing** `E:\AIdle_openworld\game` only (sau pilot).  
9. **Smoke ship path** vẫn stock Godot 4.3 headless; Summer evidence là **bổ sung**, không thay gate machine.  
10. **`.summer/` memory** (GameSoul, etc.) nếu tạo: chỉ sidecar notes — **không** là world truth.

---

## 4. Map Summer tools → AIdle workstreams

### 4.1 High acceleration (ưu tiên)

| AIdle workstream | Summer tools / skills | Output expected | Lease class |
|------------------|----------------------|-----------------|-------------|
| Commercial **headed evidence** (Gate 9 GPU, visual QA) | `summer_screenshot`, `summer_play`, console/debugger | PNG + error log under `evidence/**` | VERIFY_ONLY / evidence write |
| **UI / Control 1B polish** residual | scene ops + `ui-basics` skill + script errors | Named `.tscn` / `.gd` only | PATCH_DRAFT exact files |
| **Outline / materials** visual check | screenshot + inspect node props | Pass/fail report; mat apply only if leased | VERIFY then optional PATCH |
| **Mockup cast gallery** placement tweaks | `summer_set_prop`, instantiate under gallery roots | Position/scale only on allowed nodes | named main/scene lease |
| **Debug crash / null** after playtest | `summer:debug` pattern + `get_debugger_errors` | Finding + proposed patch | READ_ONLY then PATCH_DRAFT |
| **Perf feel** (non-budget machine) | `tune-performance` skill + play | Notes for Gate 9; no silent project setting churn | VERIFY_ONLY first |

### 4.2 Medium acceleration (sau pilot ổn)

| Workstream | Summer role | Constraint |
|------------|-------------|------------|
| Prop shell volume | `summer_generate_3d` / image | Paid + Human; land **quarantine** not `game/` |
| Audio SFX draft | `summer_generate_audio` | Post-alpha for voice; SFX only if style OK + HITL |
| Import external GLB | `summer_import_asset` / URL | URL = network HITL; then `validate_ai_gdt_intake.py` |
| Level layout draft | scene composition skills | Copy to AIdle scenes only via WO; no free world truth |

### 4.3 Low / avoid (không dùng để “hoàn thiện core”)

| Area | Why avoid as primary |
|------|----------------------|
| Character **cast production** | Path of record = Blender 14-bone batch + real AnimationPlayer keys |
| DNA / Block Assembly / Persist | Architecture lock; Summer không hiểu AIdle authority |
| Economy / World Commit | Hard forbid |
| Full game scaffold `summer create` | Contaminates product with starter templates |
| Multiplayer Summer cloud | Out of scope AIdle openworld MVP |
| Replace stock Godot in CI smokes | Version drift risk |

---

## 5. Phases (chi tiết, thứ tự)

### Phase S0 — Plan freeze (DONE khi file này + journal)

- [x] Inspect installer signature/size/version  
- [x] Research CLI/MCP/skills boundaries  
- [x] Write this plan  
- [ ] Human read + optional edits  
- **Gate:** Human message kiểu `INSTALL_SUMMER_HITL_001` hoặc `defer Summer`

### Phase S1 — Install HITL (Human only; agent **không** tự chạy)

**Mục tiêu:** Engine app + Node CLI + doctor green; **chưa** mở project AIdle.

**Checklist Human (khuyến nghị):**

1. Backup / snapshot disk (optional nhưng nên có trước editor lạ).  
2. Node.js **18+** trên PATH (`node --version`).  
3. Chạy installer **hoặc** `npx -y summer-engine@latest install` (không cả hai mù quáng — chọn một path; local Setup.exe đã có sẵn).  
4. `npx -y summer-engine@latest login` (browser; token `~/.summer/auth-token` — **không** commit token).  
5. `npx -y summer-engine@latest doctor --json` → `ok` cho `engine-install`, `login`, `node-version`.  
6. **Không** `setup` agent MCP vào production game repo cho đến S2 allowlist.  
7. Agent ghi receipt: install path, version string, doctor JSON hash (sau khi Human báo xong).

**Hard stop:** Agent không chạy Setup.exe / `summer install` / `summer login` khi chưa có HITL token.

### Phase S2 — Dual-editor pilot (read-only first)

**Mục tiêu:** Chứng minh Summer **mở** được `E:\AIdle_openworld\game` mà không phá.

| Step | Action | Pass criteria |
|------|--------|---------------|
| S2.1 | Close stock Godot if open; open project once in Summer | Project loads; no forced resave storm |
| S2.2 | `summer_get_project_context` / scene tree read | Tree shows main + cast galleries |
| S2.3 | `summer_screenshot` viewport or scene | PNG saved under `orchestration/evidence/summer_s2/` (WO) |
| S2.4 | Diff git / file mtimes on `game/` | **Zero unintended writes** or only `.godot` cache documented |
| S2.5 | Re-open in stock Godot 4.3 + run known smoke | `AIDLE_MOCKUP_CAST_PROPS_PRODUCTION` still PASS |

**Fail → rollback:** discard Summer-side changes; keep stock Godot path only.

**Parallel:** Optional install Godot-MCP (AI-GDT) vs Summer MCP — pick **one** primary editor bridge per session to avoid tool thrash.

### Phase S3 — Accelerate commercial residual (lease-bound)

Chỉ sau S2 PASS. Work order examples:

| WO id (draft) | Scope | Summer use | Authority |
|---------------|-------|------------|-----------|
| WO-SUMMER-EVIDENCE-001 | Headed Gate9 / visual proof | play + screenshot + debugger | VERIFY_ONLY |
| WO-SUMMER-UI-CTRL-001 | Named Control 1B files only | inspect + patch + re-verify | PATCH_DRAFT |
| WO-SUMMER-OUTLINE-VIS-001 | Outline mat on gallery meshes | screenshot before/after | PATCH named mats/scenes |
| WO-SUMMER-DEBUG-001 | Crash/null from Human playtest | debug skill ladder | READ then PATCH |

**Done when:** residual commercial checklist items have **machine smoke + Summer evidence pack** where headed was blocking.

### Phase S4 — Asset gen pilot (optional, paid HITL)

Align AI-GDT pipeline S0–S9:

1. Human approves job + budget (Summer Studio credits).  
2. `summer_generate_3d` **or** AI-GDT Meshy/Tripo — **one** tool per job.  
3. Output → `AIdle_Blender_Bridge_P0/storage/generated_quarantine/<JOB_ID>/`.  
4. `validate_ai_gdt_intake.py` (glTF, size, hash).  
5. Style lock `#fdf3e2` / cozy low-poly remesh if needed (Blender).  
6. Promote via WO named `game/assets/...` only.  
7. Bind catalog (`module_catalog` / roster) + smoke.

**Never:** generate straight into `game/assets` from MCP.

### Phase S5 — Steady-state operating model

| Role | Tool of record |
|------|----------------|
| Authority runtime + CI smokes | Stock Godot 4.3 headless |
| Cast/prop mesh production | Blender batch + P1E |
| Agent editor inspect / headed evidence | Summer MCP **or** Godot-MCP (Human picks primary) |
| Text/Image→3D | AI-GDT catalog + optional Summer generate (HITL) |
| Orchestration / accept / Red | MAF + Human batch only |

---

## 6. Install playbook (AIdle-adapted — **do not auto-run**)

Upstream agent playbook: SummerEngine/summer-engine-agent README.  
**AIdle deltas** (bắt buộc):

| Upstream default | AIdle rule |
|------------------|------------|
| “Install and scaffold a game” | **Forbidden** scaffold; open existing `game/` only after S2 |
| `summer create 3d-basic` | **Do not** inside `AIdle_openworld` tree |
| Auto `setup <agent> --yes` | Only after Human; prefer **project-scope** MCP config outside game assets |
| Jump to build skills | Always load vision lock + exact WO first |
| `summer_generate_*` freely | HITL + quarantine only |
| Brainstorm GameSoul as product truth | Optional sidecar; never overrides vision lock |

**Suggested command sequence (Human or agent after HITL):**

```text
# 0) Preflight
node --version
# optional if using npm path:
npx -y summer-engine@latest doctor --json

# 1) Engine: either local Setup.exe (already on E:\) OR
# npx -y summer-engine@latest install

# 2) Auth (browser)
# npx -y summer-engine@latest login

# 3) Doctor again
# npx -y summer-engine@latest doctor --json

# 4) MCP for agent — AFTER Human chooses harness (codex/cursor/claude-code)
# npx -y summer-engine@latest setup <agent> --yes
# Prefer documenting config path; avoid polluting game/ with unrelated plugin files without WO

# 5) Open existing project (NOT create)
# npx -y summer-engine@latest run "E:\AIdle_openworld\game"
# wait until local-api ok (localhost:6550)
```

**Port / process hygiene:**

- Summer local API: **6550** (document; conflict check before start).  
- Only one of: Summer editor / stock Godot editor writing project at a time.  
- Kill play session (`summer_stop`) before scene structural edits.

---

## 7. Do / Don’t (quick card)

### DO

- Use Summer for **verify loop**: script errors → screenshot → play → debugger.  
- Export evidence to **leased** evidence paths.  
- Keep Blender + stock Godot as production mesh/smoke.  
- Map every edit to WO + receipt.  
- Treat generate/import as **AI-GDT quarantine class**.  
- Re-run stock smokes after any Summer-side file touch.

### DON’T

- Don’t run installer without Human.  
- Don’t `summer create` inside AIdle.  
- Don’t let Summer skills override MAF / vision lock / Architecture Lock.  
- Don’t World Commit / Persist mutate from MCP.  
- Don’t put auth tokens or API keys in repo.  
- Don’t claim commercial gate PASS from Summer alone without stock smoke.  
- Don’t enable free-agent paid cloud gen (Red F01 / cost / network).  
- Don’t dual-write scenes with two editors open.

---

## 8. Metrics (có / không tăng tốc)

Đo sau 1 tuần pilot S2–S3 (Human + agent log):

| Metric | Baseline (hiện tại) | Target with Summer |
|--------|---------------------|--------------------|
| Time to headed screenshot evidence | Manual editor | ≤ 15 min agent-driven pack |
| Time from playtest bug → repro log | Ad-hoc | Debugger errors + screenshot same session |
| UI polish cycle (edit→see→fix) | CLI smoke only | + live viewport verify |
| Unintended `game/**` writes per session | 0 goal | **0** (hard) |
| Stock mockup/commercial smokes still PASS | PASS | PASS after every Summer edit session |
| Paid gen jobs without HITL | 0 | **0** |
| Cast production throughput | Blender batch | Unchanged primary; Summer gen optional extra shells only |

**Kill criteria (dừng Summer path):**

- Project corruption or forced format migration.  
- >0 silent World/Persist mutations.  
- Stock 4.3 smoke FAIL after Summer open without clear revert.  
- License/auth friction blocking more hours than it saves.

---

## 9. Risk register

| ID | Risk | Mitigation |
|----|------|------------|
| R1 | Godot version / resource format drift | S2 open-only pilot; stock smoke always |
| R2 | Agent over-build via skills | WO lease; ban create/brainstorm-as-truth |
| R3 | Dual editor conflict | Single writer lock; close other editor |
| R4 | Paid API spend / network | HITL for all `summer_generate_*` / URL import |
| R5 | Secret leakage (`~/.summer/auth-token`) | Never copy into repo; gitignore audit |
| R6 | Tool overlap Godot-MCP vs Summer | Pick one primary MCP per phase |
| R7 | Closed engine binary trust | Authenticode Valid; pin version 0.5.54; no silent update |
| R8 | `.summer/` memory drift vs vision lock | Vision lock always wins; treat GameSoul as non-canon |

---

## 10. Relation to AI-GDT package

| AI-GDT item | Summer action |
|-------------|---------------|
| `tool_catalog.json` | Add entry `summer_engine` (support_install_opt_in) — see §12 |
| `godot_mcp_aidle_bridge.md` | Peer document; Summer is **alternative/complement** editor bridge |
| `module_pipeline_v2.yaml` | S4 gen jobs feed same S0–S9 quarantine steps |
| `validate_ai_gdt_intake.py` | Required after any Summer GLB land |
| Godot-MCP priority | If Summer S2 proves screenshot/play superior, demote Godot-MCP to fallback; else keep Godot-MCP for stock 4.3 fidelity |

---

## 11. Decision matrix for Human

| Option | When to choose |
|--------|----------------|
| **A. Install + S2 pilot** (recommended if time available) | Want faster headed evidence + UI polish this commercial wave |
| **B. Defer install** | Focus pure content/cast; CLI smokes enough |
| **C. Install engine only, no MCP** | Human uses Summer UI manually; agents stay CLI |
| **D. Prefer Godot-MCP only** | Stay on stock 4.3 binary exclusively for agent control |

Reply tokens (examples):

- `INSTALL_SUMMER_HITL_001` → agent may assist S1 commands after Human runs Setup  
- `SUMMER_S2_OPEN_GAME` → authorize open `game/` read-only pilot  
- `DEFER_SUMMER` → park plan; continue AI-GDT/stock only  

---

## 12. Catalog stub (for tool_catalog merge)

```json
{
  "id": "summer_engine",
  "name": "Summer Engine 0.5.54",
  "url": "https://summerengine.com",
  "agent_layer": "https://github.com/SummerEngine/summer-engine-agent",
  "installer_local": "E:\\SummerEngine-0.5.54-Setup.exe",
  "engine": "Godot-compatible fork (verify vs AIdle 4.3 pin)",
  "aidle_jobs": [
    "editor_inspect",
    "headed_capture",
    "run_play_verify",
    "ui_polish_under_lease",
    "optional_paid_generate_quarantine"
  ],
  "tier": "support_install_opt_in",
  "network": "paid_generate_hitl_only",
  "notes": "Sidecar only; not World Commit; not cast path of record; plan SUMMER_ENGINE_USAGE_PLAN_001.md"
}
```

---

## 13. Immediate next actions (agent after this doc)

1. Journal Entry 077 (plan published).  
2. Optionally merge `summer_engine` into `ai_gdt/tool_catalog.json` (documentation only).  
3. **Wait** for Human install decision.  
4. Continue commercial residual / cast polish on stock path until HITL.

---

## 14. Document control

| Field | Value |
|-------|--------|
| Doc id | `SUMMER_ENGINE_USAGE_PLAN_001` |
| Author | Grok (parent 019f7ffd…) |
| Date | 2026-07-23 |
| `accepted` | false |
| `self_accept` | false |
| Install executed | **no** |

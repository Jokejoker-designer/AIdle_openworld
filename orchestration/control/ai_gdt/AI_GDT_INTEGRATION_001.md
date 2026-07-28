# AI Game DevTools → AIdle Openworld integration 001

Source hub: [Yuan-ManX/ai-game-devtools](https://github.com/Yuan-ManX/ai-game-devtools) (AI-GDT)  
Status: **ACTIVE support layer** · Directive 99 · Parent `019f7ffd-3995-71c0-aca1-51078e24a852`  
`accepted=false` · does **not** enable Red F01 network/ship · Text-to-3D stays **quarantine + HITL**

## 1. Purpose

Use AI-GDT as the **curated toolbox index** for expanding AIdle’s module / cast / animation
pipeline — especially:

| AI-GDT focus | AIdle binding |
|--------------|---------------|
| **Godot-MCP** (+ GameDev-MCP-Server) | Agent ↔ Godot Editor/runtime tools (inspect, run, scene ops) |
| **3D Model** (Meshy, Hunyuan3D, TripoSR, Shap-E, CSM, Luma…) | Offline **AssetRequest → generate → quarantine → QA → promote** |
| **Avatar** (Ready Player Me, Rodin, MotionGPT…) | Companion / NPC visual research (MVP Companion remains **text-only**) |
| **Animation** (MotionGPT, HY-Motion, Omni Animation, Stable Animation…) | Clip authoring beyond hand-key Blender for cast GLBs |
| **Agent frameworks** (MetaGPT, ChatDev, Auto-GPT, LangChain…) | Align with MAF + TrustLayer x16 (do not replace) |
| **Game / World Model** (HunyuanWorld, Cosmos…) | Research only — not runtime world truth |

## 2. Hard boundaries (unchanged AIdle law)

1. **World Commit** is the only durable mutator — AI never writes canonical inventory/economy.
2. Generated 3D is **untrusted** until QA + signed promotion (same as Blender Bridge P0).
3. **No credentials** in Godot client / bridge files / logs / saves.
4. **Godot-MCP** may edit editor state only under exact lease; never silent World Commit.
5. Unrestricted Text-to-3D / neural portals remain **TIER3 product execution** until a dedicated
   directive opens them; this integration **stages** the intake path only.
6. TTS / voice avatar lipsync tools are **post-alpha** (vision lock).

## 3. Layer map

```
┌─────────────────────────────────────────────────────────────┐
│  Grok / MAF agents (parent 019f7ffd…) + TrustLayer x16     │
├─────────────────────────────────────────────────────────────┤
│  AI-GDT catalog (this folder)  → tool pick by job type      │
├──────────────┬──────────────────┬───────────────────────────┤
│ Godot-MCP    │ Text/Image→3D    │ Animation / Avatar tools  │
│ editor ops   │ AssetRequest gen │ motion / retarget clips   │
├──────────────┴──────────────────┴───────────────────────────┤
│  Quarantine: AIdle_Blender_Bridge_P0/storage/generated_…    │
│  Validate: glTF parse · bone policy · hash · style lock     │
│  Promote: named game/** lease only (WO + receipt)           │
├─────────────────────────────────────────────────────────────┤
│  Runtime: cast_presenter · p1e_module_kit · glb_intake     │
│           nori7 / cast roster · Block Assembly · Persist    │
└─────────────────────────────────────────────────────────────┘
```

## 4. Expanded module creation pipeline (vNext of cast/props)

### 4.1 Module types

| Type | Example | Author path |
|------|---------|-------------|
| **Prop module** | `cozy_house_small_A` | P1E library / Meshy·Hunyuan3D image-to-3D → quarantine |
| **Character cast** | Foundry IDs | Blender batch / Avatar tool → retarget to skel family → clips |
| **Block kit piece** | UCBV architecture | DNA recipe + offline mesh · not free LLM mesh |
| **VFX / outline** | silhouette shader | Shader section tools + Godot-MCP apply |

### 4.2 Steps (machine-enforceable)

1. **Spec** — Foundry `character_spec` or prop `module_id` + style lock `#fdf3e2`.
2. **Tool select** — `tool_catalog.json` → `aidle_job` mapping.
3. **Generate offline** — never write `game/**` directly from generator.
4. **Land quarantine** — `generated_quarantine/<JOB_ID>/`.
5. **Validate** — `validate_ai_gdt_intake.py` (glTF, optional bones, size, hash).
6. **Red findings** — style / authority / scope.
7. **Promote** — WO names exact `game/**` paths; one writer; receipt.
8. **Runtime bind** — roster / module_catalog / presenter.

## 5. Godot-MCP (priority integration)

Upstream: [IvanMurzak/Godot-MCP](https://github.com/IvanMurzak/Godot-MCP)  
Shared: [GameDev-MCP-Server](https://github.com/IvanMurzak/GameDev-MCP-Server)

### AIdle use cases

- Headed capture / scene tree inspect for commercial evidence
- Run `-s` smokes via agent without inventing logs
- Apply outline materials / place cast gallery under lease

### Install stance

- Documented in `godot_mcp_aidle_bridge.md`
- **Opt-in** by Human (C# addon + local MCP server)
- Default: adapters call **Godot CLI** (already used) if MCP not installed

### Peer: Summer Engine (sidecar)

- Plan: `../SUMMER_ENGINE_USAGE_PLAN_001.md`
- Catalog id: `summer_engine` (52 MCP tools, screenshot/play/debug ladder)
- Same allowlist spirit as Godot-MCP; **not** auto-installed; stock Godot 4.3 remains smoke authority
- Prefer **one** primary editor MCP per session (Summer *or* Godot-MCP) to avoid dual-writer thrash

## 6. Text-to-3D / Image-to-3D (module expansion)

Preferred open / API tools from AI-GDT for AIdle props/cast shells:

| Tool | Role in AIdle |
|------|----------------|
| **Meshy** | Game-ready textured mesh from image/text (HITL API) |
| **Hunyuan3D 2.x** | High-res textured 3D (offline research / HITL) |
| **TripoSR** | Fast single-image → mesh (local/open) |
| **Shap-E** | Text/image → 3D (open research) |
| **CSM** | Image/video → 3D world pieces (HITL) |
| **Luma AI** | Photoreal capture — style filter before promote |

All outputs enter **quarantine**, then style remesh/simplify toward cozy low-poly if needed
(existing Blender factory), then promote.

## 7. Animation tools

| Tool | AIdle role |
|------|------------|
| **MotionGPT / HY-Motion 1.0** | Text → motion curves → retarget to cast skeleton |
| **Omni Animation / Stable Animation** | Clip generation research |
| **Blender offline** (current) | Production path of record for keyed clips |

Clips must land as **real fcurves/keys** in GLB (never name-only metadata).

## 8. Agent frameworks vs MAF

AI-GDT lists MetaGPT, ChatDev, Auto-GPT, LangChain, etc.

**AIdle keeps MAF + TrustLayer x16 + parent-only spawn** as the operating system.
External agent frameworks may inform design patterns only — they do **not** replace
`agent_step_contract`, exact leases, or Human batch accept.

## 9. Files in this package

| Path | Role |
|------|------|
| `tool_catalog.json` | Curated AI-GDT entries + AIdle job mapping |
| `module_pipeline_v2.yaml` | Expanded module pipeline machine steps |
| `godot_mcp_aidle_bridge.md` | Godot-MCP install & allowlist |
| `adapters/validate_ai_gdt_intake.py` | Quarantine intake validator |
| `adapters/submit_asset_request_stub.py` | AssetRequest → quarantine job stub |
| `AI_GDT_INTEGRATION_001.md` | This document |

## 10. Next execution (after Human continues)

1. Optional: install Godot-MCP against Godot 4.3 project (HITL).
2. Pilot **one** prop via Image→3D (TripoSR/Meshy) → quarantine → promote.
3. Pilot **one** cast clip pack via MotionGPT/HY-Motion retarget onto cast skeleton.
4. Fold results into `cast_roster` / `p1e_cozy` catalogs.

# Current System Alignment and Governance — v1.1

Updated: 2026-07-21 · Owner: Human Product Lead

## 1. Truth hierarchy

Khi có xung đột, thứ tự authority là:

1. `E:/AIdle_openworld/AGENTS.md`
2. `E:/AIdle_openworld/orchestration/ARCHITECTURE_LOCK.md`
3. current monotonic directive/work order on disk
4. contracts and executable evidence
5. this Blueprint
6. reference DOCX/ZIP files

Reference material is design input, not executable proof.

## 2. Runtime and tool pins

| Component | Current lock |
|---|---|
| Godot | 4.3-stable, 2.5D fixed camera |
| Blender | `E:/blender.exe`, 5.2.0 LTS |
| Character Bridge | `E:/AIdle_Blender_Bridge_P0` |
| Bridge listener | loopback only; no public bind |
| Companion | text-only |
| Canonical mutation | World Commit only |

## 3. Current implementation truth

| Capability | State | Meaning |
|---|---|---|
| B0 Character Bridge machine gate | ACCEPTED | Existing bridge, 11 tests, compile and a server-mediated real Blender quarantine probe passed |
| P0E Environment Bridge | READY / NOT IMPLEMENTED | This package defines the next bounded extension |
| P1E Cozy Starter Realm | BLOCKED | Requires P0E verification and the Human G8 decision |
| Approved Environment Catalog | NOT AUTHORIZED | Quarantine outputs cannot promote themselves |
| Godot Scene intake | BLOCKED | No Blueprint or Blender worker may patch runtime scenes during P0E |

## 4. Non-negotiable boundaries

- Environment and character jobs share the Bridge-wide single-worker lease
  (`max_active_jobs = 1`). A client cannot raise or reset it.
- Client payloads never contain output paths, Python, shell, URLs, add-ons or
  arbitrary Blender operators.
- A valid client request is converted server-side into an internal spec. Only
  the server selects the absolute quarantine directory.
- Idempotency binds a canonical validated request fingerprint. Reuse of the
  same key with a changed payload fails closed.
- Blender returns meshes, transforms, registry IDs, hints, previews and
  provenance. Godot owns interaction, collision, navigation, persistence,
  manifestation and World Commit.
- Content assembly phase (`TERRAIN`, `PATH`, `SHELTER`, `NATURE`,
  `INTERACTIVE`, `LIGHTING`, `LANDMARK`) is metadata. It is not the runtime
  manifestation state (`wireframe`, `hologram`, `materializing`, `complete`).
- A direct Blender CLI artifact is not lifecycle proof. Acceptance requires a
  server-mediated job receipt, validation report, hashes and quarantine state.

## 5. Security truth versus target hardening

Currently evidenced: strict request models, allowlisted templates/operations,
server-owned output path, `--factory-startup`, `--disable-autoexec`, timeout,
loopback service and generated quarantine.

Target hardening, **not yet claimed as implemented**: separate OS account,
enforced OS/container egress denial, resource quotas beyond current P0 limits,
signed registry/catalog promotion and production-grade durable queueing.

## 6. MAF and TrustLayer operating model

- Parent: same Grok Desktop parent, coordinator-only.
- Agent step: named installed profile + tools + state + middleware + authority.
- Session/state: directive, work order, status, journal, trace and receipt files.
- Workflow: scoped waves with max five children and no grandchildren.
- Observability: transcript refs, commands/exits, hashes and schema-valid
  `agent_step_contract` receipts.
- HITL: Human Product Lead accepts high-risk or final product gates.
- Red finds only. Blue patches only its lease. Purple verifies and never patches.
- One writer owns each file. No worker accepts its own output.

## 7. Delivery gates

```text
P0E schema/registry plan
  -> Bridge implementation in E:/AIdle_Blender_Bridge_P0
  -> character regression + environment negative tests
  -> server-mediated Blender probe
  -> Red findings
  -> independent QA/Purple
  -> Human/Codex acceptance
  -> P1E remains blocked until G8 Human decision
```

No step in this Blueprint authorizes install, credential use, public network,
push, deploy, publish, approved catalog write or canonical world mutation.

# Grok autonomous operating envelope — ENV0

Status: `ACTIVE` · Authorized by: Human Product Lead · 2026-07-21

## Purpose

Continue the bounded Environment Bridge P0E implementation in the one existing
Grok Desktop parent `019f7ffd-3995-71c0-aca1-51078e24a852` when Codex usage is
limited. This is a MAF workflow handoff, not a transfer of product acceptance or
canonical world authority.

## Permitted autonomy

The parent may coordinate ENV0-001, iterate corrections inside the work order,
spawn the five installed profiles named there, collect evidence, and return
`REVIEW_REQUESTED`, `CHANGES_REQUESTED`, `NEED_HUMAN` or `WAITING_HUMAN`.

The parent may update `grok_status.json`, ENV0 receipts/logs/traces and create
correction work orders scoped to ENV0-001. It may not edit
`codex_directive.json`, historical acceptance evidence or mark a task ACCEPTED.

## Mandatory MAF workflow

1. Load COMPLIANCE, TrustLayer registry, plan, journal, Architecture Lock,
   Blueprint v1.1, work order, skills manifest and character/UI registries.
2. Verify same unique Desktop parent, state and file leases.
3. Run schema VERIFY_ONLY before Blue implementation.
4. Run the single Blue product writer.
5. Run Red findings-only, then QA evidence, then Purple verification.
6. Emit transcript-backed, schema-valid agent step receipts.
7. Route final acceptance to Human Product Lead if Codex is unavailable.

## Hard stops

- G8 stays `HITL_REQUIRED`; P1E Cozy, Scene runtime, Control 1B and Character
  Foundry 1C stay blocked.
- No new top-level session, Grok CLI, grandchildren or support profile.
- No Godot/Scene/Character/Control patch, approved catalog write or World Commit.
- No dependency install, credential, live provider, public network, push,
  deploy or publish.
- Stop on writer conflict, authority drift, non-unique parent or three identical
  failure signatures.

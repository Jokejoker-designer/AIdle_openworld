# AIdle stack and AI Credit triage

Date: 2026-07-21  
Owner: Codex / architecture review  
Authority: `REPORT_ONLY` for roadmap decisions; no dependency installation

## Decision

The two submitted proposals are directionally compatible with AIdle, but they
do not authorize an immediate stack migration or dependency install. The
existing Architecture Lock remains authoritative: Godot 4.3, a 2.5D
text-only alpha, Free Desktop Bridge without API, and Paid API only through a
trusted provider-neutral gateway.

## Already covered; do not duplicate

- Godot client and 2.5D Private Reality vertical slice.
- Provider-neutral Paid gateway fixture with validation, redaction, bounded
  budget, retry and idempotency controls.
- Local signed persistence journal and deterministic two-client authority POC.
- Shared AGM Snapshot and Decision Envelope across Free and Paid editions.
- Preview, explicit confirmation and World Commit boundaries.

## Useful later, but only behind a compatibility POC or ADR

- Blender and Material Maker: offline art-production tools, not runtime
  dependencies.
- LimboAI, Dialogic and Godot SQLite: evaluate after G8 with Godot 4.3
  compatibility, maintenance and overlap checks. They must not replace the
  existing AGM contract, consent flow or signed persistence without an ADR.
- FastAPI, Pydantic, PostgreSQL and pgvector: preferred production-backend
  candidates after the local vertical slice and Human alpha gate. Current
  dependency-light fixtures remain the executable truth until then.
- Valkey, LiteLLM, Nakama, NATS, SeaweedFS and OpenTelemetry: conditional scale
  components. Add only when a measured bottleneck or selected multiplayer
  backend requires them.
- Ollama, llama.cpp, vLLM, TripoSR, TRELLIS and ComfyUI: R&D/post-alpha lanes;
  generated meshes and model output remain untrusted artifacts.

The submitted Godot 4.7.1 recommendation does not override the locked local
Godot 4.3 toolchain. An engine upgrade requires a separate compatibility ADR
and full regression evidence.

## Central API and AIdle Credits

The proposed central API model fits only the `api_paid` edition:

`player session -> trusted AIdle gateway -> provider project/service key`

Provider credentials never enter Godot or a player device. The Free Desktop
Bridge remains no-API. A future paid service should use server-side hard caps,
idempotency, reserve-before-call accounting, final charge/release, an immutable
usage ledger, per-player/per-feature/global limits and an emergency kill
switch.

This is a post-alpha commercial/economy milestone, not current G8 scope. Before
implementation it needs:

1. an ADR for identity, wallet, reservation, reconciliation and refund rules;
2. measured provider costs and feature-specific maximum-cost envelopes;
3. fraud/race-condition tests and server-authoritative ledger semantics;
4. privacy, retention, tax/payment and regional policy review;
5. Human approval for plans, prices, purchasable credits and live credentials.

No hard-coded credit price, plan allowance or provider model is accepted from
the proposal as product truth.

## Immediate route

Finish G8 with a fresh D3 Purple gate. Keep Control 1B and Character Foundry
Scene 1C queued. After Human alpha acceptance, open a bounded architecture
spike for the next component that solves a demonstrated gap; do not install the
entire recommended stack at once.

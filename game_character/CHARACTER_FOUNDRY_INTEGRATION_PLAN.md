# AIdle Character Foundry — Integration Plan

Status: `QUEUED_AFTER_G8_D2_AND_D3`  
Owner: Human Product Lead  
Machine acceptor: Codex  
Updated: `2026-07-21T11:25:38+07:00`

## Source lock

- Package: `game_character/AIdle_Character_Foundry_MD`
- Manifest version: `1.0`
- Manifest SHA-256: `BDBA6B53174E1D6671F28302B4AE67275AD22BF3C2E978603791ACD19E6CC4BA`
- Inventory: 28 character specifications across 7 World Profiles.
- The Markdown pack is design input. It is not executable runtime authority.

## Two character layers must remain separate

1. **Agent characters** are TrustLayer/UI personas used by Codex and Grok to perform project work. Their authority comes from `E:/agents/characters/registry.yaml`, the UI registry, a work order and an authority token.
2. **Game characters** are player-facing Companion/NPC/creature definitions from this Foundry. They have gameplay allowlists and limitations, but no project-tool authority and no direct World Commit capability.

No Foundry character may be used as a substitute for a TrustLayer worker, reviewer or final acceptor.

## Runtime boundary

```text
Foundry Markdown
  -> intake + provenance check
  -> versioned CharacterSpec validation
  -> Character Registry candidate
  -> in-world preview / spawn proposal
  -> explicit confirmation when state or ownership changes
  -> existing executor + World Commit
  -> persistence / authority receipt
```

- Dialogue, mood, quest and build suggestions travel through the existing AGM Snapshot and Decision Envelope.
- Animation events emit signals only. They never mutate inventory, ownership, economy, collision or canonical world state.
- Behavior outside `behavior_allowlist` fails closed.
- Refusal/cancel behavior remains visible and testable.
- Generated art, mesh or animation is an untrusted artifact until style, provenance, rig, collision and gameplay QA pass.

## Ordered deployment with Scene 1 → 7

| Scene | World Profile | Foundry characters | Planned use |
|---:|---|---|---|
| 1 | Cozy Cyber-Pixel / Dreamy Low-Poly | Nori-7, Mây Mạch, Bác Bắp, Bụi Mơ | First executable character slice in the Starter Realm. |
| 2 | Tiny Diorama World | Pip Đất Sét, Tock Đường Ray, Miette Chim Giấy, Patch Gấu Nút | Grid/recipe/tutorial cast after Scene 1 is accepted. |
| 3 | Solarpunk Haven | Luma Tán Lá, Sora Giữ Sương, Kito Thụ Phấn, Mầm Tám | Ecology and restoration roles. |
| 4 | Arcane Clockwork | Brassel Thợ Rune, Oria Chuông Trời, Cinder-04, Quillix | Physical/magic layer and mechanism roles. |
| 5 | Spirit Valley | Vân Hồ, Đăng Tâm, Trúc Nhi, Mộc Ông | Spirit relationship and recovery roles. |
| 6 | Surrealism Canvas | Kẻ Giữ Khung, Lụa Ngược, Ông Nhỏ Lớn, Gấp Bóng | Bounded anomaly and surreal-rule roles. |
| 7 | Oceanpunk / Bioluminescent Abyss | Nereu-5, Lumi Ray, Coralyn, Bronti Vỏ Thành | Depth, sonar and underwater navigation roles. |

The deployment order follows `Scene/SCENE_IMPLEMENTATION_TRACKER.md`, not the folder numbering inside the Foundry package.

## Scene 1C — Cozy Character Foundation

This is queued work and is not part of active Directive 33.

| Character | Initial role | MVP authority boundary |
|---|---|---|
| Nori-7 (`CCP-RH-001`) | Farming helper and tool guide | May propose watering/collection tasks; cannot consume resources or change planting schedules without confirmation. |
| Mây Mạch (`CCP-NS-002`) | Social courier and quest connector | May introduce NPCs and propose community quests; cannot open private mail or transfer owned items directly. |
| Bác Bắp (`CCP-NW-003`) | Repair/crafting mentor | May diagnose and propose repair/upgrade recipes; cannot apply unsafe or unconfirmed upgrades. |
| Bụi Mơ (`CCP-CT-004`) | Tameable ambient companion | May reveal small unowned finds and express attachment; cannot take owned items or silently alter yield. |

Nori-7 does not automatically replace the existing AIda/AI Companion identity. A replacement, merge or dual-companion decision requires a separate Human Product Lead decision and an architecture note.

## Required implementation waves

1. **Schema intake** — convert the Markdown schema into a versioned machine contract and validate all 28 records without changing their source text.
2. **Registry adapter** — stable IDs, world mapping, version/provenance, duplicate and copyright-review fields.
3. **Cozy visual slice** — local Godot primitives or approved assets for the four Scene 1 characters; fixed-camera silhouette and rear-readability checks.
4. **Behavior adapter** — text-only dialogue style, ability/limitation and allowlist/denylist mapped to AGM actions.
5. **Manifestation integration** — object-level wireframe → hologram → materializing → complete preview; cancel leaves no entity/collision.
6. **Executor and persistence** — explicit confirmation, idempotency, revision check, receipt, save/reload and compensation.
7. **Purple + human gate** — adversarial authority review, headed screenshots at both target resolutions and Human Product Lead acceptance.

Every wave requires real installed subagents selected by the work order, exact skill and character binding, one writer per file, schema-valid step receipts and independent Codex acceptance. Purple reviewers never patch.

## Acceptance gates

- All 28 source files match the manifest and retain provenance.
- Every character has a useful gameplay role, one ability and one meaningful limitation.
- Silhouette remains readable in the fixed 2.5D/isometric camera, including one rear-view identifier.
- A new character changes at least five design dimensions; palette-only variants remain skins.
- No unrestricted AI agency, direct commit tool, hidden purchase pressure or consent manipulation.
- Text-only MVP remains intact; voice/TTS is deferred.
- No generated scripts, shaders, provider calls, credentials, public network or dependency installation.
- Scene 2 remains blocked until Scene 1A, 1B and this queued 1C gate are explicitly accepted or the Human Product Lead changes the phase gate.

## Immediate coordination rule

Directive 33 D2 children keep their current leases unchanged. Do not inject this scope into running D2 children and do not modify their receipts. After Codex accepts D2, complete D3 Purple review first; then issue a separate Character Foundry work order for Scene 1C.

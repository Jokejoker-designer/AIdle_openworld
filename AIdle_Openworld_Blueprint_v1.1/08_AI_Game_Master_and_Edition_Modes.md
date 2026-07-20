# AI Game Master and Edition Modes

## Product role

The AI Game Master (AGM) is the director, quest writer, high-level Companion
brain and pacing controller. Godot is the stage: it renders the 2.5D world,
collects player actions, exports bounded state, validates AGM decisions and
executes allowed effects.

The AGM may propose Companion dialogue, bounded mood/relationship deltas,
quest operations, allowlisted world events, build proposals expressed as
Structured World Prompts, pacing hints and the next decision trigger.

The AGM cannot directly mutate the scene tree, persistence, collision,
inventory, ownership, currency or marketplace state. Every response is
untrusted input until schema, policy, budget, consent and authority checks pass.

## Shared loop

1. Godot emits a versioned `WorldStateSnapshot` with minimal necessary state.
2. The selected edition transports it to an AI Desktop or API gateway.
3. The AGM returns one versioned `AGMDecisionEnvelope` JSON object.
4. Godot rejects unknown fields, stale snapshot IDs, replayed decision IDs,
   unsupported actions, excessive deltas and raw executable content.
5. Dialogue and quest UI may update after validation. Durable builds still
   require Structured World Prompt preview, confirmation and World Commit.
6. Godot records an execution receipt for the next snapshot.

## Free edition — Desktop Bridge

Edition ID: `desktop_bridge_free`.

- **Send to AI** copies a redacted snapshot and AGM instruction to clipboard.
  The player pastes it into Grok Desktop or ChatGPT Desktop.
- **Receive from AI** imports the copied JSON response into Godot.
- File mode writes the outbound bridge JSON; the response is placed in the
  inbound bridge JSON and imported after visible player confirmation. Exact
  paths are locked by the G1-003 machine contract.
- No provider API, hidden UI automation, cookie extraction or desktop session
  scraping is permitted.
- Without a valid response, the Starter Realm remains playable while
  AI-directed progression waits visibly; Godot does not invent an AGM answer.

## Paid edition — API Gateway

Edition ID: `api_paid`.

- Godot sends the same snapshot contract to a trusted AIdle gateway.
- The gateway owns provider selection, authentication, rate limits, retries,
  moderation, cost budgets, schema-constrained generation and observability.
- Provider credentials never ship in the game client.
- Failure becomes an explicit retry/offline state, never silent durable mutation.
- Provider, payment and production credentials require Human approval.

## Starter Realm

Both editions begin with the same deterministic Starter Realm: small house,
farm plot, path, lights and AIda. The first snapshot asks the AGM for an
onboarding quest chain. The realm itself never depends on an AI response.

## Privacy and memory

Snapshots contain bounded recent conversation and summaries, not unrestricted
history. Users can inspect, redact and delete exported memory. Secrets,
credentials, raw system prompts and unrelated local files are prohibited.

## Single-contract invariant

Free and Paid are transports, not separate game designs. They cannot fork quest
semantics, authority, mutation rules or save formats. A recorded Decision
Envelope must replay through the same deterministic executor in both editions.

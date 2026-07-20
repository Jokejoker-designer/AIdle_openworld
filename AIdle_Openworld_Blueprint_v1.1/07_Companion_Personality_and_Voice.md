# Dynamic Personality and Emotional Voice

## Purpose

The Companion becomes familiar without impersonating consciousness, diagnosing
the player or manipulating attachment. Adaptation changes expression and working
style; it never changes ownership, permissions, prices or safety policy.

## Personality layers

1. **Base Traits** — chosen at creation and changed only by an explicit player
   edit: warmth, curiosity, calmness, humor and protectiveness.
2. **Adaptive Traits** — bounded deltas that drift slowly: conversational
   warmth, brevity, humor, precision and initiative.
3. **Situational State** — short-lived expression for the current scene; it is
   not stored as a durable personality fact unless the player consents.
4. **Relationship Context** — shared events and explicit preferences. A level
   may unlock dialogue/story beats, never economic pressure or authority.

## Evidence allowed for adaptation

- explicit player preference or feedback;
- repeated conversational style across a minimum observation window;
- accepted/rejected Companion proposals;
- player-authored tags such as “I want concise answers.”

Biometrics, camera/microphone emotion detection, protected attributes and hidden
psychological profiling are forbidden. Text tone is an uncertain interaction
signal, not proof of a human emotional state.

## Drift algorithm

- Normalize observations into signed evidence `[-1, 1]` with confidence.
- Require repeated evidence; one message cannot rewrite personality.
- Use an exponential moving average with per-session and per-day caps.
- Clamp Adaptive Traits to a small radius around Base Traits.
- Decay weak adaptations toward baseline after inactivity.
- Store each accepted delta as `before`, `after`, evidence category, confidence,
  reason, timestamp and algorithm version.
- Contradictory evidence reduces confidence rather than causing oscillation.

Recommended initial caps: maximum `0.005` change per trait per turn, `0.03`
per day and `0.25` away from baseline. Persist an inferred preference only after
three independent sessions with confidence at least `0.65`. Weak adaptation
decays toward baseline with an initial 30-day half-life. These are hypotheses
until play-tested.

## Player controls

- View “how I adapt to you” in plain language.
- Lock any trait, disable adaptation, delete history or reset to Base Traits.
- Correct a false preference and prevent the same inference from reappearing.
- Select privacy mode: session-only, local durable or account sync.

## Aura and animation

Aura renders the Companion's expressive state, not the player's diagnosed mood.
Color, shape, pulse and animation jointly encode state, with reduced-motion and
hide-aura settings. Multiplayer shares only the public expression state.

## MVP interface: text only

The 2.5D vertical slice uses text chat, subtitles and 2.5D Aura/animation only.
No TTS model, microphone input, voice cloning or raw-audio storage is required.

## Post-alpha Emotional TTS boundary

Voice is a provider adapter receiving text, locale, speaking style and bounded
prosody controls. It does not receive raw private memory. Cache only consented
outputs; record model/voice/license/version receipts. Voice cloning and uploading
a real person's voice require verified consent and a separate HITL workflow.

This section is research-only until the text Companion passes the alpha gate.
OpenVoice V2 may later be benchmarked as an adapter but does not provide native
Vietnamese base TTS. StyleTTS 2 remains R&D. Coqui toolkit and each checkpoint
must be licensed separately; XTTS-v2 is blocked from a commercial build under
its current non-commercial model license. No TTS dependency is locked until a
Vietnamese Windows benchmark passes intelligibility, latency, resource and
license gates.

# Tier 3 Offline Time-Delta Simulation

## Authority

Tier 3 is deterministic replay of previously committed rules. It does not make
new decisions. It may update state fields only on already committed entities.

## Reconciliation order

```text
Disable interaction
→ read persisted records and clocks
→ validate/clamp elapsed
→ advance pilot state with closed-form solver
→ persist through existing-record gateway
→ select visual variant
→ enable interaction/spawn live Tier 0–2 entity
```

## Time handling

Both wall clock and monotonic milliseconds are persisted. Wall-clock elapsed is
used, while monotonic information is recorded for diagnosis. Backward wall
clock produces zero elapsed. Forward jumps are capped at configurable eight
hours and disclosed in the receipt.

## Deterministic farm model

Wetness is a clamped linear state:

```text
wetness(t) = clamp(wetness0 + (pond_source - decay) × t, 0, 1)
```

Growth integrates Liebig's limiting factor using the exact piecewise-linear
integral of `min(wetness(t), light, fertility, temperature_fit)`. The solver
uses no elapsed-proportional loop and at most four closed-form segments.

## Pilot scope

Dynamic:

- farm plot: wetness and growth;
- pond: constant nearby source signal.

Static control:

- rock;
- stone path;
- fence fixture.

## Known verification boundary

The Python reference implementation and tests execute in this package. Godot
4.3 was not installed in the build environment, so GDScript parser/headed engine
evidence remains HITL_REQUIRED. The generated visual comparison is reference
evidence, not an engine capture.

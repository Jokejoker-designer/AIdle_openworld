# AI Game Master contracts

Machine contracts live under `contracts/agm/`:

- World State Snapshot schema (planned by G1-003)
- AGM Decision Envelope schema (planned by G1-003)
- valid and adversarial invalid fixtures for both

Snapshot fields include schema version, snapshot ID, edition mode, latest
player action, bounded player/world/quest/Companion state, art style,
progression phase and the last execution receipt. Sensitive fields are forbidden.

Decision fields include schema version, decision ID, source snapshot ID,
dialogue, quest operations, build proposals, allowlisted event proposals,
bounded mood/relationship deltas, next trigger and trace metadata. Unknown
fields and arbitrary code or scripts are rejected.

Transport adapters may add delivery metadata outside the hashed payload but
cannot alter payload semantics.

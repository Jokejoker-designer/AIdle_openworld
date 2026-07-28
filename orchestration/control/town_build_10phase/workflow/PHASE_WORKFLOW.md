# Phase Workflow — MOCKUP_PARITY_100

## States

`READY → CLAIMED → IN_PROGRESS → REVIEW_REQUESTED → PARITY_100_VERIFIED → HUMAN_ACCEPT`

Error: `CHANGES_REQUESTED` → rework until parity 100.  
Three identical failure signatures → `NEED_HUMAN`.

## Hard stop (must not stop early)

Agents **must continue rework** while any parity check is false:

1. IDs match mockup  
2. Clips named exact + idle plays  
3. Building + 3 props load  
4. No cyan body  
5. Silhouette readable 2.5D  
6. Town no overlap  
7. District role intact  
8. Assets hashed  

“Looks fine” without evidence = protocol violation.

## Parallelism

Within a phase after parity target locked:

- Character anim ∥ Building module ∥ Prop set  
- Then layout verify → runtime integrate → Red → Purple  

## One writer

One writer lease per file. Red/Purple never patch product.

# AIdle Worktree Registry

Current decision: `BLOCKED_NOW_SAFE_AFTER_CLEAN_CHECKPOINT`.

## Why no worktree is created now

- Active branch: `codex/foundation-2_5d` at base `e15544734d0b408e7a099646af258a18bb3c97fc`.
- Directive 25 and its real-child transcript lineage are still in progress.
- The main tree contains many modified and untracked Directive 24/G8 files.
- A worktree created from current HEAD would omit that draft and create a stale,
  divergent evidence base.

No stash, reset, clean, checkout, branch, commit or worktree action is authorized
by this registry.

## Unlock conditions

1. Grok reaches `REVIEW_REQUESTED / WAITING_CODEX` with no active child.
2. Codex reviews D0-D3 receipts/transcripts and accepts or issues a new correction.
3. Dirty state is separated into intentional checkpoint commits; main tree is
   clean and its base SHA is immutable.
4. A new work order names the worktree, branch, base SHA, sole writer, exact file
   allowlist, tests and integration order.

## Reserved future worktrees

| Purpose | Path | Branch | Ownership |
|---|---|---|---|
| G8 core correction, only if newly authorized | `E:\worktrees\codex\aidle-g8-core-r004` | `codex/g8-001-r004-core` | Core-owned runner/HUD/main/art-style set |
| G8 executor correction, only if newly authorized | `E:\worktrees\codex\aidle-g8-executor-r004` | `codex/g8-001-r004-executor` | Headed demo flow and Starter Realm panel set |
| Governance/evidence | `E:\worktrees\codex\aidle-g8-governance-r004` | `codex/g8-001-r004-governance` | Markdown, receipts and merge ledger only |
| Control 1B core, after G8 acceptance | `E:\worktrees\codex\aidle-control-1b-core` | `codex/control-1b-core` | Input/context router allowlist |
| Control 1B UI, after G8 acceptance | `E:\worktrees\codex\aidle-control-1b-ui` | `codex/control-1b-ui` | Context HUD/action UI allowlist |
| Control 1B verification | `E:\worktrees\codex\aidle-control-1b-verification` | `codex/control-1b-verification` | Tests, receipts and reviews only |

## Required worktree manifest

Every future worktree must record: work order, parent session, agent/character,
authority, skill sources/modes, base commit, branch, path, writer lease, allowed
and forbidden files, context hash, created/released timestamps and merge verdict.
Overlapping writer leases or a changing base route to `HITL_REQUIRED`.

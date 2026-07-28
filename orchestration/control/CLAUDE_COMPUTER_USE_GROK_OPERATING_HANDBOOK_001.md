# Claude computer-use → Grok Build operating handbook 001

Source: handoff pasted by the Human Product Lead 2026-07-23, generated from the
Grok Build environment itself. Saved verbatim-in-substance as governance
reference. This does NOT mean computer-use access is active — see §0.

## 0. Current real status (do not skip this)

- Computer-use access to the Grok GUI window is **still NOT granted**.
  `request_access` has been tried with `"grok"`, `"Grok"`, `"Grok Desktop"`,
  `"xAI Grok"`, `"Grok AI"`, `"grok-windows-x86_64"` — none resolved to an
  installed/running app in this tool's resolver. Every attempt was silently
  short-circuited (no dialog was ever shown to the Human for these).
- This handoff's **Method B (headless CLI, `grok -p ...`)** and **Method C
  (ACP stdio/serve)** both require running a process ON THE HUMAN'S ACTUAL
  WINDOWS MACHINE. Claude's `mcp__workspace__bash` tool is an isolated Linux
  sandbox with only mounted-folder file access — it CANNOT execute
  `C:\Users\phant\.grok\bin\grok.exe` or anything else on her real OS. So
  **Methods B and C are not usable by Claude today**, regardless of this
  handbook's instructions, unless a different tool is added later.
- **Method A (Computer Use into the TUI/GUI)** is the only theoretically
  available path, and it is blocked purely on the `request_access` app-name
  resolution step above — not on anything in this handbook.
- Practical status: Claude continues directing Grok via paste-in prompt files
  (as done for every wave so far) until access resolves.

## 1. Environment snapshot (as reported by Grok Build, 2026-07-23)

| Item | Value |
|---|---|
| Binary | `C:\Users\phant\.grok\bin\grok.exe` |
| Version | grok 0.2.111 (94172f2aa4) [stable] |
| GROK home | `C:\Users\phant\.grok` |
| CWD (session) | `C:\Users\phant\.grok\downloads` |
| Permission mode | always-approve (in `config.toml`) |
| Model | grok-4.5 |
| Agent | grok-build-plan |
| Reasoning | high |
| Sandbox | off |
| Active-sessions file | `C:\Users\phant\.grok\active_sessions.json` |
| Session store | `C:\Users\phant\.grok\sessions\C%3A%5CUsers%5Cphant%5C.grok%5Cdownloads\<session-id>\` |

**Sessions reported active at handoff time:**
1. `019f8ded-1cdc-7052-be45-1d519dd5c9b7` — "Update Grok Build to Latest
   Version" — **NOT one of the two registered parents.** Flagged, not adopted
   (see §5).
2. `019f8e3c-e53b-74e0-a878-df6b8398338e` — "AIdle_openworld Agent Character
   Animation Design..." — this IS the registered **design parent**.

Notably **`019f7ffd-3995-71c0-aca1-51078e24a852` (the registered BUILD
parent) was not in this handoff's active list at all.** Not treated as gone —
just not confirmed live in this particular snapshot.

## 2. Method A — Computer Use into the TUI (the only path open to Claude)

Once `request_access` succeeds:
1. Screenshot first — is Grok idle or mid tool-call?
2. Focus the prompt (Tab or Space if not already focused).
3. Type the directive as plain text.
4. Enter = send now, or queue if Grok is mid-turn.
5. Mid-turn controls: `Ctrl+Enter` = cancel current + send new now (or
   `Ctrl+L` in VS Code-family terminals); `Esc` = cancel turn, keep draft;
   `Ctrl+C` = clear draft (1st press) / cancel (2nd press).
6. `Ctrl+O` always-approve toggle, `Ctrl+P`/`?` command palette, `Ctrl+S`/
   `/resume` session picker, `/quit` exit, `/status`, `/context`, `/compact
   keep <point>`, `/todo`/`Ctrl+T`, `/copy`, `/new` (new session — see §5).
7. Paste: `Ctrl+V` text, `Alt+V` image (Windows Terminal).

## 3. Worker-brief prompt shape (for Claude to type into Grok, once able)

```
[SUPERVISOR DIRECTIVE]
Goal: <one line>
Scope: <files/dirs allowed>
Out of scope: <not allowed>
Authority: READ_ONLY | PATCH_DRAFT | VERIFY_ONLY | HUMAN_APPROVAL_REQUIRED
Done when: <criteria>
Constraints:
- No force-push / no data deletion / no shared remote state without explicit permission
- Report briefly: what changed / how verified / blockers
```

This is consistent with (not a replacement for) the project's own
`STANDARD_GROK_WORK_ORDER_PROMPT_TEMPLATE_001.md` — that template stays the
authoritative content shape for WO dispatch; this is the transport mechanics.

## 4. Guardrails (binding on Claude if/when computer-use access is granted)

1. Confirm the focused window is the correct Grok session before typing
   anything (check title/session id against §1's registered parents).
2. Never `/quit` unless the Human explicitly asks to close it.
3. Never `/new` while supervising a live session — it drops context, and per
   entry 003 of `CONDUCTOR_JOURNAL.md`, a prior conductor session nearly
   created a duplicate top-level session this way (via `open_application`,
   not `/new`, but same family of mistake). Prefer `/resume` to a named id.
4. One clear directive beats many partial messages — do not spam.
5. If a permission prompt appears (rare under always-approve), read it, do
   not blind-click.
6. Destructive git/ops instructions to Grok require asking the Human first —
   same rule as everywhere else in this project's governance.
7. Self-test before real directives: send a `[SUPERVISOR PING]` with
   `Authority: REPORT_ONLY` asking for session id / model / current task in 3
   lines, no tool calls. Confirms the channel is real before trusting it.

## 5. Open finding — third session ID not adopted

`019f8ded-1cdc-7052-be45-1d519dd5c9b7` ("Update Grok Build to Latest
Version") appeared in this handoff's active-sessions list. The project's
governance (`codex_directive.json` → `parent_sessions`) registers exactly
two Human-authorized parents: build `019f7ffd-...` and design `019f8e3c-...`.
This third id looks like a Grok-app self-update/maintenance session, not a
game-development parent, and is **not** added to `parent_sessions` on this
handbook's say-so alone — that would silently violate the "exactly two,
explicitly Human-authorized" rule Claude itself wrote into the vision lock
two turns ago. Needs the Human's confirmation before any governance change.

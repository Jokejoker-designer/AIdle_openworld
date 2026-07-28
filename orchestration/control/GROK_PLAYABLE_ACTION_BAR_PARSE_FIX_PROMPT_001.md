# Grok build session (019f7ffd) — fix real parse error in playable_action_bar.gd

Paste the block below into Grok Desktop session `019f7ffd-3995-71c0-aca1-51078e24a852`
(the Build parent). The Human ran the real game and hit this error live — pasted the raw
engine log. Claude conductor read the actual file and confirmed the exact bug before
writing this directive.

---

```
[SUPERVISOR DIRECTIVE] Fix real script parse error blocking gardener UI — Human hit this live

Human ran the actual game (not a QA test) and got this real engine error:

SCRIPT ERROR: Parse Error: Cannot infer the type of "is_garden" variable because the value doesn't have a set type.
          at: GDScript::reload (res://scripts/ui/playable_action_bar.gd:216)
ERROR: Failed to load script "res://scripts/ui/playable_action_bar.gd" with error "Parse error".

Game still booted (rest of the log is clean — town/street/companion all loaded fine) but
this script failing to parse means the gardener action bar row does not actually work in
real play — this is why she reported "animation chưa hoạt động được" (animation doesn't
work) despite the QA receipt/GIFs looking fine. The QA test (nori7_anim_15clip_headed_qa_001.gd)
never loads this UI script at all, so it never caught this — it only exercises the
presenter directly, not the real button wiring.

Root cause (confirmed by reading the file directly): game/scripts/ui/playable_action_bar.gd
line 216:

    var is_garden := b == btn_water or b == btn_plant or b == btn_harvest or b == btn_charge or b == btn_low_energy

`b` comes from `for b in all_btns:` where `all_btns: Array` (line 209) is an UNTYPED array,
so `b` is Variant. GDScript's static analyzer cannot infer a concrete type for the
`==`/`or` chain result under `:=` inferred typing when the left operand is Variant-typed,
so it fails to parse.

Fix (one line, no logic change): give the variable an explicit type instead of inferring it:

    var is_garden: bool = (b == btn_water or b == btn_plant or b == btn_harvest or b == btn_charge or b == btn_low_energy)

Scope:
1. Apply exactly that one-line fix at line 216. Do not touch any other line/logic in this
   file or any other file.
2. Re-run the actual game headed (not just the QA test script) far enough to confirm the
   script now loads with ZERO parse/script errors in the console, the action bar (all
   rows, not just gardener) renders, and clicking each of the 5 gardener buttons (Water/
   Plant/Harvest/Charge/Rest) actually fires gardener_action_pressed -> _on_gardener_action
   -> Nori apply_trigger, with the console print you documented earlier
   ("[Main] gardener_action action=... ok=true ... client_world_commit=false").
3. File a small receipt (e.g. playable_action_bar_parse_fix_001.json) with: exact diff,
   before/after console output (specifically confirm the SCRIPT ERROR line is gone), and
   confirmation all 5 buttons were actually clicked and produced the expected console
   line — not just "script loads now" without exercising the buttons.
4. Also add one line to your own honesty ledger: the original nori7_anim_15clip_qa_receipt.json
   claim "UI gardener row: PlayableActionBar Row3 -> Water/Plant/Harvest/Charge/Rest" as
   done was not actually exercised end-to-end in a real running game before being reported
   complete -- note this gap plainly, don't paper over it.
5. accepted=false, self_accept=false, Purple stays WAITING -- this is a bug fix + honest
   re-verification, not a product acceptance event.

This is a real regression in game/** — no scope ambiguity here, just fix it and prove it
with a real headed play-through, not another isolated unit-style test.
```

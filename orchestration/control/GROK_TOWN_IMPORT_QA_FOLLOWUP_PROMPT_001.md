# Grok town-import QA follow-up prompt 001

Paste into the BUILD session (`019f7ffd-3995-71c0-aca1-51078e24a852`). Independent
verification of WO-TOWN-GRID-IMPORT-001 is done; Blue+Red hold, QA is missing.

---

```
TOWN CADASTRE IMPORT — QA follow-up (directive 99, WO-TOWN-GRID-IMPORT-001)

Independently verified: payload_fingerprint round-trips (game resource == design
plan, 50 plots both), town_layout_10phase.json untouched, starter_realm_builder.gd
and main.gd additive-only (nothing deleted, flags default correctly), and
town_grid_loader.gd's honesty logic is real in code (placeholder vs real GLB is
gated on FileAccess.file_exists on the resolved path, not a claim). Blue and Red
do not need rework.

Gap: no QA phase ran. Only a headless smoke print exists inside BLUE's own
receipt — there is no QA_*.json, and PURPLE_WAITING_001.json's evidence list has
no headed screenshot. Your own status report said "headed screenshot = Human
next" — that step is still open, not done, and the WO's acceptance criteria
require it (headed screenshot, real GLBs visible at their plots, honest
placeholders elsewhere, art-style recorded).

New standing rule now in force (see AIDLE_GAME_VISION_LOCK_001.md): anything
built against a MOCKUP_SSOT_V2 entry must visually match that mockup 100%
(silhouette/palette/key details) before its wave can close. This wave claims 21
real GLBs placed — each one now needs a headed comparison against its mockup art,
not just "GLB loaded without error."

Do this and file QA_town_grid_headed_001.json under
orchestration/receipts/town_grid_import_001/:
1. Launch the realm with the cadastre live (attach_town_cadastre=true or the
   cadastre scene entry). Capture a real headed screenshot showing all 50 plots
   (footprint + label visible), zero new Godot errors.
2. For each plot with a real production GLB, note visual match against its
   MOCKUP_SSOT_V2 concept art — flag any mismatch honestly rather than closing
   over it. Do not claim 100% match unless it is actually 100%.
3. Attach the raw headed Godot log FILE PATH in the receipt (not just a restated
   marker string) so Claude can decode it independently.
4. Keep accepted=false, self_accept=false. Purple stays WAITING for Human batch
   accept after Claude re-verifies the headed evidence.

Full detail: orchestration/receipts/town_grid_import_001/CLAUDE_VERIFY_001.json
```

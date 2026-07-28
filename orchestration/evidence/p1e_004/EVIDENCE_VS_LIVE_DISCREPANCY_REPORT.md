# Evidence vs live game discrepancy — root-cause report (no fix applied)

**Date:** 2026-07-22  
**Authority:** REPORT_ONLY / VERIFY_ONLY  
**accepted:** false · **self_accept:** false  
**Product decision deferred** on art-style × Cozy kit (Human Product Lead)

## CONFIRMED (Human Product Lead + conductor)

**Possibility TWO only — art style mismatch.** Stop investigating 1/3/4 as primary.

- HUD: `Art: Surrealism Canvas` / `surrealism_canvas`
- `world_meta.cfg`: `art_style="surrealism_canvas"`
- Palette: cozy ground `8FBC8F` vs surrealism ground `8B7AA8` (lavender she sees)
- Evidence was correct for cozy / Blender; live game correct for surrealism
- Durable receipt: `orchestration/receipts/p1e/P1E_004_STYLE_MISMATCH_ROOT_CAUSE_001.json`
- QA standard: `orchestration/standards/HEADED_VISUAL_EVIDENCE_QA.md`

## Human observation (live headed)

- Pond white  
- Rocks white  
- Player capsule white  
- Ground pale lavender  
- HUD earlier: **Art: Surrealism Canvas**

## Conductor evidence that looked “colourful”

| Artefact | Kind | Timestamp (local) | Chromatic sat>15% | Notes |
|----------|------|-------------------|-------------------|--------|
| `p1e_w1/starter_realm_preview_p1e003_corr_w1.png` | **Blender EEVEE** export | 2026-07-21 22:53 | ~94.5% (human) | Not Godot; no ArtStyleManager |
| `p1e_004/starter_realm_preview_p1e004_corr_hsl.png` | **Blender EEVEE** export | 2026-07-22 00:42 | colourful | Same — Blender package preview |
| `p1e_intake/godot_seven_modules_runtime.png` | Godot capture | **2026-07-21 21:07** | ~97.9% (human) | **Stale** vs later product |

---

## Four possibilities

### 1) Evidence staleness — **CONFIRMED for Godot runtime PNG**

- `godot_seven_modules_runtime.png` mtime **21:07 on 2026-07-21**.
- After that (product timeline): P1E-003 densify/corr water emission, ArtStyleManager commit `1cd0be4`, P1E-004 DNA, water HSL package **BLD-03CB1AADD475**.
- **Default live package path was never pointed at CORR package.**  
  `glb_intake_package.gd`:
  - `DEFAULT_QUARANTINE_JOB = "BLD-10A9DEB39E8E"`
  - Smoke `p1e003` was retargeted to `BLD-03CB1AADD475` only.
- So: smoke measured CORR package; **live default still loads BLD-10A9DEB39E8E** (white-emission pond era).

Blender previews are also **not** the running game (different renderer, no art-style system).

### 2) Art style mismatch — **CONFIRMED for live session**

Saved world meta on this machine:

```
C:\Users\phant\AppData\Roaming\Godot\app_userdata\AIdle Openworld\world_meta.cfg
art_style="surrealism_canvas"
updated_at="2026-07-21T00:13:43"  (and a second copy with same style)
```

- `DEFAULT_ART_STYLE` in code is `cozy_cyber_pixel`.
- `ArtStyleManager._load_world_meta()` **restores saved style over default** when the key exists.
- Cozy kit + `COZY_ART_BIBLE_001` hexes are authored for **cozy_cyber_pixel**.
- Live HUD “Art: Surrealism Canvas” matches disk.

Environment application under active style (`world_root.gd` `_apply_art_style_environment`):

- Ground mesh albedo ← `palette.ground`  
  Surrealism builtin after palette edit: **`#8B7AA8` (pale lavender)**  
- Sky / ambient ← `palette.sky` lightened (`#A8B4E0` family)  
- Matches human “ground is pale lavender”.

**Product decision required (not taken here):**  
Does Cozy kit ship **only** under `cozy_cyber_pixel`, or does every kit need per-style palette variants? That is for Human Product Lead.

### 3) Did ArtStyleManager fix change what loads? — **Dictionary path: no; palette content: yes (bundled)**

Commit `1cd0be4`:

- **Did fix** eager `.get()` crash (does not change which style id is selected).
- **Did not change** `_load_world_meta` selection rule (still: saved id if present).
- **Did change surrealism palette content** in the same file/commit:
  - ground `3C096C` → `8B7AA8` (deep purple → **pale lavender**)
  - sky `240046` → `A8B4E0` (near-black → light periwinkle)
- So for a user **already on surrealism_canvas**, the ASM “fix” commit **also** lightened the wash they see. That is separate from the Dictionary bugfix and should have been its own allowlisted visual decision.

### 4) Style palette re-paints GLB materials? — **NO for GLB module meshes; YES for env/ground/procedural fillers**

| Path | Style palette applies? |
|------|-------------------------|
| GLB surfaces via `glb_intake` / `glb_intake_runtime_builder` | **No** recolor by style — materials from GLTF |
| `Systems/Ground` mesh | **Yes** — `material_override` from palette.ground |
| `WorldEnvironment` sky/ambient | **Yes** — palette.sky |
| Procedural fence / ground_variation fillers | **Yes** — `starter_realm_builder._palette()` |
| Player capsule mesh | **No style** — default white presentation mesh unless authored |

Conclusion: GLB pond/rocks do **not** get palette-repainted after intake. Live white pond is more consistent with **package BLD-10A9DEB39E8E emission wash** + **bright ambient**, not a post-GLB style recolor of `baseColorFactor`. White player is the default capsule, not kit materials.

---

## Combined root cause (ranked)

1. **Wrong artefact class for “game looks right” claims**  
   Blender package PNG + stale Godot PNG ≠ headed game with saved style + default package path.

2. **Live package default = BLD-10A9DEB39E8E** (white-emission pond), while CORR evidence measured **BLD-03CB1AADD475** / Blender HSL PNG.

3. **Live art style = surrealism_canvas** (world_meta), not cozy_cyber_pixel → lavender ground + cool high ambient wash; Cozy kit not authored for that style.

4. **ASM commit also lightened surrealism palette** (ground/sky), amplifying pale wash for existing surrealism saves — without changing style **selection**.

5. **Not primary:** style-driven recolor of GLB material slots (does not exist on intake).

---

## Permanent QA rule (to adopt)

Headed visual evidence **must**:

1. Be captured from **Godot headed** (or documented renderer).  
2. State **`art_style_id_active`** on the receipt.  
3. State **`package_job_id`** / path the realm was built from.  
4. Match the **same build + same style** the human will run (or explicitly mark “not live parity”).

Without those fields, visual PASS claims are untrustworthy.

---

## What we are **not** doing until you decide

- No pond recolor “fix” for surrealism.  
- No silent force of cozy_cyber_pixel.  
- No art wave 2.  
- No product decision on kit × style matrix.

**Need from conductor / Human Product Lead:**

A. Live default package: pin to which BLD job?  
B. Cozy kit: cozy-only, or multi-style variants?  
C. Surrealism palette lightening in `1cd0be4`: keep or revert ground/sky?  
D. Player capsule: intentional white shell or needs style material?

`accepted=false` · `self_accept=false` · WAITING_HUMAN

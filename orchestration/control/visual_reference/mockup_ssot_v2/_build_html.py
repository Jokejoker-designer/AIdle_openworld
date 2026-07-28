# -*- coding: utf-8 -*-
"""Generate MOCKUP_SSOT_V2.html from MOCKUP_SSOT_V2.json."""
import json
from pathlib import Path

dest = Path(__file__).resolve().parent
index = json.loads((dest / "MOCKUP_SSOT_V2.json").read_text(encoding="utf-8"))


def svg_building(bid: str, name: str) -> str:
    colors = {
        "cozy_house_small_A": ("#fdf3e2", "#c45c3e"),
        "cozy_greenhouse_A": ("#d4f0e0", "#7fc98f"),
        "cozy_barn_small_A": ("#e8d4b8", "#a67c52"),
        "cozy_workshop_A": ("#efe0c8", "#8b6b4a"),
        "cozy_market_stall_A": ("#fff1c7", "#e07a5f"),
        "cozy_windmill_A": ("#f5efe3", "#6b8cae"),
        "cozy_well_house_A": ("#e8e4dc", "#7a8b99"),
        "cozy_watchtower_A": ("#efe6d4", "#9a7b5a"),
        "cozy_bridge_arch_A": ("#d9d2c5", "#8a8378"),
        "cozy_gazebo_A": ("#fdf3e2", "#72A96B"),
    }
    wall, roof = colors.get(bid, ("#fdf3e2", "#c98a5e"))
    short = name[:12]
    return f'''<svg viewBox="0 0 120 100" class="ico"><rect x="25" y="40" width="70" height="45" rx="4" fill="{wall}" stroke="#263238" stroke-width="2"/>
    <polygon points="20,42 60,12 100,42" fill="{roof}" stroke="#263238" stroke-width="2"/>
    <rect class="door" x="52" y="58" width="16" height="27" rx="2" fill="#f5c451"/>
    <circle class="window" cx="40" cy="58" r="6" fill="#9ED7E5" stroke="#263238" stroke-width="1.5"/>
    <text x="60" y="96" text-anchor="middle" font-size="7" fill="#263238" font-family="Segoe UI">{short}</text></svg>'''


def svg_prop(pid: str) -> str:
    if "tree" in pid:
        return '''<svg viewBox="0 0 100 100" class="ico"><ellipse class="canopy" cx="50" cy="40" rx="28" ry="24" fill="#72A96B" stroke="#263238" stroke-width="2"/><rect x="45" y="55" width="10" height="30" rx="2" fill="#8B5A2B"/></svg>'''
    if "rock" in pid:
        return '''<svg viewBox="0 0 100 100" class="ico"><ellipse cx="50" cy="62" rx="30" ry="18" fill="#9a958c" stroke="#263238" stroke-width="2"/><ellipse cx="42" cy="56" rx="12" ry="8" fill="#b5b0a6"/></svg>'''
    if "flower" in pid or "bush" in pid or "grass" in pid:
        return '''<svg viewBox="0 0 100 100" class="ico"><circle class="bloom" cx="50" cy="42" r="14" fill="#e88ab5" stroke="#263238" stroke-width="1.5"/><circle cx="50" cy="42" r="5" fill="#f5c451"/><line x1="50" y1="56" x2="50" y2="80" stroke="#5a8f4a" stroke-width="4"/></svg>'''
    if "pond" in pid or "birdbath" in pid:
        return '''<svg viewBox="0 0 100 100" class="ico"><ellipse class="water" cx="50" cy="58" rx="34" ry="16" fill="#7ec8e3" stroke="#263238" stroke-width="2"/><ellipse cx="50" cy="58" rx="18" ry="6" fill="#b8e4f5" opacity="0.7"/></svg>'''
    if "lamp" in pid:
        return '''<svg viewBox="0 0 100 100" class="ico"><rect x="46" y="40" width="8" height="40" fill="#8B5A2B"/><circle class="glow" cx="50" cy="32" r="14" fill="#f5c451" opacity="0.9"/><circle cx="50" cy="32" r="8" fill="#fff1c7"/></svg>'''
    if "fence" in pid:
        return '''<svg viewBox="0 0 100 100" class="ico"><rect x="12" y="35" width="8" height="40" fill="#c98a5e"/><rect x="46" y="35" width="8" height="40" fill="#c98a5e"/><rect x="80" y="35" width="8" height="40" fill="#c98a5e"/><rect x="12" y="45" width="76" height="6" fill="#a67c52"/><rect x="12" y="60" width="76" height="6" fill="#a67c52"/></svg>'''
    if "path" in pid:
        return '''<svg viewBox="0 0 100 100" class="ico"><ellipse cx="30" cy="55" rx="14" ry="8" fill="#c9b98a"/><ellipse cx="50" cy="62" rx="14" ry="8" fill="#b8a878"/><ellipse cx="70" cy="55" rx="14" ry="8" fill="#c9b98a"/></svg>'''
    if "farm" in pid or "crop" in pid:
        return '''<svg viewBox="0 0 100 100" class="ico"><rect x="15" y="50" width="70" height="28" rx="4" fill="#8B6914" stroke="#263238"/><rect x="20" y="40" width="8" height="18" fill="#72A96B"/><rect x="36" y="36" width="8" height="22" fill="#7fc98f"/><rect x="52" y="42" width="8" height="16" fill="#72A96B"/><rect x="68" y="38" width="8" height="20" fill="#5a8f4a"/></svg>'''
    if "campfire" in pid:
        return '''<svg viewBox="0 0 100 100" class="ico"><ellipse cx="50" cy="70" rx="18" ry="6" fill="#8a8378"/><path class="flame" d="M50 30 Q60 50 50 65 Q40 50 50 30" fill="#e07a5f"/><path d="M50 38 Q56 50 50 60 Q44 50 50 38" fill="#f5c451"/></svg>'''
    if "scarecrow" in pid:
        return '''<svg viewBox="0 0 100 100" class="ico"><line x1="50" y1="30" x2="50" y2="80" stroke="#8B5A2B" stroke-width="4"/><line x1="25" y1="45" x2="75" y2="45" stroke="#8B5A2B" stroke-width="4"/><circle cx="50" cy="28" r="10" fill="#efe0c8" stroke="#263238"/><rect x="35" y="45" width="30" height="20" rx="3" fill="#c45c3e"/></svg>'''
    return '''<svg viewBox="0 0 100 100" class="ico"><rect x="28" y="40" width="44" height="36" rx="3" fill="#c98a5e" stroke="#263238" stroke-width="2"/><line x1="28" y1="52" x2="72" y2="52" stroke="#8B5A2B" stroke-width="2"/><line x1="50" y1="40" x2="50" y2="76" stroke="#8B5A2B" stroke-width="2"/></svg>'''


html_chars = []
for i, c in enumerate(index["characters"], 1):
    vid = c.get("video")
    media = ""
    if vid:
        media = f'<video class="media" src="{vid}" autoplay muted loop playsinline data-role="video"></video>'
    photo_hidden = " hidden" if vid else ""
    media += f'<img class="media photo" src="{c["img"]}" alt="{c["name"]}" data-role="photo"{photo_hidden}/>'
    clips = "".join(
        f'<span class="clip{" real" if c.get("prod") == "runtime_glb" else ""}">{cl}</span>'
        for cl in c["clips"]
    )
    badge = "ok" if c.get("prod") == "runtime_glb" else "warn"
    badge_txt = "GLB prod" if c.get("prod") == "runtime_glb" else "mockup art"
    html_chars.append(
        f'''
    <article class="card char" data-id="{c['id']}" data-motion="{c['motion']}">
      <div class="stage anim-{c['motion']}" data-stage>
        {media}
        <div class="ground"></div>
      </div>
      <div class="body">
        <h3>{i}. {c['name']}</h3>
        <div class="meta">{c['id']} · {c['class']} · {c['world']}</div>
        <div class="meta">form: {c['form']} · signature: {c['signature']}</div>
        <div class="clips">{clips}</div>
        <div class="btns">
          <button type="button" data-anim="idle" class="active">idle</button>
          <button type="button" data-anim="walk">walk</button>
          <button type="button" data-anim="scan">scan</button>
          <button type="button" data-anim="happy">happy</button>
          <button type="button" data-anim="cancel">cancel</button>
          <button type="button" data-toggle-vid title="Anh / Video">media</button>
        </div>
        <span class="badge {badge}">{badge_txt}</span>
      </div>
    </article>'''
    )

html_bld = []
for i, b in enumerate(index["buildings"], 1):
    img = b.get("img")
    vid = b.get("video")
    if img:
        media = f'<img class="media photo" src="{img}" alt="{b["name"]}"/>'
        if vid:
            media = f'<video class="media" src="{vid}" autoplay muted loop playsinline></video>' + media
    else:
        media = svg_building(b["id"], b["name"])
    html_bld.append(
        f'''
    <article class="card bld" data-id="{b['id']}" data-anim="{b['anim']}">
      <div class="stage anim-{b['anim']}" data-stage>{media}<div class="ground"></div></div>
      <div class="body">
        <h3>{i}. {b['name']}</h3>
        <div class="meta">{b['id']} · {b['cat']}</div>
        <div class="meta">ambient: <code>{b['anim']}</code></div>
      </div>
    </article>'''
    )

html_props = []
for i, p in enumerate(index["props"], 1):
    img = p.get("img")
    vid = p.get("video")
    if img:
        media = f'<img class="media photo" src="{img}" alt="{p["name"]}"/>'
        if vid:
            media = (
                f'<video class="media" src="{vid}" autoplay muted loop playsinline></video>'
                f'<img class="media photo" src="{img}" alt="{p["name"]}" hidden/>'
            )
    else:
        media = svg_prop(p["id"])
    html_props.append(
        f'''
    <article class="card prop" data-id="{p['id']}" data-anim="{p['anim']}">
      <div class="stage anim-{p['anim']}" data-stage>{media}<div class="ground"></div></div>
      <div class="body">
        <h3>{i}. {p['name']}</h3>
        <div class="meta">{p['id']} · {p['cat']}</div>
        <div class="meta">ambient: <code>{p['anim']}</code></div>
      </div>
    </article>'''
    )

html = f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>AIdle MOCKUP SSOT V2 — 15 NV + 30 Prop + 10 Building (OFFICIAL DESIGN LOCK)</title>
<style>
:root {{
  --cream:#fdf3e2; --cream-shade:#efe0c8; --leaf:#72A96B; --ink:#263238;
  --sky:#9ED7E5; --wood:#c98a5e; --cyan:#62E6FF; --card:#fffaf0;
  --border:#e8d9c0; --warm:#f5c451; --danger:#D85C5C;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; font-family:"Segoe UI", system-ui, sans-serif; color:var(--ink);
  background:
    radial-gradient(1200px 600px at 10% -10%, #e8f7ff 0%, transparent 50%),
    radial-gradient(900px 500px at 100% 0%, #fff3d6 0%, transparent 45%),
    linear-gradient(180deg, #f7f0e4, #efe6d4 40%, #e7f2ea);
  line-height:1.45;
}}
header, section, footer {{ max-width:1280px; margin:0 auto; padding:16px 24px; }}
header {{ padding-top:28px; }}
h1 {{ margin:0 0 8px; font-size:1.6rem; letter-spacing:-0.02em; }}
h2 {{ margin:28px 0 12px; font-size:1.2rem; border-left:4px solid var(--leaf); padding-left:10px; }}
.lock-banner {{
  background: linear-gradient(90deg, #1b4332, #2d6a4f);
  color:#e8f5e9; border-radius:14px; padding:14px 18px; margin:12px 0 8px;
  border:2px solid #95d5b2; box-shadow:0 8px 24px rgba(27,67,50,.25);
}}
.lock-banner strong {{ color:#b7f0c8; }}
.badge {{ display:inline-block; background:var(--cream); border:1px solid var(--border);
  border-radius:999px; padding:2px 10px; font-size:.78rem; margin:4px 4px 0 0; }}
.badge.ok {{ background:#e4f7ea; border-color:#b7e2c4; }}
.badge.warn {{ background:#fff4d6; border-color:#efd48a; }}
.badge.lock {{ background:#1b4332; color:#e8f5e9; border-color:#95d5b2; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:16px; }}
.grid.dense {{ grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); }}
.card {{ background:var(--card); border:1px solid var(--border); border-radius:16px; overflow:hidden;
  box-shadow:0 8px 24px rgba(38,50,56,.06); display:flex; flex-direction:column; }}
.stage {{ position:relative; height:200px; display:grid; place-items:center; overflow:hidden;
  background: linear-gradient(180deg, #dfeff5 0%, #f5efe3 55%, #e4dcc8 100%); }}
.stage .media, .stage .ico {{ max-width:88%; max-height:86%; object-fit:contain;
  filter: drop-shadow(0 10px 14px rgba(0,0,0,.12)); z-index:2; }}
.stage video.media {{ max-height:90%; border-radius:8px; }}
.stage .ico {{ width:120px; height:100px; }}
.ground {{ position:absolute; bottom:18px; left:15%; right:15%; height:10px; border-radius:50%;
  background:rgba(38,50,56,.08); z-index:1; }}
.body {{ padding:12px 14px 14px; flex:1; display:flex; flex-direction:column; gap:5px; }}
.body h3 {{ margin:0; font-size:1rem; }}
.meta {{ font-size:.76rem; opacity:.82; font-family:ui-monospace, Consolas, monospace; }}
.clips {{ display:flex; flex-wrap:wrap; gap:4px; margin-top:2px; }}
.clip {{ font-size:.66rem; background:#eef7fb; border:1px solid #cfe3ec; border-radius:6px; padding:2px 6px; }}
.clip.real {{ background:#e6f8ec; border-color:#b6e2c3; }}
.btns {{ display:flex; flex-wrap:wrap; gap:5px; margin-top:6px; }}
button {{ border:1px solid var(--border); background:#fff; border-radius:8px; padding:4px 8px;
  font-size:.72rem; cursor:pointer; }}
button.active {{ background:var(--leaf); color:#123; border-color:#5aa86d; }}
.toolbar {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin:10px 0 4px; }}
.toolbar select {{ padding:6px 10px; border-radius:8px; border:1px solid var(--border); background:#fff; }}
.sheet-preview {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:12px 0; }}
.sheet-preview img {{ width:100%; border-radius:12px; border:1px solid var(--border); background:#fff; }}
@media (max-width:800px) {{ .sheet-preview {{ grid-template-columns:1fr; }} }}
@keyframes bob {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-6px)}} }}
@keyframes bob_small {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-3px)}} }}
@keyframes breathe {{ 0%,100%{{transform:scale(1)}} 50%{{transform:scale(1.06)}} }}
@keyframes walk {{ 0%,100%{{transform:translate(0,0) rotate(-1.5deg)}} 50%{{transform:translate(6px,-5px) rotate(1.5deg)}} }}
@keyframes scan {{ 0%,100%{{transform:rotate(0)}} 25%{{transform:rotate(-8deg)}} 75%{{transform:rotate(8deg)}} }}
@keyframes happy {{ 0%,100%{{transform:scale(1) translateY(0)}} 40%{{transform:scale(1.08) translateY(-10px)}} 70%{{transform:scale(1.02) translateY(-2px)}} }}
@keyframes cancel {{ 0%,100%{{transform:translateX(0)}} 20%{{transform:translateX(-5px)}} 40%{{transform:translateX(5px)}} 60%{{transform:translateX(-3px)}} }}
@keyframes sway {{ 0%,100%{{transform:rotate(-2.5deg)}} 50%{{transform:rotate(2.5deg)}} }}
@keyframes sway_small {{ 0%,100%{{transform:rotate(-1.2deg)}} 50%{{transform:rotate(1.2deg)}} }}
@keyframes pulse {{ 0%,100%{{opacity:.55}} 50%{{opacity:1; filter:drop-shadow(0 0 12px rgba(245,196,81,.7))}} }}
@keyframes spin {{ from{{transform:rotate(0)}} to{{transform:rotate(360deg)}} }}
@keyframes steam_rise {{ 0%{{transform:translateY(2px);opacity:.55}} 100%{{transform:translateY(-16px);opacity:0}} }}
@keyframes door_pulse {{ 0%,100%{{opacity:.65}} 50%{{opacity:1; filter:drop-shadow(0 0 8px #f5c451)}} }}
@keyframes flag_sway {{ 0%,100%{{transform:rotate(-3deg)}} 50%{{transform:rotate(4deg)}} }}
@keyframes cloth_sway {{ 0%,100%{{transform:skewX(-2deg)}} 50%{{transform:skewX(2deg)}} }}
@keyframes ripple {{ 0%,100%{{transform:scaleX(1)}} 50%{{transform:scaleX(1.04)}} }}
@keyframes flicker {{ 0%,100%{{transform:scaleY(1); opacity:.9}} 50%{{transform:scaleY(1.12); opacity:1}} }}
@keyframes idle_static {{ 0%,100%{{transform:translateY(0)}} }}
@keyframes manifestIn {{
  0% {{ opacity:.15; transform:scale(.92); filter:brightness(2) saturate(.2); }}
  35% {{ opacity:.55; filter:brightness(1.4) hue-rotate(20deg); }}
  70% {{ opacity:.9; filter:brightness(1.05); }}
  100% {{ opacity:1; transform:scale(1); filter:none; }}
}}
.stage.anim-bob .media, .stage.anim-bob .ico {{ animation: bob 2.4s ease-in-out infinite; transform-origin:center bottom; }}
.stage.anim-bob_small .media, .stage.anim-bob_small .ico {{ animation: bob_small 3.0s ease-in-out infinite; transform-origin:center bottom; }}
.stage.anim-breathe .media, .stage.anim-breathe .ico {{ animation: breathe 2.8s ease-in-out infinite; transform-origin:center bottom; }}
.stage.anim-walk .media, .stage.anim-walk .ico {{ animation: walk .7s ease-in-out infinite; transform-origin:center bottom; }}
.stage.anim-scan .media, .stage.anim-scan .ico {{ animation: scan 1.4s ease-in-out infinite; transform-origin:center 60%; }}
.stage.anim-happy .media, .stage.anim-happy .ico {{ animation: happy 1.1s ease-in-out infinite; transform-origin:center bottom; }}
.stage.anim-cancel .media, .stage.anim-cancel .ico {{ animation: cancel .55s ease-in-out infinite; }}
.stage.anim-sway .media, .stage.anim-sway .ico {{ animation: sway 3.5s ease-in-out infinite; transform-origin:center bottom; }}
.stage.anim-sway_small .media, .stage.anim-sway_small .ico {{ animation: sway_small 4.2s ease-in-out infinite; transform-origin:center bottom; }}
.stage.anim-pulse .media, .stage.anim-pulse .ico {{ animation: pulse 2.0s ease-in-out infinite; }}
.stage.anim-spin .ico {{ animation: spin 9s linear infinite; transform-origin:center 40%; }}
.stage.anim-steam_rise .media, .stage.anim-steam_rise .ico {{ animation: steam_rise 2.6s ease-out infinite; }}
.stage.anim-door_pulse .media, .stage.anim-door_pulse .door {{ animation: door_pulse 2.0s ease-in-out infinite; }}
.stage.anim-flag_sway .ico {{ animation: flag_sway 3.2s ease-in-out infinite; transform-origin:top center; }}
.stage.anim-cloth_sway .ico {{ animation: cloth_sway 3.0s ease-in-out infinite; }}
.stage.anim-ripple .media, .stage.anim-ripple .water {{ animation: ripple 3.0s ease-in-out infinite; }}
.stage.anim-flicker .ico {{ animation: flicker .55s ease-in-out infinite; transform-origin:center bottom; }}
.stage.anim-idle_static .media, .stage.anim-idle_static .ico {{ animation: idle_static 4s linear infinite; }}
.stage.manifest {{ background: radial-gradient(circle at 50% 60%, rgba(98,230,255,.35), transparent 55%), linear-gradient(180deg,#1a2a33,#2c3e48); }}
.stage.manifest .media {{ animation: manifestIn 3.2s ease-in-out infinite; }}
table.reg {{ width:100%; border-collapse:collapse; font-size:.86rem; background:var(--card); border:1px solid var(--border); border-radius:12px; overflow:hidden; }}
table.reg th, table.reg td {{ border-bottom:1px solid var(--border); padding:8px 10px; text-align:left; vertical-align:top; }}
table.reg th {{ background:#f3ebe0; }}
.pipeline {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:8px; margin:12px 0; }}
.pipe-step {{ background:var(--card); border:1px dashed var(--border); border-radius:12px; padding:10px; font-size:.8rem; }}
.pipe-step strong {{ display:block; margin-bottom:4px; color:#1b5e20; }}
footer {{ opacity:.88; font-size:.85rem; padding-bottom:48px; }}
.tabs {{ display:flex; gap:8px; flex-wrap:wrap; margin:8px 0 0; }}
.tabs a {{ text-decoration:none; color:var(--ink); background:var(--card); border:1px solid var(--border); border-radius:999px; padding:6px 12px; font-size:.85rem; }}
.tabs a:hover {{ background:var(--cream); }}
</style>
</head>
<body>
<header>
  <h1>AIdle Official Mockup SSOT V2</h1>
  <p><strong>15 nhân vật</strong> (animation) · <strong>30 vật thể</strong> · <strong>10 building</strong></p>
  <div class="lock-banner">
    LOCK <strong>QUY ĐỊNH KHÓA THIẾT KẾ:</strong> Toàn bộ art, mesh, rig, clip, prop, building trong game
    <strong>phải bám sát mockup này</strong> (silhouette, palette, motion timing, ID, clip names).
    Lệch mockup = fail QA / CHANGES_REQUESTED. Chi tiết: <code>MOCKUP_DESIGN_LOCK.md</code>
  </div>
  <span class="badge lock">DESIGN_SSOT_ACTIVE</span>
  <span class="badge ok">15 cast</span>
  <span class="badge ok">30 props</span>
  <span class="badge ok">10 buildings</span>
  <span class="badge warn">accepted=false · not ship</span>
  <span class="badge">Cozy Cyber-Pixel 2.5D</span>
  <span class="badge">cyan = manifestation only</span>
  <div class="tabs">
    <a href="#chars">Nhân vật</a>
    <a href="#buildings">Building</a>
    <a href="#props">Vật thể</a>
    <a href="#manifest">Manifestation</a>
    <a href="#rules">Quy định</a>
  </div>
</header>

<section>
  <h2>Reference sheets (art direction)</h2>
  <div class="sheet-preview">
    <div>
      <div class="meta">10 buildings sheet</div>
      <img src="buildings/buildings_sheet_10.jpg" alt="buildings sheet"/>
    </div>
    <div>
      <div class="meta">30 props sheet</div>
      <img src="props/props_sheet_30.jpg" alt="props sheet"/>
    </div>
  </div>
  <div class="pipeline">
    <div class="pipe-step"><strong>1. Mockup SSOT</strong>Trang này + JSON</div>
    <div class="pipe-step"><strong>2. Design package</strong>Foundry + style lock</div>
    <div class="pipe-step"><strong>3. Offline Blender</strong>GLB + clips + SHA</div>
    <div class="pipe-step"><strong>4. Quarantine QA</strong>vs mockup delta</div>
    <div class="pipe-step"><strong>5. WO promote</strong>game/assets</div>
    <div class="pipe-step"><strong>6. Runtime smoke</strong>idle play + load</div>
  </div>
</section>

<section id="chars">
  <h2>15 Nhân vật — animation thật (video + clip switch)</h2>
  <p class="meta">Clip tối thiểu: idle · walk · scan · happy · cancel. Nori thêm Layer B. Timing: bob 2.4s / bob_small 3.0s / breathe 2.8s.</p>
  <div class="toolbar">
    <label>Play-all clip:
      <select id="playAllClip">
        <option value="idle">idle</option>
        <option value="walk">walk</option>
        <option value="scan">scan</option>
        <option value="happy">happy</option>
        <option value="cancel">cancel</option>
      </select>
    </label>
    <button type="button" id="btnPlayAll">Áp dụng toàn cast</button>
    <button type="button" id="btnShowVideo">Ưu tiên video idle</button>
    <button type="button" id="btnShowPhoto">Ưu tiên ảnh + CSS</button>
  </div>
  <div class="grid" id="charGrid">
    {"".join(html_chars)}
  </div>
</section>

<section id="buildings">
  <h2>10 Building — ambient animation</h2>
  <div class="grid">
    {"".join(html_bld)}
  </div>
</section>

<section id="props">
  <h2>30 Vật thể — ambient animation</h2>
  <div class="grid dense">
    {"".join(html_props)}
  </div>
</section>

<section id="manifest">
  <h2>Manifestation 4 stage (cyan reserved)</h2>
  <div class="grid">
    <article class="card"><div class="stage manifest"><div style="width:70%;height:70%;border:2px dashed var(--cyan);border-radius:8px;animation:pulse 2s ease-in-out infinite"></div></div><div class="body"><h3>1. wireframe</h3><div class="meta">edges only · no collision</div></div></article>
    <article class="card"><div class="stage manifest"><div style="width:70%;height:70%;background:rgba(98,230,255,.25);border:2px solid var(--cyan);border-radius:8px"></div></div><div class="body"><h3>2. hologram</h3><div class="meta">translucent fill · no collision</div></div></article>
    <article class="card"><div class="stage manifest"><div style="width:70%;height:70%;background:linear-gradient(0deg,var(--cream) 45%,rgba(98,230,255,.35) 45%);border:2px solid var(--cyan);border-radius:8px;animation:manifestIn 3.2s ease-in-out infinite"></div></div><div class="body"><h3>3. materializing</h3><div class="meta">material rises · no collision</div></div></article>
    <article class="card"><div class="stage"><div style="width:70%;height:70%;background:var(--cream);border:2px solid var(--wood);border-radius:8px;box-shadow:0 0 0 3px #f5c451 inset"></div></div><div class="body"><h3>4. complete</h3><div class="meta">warm palette · collision after commit</div></div></article>
  </div>
</section>

<section id="rules">
  <h2>Quy định bám mockup (tóm tắt)</h2>
  <table class="reg">
    <tr><th>Hạng mục</th><th>Bắt buộc theo mockup</th></tr>
    <tr><td>Character ID</td><td>Đúng Foundry ID trong JSON (vd CCP-RH-001). Không invent ID.</td></tr>
    <tr><td>Silhouette</td><td>Đọc được 2.5D; rear marker; chibi ~2 head; ≤3 palette families.</td></tr>
    <tr><td>Animation clips</td><td>Tên clip khớp: idle/walk/scan/happy/cancel (+ Layer B Nori). Không alias thiếu → idle.</td></tr>
    <tr><td>Motion timing</td><td>Theo art bible: bob 2.4s, bob_small 3.0s, sway 3.5s, pulse 2.0s…</td></tr>
    <tr><td>Building / prop ID</td><td>module_id ổn định trong JSON; promote P1E catalog.</td></tr>
    <tr><td>Cyan</td><td>Chỉ manifestation — không tô body/building chính bằng cyan.</td></tr>
    <tr><td>Delta QA</td><td>Production GLB/concept lệch mockup &gt; ngưỡng style lock → CHANGES_REQUESTED.</td></tr>
    <tr><td>Authority</td><td>Mockup = design SSOT. Runtime truth vẫn là World Commit + GLB hash sau WO.</td></tr>
  </table>
  <p>File khóa đầy đủ: <code>MOCKUP_DESIGN_LOCK.md</code> · Index máy: <code>MOCKUP_SSOT_V2.json</code></p>
</section>

<footer>
  <p>MOCKUP_SSOT_V2 · status DESIGN_SSOT_ACTIVE · accepted=false · self_accept=false</p>
  <p>Video samples: Nori idle, Bụi Mơ idle, Bác Bắp idle, Kito idle, House ambient, Lamp pulse. Các entity còn lại: CSS motion đúng bible + art sheet.</p>
  <p>Path: orchestration/control/visual_reference/mockup_ssot_v2/</p>
</footer>

<script>
(function(){{
  function setAnim(card, name){{
    const stage = card.querySelector('[data-stage]');
    if(!stage) return;
    stage.className = stage.className.split(/\\s+/).filter(c => !c.startsWith('anim-')).join(' ');
    stage.classList.add('anim-' + name);
    card.querySelectorAll('.btns button[data-anim]').forEach(b => {{
      b.classList.toggle('active', b.getAttribute('data-anim') === name);
    }});
  }}
  document.querySelectorAll('.card.char').forEach(card => {{
    card.querySelectorAll('button[data-anim]').forEach(btn => {{
      btn.addEventListener('click', () => setAnim(card, btn.getAttribute('data-anim')));
    }});
    const tog = card.querySelector('button[data-toggle-vid]');
    if(tog){{
      tog.addEventListener('click', () => {{
        const v = card.querySelector('video.media');
        const img = card.querySelector('img.media');
        if(!v || !img) return;
        if(v.hidden){{ v.hidden=false; img.hidden=true; }}
        else {{ v.hidden=true; img.hidden=false; }}
      }});
    }}
  }});
  const playAll = document.getElementById('btnPlayAll');
  const sel = document.getElementById('playAllClip');
  if(playAll){{
    playAll.addEventListener('click', () => {{
      const name = sel.value;
      document.querySelectorAll('.card.char').forEach(c => setAnim(c, name));
    }});
  }}
  function prefer(mode){{
    document.querySelectorAll('.card.char').forEach(card => {{
      const v = card.querySelector('video.media');
      const img = card.querySelector('img.media');
      if(!img) return;
      if(mode==='video' && v){{ v.hidden=false; img.hidden=true; }}
      else {{ if(v) v.hidden=true; img.hidden=false; }}
    }});
  }}
  const bv = document.getElementById('btnShowVideo');
  const bp = document.getElementById('btnShowPhoto');
  if(bv) bv.addEventListener('click', () => prefer('video'));
  if(bp) bp.addEventListener('click', () => prefer('photo'));
}})();
</script>
</body>
</html>
'''

out = dest / "MOCKUP_SSOT_V2.html"
out.write_text(html, encoding="utf-8")
print("Wrote", out, "bytes", out.stat().st_size)
